# 3D Objects Manipulator
This repository contains the codes related to the 3D simplification module of the paper [LINK_PLACEHOLDER](), which are the cut-out and mesh simplification methods.


## Installation

To install it, first clone it with `git clone`. Then, you need to install the conda enviroment of the project using the command in the repository folder: ``conda env create -f environment.yml``, which will create the environment named **simplification**. At least, you will need to manually install the sionna package because we are using a modified version. To install it, go to the sionna folder in the interpolation repository and run the command ``pip install .`` inside it.

The main module is the python script `mesh_cut_out_simplification.py`, which will actually perform simplification, whether mesh- or cut-out based simplification in any given scenario. 

If you want to reproduce the simulation from the paper involving the simplifications, you must simply run one of the python scripts ``compute_ray_tracing_duration_*.py`` and ``nmse_simulations_*.py``. These scripts will download from the LASSE's Nextcloud the necessary files to achieve the results of the paper.

## Usage

### Scene Simplification
In order to run the main code, i.e., the script that implements the simplification methods (mesh and cut-out) a 3D scenario in the Mitsuba format will be necessary as our input. 
First, you need to place your Mitsuba file in the folder `mitsubas/` with the following configuration (if necessary rename the files and folders):

```
original_mitsuba
  ├── export.xml
  └── meshes
        └── ... .ply
        └── ... .ply
        └── ... .ply
```

After that, you can run the `mesh_cut_out_simplification.py` to simplify your scene. For example:

```
python mesh_cut_out_simplification -ms vertex -p 0.3 -ct sphere
```

which will use the vertex clustering mesh-simplification with the sphere cut-out simplification at same time in the scene. The output scenario will be placed in ``mitsubas/simplifications/simplified_scenario``. To define the configs parameters of the simulation, for example the RX and TX position, you need to change the ``tx_position`` and ``rx_position`` in the ``config.json``. Furthermore, to see the others methods you can use:
```
python mesh_cut_out_simplification --help
```

### Reproducing the Results from the Paper

As the names suggest, the scripts that will generate the ray tracing durations and NMSE values for both the mixed and solo versions are ``compute_ray_tracing_duration_*.py`` and ``nmse_simulations_*.py``. You just need to run either one, and it will download the Mitsubas files used in the paper and generate the respective results. For example (using the mixed cases):

```
python compute_ray_tracing_duration_mixed
```

This will generate ray tracing durations along a pre-defined track, which is created using two points in the scene and interpolating between them with a step of ``0.5`` (defined in configs.json). For the mixed cases, this track will always be the linear. Finally, these values are stored in the ``npzs/duration`` folder.

For the NMSE, It is quite similar, like:

```
python nmse_simulations_mixed
```
Here, we will also use the same pre-defined path. The results are stored in the folder ``npzs/nmse``.

For the original cases, i.e., without mixing, you need to run, for example:

```
python nmse_simulations_original -pt 0
```

or

```
python compute_ray_tracing_duration_original -pt 1
```

The ``-pt`` argument specifies the track used in the simulations: ``0`` corresponds to the linear track, and ``1`` to the square track.

#### Note
These last four scripts and mitsubas that they downloaded already have the logic for the tests embedded within them, e.g., the mitsubas are cut-out based on a certain TX and RX position, and the script will also perform actions at these position. Therefore, these scripts will not work for other personal 3D scenarios.  

### Plots

There is a script for plotting located in the ``simulations_results/``. After running the NMSE and ray tracing duration simulations, you will have two ``.npz`` files, one in each folder inside the ``npzs/`` **(you NEED to have both)**. Then, you can run the plot.py script as shown below:

```
python plot.py -n 1 -t normal
```

This will use the first npzs files in each folder, i.e., ``rt_duration1.npz`` and ``nmses1.npz``, to generate the following plots:

- **NMSE**
  - Cumulative sum: ``cumulative_nmse.pdf``
  - Cumulative distribution function: ``nmse_cdf.pdf``
  - Mean with STD: ``nmse_mean_std_plot.pdf``

- **Ray tracing duration**
  - Bar plot (mean and std): ``ray_tracing_duration.pdf``
  - Bar plot (sum): ``ray_tracing_duration_sum.pdf``

It is also important to use the ``-t`` option to specify the type of simulation performed, which must be the same for NMSE, and the duration, i.e., `rt_duration1.npz` and `nmses1.npz` must have the same simulation type, which can be `normal` or `mixed`.

Regarding the trade-off plot, you need to run, for example:

```
python tradeoff_plot.py -s 2 -m 3
```

This command will create a trade-off plot comparing the solo durations and nmses (indice 2) with the mixed durations and nmses (indice 3), and save it in the same folder as ``23tradeoff_plot.pdf``.

### Roadmap

- [ ] Create a function to define custom materials.
- [ ] Integrate this module with the interpolation and remove unnecessary python path modification.
- [ ] Better organize the scripts within the repository, especially the ones in the ``utils/`` folder.
- [ ] Better organize the ``plot.py`` regarding defs, classes, etc.
- [ ] Define whether there will be parsers or not (parsers.py).



