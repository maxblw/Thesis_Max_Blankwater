# Thesis: Combiwall Modelling and Analysis

This repository contains the notebooks, scripts, and data for thesis work on modelling and analysing a combiwall system. It brings together measurement interpretation, PLAXIS finite-element modelling, surrogate modelling, and comparisons between model behaviour and observations.

## Project areas

| Directory | Contents |
| --- | --- |
| `Measurement_interpretation/` | Notebooks and Python functions for interpreting inclinometer and strain measurements. |
| `PLAXIS_Scripts/Calibration/` | Calibration model notebook, helper modules, parameter sets, and logs. |
| `PLAXIS_Scripts/Parametric_Study/` | Parametric-study model notebook, helper modules, and logs. |
| `Surrogates/` | Calibration and parametric-study surrogate notebooks, shared functions, and logs. |
| `Behaviour_comparison/` | Notebooks and scripts for comparing and validating model behaviour. |
| `Data/` | FEM samples, initial model predictions, input coordinates, and measurement data. |

## Notebooks to get started

- **Measurement interpretation:** `Measurement_interpretation/inclino/inclino_measurements_main.ipynb` and `Measurement_interpretation/strain/strain_interpretation_main.ipynb`
- **PLAXIS calibration:** `PLAXIS_Scripts/Calibration/calibration_FEM_main.ipynb`
- **PLAXIS parametric study:** `PLAXIS_Scripts/Parametric_Study/parametric_study_FEM_main.ipynb`
- **Surrogate models:** `Surrogates/calibration_surrogate_main.ipynb` and `Surrogates/ps_surrogate_main.ipynb`
- **Behaviour comparison and validation:** `Behaviour_comparison/comparison_main.ipynb` and `Behaviour_comparison/validation.ipynb`

Python helper modules are kept alongside the notebooks that use them. Check each notebook's imports and input paths before running it; run cells in order and adjust machine-specific paths as needed.

## Environments

The repository provides separate Conda environment files for the PLAXIS scripts and the openTURNS surrogate workflow:

```bash
conda env create -f PLAXIS_environment.yml
conda activate PLAXIS
```

```bash
conda env create -f openTURNS_environment.yml
conda activate openTURNS
```

These environments support different parts of the project. Running the FEM notebooks also requires a compatible PLAXIS installation and scripting access; installing the Conda environment does not install PLAXIS. The environment files include Windows-specific configuration, so review their `prefix` entries when creating environments on another machine.

## Data and generated results

Data is grouped under `Data/` by purpose, with FEM samples further separated into calibration and parametric-study sets. Supporting logs and outputs are also kept in their respective workflow directories. Preserve original measurement and input files when generating or updating results.
