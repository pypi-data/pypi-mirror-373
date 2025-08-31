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


# here is a list of parameters which are change based on the packet flow version.
# the flow min and flow mac MUST be ordered

packet_flow_parameters = {
    'sprinkler_num': [
        {'flow_min': None,    'flow_max': '0x602', 'value': 6},
        {'flow_min': '0x603', 'flow_max': '0x7ff', 'value': 2},
        {'flow_min': '0x800', 'flow_max': '0x807', 'value': {0: 4, 1: float('nan'), 2: 2, 3: 2, 99: 3}},  # dictionary of packet type as key and value as number of packets per sprinkler
        {'flow_min': '0x808', 'flow_max': None, 'value': 2},
    ],
    'enc_flow': [
        {'flow_min': None, 'flow_max': '0x608', 'value': 'legacy'},
        {'flow_min': '0x609', 'flow_max': '0x609', 'value': 'patch'},
        {'flow_min': '0x60a', 'flow_max': '0x67f', 'value': 'new'},
        {'flow_min': '0x680', 'flow_max': '0x684', 'value': 'legacy'},
        {'flow_min': '0x685', 'flow_max': '0x69f', 'value': 'new'},
        {'flow_min': '0x6a0', 'flow_max': '0x6af', 'value': 'legacy'},
        {'flow_min': '0x6b0', 'flow_max': None, 'value': 'new'},
    ],
    'first_packet_counter': [
        {'flow_min': None, 'flow_max': '0x503', 'value': 251},  # version <= 2.3
        {'flow_min': '0x504', 'flow_max': '0x51f', 'value': 257},  # version 2.4
        {'flow_min': '0x520', 'flow_max': '0x5ff', 'value': 257},  # version 2.5, 2.9
        {'flow_min': '0x600', 'flow_max': None, 'value': 254 + 255*256},  # version 3.0
    ],
    'first_cntr_8_msb': [
        {'flow_min': None, 'flow_max': '0x503', 'value': 0},  # version <= 2.3
        {'flow_min': '0x504', 'flow_max': '0x5ff', 'value': 1},  # version 2.4, 2.5, 2.9
        {'flow_min': '0x600', 'flow_max': None, 'value': 255},  # version 3.0
    ],
    'packets_per_cycle': [
        {'flow_min': None,    'flow_max': '0x602', 'value': 6},
        {'flow_min': '0x603', 'flow_max': None, 'value': 4},
    ],
    'sprinklers_per_cycle': [
        {'flow_min': None,    'flow_max': '0x602', 'value': 1},
        {'flow_min': '0x603', 'flow_max': None, 'value': 'all'},
    ],
    'n_cycles_per_aux_meas': [
        {'flow_min': None,    'flow_max': '0x5ff', 'value': 4},  # gen2
        {'flow_min': '0x600', 'flow_max': None, 'value': 1},  # gen3
    ],
    'n_cycles_per_rx_clock': [
        {'flow_min': None,    'flow_max': '0x614', 'value': 4},
        {'flow_min': '0x615', 'flow_max': None, 'value': 1},
    ],
}


def get_flow_param(flow_in, param_name, args=None):
    """
    This function extract the value of the specified parameter name based on the packet flow version
    :param flow_in the packet flow version
    :type flow_in str
    :param param_name the flow parameter
    :type param_name str
    """
    flow_in = flow_in.lower().replace('.', '')
    flow_in = flow_in if flow_in.startswith('0x') else '0x' + flow_in
    if param_name not in packet_flow_parameters.keys():
        raise KeyError(f'get_flow_params: param_name is not in the map: {packet_flow_parameters.keys()}')

    param_values = packet_flow_parameters[param_name]
    for packet_flow in param_values:
        if packet_flow['flow_max'] and flow_in > packet_flow['flow_max'].lower():
            continue
        if packet_flow['flow_min'] and flow_in < packet_flow['flow_min'].lower():
            raise ValueError(f'flow_in is {flow_in} but we could not find a match flow')
        val = packet_flow['value']
        if isinstance(val, dict):
            if args is None or args not in val.keys():
                raise ValueError(f'get_flow_params: param_name: {param_name} is dictionary, args should be pass as one of the following options: {val.keys()}')
            val = val[args]
        return val


if __name__ == '__main__':
    print(get_flow_param(flow_in='0x7b0', param_name='sprinkler_num'))
