"""
LASSE
Ray tracing acceleration script for generating results
with multiple scenarios
Created by Cláudio Modesto
"""

import argparse
from pathlib import Path
import glob
import os
import numpy as np
from process_data import RaytracingGenerator
from interpolators import Interpolators
from utils import get_nmse, create_geometric_channels, shrink_dim_per_rx
from matplotlib import pyplot as plt

plt.rcParams["pdf.fonttype"] = 42
# create results directory
if not os.path.isdir("results/multiple"):
    os.makedirs("results/multiple", exist_ok=True)

# Antennas specifications
N_TX_ANTENNAS = 8
N_RX_ANTENNAS = 4
ANGLE_WITH_ARRAY_NORMAL = 0
NORMALIZED_DISTANCE = 0.5

parser = argparse.ArgumentParser()
parser.add_argument(
    "--interp-type", "-i", 
    help="Type of Interpolation [linear_2 | linear_n | poly]", 
    type=str,
    required=True
)
parser.add_argument(
    "--dir", "-s",
    help="Path to ray tracing datasets",
    type=str,
    required=True
)
parser.add_argument(
    "--plot-type", "-p", help="Type of plot [cdf | hist]", 
    type=str, required=True
)
parser.add_argument(
    "--baseline",
    help="plot baseline interpolation", 
    action="store_true",
    required=False
)

args = parser.parse_args()

OUTPUT_PATH_NAME = f"results/multiple/numerical_results_{args.interp_type}.txt"
if os.path.isfile(OUTPUT_PATH_NAME):
    os.remove(OUTPUT_PATH_NAME)
else:
    Path(OUTPUT_PATH_NAME).touch()

results_per_scenario, scenario_names = [], []
channel_nmse, channels_nmse = [], []
for ds_name in sorted(glob.glob(f"{args.dir}/*.mb")):
    scenario_names.append(ds_name.split("/")[-1].split("_")[0].title())
    results_per_realization = []

    data_generator = RaytracingGenerator(ds_name)
    augmentor = Interpolators()
    orig_processed_data = data_generator.get_dataset()
    orig_processed_data_w_split = data_generator.get_dataset(split_channel_coeff=True)

    extracted_orig_proc_data = shrink_dim_per_rx(orig_processed_data)
    extracted_orig_proc_data_w_split = shrink_dim_per_rx(orig_processed_data_w_split)

    # get the ground truth wireless channels
    orig_wireless_channels = create_geometric_channels(
                                            extracted_orig_proc_data,
                                            N_TX_ANTENNAS,
                                            N_RX_ANTENNAS,
                                            NORMALIZED_DISTANCE,
                                            ANGLE_WITH_ARRAY_NORMAL)

    if args.interp_type == "linear_2":
        ray_gen = augmentor.linear_2_factor_interp
        n_terms = [2]
    elif args.interp_type == "linear_n":
        ray_gen = augmentor.linear_n_factor_interp
        n_terms = [10]
    elif args.interp_type == "poly":
        ray_gen = augmentor.poly_interp
        n_terms = [2]
    else: # default
        n_terms = [2]
        ray_gen = augmentor.linear_2_factor_interp

    N_REALIZATIONS = 50 # number of realization (different channels will be generated)
    results_per_factor = []
    for factor in n_terms:
        for sample in range(N_REALIZATIONS):
            channel_nmse = []
            # carry out the ray tracing interpolation process
            interp_processed_data = ray_gen(extracted_orig_proc_data_w_split,
                                            factor)
            predicted_wireless_channels = create_geometric_channels(interp_processed_data,
                                                                N_TX_ANTENNAS,
                                                                N_RX_ANTENNAS,
                                                                NORMALIZED_DISTANCE,
                                                                ANGLE_WITH_ARRAY_NORMAL,
                                                                split_channel_coeff=True)

            # linear interpolation results
            linear_interp_channel_nmse = [get_nmse(orig_wireless_channels[k],
                                        predicted_wireless_channels[k],
                                        convert_db=True) for k in
                                                    range(len(orig_wireless_channels))]
            if args.baseline:
                # carry out matrix interpolation
                interpolated_matrix = augmentor.matrix_n_interp(orig_wireless_channels, n_terms=factor)

                # matrix interpolation results
                matrix_interp_channel_nmse = [get_nmse(orig_wireless_channels[k],
                                interpolated_matrix[k],
                                convert_db=True) for k in range(len(orig_wireless_channels))]

            if args.baseline:
                channel_nmse = [linear_interp_channel_nmse[:-1], matrix_interp_channel_nmse[:-1]]
                results_per_realization.append(channel_nmse)
            else:
                channel_nmse = linear_interp_channel_nmse[:-1]
                results_per_realization.append([channel_nmse])

        results_per_factor.append(results_per_realization)
    results_per_scenario.append(results_per_factor)
# convert to numpy array (shape (n_scenarios, n_factors, n_realizations, n_receiver, n_channels))
results_per_scenario = np.array(results_per_scenario)

# take average for each discrete time instant of the realizations
avg_nmse_at_n = []
for i in range(results_per_scenario.shape[1]):
    avg_nmse_at_n.append(list(np.average(results_per_scenario[:, i], axis=1)))

if args.plot_type == "hist":
    linear_colors = ["#1f77b4", "#2ca02c", "purple"]
    matrix_colors = ["red", "goldenrod", "blue"]
    for i in range(len(avg_nmse_at_n[0])):
        linear_sorted_nmse = np.sort([x for x in avg_nmse_at_n[0][i][0] if not np.isinf(x)])
        with open(OUTPUT_PATH_NAME, "a", encoding="utf-8") as f:
            print(f"== Scenario: {scenario_names[i]} \n \
                Our method Max. NMSE: {np.max(linear_sorted_nmse)} \n \
                Our method Mean. NMSE: {np.mean(linear_sorted_nmse)}", file=f)

        if args.baseline:
            matrix_sorted_nmse = np.sort([x for x in avg_nmse_at_n[0][i][1] if not np.isinf(x)])
            with open(OUTPUT_PATH_NAME, "a", encoding="utf-8") as f:
                print(f"== Scenario: {scenario_names[i]} \n \
                Baseline Max. NMSE: {np.max(matrix_sorted_nmse)} \n \
                Baseline Mean. NMSE: {np.mean(matrix_sorted_nmse)}", file=f)

        plt.hist(linear_sorted_nmse,
                        alpha=0.5,
                        bins=10,
                        color=linear_colors.pop(),
                        linewidth=1.5,
                        label=f"ARTS method. at {scenario_names[i]}")

        if args.baseline:
            plt.hist(matrix_sorted_nmse,
            alpha=0.7,
            linewidth=1.5,
            color=matrix_colors.pop(),
            edgecolor="black",
            bins=10,
            label=f"Matrix interp. at {scenario_names[i]}")

    plt.legend(fontsize=9)
    plt.ylabel("Occurrences", fontsize=15)
    plt.xlabel("$NMSE_{db}$", fontsize=15)
    plt.savefig(f"results/multiple/{args.interp_type}_hist_nmse.pdf",
                bbox_inches="tight")
    plt.close()

elif args.plot_type == "cdf":
    for i in range(len(avg_nmse_at_n[0])):
        linear_sorted_nmse = np.sort([x for x in avg_nmse_at_n[0][i][0] if not np.isinf(x)])
        with open(OUTPUT_PATH_NAME, "a", encoding="utf-8") as f:
            print(f"== Scenario: {scenario_names[i]} \n \
                Our method Max. NMSE: {np.max(linear_sorted_nmse)} \n \
                Our method Mean. NMSE: {np.mean(linear_sorted_nmse)}", file=f)
        linear_cdf = np.arange(1, len(linear_sorted_nmse) + 1) / len(linear_sorted_nmse)
        
        plt.plot(linear_sorted_nmse, linear_cdf, linewidth=2, linestyle="solid",
                    label=f"ARTS method at {scenario_names[i]}")

        if args.baseline:
            matrix_sorted_nmse = np.sort([x for x in avg_nmse_at_n[0][i][1] if not np.isinf(x)])
            with open(OUTPUT_PATH_NAME, "a", encoding="utf-8") as f:
                print(f"== Scenario: {scenario_names[i]} \n \
                Baseline Max. NMSE: {np.max(matrix_sorted_nmse)} \n \
                Baseline Mean. NMSE: {np.mean(matrix_sorted_nmse)}", file=f)
            matrix_cdf = np.arange(1, len(matrix_sorted_nmse) + 1) / len(matrix_sorted_nmse)

            if args.baseline:
                plt.plot(matrix_sorted_nmse, matrix_cdf, linewidth=2, linestyle="--",
                        label=f"Matrix interp. at {scenario_names[i]}")

    plt.legend(fontsize=9)
    plt.ylabel("Cumulative probability", fontsize=15)
    plt.xlabel("$NMSE_{db}$", fontsize=15)
    plt.grid()
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    plt.tight_layout()
    plt.savefig(f"results/multiple/{args.interp_type}_cdf_nmse.pdf",
                bbox_inches="tight")
    plt.close()
