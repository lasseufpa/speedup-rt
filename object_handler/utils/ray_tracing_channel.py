"""Functions related to the channel generation and ray-tracing"""

import sys
import os
from typing import Tuple
import time
import numpy as np

# Mimo channel code import and avoid unnecessary TF logs
sys.path.append("../wireless_channel_generator/augmentation")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

from mimo_channel import get_narrow_band_ULA_MIMO_channel 
from utils.misc import set_up_system_configs

import tensorflow as tf
from sionna.rt import Paths
from sionna.rt import Scene
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, RadioMaterial

# Just set up the config file
config = set_up_system_configs()

def configure_scene_ray_tracing_parameters(scene_path: str) -> Scene:
    """
    Define the same scene parameters for each scene or scenario to do
    the ray-tracing and estimate the channel. 
    """
    # Defining the custom materials
    custom_material_asphalt = RadioMaterial("asphalt", 5.72, 5e-4)

    # Defining a fixed-transmitter
    tx = Transmitter(name="tx",
                     position=[config["tx_position"][0],
                               config["tx_position"][1],
                               config["tx_position"][2]],
                     orientation=[config["tx_orientation"][0],
                                  config["tx_orientation"][1],
                                  config["tx_orientation"][2]])

    # Load scene
    scene = load_scene(scene_path)

    # Configure antenna array for all transmitters
    scene.tx_array = PlanarArray(
        num_rows=int(np.sqrt(config["nTx"])),
        num_cols=int(np.sqrt(config["nTx"])),
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern=config["pattern"],
        polarization=config["polarization"],
    )

    # Configure antenna array for all receivers
    scene.rx_array = PlanarArray(
        num_rows=int(np.sqrt(config["nRx"])),
        num_cols=int(np.sqrt(config["nRx"])),
        vertical_spacing=0.5,
        horizontal_spacing=0.5,
        pattern=config["pattern"],
        polarization=config["polarization"],
    )

    # Defining the custom materials
    scene.add(custom_material_asphalt)

    # Add transmitter instance to scene
    scene.add(tx)

    # Adjusting some scene parameters
    scene.frequency = config["scene_frequency"]  # in Hz
    scene.synthetic_array = True

    return scene

def make_ray_tracing(scene: Scene) -> Paths:
    """
    Calculate ray-tracing paths, i.e. actually do the ray-tracing.
    """
    # Compute propagation paths
    rt_paths = scene.compute_paths(
        max_depth=config["max_depth"], # Max ray interactions
        num_samples=config["num_samples"],  # Number of rays shot into random directions
        scattering=True,
        diffraction=True,
        reflection=True,
    )

    return rt_paths

def rt_duration_varying_rx_position(rx_x_positions: np.ndarray,
                      rx_y_positions: np.ndarray,
                      scene: Scene,
                      path_type: int) -> list:
    """
    Perform the ray-tracing duration simulation and record the 
    durations based on the rx positions on the x and y axes.
    """
    durations = []
    if path_type == 0:
        for rx_x_new in rx_x_positions:
            for rx_y_new in rx_y_positions:
                # Create a new receiver with a new position for each loop
                rx = Receiver(name="rx",
                            position=[rx_x_new,
                                        rx_y_new,
                                        config["rx_position_linear"][2]],
                            orientation=[config["rx_orientation"][0],
                                        config["rx_orientation"][1],
                                        config["rx_orientation"][2]])
                # Avoiding errors
                scene.remove("rx")
                # Add receiver instance to scene (New Position)
                scene.add(rx)

                # Calculate the ray-tracing duration
                starting_instant = time.perf_counter()
                # Compute propagation paths
                _ = scene.compute_paths(
                    max_depth=config["max_depth"], # Max ray interactions
                    num_samples=config["num_samples"],  # Number of rays shot into random directions
                    scattering=True,
                    diffraction=True,
                    reflection=True,
                )
                ending_instant = time.perf_counter()
                duration = ending_instant-starting_instant
                durations.append(duration)
    elif path_type == 1:
        for rx_x_new in rx_x_positions:
            if rx_x_new == rx_x_positions[0] or rx_x_new == rx_x_positions[-1]:
                for rx_y_new in rx_y_positions:
                    # Create a new receiver with a new position for each loop
                    rx = Receiver(name="rx",
                                position=[rx_x_new,
                                            rx_y_new,
                                            config["rx_position_square"][2]],
                                orientation=[config["rx_orientation"][0],
                                            config["rx_orientation"][1],
                                            config["rx_orientation"][2]])
                    # Avoiding errors
                    scene.remove("rx")
                    # Add receiver instance to scene (New Position)
                    scene.add(rx)

                    # Calculate the ray-tracing duration
                    starting_instant = time.perf_counter()
                    # Compute propagation paths
                    _ = scene.compute_paths(
                        max_depth=config["max_depth"], # Max ray interactions
                        num_samples=config["num_samples"],  # Number of rays shot into random directions
                        scattering=True,
                        diffraction=True,
                        reflection=True,
                    )
                    ending_instant = time.perf_counter()
                    duration = ending_instant-starting_instant
                    durations.append(duration)
            else:
                for rx_y_new in rx_y_positions:
                    if rx_y_new == rx_y_positions[0] or rx_y_new == rx_y_positions[-1]:
                        # Create a new receiver with a new position for each loop
                        rx = Receiver(name="rx",
                                    position=[rx_x_new,
                                                rx_y_new,
                                                config["rx_position_square"][2]],
                                    orientation=[config["rx_orientation"][0],
                                                config["rx_orientation"][1],
                                                config["rx_orientation"][2]])
                        # Avoiding errors
                        scene.remove("rx")
                        # Add receiver instance to scene (New Position)
                        scene.add(rx)

                        # Calculate the ray-tracing duration
                        starting_instant = time.perf_counter()
                        # Compute propagation paths
                        _ = scene.compute_paths(
                            max_depth=config["max_depth"], # Max ray interactions
                            num_samples=config["num_samples"],  # Number of rays shot into random directions
                            scattering=True,
                            diffraction=True,
                            reflection=True,
                        )
                        ending_instant = time.perf_counter()
                        duration = ending_instant-starting_instant
                        durations.append(duration)
    return durations

def calculate_h_freq(channel_paths: Paths) -> np.matrix:
    """
    Calculate the channel frequency response in a MIMO ULA case.
    """
    # Returns the channel impulse response in the form of path coefficients (a)
    a, _, _, _= channel_paths.cir()

    # Mimo channel parameters
    n_tx_mimo = config["nTx_mimo"]
    n_rx_mimo = config["nRx_mimo"]
    a = np.squeeze(a[0, 0, 0, 0, 0])

    # Create the mimo channel
    mimo_channel = get_narrow_band_ULA_MIMO_channel(channel_paths.phi_t[0, 0, 0],
                                               channel_paths.phi_r[0, 0, 0],
                                               a, n_tx_mimo, n_rx_mimo,
                                               normalized_ant_distance=0.5,
                                               angle_with_array_normal=0,
                                               split_channel_coeff=False)
    return mimo_channel

def nmse_varying_rx_position(rx_x_positions: np.ndarray,
                            rx_y_positions: np.ndarray,
                            scene: Scene,
                            path_type: int) -> list:
    """
    Make the nmse simulation and generate the channel based on the rx positions on the x and y axes. 
    """
    h_freq_list = []
    if path_type == 0:
        for rx_x_new in rx_x_positions:
            for rx_y_new in rx_y_positions:
                # Create a new receiver with a new position for each loop
                rx = Receiver(name="rx",
                            position=[rx_x_new,
                                        rx_y_new,
                                        config["rx_position_linear"][2]],
                            orientation=[config["rx_orientation"][0],
                                        config["rx_orientation"][1],
                                        config["rx_orientation"][2]])
                # Avoiding errors
                scene.remove("rx")

                # Add receiver instance to scene (New Position)
                scene.add(rx)

                # Compute the ray tracing paths
                paths = make_ray_tracing(scene)

                # Find the channel h_freq
                h_freq = calculate_h_freq(paths)
                # Store it to NMSE calculation
                h_freq_list.append(h_freq)
    elif path_type == 1:
        for rx_x_new in rx_x_positions:
            if rx_x_new == rx_x_positions[0] or rx_x_new == rx_x_positions[-1]:
                for rx_y_new in rx_y_positions:
                    # Create a new receiver with a new position for each loop
                    rx = Receiver(name="rx",
                                position=[rx_x_new,
                                            rx_y_new,
                                            config["rx_position_square"][2]],
                                orientation=[config["rx_orientation"][0],
                                            config["rx_orientation"][1],
                                            config["rx_orientation"][2]])
                    # Avoiding errors
                    scene.remove("rx")

                    # Add receiver instance to scene (New Position)
                    scene.add(rx)

                    # Compute the ray tracing paths
                    paths = make_ray_tracing(scene)

                    # Find the channel h_freq
                    h_freq = calculate_h_freq(paths)
                    # Store it to NMSE calculation
                    h_freq_list.append(h_freq)
            else:
                for rx_y_new in rx_y_positions:
                    if rx_y_new == rx_y_positions[0] or rx_y_new == rx_y_positions[-1]:
                        # Create a new receiver with a new position for each loop
                        rx = Receiver(name="rx",
                                    position=[rx_x_new,
                                                rx_y_new,
                                                config["rx_position_square"][2]],
                                    orientation=[config["rx_orientation"][0],
                                                config["rx_orientation"][1],
                                                config["rx_orientation"][2]])
                        # Avoiding errors
                        scene.remove("rx")

                        # Add receiver instance to scene (New Position)
                        scene.add(rx)

                        # Compute the ray tracing paths
                        paths = make_ray_tracing(scene)

                        # Find the channel h_freq
                        h_freq = calculate_h_freq(paths)
                        # Store it to NMSE calculation
                        h_freq_list.append(h_freq)
    return h_freq_list

def coverage_map_function(original_xml_path: str) -> Tuple[list, float]:
    """
    Make the coverage map for the coverage map cut-out method.
    """
    # List with cm power and position values
    cmap_data_list = []

    # Initial configurations
    cmap_scene = configure_scene_ray_tracing_parameters(original_xml_path)

    # Cell Size (cmap)
    cell_size = config["cmap_cell_size"]

    print("Starting coverage map ...")
    cmap = cmap_scene.coverage_map(max_depth=config["max_depth"],
                    diffraction=True,
                    scattering=True,
                    reflection=True,
                    cm_cell_size=(cell_size, cell_size), # Grid size of coverage map cells in m
                    num_samples=int(config["num_samples"]))

    power_levels = np.log10(cmap.path_gain) * 10 # Power in dB
    global_coordinates = cmap.cell_centers.numpy() # Coordinates in blender

    for x in range(cmap.num_cells_y): # Number of y_cells (cmap)
        for y in range(cmap.num_cells_x): # Number of x_cells (cmap)
            power_level = power_levels[0, x, y]
            coordinates = global_coordinates[x, y, :]
            cmap_data_list.append((power_level, coordinates))

    return cmap_data_list, cell_size

def interactions_compute_paths_function(original_xml_path: str) -> list:
    """
    Calculate ray-tracing paths and store interaction points 
    for the interactions cut-out method.
    """
    # Configure the scene and paths
    interactions_scene = configure_scene_ray_tracing_parameters(original_xml_path)
    paths = make_ray_tracing(interactions_scene)

    # Save the ray interactions
    interactions = []
    for value in tf.reshape(paths.vertices, [-1,3]):
        interactions.append(value.numpy())

    return interactions
