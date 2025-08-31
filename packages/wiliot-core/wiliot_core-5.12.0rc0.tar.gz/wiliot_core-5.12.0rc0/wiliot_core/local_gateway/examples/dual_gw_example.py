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

# check out the confluence: https://wiliot.atlassian.net/wiki/spaces/SW/pages/3228827713/GW+Tester+Board+GPIO

import time

from wiliot_core import set_logger
from wiliot_core import WiliotGateway, ActionType, DataType
from wiliot_core import PacketList


MASTER_NAME = '3D2C07C18B3BBD54'  # to get gw name you can send !get_name
WORKER_NAME = '6CE32EC8D34804A3'
CONNECTED_PIN = 'P004'  # both GWs should be connect by one of the optional GPIO (check out the above link ) + GND
TEST_TIME = 5  # seconds

if __name__ == '__main__':
    my_logger_path, my_logger = set_logger(app_name='DualGwExample',
                                           dir_name='dual_gw_example',
                                           file_name='dual_gw_log')
    # init:
    gw_master = WiliotGateway(device_name=MASTER_NAME, is_multi_processes=True, logger_name=my_logger.name,
                              mp_reset_time_upon_gw_start=True)
    if not gw_master.is_connected():
        my_logger.error('error during connection to gw master')
        exit(-1)
    gw_master.reset_gw()
    if not gw_master.is_gw_alive():
        my_logger.error('error after reset gw master')
        exit(-1)

    gw_worker = WiliotGateway(device_name=WORKER_NAME, is_multi_processes=True, logger_name=my_logger.name)
    if not gw_worker.is_connected():
        my_logger.error('error during connection to gw worker')
        exit(-1)
    gw_worker.reset_gw()
    if not gw_worker.is_gw_alive():
        my_logger.error('error after reset gw worker')
        exit(-1)

    # configure:
    gw_master.config_gw(received_channel=37, energy_pattern_val=18, time_profile_val=[5, 15],
                        with_ack=True, start_gw_app=False)
    gw_rsp = gw_master.write(f"!cmd_gpio CONTROL_OUT {CONNECTED_PIN} 0")  # both gw are working together
    my_logger.info(gw_rsp)

    gw_worker.config_gw(received_channel=37, time_profile_val=[0, 15], with_ack=True, start_gw_app=False)
    gw_rsp = gw_worker.write(f"!cmd_gpio CONTROL_IN {CONNECTED_PIN} 1")
    my_logger.info(gw_rsp)

    # start collecting packets
    gw_master.config_gw(start_gw_app=True)
    t_i = time.time()
    all_packets_master = PacketList()
    all_packets_worker = PacketList()
    all_worker_rsp = []
    while time.time() - t_i < TEST_TIME:
        # collecting from master
        if gw_master.is_data_available():
            packets_master = gw_master.get_packets(action_type=ActionType.ALL_SAMPLE, data_type=DataType.PACKET_LIST)
            all_packets_master.__add__(packets_master)

        # collecting from slave
        if gw_worker.is_data_available():
            packets_worker = gw_worker.get_packets(action_type=ActionType.ALL_SAMPLE, data_type=DataType.PACKET_LIST)
            all_packets_worker.__add__(packets_worker)

        # for time sync
        all_worker_rsp += gw_worker.get_gw_responses()

    # stop both GWs:
    gw_master.stop_gw_app()
    gw_master.exit_gw_api()

    # merge results
    try:
        time_to_sync = gw_worker.get_time_of_controlled_start_app(all_worker_rsp)
        all_packets_master.sync_packet_list(new_packet_list=all_packets_worker,
                                            new_source_name='ch4', my_source_name='ch37',
                                            time_sync_new=time_to_sync, do_sort=True)
    except Exception as e:
        my_logger.warning(f'could not merge results due to {e}')

    my_logger.info(f'merge packet list: {len(all_packets_master)}')
    df = all_packets_master.get_df(add_sprinkler_info=True)
    df.to_csv('dual_test.csv')
    my_logger.info(df)
    my_logger.info('done')
