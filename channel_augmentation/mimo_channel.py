"""
LASSE
Created by Aldebaro Klautau
Edited by Cláudio Modesto

Script to generated and post-processing MPC parameters to generate
deterministic channels
"""

import numpy as np

def calc_omega(elevation_angles, azimuth_angles, normalized_ant_distance = 0.5):
    sin_elevations = np.sin(elevation_angles)
    omegax = 2 * np.pi * normalized_ant_distance * sin_elevations * np.cos(azimuth_angles)
    omegay = 2 * np.pi * normalized_ant_distance * sin_elevations * np.sin(azimuth_angles)
    return np.matrix((omegax, omegay))

def get_narrow_band_UPA_MIMO_channel(departure_elevation,departure_azimuth,arrival_elevation,arrival_azimuth, complex_gain,
                                number_Tx_antennasX, number_Tx_antennasY, number_Rx_antennasX,
                                number_Rx_antennasY, pathPhases = None, normalized_ant_distance=0.5):
    """Uses UPAs at both TX and RX.
    Will assume that all 4 normalized distances (Tx and Rx, x and y) are the same.
    """
    number_Tx_antennas = number_Tx_antennasX * number_Tx_antennasY
    number_Rx_antennas = number_Rx_antennasX * number_Rx_antennasY

    numRays = np.shape(departure_elevation)[0]
    #number_Rx_antennas is the total number of antenna elements of the array, idem Tx
    H = np.matrix(np.zeros((number_Rx_antennas, number_Tx_antennas)))


    # recall that in the narrowband case, the time-domain H is the same as the
    # frequency-domain H
    # Each vector below has the x and y values for each ray. Example 2 x 25 dimension
    departure_omega = calc_omega(departure_elevation, departure_azimuth, normalized_ant_distance)
    arrival_omega = calc_omega(arrival_elevation, arrival_azimuth, normalized_ant_distance)

    rangeTx_x = np.arange(number_Tx_antennasX)
    rangeTx_y = np.arange(number_Tx_antennasY)
    rangeRx_x = np.arange(number_Rx_antennasX)
    rangeRx_y = np.arange(number_Rx_antennasY)
    for ray_i in range(numRays):
        #departure
        vecx = np.exp(1j * departure_omega[0,ray_i] * rangeTx_x)
        vecy = np.exp(1j * departure_omega[1,ray_i] * rangeTx_y)
        departure_vec = np.matrix(np.kron(vecy, vecx))
        #arrival
        vecx = np.exp(1j * arrival_omega[0,ray_i] * rangeRx_x)
        vecy = np.exp(1j * arrival_omega[1,ray_i] * rangeRx_y)
        arrival_vec = np.matrix(np.kron(vecy, vecx))

        H = H + complex_gain[ray_i] * arrival_vec.conj().T * departure_vec
    return H


def get_narrow_band_ULA_MIMO_channel(azimuths_tx: float, azimuths_rx: float, path_gain,
                                number_Tx_antennas: int, number_Rx_antennas: int,
                                normalized_ant_distance=0.5, angle_with_array_normal=0,
                                path_phase=None, split_channel_coeff=False, random_phase=False):
    """
    assumes one beam per antenna element

    the first column will be the elevation angle, and the second column is the azimuth angle correspondingly.
    p_gain will be a matrix size of (L, 1)
    departure angle/arrival angle will be a matrix as size of (L, 2), where L is the number of paths

    t1 will be a matrix of size (nt, nr), each
    element of index (i,j) will be the received
    power with the i-th precoder and the j-th
    combiner in the departing and arrival codebooks
    respectively

    :param departure_angles: ((elevation angle, azimuth angle),) (L, 2) where L is the number of paths
    :param arrival_angles: ((elevation angle, azimuth angle),) (L, 2) where L is the number of paths
    :param p_gaindB: path gain (L, 1) in dB where L is the number of paths
    :param number_Rx_antennas, number_Tx_antennas: number of antennas at Rx and Tx, respectively
    :param pathPhases: in degrees, same dimension as path_gain
    :return:
    """
    azimuths_tx = np.deg2rad(azimuths_tx)
    azimuths_rx = np.deg2rad(azimuths_rx)
    # nt = number_Rx_antennas * number_Tx_antennas #np.power(antenna_number, 2)
    m = np.shape(azimuths_tx)[0]  # number of rays
    H = np.matrix(np.zeros((number_Rx_antennas, number_Tx_antennas)))

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
        at = np.matrix(array_factor_ula(number_Tx_antennas,
                                                azimuths_tx[i],
                                                normalized_ant_distance,
                                                angle_with_array_normal))
        ar = np.matrix(array_factor_ula(number_Rx_antennas,
                                                azimuths_rx[i],
                                                normalized_ant_distance,
                                                angle_with_array_normal))
        H = H + complex_path_gain[i] * ar.conj().T * at  # outer product of ar Hermitian and at

    return H

def array_factor_ula(n_ant_elements, theta, normalized_ant_distance=0.5, angleWithArrayNormal=0):
    '''
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
    '''
    indices = np.arange(n_ant_elements)
    if (angleWithArrayNormal == 1):
        arrayFactor = np.exp(1j * 2 * np.pi * normalized_ant_distance * indices * np.sin(theta))
    else:  # default
        arrayFactor = np.exp(1j * 2 * np.pi * normalized_ant_distance * indices * np.cos(theta))
    arrayFactor = arrayFactor / np.sqrt(n_ant_elements)
    return arrayFactor  # normalize to have unitary norm

def get_codebook_operated_channel(H, Wt, Wr):
    if Wr is None: #only 1 antenna at Rx, and Wr was passed as None
        return H * Wt
    if Wt is None: #only 1 antenna at Tx
        return Wr.conj().T * H
    return Wr.conj().T * H * Wt # return equivalent channel after precoding and combining

def dft_codebook(dim):
    seq = np.matrix(np.arange(dim))
    mat = seq.conj().T * seq
    w = np.exp(-1j * 2 * np.pi * mat / dim)

    return w

def get_DFT_operated_channel(H, number_tx_antennas, number_rx_antennas):
    wt = dft_codebook(number_tx_antennas)
    wr = dft_codebook(number_rx_antennas)
    dict_operated_channel = wr.conj().T * H * wt

    return dict_operated_channel  # return equivalent channel after precoding and combining
