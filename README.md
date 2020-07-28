# Synchronous transmissions on Bluetooth 5 and IEEE 802.15.4 - A replication study

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3964355.svg)](https://doi.org/10.5281/zenodo.3964355)


This repository contains the raw data and analysis scripts of a replication study of synchronous transmissions using the [nRF52840 Dongle](https://www.nordicsemi.com/en/Software%20and%20tools/Development%20Kits/nRF52840%20Dongle) where we compare the success rate of synchronous transmission attempts using two transmitters while varying a number of parameters. The repository also contains the source code of a data visualization application, which you can either
- [run locally](#Run-locally) or
- [online in your web browser](URL) at http://explore-st-data.ethz.ch/

The study is described in more details in the following publication.
> **Synchronous transmissions on Bluetooth 5 and IEEE 802.15.4 - A replication study**  
Romain Jacob, Anna-Brit Schaper, Andreas Biri, Reto da Forno, Lothar Thiele   
[CPS-IoTBench'20](https://cpsbench20.ethz.ch/)  
[ [Direct link](https://openreview.net/forum?id=BSZPNEUHiS2) ]

The dataset has been collected during the [Master thesis of Anna-Brit Schaper.](https://doi.org/10.3929/ethz-b-000375332)

## Repository structure
- `app.py`, `index.py` and `/tabs` contain the source files of the application
- `/src/plots.py` contains the plotting functions used by the application
- the other files in `/src` contain various functions and metadata used in the processing pipeline
- `/data_raw` contains the raw data (see format therein)
- `/data_preprocessed` contains the preprocessed data, used by the application (see format therein)
- `process_and_plots.ipynb` is a Jupyter notebook showcasing the used of the plotting functions and generating the plots shown in the publication referenced above.


## Run locally
The data visualization application is written in Python using [Dash](https://plotly.com/dash/), an open source framework building on the plotting library [Plotly](https://plotly.com/python/) and the web framework [Flask](https://flask.palletsprojects.com/en/1.1.x/).

To run the application locally, create a Python environment with all required dependencies using either PIP and venv or Conda.

> If you simply want to see the application, you can access it online at http://explore-st-data.ethz.ch/

**Using Conda**
```bash
conda env create -f environment.yml
conda activate SyncTransVisualization
```
**Using PIP**
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Once the dependancies are installed, run the app with
```bash
python3 index.py
```
and open in your browser the local IP where your application runs (default is `http://127.0.0.1:8050/`).
