We performed experiments with two pairs of boards in order to investigate the potential impact of the carrier frequency difference between the transmitters. The `transmitter_pairs.md` file contains the part number of the board we used together with measurements of their carrier frequency, realized using a spectrum analyzer.

The data are stored
- in one directory per pair
- in two directories depending on whether the same (`same_data`) or different (`different_data`) payload were sent
- in one directory per run, named by the time of the experiment (formatted as `YYYYMMDD_HHMMSS`)
- in two CSV files (`prr.csv` and `rssi.csv`) with data columns description provided below.

### prr.csv
|Column|Description|
|-|-|
|ExpCount|ID of the parameter settings combination|
|TxPowerA|Transmit power set on Transmitter 0, in dB|
|TxPowerB|Transmit power set on Transmitter 1 in dB|
|Mode|Communication mode, see the mode table below|
|TimeDelta|Time delta, in timer ticks. 1 tick = 62.5 ns|
|RxCount|Number of packets received for the parameter combination ID|
|TxCount|Number of packets transmitted for the parameter combination ID|



### Communication mode
|Mode ID|Mode|
|-|-|
|0|IEEE 802.15.4|
|1|BLE 1 Mbit|
|2|BLE 2 Mbit|
|3|BLE 125 kbit|
|4|BLE 500 kbit|
