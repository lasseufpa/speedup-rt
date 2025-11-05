""" Calculates the NMSE for the simplified scenario channels relative to the original (separeted_versions) """

import os
import argparse
from utils.misc import mitsubas_check_and_download, save_nmse, \
                       configure_rx_positions_modern_city, set_up_system_configs
from utils.ray_tracing_channel import configure_scene_ray_tracing_parameters, \
                                      nmse_varying_rx_position

if __name__ == "__main__":
    # Check if the mitsubas files exist, if not, download them
    mitsubas_check_and_download()

    # Configure the seeds and GPU, and return the json with the stored parameters
    config = set_up_system_configs()

    # Path to mitsubas
    cwd = os.getcwd()

    # Configuring the parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_type",
                        "-pt",
                        default=0,
                        type=int,
                        help="Path chosen to move the Rx (Linear - 0, Square - 1)")
    args = parser.parse_args()

    # Specific path
    PATH_TYPE = args.path_type
    if PATH_TYPE == 0:
        normal_mitsuba_xml_path = cwd + config["original_path_paper"]
        cmap_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_linear_simplifications_cmap_cutout_path"]
        sphere_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_linear_simplifications_sphere_cutout_path"]
        vertex_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_linear_simplifications_vertex_simplification_path"]
        quadric_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_linear_simplifications_quadric_simplification_path"]
        rectangle_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_linear_simplifications_rectangle_cutout_path"]
        interactions_xml_path = cwd + config["modern_city_scenario_separated_linear_simplifications_interactions_cutout_path"]
    else:
        normal_mitsuba_xml_path = cwd + config["original_path_paper"]
        cmap_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_square_simplifications_cmap_cutout_path"]
        sphere_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_square_simplifications_sphere_cutout_path"]
        vertex_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_square_simplifications_vertex_simplification_path"]
        quadric_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_square_simplifications_quadric_simplification_path"]
        rectangle_mitsuba_xml_path = cwd + config["modern_city_scenario_separated_square_simplifications_rectangle_cutout_path"]
        interactions_xml_path = cwd + config["modern_city_scenario_separated_square_simplifications_interactions_cutout_path"]

    # Step to define the number of rx positions
    ITER_SPACE = config["iteration_space"]

    # Generate the positions to move the Rx
    rx_x_positions, rx_y_positions = configure_rx_positions_modern_city(config,
                                                                        ITER_SPACE,
                                                                        PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading ground truth scene ...")
    scene = configure_scene_ray_tracing_parameters(normal_mitsuba_xml_path)
    print("Original scene: ")
    hs_freq_ground_truth = nmse_varying_rx_position(rx_x_positions,
                                                    rx_y_positions,
                                                    scene,
                                                    PATH_TYPE)

    # ----------------------------------------------------------------
    print("Loading cmap scene ...")
    scene = configure_scene_ray_tracing_parameters(cmap_mitsuba_xml_path)
    print("Cmap scene: ")
    hs_freq_cmap = nmse_varying_rx_position(rx_x_positions,
                                            rx_y_positions,
                                            scene,
                                            PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading sphere scene ...")
    scene = configure_scene_ray_tracing_parameters(sphere_mitsuba_xml_path)
    print("Sphere scene: ")
    hs_freq_sphere = nmse_varying_rx_position(rx_x_positions,
                                              rx_y_positions,
                                              scene,
                                              PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading vertex scene ...")
    scene = configure_scene_ray_tracing_parameters(rectangle_mitsuba_xml_path)
    print("Vertex scene: ")
    hs_freq_rectangle = nmse_varying_rx_position(rx_x_positions,
                                              rx_y_positions,
                                              scene,
                                              PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading quadric scene ...")
    scene = configure_scene_ray_tracing_parameters(interactions_xml_path)
    print("Quadric scene: ")
    hs_freq_interactions = nmse_varying_rx_position(rx_x_positions,
                                               rx_y_positions,
                                               scene,
                                               PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading rectangle scene ...")
    scene = configure_scene_ray_tracing_parameters(vertex_mitsuba_xml_path)
    print("Rectangle scene: ")
    hs_freq_vertex = nmse_varying_rx_position(rx_x_positions,
                                                 rx_y_positions,
                                                 scene,
                                                 PATH_TYPE)

    # ----------------------------------------------------------------
    print("Loading interactions scene ...")
    scene = configure_scene_ray_tracing_parameters(quadric_mitsuba_xml_path)
    print("Interactions scene: ")
    hs_freq_quadric = nmse_varying_rx_position(rx_x_positions,
                                                    rx_y_positions,
                                                    scene,
                                                    PATH_TYPE)

    # Save all in an NPZ
    save_nmse(
            hs_freq_ground_truth=hs_freq_ground_truth,
            hs_freq_cmap=hs_freq_cmap,
            hs_freq_sphere=hs_freq_sphere,
            hs_freq_rectangle=hs_freq_rectangle,
            hs_freq_interactions=hs_freq_interactions,
            hs_freq_vertex=hs_freq_vertex,
            hs_freq_quadric=hs_freq_quadric,
    )
    