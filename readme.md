This repository contains the code and samples for surrogate models 

``` text
project/
├── README.md
├── Surrogates/
│ ├── Logs
│ | └── Calibration_Surrogate/
│ ├── calibration_surrogate_main.ipynb
│ ├── surrogate_func.py
│ └── helper_func.py
└── FEM_Samples/
  ├── Calibration/
  └── Parametric_Study/
```

# Surrogate Modelling (`\Surrogates`)
The code used to train PCE models on FEM samples is shown in the folder `\Surrogates`. The main functions are run from a `\main` notebook with the suffix `.._surrogate_main.ipynb`. the function to train and test the models are contained withing the file `surrogate_func.py` and functions to plot the results are contained in `helper_func`. The `\Logs` folder contains error metric logs and sobol indices used for hyperparameter tuning. 

# FEM Samples (`\FEM_Samples`)
The PLAXIS-generated FEM samples are contained within the folder FEM_Samples. The sample folder contains PLAXIS imports for the elements as described in the table below. The files are structures using the `run_name` which is either "calibration" or "ps", for the calibration and parametric study. `sampletype`, is represented by M, N or U, describing Moment, Axial force and Displacement respectively.

| Element | Filename | Description | 
|---------|----------|-------------| 
| Tubular piles | `{run_name}_BP_{sampletype}.csv` | Forces and displacements for the tubular piles in the combiwalls | 
| Vibropiles (landside) | `{run_name}_VPL_{sampletype}.csv` | Forces and displacements for the vibropiles at the landside | 
| Vibropiles (waterside) | `{run_name}_VPW_{sampletype}.csv` | Forces and displacements for the vibropiles at the waterside | 
| Anchors (top row) | `{run_name}_GAT_{sampletype}.csv` | Forces and displacements for the top row of anchors | 
| Anchors (bottom row) | `{run_name}_GAB_{sampletype}.csv` | Forces and displacements for the top row of anchors |
