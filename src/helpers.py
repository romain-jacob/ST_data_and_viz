import src.colors as colors

Modes = dict(
    ZigBee      = dict(
        id=0,
        color=colors.violet,
        label="IEEE 802.15.4"
    ),
    BLE_2M      = dict(
        id=2,
        color=colors.green,
        label="BLE 2 Mbit"
    ),
    BLE_1M      = dict(
        id=1,
        color=colors.blue,
        label="BLE 1 Mbit"
    ),
    BLE_500K    = dict(
        id=4,
        color=colors.orange,
        label="BLE 500 Kbit"
    ),
    BLE_125K    = dict(
        id=3,
        color=colors.red,
        label="BLE 125 Kbit"
    ),
)
