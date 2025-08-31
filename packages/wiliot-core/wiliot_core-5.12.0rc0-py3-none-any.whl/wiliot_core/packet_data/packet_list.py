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

import logging
import numpy as np
import pandas as pd
import copy
import inspect
import re
import os
import datetime

from wiliot_core.packet_data.packet import Packet, InlayTypes
from wiliot_core.packet_data.config_files.parse_packet import extract_packet_data_types, extract_gw_data_types
from wiliot_core.packet_data.utils.convert_cloud_packets import ConvertCloudPacket
from wiliot_core.packet_data.utils.dewhiten_packet import dewhitening_packets
from wiliot_core.packet_data.config_files.stat_calculation import StatisticsCalc


class PacketList(list):
    def __init__(self, packet_obj_type=Packet, packet_list_obj_type=None, list_custom_data=None, logger_name=None):
        """
        :param packet_obj_type:
        :param packet_list_obj_type:
        :param list_custom_data: the packet_list custom data as dictionary
        :type list_custom_data: dict
        :param logger_name: the log file we want to write into it.
        """
        self.packet_list = np.array([], dtype=Packet)  # ndarray - contains packets
        self.payload_map_list = {} # dict - keys: payload, values: index in self.packet_list
        self.unique_group_ids = set()
        self.is_df_changed = True
        self.packet_df = None
        self.packet_obj_type = packet_obj_type
        if packet_list_obj_type is None:
            self.packet_list_obj_type = PacketList
        else:
            self.packet_list_obj_type = packet_list_obj_type

        if list_custom_data is not None:
            self.list_custom_data = list_custom_data
        else:
            self.list_custom_data = {}
        if logger_name is not None:
            self.logger = logging.getLogger(logger_name)
        else:
            self.logger = None

    def __add__(self, other_packet_list):
        """
        merge 2 PacketList object using '+' sign: packet_list1+packet_list2

        :type other_packet_list: PacketList
        :param other_packet_list:

        :return: merged packet_list, not mandatory
        """
        for packet in other_packet_list.packet_list:
            self.append(packet=packet)

        return self

    def printing_and_logging(self, message):
        if self.logger:
            self.logger.warning(message)
        else:
            print(message)

    def __len__(self):
        """
        Total amount of packets (sprinklers calculated separately)
        """
        return self.size()

    def __iter__(self):
        self.n = 0
        return iter(self.packet_list)

    def __next__(self):
        if self.n <= len(self):
            return self.packet_list[self.n]
        else:
            raise StopIteration

    def __getitem__(self, key):
        return self.packet_list[key]

    def __setitem__(self, key, packet: Packet):
        # raise ValueError("Set item is not supported yet by PacketList type")
        self.is_df_changed = True
        if isinstance(packet, Packet):
            old_packet = self.packet_list[key]
            del self.payload_map_list[old_packet.get_packet_string(gw_data=False, process_packet=False)]
            self.payload_map_list[packet.get_packet_string(gw_data=False, process_packet=False)] = key
            self.packet_list[key] = packet
        else:
            raise TypeError("Can only set Packet type to PacketList")

    def pop(self, index=0):
        """

        :param index: index to pop out of the list
        :type index: int
        :return: the shorter packet list
        :rtype: PacketList
        """
        packet_list = self.copy()
        raw_packet = np.take(packet_list.packet_list, index).packet_data['raw_packet']
        packet_list.packet_list = np.delete(packet_list.packet_list, index)
        packet_list.payload_map_list.pop(raw_packet, None)
        return packet_list

    def copy(self):
        if self.size() == 0:
            return copy.deepcopy(self)
        else:
            copy_packet_list = self.packet_list_obj_type()
            for p in self.packet_list:
                copy_packet_list.append(p.copy())
            return copy_packet_list

    def size(self):
        """
        Total amount of packets, sprinklers count individually
        """
        packet_list_size = 0
        for packet in self.packet_list:
            packet_list_size += len(packet)
        return packet_list_size

    def append(self, packet: Packet, ignore_sprinkler=False, sort_by_time=False):
        """
        Adds single Packet to PacketList

        :type packet: Packet
        :param packet: packet to be added to packet_list
        :type ignore_sprinkler: Bool
        :param ignore_sprinkler: allow duplicates packets from different sprinkler
        :type sort_by_time: bool
        :param sort_by_time: if true append to sprinkler based on the time from start

        :return: packet_list
        """
        if packet.is_valid_packet:
            self.is_df_changed = True
            payload = packet.get_payload()
            if payload not in self.payload_map_list.keys():
                self.packet_list = np.append(self.packet_list, packet)
                payload_list_index = self.packet_list.size - 1
                self.payload_map_list[payload] = payload_list_index
                self.unique_group_ids.add(packet.get_group_id())
            else:
                payload_list_index = self.payload_map_list[payload]
                self.packet_list[payload_list_index].append_to_sprinkler(packet=packet, do_sort=sort_by_time)

    def get_sprinkler(self, packet):
        """
        @param packet: a packet data type. Needs to be appended before using this function.
        @return: A packet sprinkler of this packet.
        """
        payload = packet.get_payload()
        if payload in self.payload_map_list.keys():
            payload_list_index = self.payload_map_list[payload]
            return self.packet_list[payload_list_index]
        else:
            return None

    def dump(self, packet_dict_list: list):
        """
        gets list of raw_packet or packet_dict and fill packet_list with data

        :type packet_dict_list: list
        :param packet_dict_list: gw list (get_packets), fill packet_list with data

        :return: bool status
        """
        if len(self) > 0:
            # packet_list not empty
            return False
        self.is_df_changed = True
        for packet_dict in packet_dict_list:
            packet = self.packet_obj_type(packet_dict,
                                          logger_name=self.logger.name if self.logger is not None else None)
            if packet.is_valid_packet:
                self.append(packet)
        return True

    def update_packet_df(self, packet_df):
        self.packet_df = packet_df
        self.is_df_changed = False

    def get_df(self, sprinkler_filter=False, add_sprinkler_info=True, is_overwrite=False, as_dict=False,
               first_packet_id=0):
        """
        returns packet_list data as dataframe, BE CAREFUL WHEN CHANGING FUNCTIONALITY, this is a fundamental function

        :type sprinkler_filter: Bool
        :param sprinkler_filter: determine if to keep all occurrences of sprinkler per packet
        :type add_sprinkler_info: Bool
        :param add_sprinkler_info: adds 'num_packets_per_sprinkler','per','tbp' attributes to df
        :param is_overwrite: if True, get df overwrite columns with the same name
        :type is_overwrite: bool
        :param as_dict: if True, returns a dictionary instead of dataframe
        :type as_dict: bool
        :param first_packet_id: if specified, the df include packets only from this packet id and larger
        :type first_packet_id: int
        :return: Dataframe
        """
        if not self.is_df_changed:
            sprinkler_info_calculated = 'packet_id' in self.packet_df.keys()
            if sprinkler_filter and sprinkler_info_calculated:
                return self.packet_df.drop_duplicates(subset='packet_id')
            elif (sprinkler_info_calculated and not is_overwrite) or not add_sprinkler_info:
                return self.packet_df

        all_packets_dict = []
        for packet_id, packet in enumerate(self.packet_list):
            if packet_id < first_packet_id:
                continue
            sprinkler_dict = packet.as_dict()
            # add sprinkler info:
            if sprinkler_filter is True or add_sprinkler_info is True:
                tbp = packet.get_tbp()
                if tbp is None:
                    tbp = -1
                per = packet.get_per()

                sprinkler_keys = ['packet_id', 'sprinkler_counter', 'num_packets_per_sprinkler', 'tbp', 'per']
                sprinkler_values = [[packet_id] * len(packet), list(range(1, len(packet) + 1)),
                                    [packet.get_valid_len()] * len(packet), [tbp] * len(packet), [per] * len(packet)]
                for k, v in zip(sprinkler_keys, sprinkler_values):
                    if k in sprinkler_dict.keys() and not is_overwrite:
                        continue
                    sprinkler_dict[k] = v
            # append packet dict:
            if isinstance(sprinkler_dict['raw_packet'], list) and len(sprinkler_dict['raw_packet']) > 1:
                for ind in range(len(sprinkler_dict['raw_packet'])):
                    all_packets_dict.append({k: v[ind] for k, v in sprinkler_dict.items()})
            else:
                for k, v in sprinkler_dict.items():
                    if isinstance(v, list):
                        sprinkler_dict[k] = v[0]
                    elif isinstance(v, np.ndarray):
                        sprinkler_dict[k] = v.item()
                all_packets_dict.append(sprinkler_dict)

        if as_dict:
            return all_packets_dict

        self.packet_df = pd.DataFrame(all_packets_dict)
        self.is_df_changed = False

        if sprinkler_filter:
            if len(self.packet_df['packet_id'].unique()) == 1:
                return self.packet_df.head(1)
            return self.packet_df.drop_duplicates(subset='packet_id')
        else:
            return self.packet_df

    def packet_df_to_sprinkler_df(self, packet_df):
        """
        gets packet_df and returns sprinkler df
        :type packet_df: DataFrame
        :param packet_df: df to convert
        :return: Dataframe - sprinkler_df
        """
        packet_list = self.import_packet_df(packet_df=packet_df)
        sprinkler_df = packet_list.get_df(sprinkler_filter=True, add_sprinkler_info=True)

        return sprinkler_df

    def sort_df_by(self, column='gw_clock'):
        """
        returns dataframe sorted by column
        :type column: str
        :param column: the column to filter by

        :return: Dataframe
        """
        packet_df = self.get_df()
        packet_df_sorted = packet_df.sort_values(column)
        return packet_df_sorted

    def filter_packet_by(self, packet_data_key='adv_address', values='', filter_out=False):
        """
        filter packet_list by adv_address or any other data key
        :type packet_data_key: str
        :param packet_data_key:
        :type values: str or list of strings
        :param values: e.g. adv_address to search
        :type filter_out: bool
        :param filter_out: if True return all packets that does NOT have packet_data_key values

        :return: filtered PacketList
        """
        packet_list = self.packet_list_obj_type(list_custom_data=self.list_custom_data)
        for index, packet in enumerate(self.packet_list):
            filter_data = packet.extract_packet_data_by_name(packet_data_key)
            if filter_data is None:
                p_valid = 'valid' if packet.is_valid_packet else 'invalid'
                self.printing_and_logging(f'PacketList->filter_packet_by: packet_data_key does not exist '
                                          f'for {p_valid} packet:{packet.get_packet_string()}')
                continue

            if not isinstance(values, list):
                values = [values]

            if len(filter_data) > 1:  # filter by sprinklers
                filtered_sprinkler_id = [i for i, f_d in enumerate(filter_data) if (not filter_out and f_d in values) or
                                         (filter_out and f_d not in values)]
                if len(filtered_sprinkler_id):
                    packet_list.append(self.packet_list[index].filter_by_sprinkler_id(filtered_sprinkler_id))
            else:  # filter by packet
                if (not filter_out and filter_data[0] in values) or (filter_out and filter_data[0] not in values):
                    packet_list.append(self.packet_list[index])

        return packet_list

    def filter_df_by(self, packet_df=None, column='adv_address', values='', values_range=[]):
        """
        filter dataframe by value or (exclusive) by value range
        :type packet_df: DataFrame
        :param packet_df: gets get_df dataframe (packet_df only)
        :type column: str
        :param column: column to filter by
        :type values: str or int or list of strings
        :param values: value to search
        :type values_range: 2 elements list of int
        :param values_range: range to find

        :return: filtered Dataframe
        """
        if packet_df is None:
            packet_df = self.get_df()
        if values_range:
            start = values_range[0]
            end = values_range[1]
            packet_df_filtered = packet_df.loc[(packet_df[column] > start) & (packet_df[column] <= end)]
        else:
            if isinstance(values, list):
                packet_df_filtered = packet_df.loc[packet_df[column].isin(values)]
            else:
                packet_df_filtered = packet_df.loc[packet_df[column] == values]
        return packet_df_filtered

    def get_avg_rssi(self):
        """
        return packet list average rssi (4 decimal points accuracy)
        :return: average rssi for tag
        """
        all_rssi = np.array([])
        for packet in self.packet_list:
            if 'rssi' not in packet.gw_data.keys():
                continue
            for i in range(len(packet)):
                all_rssi = np.append(all_rssi, np.take(packet.gw_data['rssi'], i))

        if len(all_rssi) == 0:
            return float('nan')
        avg_rssi = round(all_rssi.mean(), 4)
        return avg_rssi

    def get_avg_tbp(self, ignore_outliers=False):
        """
        return packet list average tbp (4 decimal points accuracy)
        :param ignore_outliers: reject data outside the 2 std area
        :type ignore_outliers: bool

        :return: average tbp for tag
        """

        def reject_outliers(data, m=2):
            return data[abs(data - np.mean(data)) < m * np.std(data)]

        tbp_list = np.array([])
        for packet in self.packet_list:
            packet_tbp = packet.get_tbp()
            if packet_tbp is not None:
                tbp_list = np.append(tbp_list, packet_tbp)
        if len(tbp_list) == 0:
            return None
        avg_tbp = round(tbp_list.mean(), 4)
        if ignore_outliers:
            avg_tbp = round(reject_outliers(tbp_list).mean(), 4)
        return avg_tbp

    def to_csv(self, path, append=False, export_packet_id=True, columns=None, add_sprinkler_info=True,
               is_overwrite=False):
        """
        export entire PacketList to csv

        :type path: str
        :param path: path to save csv
        :type append: bool
        :param append: to append the df to an existing csv file

        :return: bool - export status
        """

        return self.export_packet_df(packet_df=self.get_df(add_sprinkler_info=add_sprinkler_info,
                                                           is_overwrite=is_overwrite),
                                     path=path,
                                     append=append,
                                     export_packet_id=export_packet_id, columns=columns)

    def export_packet_df(self, packet_df, path, append=False, export_packet_id=True, columns=None):
        """
        export given dataframe to csv

        :type packet_df: Dataframe
        :param packet_df: filtered dataframe to save as csv
        :type path: str
        :param path: path to save csv
        :type append: bool
        :param append: to append the df to an existing csv file

        :return: bool - export status
        """
        try:
            # this call of 'to_csv' is a generic pandas function
            if not export_packet_id and 'packet_id' in packet_df:
                packet_df.drop('packet_id', axis=1, inplace=True)

            if append:
                packet_df.to_csv(path, mode='a', index=False, header=False, columns=columns)
            else:
                packet_df.to_csv(path, index=False, columns=columns)
            return True
        except KeyError as e:

            raise KeyError(f'problem during export packet df {e}')

    def packet_string_to_object(self, packet_in, time_from_start, configs=None, custom_data=None, inlay_type=None,
                                ignore_crc=False):
        packet_obj = Packet(packet_in, float(time_from_start), custom_data=custom_data, inlay_type=inlay_type,
                            logger_name=self.logger.name if self.logger is not None else None,
                            ignore_crc=ignore_crc)
        return packet_obj

    def import_packet_df(self, path=None, packet_df=None, custom_data_attr=None, import_all=False,
                         list_custom_data=None, verbose=True, inlay_type=None, ignore_crc=True,
                         obj_out=None):
        """
        import from a csv of dataframe
        :type path: str
        :param path: the message or part of the message that needed to be read
        :type packet_df: DataFrame
        :param packet_df: gets get_df dataframe (packet_df only)
        :type custom_data_attr: list
        :param custom_data_attr: if specified, only the specified additional columns in the attached df/csv will be
                                added to the packets as custom_data
        :type import_all: bool
        :param import_all: if True, all other columns in the attached df/csv will be added to the packets as custom_data
        :type list_custom_data: dict
        :param list_custom_data: the packet_list custom data as dictionary
        :type verbose: bool
        :param verbose: if False, remove some of the printing while converting each packet to packet object
        :type inlay_type: InlayTypes
        :param inlay_type: the packet_list inlay type
        :type ignore_crc: bool
        :param ignore_crc: if True, update for all packets crc_valid = True,
                           relevant for data collected by old GW FW version
        :type obj_out: PacketList or DecryptedPacketList or TagCollection or DecryptedTagCollection
        :param obj_out: if specified the return object from the function will be as the obj_out,
                        otherwise would be same as self object type
        :return: obj_out
        """
        class UnsupportedFileFormat(Exception):
            def __init__(self):
                supported_content_str = 'dataframe/file must contains one of the following columns conventions:\n' \
                    '1. raw_packet AND gw_packet\n2. encryptedPacket\n3. decrypted_full_packet\n4. encrypted_packet\n' \
                        '5. rawPacket AND packetVersion (tables from databricks based on cloud conversion that rawPacket is the packet payload\n'
                super().__init__(f'{supported_content_str}')
        non_packets_rows = []
        list_custom_data = list_custom_data if list_custom_data is not None else self.list_custom_data
        if obj_out is None:
            obj_out = self.packet_list_obj_type(list_custom_data=list_custom_data)
        if path is not None:
            if str(path).endswith('.csv'):
                import_packets_df = pd.read_csv(path)
            elif str(path).endswith('.log'):
                import_packets_df = pd.DataFrame()  #TODO need to implement
            elif str(path).endswith('.json'):
                import_packets_df = pd.read_json(path)
                import_packets_df = dewhitening_packets(import_packets_df)
        else:
            import_packets_df = packet_df

        first_timestamp = None
        static_keys_list = self.get_generic_df_cols() if import_all else None
        for index, row in import_packets_df.iterrows():
            try:
                reconstructed_packet = None
                if 'raw_packet' in row.keys():
                    raw_packet = row['raw_packet']
                    gw_data = row['gw_packet'] if ('gw_packet' in row.keys() and row['gw_packet']) else ''
                    if not pd.isnull(raw_packet) and not pd.isnull(gw_data):
                        reconstructed_packet = str(raw_packet) + str(gw_data)
                elif 'encryptedPacket' in row.keys():
                    reconstructed_packet = row['encryptedPacket']
                elif 'decrypted_full_packet' in row.keys():
                    reconstructed_packet = row['decrypted_full_packet']
                elif 'encrypted_packet' in row.keys():
                    reconstructed_packet = row['encrypted_packet']
                elif 'rawPacket' in row.keys() and ('packetVersion' in row.keys() or 'flowVersion' in row.keys()):
                    if first_timestamp is None:
                        if 'timestamp' in import_packets_df.keys():
                            first_timestamp = import_packets_df['timestamp'].min()
                        else:
                            first_timestamp = 0
                    c = ConvertCloudPacket(enriched_packet_row=row, first_timestamp=first_timestamp)
                    reconstructed_packet = c.get_reconstruct_packet()
                else:
                    raise UnsupportedFileFormat()
                if reconstructed_packet == '' or pd.isnull(reconstructed_packet):
                    non_packets_rows.append(index)
                    continue
            except UnsupportedFileFormat:
                raise
            except Exception as e:
                non_packets_rows.append(index)
                continue

            if 'time_from_start' in row.keys():
                time_from_start = row['time_from_start']
            elif 'time' in row.keys() and (not isinstance(row['time'], str) or
                                           row['time'].replace('.', '').isnumeric()):
                time_from_start = row['time']
            elif 'timestamp' in row.keys() and (
                    not isinstance(row['timestamp'], str) or row['timestamp'].replace('.', '').isnumeric()):
                time_from_start = float(row['timestamp']) - (first_timestamp if first_timestamp is not None else 0)
                time_from_start = float(time_from_start / 1000)  # timestamp is usually in ms
            else:
                time_from_start = float('nan')

            try:
                time_from_start = float(time_from_start)
            except ValueError:
                time_from_start = float('nan')

            # adding custom data
            custom_data = {}
            try:
                if import_all:
                    for k in row.keys():
                        if k not in static_keys_list:
                            custom_data[k] = row[k]
                elif custom_data_attr is not None:
                    for k in custom_data_attr:
                        if k in row.keys():
                            custom_data[k] = row[k]
            except Exception as e:
                    self.printing_and_logging(f'exception raised during extracting custom data in import df: {e}')
            try:
                p = self.packet_string_to_object(packet_in=reconstructed_packet,
                                                 time_from_start=time_from_start,
                                                 configs=row,
                                                 custom_data=custom_data,
                                                 inlay_type=inlay_type,
                                                 ignore_crc=ignore_crc)
                obj_out.append(p)
            except Exception as e:
                self.printing_and_logging('exception raised during import df: {}'.format(e))

        if len(non_packets_rows) and verbose:
            self.printing_and_logging('the following {} rows could not be imported '
                                      'to the packet list:{}'.format(len(non_packets_rows), non_packets_rows))
        return obj_out

    def get_statistics(self, packet_df=None):
        """
        Calculates statistics of self.
        @return dictionary with predefined statistics of the packetList.
        """
        return self.get_df_statistics(packet_df=packet_df)

    def get_group_statistics(self, group_by_col='adv_address'):
        """
        Calculates statistics of self, grouped by some value.
        @return dictionary of items at the group, Dictionary values are dictionaries of statistics.
        """
        packet_df = self.get_df()
        # if not defines - get all values:

        groups_id_list = packet_df[group_by_col].unique()

        group_statistics = {}
        for group_id in groups_id_list:
            packet_df_filtered = packet_df.loc[packet_df[group_by_col] == group_id]
            group_statistics[group_id] = self.get_df_statistics(packet_df=packet_df_filtered)
            group_statistics[group_id][group_by_col] = group_id
        return group_statistics

    def group_by(self, group_by_col='adv_address'):
        """
        Calculates statistics of self, grouped by some value.
        @return dictionary of items at the group, Dictionary values are dictionaries of statistics.
        """
        packet_df = self.get_df(sprinkler_filter=True)
        # if not defines - get all values:

        groups_id_list = packet_df[group_by_col].unique()

        group = {}
        for group_id in groups_id_list:
            group[group_id] = self.filter_packet_by(group_by_col, group_id)
            # group[group_id][group_by_col] = group_id
        return group

    def get_num_packets(self):
        """
        Total amount of packets, sprinklers packets count separately
        """
        return len(self.packet_list)

    def get_df_statistics(self, packet_df=None, stat_calc=StatisticsCalc):
        """
        Calculates statistics from packetList DF.
        @param packet_df - dataframe generated by packetList
        @param stat_calc - object to calc the statistics
        @return dictionary with predefined statistics of the packetList.
        """
        statistics = {}
        if (packet_df is not None and packet_df.shape[0] == 0) or (packet_df is None and self.size() == 0):
            statistics = {'num_packets': 0, 'num_cycles': 0}
            return statistics

        # sprinkler_df = self.get_df(sprinkler_filter=True)
        if packet_df is None:
            packet_df = self.get_df(add_sprinkler_info=True)
        if 'sprinkler_counter' in packet_df.keys():
            sprinkler_df = packet_df[packet_df['sprinkler_counter'] == 1]
        else:
            sprinkler_df = self.packet_df_to_sprinkler_df(packet_df)

        s = stat_calc(packet_df, sprinkler_df)
        stat_attr = (getattr(s, name) for name in dir(s) if not name.startswith('_'))
        stat_methods = [a for a in stat_attr if inspect.ismethod(a)]
        statistics = {}
        for method in stat_methods:
            calc_stat = method()
            statistics = {**statistics, **calc_stat}

        return statistics

    def to_tag_list(self):
        # import here to avoid infinite loop (packet_list calls tag_list and tags_list calls packet_list)
        from wiliot_core.packet_data.tag_collection import TagCollection
        tag_list = TagCollection()
        for packet in self.packet_list:
            tag_list.append(packet)
        return tag_list

    def sync_packet_list(self, new_packet_list, time_sync_new, my_source_name='original', new_source_name='new',
                         do_sort=False):
        """
        This function merge one packet list to the self packet list. if time_sync_list is specified it sync the data based on
        the time sync list
        """
        if pd.isnull(time_sync_new):
            raise ValueError(f'cannot sync packet list due to time sync new id null: {time_sync_new}')

        for p in self.packet_list:
            p.add_custom_data({'source': my_source_name})

        for p in new_packet_list:
            p.gw_data['time_from_start'] = np.array(p.gw_data['time_from_start'] - time_sync_new)
            p.add_custom_data({'source': new_source_name, 'timestamp': float('nan')})
            self.append(p, sort_by_time=do_sort)

        if do_sort:
            min_time_from_start = []
            for p in self.packet_list:
                min_time_from_start.append(np.min(p.gw_data['time_from_start']))

            min_time_from_start = np.array(min_time_from_start)
            idx = min_time_from_start.argsort()
            self.packet_list = self.packet_list[idx]

    def get_generic_df_cols(self):
        packet_data = list(extract_packet_data_types().keys())
        gw_data = list(extract_gw_data_types().keys())
        return packet_data + gw_data
    
    def log_file_to_packet_struct(self, log_path, ignore_crc=False, packet_obj=None, packet_list_obj=None):
        packet_obj = packet_obj if packet_obj is not None else Packet
        packet_list_obj = packet_list_obj if packet_list_obj is not None else PacketList
        try:
            packet_list_out = packet_list_obj()
            user_event_out = []
            if os.path.isfile(log_path):
                f = open(log_path, 'r')
                lines = f.readlines()

                for i, line in enumerate(lines):
                    try:
                        if 'packet' in line:
                            # a data line
                            line_to_compare = line.replace(' ', '').replace("'", '')
                            if "raw:process_packet" in line_to_compare:
                                re_match = re.search(r"process_packet\(\"(\w+)\"", line)
                                packet_raw = str(re_match.groups(1)[0])
                            elif "packet:" in line_to_compare:  # packet: ABCD format (data type = processed
                                re_match = re.search(r",packet:(\w+)", line)
                                packet_raw = str(re_match.groups(1)[0])
                            elif "raw:full_packet" in line_to_compare:  # packet: ABCD format (data type = processed
                                re_match = re.search(r"full_packet\(\"(\w+)\"", line)
                                packet_raw = str(re_match.groups(1)[0])
                            else:
                                continue  # line without packets
                            if "'time': " in line:
                                re_match = re.search(r"'time': (\d+.\d+)", line)
                                packet_time = float(re_match.groups(1)[0])
                            else:
                                re_match = re.search(r"time:(\d+.\d+)", line)
                                packet_time = float(re_match.groups(1)[0])
                            
                            # timestamp calc:
                            try:
                                timestamp_str = line.split(' ')[0]
                                timestamp_list = timestamp_str.split(',')
                                dt_time = datetime.datetime.strptime(timestamp_list[0],"%H:%M:%S")
                                timestamp_sec = (dt_time.hour * 60 * 60) + (dt_time.minute * 60) + (dt_time.second)
                                timestamp_sec += (int(timestamp_list[1]) if len(timestamp_list) > 1 else 0) / 1000
                                custom_data = {'timestamp': timestamp_sec}
                            except Exception as e:
                                print(f'failed to parse timestamp from line: {line}, error: {e}')
                                custom_data = None

                            packet_list_out.append(packet_obj(raw_packet=packet_raw, time_from_start=packet_time,
                                                              ignore_crc=ignore_crc, custom_data=custom_data))
                        if 'user_event' in line:
                            user_event_time = float('nan')
                            user_event_data = ''
                            if "user_event_time" in line:
                                re_match = re.search(r"user_event_time: (\d+.\d+),", line)
                                user_event_time = float(re_match.groups(1)[0])
                            if 'User event' in line:
                                user_event_data = line.split('User event: ')[-1].replace('\n', '')
                            user_event_out.append(
                                {'user_event_time': user_event_time, 'user_event_data': user_event_data})

                        if i % 1000 == 0:
                            print(f'analyzing row number {i}')
                    except Exception as e:
                        print(f'line {line} was failed to upload due to: {e}')
                f.close()
            if len(user_event_out) > 0:
                user_event_df = pd.DataFrame(user_event_out)
                user_event_df.to_csv(log_path.replace('.log', '_user_event.csv'), index=False)
            return packet_list_out
        except Exception as e:
            raise Exception(f'export packets from log was failed due to: {e}')
        
    def enrich(self, parsed_data: list) -> None:
        """
        Enriches the PacketList with parsed data from the manufacturing API.
        Call with res['results'] from the manufacturing API response.
        """
        for p in parsed_data:
            if p['status'] == 'Success':
                p_ind = self.payload_map_list[p['payload']]
                for k, v in p['parsedData'].items():
                    self[p_ind].decoded_data[k] = v


if __name__ == '__main__':
    df_path = r"C:\Users\shunit\Downloads\packets.json"
    new_list = PacketList()
    new_list = new_list.import_packet_df(path=df_path, import_all=True)
    
    
    import os
    p = PacketList()
    generic_df_cols = p.get_generic_df_cols()
    print(generic_df_cols)
    try:
        df_path = r"MY_DATA_FILE.csv"

        new_list = PacketList()
        new_list.append(Packet(
            'process_packet("04A3E93988271E16AFFD0200004E9D46293BEED581709F1214C88F6F3978E2136EB48E413533807C")'))
        new_list.get_df()

        new_list = new_list.import_packet_df(path=df_path, import_all=True)
        print(f'avg rssi: {new_list.get_avg_rssi()}')
        f_out = new_list.filter_packet_by(packet_data_key='rssi', values=[40, 60])
        new_list_df = new_list.get_df(sprinkler_filter=True, add_sprinkler_info=True, is_overwrite=True)
        new_list.to_csv(df_path.replace('.csv', '_decrypted.csv'))
        new_list_short = PacketList()
        new_list_short = new_list_short.import_packet_df(path=df_path, custom_data_attr=['common_run_name',
                                                                                         'external_id'])
        new_list_short_df = new_list_short.get_df(add_sprinkler_info=True)

    except Exception as e:
        print(e)

    print('done')
