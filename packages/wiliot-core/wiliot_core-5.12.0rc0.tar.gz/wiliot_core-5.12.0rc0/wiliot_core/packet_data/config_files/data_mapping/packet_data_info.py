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

from wiliot_core.packet_data.config_files.data_mapping.packet_data_funcs import *


packet_structure = [  # all fields that construct the packet
    'header', 
    'extended_header', 
    'adv_address', 
    'adi', 
    'en', 
    'type', 
    'data_uid', 
    'recieved_group_id',
    'nonce', 
    'enc_uid', 
    'mic', 
    'enc_payload'
    ]

BLE5_ONLY_FIELDS = ['header', 'extended_header', 'adi']  # fiedls that are not part of the LEGACY packet

packet_data_info = {
    'raw_packet': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (0, 86),
            'BLE5-DBL-EXT': (0, 102),
            'BLE5-POINTER': (0, 18),
            'LEGACY': (4, 74),
        },
        'input': 'packet_data',
        'function': None,
    },
    #  ##########  main fields  ##########  #
    'header': {
        'type': str,
        'index_info': {'all': (0, 4)},
        'input': 'packet_data',
        'function': None,
    },
    'extended_header': {
        'type': str,
        'input': 'raw_packet',
        'index_info': {
            'BLE5-EXT': (4, 4),
            'BLE5-DBL-EXT': (4, 4),
            'BLE5-POINTER': (4, 4),
        },
        'function': None,
    },
    'adv_address': {
        'type': str,
        'input':'raw_packet',
        'index_info': {
            'BLE5-EXT': (8, 12),
            'BLE5-DBL-EXT': (8, 12),
            'LEGACY': (0, 12)
        },
        'function': None
    },
    'adi': {
        'type': str,
        'input': 'raw_packet',
        'index_info': {
            'BLE5-EXT': (20, 4),
            'BLE5-DBL-EXT': (20, 4),
            'BLE5-POINTER': (8, 4),
        },
        'function': None
    },
    'en': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (24, 2),
            'BLE5-DBL-EXT': (24, 2),
            'LEGACY': (12, 2)
            },
        'input': 'raw_packet',
        'function': None,
    },
    'type': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (26, 2),
            'BLE5-DBL-EXT': (26, 2),
            'LEGACY': (14, 2)
            },
        'input': 'raw_packet',
        'function': None
    },
    'data_uid': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (28, 4),
            'BLE5-DBL-EXT': (28, 4),
            'LEGACY': (16, 4)
            },
        'input': 'raw_packet',
        'function': None
    },
    'recieved_group_id': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (32, 6),
            'BLE5-DBL-EXT': (32, 6),
            'LEGACY': (20, 6)},
        'input': 'raw_packet',
        'function': None,
    },
    'nonce': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (38, 8),
            'BLE5-DBL-EXT': (38, 8),
            'LEGACY': (26, 8)},
        'input': 'raw_packet',
        'function': None
    },
    'enc_uid': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (46, 12),
            'BLE5-DBL-EXT': (46, 12),
            'LEGACY': (34, 12)},
        'input': 'raw_packet',
        'function': None
    },
    'mic': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (58, 12),
            'BLE5-DBL-EXT': (58, 12),
            'LEGACY': (46, 12)},
        'input': 'raw_packet',
        'function': None
    },
    'enc_payload': {
        'type': str,
        'index_info': {
            'BLE5-EXT': (70, 16),
            'BLE5-DBL-EXT': (70, 32),
            'LEGACY': (58, 16)},
        'input': 'raw_packet',
        'function': None
    },
    #  ##########  calculated fields  ##########  #
    'raw_group_id': {
        'type': str,
        'index_info': {'all': (0, 6)},
        'input': 'recieved_group_id',
        'function': calculate_raw_group_id,
    },
    'group_id': {
        'type': str,
        'index_info': {'all': (0, 6)},
        'input': 'recieved_group_id',
        'function': calculate_group_id
    },
    'decrypted_packet_type': {
        'type': int,
        'index_info': {'all': (4, 1)},
        'input': 'recieved_group_id',
        'function': calculate_decrypted_packet_type
    },
    'bridge_packet': {
        'type': str,
        'index_info': {'all': (0, 6)},
        'input': 'recieved_group_id',
        'function': calculate_bridge_packet
    },
    'ble_type': {
        'type': str,
        'index_info': {},
        'input': None,
        'function': get_ble_type,
        'args': ['expected_length']
    },
    'packet_length': {
        'type': int,
        'index_info': {},
        'input': None,
        'function': get_packet_length,
        'args': ['expected_length']
    },
    'is_packet_from_bridge': {
        'type': bool,
        'index_info': {'all': (0, 4)},
        'input': 'data_uid',
        'function': is_packet_from_bridge
    },
    'flow_ver': {
        'type': str,
        'index_info': {},
        'input': None,
        'function': calculate_flow_ver,
        'args': ['adv_address', 'is_packet_from_bridge']
    },
    'first_packet_ind': {
        'type': bool,
        'index_info': {},
        'input': None,
        'function': get_first_packet_ind,
        'args': ['flow_ver', 'decrypted_packet_type', 'adv_address', 'nonce']
    },
    'test_mode': {
        'type': int,
        'index_info': {},
        'input': None,
        'function': check_test_mode,
        'args': ['adv_address', 'flow_ver', 'data_uid'],
    },
    'bridge_side_info': {
        'type': str,
        'index_info': {},
        'input': None,
        'function': get_bridge_side_info,
        'args': ['is_packet_from_bridge', 'side_info_packet', 'bridge_packet', 'mic', 'ble_type']
    },
    'bridge_si_rssi': {
        'type': int,
        'index_info': {},
        'input': None,
        'function': get_bridge_si_rssi,
        'args': ['is_packet_from_bridge', 'bridge_side_info', 'mic']
    },
    'bridge_id': {
        'type': str,
        'index_info': {},
        'input': None,
        'function': get_bridge_id,
        'args': ['is_packet_from_bridge', 'adv_address']
    },
}