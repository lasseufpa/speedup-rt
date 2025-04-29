# Accelerating Ray Tracing-Based Wireless Channels Generation for Real-Time Network Digital Twins

ArXiv link: https://arxiv.org/abs/2504.09751

This repository contains the ARTS and the baseline related source code of the above mentioned paper.

## Getting started
The first step is to create the python environment with Conda, using the following command:

### Installing Conda Environment
```bash
conda env create -f environment.yml
```

### Installing Modified Sionna 0.19
The current Sionna version does not return the ray phase, so this modification allow us to retrieve this information.
```bash
pip install rtr/.

```

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
- `--channel`: Type of channel to be used (`geometric`, `ofdm`).
- `--n-terms`: Number of terms to be generated between two scenes.

### Multiple RT Scenes Augmentation (multiple scenarios)
The following commands will generate the paper results (in format of CDF) considering three scenarios: Etoile, St. Canyon and Munich. In this case, we considered an RT augmentation with ARTS method and its baseline (matrix interpolation).

Obs: The following command will replicate the experiment 1 from the paper. To replicate the experiment you need to change the number of terms to be generated.
#### ARTS Method
```bash
python3 multiple_augmentation.py --dir ../data_generator/datasets/ --interp-type linear_2 --plot cdf --baseline
```
Where:

- `--dir`: Directory to multiple datasets.
- `--interp-type`: Interpolation approach that should be used (`linear_2` | `linear_n` | `poly`).
- `--plot-type`: Type of result plot to be generated, which can be cumulative distributed function or a histogram (`cdf` | `hist`).
- `--baseline`: Show baseline plot curves.

## Dataset Generator with Sionna RT
To generate different datasets, from the available in this repository, execute one of the following commands. This command will create a dataset considering the St. Canyon scenario with 1000 scenes, with the following characteristics:

| Parameters          | Value |
|-----------------------|------|
| Number of Tx          | 1 |
| Number of Rx          | 1 |
| Carrier Frequency     | 2.14 GHz |
| Number of Tx antennas | 8 |
| Number of Rx antennas | 4 |


### Generating RT dataset

```bash
python3 mpc_generator.py --scenario canyon --delta 0.2 --scenes 1000
```

Where:

- `--scenario`: It is the scenario that should be used to generate the dataset (canyon | munich | etoile).
- `--delta`: The space, in meters, between each scene. 
- `--scenes`: Number of scenes (snapshots).

## Troubleshootings
A common initial problem is missing packages related to LLVM. So, if a problem like this occur:
```
the LLVM backend is inactive because the LLVM shared library ("libLLVM.so") could not be found!
```

Try to install LLVM system packages, such as:
```
sudo apt install llvm libllvm-dev
```

After that, configure the required environment variable `DRJIT_LIBLLVM_PATH` with the correct version of LLVM package:
```
export DRJIT_LIBLLVM_PATH=/usr/lib/llvm-18/lib/libLLVM.so
```

## Credits
If you benefit from this work, please cite on your publications using:
```
@misc{modesto2025acceleratingraytracingbasedwireless,
      title={Accelerating Ray Tracing-Based Wireless Channels Generation for Real-Time Network Digital Twins}, 
      author={Cláudio Modesto and Lucas Mozart and Pedro Batista and André Cavalcante and Aldebaro Klautau},
      year={2025},
      eprint={2504.09751},
      archivePrefix={arXiv},
      primaryClass={cs.NI},
      url={https://arxiv.org/abs/2504.09751}, 
}
```
