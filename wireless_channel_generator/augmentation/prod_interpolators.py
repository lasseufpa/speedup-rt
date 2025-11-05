"""
LASSE
Created by Cláudio Modesto

Interpolator class for ray tracing post-processing in production environments
"""
import copy
import numpy as np
from utils import find_equivalent_ray


class Interpolators:
    """
    Interpolators()

    Stores the interpolated rays using different methods
    """

    def __init__(self):
        pass

    def linear_n_factor_interp(self, ray_data, n_terms):
        """
        Linear interpolation for n terms between two known samples
        """
        eq_ray_method = "face_id"
        known_samples = copy.deepcopy(ray_data)
        orig_known_samples_index = np.arange(0, len(known_samples.keys()))

        all_index = np.arange(0, len(known_samples.keys()) * n_terms - (n_terms - 1))
        interp_samples_index = []
        for i in range(n_terms - 1):
            interp_samples_index.extend(all_index[i+1::n_terms])
        interp_samples_index = np.sort(interp_samples_index)

        if eq_ray_method == "face_id":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                    orig_known_samples_index, n_terms)
        elif eq_ray_method == "time_arrival":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                    orig_known_samples_index, n_terms)
        elif eq_ray_method == "interactions":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                    orig_known_samples_index, n_terms)

        new_known_samples_index = all_index[::n_terms]
        poly_known_samples = copy.deepcopy(paired_known_samples)
        interpolated_samples = {}
        for ray_id in range(len(poly_known_samples[0])):
            known_rays = []
            for run in orig_known_samples_index:
                known_rays.append(poly_known_samples[run][ray_id])

            gain_known_samples = [known_rays[k][0] for k in range(len(known_rays))]
            theta_r_known_samples = [known_rays[k][1] for k in range(len(known_rays))]
            phi_r_known_samples = [known_rays[k][2] for k in range(len(known_rays))]
            theta_t_known_samples = [known_rays[k][3] for k in range(len(known_rays))]
            phi_t_known_samples = [known_rays[k][4] for k in range(len(known_rays))]
            phase_known_samples = [known_rays[k][5] for k in range(len(known_rays))]
            tau_known_samples = [known_rays[k][6] for k in range(len(known_rays))]

            gain_interp_samples = np.interp(interp_samples_index, new_known_samples_index,
                                            gain_known_samples)
            theta_r_interp_samples = np.interp(interp_samples_index, new_known_samples_index,
                                            theta_r_known_samples)
            phi_r_interp_samples = np.interp(interp_samples_index, new_known_samples_index,
                                            phi_r_known_samples)
            theta_t_interp_samples = np.interp(interp_samples_index, new_known_samples_index,
                                            theta_t_known_samples)
            phi_t_interp_samples = np.interp(interp_samples_index, new_known_samples_index,
                                            phi_t_known_samples)
            phase_interp_samples = np.interp(interp_samples_index, new_known_samples_index,
                                            phase_known_samples)
            tau_interp_samples = np.interp(interp_samples_index, new_known_samples_index,
                                            tau_known_samples)

            # reconstruct the known scenes to a new index
            run_idx = 0
            new_known_samples = {}
            for run in new_known_samples_index:
                if run not in new_known_samples:
                    new_known_samples[run] = known_samples[run_idx]
                run_idx += 1

            run_idx = 0
            # reconstruct the interpolated scenes in each index
            for run in interp_samples_index:
                if run not in interpolated_samples:
                    interpolated_samples[run] = {}

                interpolated_samples[run][ray_id] = [
                                        gain_interp_samples[run_idx],
                                        theta_r_interp_samples[run_idx],
                                        phi_r_interp_samples[run_idx],
                                        theta_t_interp_samples[run_idx],
                                        phi_t_interp_samples[run_idx],
                                        phase_interp_samples[run_idx],
                                        tau_interp_samples[run_idx]
                                        ]
                run_idx += 1

        # merge the known scenes with the generated one
        new_known_samples.update(interpolated_samples)

        return new_known_samples
