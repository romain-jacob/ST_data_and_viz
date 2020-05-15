import src.colors as colors

Modes = dict(
    ZigBee      = dict(
        id=0,
        color=colors.violet,
        label="IEEE 802.15.4",
        CIthreshold_ticks=4,
        CIthreshold_label='$\\tau\\text{/2} \\; \\text{ (0.25}\\,\\mu\\text{s}\\text{)}$',
        # CIthreshold_label='$\\;\\;\\tau\\text{/2} \\\\ \\text{0.25}\\mu\\text{s}$',
        # CIthreshold_label_minus='$\\text{-}\\tau\\text{/2}$'
    ),
    BLE_2M      = dict(
        id=2,
        color=colors.green,
        label="BLE 2 Mbit",
        CIthreshold_ticks=6,
        CIthreshold_label='$\\text{3/4}\\tau \\; \\text{ (0.375}\\,\\mu\\text{s}\\text{)}$',
        # CIthreshold_label='$\\;\\;\\,\\text{3/4}\\tau \\\\ \\text{0.375}\\mu\\text{s}$',
        # CIthreshold_label_minus='$\\text{-3/4}\\tau$'

    ),
    BLE_1M      = dict(
        id=1,
        color=colors.blue,
        label="BLE 1 Mbit",
        CIthreshold_ticks=12,
        CIthreshold_label='$\\text{3/4}\\tau \\; \\text{ (0.75}\\,\\mu\\text{s}\\text{)}$',
        # CIthreshold_label='$\\;\\;\\text{3/4}\\tau \\\\ \\text{0.75}\\mu\\text{s}$',
        # CIthreshold_label_minus='$\\text{-3/4}\\tau$'
    ),
    BLE_500K    = dict(
        id=4,
        color=colors.orange,
        label="BLE 500 kbit",
        CIthreshold_ticks=4,
        CIthreshold_label='$\\tau\\text{/4} \\; \\text{ (0.25}\\,\\mu\\text{s}\\text{)}$',
        # CIthreshold_label='$\\;\\;\\tau\\text{/4} \\\\ \\text{0.25}\\mu\\text{s}$',
        # CIthreshold_label_minus='$\\text{-}\\tau\\text{/4}$'
    ),
    BLE_125K    = dict(
        id=3,
        color=colors.red,
        label="BLE 125 kbit",
        CIthreshold_ticks=8,
        CIthreshold_label='$\\tau\\text{/2} \\; \\text{ (0.50}\\,\\mu\\text{s}\\text{)}$',
        # CIthreshold_label='$\\;\\;\\tau\\text{/2} \\\\ \\text{0.50}\\mu\\text{s}$',
        # CIthreshold_label_minus='$\\text{-}\\tau\\text{/2}$'
    ),
)

Parameters = dict(
    SamePayload     = [
            dict(path = 'different_data'),
            dict(path = 'same_data'),
    ],
    TransPair       = dict(
            A = dict(path = 'transmitter_pair_a'),
            B = dict(path = 'transmitter_pair_b'),
            all = dict(path = 'transmitter_pair_all'),
    ),
)
