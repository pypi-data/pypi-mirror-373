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


# ---------------------------------------
#               run in real time:
# ---------------------------------------
import threading
import time
from wiliot_core import WiliotGateway, ActionType, DataType

continue_until_empty = False
data_type = DataType.TAG_COLLECTION


def recv_data_handler():
    """

    :type action_type:ActionType
    :type data_type: DataType
    :return:
    """
    print("DataHandlerProcess Start")
    while True:
        time.sleep(0)  # important for the processor - keep it for fast performance
        # check if there is data to read
        if ObjGW.is_data_available():
            # get data
            try:
                data_in = ObjGW.get_packets(data_type=data_type,
                                            action_type=ActionType.ALL_SAMPLE)
                if not data_in:
                    print('did not get data')
                    time.sleep(0.1)
                    continue
                if data_type.value == 'raw':
                    for packet_dic in data_in:
                        print("{} : {}".format(packet_dic['raw'], packet_dic['time']))
                elif data_type.value == 'packet_list':
                    for packet in data_in:
                        print(packet.get_packet_string())
                elif data_type.value == 'tag_collection':
                    for tag_id in data_in.tags.keys():
                        print(f'collected packet from tag: {tag_id}')
                        for packet in data_in.tags[tag_id]:
                            print(packet.get_packet_string())
            except Exception as e:
                print('we got exception during collecting packets: {}'.format(e))
                time.sleep(0.1)
        else:  # no available data
            if continue_until_empty:
                # stop the analysis process
                ObjGW.stop_continuous_listener()
                return


# Open GW connection
ObjGW = WiliotGateway(auto_connect=True)
is_connected, _, _ = ObjGW.get_connection_status()
if is_connected:
    ObjGW.start_continuous_listener()
    # Config GW:
    config_param, gateway_output = ObjGW.config_gw(pacer_val=0, energy_pattern_val=18, time_profile_val=[5, 15],
                                                   beacons_backoff_val=0, received_channel=37)
    print(f'config params:\n{config_param}')
    print(f'gateway output:\n{gateway_output}')
    rsp = ObjGW.write('!version', with_ack=True)
    print(rsp)
    ObjGW.check_current_config()
    # acquiring and processing in real time
    
    dataHandlerListener = threading.Thread(target=recv_data_handler, args=())
    dataHandlerListener.start()
    
    # stop all process due to event:
    time.sleep(5)
    is_stopped = ObjGW.stop_gw_app()
    if not is_stopped:
        print('could not stop the gw from transmitting and receiving')
    continue_until_empty = True
    
    # Close GW connection:
    ObjGW.close_port(is_reset=True)

else:
    print("connection failed")

# clean exit:
ObjGW.exit_gw_api()
