""" Calculates the ray-tracing duration for the original and simplification scenario (separeted_versions) """

import os
import argparse
from utils.misc import mitsubas_check_and_download, save_rt_duration, set_up_system_configs, \
                       configure_rx_positions_modern_city
from utils.ray_tracing_channel import configure_scene_ray_tracing_parameters, \
                                      rt_duration_varying_rx_position

if __name__ == "__main__":
    # Check if the mitsubas files exist, if not, download them
    mitsubas_check_and_download()

    # Configuring the parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--path_type",
                        "-pt", default=0,
                        type=int,
                        help="Path chosen to move the RX (Linear - 0, Square - 1)")
    args = parser.parse_args()

    # Configure the seeds and GPU, and return the json with the stored parameters
    config = set_up_system_configs()

    # Mitsubas paths
    cwd = os.getcwd()

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
    print("Starting rt duration calculation ...")

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(normal_mitsuba_xml_path)
    rt_duration_normal = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(cmap_mitsuba_xml_path)
    rt_duration_cmap = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(sphere_mitsuba_xml_path)
    rt_duration_sphere = rt_duration_varying_rx_position(rx_x_positions,
                                                       rx_y_positions,
                                                       scene,
                                                       PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(rectangle_mitsuba_xml_path)
    rt_duration_rectangle = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(interactions_xml_path)
    rt_duration_interactions = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(vertex_mitsuba_xml_path)
    rt_duration_vertex = rt_duration_varying_rx_position(rx_x_positions,
                                                          rx_y_positions,
                                                          scene,
                                                          PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(quadric_mitsuba_xml_path)
    rt_duration_quadric = rt_duration_varying_rx_position(rx_x_positions,
                                                            rx_y_positions,
                                                            scene,
                                                            PATH_TYPE)

    # Mechanisms for saving the values on npzs
    save_rt_duration(rt_duration_normal=rt_duration_normal,
                     rt_duration_cmap=rt_duration_cmap,
                     rt_duration_sphere=rt_duration_sphere,
                     rt_duration_rectangle=rt_duration_rectangle,
                     rt_duration_interactions=rt_duration_interactions,
                     rt_duration_vertex=rt_duration_vertex,
                     rt_duration_quadric=rt_duration_quadric)
