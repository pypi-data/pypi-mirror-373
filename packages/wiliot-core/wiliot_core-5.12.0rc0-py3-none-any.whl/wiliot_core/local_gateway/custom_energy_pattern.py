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
from wiliot_core.local_gateway.local_gateway_core import valid_output_power_vals, valid_bb, \
    valid_sub1g_output_power


class CustomEnergyPattern(object):
    def __init__(self, gw_obj):
        self.gw_obj = gw_obj
        self.power_2_4 = valid_output_power_vals
        self.abs_power_arr = [p['abs_power'] for p in self.power_2_4]

    def set_scan_channel(self, scan_ch):
        """
        set scanning channel
        :param scan_ch: can be ble ch (0-40) or frequency in Mhz
        :type scan_ch: int
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        rsp = self.gw_obj.write('!scan_ch {} 37'.format(scan_ch))
        return rsp

    def set_time_period_2_4_ghz(self, period_2_4):
        """
        setting the time period of the gateway application (tx-rx)
        :param period_2_4: the time period for the 2.4ghz tx/rx (between 0-255) in milliseconds
        :type period_2_4: int
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        rsp = self.gw_obj.write('!set_2_4_ghz_time_period {}'.format(period_2_4))
        return rsp

    def set_beacons_pattern_2_4_ghz(self, beacon_2_4_frequencies, beacon_2_4_duration,
                                    beacon_to_beacon=None, beacon_to_energy=None):
        """
        set the beacon pattern in 2.4GHz including number of beacons, frequencies and timing
        :param beacon_2_4_frequencies: a list of frequencies, the number of beacons equals to the length of this list
        :type beacon_2_4_frequencies: list
        :param beacon_2_4_duration: the beacon duration in microseconds
        :type beacon_2_4_duration: int
        :param beacon_to_beacon: the time between two successive beacons in microseconds
        :type beacon_to_beacon: int
        :param beacon_to_energy: relevant only if beacon_to_beacon was specified.
                                 the time between the last beacon and the energy in microseconds
        :type beacon_to_energy: int
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        cmd = '!set_beacons_pattern {} {}'.format(beacon_2_4_duration, len(beacon_2_4_frequencies))
        for f in beacon_2_4_frequencies:
            cmd += ' {}'.format(f)
        if beacon_to_beacon is not None:
            cmd += ' {}'.format(beacon_to_beacon)
            if beacon_to_energy is not None:
                cmd += ' {}'.format(beacon_to_energy)
        rsp = self.gw_obj.write(cmd)
        return rsp

    def set_beacons_output_power(self, beacon_2_4_power):
        """
        set the beacons output power
        :param beacon_2_4_power: the beacon output power according to the valid list of 2.4ghz output power
        :type beacon_2_4_power:
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        beacon_backoff = self.power_2_4[-1]['abs_power'] - beacon_2_4_power
        if beacon_backoff not in valid_bb:
            print('{} power value is not a valid power value (valid power values are: {})'.format(beacon_2_4_power,
                                                                                                  self.abs_power_arr))
        rsp = self.gw_obj.write('!beacons_backoff {}'.format(self.power_2_4[-1]['abs_power'] - beacon_2_4_power))
        return rsp

    def set_energy_pattern_2_4_ghz(self, energy_2_4_frequencies, is_sub1g_energy, energy_2_4_duration=None):
        """
        set the energy pattern in 2.4ghz, including frequencies and timing
        :param energy_2_4_frequencies: list of frequency,
                                       so each cycle the next frequency will be used for the energizing frequency
        :type energy_2_4_frequencies: list
        :param is_sub1g_energy: true if energy in sub1g is also needed
        :type is_sub1g_energy: bool
        :param energy_2_4_duration: the time duration of the energy constant wave in microsecond
        :type energy_2_4_duration: int
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        cmd = '!set_dyn_energizing_pattern 6 {} {}'.format(is_sub1g_energy, len(energy_2_4_frequencies))
        for f in energy_2_4_frequencies:
            cmd += ' {}'.format(f)
        if energy_2_4_duration is not None:
            cmd += ' {}'.format(energy_2_4_duration)
        rsp = self.gw_obj.write(cmd)
        return rsp

    def set_energy_output_power_2_4_ghz(self, energy_2_4_power):
        """
        set the output power of the energy
        :param energy_2_4_power: the constant wave output power according to the valid list of 2.4ghz output power
        :type energy_2_4_power: int
        :return: the gw ack response
        :rtype: list of two dictionaries, each dict with time and raw fields
        """
        if energy_2_4_power not in self.abs_power_arr:
            print('{} power value is not a valid power value (valid power values are: {})'.format(energy_2_4_power,
                                                                                                  self.abs_power_arr))
        abs_output_power_index = self.abs_power_arr.index(energy_2_4_power)
        rsp1 = self.gw_obj.write('!bypass_pa {}'.format(self.power_2_4[abs_output_power_index]['bypass_pa']))
        rsp2 = self.gw_obj.write('!output_power {}'.format(self.power_2_4[abs_output_power_index]['gw_output_power']))
        return [rsp1, rsp2]

    def set_time_period_sub1g(self, period_sub1g):
        """
        set the time period of the sub1g tx/rx
        :param period_sub1g: the time period of the sub1g tx/rx in milliseconds
        :type period_sub1g: int
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        rsp = self.gw_obj.write('!set_sub_1_ghz_time_period {}'.format(period_sub1g))
        return rsp

    def set_energy_pattern_sub1g(self, energy_sub1g_frequencies, energy_sub1g_duration=None):
        """
        set the energy pattern in sub1g, including frequencies and timing
        :param energy_sub1g_frequencies: list of frequency,
                                         each cycle the next frequency will be used for the energizing frequency
        :type energy_sub1g_frequencies: list
        :param energy_sub1g_duration: the time duration of the constant wave in microseconds
        :type energy_sub1g_duration: int
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        cmd = '!set_sub_1_ghz_energy_params {}'.format(len(energy_sub1g_frequencies))
        for f in energy_sub1g_frequencies:
            cmd += ' {}'.format(f)
        if energy_sub1g_duration is not None:
            cmd += '{}'.format(energy_sub1g_duration)
        rsp = self.gw_obj.write(cmd)
        return rsp

    def set_energy_output_power_sub1g(self, energy_sub1g_power):
        """
        set the energy output power in sub1g
        :param energy_sub1g_power: should be between 17-29 dbm
        :type energy_sub1g_power: int
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        if energy_sub1g_power not in valid_sub1g_output_power:
            print('{} power value is not a valid power value (valid power values are: {})'.format(
                energy_sub1g_power, valid_sub1g_output_power))
        rsp = self.gw_obj.write('!set_sub_1_ghz_power {}'.format(energy_sub1g_power))
        return rsp

    def run_gateway_app(self):
        """
        start receiving and transmitting
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        rsp = self.gw_obj.write('!gateway_app')
        return rsp

    def stop_gateway_app(self):
        """
        stop receiving and transmitting
        :return: the gw ack response
        :rtype: dict with time and raw fields
        """
        rsp = self.gw_obj.write('!cancel')
        return rsp


if __name__ == '__main__':
    from wiliot_core.local_gateway.local_gateway_core import WiliotGateway, ActionType
    import time

    gw = WiliotGateway(port='COM3', auto_connect=True)  # generate the gw obj and connect to it
    custom_ep = CustomEnergyPattern(gw_obj=gw)  # init custom ep
    if gw.connected:
        gw.start_continuous_listener()  # start a thread for getting the packets from the gw
        rsp = custom_ep.set_scan_channel(scan_ch=37)  # config the gw using the custom ep functions
        print(rsp)
        rsp = custom_ep.run_gateway_app()  # run the gw app
        print(rsp)
        print('energizing the tag for 30 seconds')
        time.sleep(30)
        packets = gw.get_packets(action_type=ActionType.ALL_SAMPLE)
        for p in packets:  # printing packets
            print(p.get_packet_string())
        rsp = custom_ep.stop_gateway_app()  # stop the gw app
        print(rsp)
    else:
        print('gw is not connected, please check connection and rerun')
    gw.exit_gw_api()  # close all communication with gw ap
