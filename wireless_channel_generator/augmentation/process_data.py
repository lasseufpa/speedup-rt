"""
LASSE
Created by Cláudio Modesto

Script to preprocess RT datasets to be used in RT augmentation methods
"""

import pickle
import numpy as np

class RaytracingGenerator:
    """
    Class for ray tracing data generators
    """
    def __init__(self, dataset_path):
        with open(dataset_path, 'rb') as f: # read the sionna dataset
            ray_data = pickle.load(f)
        self.ray_data = ray_data

    def get_dataset(self, split_channel_coeff=False):
        """
        Process data from RT simulators such as NVIDIA's Sionna
        """
        processed_data = {}
        for run, _ in enumerate(self.ray_data):
            processed_data[run] = []
            for ray_id in range(self.ray_data[run]['phase'].shape[5]):
                if split_channel_coeff:
                    gain = np.abs(self.ray_data[run]['frozen_path_coef'][:, :, :, :, :, ray_id])
                    phase = np.rad2deg(np.angle(self.ray_data[run]['frozen_path_coef'][:, :, :, :, :, ray_id]) +
                                        self.ray_data[run]['phase'][:, :, :, :, :, ray_id])
                else:
                    gain = self.ray_data[run]['path_coef'][:, :, :, :, :, ray_id]
                    phase = np.rad2deg(np.angle(self.ray_data[run]['path_coef'][:, :, :, :, :, ray_id]))
                processed_data[run].append([ # get the MPC parameters of each ray
                    gain,
                    np.rad2deg(self.ray_data[run]['theta_r'][:, :, :, ray_id]),
                    np.rad2deg(self.ray_data[run]['phi_r'][:, :, :, ray_id]),
                    np.rad2deg(self.ray_data[run]['theta_t'][:, :, :, ray_id]),
                    np.rad2deg(self.ray_data[run]['phi_t'][:, :, :, ray_id]),
                    phase,
                    self.ray_data[run]['tau'][:, :, :, ray_id],
                    self.ray_data[run]['interactions'][ray_id].tolist(),
                    self.ray_data[run]['id_objects'][ray_id].tolist()
                    ])

        for scene, _ in enumerate(processed_data):
            for ray in range(len(processed_data[scene])):
                try:
                    current_id = processed_data[scene][ray][8]
                    next_id = processed_data[scene + 1][ray][8]
                except Exception as e:
                    continue
                if current_id == next_id:
                    continue

                for next_ray in range(len(processed_data[scene + 1])):
                    next_id = processed_data[scene + 1][next_ray][8]

                    if current_id == next_id:
                        processed_data[scene + 1][next_ray], \
                        processed_data[scene + 1][ray] = \
                        processed_data[scene + 1][ray], processed_data[scene + 1][next_ray]

        # crop excedent number of rays
        lengths = []
        for scene, _ in enumerate(processed_data):
            lengths.append(len(processed_data[scene]))

        if not all(length == lengths[0] for length in lengths):
            minimum_length = min(lengths)
            for scene, _ in enumerate(processed_data):
                del processed_data[scene][minimum_length:]

        return processed_data
