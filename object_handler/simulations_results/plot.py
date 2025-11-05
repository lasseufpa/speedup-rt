""" Plotting Functions """

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt

def parse_args():
    '''
    Define the parser arguments to choose the plots.
    '''
    parser = argparse.ArgumentParser(description="Generate Ray Tracing Duration plot.")
    parser.add_argument("--number_of_folder", "-n",
                        required=True,
                        type=int,
                        help="Number of the dur/nmses folder to run")
    parser.add_argument("--type_of_simulation", "-t",
                        required=True,
                        type=str,
                        help="Type of simulation (mixed or normal)")
    return parser.parse_args()

def load_rt_duration_data(file_number):
    '''
    Load the ray tracing durations from the npz                    
    '''
    np_load = np.load(f"../npzs/duration/rt_durations{file_number}.npz")
    return {
        "no_mesh_simplification": np_load["rt_duration_normal"],
        "cmap_cut": np_load["rt_duration_cmap"],
        "sphere_cut": np_load["rt_duration_sphere"],
        "rectangle_cut": np_load["rt_duration_rectangle"],
        "interactions_cut": np_load["rt_duration_interactions"],
        "vertex_clustering": np_load["rt_duration_vertex"],
        "quadric_edge_collapse": np_load["rt_duration_quadric"]
    }

def load_rt_duration_mixed_data(file_number):
    '''
    Load the ray tracing durations (mixed) from the npz                    
    '''
    np_load = np.load(f"../npzs/duration/rt_durations{file_number}.npz")
    return {
        "cmap_vertex": np_load["rt_duration_cmap_vertex"],
        "sphere_vertex": np_load["rt_duration_sphere_vertex"],
        "rectangle_vertex": np_load["rt_duration_rectangle_vertex"],
        "interactions_vertex": np_load["rt_duration_interactions_vertex"],
        "cmap_quadric": np_load["rt_duration_cmap_quadric"],
        "sphere_quadric": np_load["rt_duration_sphere_quadric"],
        "rectangle_quadric": np_load["rt_duration_rectangle_quadric"],
        "interactions_quadric": np_load["rt_duration_interactions_quadric"]
    }

def load_nmse_data(file_number):
    '''
    Load nmses from npz and perform a preprocessing on 
    the data to remove outliers and keep 150 values.
    '''
    np_load = np.load(f"../npzs/nmse/nmses{file_number}.npz")
    return {
        "cmap_cut": np.array([x for x in np_load["hs_freq_cmap"]
                              if np.isfinite(x) and -100 < x < 100])[:-5],
        "sphere_cut": np.array([x for x in np_load["hs_freq_sphere"]
                                if np.isfinite(x) and -100 < x < 100])[:-12],
        "rectangle_cut": np.array([x for x in np_load["hs_freq_rectangle"]
                                          if np.isfinite(x) and -100 < x < 100])[:-12],
        "interactions_cut": np.array([x for x in np_load["hs_freq_interactions"]
                                      if np.isfinite(x) and -100 < x < 100])[:-12],
        "vertex_clustering": np.array([x for x in np_load["hs_freq_vertex"]
                                       if np.isfinite(x) and -100 < x < 100])[:-12],
        "quadric_edge_collapse": np.array([x for x in np_load["hs_freq_quadric"]
                                           if np.isfinite(x) and -100 < x < 100])[:-12]
    }

def load_nmse_mixed_data(file_number):
    '''
    Load nmses from npz (mixed).
    '''
    np_load = np.load(f"../npzs/nmse/nmses{file_number}.npz")
    return {
        "cmap_vertex": np_load["hs_freq_cmap_vertex"],
        "sphere_vertex": np_load["hs_freq_sphere_vertex"],
        "rectangle_vertex": np_load["hs_freq_rectangle_vertex"],
        "interactions_vertex": np_load["hs_freq_interactions_vertex"],
        "cmap_quadric": np_load["hs_freq_cmap_quadric"],
        "sphere_quadric": np_load["hs_freq_sphere_quadric"],
        "rectangle_quadric": np_load["hs_freq_rectangle_quadric"],
        "interactions_quadric": np_load["hs_freq_interactions_quadric"]
    }

def calculate_avg_std(data):
    '''
    Evaluate average and standard deviation.
    '''
    stats = {}
    for data_key, values in data.items():
        stats[data_key] = {
            "mean": values.mean(),
            "std": values.std()
        }
    return stats

def bar_plot_duration_sum(data, file_number, labels):
    '''
    Bar chart summing up all values for each type of rt duration.
    '''
    values = [np.sum(i) for i in data.values()]
    bar_width = 1
    bars = [bar_width * i for i in range(1, len(values) + 1)]

    plt.figure(figsize=(8, 7))

    for i, label in enumerate(labels):
        plt.bar(bars[i], values[i], bar_width,
                capsize=5, label=label, edgecolor="black", linewidth=2)

    # Customize plot
    plt.ylabel("Total ray tracing duration (s)", fontsize=15)
    plt.xticks(bars, labels, rotation=30, ha='right', fontsize=15)
    plt.gca().xaxis.set_label_coords(0.5, -0.03)
    plt.tight_layout()
    plt.legend(loc="upper center", bbox_to_anchor=(0.47, 1), fontsize=13)

    # Save plot
    save_fig_path = os.path.join(file_number, "rt_duration_plots", "ray_tracing_duration_sum.pdf")
    os.makedirs(os.path.dirname(save_fig_path), exist_ok=True)
    plt.savefig(save_fig_path, bbox_inches='tight')
    plt.close()

def bar_plot_nmse(stats, file_number, labels, pargs):
    '''
    Bar plot for nmses.
    '''
    bar_plot_means = [stat["mean"] for stat in stats.values()]
    c = [stat["std"] for stat in stats.values()]

    colors = ["#ff7f0e",
              "#2ca02c", 
              "#d62728", 
              "#9467bd", 
              "#8c564b", 
              "#e377c2"]

    plt.figure(figsize=(10, 10))

    bar_width = 1
    bars = [bar_width * i for i in range(1, len(bar_plot_means) + 1)]
    if pargs.type_of_simulation == "original":
        for i, (label, color) in enumerate(zip(labels, colors)):
            plt.bar(bars[i],
                    bar_plot_means[i],
                    bar_width,
                    yerr=c[i],
                    capsize=5,
                    label=label,
                    edgecolor="black",
                    linewidth=2,
                    color=color
                )
    else:
        for i, label in enumerate(labels):
            plt.bar(bars[i],
                    bar_plot_means[i],
                    bar_width,
                    yerr=c[i],
                    capsize=5,
                    label=label,
                    edgecolor="black",
                    linewidth=2,
                )

    # Customize plot
    plt.ylabel("$NMSE_{dB}$ mean", fontsize=15)
    plt.xticks(bars, labels, rotation=30, ha='right', fontsize=15)
    plt.tight_layout()
    plt.legend(fontsize=12)

    # Save plot
    save_fig_path = os.path.join(file_number, "nmse_plots", "nmse_mean_std_plot.pdf")
    os.makedirs(os.path.dirname(save_fig_path), exist_ok=True)
    plt.savefig(save_fig_path, bbox_inches='tight')
    plt.close()

def bar_plot_duration_stats(stats, file_number, labels):
    '''
    Bar plot for ray tracing durations stats.
    '''
    bar_plot_means = [stat["mean"] for stat in stats.values()]
    c = [stat["std"] for stat in stats.values()]

    bar_width = 1
    bars = [bar_width * i for i in range(1, len(bar_plot_means) + 1)]

    plt.figure(figsize=(8, 7))

    for i, label in enumerate(labels):
        plt.bar(bars[i], bar_plot_means[i], bar_width, yerr=c[i],
                capsize=5, label=label, edgecolor="black", linewidth=2)

    # Customize plot
    plt.ylabel("Ray tracing duration (s)", fontsize=15)
    plt.xticks(bars, labels, rotation=30, ha='right', fontsize=15)
    plt.gca().xaxis.set_label_coords(0.5, -0.03)
    plt.tight_layout()
    plt.legend(loc="upper center", bbox_to_anchor=(0.47, 1), fontsize=13)

    # Save plot
    save_fig_path = os.path.join(file_number, "rt_duration_plots", "ray_tracing_duration.pdf")
    os.makedirs(os.path.dirname(save_fig_path), exist_ok=True)
    plt.savefig(save_fig_path, bbox_inches='tight')
    plt.close()

def nmse_cumulative_sum_plot(data, file_number, labels, pargs):
    '''
    Cumulative sum plot for nmses
    '''

    colors = ["#ff7f0e",
              "#2ca02c",
              "#d62728", 
              "#9467bd", 
              "#8c564b", 
              "#e377c2"]

    last_row = []

    if pargs.type_of_simulation == "original":
        for data, color, label in zip(data, colors, labels):
            plt.plot(np.cumsum(data), color=color, label=label)
            last_row.append(np.cumsum(data)[-1])
    else:
        for data, label in zip(data, labels):
            plt.plot(np.cumsum(data), label=label)
            last_row.append(np.cumsum(data)[-1])

    plt.ylabel("Cumulative $NMSE_{dB}$", fontsize=15)
    plt.xlabel("Cumulative Scenes", fontsize=15)

    # Adjust legend order
    handles, labels = plt.gca().get_legend_handles_labels()
    order = np.argsort(last_row)
    order = np.flip(order)
    plt.legend([handles[i] for i in order], [labels[i] for i in order],
               loc='lower left', fontsize=10)

    # Save plot
    save_fig_path = os.path.join(file_number, "nmse_plots", "cumulative_nmse.pdf")
    os.makedirs(os.path.dirname(save_fig_path), exist_ok=True)
    plt.savefig(save_fig_path, bbox_inches='tight')
    plt.close()

def nmse_cdf_plot(data, file_number, labels, pargs):
    '''
    Cdf plot for nmses
    '''

    colors = ["#ff7f0e",
              "#2ca02c", 
              "#d62728", 
              "#9467bd", 
              "#8c564b", 
              "#e377c2"]

    ls = ["--","--","--","--","-","-"]

    if pargs.type_of_simulation == "original":
        for data, color, label, ls in zip(data, colors, labels, ls):
            x, y = np.sort(data), np.arange(1, len(data) + 1) / len(data)
            plt.plot(x, y, color=color, lw=2, ls=ls, label=label)
    else:
        for data, label in zip(data, labels):
            x, y = np.sort(data), np.arange(1, len(data) + 1) / len(data)
            plt.plot(x, y, lw=2, label=label)

    plt.ylabel("Cumulative $NMSE_{dB}$", fontsize=15)
    plt.xlabel("Cumulative Scenes", fontsize=15)
    # plt.title("Cumulative NMSE per Simplification Type", fontsize=14)
    plt.legend(loc='upper left', fontsize=11)

    # Save plot
    save_fig_path = os.path.join(file_number, "nmse_plots", "nmse_cdf.pdf")
    os.makedirs(os.path.dirname(save_fig_path), exist_ok=True)
    plt.savefig(save_fig_path, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    args = parse_args()
    FILE_NUMBER = str(args.number_of_folder)

    # Load data and calculate statistics
    if args.type_of_simulation == "normal":
        rt_duration_data = load_rt_duration_data(FILE_NUMBER)
        nmse_data = load_nmse_data(FILE_NUMBER)
        duration_labels = [
        "Original scenario", "Coverage map cut-out", "Sphere cut-out",
        "Rectangle cut-out", "Interactions cut-out", "Vertex clustering", "Quadric edge collapse"
        ]
        nmse_labels = [
        "Coverage map cut-out", "Sphere cut-out",
        "Rectangle cut-out", "Interactions cut-out", "Vertex clustering", "Quadric edge collapse"
        ]
    elif args.type_of_simulation == "mixed":
        rt_duration_data = load_rt_duration_mixed_data(FILE_NUMBER)
        nmse_data = load_nmse_mixed_data(FILE_NUMBER)
        duration_labels = [
        'CMAP + Vertex', 'Sphere + Vertex', 'Rectangle + Vertex', 'Interactions + Vertex',
        'CMAP + Edge collapse', 'Sphere + Edge collapse', 'Rectangle + Edge collapse', 'Interactions + Edge collapse'
        ]
        nmse_labels = [
        'CMAP + Vertex', 'Sphere + Vertex', 'Rectangle + Vertex', 'Interactions + Vertex',
        'CMAP + Edge collapse', 'Sphere + Edge collapse', 'Rectangle + Edge collapse', 'Interactions + Edge collapse'
        ]
    else: # Use normal as default
        rt_duration_data = load_rt_duration_data(FILE_NUMBER)
        nmse_data = load_nmse_data(FILE_NUMBER)
        duration_labels = [
        "Original scenario", "Coverage map cut-out", "Sphere cut-out",
        "Rectangle cut-out", "Interactions cut-out", "Vertex clustering", "Quadric edge collapse"
        ]
        nmse_labels = [
        "Coverage map cut-out", "Sphere cut-out",
        "Rectangle cut-out", "Interactions cut-out", "Vertex clustering", "Quadric edge collapse"
        ]

    rt_duration_stats = calculate_avg_std(rt_duration_data)
    nmse_stats = calculate_avg_std(nmse_data)

    # Debug printout
    print("Ray tracing duration:")
    for key, stat in rt_duration_stats.items():
        print(f"{key}: mean = {stat['mean']:.4f}, std = {stat['std']:.4f}")

    print("NMSE:")
    for key, stat in nmse_stats.items():
        print(f"{key}: mean = {stat['mean']:.4f}, std = {stat['std']:.4f}")

    # Plot and save
    bar_plot_duration_stats(rt_duration_stats, FILE_NUMBER, duration_labels)
    bar_plot_nmse(nmse_stats, FILE_NUMBER, nmse_labels, args)
    nmse_cumulative_sum_plot(nmse_data.values(), FILE_NUMBER, nmse_labels, args)
    nmse_cdf_plot(nmse_data.values(), FILE_NUMBER, nmse_labels, args)
    bar_plot_duration_sum(rt_duration_data, FILE_NUMBER, duration_labels)
