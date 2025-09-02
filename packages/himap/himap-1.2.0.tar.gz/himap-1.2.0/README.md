# HiMAP:  Hidden Markov models for Advanced Prognostics

HiMAP is a Python package for implementing hidden Markov Models (HMMs) and hidden semi-Markov Models (HSMMs) tailored for prognostic applications. It provides a probabilistic framework for predicting Remaining Useful Life (RUL) and modeling complex degradation processes without requiring labeled datasets.

## Table of Contents

- [Configuration and Installation](#installation)
- [Data Structure](#structure)
- [Example](#example)
- [Contributors](#contributors)

## Requirements
> [!WARNING]
> A C++ compiler is required to build the .pyx files.

### Windows users:
Microsoft Visual C/C++ (MSVC) 14.0 or higher is required to build the .pyx files.

https://visualstudio.microsoft.com/visual-cpp-build-tools/ 

(Download Build Tool - After Visual Studio Installer is ready, choose Desktop development with C++)

### Linux users:
The GNU C Compiler (gcc) is usually present. Next to a C compiler, Cython requires the Python header files. 
On Ubuntu or Debian run the following command:

```
sudo apt-get install build-essential python3-dev
```

>[!Note]
>For more information refer to the Cython package documentation:
>
>https://cython.readthedocs.io/en/latest/src/quickstart/install.html

## Installation
You can install HiMAP in two ways:

### Option 1: Install via `pip`

The easiest way to install HiMAP is through `pip`. Simply run the following command:

```bash
pip install himap
```

>[!Note]
>To install the package, you need `Python=3.9.16`


### Option 2: Install from Source Code

If you prefer to install HiMAP directly from the source, follow these steps:

1. Create an Anaconda environment and activate it.

  Step 1a

```
conda create -n himap python=3.9.16
```

  Step 1b

```
conda activate himap
```


2. This repository can be directly pulled through GitHub by the following commands:

  Step 2a
```
conda install git
```

  Step 2b
```
git clone https://github.com/GroupiSP/himap.git
```


  Step 2c
```
cd himap
```

3. The dependencies can be installed using the requirements.txt file
```
pip install -r requirements.txt
```

4. To compile the Cython code, run the following commands:
```
python setup_cython.py build_ext --inplace
```

>[!Note]
>For detailed usage instructions, guides, and API references, please visit our comprehensive documentation: [Read the docs](https://himap.readthedocs.io/en/latest/)

## Structure


```
../hsmm_dev/
      └── LICENSE
      └── README.md
      └── requirements.txt
    
      ├── hmm/                                                          -- Required
          └── ab.py                                                     -- Required
          └── base.py                                                   -- Required
          └── main.py                                                   -- Required
          └── plot.py                                                   -- Required
          └── smoothed.pyd                                              -- Required
          └── utils.py                                                  -- Required
          
          ├── cython_build/                                             -- Required      
              └── fwd_bwd.pyx                                           -- Required
              └── setup.py                                              -- Required


          ├── example_data/                                             -- Required      
              └── test_FD001_disc_20_mod.csv                            -- Required
              └── train_FD001_disc_20_mod.csv                           -- Required

          ├── results/                                                  -- Automatically generated      
              ├── dictionaries                                          -- Automatically generated
              ├── figures/                                              -- Automatically generated
              ├── models/                                               -- Automatically generated
```

## Example


To describe how to train and use the HMM and HSMM models, we show an example below. To run the code from the Anaconda terminal with default values, go to the `himap` directory and run the `main.py` file via the commands:

```
cd himap
```

```
python main.py
```

This runs the HMM model for the C-MAPSS dataset by default and fits the best model utilizing the Bayesian Information Criterion.

If you want to fit the HSMM model to the C-MAPSS data run the command:

```
python main.py --hsmm True 
```

If you want to run the example utilizing Monte Carlo Sampling generated data run the command:

```
python main.py --mc_sampling True
```

See the `main.py` file for different existing variables and options.

### Results

The results are saved inside the directory `../himap/results/`

## Contributors

- [Thanos Kontogiannis](https://github.com/thanoskont)
- [Mariana Salinas-Camus](https://github.com/mariana-sc)
- [Nick Eleftheroglou](https://www.tudelft.nl/staff/n.eleftheroglou/)

## License
As of v1.1.0 (2025-08-25), **HiMAP** is licensed under the **Apache License 2.0**.
Prior releases remain under their original licenses.

See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).
