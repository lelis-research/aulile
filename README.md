# Synthesizing Libraries of Programs with Auxiliary Functions
A common approach to program synthesis is to use a learned function to guide the search for a program that satisfies the user's intent. In this paper, we propose a method that offers search guidance, through a domain-dependent auxiliary function, that can be orthogonal to the guidance previous functions provide. Our method, which we call Auxiliary-Based Library Learning (Aulile), searches for a solution in the program space using a base algorithm. If this search does not produce a solution, Aulile enhances the language with a library of programs discovered in the search that optimizes for the auxiliary function. Then, it repeats the search with this library-augmented language. This process is repeated until a solution is found or the system reaches a timeout. We evaluate Aulile in string manipulation tasks. Aulile improved, in some cases by a large margin, the performance of several base algorithms that use different search and learning strategies: Bus, Bustle, Crossbeam, and Bee Search. Our results suggest that Aulile offers an effective method of injecting domain knowledge into existing systems through a library learning scheme that optimizes for an auxiliary function.

## Table of Contents
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Citation](#citation)

## Directory Structure

```
.
├── README.md
├── batcher-a-bee-bee.sh # Batch submission script for A-Bee and Bee
├── batcher-a-bus-bus.sh # Batch submission script for A-Bus and Bus
├── batcher-a-bustle-bustle.sh # Batch submission script for A-Bustle and Bustle
├── config
│   ├── bustle_38.txt
│   ├── bustle_benchmarks.txt
│   └── sygus_string_benchmarks.txt
├── data
│   └── random_bustle_encoded_training_data.csv
├── logs
├── models
│   ├── bustle_model_01.hdf5
│   ├── bustle_model_02.hdf5
│   ├── bustle_model_03.hdf5
│   ├── bustle_model_04.hdf5
│   ├── bustle_model_05.hdf5
│   └── sygus_models
│       ├── EncodedBustleModelForPS_1.hdf5
│       ├── EncodedBustleModelForPS_1234.hdf5
│       ├── EncodedBustleModelForPS_2.hdf5
│       ├── EncodedBustleModelForPS_3.hdf5
│       ├── EncodedBustleModelForPS_4.hdf5
│       └── EncodedBustleModelForPS_5.hdf5
├── requirements.txt
├── src
│   ├── bee.py
│   ├── bus.py
...
├── src_a_bustle_a_bus
│   ├── a-bus.py
│   ├── a-bustle.py
│   ├── bus.py
│   ├── bustle.py
...
├── src_a_crossbeam # This is the directory for the A-crossbeam
...
├── submitter-a-bee-bee.sh
├── submitter-a-bus-bus.sh
└── submitter-a-bustle-bustle.sh
```

## Installation

### Create a virtual environment
`python3 -m venv tensorflow`

###  Activate the virtual environment
`source tensorflow/bin/activate`

### Install the required packages
`pip install -r requirements.txt`

## Usage

To run **A-Bee** and **Bee**, go to the `src` directory and run the following command:
`python bee.py`

To run **A-Bus**, **Bus**, **A-Bustle** or **Bustle**, go to the `src_a_bustle_a_bus` directory and run the following command:
`python bus.py` or `python a-bus.py`

To run the **A-Crossbeam**, follow the instructions in the `src_a_crossbeam` directory.

## Citation

If you use this code in your research, please cite the following paper:

```
@article{
    aulile2024,
    title={Synthesizing Libraries of Programs with Auxiliary Functions},
    author={Anonymous},
    journal={Submitted to Transactions on Machine Learning Research},
    year={2023},
    url={https://openreview.net/forum?id=tP1PBrMUlX},
    note={Under review}
}
```# aulile
