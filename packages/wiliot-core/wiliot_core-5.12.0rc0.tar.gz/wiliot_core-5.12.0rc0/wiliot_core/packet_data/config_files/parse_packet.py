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

from wiliot_core.packet_data.config_files.data_mapping.packet_data_info import *
from wiliot_core.packet_data.config_files.data_mapping.gw_data_info import *


def extract_packet_data_types():
    return {key: value['type'] for key, value in packet_data_info.items()}


def extract_gw_data_types():
    return {key: value['type'] for key, value in gw_data_info.items()}

def check_packet_includes_side_info(packet_data_input):
    """
    Check if the packet data input includes side info.
    :param packet_data_input: The packet data input as a string.
    :return: True if side info is included, False otherwise.
    """
    if len(packet_data_input) < 2:
        return False, None
    if not packet_data_input.startswith('47'):
        return False, None
    estimated_bytes_hex = packet_data_input[2:4] 
    estimated_bytes = int(estimated_bytes_hex, 16)
    if estimated_bytes == len(packet_data_input[4:]) / 2:
        # a valid packet with side info
        n_side_info_bytes = int(estimated_bytes_hex,16) - int('31', 16)
        tag_packet = packet_data_input[:-(2*n_side_info_bytes)]
        side_info_packet = packet_data_input[-(2*n_side_info_bytes):]
        return True, {'tag_packet': tag_packet, 'side_info_packet': side_info_packet}
    gw_len_chars = find_len(gw_data_info, 'stat_param') + find_len(gw_data_info, 'rssi')
    if estimated_bytes == len(packet_data_input[4:-gw_len_chars]) / 2:
        # a valid packet with side info and GW data
        n_side_info_bytes = int(estimated_bytes_hex,16) - int('31', 16)
        tag_packet = packet_data_input[:-(2*n_side_info_bytes) - gw_len_chars] + packet_data_input[-gw_len_chars:]
        side_info_packet = packet_data_input[-(2*n_side_info_bytes)-gw_len_chars:-gw_len_chars]
        return True, {'tag_packet': tag_packet, 'side_info_packet': side_info_packet}

    return False, None

def check_packet_length_with_no_indication(packet_data_input):
    # check if packet with side info:
    is_packet_with_side_info, packet_dict = check_packet_includes_side_info(packet_data_input)
    if is_packet_with_side_info:
        packet_dict['expected_length'] = packet_length_types['4731']
        return packet_dict

    packet_dict = {'tag_packet': packet_data_input, 'expected_length': None, 'side_info_packet': ''}
    
    received_len = len(packet_data_input)
    for packet_prefix, length_dict in packet_length_types.items():
        if received_len == length_dict['packet_tag_length']:
            packet_data_input += '0' * (
                    find_len(gw_data_info, 'stat_param') + find_len(gw_data_info, 'rssi'))
            packet_dict['expected_length'] = length_dict

        elif received_len == length_dict['packet_tag_length'] + (
                find_len(gw_data_info, 'stat_param') + find_len(gw_data_info, 'rssi')):
            packet_dict['expected_length'] = length_dict

        elif length_dict['name'] == 'LEGACY':
            if received_len == length_dict['packet_tag_length'] - find_len(packet_data_info, 'header'):
                packet_data_input = packet_prefix + packet_data_input + '0' * (
                        find_len(gw_data_info, 'stat_param') + find_len(gw_data_info,
                                                                                                    'rssi'))
                packet_dict['expected_length'] = length_dict
            elif received_len == \
                    length_dict['packet_tag_length'] - find_len(packet_data_info, 'header') + (
                    find_len(gw_data_info, 'stat_param') + find_len(gw_data_info, 'rssi')):
                packet_data_input = packet_prefix + packet_data_input
                packet_dict['expected_length'] = length_dict

        if packet_dict['expected_length'] is not None:
            break
    
    packet_dict['tag_packet'] = packet_data_input
    return packet_dict


def fix_packet_length(packet_data_input, is_full_packet):

    packet_dict = {'expected_length': None, 'tag_packet': packet_data_input, 'side_info_packet': ''}

    for full_key in packet_length_types.keys():
        if packet_data_input.startswith(full_key):
            is_full_packet = True
            break
    
    if is_full_packet is None:
        packet_dict = check_packet_length_with_no_indication(packet_data_input)

        if packet_dict['expected_length'] is None:
            raise ValueError(f'invalid packet length for packet {packet_data_input}, '
                            f'these are the valid tag packet length: {packet_length_types}')
    elif is_full_packet:
        packet_dict['expected_length'] = packet_length_types[packet_data_input[:find_len(packet_data_info, 'header')]]
    else:
        packet_data_input = '4225' + packet_data_input
        packet_dict['tag_packet'] = packet_data_input
        packet_dict['expected_length'] = packet_length_types[packet_data_input[:find_len(packet_data_info, 'header')]]
    
    # check if packet length is valid
    received_len = len(packet_dict['tag_packet'])

    if received_len == packet_dict['expected_length']['packet_tag_length'] + GW_PACKET_LEN:
        pass
    elif received_len == packet_dict['expected_length']['packet_tag_length']:
        packet_data_input += '0' * GW_PACKET_LEN
    else:
        raise ValueError(f'invalid packet length for packet {packet_data_input}, '
                        f'expected tag packet length: {packet_dict["expected_length"]["packet_tag_length"]}')
    
    return packet_dict


def parser(data_dict, packet_dict, array_data=False):
    result = {'packet_data': packet_dict['tag_packet']}
    packet_type = packet_dict['expected_length']['name']
    for key, info in data_dict.items():
        if key in result.keys():
            continue
            
        input_data = result.get(info['input'])
        start, length = info['index_info'].get(packet_type, (0, 0)) if packet_type in info['index_info'] else info['index_info'].get('all', (0, 0))
        func = info.get('function')
        args_names = info.get('args', [])
        data_type = info.get('type')
        data_out = None
        if input_data is not None:
            data_out = input_data[start:start + length]

        if callable(func):
            args_g = {arg_name: packet_dict[arg_name] for arg_name in args_names if arg_name in packet_dict}
            args_r = {arg_name: result[arg_name] for arg_name in args_names if arg_name in result}
            result[key] = func(data_out, args={**args_g, **args_r})
        else:
            result[key] = data_out
        
        if type(result[key]) != data_type:
            raise TypeError(f'key: {key} has wrong type {type(result[key])} (should be {data_type})')
    
    del result['packet_data']
    if array_data:
        for k, v in result.items():
            result[k] = np.array([v])
    return result


def parse_packet(packet_data, time_from_start, is_full_packet, ignore_crc):
    # update packet string and check its type
    packet_dict = fix_packet_length(packet_data, is_full_packet)  # This should be the only function here
    # arrange packet_params
    packet_dict['time_from_start'] = time_from_start
    packet_dict['ignore_crc'] = ignore_crc

    packet_result = parser(packet_data_info, packet_dict)
    gw_result = parser(gw_data_info, packet_dict, array_data=True)

    return gw_result, packet_result

def construct_packet_from_fields(packet_data, fields_to_zero=None, fields_to_convert=None, gw_data='', prefix=False,
                                 gw_fields_to_convert=None):
    """
    fields_to_zero : a list of fields names, need to be zero
    fields_to_convert : dict of field name as key and its value based on packet_structure variable
    gw_fields_to_convert : if gw_data is not specified,
                           dict of field name as key and its value based on gw_bit_structure variable
    """
    new_packet = []
    if packet_data.get('ble_type') in [x['name'] for x in packet_length_types.values()]:
        is_legacy_packet = packet_data['ble_type'] == 'LEGACY'
    else:
        is_legacy_packet = packet_length_types.get(packet_data['header'], {'name': 'LEGACY'})['name'] == 'LEGACY'
    
    for field in packet_structure:
        if is_legacy_packet and field in BLE5_ONLY_FIELDS:
            continue  # do not add ble5 fields to legacy packets
        if fields_to_zero and field in fields_to_zero:
            field_len = find_len(packet_data_info, field)
            new_packet.append('0' * field_len)  # BLE5-EXT and BLE5-DBL-EXT have the same length
        elif fields_to_convert and field in fields_to_convert:
            new_packet.append(fields_to_convert[field].upper())
        else:
            new_packet.append(packet_data.get(field, ''))

    # added the tag packet
    construct_packet = ''.join(new_packet)

    # add the bridge side info if exists
    bridge_side_info = packet_data.get('bridge_side_info', '')
    construct_packet += bridge_side_info

    # add the gw data if exists
    if gw_data == '' and gw_fields_to_convert is not None:
        gw_bit_data = ''
        if 'crc_valid' not in gw_fields_to_convert.keys():
            gw_fields_to_convert['crc_valid'] = 1
        for field, field_bit_len in gw_bit_structure.items():
            if field in gw_fields_to_convert.keys():
                bin_field = bin(int(gw_fields_to_convert[field]))[2:]
            else:
                bin_field = '0'
            bin_field = bin_field.zfill(field_bit_len)
            bin_field = bin_field[-field_bit_len:]
            gw_bit_data += str(bin_field)
        gw_data = hex(int(gw_bit_data, 2))[2:].upper()

    construct_packet += gw_data

    if prefix:
        construct_packet = f'process_packet("{construct_packet}")' if is_legacy_packet \
            else f'full_packet("{construct_packet}")'
    return construct_packet
