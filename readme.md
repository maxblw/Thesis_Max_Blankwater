# Thesis: Combiwall Modelling and Surrogate Analysis

This repository contains the code and data supporting thesis work on the numerical modelling, calibration, and parametric analysis of a combiwall system. The workflow uses PLAXIS finite-element simulations and Polynomial Chaos Expansion (PCE) surrogate models, alongside interpretation of inclinometer and strain measurements.

## Repository contents

- `Measurement_interpretation/` — notebooks and Python helpers for processing inclinometer and strain measurements.
- `PLAXIS_Scripts/Calibration/` — calibration notebook, model and result helpers, and calibration parameter sets.
- `PLAXIS_Scripts/Parametric_Study/` — parametric-study notebook and supporting functions.
- `Data/FEM_Samples/` — FEM sample data organized by calibration and parametric study.
- `Data/Measurements/` and `Data/Input_coords/` — measurement and coordinate inputs.
- `Surrogates/` — calibration and parametric-study surrogate notebooks, shared functions, and logs.
- `PLAXIS_environment.yml` and `openTURNS_environment.yml` — Conda environment specifications for the PLAXIS scripting and surrogate workflows, respectively.

## Workflows

### Measurement interpretation

Start with the notebooks in `Measurement_interpretation/inclino/` or `Measurement_interpretation/strain/`. Their companion Python modules contain the associated processing functions. The source measurement files are organized under `Data/Measurements/` and the interpretation folders.

### FEM calibration and parametric study

The main PLAXIS notebooks are:

- `PLAXIS_Scripts/Calibration/calibration_FEM_main.ipynb`
- `PLAXIS_Scripts/Parametric_Study/parametric_study_FEM_main.ipynb`

Supporting calculations and result extraction are implemented in the Python modules alongside each notebook. Calibration parameter sets are stored under `PLAXIS_Scripts/Calibration/Parameter_Sets/`; FEM sample data is organized in `Data/FEM_Samples/`.

### Surrogate modelling

The surrogate notebooks are `Surrogates/calibration_surrogate_main.ipynb` and `Surrogates/ps_surrogate_main.ipynb`. Shared model and plotting helpers are in `Surrogates/surrogate_func.py` and `Surrogates/helper_func.py`; generated logs are under `Surrogates/Logs/`.

## Environment and execution

Create the Conda environment for the workflow you intend to run:

```bash
conda env create -f openTURNS_environment.yml
conda activate openTURNS
```

For PLAXIS scripting, use the separate environment specification:

```bash
conda env create -f PLAXIS_environment.yml
conda activate PLAXIS
```

The environment files were exported on Windows and contain an author-specific absolute `prefix`. When setting them up on another machine, remove or update that `prefix` entry as appropriate. PLAXIS scripts also require a compatible PLAXIS installation and scripting access; the environment file alone does not provide the software. Review notebook configuration and input paths for your local setup, then run notebook cells in order.

## Data and outputs

The repository separates source measurements, model inputs, FEM samples, and surrogate logs by workflow. Some outputs are produced by running the notebooks; availability depends on the checked-in data and the local PLAXIS setup. Keep generated files in the corresponding workflow folders and avoid overwriting source inputs.
