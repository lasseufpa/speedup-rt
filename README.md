# Accelerating Ray Tracing-Based Wireless Channels Generation for Real-Time Network Digital Twins

This repository contains the ARTS, the baseline related source code for post-processing ray tracing outputs, and the post-processing techiniques to simplify 3D scenarios.

## :bulb: Introduction
Ray tracing (RT) simulation is a widely used approach to enable modeling wireless channels in applications such as network digital twins. However, the computational cost to execute ray tracing (RT) is proportional to factors such as the level of detail used in the adopted 3D scenario. This work proposes RT pre-processing algorithms that aim at simplifying the 3D scene without distorting the channel, by reducing the scenario area and/or simplifying object shapes in the scenario. It also proposes a post-processing method that augments a set of RT results to achieve an improved time resolution. These methods enable using RT in applications that use a detailed and photorealistic 3D scenario while generating consistent wireless channels over time. Our simulation results with different urban scenarios scales, in terms of area and object details, demonstrate that it is possible to reduce the simulation time by more than 50% without compromising the accuracy of the multipath RT parameters, such as angles of arrival and departure, delay, phase, and path gain. 

## :gear: Installing Conda environment
```bash
conda env create -f environment.yml
```

### Installing modified Sionna 0.19.2
The current Sionna version does not return the ray phase, so this modification allow us to retrieve this information.
```bash
pip install ray_tracer/.

```

## Wireless channel generator
The first step is to create the python environment with Conda, using the following command:


## Single RT Scenes Augmentation (only one scenario) 
### Matrix Interpolation
Considering that your current directory is `channel_augmentation`, execute one of the following commands. These examples consider the St. Canyon scenario, a geometric 2D channel model and the final result if CDF plot format.

```bash
python3 single_augmentation.py --file ../data_generator/datasets/canyon_based_sionna_dataset_1001_test_0.2.mb --interp-type matrix --channel geometric --plot-type cdf
```

#### ARTS Method
```bash
python3 single_augmentation.py --file ../data_generator/datasets/canyon_based_sionna_dataset_1001_test_0.2.mb --interp-type linear_2 --chanel geometric --plot-type cdf --n-terms 2
```

Where:

- `--file`: Directory to multiple datasets.
- `--interp-type`: Interpolation approach that should be used (`linear_2` | `linear_n` | `poly`).
- `--plot-type`: Type of result plot to be generated, which can be cumulative distributed function or a histogram (`cdf` | `hist`).
- `--n-terms`: Number of terms to be generated between two scenes.
- `--ant-pattern`: Type of antenna array (`ula` | `upa`)
- `--channel-type`: Type of channel, which can be wideband or narrowband (`wb` | `nb`)

### Multiple RT Scenes Augmentation (multiple scenarios)
The following commands will generate the paper results (in format of CDF) considering three scenarios: Etoile, St. Canyon and Munich. In this case, we considered an RT augmentation with ARTS method and its baseline (matrix interpolation).

Obs: The following command will replicate the experiment 1 from the paper. To replicate the experiment you need to change the number of terms to be generated.
#### ARTS Method
```bash
python3 multiple_augmentation.py --dir ../data_generator/datasets/ --interp-type linear_2 --plot cdf --baseline --ant-pattern ula --channel-type nb
```
Where:

- `--dir`: Directory to multiple datasets.
- `--interp-type`: Interpolation approach that should be used (`linear_2` | `linear_n` | `poly`).
- `--plot-type`: Type of result plot to be generated, which can be cumulative distributed function or a histogram (`cdf` | `hist`).
- `--baseline`: Show baseline plot curves.
- `--ant-pattern`: Type of antenna array (`ula` | `upa`)
- `--channel-type`: Type of channel, which can be wideband or narrowband (`wb` | `nb`)

## Dataset Generator with Sionna RT
To generate different datasets, from the available in this repository, execute one of the following commands. This command will create a dataset considering the St. Canyon scenario with 1000 scenes, with the following characteristics:

## :test_tube: Dataset generator with Sionna RT
To generate different datasets, from the available in this repository, execute one of the following commands. This command will create a dataset considering the St. Canyon scenario with 1000 scenes, with the following characteristics:

| Parameters          | Value |
|-----------------------|------|
| Number of Tx          | 1 |
| Number of Rx          | 1 |
| Carrier Frequency     | 2.14 GHz |
| Number of Tx antennas | 1 |
| Number of Rx antennas | 1 |


### Generating RT dataset

```bash
python3 mpc_generator.py --scenario canyon --delta 0.2 --scenes 1000
```

Where:

- `--scenario`: It is the scenario that should be used to generate the dataset (canyon | munich | etoile).
- `--delta`: The space, in meters, between each scene. 
- `--scenes`: Number of scenes (snapshots).

## :jigsaw: 3D Objects Manipulator

The main module is the python script `mesh_cut_out_simplification.py`, which will actually perform simplification, whether mesh- or cut-out based simplification in any given scenario. 

If you want to reproduce the simulation from the paper involving the simplifications, you must simply run one of the python scripts ``compute_ray_tracing_duration_*.py`` and ``nmse_simulations_*.py``. These scripts will download from the LASSE's Nextcloud the necessary files to achieve the results of the paper.

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
python compute_ray_tracing_duration_original.py -pt 1
```

The ``-pt`` argument specifies the track used in the simulations: ``0`` corresponds to the linear track, and ``1`` to the square track.


:information_source: These last four scripts and mitsubas that they downloaded already have the logic for the tests embedded within them, e.g., the mitsubas are cut-out based on a certain TX and RX position, and the script will also perform actions at these position. Therefore, these scripts will not work for other personal 3D scenarios.  

### :bar_chart: Plots

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

### Scene simplification
In order to run your own simplification scenario, the main code, i.e., the script that implements the simplification methods (mesh and cut-out) a 3D scenario should be executed. In this sense, you need to place your Mitsuba file in the folder `mitsubas/` with the following configuration (if necessary rename the files and folders):

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
python mesh_cut_out_simplification.py --mesh vertex --parameter 0.3 -cut_type sphere
```

which will use the vertex clustering mesh-simplification with the sphere cut-out simplification at same time in the scene. The output scenario will be placed in ``mitsubas/simplifications/simplified_scenario``. To define the configs parameters of the simulation, for example the RX and TX position, you need to change the ``tx_position`` and ``rx_position`` in the ``config.json``. Furthermore, to see the others methods you can use:

```
python mesh_cut_out_simplification.py --help
```

This help command will show the following flags:

`--mesh`: Enables mesh simplification, which can be `vertex` or `quadric`

`--parameter`: Parameter to define the level of simplification. Varies between 0 to 1. 1 is the highest level.

`--cut_type`: Define the type of cut-out simplification. Can be `no_cut`, `rectangle`, `sphere`, `cmap`, `interactions`.


### Roadmap to run your own simplification

- [ ] Create a function to define custom materials.
- [ ] Integrate this module with the interpolation and remove unnecessary python path modification.
- [ ] Better organize the scripts within the repository, especially the ones in the ``utils/`` folder.
- [ ] Better organize the ``plot.py`` regarding defs, classes, etc.
- [ ] Define whether there will be parsers or not (parsers.py).

## Troubleshootings
A common initial problem is missing packages related to LLVM. So, if a problem like this occur:
```
the LLVM backend is inactive because the LLVM shared library ("libLLVM.so") could not be found!
```

Try to install LLVM system packages, such as:
```
sudo apt install llvm libllvm-dev
```

And the `llvmlite` python package in your environment, using `pip`:

```
pip install llvmlite
```


After that, configure the required environment variable `DRJIT_LIBLLVM_PATH` with the correct version of LLVM package. In this case the correct version was 18:
```
export DRJIT_LIBLLVM_PATH=/usr/lib/llvm-18/lib/libLLVM.so
```

## Credits
If you benefit from this work, please cite on your publications using:
```
@ARTICLE{modesto2025,
  author={Modesto, Cláudio and Mozart, Lucas and Batista, Pedro and Cavalcante, André and Klautau, Aldebaro},
  journal={IEEE Open Journal of the Communications Society}, 
  title={Accelerating Ray Tracing-Based Wireless Channels Generation for Real-Time Network Digital Twins}, 
  year={2025},
  volume={6},
  number={},
  pages={5464-5478},
  doi={10.1109/OJCOMS.2025.3583202}}

```
