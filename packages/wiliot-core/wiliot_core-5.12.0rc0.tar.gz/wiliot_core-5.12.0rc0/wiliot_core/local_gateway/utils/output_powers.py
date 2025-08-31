from enum import Enum


class OutputPowers(Enum):
    pos0dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_0dBm', 'numeric_val': 0}
    pos2dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Pos2dBm', 'numeric_val': 2}
    pos3dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Pos3dBm', 'numeric_val': 3}
    pos4dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Pos4dBm', 'numeric_val': 4}
    pos5dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Pos5dBm', 'numeric_val': 5}
    pos6dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Pos6dBm', 'numeric_val': 6}
    pos7dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Pos7dBm', 'numeric_val': 7}
    pos8dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Pos8dBm', 'numeric_val': 8}
    neg4dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Neg4dBm', 'numeric_val': -4}
    neg8dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Neg8dBm', 'numeric_val': -8}
    neg12dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Neg12dBm', 'numeric_val': -12}
    neg16dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Neg16dBm', 'numeric_val': -16}
    neg20dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Neg20dBm', 'numeric_val': -20}
    neg30dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Neg30dBm', 'numeric_val': -30}
    neg40dbm = {'output_power': 'RADIO_TXPOWER_TXPOWER_Neg40dBm', 'numeric_val': -40}
