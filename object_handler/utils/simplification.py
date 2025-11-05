""" Implementations of simplifications methods (mesh and cut-out simplifications) """

import os
import argparse
import shutil
import numpy as np
from tqdm import tqdm
from pymeshlab.pmeshlab import MeshSet
import pymeshlab.pmeshlab
from utils.misc import remove_lines_from_xml, \
                       adjust_positions_in_multi_material_scenario, \
                       set_up_system_configs, Tuple
from utils.ray_tracing_channel import coverage_map_function, \
                                      interactions_compute_paths_function

class Simplificator:
    """
    Specify whether simplification will be applied, and if so, determine the type of simplification: 
    cut-out or mesh simplification.
    """
    def __init__(self, ms: MeshSet,
                 args: argparse.Namespace,
                 new_xml_path: str,
                 json_config: dict) -> None:
        self.ms = ms
        self.args = args
        self.new_xml_path = new_xml_path
        self.config = json_config

    def simplification_algorithm(self) -> MeshSet:
        """
        Applying mesh simplification to an object
        """
        # Apply the algorithm
        if self.args.mesh_simplification_method == "quadric":
            n_faces = self.ms.current_mesh().face_number()
            if n_faces > self.config["number_face_collapse"]:
                # Only objects with more than 15 faces
                # (objects with less than 15 faces are destroyed by the decimate)
                self.ms.meshing_decimation_quadric_edge_collapse(targetperc=self.args.parameter)
        elif self.args.mesh_simplification_method == "vertex":
            self.ms.meshing_decimation_clustering(threshold=pymeshlab.pmeshlab.
                                                  PercentageValue(self.args.parameter))

    def without_cut(self, out: str) -> None:
        """
        Mesh simplification without cut-out.
        """
        self.simplification_algorithm()
        self.ms.save_current_mesh(out)

    def rectangle_cut(self,
                      out: str,
                      vertices_pos: np.ndarray,
                      keyword_to_cut_xml: str,
                      object_name: str,
                      position_dict_multi_material: dict) -> None:
        """
        Rectangle cut-out method, defines a rectangle with a margin, 
        anything outside this area is cut off.
        """
        vertex_pos = adjust_positions_in_multi_material_scenario(vertices_pos,
                                                                  object_name,
                                                                  position_dict_multi_material)
        # Distance between Tx and Rx
        dist_tx_rx = np.sqrt((self.config["tx_position"][0] - self.config["rx_position"][0])**2 +
                             (self.config["tx_position"][1] - self.config["rx_position"][1])**2 +
                             (self.config["tx_position"][2] - self.config["rx_position"][2])**2)
        dist_tx_rx = dist_tx_rx/2 # A large distance will not cut much,
                                  # so we divide the distance by 2

        # print('distance: ', dist_tx_rx)

        # Defines the conditions to identify the location of the object in the rectangle region
        # Tx[0] > Rx[0] and Tx[1] > Rx[1]
        tx_x_tx_y_greater = (vertex_pos[0] < self.config["tx_position"][0] + dist_tx_rx and \
                             vertex_pos[0] > self.config["rx_position"][0] - dist_tx_rx) and \
                            (vertex_pos[1] < self.config["tx_position"][1] + dist_tx_rx and \
                             vertex_pos[1] > self.config["rx_position"][1] - dist_tx_rx)

        # Tx[0] > Rx[0] and Tx[1] < Rx[1]
        tx_x_rx_y_greater = (vertex_pos[0] < self.config["tx_position"][0] + dist_tx_rx and \
                             vertex_pos[0] > self.config["rx_position"][0] - dist_tx_rx) and \
                            (vertex_pos[1] > self.config["tx_position"][1] - dist_tx_rx and \
                             vertex_pos[1] < self.config["rx_position"][1] + dist_tx_rx)

        # Tx[0] < Rx[0] and Tx[1] > Rx[1]
        rx_x_tx_y_greater = (vertex_pos[0] > self.config["tx_position"][0] - dist_tx_rx and \
                             vertex_pos[0] < self.config["rx_position"][0] + dist_tx_rx) and \
                            (vertex_pos[1] < self.config["tx_position"][1] + dist_tx_rx and \
                             vertex_pos[1] > self.config["rx_position"][1] - dist_tx_rx)

        # Tx[0] < Rx[0] and Tx[1] < Rx[1]
        rx_x_rx_y_greater = (vertex_pos[0] > self.config["tx_position"][0] - dist_tx_rx and \
                             vertex_pos[0] < self.config["rx_position"][0] + dist_tx_rx) and \
                            (vertex_pos[1] > self.config["tx_position"][1] - dist_tx_rx and \
                             vertex_pos[1] < self.config["rx_position"][1] + dist_tx_rx)

        if self.config["tx_position"][0] > self.config["rx_position"][0]: # Tx[0] > Rx[0]
            if self.config["tx_position"][1] > self.config["rx_position"][1]: # Tx[1] > Rx[1]
                if tx_x_tx_y_greater:
                    self.simplification_algorithm()
                    self.ms.save_current_mesh(out)
                else:
                    # Cut
                    remove_lines_from_xml(self.new_xml_path, keyword_to_cut_xml)
            else: # Tx[1] < Rx[1]
                if tx_x_rx_y_greater:
                    self.simplification_algorithm()
                    self.ms.save_current_mesh(out)
                else:
                    # Cut
                    remove_lines_from_xml(self.new_xml_path, keyword_to_cut_xml)
        else: # Tx[0] < Rx[0]
            if self.config["tx_position"][1] > self.config["rx_position"][1]: # Tx[1] > Rx[1]
                if rx_x_tx_y_greater:
                    self.simplification_algorithm()
                    self.ms.save_current_mesh(out)
                else:
                    # Cut
                    remove_lines_from_xml(self.new_xml_path, keyword_to_cut_xml)
            else: # Tx[1] < Rx[1]
                if rx_x_rx_y_greater:
                    self.simplification_algorithm()
                    self.ms.save_current_mesh(out)
                else:
                    # Cut
                    remove_lines_from_xml(self.new_xml_path, keyword_to_cut_xml)

    def sphere_cut(self,
                   out: str,
                   vertices_pos: np.ndarray,
                   keyword_to_cut_xml: str,
                   object_name: str,
                   position_dict_multi_material: dict) -> None:
        """
        Sphere cut-out method, defines a sphere based on the Tx and Rx distance,
        anything outside the sphere's area is cut off.
        """
        vertex_pos = adjust_positions_in_multi_material_scenario(vertices_pos,
                                                                  object_name,
                                                                  position_dict_multi_material)
        # Distance between tx and rx
        dist_tx_rx = np.sqrt((self.config["tx_position"][0] - self.config["rx_position"][0])**2 +
                             (self.config["tx_position"][1] - self.config["rx_position"][1])**2 +
                             (self.config["tx_position"][2] - self.config["rx_position"][2])**2)
        # Sphere's center
        center = np.array([(self.config["tx_position"][0] + self.config["rx_position"][0])/2,
                           (self.config["tx_position"][1] + self.config["rx_position"][1])/2,
                           (self.config["tx_position"][2] + self.config["rx_position"][2])/2])

        # Distance between the current 3D object and the center
        d = np.sqrt((vertex_pos[0] - center[0])**2 +
                    (vertex_pos[1] - center[1])**2 +
                    (vertex_pos[2] - center[2])**2)

        if d < dist_tx_rx: # Within the sphere's radius
            self.simplification_algorithm()
            self.ms.save_current_mesh(out)
        else:
            # Cut
            remove_lines_from_xml(self.new_xml_path, keyword_to_cut_xml)

    def coveragemap_cut(self,
                        out: str,
                        vertices_pos: np.ndarray,
                        keyword_to_cut_xml: str,
                        cm_data_list: Tuple[list, np.float32],
                        cell_size: float,
                        object_name: str,
                        position_dict_multi_material: dict) -> None:
        """
        Coverage map cut-out method, map each scene object into the cmap, 
        anything with less than the db_value is cut off.
        """
        db_value = -140 # Threshold in dB to cut
        vertex_pos = adjust_positions_in_multi_material_scenario(vertices_pos,
                                                                  object_name,
                                                                  position_dict_multi_material)
        for power, coords in cm_data_list: # iterates through all cmap values
            if(vertex_pos[0] > coords[0] - cell_size and
               vertex_pos[0] < coords[0] + cell_size and
               vertex_pos[1] > coords[1] - cell_size and
               vertex_pos[1] < coords[1] + cell_size and power > db_value):
                self.simplification_algorithm() # Save and simply
                self.ms.save_current_mesh(out)
                return None

        # Check if the object is the ground, save if yes
        if object_name == "ground.ply" or object_name == "mesh-Plane.ply":
            self.simplification_algorithm()
            self.ms.save_current_mesh(out)
        else:
            # Cut
            remove_lines_from_xml(self.new_xml_path, keyword_to_cut_xml)

    def interactions_cut(self,
                         out: str,
                         vertices_pos: np.ndarray,
                         keyword_to_cut_xml: str,
                         object_name: str,
                         position_dict_multi_material: dict,
                         interactions: list) -> None:
        """
        Interactions cut-out method, map all ray interaction points on the objects of scene and
        create a small area around them, anything outside this area is cut off.
        """
        vertex_pos = adjust_positions_in_multi_material_scenario(vertices_pos,
                                                                  object_name,
                                                                  position_dict_multi_material)
        interaction_threshold = 2
        for coords in interactions:
            if(vertex_pos[0] > coords[0] - interaction_threshold and
               vertex_pos[0] < coords[0] + interaction_threshold and
               vertex_pos[1] > coords[1] - interaction_threshold and
               vertex_pos[1] < coords[1] + interaction_threshold and
               vertex_pos[2] > coords[2] - interaction_threshold and
               vertex_pos[2] < coords[2] + interaction_threshold):
                self.simplification_algorithm() # Save and simply
                self.ms.save_current_mesh(out)
                return None
        # Cut
        remove_lines_from_xml(self.new_xml_path, keyword_to_cut_xml)

def simplification_process(ms: MeshSet,
                           args: argparse.Namespace,
                           original_xml_path,
                           original_meshes_path,
                           new_folder_path,
                           new_xml_path,
                           new_meshes_path) -> None:
    """
    Set up folders and simplify objects one at a time 
    according to the chosen simplification method.
    """
    # Configure the seeds and GPU, and return the json with the stored parameters
    config = set_up_system_configs()

    # Adjust the output folder (xml + clean meshes)
    if not os.path.exists(new_folder_path):
    # Create scenario folder, if it doesn't exist
        os.makedirs(new_folder_path)

    # Copy the original xml
    shutil.copy(original_xml_path, new_xml_path)

    # Create meshes folder, if it doesn't exist
    if not os.path.exists(new_meshes_path):
        os.makedirs(new_meshes_path)

    # Remove the files from the meshes folder if there are any
    for _, _, files in os.walk(os.path.join(new_folder_path, "meshes")):
        for file in files:
            os.remove(os.path.join(new_meshes_path, file))

    print("Starting the simplification ...")

    # Create a simplification class
    simplification = Simplificator(ms, args, new_xml_path, config)

    # Avoiding errors
    cmap_data_list, cell_size = None, None
    interactions = None

    # Debug and choose of the simplification type
    if args.cut_type == "rectangle":
        print("Using the rectangle type")
        simplify_and_cut_function = simplification.rectangle_cut
        parameters = ["out", "vertices_pos",
                      "keyword_to_cut_xml",
                      "object_name",
                      "position_dict_multi_material"]
    elif args.cut_type == "sphere":
        print("Using the sphere type")
        simplify_and_cut_function = simplification.sphere_cut
        parameters = ["out", "vertices_pos",
                      "keyword_to_cut_xml",
                      "object_name",
                      "position_dict_multi_material"]
    elif args.cut_type == "cmap":
        print("Using coverage map type")
        # Make the coverage map
        cmap_data_list, cell_size = coverage_map_function(original_xml_path)
        simplify_and_cut_function = simplification.coveragemap_cut
        parameters = ["out", "vertices_pos",
                      "keyword_to_cut_xml",
                      "cmap_data_list",
                      "cell_size",
                      "object_name",
                      "position_dict_multi_material"]
    elif args.cut_type == "interactions":
        simplify_and_cut_function = simplification.interactions_cut
        # Find the interactions
        interactions = interactions_compute_paths_function(original_xml_path)
        parameters = ["out",
                      "vertices_pos",
                      "keyword_to_cut_xml",
                      "object_name",
                      "position_dict_multi_material",
                      "interactions"]
    elif args.cut_type == "no_cut":
        print("Without cut type")
        simplify_and_cut_function = simplification.without_cut
        parameters = ["out"]
    elif args.cut_type is None:
        print("Without cut type")
        simplify_and_cut_function = simplification.without_cut
        parameters = ["out"]
    else:
        raise Exception("Simplification cut-out type invalid")

    # Dict to correct the position of objects that should be one, but are multiple
    position_dict_multi_material = {}

    for m in tqdm(os.listdir(original_meshes_path), colour="green"):
        # Load the mesh
        ms.load_new_mesh(os.path.join(original_meshes_path, m))
        cm = ms.current_mesh()
        # Position of the object
        vertices_pos = cm.vertex_matrix()
        # Save the mesh
        out = os.path.join(new_meshes_path, str(m))
        # To avoid cut the floor
        object_name = str(m)
        # String to identify objects in xml to cut
        keyword_to_cut_xml = "/" + str(m)

        # Associate strings with the real parameters
        parameters_dict = {
            "out": out,
            "vertices_pos": vertices_pos,
            "keyword_to_cut_xml": keyword_to_cut_xml,
            "cmap_data_list": cmap_data_list,
            "cell_size": cell_size,
            "object_name": object_name,
            "position_dict_multi_material": position_dict_multi_material,
            "interactions": interactions
        }
        arg = [parameters_dict[arg] for arg in parameters]

        # Simplify and cut objects
        simplify_and_cut_function(*arg)
