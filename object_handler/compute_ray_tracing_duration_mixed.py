""" Calculates the ray-tracing duration for the original and simplification scenario """

import os
from utils.misc import mitsubas_check_and_download, save_rt_duration, set_up_system_configs, \
                       configure_rx_positions_modern_city
from utils.ray_tracing_channel import configure_scene_ray_tracing_parameters, \
                                      rt_duration_varying_rx_position

if __name__ == "__main__":
    # Check if the mitsubas files exist, if not, download them
    mitsubas_check_and_download()

    # Configure the seeds and GPU, and return the json with the stored parameters
    config = set_up_system_configs()

    # Mitsubas paths
    cwd = os.getcwd()

    normal_mitsuba_xml_path = cwd + config["original_path_paper"]
    cmap_vertex_mitsuba_xml_path = cwd + config["modern_city_scenario_cmap_cutout_vertex_path"]
    sphere_vertex_mitsuba_xml_path = cwd + config["modern_city_scenario_sphere_cutout_vertex_path"]
    rectangle_vertex_mitsuba_xml_path = cwd + config["modern_city_scenario_rectangle_cutout_vertex_path"]
    interactions_vertex_xml_path = cwd + config["modern_city_scenario_interactions_cutout_vertex_path"]
    cmap_quadric_mitsuba_xml_path = cwd + config["modern_city_scenario_cmap_cutout_quadric_path"]
    sphere_quadric_mitsuba_xml_path = cwd + config["modern_city_scenario_sphere_cutout_quadric_path"]
    rectangle_quadric_mitsuba_xml_path = cwd + config["modern_city_scenario_rectangle_cutout_quadric_path"]
    interactions_quadric_xml_path = cwd + config["modern_city_scenario_interactions_cutout_quadric_path"]

    # Step to define the number of rx positions
    ITER_SPACE = config["iteration_space"]

    # Specific path (To mixed cases, there is only path 0 in the simulations)
    PATH_TYPE = 0

    # Generate the positions to move the Rx
    rx_x_positions, rx_y_positions = configure_rx_positions_modern_city(config,
                                                                        ITER_SPACE,
                                                                        PATH_TYPE)
    print()
    print("Starting rt duration calculation ...")

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(normal_mitsuba_xml_path)
    rt_duration_normal = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(cmap_vertex_mitsuba_xml_path)
    rt_duration_cmap_vertex = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(sphere_vertex_mitsuba_xml_path)
    rt_duration_sphere_vertex = rt_duration_varying_rx_position(rx_x_positions,
                                                       rx_y_positions,
                                                       scene,
                                                       PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(rectangle_vertex_mitsuba_xml_path)
    rt_duration_rectangle_vertex = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(interactions_vertex_xml_path)
    rt_duration_interactions_vertex = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(cmap_quadric_mitsuba_xml_path)
    rt_duration_cmap_quadric = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(sphere_quadric_mitsuba_xml_path)
    rt_duration_sphere_quadric = rt_duration_varying_rx_position(rx_x_positions,
                                                       rx_y_positions,
                                                       scene,
                                                       PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(rectangle_quadric_mitsuba_xml_path)
    rt_duration_rectangle_quadric = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # ----------------------------------------------------------------------
    scene = configure_scene_ray_tracing_parameters(interactions_quadric_xml_path)
    rt_duration_interactions_quadric = rt_duration_varying_rx_position(rx_x_positions,
                                                         rx_y_positions,
                                                         scene,
                                                         PATH_TYPE)

    # Mechanisms for saving the values on npzs
    save_rt_duration(rt_duration_normal=rt_duration_normal,
                     rt_duration_cmap_vertex=rt_duration_cmap_vertex,
                     rt_duration_sphere_vertex=rt_duration_sphere_vertex,
                     rt_duration_rectangle_vertex=rt_duration_rectangle_vertex,
                     rt_duration_interactions_vertex=rt_duration_interactions_vertex,
                     rt_duration_cmap_quadric=rt_duration_cmap_quadric,
                     rt_duration_sphere_quadric=rt_duration_sphere_quadric,
                     rt_duration_rectangle_quadric=rt_duration_rectangle_quadric,
                     rt_duration_interactions_quadric=rt_duration_interactions_quadric)
