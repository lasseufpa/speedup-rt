"""
LASSE
Created by Cláudio Modesto

Script to generate new channels in a production environments
"""

import argparse
import copy
from process_data import RaytracingGenerator
from prod_interpolators import Interpolators

from utils import create_geometric_channels, shrink_dim_per_rx

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
    "--n-terms", "-n", help="Number of scenes between two samples to be generated", 
    type=int, required=True
)
parser.add_argument(
    "--ant-pattern", "-a", help="Antenna pattern [ula | upa]", 
    type=str, required=True
)
parser.add_argument(
    "--channel-type", "-c", help="Antenna pattern [wb | nb]", 
    type=str, required=True
)

args = parser.parse_args()

data_generator = RaytracingGenerator(args.file)
augmentor = Interpolators()

# get ray tracing parameters
orig_processed_data = data_generator.get_dataset()
# get ray tracing parameters with complex gain and phase splitted
orig_processed_data_w_split = data_generator.get_dataset(split_channel_coeff=True)

shrinked_orig_proc_data = shrink_dim_per_rx(copy.deepcopy(orig_processed_data))
shrinked_orig_proc_data_w_split = shrink_dim_per_rx(
                                    copy.deepcopy(orig_processed_data_w_split))
channel_nmse = [] # placeholder for final NMSE results

# interpopolation
N_TERMS = args.n_terms

# carry out the ray tracing interpolation process
interp_processed_data = augmentor.linear_n_factor_interp(shrinked_orig_proc_data_w_split,
                                    n_terms=N_TERMS)

orig_wireless_channels = create_geometric_channels(shrinked_orig_proc_data_w_split,
                                                args.ant_pattern,
                                                args.channel_type,
                                                ula_parameters,
                                                upa_parameters,
                                                NORMALIZED_DISTANCE,
                                                ANGLE_WITH_ARRAY_NORMAL,
                                                split_channel_coeff=True)

# get mimo geometric channel using interpolated mpc parameters
augmented_wireless_channels = create_geometric_channels(interp_processed_data,
                                                args.ant_pattern,
                                                args.channel_type,
                                                ula_parameters,
                                                upa_parameters,
                                                NORMALIZED_DISTANCE,
                                                ANGLE_WITH_ARRAY_NORMAL,
                                                split_channel_coeff=True,
                                                random_phase=False)

print("Number of channels before augmentation: ", len(orig_wireless_channels))
print("Number of channels after augmentation: ", len(augmented_wireless_channels))
