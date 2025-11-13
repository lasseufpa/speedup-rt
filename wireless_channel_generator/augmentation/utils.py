"""
Created by Cláudio Modesto
Utilitary functions used across the experiments
LASSE
"""

import numpy as np
from mimo_channel import (get_nb_ula_mimo_channel,
                            get_nb_upa_mimo_channel,
                            get_wb_ula_mimo_channel)

def get_nmse(target, predicted, convert_linear=False, convert_db=False):
    """
    Get Normalized Mean Square Error between two sequences
    """
    # convert to linear
    if convert_linear:
        target = np.array([pow(10, x/10) for x in target])
        predicted = np.array([pow(10, x/10) for x in predicted])

    nmse = np.linalg.norm(np.array(target) - np.array(predicted)) ** 2 / (
        np.linalg.norm(target) ** 2)

    # Convert to DB
    if convert_db:
        nmse = 10*np.log10(nmse)

    return nmse


def find_equivalent_ray(method: str, known_samples, known_sample_index, n_terms: int):
    """
    Function to compare whether two rays are equivalent.
    The supported methods are based on face identification,
    time of arrival and interactions
    """
    if method == "face_id":
        for scene in known_sample_index:
            for ray in range(len(known_samples[scene])):
                try:
                    current_id = known_samples[scene][ray][8]
                    next_id = known_samples[scene + n_terms][ray][8]
                except Exception as e:
                    continue

                if current_id == next_id:
                    continue
        
                for next_ray in range(len(known_samples[scene + n_terms])):
                    next_id = known_samples[scene + n_terms][next_ray][8]

                    if current_id == next_id:
                        known_samples[scene + n_terms][next_ray], \
                            known_samples[scene + n_terms][ray] = known_samples[scene + n_terms][ray], known_samples[scene + n_terms][next_ray]

        return known_samples

    elif method == "time_arrival":
        delta = 3e-9
        for scene in known_sample_index:
            for ray in range(len(known_samples[scene-1])):
                try:
                    current_tau = known_samples[scene][ray][6]
                    next_tau = known_samples[scene+1][ray][6]
                except Exception as e:
                    continue

                if np.abs(next_tau - current_tau) < delta:
                    continue

                for next_ray in range(len(known_samples[scene + 1])):
                    next_tau = known_samples[scene + 1][next_ray][6]

                    if np.abs(next_tau - current_tau) < delta:
                        known_samples[scene + 1][next_ray], \
                            known_samples[scene + 1][ray] = known_samples[scene + 1][ray], known_samples[scene + 1][next_ray]

        return known_samples

    elif method == "interactions":
        rho = 0.4
        for scene in known_sample_index:
            for ray in range(len(known_samples[scene])):
                try:
                    dist = [np.linalg.norm(np.array(known_samples[scene][ray][7][k]) -
                                        np.array(known_samples[scene+1][ray][7][k]))
                                            for k in range(len(known_samples[scene][ray][7]))]
                except Exception as e:
                    continue

                if dist < rho:
                    known_samples[scene + 1][next_ray], \
                        known_samples[scene + 1][ray] = known_samples[scene + 1][ray], known_samples[scene + 1][next_ray]

        return known_samples

def get_geometric_channel_upa(data,
    ula_parameters: dict,
    split_channel_coeff: bool,
    ):

    """
    Function to create MIMO UPA geometric channel matrix
    from MPC paramters
    """
    
    complex_gain = np.array(data[0])
    aoa_az = np.real(np.array(data[1]))
    aoa_ele = np.real(np.array(data[2]))
    aod_az = np.real(np.array(data[3]))
    aod_ele = np.real(np.array(data[4]))

    if split_channel_coeff:
        phase = np.real(np.array(data[5]))
        mimo_channel = get_nb_upa_mimo_channel(aod_ele, aod_az, aoa_ele,
                                            aoa_az, complex_gain,
                                            ula_parameters["n_tx_ant_x"],
                                            ula_parameters["n_tx_ant_y"],
                                            ula_parameters["n_rx_ant_x"],
                                            ula_parameters["n_rx_ant_y"],
                                            split_channel_coeff=True,
                                            path_phase=phase)
    else:
        mimo_channel = get_nb_upa_mimo_channel(aod_ele, aod_az, aoa_ele,
                                                        aoa_az, complex_gain,
                                        ula_parameters["n_tx_ant_x"],
                                        ula_parameters["n_tx_ant_y"],
                                        ula_parameters["n_rx_ant_x"],
                                        ula_parameters["n_rx_ant_y"],
                                        split_channel_coeff=False)

    return mimo_channel


def get_geometric_channel_ula(
    data,
    ula_parameters: dict,
    normalized_distance: float,
    angle_with_array_normal: float,
    split_channel_coeff: bool,
    random_phase: bool
    ):

    """
    Function to create MIMO ULA geometric channel matrix
    from MPC paramters
    """

    complex_gain = np.array(data[0])
    aoa_az = np.real(np.array(data[1]))
    aod_az = np.real(np.array(data[2]))

    if split_channel_coeff:
        phase = np.real(np.array(data[3]))
        mimo_channel = get_nb_ula_mimo_channel(aoa_az, aod_az,
                                        complex_gain, ula_parameters["n_tx_ant"],
                                        ula_parameters["n_rx_ant"], normalized_distance,
                                        angle_with_array_normal, path_phase=phase,
                                        split_channel_coeff=True, random_phase=random_phase)
    else:
        mimo_channel = get_nb_ula_mimo_channel(aoa_az, aod_az,
                                        complex_gain, ula_parameters["n_tx_ant"],
                                        ula_parameters["n_rx_ant"], normalized_distance,
                                        angle_with_array_normal)

    return mimo_channel

def get_geometric_channel_wb_ula(
    data,
    ula_parameters: dict,
    normalized_distance: float,
    angle_with_array_normal: float,
    split_channel_coeff
    ):

    """
    Function to create wideband MIMO ULA 
    geometric channel matrix from MPC paramters
    """


    complex_gain = np.array(data[0])
    aoa_az = np.real(np.array(data[1]))
    aod_az = np.real(np.array(data[2]))
    tau = np.real(np.array(data[3]))
    carrier_f = 2.14e9 # GHz

    if split_channel_coeff:
        mimo_channel = get_wb_ula_mimo_channel(aoa_az, aod_az, complex_gain,
                                    tau, carrier_f, ula_parameters["n_tx_ant"],
                                    ula_parameters["n_rx_ant"], normalized_distance,
                                    angle_with_array_normal,
                                    split_channel_coeff=True)
    else:
        mimo_channel = get_wb_ula_mimo_channel(aoa_az, aod_az, complex_gain,
                            tau, carrier_f, ula_parameters["n_tx_ant"],
                            ula_parameters["n_rx_ant"], normalized_distance,
                            angle_with_array_normal)

    return mimo_channel

def create_geometric_channels(
                            processed_data,
                            antenna_pattern: str,
                            channel_type: str,
                            ula_parameters: dict,
                            upa_parameters: dict,
                            normalized_distance: float,
                            angle_with_array_normal: float,
                            split_channel_coeff=False,
                            random_phase=False) -> list:
    """
    Create wireless geometric channels from ray tracing parameters
    """

    wireless_channels = []

    for run, _ in enumerate(processed_data):
        phase, complex_gain = [], []
        arr_azi, dep_azi = [], []
        arr_ele, dep_ele = [], []
        tau = []
        for ray_id in range(len(processed_data[run])):
            complex_gain.append(processed_data[run][ray_id][0])
            arr_ele.append(processed_data[run][ray_id][1])
            arr_azi.append(processed_data[run][ray_id][2])
            dep_ele.append(processed_data[run][ray_id][3])
            dep_azi.append(processed_data[run][ray_id][4])
            phase.append(processed_data[run][ray_id][5])
            tau.append(processed_data[run][ray_id][6])
        # separate complex gain in complex amplitude and phase

        if antenna_pattern == "ula" and channel_type == 'nb':
            if split_channel_coeff:
                payload = [complex_gain, arr_azi, dep_azi, np.float32(phase)]
            else:
                payload = [complex_gain, arr_azi, dep_azi]
            channel = get_geometric_channel_ula(
                                        payload, ula_parameters,
                                        normalized_distance,
                                        angle_with_array_normal,
                                        split_channel_coeff,
                                        random_phase)
            wireless_channels.append(channel)
        elif antenna_pattern == "upa" and channel_type == 'nb':
            if split_channel_coeff:
                payload = [complex_gain, arr_azi, arr_ele, dep_azi, dep_ele, np.float32(phase)]
            else:
                payload = [complex_gain, arr_azi, arr_ele, dep_azi, dep_ele]
            channel = get_geometric_channel_upa(
                                        payload, upa_parameters,
                                        split_channel_coeff)
            wireless_channels.append(channel)

        elif antenna_pattern == "ula" and channel_type == "wb":
            if split_channel_coeff:
                payload = [complex_gain, arr_azi,
                dep_azi, tau]
            else:
                payload = [complex_gain, arr_azi,
                dep_azi, tau]                
            channel = get_geometric_channel_wb_ula(
                                        payload,
                                        ula_parameters,
                                        normalized_distance,
                                        angle_with_array_normal,
                                        split_channel_coeff)
            wireless_channels.append(channel)


    return wireless_channels

def shrink_dim_per_rx(processed_data):
    """
    shrink MPC parameters dimensions considering a given receiver
    """
    for run, _ in enumerate(processed_data):
        for ray_id in range(len(processed_data[run])):
            processed_data[run][ray_id][0] = np.squeeze(
                                        processed_data[run][ray_id][0][0, 0, 0, 0][0])
            processed_data[run][ray_id][1] = processed_data[run][ray_id][1][0, 0][0]
            processed_data[run][ray_id][2] = processed_data[run][ray_id][2][0, 0][0]
            processed_data[run][ray_id][3] = processed_data[run][ray_id][3][0, 0][0]
            processed_data[run][ray_id][4] = processed_data[run][ray_id][4][0, 0][0]
            processed_data[run][ray_id][5] = processed_data[run][ray_id][5][0, 0, 0, 0, 0][0]
            processed_data[run][ray_id][6] = processed_data[run][ray_id][6][0, 0][0]

    return processed_data

def expand_dim_per_rx(processed_data):
    """
    Expand MPC parameters dimension considering a given receiver
    """

    for run, _ in enumerate(processed_data):
        for ray_id in range(len(processed_data[run])):
            processed_data[run][ray_id] = [np.reshape(processed_data[run][ray_id][0],
                                                        (1, 1, 1, 1, 1, 1, 1)),
            np.reshape(processed_data[run][ray_id][1],
                                                        (1, 1, 1, 1)),
            np.reshape(processed_data[run][ray_id][2],
                                                        (1, 1, 1, 1)),
            np.reshape(processed_data[run][ray_id][3],
                                                        (1, 1, 1, 1)),
            np.reshape(processed_data[run][ray_id][4],
                                                        (1, 1, 1, 1)),
            np.reshape(processed_data[run][ray_id][5],
                                                        (1, 1, 1, 1, 1, 1)),
            np.reshape(processed_data[run][ray_id][6],
                                                        (1, 1, 1, 1))]
    return processed_data
