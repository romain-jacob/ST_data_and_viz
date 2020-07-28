This directory contains preprocessed data facilitating future data analysis. The data in this directory are generated using the `parse_all_data` function available in `/src/preprocess.py`.

> We performed experiments with two pairs of boards in order to investigate the potential impact of the carrier frequency difference between the transmitters. See `../data_raw/README.md` for details.

The preprocessed data are stored
- in one directory per pair or in a directory aggregating all pairs (`transmitter_pair_all`)
- in two directories depending on whether the same (`same_data`) or different (`different_data`) payload were sent
- in one directory per run, named by the time of the experiment (formatted as `YYYYMMDD_HHMMSS`)
- in two CSV files (`medianRSSI.csv` and `prr.csv`) with data columns description provided below.

In addition the directory contains, for each transmitter pairs and payload folders, two series of CSV files named
- `PowerDeltaTraces_X_Y_(Z).csv`
- `TimeDeltaTraces_X_Y_(Z).csv`

where
- `X` indicates the transmitter pair (`A`, `B`, or `all`)
- `Y` indicates whether transmitters sent the same (`1`) or different (`0`) packets
- `Z` indicates a given
  + time delta in timer ticks in `PowerDeltaTraces_X_Y_(Z).csv`
  + power delta in dB in `TimeDeltaTraces_X_Y_(Z).csv`

Thus, the file name describes the corresponding test settings. For this setting, these files contain PRR statistics computed over the different runs using the same settings. Namely, for mode `M`, the file columns contain:

|Column|Description|
|-|-|
|PowerDelta|Power delta difference at the receiver, in dB. In `PowerDeltaTraces_X_Y_(Z).csv` only|
|TimeDelta|Time delta, in timer ticks. In `TimeDeltaTraces_X_Y_(Z).csv` only|
|median_`M`|Median PRR value, in percentage|
|LB_`M`| Lower bound of the two-sided 75% confidence interval on the median PRR value, in percentage|
|UB_`M`| Upper bound of the two-sided 75% confidence interval on the median PRR value, in percentage|

Values are left empty when there are no data points available or not enough to compute the confidence interval.

Finally, the `data_preprocessed_all.csv` file is an aggregate of all the `prr.csv` files in the directory, only extended with a `GlobalExpCount` column serving as a global identifier.

### medianRSSI.csv
Contains the median RSSI measurements per setting computed from the raw data (`/data_raw/.../rssi.csv`)

|Column|Description|
|-|-|
|Mode|Communication mode, see the mode table below|
|Transmitter|ID of the transmitter (0 or 1)|
|TxPower|Transmit power set at the transmitter, in dB|
|medianRSSI| median RSSI value measured at the receiver, in dB. Settings leading to no successful RSSI measurements are not included in the file.|

### prr.csv
Extends the raw PRR data (`/data_raw/.../prr.csv`) with RSSI and metadata.

|Column|Description|
|-|-|
|ExpCount|ID of the parameter settings combination|
|TxPowerA|Transmit power set on Transmitter 0, in dB|
|TxPowerB|Transmit power set on Transmitter 1 in dB|
|Mode|Communication mode, see the mode table below|
|TimeDelta|Time delta, in timer ticks. 1 tick = 62.5 ns|
|RxCount|Number of packets received for the parameter combination ID|
|TxCount|Number of packets transmitted for the parameter combination ID|
|RssiA|Median RSSI measurement of Transmitter 0, in dB. Empty if no valid measurements available.|
|RssiB|Median RSSI measurement of Transmitter 1, in dB. Empty if no valid measurements available.|
|PRR| PRR at the receiver, in percentage|
|PowerDelta|Power delta difference at the receiver, in dB. Computed as the absolute difference between `RssiA` and `RssiB`.  Empty if no valid measurements available for either Transmitter 0 or 1.|
|DateTime|Timestamp of the run, formatted as `YYYY-MM-DD HH:MM:SS`|
|SamePayload|Identify whether transmitters sent the same (`1`) or different (`0`) packets.|
|TransPair|Identifier of the transmitter pair (`A` or `B`)|

### Communication mode
|Mode ID|Mode|
|-|-|
|0|IEEE 802.15.4|
|1|BLE 1 Mbit|
|2|BLE 2 Mbit|
|3|BLE 125 kbit|
|4|BLE 500 kbit|
