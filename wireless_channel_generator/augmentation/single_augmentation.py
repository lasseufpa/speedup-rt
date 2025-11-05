"""
LASSE
Created by Cláudio Modesto

Script to generate the paper results considering a single RT scenarios
"""

import argparse
import os
import copy
from process_data import RaytracingGenerator
from poc_interpolators import Interpolators
from utils import (get_nmse, create_geometric_channels, shrink_dim_per_rx)
from matplotlib import pyplot as plt
import numpy as np

# create results directory
if not os.path.isdir("results/single"):
    os.makedirs("results/single", exist_ok=True)


# Antenna specifications for ULA
ula_parameters = {"n_tx_ant": 8, "n_rx_ant": 4}
# Antenna specifications for UPA
upa_parameters = {"n_tx_ant_x": 4, "n_tx_ant_y": 4, "n_rx_ant_x": 8, "n_rx_ant_y": 4}
ANGLE_WITH_ARRAY_NORMAL = 0
NORMALIZED_DISTANCE = 0.5

parser = argparse.ArgumentParser()
parser.add_argument(
    "--file", "-f", help="Path to a single RT dataset", 
    type=str, required=True
)
parser.add_argument(
    "--interp-type", "-i", help="Type of Interpolation [linear_2 | linear_n| poly]", 
    type=str, required=True
)
parser.add_argument(
    "--plot-type", "-p", help="Type of plot [cdf | hist]", 
    type=str, required=True
)
parser.add_argument(
    "--channel", "-c", help="Type of channel [wb | nb]", 
    type=str, required=True
)
parser.add_argument(
    "--n-terms", "-n", help="Number of scenes between two samples to be generated", 
    type=int, required=True
)

args = parser.parse_args()

data_generator = RaytracingGenerator(args.file)
augmentor = Interpolators()
OUTPUT_PATH_NAME = f"results/single/numerical_results_{args.interp_type}.txt"


# get ray tracing parameters
orig_processed_data = data_generator.get_dataset()
# get ray tracing parameters with complex gain and phase splitted
orig_processed_data_w_split = data_generator.get_dataset(split_channel_coeff=True)

shrinked_orig_proc_data = shrink_dim_per_rx(copy.deepcopy(orig_processed_data))
shrinked_orig_proc_data_w_split = shrink_dim_per_rx(
                                    copy.deepcopy(orig_processed_data_w_split))
channel_nmse = [] # placeholder for final NMSE results

# get ground truth mimo geometric channel
orig_wireless_channels = create_geometric_channels(
                                                shrinked_orig_proc_data,
                                                args.ant_pattern,
                                                args.channel_type,
                                                ula_parameters,
                                                upa_parameters,
                                                NORMALIZED_DISTANCE,
                                                ANGLE_WITH_ARRAY_NORMAL)

N_TERMS = args.n_terms
if args.interp_type in ("linear_2", "linear_n", "poly"):
    if args.interp_type == "linear_2":
        aug_method = augmentor.linear_2_factor_interp
    elif args.interp_type == "linear_n":
        aug_method = augmentor.linear_n_factor_interp
    elif args.interp_type == "poly":
        aug_method = augmentor.poly_interp
    else:
        aug_method = augmentor.linear_2_factor_interp

    # carry out the ray tracing interpolation process
    interp_processed_data = aug_method(shrinked_orig_proc_data_w_split, n_terms=N_TERMS)

    # get mimo geometric channel using interpolated mpc parameters
    predicted_wireless_channels = create_geometric_channels(interp_processed_data,
                                                    args.ant_pattern,
                                                    args.channel_type,
                                                    ula_parameters,
                                                    upa_parameters,
                                                    NORMALIZED_DISTANCE,
                                                    ANGLE_WITH_ARRAY_NORMAL,
                                                    split_channel_coeff=True)

    # obtain channel nmse for each scene
    channel_nmse = [get_nmse(np.squeeze(orig_wireless_channels[k]),
                            np.squeeze(predicted_wireless_channels[k]),
                            convert_db=True) for k in range(len(orig_wireless_channels))]

elif args.interp_type == "matrix":
    # carry out the matrix interpolation
    predicted_wireless_channels = augmentor.matrix_n_interp(orig_wireless_channels, n_terms=N_TERMS)

    # obtain channel nmse for each scene
    channel_nmse = [get_nmse(orig_wireless_channels[k],
                    predicted_wireless_channels[k], convert_db=True) for k
                        in range(len(orig_wireless_channels))]


if args.plot_type == "hist":
    sorted_nmse = np.sort([x for x in channel_nmse if not np.isinf(x)])
    with open(OUTPUT_PATH_NAME, "a", encoding="utf-8") as f:
        print(f"== Histogram Channel Augmentation \n \
            Our method Max. NMSE: {np.max(sorted_nmse)} \n \
            Our method Mean NMSE: {np.mean(sorted_nmse)}", file=f)

    plt.hist(sorted_nmse,
                alpha=0.5,
                bins=10,
                linewidth=1.5)

    plt.legend(fontsize=9)
    plt.ylabel("Occurrences", fontsize=15)
    plt.xlabel("$NMSE_{db}$", fontsize=15)
    plt.savefig(f"results/single/{args.interp_type}_hist_nmse.pdf",
                bbox_inches="tight")
    plt.close()

elif args.plot_type == "cdf":
    sorted_nmse = np.sort([x for x in channel_nmse if not np.isinf(x)])
    with open(OUTPUT_PATH_NAME, "a", encoding="utf-8") as f:
        print(f"== CDF Channel Augmentation: \n \
            Our method Max. NMSE: {np.max(sorted_nmse)} \n \
            Our method Mean NMSE: {np.mean(sorted_nmse)}", file=f)
    cdf = np.arange(1, len(sorted_nmse) + 1) / len(sorted_nmse)

    plt.plot(sorted_nmse, cdf, linewidth=2, linestyle="solid")
    plt.legend(fontsize=9)
    plt.ylabel("Cumulative probability", fontsize=15)
    plt.xlabel("$NMSE_{db}$", fontsize=15)
    plt.grid()
    plt.savefig(f"results/single/{args.interp_type}_cdf_nmse.pdf",
                bbox_inches="tight")
    plt.close()
