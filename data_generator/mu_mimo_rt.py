'''
Script to generate ray tracing datasets
'''
import argparse
import pickle
import numpy as np
import tensorflow as tf

# Import Sionna RT components
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Camera

parser = argparse.ArgumentParser()

parser.add_argument(
"--scenario", "-s", help="Type of scenario [canyon | etoile | munich | modern]", 
                type=str, required=True
)
parser.add_argument(
"--scenes", "-c", help="Number of scenes", type=int, required=True
)
parser.add_argument(
"--delta", "-n", help="Step movement per RT", type=float, required=True
)

args = parser.parse_args()


def generate_positions(initial_position: list, n_scenes: int,
                        delta: float, scenario: str) -> list:
    '''
    Create a linear track considering for a single mobility scenario (only Rx)
    '''

    positions = []
    steps = 0
    current_position = initial_position

    for _ in range(n_scenes):
        if scenario == 'munich':
            if steps > 100:
                current_position = [current_position[0],
                                    current_position[1] - delta, current_position[2]]
            elif steps > 90:
                current_position = [current_position[0] + delta,
                                    current_position[1], current_position[2]]
            else:
                current_position = [current_position[0],
                                    current_position[1] + delta, current_position[2]]
            steps = steps + delta
            positions.append(current_position)

        elif scenario == 'canyon':
            if steps > 83:
                current_position = [current_position[0] + delta,
                                    current_position[1], current_position[2]]
            elif steps > 80:
                current_position = [current_position[0],
                                    current_position[1] - delta, current_position[2]]
            else:
                current_position = [current_position[0] - delta,
                                    current_position[1], current_position[2]]
            steps = steps + delta
            positions.append(current_position)

        else:
            current_position = [current_position[0] - delta, 
                                current_position[1], current_position[2]]
            positions.append(current_position)

    return positions

if args.scenario == 'canyon':
    scene = load_scene('sionna/rt/scenes/simple_street_canyon/simple_street_canyon.xml')
    cam_look_at=[0, 0, 0]
    cam_position=[0, 0, 150]
    tx_position = [-31, 10, 29]
    rx_position = [23.0, 1.1, 1.4]
    rx_interf_position = [-23.0, 4.1, 1.4]
elif args.scenario == 'etoile':
    scene = load_scene('sionna/rt/scenes/etoile/etoile.xml')
    cam_position = [94.1, 63.1, 300]
    cam_look_at = [94.1, 63.1, 0]
    tx_position = [58.1, 74.3, 2.4]
    rx_position = [130.1, 51.9, 1.4]
    rx_interf_position = [45, 51.9, 1.4]
elif args.scenario == 'munich':
    scene = load_scene('sionna/rt/scenes/munich/munich.xml')
    cam_position = [-250,250,150]
    cam_look_at = [-15,30,28]
    tx_position=[8.5, 21, 27]
    rx_position=[45, 25, 1.5]
elif args.scenario == 'modern':
    scene = load_scene('sionna/rt/scenes/modern_city/modern_city.xml')
    cam_position = [30, 20, 50]
    cam_look_at = [-10,20,28]
    tx_position=[8.38372,-35.8423, 14]
    rx_position=[-10.8001, 9.67042, 1.5]

scene.frequency = 2.14e9
scene.synthetic_array = True

# Configure antenna array for all transmitters
scene.tx_array = PlanarArray(num_rows=1,
                            num_cols=1,
                            vertical_spacing=0.5,
                            horizontal_spacing=0.5,
                            pattern="iso",
                            polarization="cross")

# Configure antenna array for all receivers
scene.rx_array = PlanarArray(num_rows=1,
                            num_cols=1,
                            vertical_spacing=0.5,
                            horizontal_spacing=0.5,
                            pattern="iso",
                            polarization="cross")

# Create transmitter
tx = Transmitter(name="tx",
                position=tx_position)

# Add transmitter instance to scene
scene.add(tx)

resolution = [2000, 2000]

my_cam = Camera("my_cam", position=cam_position,
                look_at=cam_look_at)
scene.add(my_cam)

# Render scene with new camera*
scene.render("my_cam", resolution=resolution, num_samples=512) # Increase num_samples to increase image quality

RENDER_TO_FILE = True
n_scenes = args.scenes
scene_data = []

rx_positions = generate_positions(rx_position, n_scenes, args.delta, args.scenario)

for scene_id in range(n_scenes):
    print('Scene: ', scene_id)
    # Create a receiver

    rx = Receiver(
                name='rx',
                position=rx_positions[scene_id],
                orientation=[0, 0, 0])

    # Add receiver instance to scene
    scene.add(rx)

    rx_interf = Receiver(
                name='rx_interf',
                position=rx_interf_position,
                color=(0.850, 0.1, 0.1),
                orientation=[0, 0, 0])

    scene.add(rx_interf)

    #tx.look_at(rx)  # Transmitter points towards receiver

    # Compute propagation paths
    paths = scene.compute_paths(
                                max_depth=3,
                                num_samples=5e6,
                                diffraction=True,
                                scattering=False)
    interactions = paths.vertices

    # Selects the index of non-existing rays
    indices_false = [indice for indice, value in
                                enumerate(np.array(
                                paths.mask[0, 0, 0])) if not np.all(value)]

    # IDs of the objects that the ray interacted with along the path
    id_objects = paths.objects.numpy()
    id_objects = id_objects[:, 0, 0, :].T.tolist()

    num_paths = len(paths.vertices[0][0][0])
    max_depth = len(paths.vertices[:])

    reshaped_tensor = tf.transpose(interactions, perm=[3, 0, 1, 2, 4])
    reshaped_tensor = tf.reshape(reshaped_tensor,
                                (reshaped_tensor.shape[2], num_paths, max_depth, 3))
    # Converting numpy array to list
    interactions = reshaped_tensor.numpy().tolist()

    # Improves interaction data
    # Add 0 when the ray has no interaction with the environment
    for i in range(len(id_objects)):
        for j in range(len(id_objects[i])):
            if id_objects[i][j] == -1:
                interactions[0][i][j] = [0 for _ in interactions[0][i][j]]

    interactions = interactions[0]
    a, tau, phase, frozen_a = paths.cir()
    print(a.shape)

    theta_t, theta_r = paths.theta_t, paths.theta_r
    phi_t, phi_r = paths.phi_t, paths.phi_r
    path_types = paths.types[0]

    a = np.delete(a, indices_false, 5)
    frozen_a = np.delete(frozen_a, indices_false, 5)
    tau = np.delete(tau, indices_false, 3)
    theta_t = np.delete(theta_t, indices_false, 3)
    theta_r = np.delete(theta_r, indices_false, 3)
    phi_t = np.delete(phi_t, indices_false, 3)
    phi_r = np.delete(phi_r, indices_false, 3)
    interactions = np.delete(interactions, indices_false, 0)
    id_objects = np.delete(id_objects, indices_false, 0)
    path_types = np.delete(path_types, indices_false, 0)
    phase = np.delete(phase, indices_false, 5)
    phase = np.imag(phase)

    path_data = {
            "path_coef": np.array(a),  # path coefficient
            "frozen_path_coef": np.array(frozen_a),  # path coefficient
            "tau": np.array(tau),  # path delay
            "theta_t": np.array(theta_t),  # elevation angle of departure
            "phi_t": np.array(phi_t),  # azimuth angle of departure
            "theta_r": np.array(theta_r),  # elevation angle of arrival
            "phi_r": np.array(phi_r),  # azimuth angle of arrival
            "phase": np.array(phase),
            "interactions": np.array(interactions),
            "id_objects": np.array(id_objects),
            "path_types": np.array(path_types),
            "valid_path": np.array(paths.mask[0,0]),    
            "false_path": indices_false
            }


    if scene_id == n_scenes - 1 or scene_id % 50 == 0:
        RENDER_TO_FILE = True

    # create images of the simulation in the first and last scene
    if RENDER_TO_FILE:
        scene.render_to_file(
                            paths=paths,
                            camera="my_cam",  # Also try camera="preview"
                            filename=f"scenes_images/{args.scenario}_scene_{scene_id}.png",
                            resolution=[650, 500],
                            show_paths=True)

    scene_data.append(path_data)

    scene.remove('rx')
    scene.remove('rx_interf')
    RENDER_TO_FILE = False

with open(f'{args.scenario}_based_sionna_dataset_{n_scenes}_test_{args.delta}.mb', 'wb') as f:
    pickle.dump(scene_data, f)
