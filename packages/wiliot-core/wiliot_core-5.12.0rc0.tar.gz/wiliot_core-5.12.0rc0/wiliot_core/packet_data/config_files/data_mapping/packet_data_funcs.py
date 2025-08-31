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

from wiliot_core.packet_data.config_files.utils_map import *


GROUP_ID_MASK = 0xFFFF00
RAW_GROUP_ID_MASK = 0xFFFFC0
PACKET_DECRYPT_MASK = 0xc
BRIDGE_PACKET_MASK = 0x3F
BRG_SERVICE_UUID = 'C6FC'


def check_test_mode(no_data, args):
    flow_version = hex(int(args['flow_ver'], 16))

    if int(flow_version, 16) < 0x42c:
        if 'FFFFFFFF' in args['adv_address']:
            return 1
    elif int(flow_version, 16) < 0x500:
        adv_address = args['adv_address']
        if adv_address.startswith('FFFF') or adv_address.endswith('FFFF'):
            return 1
    else:
        if int(args['data_uid'], 16) == 5:
            return 1
    return 0


def calculate_raw_group_id(group_id_p, args):
    if not group_id_p:
        return ''
    return hex(int(group_id_p, 16) & RAW_GROUP_ID_MASK)[2:].zfill(6).upper()


def calculate_group_id(group_id_p, args):
    if not group_id_p:
        return ''
    return hex(int(group_id_p, 16) & GROUP_ID_MASK)[2:].zfill(6).upper()

def is_packet_from_bridge(data_uid, args=None):
    if not data_uid:
        return False
    return data_uid == BRG_SERVICE_UUID


def calculate_bridge_packet(group_id_p, args):
    if not group_id_p:
        return ''
    return hex(int(group_id_p, 16) & BRIDGE_PACKET_MASK)[2:].zfill(
        len(str(hex(BRIDGE_PACKET_MASK))[2:])).upper()


def calculate_flow_ver(no_data, args):
    if (args['is_packet_from_bridge'] and '**' not in args['adv_address']) or args['adv_address'].startswith('***') or args['adv_address'] == '':
        return hex(0)
    else:
        return hex(int(args['adv_address'][:2] + args['adv_address'][-2:], 16))


def calculate_decrypted_packet_type(decrypted_packet_type, args):
    if not decrypted_packet_type:
        return -1
    return (int(decrypted_packet_type, 16) & PACKET_DECRYPT_MASK) >> 2


def get_first_packet_ind(no_data, args):
    if args['flow_ver'].lower() < '0x60d':
        return False
    unique_adva = args['adv_address'][2:-2]
    if int(args['decrypted_packet_type']) == 0:
        return unique_adva == args['nonce']
    if int(args['decrypted_packet_type']) == 1:
        return unique_adva == get_nonce_minus_one(args['nonce'])
    return False


def get_packet_length(no_data, args):
    return args['expected_length']['packet_tag_length'] + GW_PACKET_LEN


def get_ble_type(no_data, args):
    return args['expected_length']['name']


def get_bridge_side_info(no_data, args):
    if not args.get('is_packet_from_bridge', False):
        return ''
    if args.get('side_info_packet', '') != '' and args['bridge_packet'] != '3B':
        raise ValueError(f"Invalid packet with bridge side info {args['side_info_packet']} BUT with bridge group id different than 3B ({args['bridge_packet']})")
    si_from_mic = args['mic'][:6] if 'DBL' not in args['ble_type'] else ''
    return args.get('side_info_packet', '') or si_from_mic

def get_bridge_si_rssi(no_data, args):
    if not args.get('is_packet_from_bridge', False):
        return 0
    bridge_side_info = args.get('bridge_side_info')
    if not bridge_side_info or len(bridge_side_info) < 4:
        return 0
    rssi_si = int(format(int(bridge_side_info[2:4], 16) & 0xFC, '04b').zfill(8)[:6],2)    # first 6 bits of the 2nd byte
    rssi_si = -(40 + rssi_si)  # convert to dBm

    return rssi_si

def get_bridge_id(no_data, args):
    if not args.get('is_packet_from_bridge', False):
        return ''
    return 'X' + reverse_data(args.get('adv_address').upper())[1:]  # first half byte is overwrite so we cannot deduce the bridge id first char
