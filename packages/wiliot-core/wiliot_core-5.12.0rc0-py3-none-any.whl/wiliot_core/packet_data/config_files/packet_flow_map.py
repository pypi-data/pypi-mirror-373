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


# https://wiliot.atlassian.net/wiki/spaces/SW/pages/2078608205/Packet+Structure

# packet version: from flow version, to flow version included. need to be sorted based on the flow version
packet_flow_map = \
    {
        1.0: ['0x100', '0x123'],
        1.2: ['0x124', '0x1FF'],
        2.0: ['0x200', '0x314'],
        2.1: ['0x315', '0x40C'],
        2.2: ['0x40D', '0x41D'],
        2.3: ['0x41E', '0x503'],
        2.4: ['0x504', '0x51F'],
        2.5: ['0x520', '0x5CF'],
        2.9: ['0x5D0', '0x5FF'],
        3.0: [['0x600', '0x60A'], ['0x700', '0x700'], ['0x680', '0x685']],  # always the first range should be the production range
        3.1: ['0x60B', '0x60C'],
        3.2: [['0x60D', '0x6FF'], ['0x686', '0x69F']],
        3.3: ['0x701', '0x7FF'],
        3.4: ['0x800', '0x809'],
        3.5: ['0x80A', '0x8FF'],
    }


def get_flow_version_by_packet_version(packet_version: float) -> str:
    est_flow = packet_flow_map[packet_version][-1]
    # the first flow range is the production range
    est_flow = packet_flow_map[packet_version][0][-1] if isinstance(
        est_flow, list) else est_flow
    return est_flow.lower()


def get_packet_version_by_flow_version(flow_version: str) -> float:
    for packet_version in packet_flow_map.keys():
        if is_packet_version_flow_version_match(packet_version, flow_version):
            return packet_version
    return None


def is_packet_version_flow_version_match(packet_version: float, flow_ver: str) -> bool:
    est_flows = packet_flow_map[packet_version]
    if isinstance(est_flows[0], list):
        for est_flow in est_flows:
            if est_flow[0].lower() <= flow_ver.lower() <= est_flow[1].lower():
                return True
    else:
        return est_flows[0].lower() <= flow_ver.lower() <= est_flows[1].lower()
    return False
