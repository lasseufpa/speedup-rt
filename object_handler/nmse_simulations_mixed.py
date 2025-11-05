""" Calculates the NMSE for the simplified scenario channels relative to the original """

import os
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

    # Specific path
    PATH_TYPE = 0

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
    print("Loading cmap (vertex) scene ...")
    scene = configure_scene_ray_tracing_parameters(cmap_vertex_mitsuba_xml_path)
    print("Cmap (vertex) scene: ")
    hs_freq_cmap_vertex = nmse_varying_rx_position(rx_x_positions,
                                            rx_y_positions,
                                            scene,
                                            PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading sphere (vertex) scene ...")
    scene = configure_scene_ray_tracing_parameters(sphere_vertex_mitsuba_xml_path)
    print("Sphere (vertex) scene: ")
    hs_freq_sphere_vertex = nmse_varying_rx_position(rx_x_positions,
                                              rx_y_positions,
                                              scene,
                                              PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading rectangle (vertex) scene ...")
    scene = configure_scene_ray_tracing_parameters(rectangle_vertex_mitsuba_xml_path)
    print("Rectangle (vertex) scene: ")
    hs_freq_rectangle_vertex = nmse_varying_rx_position(rx_x_positions,
                                              rx_y_positions,
                                              scene,
                                              PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading interactions (vertex) scene ...")
    scene = configure_scene_ray_tracing_parameters(interactions_vertex_xml_path)
    print("Interactions (vertex) scene: ")
    hs_freq_interactions_vertex = nmse_varying_rx_position(rx_x_positions,
                                               rx_y_positions,
                                               scene,
                                               PATH_TYPE)

    # ----------------------------------------------------------------
    print("Loading cmap (quadric) scene ...")
    scene = configure_scene_ray_tracing_parameters(cmap_quadric_mitsuba_xml_path)
    print("Cmap (quadric) scene: ")
    hs_freq_cmap_quadric = nmse_varying_rx_position(rx_x_positions,
                                            rx_y_positions,
                                            scene,
                                            PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading sphere (quadric) scene ...")
    scene = configure_scene_ray_tracing_parameters(sphere_quadric_mitsuba_xml_path)
    print("Sphere (quadric) scene: ")
    hs_freq_sphere_quadric = nmse_varying_rx_position(rx_x_positions,
                                              rx_y_positions,
                                              scene,
                                              PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading rectangle (quadric) scene ...")
    scene = configure_scene_ray_tracing_parameters(rectangle_quadric_mitsuba_xml_path)
    print("Rectangle (quadric) scene: ")
    hs_freq_rectangle_quadric = nmse_varying_rx_position(rx_x_positions,
                                              rx_y_positions,
                                              scene,
                                              PATH_TYPE)

    # ---------------------------------------------------------------
    print("Loading interactions (quadric) scene ...")
    scene = configure_scene_ray_tracing_parameters(interactions_quadric_xml_path)
    print("Interactions (quadric) scene: ")
    hs_freq_interactions_quadric = nmse_varying_rx_position(rx_x_positions,
                                               rx_y_positions,
                                               scene,
                                               PATH_TYPE)

    # Save all in an NPZ
    save_nmse(
            hs_freq_ground_truth=hs_freq_ground_truth,
            hs_freq_cmap_vertex=hs_freq_cmap_vertex,
            hs_freq_sphere_vertex=hs_freq_sphere_vertex,
            hs_freq_rectangle_vertex=hs_freq_rectangle_vertex,
            hs_freq_interactions_vertex=hs_freq_interactions_vertex,
            hs_freq_cmap_quadric=hs_freq_cmap_quadric,
            hs_freq_sphere_quadric=hs_freq_sphere_quadric,
            hs_freq_rectangle_quadric=hs_freq_rectangle_quadric,
            hs_freq_interactions_quadric=hs_freq_interactions_quadric,
    )
