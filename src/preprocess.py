
from pathlib import Path
import pandas as pd
import numpy as np


prr_file = 'prr.csv'
rssi_file = 'rssi.csv'

def parse_run_rssi(pair,data,datetime,force_computation=False):

    data_path = Path('data_raw')
    output_path = Path('data_preprocessed')
    data_path = data_path / pair / data / datetime
    output_path = output_path / pair / data / datetime

    if not force_computation:
        try:
            df = pd.read_csv(output_path / 'medianRSSI.csv')
            print('Processed data retrieved (not computed).')
            return df
        except FileNotFoundError:
            print('No existing file found. Computing.')

    # Create output directory if it does not exist yet
    if not output_path.is_dir():
        output_path.mkdir(parents=True, exist_ok=True)
        print('Created path: %s' % str(output_path))

    # Load RSSI data
    # -> skip leading and trailing space in column names
    rssi_df = pd.read_csv(str(data_path / rssi_file), sep=r'\s*,\s*', engine='python')

    # Create a filter for missing RSSI measurements
    filter = rssi_df["RSSI"]!="NONE"

    # Filter out the missing measurements and convert as numeric
    rssi_df = rssi_df.where(filter).dropna().astype('int32')

    # Rename columns
    rssi_df = rssi_df.rename(columns={"TX Power": "TxPower", "RSSI": "medianRSSI"})

    # Aggregate and compute the median
    rssi_medians = rssi_df.groupby(["Mode","Transmitter","TxPower"]).medianRSSI.agg('median')

    # Save as csv
    rssi_medians.to_csv(output_path / 'medianRSSI.csv')

    return rssi_medians

def parse_run_prr(pair,data,datetime,force_computation=False):

    data_path = Path('data_raw')
    output_path = Path('data_preprocessed')
    data_path = data_path / pair / data / datetime
    output_path = output_path / pair / data / datetime

    if not force_computation:
        try:
            df = pd.read_csv(output_path / 'prr.csv')
            print('Processed data retrieved (not computed).')
            return df
        except FileNotFoundError:
            print('No existing file found. Computing.')

    # Load PRR data
    # -> skip leading and trailing space in column names
    df = pd.read_csv(str(data_path / prr_file), sep=r'\s*,\s*', engine='python')

    # Load RSSI data
    rssi_df = pd.read_csv(output_path / 'medianRSSI.csv')

    # Rename columns
    df = df.rename(columns={
        "Experiment Number": "ExpCount",
        "TX Power A": "TxPowerA",
        "TX Power B": "TxPowerB",
        "Time Delta": "TimeDelta",
        "Packets Received": "RxCount",
        "Packets Transmitted": "TxCount",
    })

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

    # Loop through the rows to add
    # + PowerDelta
    # + PRR (in %)
    PowerDelta = []
    PRR = []
    for index, row in df.iterrows():

        # Compute the received power delta
        TimeDelta = row['TimeDelta']
        RssiA = row['RssiA']
        RssiB = row['RssiB']
        if TimeDelta > 0:
            PowerDelta.append(RssiB-RssiA)
        else:
            PowerDelta.append(RssiA-RssiB)

        # Compute the PRR
        RxCount = row['RxCount']
        TxCount = row['TxCount']
        PRR.append(100*RxCount/TxCount)


    # Save new info in the DataFrame
    if data == 'same_data':
        data_label = 1
    elif data == 'different_data':
        data_label = 0
    if pair == 'transmitter_pair_a':
        pair_label = 'A'
    elif pair == 'transmitter_pair_b':
        pair_label = 'B'

    df["PRR"] = PRR
    df["PowerDelta"] = PowerDelta
    df["DateTime"] = pd.to_datetime(datetime, format='%Y%m%d_%H%M%S')
    df["SamePayload"] = data_label
    df["TransPair"] = pair_label

    # Save DataFrame as csv
    df.to_csv(output_path / 'prr.csv', index=False)

    return df
