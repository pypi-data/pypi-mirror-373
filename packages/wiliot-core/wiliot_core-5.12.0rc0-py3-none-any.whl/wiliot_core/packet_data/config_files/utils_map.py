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

from enum import Enum
import numpy as np


N_BITS_PER_CHAR = 4
FLOW_VER_SIZE = 4
EN_TYPE_LEN = 4
GW_PACKET_LEN = 6
PAYLOAD_LENGTH = 16
BLE_PAYLOAD_LENGTH = 62
BLE_DOUBLE_PAYLOAD_LENGTH = 78
TAG_EXTENDED_PAYLOAD_BYTES = '0x26'

WILIOT_EN_TYPE = ['1E16', '2616']
WILIOT_DATA_UID = ['C6FC', 'AFFD']

packet_length_types = {
    '4225': {'name': 'LEGACY', 'packet_tag_length': 78},
    '4729': {'name': 'BLE5-EXT', 'packet_tag_length': 86},
    '4731': {'name': 'BLE5-DBL-EXT', 'packet_tag_length': 102},
    '4707': {'name': 'BLE5-POINTER', 'packet_tag_length': 18},
}


def find_len(data_type, att):
    index_info = data_type[att]['index_info']
    first_key = list(index_info.keys())[0]
    return index_info[first_key][1]


def get_nonce_minus_one(nonce_raw):
    int_nonce_minus_one = np.array(int.from_bytes(bytes.fromhex(nonce_raw), byteorder='little') - 1).astype(np.uint32).item()
    return reverse_data(f'{int_nonce_minus_one:08X}')


def reverse_data(data):
    data_reversed = ''
    for i in range(len(data), 0, -2):
        data_reversed += data[i - 2:i]
    return data_reversed


def hex2bin(hex_value, min_digits=0, zfill=True):
    binary_value = format(int(hex_value, 16), 'b')

    if zfill:
        binary_value = binary_value.zfill(24)

    binary_value = binary_value.zfill(min_digits)

    return binary_value


def bin2hex(binary_value, min_digits=0):
    hex_val = f'{int(binary_value, 2):X}'
    hex_val = hex_val.zfill(min_digits)
    return hex_val


def is_cloud_packet(packet_in):
    if any(packet_in.startswith(x) for x in WILIOT_DATA_UID):
        return True
    if any(packet_in.startswith(x) for x in WILIOT_EN_TYPE):
        return True
    if any(packet_in[4:].startswith(x) for x in WILIOT_DATA_UID):
        return True
    return False
