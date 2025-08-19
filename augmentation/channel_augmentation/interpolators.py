"""
LASSE
Created by Cláudio Modesto
Interpolator class for ray tracing post-processing
"""
import copy
import numpy as np
from scipy.interpolate import CubicSpline
from utils import find_equivalent_ray


class Interpolators:
    """
    Interpolators()

    Stores the interpolated rays using different methods
    """

    def __init__(self):
        pass

    def linear_n_interp(self, sequence, n_terms):
        '''
        Linear matrix n-factor interpolation
        '''

        if type(sequence) is complex:
            sequence = np.array(sequence, np.complex128)
        else:
            sequence = np.array(sequence)

        predicted_samples = np.zeros(sequence.shape)

        known_samples = sequence[::n_terms + 1]
        print(known_samples)
        for i in range(0, len(predicted_samples) - n_terms, n_terms + 1):
            predicted_samples[i] = known_samples[i // (n_terms + 1)]
            predicted_samples[i + n_terms + 1] = known_samples[i // (n_terms + 1) + 1]

            for j in range(1, n_terms + 1):
                predicted_samples[i + j] = known_samples[i // (n_terms + 1)] + \
                                        (j / (n_terms + 1)) * (known_samples[i // (n_terms + 1) + 1] - known_samples[i // (n_terms + 1)])

        return predicted_samples


    def matrix_n_interp(self, matrices, n_terms):
        '''
        Linear matrix n-factor interpolation
        '''
        matrices = np.array(matrices, np.complex128)
        predicted_samples = np.zeros(matrices.shape, np.complex128)

        known_samples = matrices[::n_terms + 1]
        for i in range(0, len(predicted_samples) - n_terms, n_terms + 1):
            try:

                predicted_samples[i] = known_samples[i // (n_terms + 1)]
                predicted_samples[i + n_terms + 1] = known_samples[i // (n_terms + 1) + 1]

                for j in range(1, n_terms + 1):
                    predicted_samples[i + j] = known_samples[i // (n_terms + 1)] + \
                                            (j / (n_terms + 1)) * (known_samples[i // (n_terms + 1) + 1] - known_samples[i // (n_terms + 1)])
            except IndexError:
                continue
        return predicted_samples


    def matrix_interp(self, matrices):
        """
        Linear 2-factor interpolation method based on channel matrix
        """
        matrices = np.array(matrices, np.complex128)

        # placeholder for known samples
        known_samples = np.zeros((int(matrices.shape[0]/2), matrices.shape[1],
                                matrices.shape[2]), np.complex128)

        matrices_len = len(matrices)
        if len(matrices) % 2 == 0:
            pass
        else:
            matrices_len = len(matrices) - 1

        index = 0
        for i in range(0, matrices_len, 2):
            known_samples[index] = matrices[i]
            index = index + 1

        interpolated_matrix = np.zeros(known_samples.shape, np.complex128)
        for i in range(len(known_samples)):
            if i == len(known_samples) - 1:
                interpolated_matrix[i] = known_samples[i-1]
            else:
                interpolated_matrix[i] = (known_samples[i] + known_samples[i+1])/2

        predicted_matrix = np.zeros(matrices.shape, np.complex128)
        
        # construct the predict matrices using the known and the interpolated samples
        index = 0
        for i in range(len(known_samples)):
            predicted_matrix[index] = known_samples[i]
            index = index + 2
        index = 1
        for j in range(len(interpolated_matrix)):
            predicted_matrix[index] = interpolated_matrix[j]
            index = index + 2

        return predicted_matrix


    def poly_interp(self, ray_data, n_terms):
        """
        Polynomial interpolation methods using ray (MPC) parameters
        such as complex gain, arrival-departure angles and phase
        """

        eq_ray_method = "face_id"

        known_samples = {}
        for i in list(ray_data.keys())[::n_terms]:
            known_samples[i] = ray_data[i]

        known_samples_index = list(ray_data.keys())[::n_terms]
        interp_samples_index = []
        for i in range(n_terms - 1):
            interp_samples_index.extend(list(ray_data.keys())[i+1::n_terms])
        interp_samples_index = np.sort(interp_samples_index)

        if eq_ray_method == "face_id":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples), 
                                                    known_samples_index, n_terms)
        elif eq_ray_method == "time_arrival":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples), 
                                                    known_samples_index, n_terms)
        elif eq_ray_method == "interactions":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples), 
                                                    known_samples_index, n_terms)

        interpolated_samples = {}
        poly_known_samples = copy.copy(paired_known_samples)
        for ray_id in range(len(poly_known_samples[0])):
            known_rays = []
            for run in known_samples_index:
                known_rays.append(poly_known_samples[run][ray_id])

            gain_known_samples = [known_rays[k][0] for k in range(len(known_rays))]
            theta_r_known_samples = [known_rays[k][1] for k in range(len(known_rays))]
            phi_r_known_samples = [known_rays[k][2] for k in range(len(known_rays))]
            theta_t_known_samples = [known_rays[k][3] for k in range(len(known_rays))]
            phi_t_known_samples = [known_rays[k][4] for k in range(len(known_rays))]
            phase_known_samples = [known_rays[k][5] for k in range(len(known_rays))]
            tau_known_samples = [known_rays[k][6] for k in range(len(known_rays))]

            gain_interp_samples = CubicSpline(known_samples_index, gain_known_samples,
                                                bc_type="clamped")(interp_samples_index)
            theta_r_interp_samples = CubicSpline(known_samples_index, theta_r_known_samples,
                                                bc_type="clamped")(interp_samples_index)
            phi_r_interp_samples = CubicSpline(known_samples_index, phi_r_known_samples,
                                                bc_type="clamped")(interp_samples_index)
            theta_t_interp_samples = CubicSpline(known_samples_index, theta_t_known_samples,
                                                bc_type="clamped")(interp_samples_index)
            phi_t_interp_samples = CubicSpline(known_samples_index, phi_t_known_samples,
                                                bc_type="clamped")(interp_samples_index)
            phase_interp_samples = CubicSpline(known_samples_index, phase_known_samples,
                                                bc_type="clamped")(interp_samples_index)
            tau_interp_samples = CubicSpline(known_samples_index, tau_known_samples,
                                                bc_type="clamped")(interp_samples_index)

            run_idx = 0
            for run in interp_samples_index:
                if run not in interpolated_samples:
                    interpolated_samples[run] = {}

                if gain_interp_samples[run_idx] == 0:
                    continue
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

        known_samples.update(interpolated_samples)

        predicted_rays = known_samples
        return predicted_rays

    def linear_n_factor_interp(self, ray_data, n_terms):
        """
        Linear interpolation for n terms between two known samples
        """
        eq_ray_method = "face_id"

        known_samples = {}
        for i in list(ray_data.keys())[::n_terms]:
            known_samples[i] = ray_data[i]

        known_samples_index = list(ray_data.keys())[::n_terms]
        interp_samples_index = []
        for i in range(n_terms - 1):
            interp_samples_index.extend(list(ray_data.keys())[i+1::n_terms])
        interp_samples_index = np.sort(interp_samples_index)

        if eq_ray_method == "face_id":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                    known_samples_index, n_terms)
        elif eq_ray_method == "time_arrival":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                    known_samples_index, n_terms)
        elif eq_ray_method == "interactions":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                    known_samples_index, n_terms)

        interpolated_samples = {}
        poly_known_samples = copy.copy(paired_known_samples)
        for ray_id in range(len(poly_known_samples[0])):
            known_rays = []
            for run in known_samples_index:
                known_rays.append(poly_known_samples[run][ray_id])

            gain_known_samples = [known_rays[k][0] for k in range(len(known_rays))]
            theta_r_known_samples = [known_rays[k][1] for k in range(len(known_rays))]
            phi_r_known_samples = [known_rays[k][2] for k in range(len(known_rays))]
            theta_t_known_samples = [known_rays[k][3] for k in range(len(known_rays))]
            phi_t_known_samples = [known_rays[k][4] for k in range(len(known_rays))]
            phase_known_samples = [known_rays[k][5] for k in range(len(known_rays))]
            tau_known_samples = [known_rays[k][6] for k in range(len(known_rays))]

            gain_interp_samples = np.interp(interp_samples_index, known_samples_index,
                                            gain_known_samples)
            theta_r_interp_samples = np.interp(interp_samples_index, known_samples_index,
                                            theta_r_known_samples)
            phi_r_interp_samples = np.interp(interp_samples_index, known_samples_index,
                                            phi_r_known_samples)
            theta_t_interp_samples = np.interp(interp_samples_index, known_samples_index,
                                            theta_t_known_samples)
            phi_t_interp_samples = np.interp(interp_samples_index, known_samples_index,
                                            phi_t_known_samples)
            phase_interp_samples = np.interp(interp_samples_index, known_samples_index,
                                            phase_known_samples)
            tau_interp_samples = np.interp(interp_samples_index, known_samples_index,
                                            tau_known_samples)

            run_idx = 0
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

        known_samples.update(interpolated_samples)

        predicted_rays = known_samples
        return predicted_rays

    def linear_2_factor_interp(self, ray_data, n_terms=2, ideal_phase=False):
        """
        2-factor linear interpolation using ray parameters
        """
        # Perform ray pairing based on face id
        eq_ray_method = "face_id"

        rho = 0.4
        delta = 3e-9

        known_samples = {}
        for i in list(ray_data.keys())[::2]:
            known_samples[i] = ray_data[i]

        interpolated_samples = {}
        known_samples_index = list(ray_data.keys())[::2]
        interp_samples_index = list(ray_data.keys())[1::2]

        random_choice = True

        if eq_ray_method == "face_id":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                        known_samples_index, n_terms)
        elif eq_ray_method == "time_arrival":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                        known_samples_index, n_terms)
        elif eq_ray_method == "interactions":
            paired_known_samples = find_equivalent_ray(eq_ray_method, copy.deepcopy(known_samples),
                                                        known_samples_index, n_terms)
        for run in interp_samples_index:
            if run != interp_samples_index[-1]:
                interpolated_samples[run] = []

                for ray_id in range(len(paired_known_samples[run-1])):
                    # Create the stable segments
                    if eq_ray_method == "interactions":
                        dist = [np.linalg.norm(np.array(paired_known_samples[run-1][ray_id][7][k]) - np.array(paired_known_samples[run+1][ray_id][7][k])) 
                            for k in range(len(ray_data[run][ray_id][7]))]
                        is_similar = all(x < rho for x in dist)
                    elif eq_ray_method == "time_arrival":
                        tau_previous_ray = paired_known_samples[run-1][ray_id][6]
                        tau_next_ray = paired_known_samples[run+1][ray_id][6]
                        is_similar = np.abs(tau_next_ray - tau_previous_ray) < delta
                    elif eq_ray_method == "face_id": # uses object faces ID
                        is_similar = paired_known_samples[run - 1][ray_id][8] == paired_known_samples[run + 1][ray_id][8]

                    if is_similar:
                        id_run1 = paired_known_samples[run - 1][ray_id].pop()
                        inter_run1 = paired_known_samples[run - 1][ray_id].pop()
                        id_run2 = paired_known_samples[run + 1][ray_id].pop()
                        inter_run2 = paired_known_samples[run + 1][ray_id].pop()

                        interpolated_samples[run].append((np.array(paired_known_samples[run-1][ray_id]) +
                                                        np.array(paired_known_samples[run+1][ray_id]))/2)

                        paired_known_samples[run - 1][ray_id].append(inter_run1)
                        paired_known_samples[run - 1][ray_id].append(id_run1)
                        paired_known_samples[run + 1][ray_id].append(inter_run2)
                        paired_known_samples[run + 1][ray_id].append(id_run2)

                    else:
                        # the probability of a birth or death ray is indepedent
                        # and modeled with bernoulli distribution with p = 0.5
                        dead_or_alive = np.random.choice([0,1], p=[0.5, 0.5])
                        if random_choice:
                            if dead_or_alive == 1:
                                interpolated_samples[run].append(copy.copy(paired_known_samples[run-1][ray_id]))
                            else:
                                interpolated_samples[run].append(copy.copy(paired_known_samples[run+1][ray_id]))

            else:
                interpolated_samples[run] = copy.copy(paired_known_samples[run-1])

            if ideal_phase:
                for ray_id in range(len(interpolated_samples[run])):
                    if ray_id in ray_data[run]:
                        interpolated_samples[run][ray_id][5] = ray_data[run][ray_id][5]

        known_samples.update(interpolated_samples)
        predicted_rays = known_samples

        return predicted_rays
