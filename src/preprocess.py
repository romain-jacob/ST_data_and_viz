from pathlib import Path
import pandas as pd
import numpy as np

from src.helpers import Modes, Parameters
from src.stats import ThompsonCI_twosided

prr_file = 'prr.csv'
rssi_file = 'rssi.csv'

def parse_run_rssi(pair,data,datetime,force_computation=''):

    data_path = Path('data_raw_cleaned')
    output_path = Path('data_preprocessed')
    data_path = data_path / pair / data / datetime
    output_path = output_path / pair / data / datetime

    if (force_computation == 'rssi'):
        print('Recomputing RSSI data...')
    else:
        try:
            df = pd.read_csv(output_path / 'medianRSSI.csv')
            print('RSSI data retrieved.')
            return df
        except FileNotFoundError:
            print('No existing file found. Computing RSSI...')

    # Create output directory if it does not exist yet
    if not output_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        print('Created path: %s' % str(output_path))

    # Load RSSI data
    # -> skip leading and trailing space in column names
    rssi_df = pd.read_csv(str(data_path / rssi_file))

    # Create a filter for missing RSSI measurements
    filter = rssi_df["RSSI"]!="NONE"

    # Filter out the missing measurements and convert as numeric
    rssi_df = rssi_df.where(filter).dropna().astype('int32')

    # Rename columns
    rssi_df = rssi_df.rename(columns={
        "RSSI": "medianRSSI",
    })

    # Aggregate and compute the median
    rssi_medians = rssi_df.groupby(["Mode","Transmitter","TxPower"]).medianRSSI.agg('median')

    # Save as csv
    rssi_medians.to_csv(output_path / 'medianRSSI.csv')

    return rssi_medians

def parse_run_prr(pair,data,datetime,force_computation=''):

    data_path = Path('data_raw_cleaned')
    output_path = Path('data_preprocessed')
    data_path = data_path / pair / data / datetime
    output_path = output_path / pair / data / datetime

    if ((force_computation == 'prr') or (force_computation == 'rssi')):
        print('Recomputing PRR data...')
    else:
        try:
            df = pd.read_csv(output_path / 'prr.csv')
            print('PRR data retrieved.')
            return df
        except FileNotFoundError:
            print('No existing file found. Computing PRR...')

    # Load PRR data
    # -> skip leading and trailing space in column names
    df = pd.read_csv(str(data_path / prr_file))

    # Load RSSI data
    rssi_df = pd.read_csv(output_path / 'medianRSSI.csv')

    # Fill-in the values based on the RSSI DataFrame
    TxPowerA = df.TxPowerA.unique()
    TxPowerB = df.TxPowerB.unique()
    Mode = df.Mode.unique()

    for M in Mode:

        # Transmitter A
        for Tx in TxPowerA:
            # Get the RSSI measurement
            RssiA = rssi_df.loc[
                (rssi_df['Mode'] == M) &
                (rssi_df['TxPower'] == Tx) &
                (rssi_df['Transmitter'] == 0)
            ]
            # If no value, set as NaN
            if len(RssiA) == 0:
                RssiA_value = np.nan
            else:
                RssiA_value = RssiA.medianRSSI.values[0]
            # Place the value in the global DataFrame
            df.loc[
                (df['Mode'] == M) &
                (df['TxPowerA'] == Tx), ("RssiA")
            ] = RssiA_value


        # Get RSSI measurement for Transmitter B
        for Tx in TxPowerB:
            # Get the RSSI measurement
            RssiB = rssi_df.loc[
                (rssi_df['Mode'] == M) &
                (rssi_df['TxPower'] == Tx) &
                (rssi_df['Transmitter'] == 1)
            ]
            # If no value, set as NaN
            if len(RssiB) == 0:
                RssiB_value = np.nan
            else:
                RssiB_value = RssiB.medianRSSI.values[0]
            # Place the value in the global DataFrame
            df.loc[
                (df['Mode'] == M) &
                (df['TxPowerB'] == Tx), ("RssiB")
            ] = RssiB_value

    # Add to the DataFrame
    # + PowerDelta
    df["PRR"] = (100*df['RxCount']/df['TxCount'])
    # + PRR (in %)
    # /!\ Do not change! Has to be B-A to properly cover the
    # parameter space (due to the experiment settings)
    df["PowerDelta"] = df['RssiB'] - df['RssiA']
    # Round values to get only integers
    df = df.round({'PowerDelta': 0})

    # Save metadata info in the DataFrame
    if data == 'same_data':
        data_label = 1
    elif data == 'different_data':
        data_label = 0
    if pair == 'transmitter_pair_a':
        pair_label = 'A'
    elif pair == 'transmitter_pair_b':
        pair_label = 'B'
    df["DateTime"] = pd.to_datetime(datetime, format='%Y%m%d_%H%M%S')
    df["SamePayload"] = data_label
    df["TransPair"] = pair_label

    # Save DataFrame as csv
    df.to_csv(output_path / 'prr.csv', index=False)

    return df

def parse_all_data(verbose=False, force_computation=''):

    # Data paths
    data_path = Path('data_raw_cleaned')
    output_path = Path('data_preprocessed')

    # 'rssi' flag triggers the recomputation of everything from the raw data
    if force_computation == 'all':
        force_computation='rssi'

    if ((force_computation == 'prr') or (force_computation == 'rssi')):
        print('Recomputing preprocessed data...')
    else:
        try:
            df = pd.read_csv(output_path / 'data_preprocessed_all.csv')
            df.set_index('GlobalExpCount', inplace=True)
            print('Processed data retrieved.')
            return df
        except FileNotFoundError:
            print('No existing file found. Computing...')

    # Temporary data structure
    frames = []

    # Loop through all folders
    for pair in [x for x in data_path.iterdir() if x.is_dir()]:
        for data in [x for x in pair.iterdir() if x.is_dir()]:
            for datetime in [x for x in data.iterdir() if x.is_dir()]:
                if verbose:
                    print(datetime)
                # Parse RSSI measurements to get the median RSS from both
                # transmitters at the receiver side
                rssi = parse_run_rssi(pair.name,data.name,datetime.name,force_computation)
                # Parse PRR measurements, add experiment metadata,
                # RSS values, and compute the estimated PowerDelta
                prr  = parse_run_prr(pair.name,data.name,datetime.name,force_computation)
                # Append all the result to a list
                frames.append(prr)

    # Concatenate all results as a unique DataFrame,
    # do some formating clean-up and save as .csv
    result = pd.concat(frames)
    result['GlobalExpCount'] = np.arange(len(result))
    result.set_index('GlobalExpCount', inplace=True)
    result = result.rename(columns={"ExpCount": "LocalExpCount"})
    result.to_csv(output_path / 'data_preprocessed_all.csv')

    print('Done.')

    return result

def clean_raw_data():
    # Data paths
    data_path = Path('data_raw')
    output_path = Path('data_raw_cleaned')

    for pair in [x for x in data_path.iterdir() if x.is_dir()]:
        for data in [x for x in pair.iterdir() if x.is_dir()]:
            for datetime in [x for x in data.iterdir() if x.is_dir()]:

                # Create output directory if it does not exist yet
                file_path = output_path / pair.name / data.name / datetime.name
                if not (file_path).is_dir():
                    file_path.mkdir(parents=True, exist_ok=True)
                    print('Created path: %s' % str(file_path))

                # ===============
                # Clean PRR files
                # ===============
                df = pd.read_csv(str(datetime / prr_file), sep=r'\s*,\s*', engine='python')

                # Rename columns
                df = df.rename(columns={
                    "Experiment Number": "ExpCount",
                    "TX Power A": "TxPowerA",
                    "TX Power B": "TxPowerB",
                    "Time Delta": "TimeDelta",
                    "Packets Received": "RxCount",
                    "Packets Transmitted": "TxCount",
                })

                # Correct a bug in TimeDelta values:
                # -100' values are written as '100'
                TimeDelta_current = None
                for index, row in df.iterrows():
                    # print(row["Time Delta"])
                    if ((TimeDelta_current == -120) &
                        (row["TimeDelta"] == 100)):
                        row["TimeDelta"] = -100
                    TimeDelta_current = row["TimeDelta"]

                # Save DataFrame as csv
                df.to_csv(file_path / 'prr.csv', index=False)

                # ===============
                # Clean RSSI files
                # ===============
                df = pd.read_csv(str(datetime / rssi_file), sep=r'\s*,\s*', engine='python')

                # Rename columns
                df = df.rename(columns={
                    "Measurement Number": "MeasureCount",
                    "TX Power": "TxPower",
                })

                # Save DataFrame as csv
                df.to_csv(file_path / 'rssi.csv', index=False)

                # Debug output
                print('Done: %s', str(datetime))

    return

def computeTimeDeltaTraces():

    data_path = Path('data_preprocessed')

    # Load the PRR data
    df = parse_all_data()

    # X values we are interested in
    x_median = np.arange(-140, 150, 10)
    # Remove +/- 130 and 110 (not tested)
    x_median = x_median[
        (x_median != 130) &
        (x_median != 110) &
        (x_median != -110) &
        (x_median != -130)]

    for TransPair in df['TransPair'].unique():
        for SamePayload in df['SamePayload'].unique():
            for PowerDelta in df['PowerDelta'].dropna().unique():

                # Initialize the storing DataFrame
                df_median = pd.DataFrame()
                df_median["TimeDelta"] = x_median

                # Filter the data to process
                filter = (
                    (df['TransPair'] == TransPair) &
                    (df['SamePayload'] == SamePayload) &
                    (df["PowerDelta"] == PowerDelta)
                )
                filtered_df = df.where(filter).dropna()

                # Loop through the modes
                for mode in Modes:
                    # print(Modes[mode])

                    # Filter specific mode data
                    mode_filter = (filtered_df["Mode"] == Modes[mode]['id'])
                    mode_df = filtered_df.where(mode_filter).dropna()

                    # Prepare data to plot
                    if len(mode_df) > 0:
                        # Extract all data points
                        y_data = mode_df["PRR"]

                        # Compute the median and CI bounds
                        y_median = []
                        y_LB = []
                        y_UB = []
                        for x in x_median:
                            median_filter = (mode_df["TimeDelta"] == x)
                            median_data = sorted(mode_df.where(median_filter).dropna().PRR.tolist())
                            # print(median_data)
                            if len(median_data) > 0:
                                y_median.append(np.median(median_data))
                                LB, UB = ThompsonCI_twosided(len(median_data), 50, 75)
                                # print(LB,UB)
                                if LB is not np.nan:
                                    y_LB.append(median_data[LB])
                                    y_UB.append(median_data[UB])
                                else:
                                    y_LB.append(np.nan)
                                    y_UB.append(np.nan)
                            else:
                                y_median.append(np.nan)
                                y_LB.append(np.nan)
                                y_UB.append(np.nan)
                    else:
                        # Force displaying the trace, even if empty
                        y_median = [np.nan]*len(x_median)
                        y_LB = [np.nan]*len(x_median)
                        y_UB = [np.nan]*len(x_median)

                    df_median['median_'+mode] = y_median
                    df_median['LB_'+mode] = y_LB
                    df_median['UB_'+mode] = y_UB

                # Save DataFrame in CSV for fast reloading
                file_path = data_path / Parameters['TransPair'][TransPair]['path'] / Parameters['SamePayload'][SamePayload]['path']
                file_name = 'TimeDeltaTraces_%s_%s_(%i).csv' % (TransPair,SamePayload,PowerDelta)
                df_median.to_csv(file_path / file_name, index=False)

                # Debug output
                print('Done with %s' % file_name)
    return


def computePowerDeltaTraces():

    data_path = Path('data_preprocessed')

    # Load the PRR data
    df = parse_all_data()

    # X values we are interested in
    x_median = np.arange(-16, 17)

    for TransPair in df['TransPair'].unique():
        for SamePayload in df['SamePayload'].unique():
            for TimeDelta in df['TimeDelta'].dropna().unique():

                # Initialize the storing DataFrame
                df_median = pd.DataFrame()
                df_median["PowerDelta"] = x_median

                # Filter the data to process
                filter = (
                    (df['TransPair'] == TransPair) &
                    (df['SamePayload'] == SamePayload) &
                    (df["TimeDelta"] == TimeDelta)
                )
                filtered_df = df.where(filter).dropna()

                # Loop through the modes
                for mode in Modes:

                    # Filter specific mode data
                    mode_filter = (filtered_df["Mode"] == Modes[mode]['id'])
                    mode_df = filtered_df.where(mode_filter).dropna()

                    # Prepare data to plot
                    if len(mode_df) > 0:
                        # Extract all data points
                        y_data = mode_df["PRR"]

                        # Compute the median and CI bounds
                        y_median = []
                        y_LB = []
                        y_UB = []
                        for x in x_median:
                            median_filter = (mode_df["PowerDelta"] == x)
                            median_data = sorted(mode_df.where(median_filter).dropna().PRR.tolist())
                            if len(median_data) > 0:
                                y_median.append(np.median(median_data))
                                LB, UB = ThompsonCI_twosided(len(median_data), 50, 75)
                                # print(LB,UB)
                                if LB is not np.nan:
                                    y_LB.append(median_data[LB])
                                    y_UB.append(median_data[UB])
                                else:
                                    y_LB.append(np.nan)
                                    y_UB.append(np.nan)
                            else:
                                y_median.append(np.nan)
                                y_LB.append(np.nan)
                                y_UB.append(np.nan)
                    else:
                        # Force displaying the trace, even if empty
                        y_median = [np.nan]*len(x_median)
                        y_LB = [np.nan]*len(x_median)
                        y_UB = [np.nan]*len(x_median)

                    df_median['median_'+mode] = y_median
                    df_median['LB_'+mode] = y_LB
                    df_median['UB_'+mode] = y_UB

                # Save DataFrame in CSV for fast reloading
                file_path = data_path / Parameters['TransPair'][TransPair]['path'] / Parameters['SamePayload'][SamePayload]['path']
                file_name = 'PowerDeltaTraces_%s_%s_(%i).csv' % (TransPair,SamePayload,TimeDelta)
                df_median.to_csv(file_path / file_name, index=False)

                # Debug output
                print('Done with %s' % file_name)
    return
