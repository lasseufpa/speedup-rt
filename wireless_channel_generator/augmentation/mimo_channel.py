"""
LASSE
Created by Aldebaro Klautau
Edited by Cláudio Modesto

Script to generate and post-processing MPC
parameters to generate simplified deterministic channels
"""

import numpy as np

def calc_omega(elevation_angles, azimuth_angles, normalized_ant_distance = 0.5):
    sin_elevations = np.sin(elevation_angles)
    omegax = 2 * np.pi * normalized_ant_distance * sin_elevations * np.cos(azimuth_angles)
    omegay = 2 * np.pi * normalized_ant_distance * sin_elevations * np.sin(azimuth_angles)

    return np.matrix((omegax, omegay))

def get_nb_upa_mimo_channel(departure_ele, departure_azi, arrival_ele,
                                     arrival_azi, path_gain,
                                    number_tx_antennas_x, number_tx_antennas_y,
                                    number_rx_antennas_x, number_rx_antennas_y,
                                    split_channel_coeff, normalized_ant_distance=0.5,
                                    path_phase=None):
    """Uses UPAs at both TX and RX.
    Will assume that all 4 normalized distances (Tx and Rx, x and y) are the same.
    """
    number_tx_antennas = number_tx_antennas_x * number_tx_antennas_y
    number_rx_antennas = number_rx_antennas_x * number_rx_antennas_y

    if split_channel_coeff:
        path_phase = np.deg2rad(path_phase)

        #include phase information, converting gains in complex-values
        complex_path_gain = path_gain * np.exp(1j * path_phase)
    else:
        complex_path_gain = path_gain

    num_rays = np.shape(departure_ele)[0]
    #number_Rx_antennas is the total number of antenna elements of the array, idem Tx
    H = np.matrix(np.zeros((number_rx_antennas, number_tx_antennas)))

    # recall that in the narrowband case, the time-domain H is the same as the
    # frequency-domain H
    # Each vector below has the x and y values for each ray. Example 2 x 25 dimension
    departure_omega = calc_omega(departure_ele, departure_azi, normalized_ant_distance)
    arrival_omega = calc_omega(arrival_ele, arrival_azi, normalized_ant_distance)

    rangetx_x = np.arange(number_tx_antennas_x)
    rangetx_y = np.arange(number_tx_antennas_y)
    rangerx_x = np.arange(number_rx_antennas_x)
    rangerx_y = np.arange(number_rx_antennas_y)

    for ray_i in range(num_rays):
        # departure
        vecx = np.exp(1j * departure_omega[0, ray_i] * rangetx_x)
        vecy = np.exp(1j * departure_omega[1, ray_i] * rangetx_y)
        departure_vec = np.matrix(np.kron(vecy, vecx))
        # arrival
        vecx = np.exp(1j * arrival_omega[0, ray_i] * rangerx_x)
        vecy = np.exp(1j * arrival_omega[1, ray_i] * rangerx_y)
        arrival_vec = np.matrix(np.kron(vecy, vecx))

        H = H + complex_path_gain[ray_i] * arrival_vec.conj().T * departure_vec

    return H


def get_nb_ula_mimo_channel(departure_azi: float, arrival_azi: float, path_gain,
                                number_tx_antennas: int, number_rx_antennas: int,
                                normalized_ant_distance=0.5, angle_with_array_normal=0,
                                path_phase=None, split_channel_coeff=False, random_phase=False):
    """
    assumes one beam per antenna element

    the first column will be the elevation angle, and the second column 
    is the azimuth angle correspondingly.p_gain will be a matrix size of (L, 1)
    departure angle/arrival angle will be a matrix as size of (L, 2), 
    where L is the number of paths

    t1 will be a matrix of size (nt, nr), each
    element of index (i,j) will be the received
    power with the i-th precoder and the j-th
    combiner in the departing and arrival codebooks
    respectively
    """
    azimuths_tx = np.deg2rad(departure_azi)
    azimuths_rx = np.deg2rad(arrival_azi)
    # nt = number_Rx_antennas * number_Tx_antennas #np.power(antenna_number, 2)
    m = np.shape(azimuths_tx)[0]  # number of rays
    H = np.matrix(np.zeros((number_rx_antennas, number_tx_antennas)))

    if split_channel_coeff:
        #generate uniformly distributed random phase in radians
        if random_phase:
            path_phase = 2*np.pi * np.random.randn(len(path_gain))
        else:
            #convert from degrees to radians
            path_phase = np.deg2rad(path_phase)

        #include phase information, converting gains in complex-values
        complex_path_gain = path_gain * np.exp(1j * path_phase)
    else:
        complex_path_gain = path_gain

    # recall that in the narrowband case, the time-domain H is the same as the
    # frequency-domain H
    for i in range(m):
        # at and ar are row vectors (using Python's matrix)
        at = np.matrix(array_factor_ula(number_tx_antennas,
                                                azimuths_tx[i],
                                                normalized_ant_distance,
                                                angle_with_array_normal))
        ar = np.matrix(array_factor_ula(number_rx_antennas,
                                                azimuths_rx[i],
                                                normalized_ant_distance,
                                                angle_with_array_normal))

        H = H + complex_path_gain[i] * ar.conj().T * at  # outer product of ar Hermitian and at

    return H

def get_wb_ula_mimo_channel(departure_azi: float, arrival_azi: float, path_gain,
                                tau, carrier_f, number_tx_antennas: int,
                                number_rx_antennas: int, normalized_ant_distance=0.5,
                                angle_with_array_normal=0, split_channel_coeff=False):
    """
    Wide band mimo channel
    """
    azimuths_tx = np.deg2rad(departure_azi)
    azimuths_rx = np.deg2rad(arrival_azi)
    m = np.shape(azimuths_tx)[0]  # number of rays
    n_fft = 64
    complex_path_gain = np.zeros((n_fft, m), dtype=complex)
    bandwidth = 100e6 # MHz
    freqs = np.linspace(carrier_f - bandwidth/2, carrier_f + bandwidth/2, n_fft)

    for k in range(n_fft):
        if split_channel_coeff:
            complex_path_gain[k] = path_gain * np.exp(-2j * np.pi * freqs[k] * tau)
        else:
            complex_path_gain[k] = np.abs(path_gain) * np.exp(-2j * np.pi * freqs[k] * tau)

    # frequency-domain H
    Hf = []
    for i in range(len(freqs)):
        channel = np.matrix(np.zeros((number_rx_antennas, number_tx_antennas)), dtype=complex)
        for j in range(m):
            # at and ar are row vectors (using Python's matrix)
            at = np.matrix(array_factor_ula(number_tx_antennas,
                                                    azimuths_tx[j],
                                                    normalized_ant_distance,
                                                    angle_with_array_normal))
            ar = np.matrix(array_factor_ula(number_rx_antennas,
                                                    azimuths_rx[j],
                                                    normalized_ant_distance,
                                                    angle_with_array_normal))

            channel = channel + complex_path_gain[i][j] * ar.conj().T * at
        Hf.append(channel)

    Hf = np.array(Hf)

    return Hf

def array_factor_ula(n_ant_elements, theta, normalized_ant_distance=0.5, angle_with_array_normal=0):
    """
    Calculate array factor for ULA for angle theta. If angleWithArrayNormal=0
    (default),the angle is between the input signal and the array axis. In
    this case when theta=0, the signal direction is parallel to the array
    axis and there is no energy. The maximum values are for directions 90
        and -90 degrees, which are orthogonal with array axis.
    If angleWithArrayNormal=1, angle is with the array normal, which uses
    sine instead of cosine. In this case, the maxima are for
        thetas = 0 and 180 degrees.
    References:
    http://www.waves.utoronto.ca/prof/svhum/ece422/notes/15-arrays2.pdf
    Book by Balanis, book by Tse.
    """
    indices = np.arange(n_ant_elements)
    if angle_with_array_normal == 1:
        array_factor = np.exp(1j * 2 * np.pi * normalized_ant_distance * indices * np.sin(theta))
    else:  # default
        array_factor = np.exp(1j * 2 * np.pi * normalized_ant_distance * indices * np.cos(theta))
    array_factor = array_factor / np.sqrt(n_ant_elements)
    return array_factor  # normalize to have unitary norm
