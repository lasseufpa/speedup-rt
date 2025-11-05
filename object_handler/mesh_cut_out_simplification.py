""" Perform the 3D simplification (cut-out or mesh) """

import os
import pymeshlab.pmeshlab
from utils.parsers import parse_arguments_simplification
from utils.misc import set_up_system_configs
from utils.simplification import simplification_process

if __name__ == "__main__":
    # Argparses
    args = parse_arguments_simplification()

    # Configure the seeds and GPU, and return the json with the stored parameters
    config = set_up_system_configs()

    # Path to original meshes/xml
    cwd = os.getcwd()
    original_xml_path = cwd + config["original_path"]
    original_meshes_path = cwd + config["original_meshes_path"]

    # New paths
    new_folder_path = cwd + config["simplified_scenario_output_folder_path"]
    new_xml_path = cwd + config["simplified_scenario_output_xml_path"]
    new_meshes_path = cwd + config["simplified_scenario_output_meshes_path"]

    # Debug
    print(f"Original Meshes Directory: {original_meshes_path}")
    print(f"Simplified Meshes Directory: {new_meshes_path}", end="\n\n")

    # Create a meshset
    ms = pymeshlab.pmeshlab.MeshSet()

    simplification_process(ms=ms,
                           args=args,
                           original_xml_path=original_xml_path,
                           original_meshes_path=original_meshes_path,
                           new_folder_path=new_folder_path,
                           new_xml_path=new_xml_path,
                           new_meshes_path=new_meshes_path)
