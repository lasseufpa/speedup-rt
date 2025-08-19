"""
LASSE
Created by Cláudio Modesto
Utilitary functions used across the experiments
"""

import numpy as np
from mimo_channel import get_narrow_band_ULA_MIMO_channel, get_DFT_operated_channel
from sionna.channel import subcarrier_frequencies, cir_to_ofdm_channel
from scipy.constants import Boltzmann  # 1.380649e-23 J.K^-1

def get_nmse(target, predicted, convert_linear=False, convert_db=False):
    """
    Get Normalized Mean Square Error between two sequences
    """
    # convert to linear
    if convert_linear:
        target = np.array([pow(10, x/10) for x in target])
        predicted = np.array([pow(10, x/10) for x in predicted])

    nmse = np.linalg.norm(np.array(target) - np.array(predicted), ord=2) ** 2 / (
        np.linalg.norm(target, ord=2) ** 2)

    # Convert to DB
    if convert_db:
        nmse = 10*np.log10(nmse)

    return nmse


def dBW2Watts(dBW):
    return np.float_power(10, (dBW / 10))


def Watts2dBW(Watts):
    return 10*np.log10(Watts)


def get_correlation_F(target, predicted):
    """
    Get F correlation from channel matrix
    """
    # it is literally F, the clean code defensors will be mad, sorry :)
    F = np.abs((np.array(predicted, np.complex128).conj().T * target))**2 / (
        (np.linalg.norm(predicted)**2) * (np.linalg.norm(target)**2)
    )

    return F


def find_equivalent_ray(method: str, known_samples, known_sample_index, n_terms: int):
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

def get_geometric_channel_ULA(
    data,
    number_Tx_antennas: int,
    number_Rx_antennas: int,
    normalized_distance: float,
    angle_with_array_normal: float,
    split_channel_coeff: bool,
    random_phase: bool
    ):

    complex_gain = np.array(data[0])
    AoA_az = np.real(np.array(data[1]))
    AoD_az = np.real(np.array(data[2]))

    if split_channel_coeff:
        phase = np.real(np.array(data[3]))
        mimo_channel = get_narrow_band_ULA_MIMO_channel(AoA_az, AoD_az,
                                        complex_gain, number_Tx_antennas,
                                        number_Rx_antennas, normalized_distance,
                                        angle_with_array_normal, path_phase=phase,
                                        split_channel_coeff=True, random_phase=random_phase)
    else:
        mimo_channel = get_narrow_band_ULA_MIMO_channel(AoA_az, AoD_az,
                                        complex_gain, number_Tx_antennas,
                                        number_Rx_antennas, normalized_distance,
                                        angle_with_array_normal)

    return mimo_channel

def create_geometric_channels(
                            processed_data,
                            n_tx_antennas: int,
                            n_rx_antennas: int,
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
        tau = []
        for ray_id in range(len(processed_data[run])):
            complex_gain.append(processed_data[run][ray_id][0])
            arr_azi.append(processed_data[run][ray_id][2])
            dep_azi.append(processed_data[run][ray_id][4])
            phase.append(processed_data[run][ray_id][5])
            tau.append(processed_data[run][ray_id][6])
        # separate complex gain in complex amplitude and phase
        if split_channel_coeff:
            payload = [complex_gain, arr_azi, dep_azi, np.float32(phase)]
        else:
            payload = [complex_gain, arr_azi, dep_azi]
        channel = get_geometric_channel_ULA(
                                    payload, n_tx_antennas,
                                    n_rx_antennas,
                                    normalized_distance,
                                    angle_with_array_normal,
                                    split_channel_coeff,
                                    random_phase)
        wireless_channels.append(channel)

    return wireless_channels

def create_ofdm_channels(processed_data,
                        split_channel_coeff=False) -> list:
    """
    Create wireless OFDM channels from ray tracing parameters
    """

    # OFDM channel parameters
    subcarrier_frequency = 15e3
    fft_size = 48

    # define the frequencies of the OFDM channel
    frequencies = subcarrier_frequencies(fft_size, subcarrier_frequency)

    wireless_channels = []
    for run, _ in enumerate(processed_data):
        phase, complex_amplitude = [], []
        tau = []
        for ray_id in range(len(processed_data[run])):
            complex_amplitude.append(processed_data[run][ray_id][0][0, 0, 0, 0, 0, :])
            phase.append(processed_data[run][ray_id][5])
            tau.append(processed_data[run][ray_id][6])

        complex_amplitude = np.array(complex_amplitude)
        complex_amplitude = np.reshape(complex_amplitude, (1, 1, 1, 1, 1,
                                                    complex_amplitude.shape[0], 1))
        phase = np.array(phase)
        phase = np.reshape(phase, (1, 1, 1, 1, 1, phase.shape[0], 1))
        tau = np.array(tau, np.float128)
        tau = np.reshape(tau, (1, 1, 1, tau.shape[0]))

        if split_channel_coeff:
            complex_gain = complex_amplitude
            complex_gain = np.array(complex_gain, np.complex64)
        else:
            complex_gain = np.array(complex_amplitude, np.complex64)

        # Compute the frequency response of the channel at frequencies.
        channel = cir_to_ofdm_channel(frequencies,
                                    complex_gain,
                                    tau,
                                    normalize=True)
        wireless_channels.append(channel)

    return wireless_channels

def get_bitrate(eigenvalues, bandwidth=100e6):
    """
    Calculates the bit rate for all the possible beam pair combinations.
    """
    H_shape = eigenvalues.shape
    ############################## Noise calculation ###########################
    standard_noise_temperature = 290  # Standard value is T_o = 290 Kelvin = ~16.85 °C
    device_noise_temperature = 298.15  # The adopted value can be T_e = 25 °C = 298.15 K
    noise_factor = 1 + (device_noise_temperature / standard_noise_temperature)
    noise_figure = -70 * np.log10(noise_factor)  # in dB
    noise_PSD = Boltzmann * standard_noise_temperature # in Joules, which is equal to W/Hz
    noise_power_dBW = Watts2dBW(noise_PSD * bandwidth) + noise_figure # noise_figure = around 100 dBW
    noise_power_watts = dBW2Watts(noise_power_dBW)
    ############################## Interference calculation ###################
    interference_power_dBW = -80
    interference_power_watts = dBW2Watts(interference_power_dBW)
    ###########################################################################
    SNR = (eigenvalues**2) / (noise_power_watts + interference_power_watts) # A1 used to flatten
    spectral_efficiency = np.sum(np.log2(1 + SNR))
    bit_rate = (bandwidth * spectral_efficiency)#.reshape(H_shape[0], H_shape[1])

    return bit_rate

def get_svd_matrix(H):
    U, S, D = np.linalg.svd(H)

    return S


def equivalent_channel(H, n_tx_antennas, n_rx_antennas):
    channel = get_DFT_operated_channel(H, n_tx_antennas, n_rx_antennas)

    return channel


def get_best_beam(equivalent_channel_magnitude):
    best_beam = np.argwhere(
        equivalent_channel_magnitude == np.max(equivalent_channel_magnitude)
    )

    return best_beam


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
