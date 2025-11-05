""" Miscellaneous functions """

import os
from typing import Tuple
import json
import zipfile
from re import sub
import wget
import numpy as np

# Avoid unnecessary TF logs
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf

def set_up_system_configs():
    '''
    Configure the system to properly run the codes.
    '''
    # GPU parameters
    GPU_NUM = "" # "": without GPU
    os.environ["CUDA_VISIBLE_DEVICES"] = f"{GPU_NUM}"

    # Tensorflow and numpy seed for reproducibility
    tf.random.set_seed(1)
    np.random.seed(1)

    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)

    return config

def get_next_file_number(directory: str) -> str:
    """
    Find the next available number to create a new duration or nmse npz file.
    """
    files = os.listdir(directory)
    if not files:
        return 1

    max_num = 0

    for file in files:
        if file == ".gitkeep":
            continue
        num = int(file[-5])
        max_num = max(max_num, num)

    return str(max_num + 1)

def remove_lines_from_xml(new_xml_path: str,
                          keyword: str) -> None:
    """
    Check the xml file, which is part of the mitsuba file, to
    remove specific lines that represent an object in the scenario. 
    """
    with open(new_xml_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Store the lines to be removed
    modified_lines = []
    skip_lines = 0

    # Logic to identify the xml lines related to the object
    # we will remove
    for i, _ in enumerate(lines):
        if skip_lines > 0:
            skip_lines -= 1
            continue

        if keyword in lines[i]:
            skip_lines = 2  # Jump 2 lines
            # if it isn't the first line, remove the previous line
            if i > 0:
                modified_lines.pop()
        else:
            modified_lines.append(lines[i])

    # Save the modified lines
    with open(new_xml_path, 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)

def get_center_of_vertices_pos(vertices_pos: np.ndarray) -> np.ndarray:
    """
    Use the vertices matrix of the object and a distance between two points
    to find the center position of the object.
    """
    vertices_matrix_len = len(vertices_pos)
    # The first position in the vertex matrix
    first_position = vertices_pos[0]
    highest_pos = vertices_pos[0]
    highest_distance = 0

    for i in range(vertices_matrix_len - 1):
        # Distance between the first vertex in the 3D object and the next
        distance = np.sqrt((vertices_pos[0][0] - vertices_pos[i+1][0])**2 +
                           (vertices_pos[0][1] - vertices_pos[i+1][1])**2 +
                           (vertices_pos[0][2] - vertices_pos[i+1][2])**2)
        if distance > highest_distance:
            # If greater, store the values
            highest_distance = distance
            highest_pos = vertices_pos[i+1]

    vertices_center_position = np.array([(first_position[0] + highest_pos[0])/2,
                                   (first_position[1] + highest_pos[1])/2,
                                   (first_position[2] + highest_pos[2])/2])
    return vertices_center_position

def adjust_positions_in_multi_material_scenario(vertices_pos: np.ndarray,
                                                object_name: str,
                                                position_dict_multi_material: dict) -> np.ndarray:
    """
    Map a single object that is divided into multiple objects using a regular expression 
    to match their names. This way, the object's center is counted as one, and the cut-out 
    methods do not cut only a single part of the object, for example.
    """
    new_center_of_vertices_pos = None
    # Remove the suffix to compare with dict keys
    pattern =  r'-itu_.*'
    new_object_name = sub(pattern, "", object_name)

    # Logic to map the object
    for chave in position_dict_multi_material:
        if new_object_name in chave:
            # If the object already is mapped, we use this value,
            # avoiding using two different positions for a house and its roof
            new_center_of_vertices_pos = position_dict_multi_material[chave]

            return new_center_of_vertices_pos

    # If object is not mapped, we get the center position and store it in the dict
    new_center_of_vertices_pos = get_center_of_vertices_pos(vertices_pos)
    position_dict_multi_material[object_name] = new_center_of_vertices_pos

    return new_center_of_vertices_pos

def mitsubas_check_and_download():
    """
    Check if the project mitsubas exists, if not, download and unzip it.
    """
    url_modern_city =  \
    'https://nextcloud.lasseufpa.org/s/2gsXWfN6AiksFXc/download/original_mitsuba.zip'
    url_simplifications =  \
    'https://nextcloud.lasseufpa.org/s/9DH3DpwymiTan4a/download/mitsubas.zip'

    # Check and download (original_modern_city_mitsuba (without_simplification))
    if not os.path.isdir('mitsubas/modern_city_mitsuba'):
        if not os.path.isfile('mitsubas/original_mitsuba.zip'):
            print("Downloading modern city mitsuba\n")
            wget.download(url_modern_city)
        with zipfile.ZipFile('original_mitsuba.zip', "r") as zip_ref:
            zip_ref.extractall('mitsubas/')
            os.remove('original_mitsuba.zip')

    # Check and download (simplified_mitsubas)
    if not os.path.isdir('mitsubas/simplifications/vertex'):
        if not os.path.isfile('mitsubas/simplifications/mitsubas.zip'):
            print("\nDownloading simplification mitsubas\n")
            wget.download(url_simplifications)
        with zipfile.ZipFile('mitsubas.zip', "r") as zip_ref:
            zip_ref.extractall('mitsubas/simplifications/')
            os.remove('mitsubas.zip')

def nmse_calculation(correct_channel: np.ndarray,
                     estimated_channel: np.ndarray) -> float:
    """
    Implements the nmse calculation.
    """
    nmse = (np.linalg.norm(correct_channel - estimated_channel, ord=2) ** 2) / (
        np.linalg.norm(correct_channel, ord=2) ** 2
    )
    nmse_db = 10 * np.log10(nmse)
    return nmse_db

def calculate_nmse_betw_scenarios(ground_truth: list,
                                  simplification: list) -> list:
    """
    Pass the scenario channel with its simplified version to the nmse formula
    and return the result value. 
    """
    nmses = []
    for ground_truth_value, simplification_value in zip(ground_truth, simplification):
        nmse_value = nmse_calculation(ground_truth_value, simplification_value)
        nmses.append(nmse_value)

    return nmses

def configure_rx_positions_modern_city(config: dict,
                                       step: float,
                                       path_type: int) -> Tuple[np.ndarray,np.ndarray]:
    """
    Calculate rx positions along a predefined path using a given step for the
    modern city scenario.
    """
    if path_type == 0:
        md_rx_position = config["rx_position_linear"]
        # Taking into account the current position
        md_rx_x_position_1_row = md_rx_position[0] + 2
        md_rx_x_position_2_row = md_rx_position[0] + 8
        md_rx_y_position_min = md_rx_position[1] - 20
        md_rx_y_position_max = md_rx_position[1] + 20

        # New rx positions
        new_rx_x_positions = np.array([md_rx_x_position_1_row, md_rx_x_position_2_row])
        new_rx_y_positions = np.arange(md_rx_y_position_min, md_rx_y_position_max +
                                   step, step)
    elif path_type == 1:
        md_rx_position = config["rx_position_square"]
        # Taking into account the current position
        md_rx_x_position_min = md_rx_position[0] - 31.541
        md_rx_x_position_max = md_rx_x_position_min + 36
        md_rx_y_position_min = md_rx_position[1] + 38.752
        md_rx_y_position_max = md_rx_y_position_min - 35

        # New rx positions
        new_rx_x_positions = np.arange(md_rx_x_position_min, md_rx_x_position_max +
                                   step, step)
        new_rx_y_positions = np.arange(md_rx_y_position_min, md_rx_y_position_max +
                                   -step, -step)

    else: # 0 version
        md_rx_position = config["rx_position_linear"]
        # Taking into account the current position
        md_rx_x_position_1_row = md_rx_position[0] + 2
        md_rx_x_position_2_row = md_rx_position[0] + 8
        md_rx_y_position_min = md_rx_position[1] - 20
        md_rx_y_position_max = md_rx_position[1] + 20

        # New rx positions
        new_rx_x_positions = np.array([md_rx_x_position_1_row, md_rx_x_position_2_row])
        new_rx_y_positions = np.arange(md_rx_y_position_min, md_rx_y_position_max +
                                   step, step)

    return new_rx_x_positions, new_rx_y_positions

def save_nmse(hs_freq_ground_truth: list, **kwargs) -> None:
    """
    Calculate the nmse between the simplified scenarios and the ground truth with
    a sanity check and save it to an npz.
    """
    next_num = get_next_file_number("npzs/nmse")
    nmses = {}
    for key, hs_freq in kwargs.items():
        nmse = calculate_nmse_betw_scenarios(hs_freq_ground_truth, hs_freq)
        nmses[key] = nmse

    np.savez("npzs/nmse/nmses" + next_num + ".npz", **nmses)
    print("Saved as nmses" + next_num + ".npz")

def save_rt_duration(**kwargs) -> None:
    """
    Save the ray-tracing durations to a npz.
    """
    next_num = get_next_file_number("npzs/duration")
    np.savez("npzs/duration/rt_durations" + next_num + ".npz", **kwargs)
    print("Saved as rt_durations" + next_num + ".npz")
