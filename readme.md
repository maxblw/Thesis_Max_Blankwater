``` text
project/
├── README.md
├── Data/
| └── FEM_Samples/
|   ├── Calibration/
|   | └──calibration_FEM_main.ipynb
|   └── Parametric_Study/
├── PLAXIS_Scripts/
| ├── Calibration/
| └── Parametric_Study/
├── Surrogates/
│ ├── Logs/
│ | ├── Calibration_Surrogate/
| | └── Parametric_study_Surrogate/
│ ├── calibration_surrogate_main.ipynb
│ └── ps_surrogate_main.py

```
# FEM Modelling (`\PLAXIS_Scripts`)
The scripts used to run calibrattion and parametric studies and subsequent analyses are contained in `\PLAXIS_Scripts`, whith the subdivisions `\Calibration` and `\Parametric_Study`. These folders contain a main notebook from which the functions are run and supporting functions files.

## Calibration (`\PLAXIS_Scripts\Calibration`)
This file contains the scripts required for parameter definition and running the calibration runs in PLAXIS, these are contained within the notebook `calibration_FEM_main.ipynb`. The function that are called for calibration are defined in `calibration_func.py` and helper function to define the plots in `helper_func.py`. Aditionally, defined parameter sets in .csv format are stored in `\Parameter_Sets`. The extracted values from PLAXIS are stored in `\Logs`. The important logs are exported to `\Data\FEM_Samples\Calibration`.

The logs are structures using the `run_name` which is either "calibration" or "ps", for the calibration and parametric study. `sampletype`, is represented by M, N or U, describing Moment, Axial force and Displacement respectively.

| Element | Filename | Description | 
|---------|----------|-------------| 
| Tubular piles | `{run_name}_BP_{sampletype}.csv` | Forces and displacements for the tubular piles in the combiwalls | 
| Vibropiles (landside) | `{run_name}_VPL_{sampletype}.csv` | Forces and displacements for the vibropiles at the landside | 
| Vibropiles (waterside) | `{run_name}_VPW_{sampletype}.csv` | Forces and displacements for the vibropiles at the waterside | 
| Anchors (top row) | `{run_name}_GAT_{sampletype}.csv` | Forces and displacements for the top row of anchors | 
| Anchors (bottom row) | `{run_name}_GAB_{sampletype}.csv` | Forces and displacements for the top row of anchors |

# Surrogate Modelling (`\Surrogates`)
The code used to train PCE models on FEM samples is shown in the folder `\Surrogates`. The main functions are run from a `\main` notebook with the suffix `.._surrogate_main.ipynb`. the two defined surrogate models are the parametric study (ps) model and the calibration model. the function to train and test the models are contained withing the file `surrogate_func.py` and functions to plot the results are contained in `helper_func.py`. The `\Logs` folder contains error metric logs and sobol indices used for hyperparameter tuning. 

# Data (`\Data`)
The data used in this project is stored in the data folder, as well as the outputs from models that are used in subsequent models.
## FEM Samples (`\FEM_Samples`)
The PLAXIS-generated FEM samples are contained within the folder FEM_Samples. The sample folder contains PLAXIS imports for the elements as described in the table below. 
