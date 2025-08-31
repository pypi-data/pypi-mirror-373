"""
Copyright (c) 2016- 2025, Wiliot Ltd. All rights reserved.

Redistribution and use of the Software in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.

  2. Redistributions in binary form, except as used in conjunction with
  Wiliot's Pixel in a product or a Software update for such product, must reproduce
  the above copyright notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.

  3. Neither the name nor logo of Wiliot, nor the names of the Software's contributors,
  may be used to endorse or promote products or services derived from this Software,
  without specific prior written permission.

  4. This Software, with or without modification, must only be used in conjunction
  with Wiliot's Pixel or with Wiliot's cloud service.

  5. If any Software is provided in binary form under this license, you must not
  do any of the following:
  (a) modify, adapt, translate, or create a derivative work of the Software; or
  (b) reverse engineer, decompile, disassemble, decrypt, or otherwise attempt to
  discover the source code or non-literal aspects (such as the underlying structure,
  sequence, organization, ideas, or algorithms) of the Software.

  6. If you create a derivative work and/or improvement of any Software, you hereby
  irrevocably grant each of Wiliot and its corporate affiliates a worldwide, non-exclusive,
  royalty-free, fully paid-up, perpetual, irrevocable, assignable, sublicensable
  right and license to reproduce, use, make, have made, import, distribute, sell,
  offer for sale, create derivative works of, modify, translate, publicly perform
  and display, and otherwise commercially exploit such derivative works and improvements
  (as applicable) in conjunction with Wiliot's products and services.

  7. You represent and warrant that you are not a resident of (and will not use the
  Software in) a country that the U.S. government has embargoed for use of the Software,
  nor are you named on the U.S. Treasury Department’s list of Specially Designated
  Nationals or any other applicable trade sanctioning regulations of any jurisdiction.
  You must not transfer, export, re-export, import, re-import or divert the Software
  in violation of any export or re-export control laws and regulations (such as the
  United States' ITAR, EAR, and OFAC regulations), as well as any applicable import
  and use restrictions, all as then in effect

THIS SOFTWARE IS PROVIDED BY WILIOT "AS IS" AND "AS AVAILABLE", AND ANY EXPRESS
OR IMPLIED WARRANTIES OR CONDITIONS, INCLUDING, BUT NOT LIMITED TO, ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY, NONINFRINGEMENT,
QUIET POSSESSION, FITNESS FOR A PARTICULAR PURPOSE, AND TITLE, ARE DISCLAIMED.
IN NO EVENT SHALL WILIOT, ANY OF ITS CORPORATE AFFILIATES OR LICENSORS, AND/OR
ANY CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES, FOR THE COST OF PROCURING SUBSTITUTE GOODS OR SERVICES,
FOR ANY LOSS OF USE OR DATA OR BUSINESS INTERRUPTION, AND/OR FOR ANY ECONOMIC LOSS
(SUCH AS LOST PROFITS, REVENUE, ANTICIPATED SAVINGS). THE FOREGOING SHALL APPLY:
(A) HOWEVER CAUSED AND REGARDLESS OF THE THEORY OR BASIS LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE);
(B) EVEN IF ANYONE IS ADVISED OF THE POSSIBILITY OF ANY DAMAGES, LOSSES, OR COSTS; AND
(C) EVEN IF ANY REMEDY FAILS OF ITS ESSENTIAL PURPOSE.
"""

import datetime
import logging
import numpy as np
import pandas as pd
import copy
from enum import Enum
from typing import Union

from wiliot_core.packet_data.config_files.parse_packet import *
from wiliot_core.utils.utils import valid_packet_start
from wiliot_core.packet_data.config_files.packet_flow_parameters import get_flow_param


FULL_PACKET_PREFIX = 'full_packet'
LEGACY_PACKET_PREFIX = 'process_packet'


packet_tag_length = 74
MAX_STAT_PARAM_VAL = 65535  # 2 bytes
MAX_GW_CLOCK = 32767  # 7 bits
MAX_TIME_DIFF = 30  # sec


class InlayTypes(Enum):
    TEO_086 = '086'
    TIKI_096 = '096'
    TIKI_099 = '099'
    BATTERY_107 = '107'
    TIKI_117 = '117'
    TIKI_118 = '118'
    TIKI_121 = '121'
    TIKI_122 = '122'
    TIKI_136 = '136'
    TIKI_H_160 = '160'
    TIKI_160 = '160'
    TIKI_168 = '168'
    TIKI_169 = '169'
    TIKI_170 = '170'
    TIKI_179 = '179'
    TIKI_184 = '184'
    TIKI_191 = '191'


class Packet(object):
    """
    Wiliot Packet Object

        :param raw_packet: the raw packet to create a Packet object
        :type raw_packet: str or dict

        :return:
    """

    def __init__(self, raw_packet:str, time_from_start:float=None, custom_data:dict=None,
                 inlay_type:Union[str, InlayTypes]=None, logger_name:str=None, ignore_crc:bool=False):
        """
        :param raw_packet:
        :type raw_packet: str
        :param time_from_start: the time when the packet was received according to the gw timer
        :type time_from_start: float
        :param custom_data: the packet custom data as dictionary
        :type custom_data: dict
        :param inlay_type: the antenna/ inlay type (e.g. tiki, teo)
        :type inlay_type: str | InlayTypes
        :param logger_name: the logger name we want to use.
        :type logger_name: str
        :param ignore_crc: if True, update for all packets crc_valid = True,
                           relevant for data collected by old GW FW version
        :type ignore_crc: bool
        """

        self.logger = logging.getLogger(logger_name) if logger_name else None
        self.is_valid_packet = False

        # check packet type:
        if FULL_PACKET_PREFIX in raw_packet:
            self.is_full_packet = True
        elif LEGACY_PACKET_PREFIX in raw_packet:
            self.is_full_packet = False
        else:
            self.is_full_packet = None

        # parse packet
        try:
            packet_in_strip = valid_packet_start(raw_packet) or raw_packet
            self.gw_data, self.packet_data = parse_packet(packet_in_strip, time_from_start, self.is_full_packet, ignore_crc)

            # assign results
            self.is_valid_packet = True
        except Exception as e:
            self.printing_and_logging(f'Could not parse the following packet {raw_packet} due to {e}')
            self.is_valid_packet = False
            self.gw_data , self.packet_data = {} , {} # Define not valid packet .gw_data or .packet_data as empty dicts 
        
        self.is_valid_packet = self.check_enc_payload() if self.is_valid_packet else False
            
        # add more info to packet struct
        self.decoded_data = {}
        if custom_data is not None:
            self.custom_data = custom_data
        else:
            self.custom_data = {}
        if 'timestamp' not in self.custom_data.keys():
            self.custom_data['timestamp'] = [datetime.datetime.now().timestamp() * 1000]  # ms
        self.inlay_type = inlay_type

        if self.is_valid_packet:
            if self.packet_data['ble_type'] in ['BLE5-EXT', 'BLE5-DBL-EXT']:
                self.custom_data['adi_per_packet'] = [self.packet_data['adi']]
                self.packet_data['raw_packet'] = construct_packet_from_fields(packet_data=self.packet_data,
                                                                              fields_to_zero=['adi'])

    def __len__(self) -> int:
        """
        gets number of sprinkler occurrences in packet
        """
        if self.is_valid_packet:
            return self.gw_data['rssi'].size
        return 0

    def __eq__(self, packet) -> bool:
        """
        packet comparison
        """
        if self.is_same_sprinkler(packet):
            if len(packet) == self.__len__():
                return all([np.take(packet.gw_data['gw_packet'], i) == np.take(self.gw_data['gw_packet'], i)
                            for i in range(len(packet))])
        return False

    def __str__(self) -> str:
        """
        packet print method
        """
        return str(
            'packet_data={packet_data}, gw_data={gw_data}'.format(packet_data=self.packet_data, gw_data=self.gw_data))

    def get_valid_len(self) -> int:
        """
        get the packet length (the number of packets per sprinkler) with valid crc
        """
        if not self.is_valid_packet:
            return 0
        return int(self.gw_data['crc_valid'].sum())


    def is_decrypted(self) -> bool:
        if self.is_valid_packet:
            if self.packet_data['group_id'] == '0' * len(self.packet_data['group_id']):
                return True
            half_mic_size = len(self.packet_data['mic']) // 2
            if self.packet_data['mic'][-half_mic_size:] == '0' * half_mic_size:
                if 'DBL' in self.packet_data.get('ble_type', 'DBL'):
                    return self.packet_data['mic'][:half_mic_size] == '0' * half_mic_size
                else:
                    return True
            
        return False

    def check_enc_payload(self) -> bool:
        enc_payload = self.packet_data['enc_payload']
        if len(enc_payload) == 0:
            self.printing_and_logging(f'empty tag data payload')
            return False
        if enc_payload == enc_payload[0] * len(enc_payload):
            self.printing_and_logging(f'identical characters in the tag data payload: {enc_payload}')
            return False
        return True

    def printing_and_logging(self, message) -> None:
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

    def is_packet_from_bridge(self) -> bool:
        if self.is_valid_packet:
            return self.packet_data['is_packet_from_bridge']
        return False

    def get_payload(self):
        if self.is_valid_packet:
            return self.packet_data['data_uid'] + self.packet_data['raw_group_id'] + self.packet_data['nonce'] + \
                   self.packet_data['enc_uid'] + self.packet_data['mic'] + self.packet_data['enc_payload']
        else:
            return ''

    def get_group_id(self)-> str:
        if not self.is_valid_packet:
            return ''
        return self.packet_data['group_id']

    def set_inlay_type(self, inlay_type):
        inlay_type = inlay_type if isinstance(inlay_type, str) else inlay_type.value
        self.inlay_type = inlay_type

    def is_in(self, packet):
        """
        is packet contains another packet

        :param packet: the other packet to verify
        :type packet: Packet

        :return: bool
        """
        if self.is_same_sprinkler(packet):
            if np.take(packet.gw_data['gw_packet'], 0) in self.gw_data['gw_packet']:
                return True
        return False

    def get_packet(self):
        """
        gets raw packet string
        """
        return str(self.packet_data['raw_packet'])

    def split_packet(self, index):
        """
        split packet by index
        """
        packet_a = self.copy()
        packet_b = self.copy()
        remain = len(self) - index
        for key in self.gw_data.keys():
            for i in range(index):
                packet_a.gw_data[key] = np.delete(packet_a.gw_data[key], -1)

            for i in range(remain):
                packet_b.gw_data[key] = np.delete(packet_b.gw_data[key], 0)

        return packet_a, packet_b

    def copy(self):
        return copy.deepcopy(self)

    def sort(self):
        """
        sort gw_data lists according to gw_time
        """
        isort = np.argsort(self.gw_data['gw_clock'])
        for key in self.gw_data.keys():
            self.gw_data[key] = self.gw_data[key][isort]

    def get_average_rssi(self) -> float:
        if self.is_valid_packet:
            return np.average(self.gw_data['rssi'])
        return 0

    def get_packet_size(self) -> int:
        return int(self.packet_data['packet_length'])

    def is_short_packet(self) -> bool:
        return len(self.get_packet_string(process_packet=False)) < self.get_packet_size()
    
    def get_packet_output(self, raw_packet=None, sprinkler_num=0, gw_data=True, process_packet=True, full_packet=False) -> str:
        """Returns a packet string, optionally processed and/or combined with gateway data."""
        if raw_packet is None:
            parsed_packet = self
        else:
            raw_packet = valid_packet_start(raw_packet) or raw_packet
            parsed_packet = Packet(raw_packet=raw_packet)

        if not self.is_valid_packet:
            return ''
        
        if process_packet and full_packet:
            raise ValueError('Cannot set both full_packet and process_packet as True')

        wrapper = ['', '']
        if process_packet:
            wrapper = ['process_packet("', '")']
        elif full_packet:
            wrapper = ['full_packet("', '")']

        gw_string = ''
        if gw_data:
            gw_list= parsed_packet.gw_data['gw_packet']
            if sprinkler_num < len(parsed_packet):
                gw_string = gw_list.take(sprinkler_num)
            else:
                raise IndexError("sprinkler_num is out of range")
        return '{raw_packet}{gw_data}'.format(raw_packet=parsed_packet.packet_data['raw_packet'], gw_data=gw_string).join(wrapper)

    def get_packet_string(self, i=0, gw_data=True, process_packet=True, full_packet=False) -> str:        # Gets formatted packet string, legacy wrapped.
        return self.get_packet_output(raw_packet=None, gw_data=gw_data, sprinkler_num=i, process_packet=process_packet, full_packet=full_packet)    
    
    def get_packet_content(self, raw_packet=None, get_gw_data=False, sprinkler_num=0) -> str:
        # Returns raw packet content optionally with gateway data.
        return self.get_packet_output(raw_packet=raw_packet, gw_data=get_gw_data, sprinkler_num=sprinkler_num, process_packet=False, full_packet=False)

    def get_adva(self) -> str:
        if not self.is_valid_packet:
            return ''
        return self.packet_data['adv_address']

    def get_flow(self) -> str:
        if not self.is_valid_packet:
            return ''
        flow_version = hex(int(self.packet_data['flow_ver'], 16))
        return flow_version

    def get_rssi(self) -> str:
        if not self.is_valid_packet:
            return '[]'
        return str(self.gw_data['rssi'])

    def is_same_sprinkler(self, packet: 'Packet') -> bool:
        if self.is_valid_packet:
            payload = packet.get_payload()
            if payload == self.get_payload():
                return True
            return False
        return None

    def append_to_sprinkler(self, packet: 'Packet', output_log=True, do_sort=False) -> bool:
        if not self.is_valid_packet or not packet.is_valid_packet:
            self.printing_and_logging('Cannot append to sprinkler invalis packets')
            status = False
        if (self.packet_data['raw_packet']!=packet.packet_data['raw_packet']
            and any(packet.gw_data['crc_valid']==1) and all(self.gw_data['crc_valid']==0)):
            # copy values from packet to self
            self.packet_data = copy.deepcopy(packet.packet_data)
            self.decoded_data = copy.deepcopy(packet.decoded_data)
            self.is_valid_packet = packet.is_valid_packet

        status = True
        if self.is_same_sprinkler(packet):
            for i in range(len(packet)):
                try:
                    # stat param should be unique (time + rssi for same packet)- we make sure no duplications are added.
                    if np.take(packet.gw_data['gw_clock'], i) not in self.gw_data['gw_clock'] or \
                            np.take(packet.gw_data['time_from_start'], i) not in self.gw_data['time_from_start']:
                        for key in gw_data_info.keys():
                            self.gw_data[key] = np.append(self.gw_data[key], np.take(packet.gw_data[key], i))
                        for key in self.custom_data.keys():
                            if key in packet.custom_data.keys():
                                self.custom_data[key] = np.append(self.custom_data[key],
                                                                  np.take(packet.custom_data[key], i))
                            else:
                                self.custom_data[key] = np.append(self.custom_data[key], [None])
                        
                        if do_sort:
                            sort_idx = self.gw_data['time_from_start'].argsort()
                            for k, v in self.gw_data.items():
                                self.gw_data[k] = v[sort_idx]
                            for k, v in self.custom_data.items():
                                self.custom_data[k] = v[sort_idx]
                    else:
                        if output_log:
                            self.printing_and_logging('Tried to add duplicated packet to sprinkler {}'.format(packet))
                except Exception as e:
                    self.printing_and_logging('Failed to add packet {} to sprinkler, exception: {}'
                                              .format(packet, str(e)))
        else:
            self.printing_and_logging('Not from the same sprinkler')
            status = False
        # self.sort()
        return status

    def as_dict(self, sprinkler_index=None) -> dict:  # None not tested
        if not self.is_valid_packet:
            return {}
        else:
            packet_data = self.packet_data.copy()
            sprinkler_gw_data = self.gw_data.copy()
            custom_data = self.custom_data.copy()
            if sprinkler_index is not None:
                if sprinkler_index > self.gw_data['stat_param'].size:
                    return None
                for gw_attr in gw_data_info.keys():
                    sprinkler_gw_data[gw_attr] = np.take(self.gw_data[gw_attr], sprinkler_index)
                for custom_attr in self.custom_data.keys():
                    custom_data[custom_attr] = np.take(self.custom_data[custom_attr], sprinkler_index)
                dict_len = 1
            else:
                dict_len = len(self)
                for k, v in packet_data.items():
                    if k == 'raw_packet' and 'adi_per_packet' in custom_data.keys():
                        adi_per_packet_list = custom_data['adi_per_packet']
                        if not isinstance(custom_data['adi_per_packet'], list) and \
                                not isinstance(custom_data['adi_per_packet'], np.ndarray):
                            adi_per_packet_list = [adi_per_packet_list] * dict_len
                        if pd.notna(adi_per_packet_list).all():
                            original_raw_packets = [construct_packet_from_fields(
                                packet_data=self.packet_data,
                                fields_to_convert={'adi': adi_per_packet}) for adi_per_packet in adi_per_packet_list]
                            packet_data[k] = original_raw_packets
                            continue
                    packet_data[k] = [v] * dict_len

            data = {**packet_data, **sprinkler_gw_data}
            data['is_valid_packet'] = np.array([self.is_valid_packet] * dict_len)
            data['inlay_type'] = np.array([self.inlay_type] * dict_len)
            for k, v in custom_data.items():  # add to df only custom data keys that are not part of the packet
                if k not in data:
                    data[k] = v
            return data
        

    def as_dataframe(self, sprinkler_index=None) -> pd.DataFrame:
        data = self.as_dict(sprinkler_index=sprinkler_index)
        packet_df = pd.DataFrame.from_dict(data)

        return packet_df

    def get_per(self, expected_sprinkler_count=None) -> float:
        """
        Calculates the packet per at the sprinkler
        @param expected_sprinkler_count - The number of packet per sprinkler
        @return packet per at percentage
        """
        if expected_sprinkler_count is None:
            if self.packet_data['test_mode']:
                expected_sprinkler_count = 6
            else:
                expected_sprinkler_count = get_flow_param(flow_in=self.packet_data['flow_ver'],
                                                          param_name='sprinkler_num', args=self.packet_data['decrypted_packet_type'])
        
        return 1 - (self.get_valid_len() / expected_sprinkler_count)

    def get_tbp(self) -> float:
        """
        calculates the rate of packets from the same sprinkler
        :return: min_times_found - in msec
        :rtype: int
        """

        def triad_ratio_logic(diff_time_1, diff_time_2, ratio=1.0, error=10):
            """ estimate the time between successive packet according to only 3 packets out of 6 """
            if abs(diff_time_1 - ratio * diff_time_2) <= diff_time_2 / error:
                return True
            elif abs(diff_time_1 - (1 / ratio) * diff_time_2) <= diff_time_1 / error:
                return True
            else:
                return False

        def estimate_diff_packet_time(times_list, pc_time_list):
            if times_list.size < np.ceil(sprinkler_num / 2) or times_list.size <= 1:
                return None
            if times_list.size == sprinkler_num / 2 and times_list.size <= 2:
                return None  # cannot estimate with only one time diff 
            # sorting based on the pc time:
            sort_idx = pc_time_list.argsort()
            pc_time_list_sorted = pc_time_list.copy()[sort_idx]
            times_list_sorted = times_list.copy()[sort_idx]

            dt = []
            for i, t_hw in enumerate(zip(times_list_sorted[1::], times_list_sorted[:-1])):
                dt_tmp = t_hw[0] - t_hw[1]
                dt_pc = round((pc_time_list_sorted[i + 1] - pc_time_list_sorted[i]) * 1000)
                if dt_pc >= MAX_GW_CLOCK:
                    # HW timing was zeroing during the same packets sprinkler
                    dt_tmp = dt_pc
                elif dt_tmp < 0:
                    dt_tmp += MAX_GW_CLOCK

                if abs(dt_pc - dt_tmp) > MAX_TIME_DIFF * 1000:
                    dt_tmp = dt_pc

                dt.append(dt_tmp)

            return dt

        def check_if_nan(lst):
            is_nan = pd.isnull(lst)
            if isinstance(is_nan, bool):
                return is_nan
            if isinstance(is_nan.tolist(), bool):
                return is_nan.tolist()
            if isinstance(is_nan, np.ndarray):
                return any(is_nan)
            return False

        def estimate_tbp_from_3_packets(estimate_diff_time):
            # gen 2 - got 3 packets, need to estimate
            if triad_ratio_logic(estimate_diff_time[0], estimate_diff_time[1], ratio=1):
                # equal distance between packets, can't decide if successive
                return None
            else:
                is_estimated = False
                for ratio in [2, 3, 4]:
                    if triad_ratio_logic(estimate_diff_time[0], estimate_diff_time[1], ratio=ratio):
                        estimate_diff_time = [min(estimate_diff_time[0], estimate_diff_time[1]),
                                              max(estimate_diff_time[0], estimate_diff_time[1]) / ratio]
                        is_estimated = True
                        break
                if not is_estimated and triad_ratio_logic(estimate_diff_time[0], estimate_diff_time[1], ratio=1.5):
                    estimate_diff_time = [min(estimate_diff_time[0], estimate_diff_time[1]) / 2,
                                          max(estimate_diff_time[0], estimate_diff_time[1]) / 3]
                    is_estimated = True
            return estimate_diff_time if is_estimated else None


        time_from_start = self.gw_data['time_from_start'][self.gw_data['crc_valid'] == 1]
        gw_clock = self.gw_data['gw_clock'][self.gw_data['crc_valid'] == 1]

        if check_if_nan(time_from_start) or check_if_nan(gw_clock):
            return None

        sprinkler_num = get_flow_param(flow_in=self.packet_data['flow_ver'], param_name='sprinkler_num', args=self.packet_data['decrypted_packet_type'])
        estimate_diff_time = estimate_diff_packet_time(gw_clock, time_from_start)
        if estimate_diff_time is None:
            return None
        elif len(self) == sprinkler_num/2 and sprinkler_num == 6:
            estimate_diff_time = estimate_tbp_from_3_packets(estimate_diff_time)

        return int(min(estimate_diff_time)) if estimate_diff_time is not None else None

    def extract_packet_data_by_name(self, key):
        """
        extract data from all packet attribute according to the key name
        :param key: the name of the data (the key of the relevant dictionary)
        :type key: str
        :return: list of the data
        :rtype: list
        """
        if self.is_valid_packet:
            if key in self.packet_data:
                data_attr = self.packet_data[key]
            elif hasattr(self, 'decoded_data') and key in self.decoded_data:
                data_attr = self.decoded_data[key]
            elif key in self.gw_data:
                data_attr = self.gw_data[key]
            elif key in self.custom_data:
                data_attr = self.custom_data[key]
            else: # key doesn't exist
                self.printing_and_logging('key:{} does not exist in packet structure')
                return None
            if isinstance(data_attr, np.ndarray):
                data_attr = data_attr.tolist()
            if not isinstance(data_attr, list):
                data_attr = [data_attr]
            return data_attr
        return None # Invalid packet

    def filter_by_sprinkler_id(self, sprinkler_ids : list):
        """
        keep only specific sprinklers in a packet according to the sprinkler id
        :param sprinkler_ids:
        :type sprinkler_ids: list
        :return: filtered packet
        :rtype: Packet or DecryptedPacket
        """

        def filter_per_attr(data_attr):
            for key in data_attr.keys():
                if isinstance(data_attr[key], list) or \
                        (isinstance(data_attr[key], np.ndarray) and data_attr[key].size > 1):
                    filtered_data = [data_attr[key][i] for i in sprinkler_ids]
                    if isinstance(data_attr[key], np.ndarray):
                        data_attr[key] = np.array(filtered_data)
                    else:
                        data_attr[key] = filtered_data
            return data_attr

        filtered_packet = self.copy()
        filtered_packet.gw_data = filter_per_attr(filtered_packet.gw_data)
        filtered_packet.custom_data = filter_per_attr(filtered_packet.custom_data)

        return filtered_packet

    def add_custom_data(self, custom_data: dict):
        for key in custom_data.keys():
            if isinstance(custom_data[key], list):
                if len(custom_data[key]) == self.__len__():
                    self.custom_data[key] = custom_data[key]
                else:
                    self.printing_and_logging('add_custom_data failed - '
                                              'the custom data is a list of a different length than'
                                              ' the number of packets')
            else:
                self.custom_data[key] = self.__len__() * [custom_data[key]]


if __name__ == '__main__':

    # test mode packets with different adi, same sprinkler:
    testing_82_tm_adi0 = Packet(
        'full_packet("4731090906D03E34CD8200001EFF000505000060750774415ACDFFFBD069756C550DB1FD75E7B127312C21F3B10A03B1CB12AF2D45AC")')
    testing_82_tm_adi1 = Packet(
        'full_packet("4731090906D03E34CD8200011EFF000505000060750774415ACDFFFBD069756C550DB1FD75E7B127312C21F3B10A03B1CB12AF2D45CE")')
    testing_82_tm_adi2 = Packet(
        'full_packet("4731090906D03E34CD8200031EFF000505000060750774415ACDFFFBD069756C550DB1FD75E7B127312C21F3B10A03B1CB12AF2D4615")')
    testing_82_tm_adi0.append_to_sprinkler(testing_82_tm_adi1)
    testing_82_tm_adi0.append_to_sprinkler(testing_82_tm_adi2)
    print(f'packet len: {len(testing_82_tm_adi0)} with the following adi: '
          f'{testing_82_tm_adi0.custom_data["adi_per_packet"]}')

    packet_2 = '03B28DCD99201EFF0005FE0000E0210FFF93B635EBFF1DB118C6D782DC2ED98C404200486436AE82'

    p1 = Packet('03B28DCD99201EFF0005FE0000E0210FFF93B635EBFF1DB118C6D782DC2ED98C404200486436AE8F', 1.528374)

    print(p1.get_packet_content('03B28DCD99201EFF0005FE0000E0210FFF93B635EBFF1DB118C6D782DC2ED98C404200486436AE82', get_gw_data=True),)

    p2 = Packet(packet_2)

    p3 = Packet('0437E62F33341E16AFFD02000058AD2AE76DE1D314B003083386A2A1AD139E42C10A0448F93472DC')
    print(p3.get_payload())

    packet_no_gw = Packet('03B28DCD99201EFF0005FE0000E0210FFF93B635EBFF1DB118C6D782DC2ED98C4042004864')
    packet_corrupted_length = Packet('03B28DCD99201EFF0005FE0000E0210FFF93B635EBFF1DB118C6D782DC2ED98C4042004864x')

    print(p1.get_packet_string(0))
    print(p1.get_average_rssi())

    print(p1 == p2)
    print(p1.append_to_sprinkler(p2))

    p6_1 = Packet(raw_packet='473109090673E063E00800002616AFFDFE0080FB7140E0F9B527E8E4751A0A18A99E360281421735AF8A000281415D687CC27F529230',
                  time_from_start=81.092617)
    p6_2 = Packet(raw_packet='473109090673E063E00800002616AFFDFE0080FB7140E0F9B527E8E4751A0A18A99E360281421735AF8A000281415D687CC27F52DEA2',
                  time_from_start=228.187184)
    p6 = p6_1.append_to_sprinkler(p6_2)
    tbp = p6_1.get_tbp()

    p6_3 = Packet(raw_packet='473109090695564AAB0800002616AFFDFE00C05AA9955A56FF3B552A24B28D275BDC8647CFDA0750ABA8541FF99340948F41D450AFCC',
                  time_from_start=38.627151)
    p6_4 = Packet(
        raw_packet='473109090695564AAB0800002616AFFDFE00C05AA9955A56FF3B552A24B28D275BDC8647CFDA0750ABA8541FF99340948F41D451BB8E',
        time_from_start=105.55923)
    p6a = p6_3.append_to_sprinkler(p6_4)
    tbp2 = p6_3.get_tbp()

    p6_5 = Packet(
        raw_packet='473109090695564AAB0800002616AFFDFE00C05AA9955A56FF3B552A24B28D275BDC8647CFDA0750ABA8541FF99340948F41D450FFFC',
        time_from_start=0.0)
    p6_6 = Packet(
        raw_packet='473109090695564AAB0800002616AFFDFE00C05AA9955A56FF3B552A24B28D275BDC8647CFDA0750ABA8541FF99340948F41D4510010',
        time_from_start=10.55923)
    p6b = p6_5.append_to_sprinkler(p6_6)
    tbp3 = p6_5.get_tbp()

    p6_7 = Packet(
        raw_packet='06455AD22E061E16AFFDFE0040FFBD941223357780F3FBC45BA7E13D7E6AFB4F89D61463EA3EFF9A',
        time_from_start=55796.199652)
    p6_8 = Packet(
        raw_packet='06455AD22E061E16AFFDFE0040FFBD941223357780F3FBC45BA7E13D7E6AFB4F89D61463EA3E00DA',
        time_from_start=55796.199652)
    p67 = p6_7.append_to_sprinkler(p6_8)
    tbp4 = p6_7.get_tbp()

    print(len(p1))
    print(p1.get_average_rssi())

    p1_dict = p1.as_dict()
    p1_df = pd.DataFrame(data=p1_dict)
    print(p1_df)

    print('end')
