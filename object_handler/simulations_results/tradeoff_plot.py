""" Generate the trade off plot """

from matplotlib import pyplot as plt
import numpy as np
import os
import argparse

def parse_args():
    '''
    Define the parser arguments to choose the plot.
    '''
    parser = argparse.ArgumentParser(description="Generate the Trade-off Plot.")
    parser.add_argument("--solo", "-s", required=True, type=int,
                        help="Number of first dur/nmses to run (solo)")
    parser.add_argument("--mixed", "-m", required=True, type=int,
                        help="Number of second dur/nmses to run (mixed)")
    return parser.parse_args()

def load_rt_duration_data(file_number):
    '''
    Function to load durations without mixing.
    '''
    np_load = np.load(f"../npzs/duration/rt_durations{file_number}.npz")
    return [
        np_load["rt_duration_cmap"],
        np_load["rt_duration_sphere"],
        np_load["rt_duration_rectangle"],
        np_load["rt_duration_interactions"],
        np_load["rt_duration_quadric"],
        np_load["rt_duration_vertex"]
    ]

def load_nmse_data(file_number):
    '''
    Function to load nmse without mixing.
    '''
    np_load = np.load(f"../npzs/nmse/nmses{file_number}.npz")
    return [
        np.array([x for x in np_load["hs_freq_cmap"] if np.isfinite(x) and -100 < x < 100])[:-5],
        np.array([x for x in np_load["hs_freq_sphere"] if np.isfinite(x) and -100 < x < 100])[:-12],
        np.array([x for x in np_load["hs_freq_rectangle"] if np.isfinite(x) and -100 < x < 100])[:-12],
        np.array([x for x in np_load["hs_freq_interactions"] if np.isfinite(x) and -100 < x < 100])[:-12],
        np.array([x for x in np_load["hs_freq_quadric"] if np.isfinite(x) and -100 < x < 100])[:-12],
        np.array([x for x in np_load["hs_freq_vertex"] if np.isfinite(x) and -100 < x < 100])[:-12]
    ]

def load_mixed_rt_duration_data(file_number):
    '''
    Function to load mixed durations
    '''
    np_load = np.load(f"../npzs/duration/rt_durations{file_number}.npz")
    return [
        np_load["rt_duration_cmap_vertex"],
        np_load["rt_duration_sphere_vertex"],
        np_load["rt_duration_rectangle_vertex"],
        np_load["rt_duration_interactions_vertex"],
        np_load["rt_duration_cmap_quadric"],
        np_load["rt_duration_sphere_quadric"],
        np_load["rt_duration_rectangle_quadric"],
        np_load["rt_duration_interactions_quadric"]
    ]

def load_mixed_nmse_data(file_number):
    '''
    Function to load mixed nmses
    '''
    np_load = np.load(f"../npzs/nmse/nmses{file_number}.npz")
    return [
        np_load["hs_freq_cmap_vertex"],
        np_load["hs_freq_sphere_vertex"],
        np_load["hs_freq_rectangle_vertex"],
        np_load["hs_freq_interactions_vertex"],
        np_load["hs_freq_cmap_quadric"],
        np_load["hs_freq_sphere_quadric"],
        np_load["hs_freq_rectangle_quadric"],
        np_load["hs_freq_interactions_quadric"]
    ]

if __name__ == "__main__":
    args = parse_args()

    # Labels
    solo_labels = ['Coverage Map (CMAP)', 'Sphere', 'Rectangle', 'Interactions',
                   'Edge collapse', 'Vertex clustering']
    mixed_labels = ['CMAP + Vertex', 'Sphere + Vertex', 'Rectangle + Vertex', 'Interactions + Vertex',
                    'CMAP + Edge collapse', 'Sphere + Edge collapse', 'Rectangle + Edge collapse', 'Interactions + Edge collapse']

    # Load data
    solo_durations = load_rt_duration_data(args.solo)
    solo_nmses = load_nmse_data(args.solo)
    mixed_durations = load_mixed_rt_duration_data(args.mixed)
    mixed_nmses = load_mixed_nmse_data(args.mixed)

    # Plot solo points
    for i in range(len(solo_durations)):
        plt.scatter(np.sum(solo_durations[i]) / 60, np.mean(solo_nmses[i]),
                    label=solo_labels[i], s=80)

    # Plot mixed points
    for j in range(len(mixed_durations)):
        plt.scatter(np.sum(mixed_durations[j]) / 60, np.mean(mixed_nmses[j]),
                    label=mixed_labels[j], marker='x', s=80)

    # Final plot settings
    plt.xlabel('RT duration (min)', fontsize=15)
    plt.ylabel('Average NMSE (dB)', fontsize=15)
    plt.legend(bbox_to_anchor=(1, 1))
    plt.tight_layout()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)

    # Save plot
    file_numbers = str(args.solo) + str(args.mixed)
    save_fig_path = os.path.join(str(file_numbers) + "tradeoff_plot.pdf")
    plt.savefig(save_fig_path, bbox_inches='tight')
    plt.close()

