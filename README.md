This repository contains a new data analysis for the data collected during Anna Brit-Schaper Master Thesis.

(to be extended)

## How to run the data visualization app locally
Create a Python environment with the required dependencies using either PIP and venv or Conda:

- Using Conda:
```bash
conda env create -f environment.yml
conda activate SyncTransVisualization
```
- Using PIP
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Once the dependancies are installed, run the app with
```bash
python3 app.py
```
and open in your browser the local IP where you app runs (default is `http://127.0.0.1:8050/`).

## Notes
- Only minor modifications to the data collected by Anna (in `data_raw`):
  - Fixed a typo in the time delta values (stored as `100` instead of `-100`)
  - CSV headers renamed for better cross-compatibility
