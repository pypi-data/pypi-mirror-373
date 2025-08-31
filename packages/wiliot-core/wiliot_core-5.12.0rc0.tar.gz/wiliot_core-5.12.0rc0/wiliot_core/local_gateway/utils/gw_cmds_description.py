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

radio_mode_str = '0: 1Mbit/s Nordic, 1: 2Mbit/s Nordic, 3: 1Mbit/s BLE, 3: 2Mbit/s BLE'


class CommandDesc(Enum):

    # information commands:
    version = {'args': None, 'desc': 'returns the Gateway Firmware version'}
    print_config = {'args': None, 'desc': 'returns the current Gateway configuration - short list'}
    print_config_extended =  {'args': None, 'desc': 'returns the current Gateway configuration - detailed list'}
    get_device_address = {'args': None, 'desc': 'returns the Gateway device address, a unique address per device'}
    get_name = {'args': None, 'desc': 'returns the Gateway name, a unique name per device'}
    full_packet_mode = {'args': ['IS_FULL_PACKET_MODE'], 'desc': 'relevant only for LEGACY (BLE4) packets. if enabled the Gateway passes the BLE4 packet including the physical header, default 0 (disable), e.g. 1'}
    run_ed_sample = {'args': None, 'desc': 'returns the Energy power the Gateway detect over the air using nordic ED methods'}

    # configurations commands:
    set_energizing_pattern = {'args': ['ENERGY_PATTERN'], 'desc': 'set the Gateway energy pattern, default 18'}
    time_profile = {'args': ['CYCLE_TIME_MS', 'ON_TIME_MS'], 'desc': 'set the Gateway time profile - cycle + on/transmit time, default 15 5'}
    scan_ch = {'args': ['RX_CHANNEL_FREQ', 'WHITENING_CHANNEL'], 'desc': 'set the Gateway scan/receive channel or frequency, default 37, e.g. 10, 2480, 39, ... the WHITENING_CHANNEL is optional if the data whitening channel is different than the scan channel.'}
    set_scan_radio = {'args': ['SCAN_RADIO_MODE', 'PREAMBLE_LENGTH'], 'desc': f'set the Gateway scan radio mode [{radio_mode_str}], default 3, and the preamble length [0=8bits, 1=16bits], default 0'}
    output_power = {'args': ['OUTPUT_POWER_STR'], 'desc': 'set the Gateway internal output-power, default pos3dBm, e.g. neg4dBm, ...'}
    bypass_pa = {'args': ['IS_BYPASS_PA_TX'], 'desc': 'set the Gateway TX Power Amplifier: 0 = means no bypass, hence PA is on, 1 = otherwise, default 0, e.g. 1'}
    bypass_tx_rx = {'args': ['IS_BYPASS_PA_TX', 'IS_BYPASS_PA_RX'], 'desc': 'set the Gateway TX and RX Power Amplifier: 0 = means no bypass, hence PA is on, 1 = otherwise, default 0, e.g. 1'}
    beacons_backoff = {'args': ['BEACONS_BACKOFF_DBM'], 'desc': 'set the Gateway beacons backoff/power reduction from the maximum power in dbm, default 0 = means no beacons backoff, e.g. 2'}

    set_sub_1_ghz_energizing_frequency = {'args': ['SUB1G_FREQ_MHZ'], 'desc': 'set the Gateway sub1g frequency in MHz, default 915000'}
    set_sub_1_ghz_energizing_mode = {'args': ['SUB1G_ENERGY_MODE'], 'desc': 'set the Gateway sub1g energy mode: 0 = [default] energy on single frequency based on the SUB1G_FREQ_MHZ, 1 = energy using the FCC hopping method, 905Mhz till 920 Mhz with 300 Khz intervals'}
    set_sub_1_ghz_power = {'args': ['SUB1G_POWER_DBM'], 'desc': 'set the Gateway sub1g output power in dBm, between 17-29, default 29'}
    sub1g_sync = {'args': ['IS_SUB1G_SYNCED'], 'desc': 'set the Gateway sub1g transmission to start at the same time the 2.4 transmission starts, otherwise the sub1g transmission would start at some point of the 2.4 cycle. default 1, e.g. 0'}
    set_sub_1_ghz_starting_point = {'args': ['SUB1G_START_POINT_MODE'], 'desc': 'set the Gateway sub1g time sync w.r.t the 2.4 transmission. mode 0 = starts with the first beacon [default], 1 = starts after completing beacons in 2.4 transmission. default 0, e.g. 1'}

    listen_to_tag_only = {'args': ['DO_LISTEN_TO_TAG_ONLY'], 'desc': 'enable/disable listen to packets that were echoed by bridges. 1 = only from tags [default], 0 = also packets echo from bridges'}
    set_rssi_th = {'args': ['RSSI_THRESHOLD'], 'desc': 'set the Gateway rssi threshold to filter packets with low signal. 0 [default] meaning no filtering, otherwise value is in minus, so to filter all packets with rssi(signal power) lower than -50dBm, set the threshold to 50'}

    pl_gw_config = {'args': ['ENABLE_PRODUCTION_LINE'], 'desc': 'enable/disable production line mode - when pulse detected on GPIO P010, Gateway sends message, start with constant wave for PL_DELAY time [default is 0] and continues with the configured energy pattern. default 0, e.g. 1'}
    trigger_pl = {'args': None, 'desc': 'trigger the Production Line process similar to external triggering by GPIO'}
    set_pl_delay = {'args': ['PL_DELAY_MS'], 'desc': 'set the Gateway Constant Wave duration in ms upon triggering the Production Line process. default 0, e.g. 100'}

    enable_crc = {'args': ['DO_PASS_BAD_CRC_PACKET'], 'desc': 'enable the Gateway to pass bad crc packets, default is 0 (disabled), e.g. 1'}
    print_crc = {'args': None, 'desc': 'returns the crc packets (any packets not only Wiliot) counter'}
    reset_crc = {'args': None, 'desc': 'reset the crc packets counters'}

    set_pacer_interval = {'args': ['PACER_INTERVAL_S'], 'desc': 'set the Gateway pacer interval - the minimum time in seconds the gateway should pass a packet from specific tag, default 0 (meaning no pacing), e.g 1'}
    set_packet_filter_on = {'args': None, 'desc': 'enable packet filter, which means the Gateway passes only unique packets'}
    set_packet_filter_off = {'args': None, 'desc': '[default] disable packet filter, which means the Gateway passes only unique packets'}

    # application commands:
    gateway_app = {'args': None, 'desc': 'start the Gateway application to transmit energy/beacons and receive packets'}
    reset = {'args': None, 'desc': 'soft reset the Gateway - will restore default configuration and re-run all the processes'}
    cancel = {'args': None, 'desc': 'stop the Gateway application, no transmitting nor receiving'}

    # Management commands:
    store_to_flash = {'args': None, 'desc': 'store the current Gateway configuration to its flash, so even after power-down or software reset the Gateway is configured with the saved configurations'}
    move_to_bootloader = {'args': None, 'desc': 'move the Gateway to bootloader mode for firmware upgrade purposes'}
    enable_hw_dual_band = {'args': ['IS_DUAL_BAND'], 'desc': 'enable or disable dual band options (sub1g) for the Gateway. the default is dual band enabled, e.g. 1 or 0'}

    # Utils:
    start_2_4_ghz_energizing = {'args': ['ENERGY_FREQ, RADIO_MODE'], 'desc': f'start to energize with constant wave on the selected freq and radio mode [{radio_mode_str}], e.g. 2480, 0'}
    start_rx = {'args': None, 'desc': f'start to listen only based on the configured scan channel'}
    start_cw = {'args': ['ON_TIME_MS, OFF_TIME_MS'], 'desc': 'start Gateway transmitting (NO receiving at all) of constant wave for the specified on time in ms, and stop transmitting based on the specified off time in ms, e.g. 2 5'}
    enable_hv_gpio = {'args': None, 'desc': 'enable the high voltage GPIO on the Gateway. when this mode is enable, instead of energy transmitted by the Gateway, the Gateway set GPIO P009 to High to interact with external hardware'}
    set_lbt = {'args': ['DO_LISTEN_BEFORE_TALK'], 'desc': 'enable the option to transmit only if there is no noise (under -70dBm) over the air. default 0, e.g. 1'}

    # dynamic patterns
    beacons_train = {'args': ['IS_SUB1G_ENERGY', 'NUMBER_OF_BEACONS', 'BEACON1', 'BEACON2', '...'], 'desc': 'set dynamic energy pattern on the Gateway (the EP number is always 41). the command set if there is energy in sub1g during the on time that is configured based on the time profile (different command), each beacon setup contains the frequency,beacon duration,silence time till the next beacon. e.g. EP18 is the same as: !beacons_train 0 4 2402,550,1 2426,550,1 2480,550,1 2480,3246,1'}

    # gpio
    cmd_gpio = {'args': ['COMMAND', 'PIN', 'ARGUMENT'], 'desc': 'for detailed explanation please check https://wiliot.atlassian.net/wiki/spaces/SW/pages/3228827713/GW+Tester+Board+GPIO. examples: !cmd_gpio SEND 1 P004 pulse 1 500, !cmd_gpio SEND 1 P004 static 1, !cmd_gpio CONTROL_OUT P030 0, !cmd_gpio CONTROL_IN P030 1'}
