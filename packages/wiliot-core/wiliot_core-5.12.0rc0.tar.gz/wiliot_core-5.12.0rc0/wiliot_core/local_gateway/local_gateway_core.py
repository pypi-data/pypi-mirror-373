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

import socket
import threading
import multiprocessing as mp
import serial # type: ignore
import datetime
import os
import time
import json
import serial.tools.list_ports # type: ignore
from enum import Enum
from collections import deque
from queue import Queue, Empty
import logging
from typing import List
from wiliot_core.local_gateway.utils.gw_commands import CommandDetails
from wiliot_core.local_gateway.continuous_listener import SerialProcess, SerialProcessState
# from wiliot_core.local_gateway.extended.continuous_listener_simulation import SerialProcessSimulation as SerialProcess  # FOR SIMULATION ONLY
from wiliot_core.utils.utils import valid_packet_start, WiliotDir, QueueHandler
from wiliot_core.packet_data.packet import Packet
from wiliot_core.packet_data.packet_list import PacketList
from wiliot_core.packet_data.tag_collection import TagCollection
from wiliot_core.local_gateway import GatewayConfigurationError

import re
import subprocess
import shlex

DECRYPTION_MODE = False
try:
    from wiliot_core.packet_data.extended.decrypted_packet import DecryptedPacket
    from wiliot_core.packet_data.extended.decrypted_packet_list import DecryptedPacketList
    from wiliot_core.packet_data.extended.decrypted_tag_collection import DecryptedTagCollection
    from wiliot_core.local_gateway.extended.configs.mini_rx import *
    from wiliot_core.local_gateway.extended.configs.mini_rx_map import mini_rx_map
    DECRYPTION_MODE = True
except ModuleNotFoundError as e:
    pass

# parameters:
valid_sub1g_output_power = list(range(17, 29 + 1))
valid_output_power_vals = [
    {'abs_power': -21, 'gw_output_power': 'neg20dBm', 'bypass_pa': '1'},
    {'abs_power': -18, 'gw_output_power': 'neg16dBm', 'bypass_pa': '1'},
    {'abs_power': -15, 'gw_output_power': 'neg12dBm', 'bypass_pa': '1'},
    {'abs_power': -12, 'gw_output_power': 'neg8dBm', 'bypass_pa': '1'},
    {'abs_power': -8, 'gw_output_power': 'neg4dBm', 'bypass_pa': '1'},
    {'abs_power': -5, 'gw_output_power': 'pos0dBm', 'bypass_pa': '1'},
    {'abs_power': -2, 'gw_output_power': 'pos2dBm', 'bypass_pa': '1'},
    {'abs_power': -1, 'gw_output_power': 'pos3dBm', 'bypass_pa': '1'},
    {'abs_power': 0, 'gw_output_power': 'pos4dBm', 'bypass_pa': '1'},
    {'abs_power': 1, 'gw_output_power': 'pos5dBm', 'bypass_pa': '1'},
    {'abs_power': 2, 'gw_output_power': 'pos6dBm', 'bypass_pa': '1'},
    {'abs_power': 3, 'gw_output_power': 'pos7dBm', 'bypass_pa': '1'},
    {'abs_power': 4, 'gw_output_power': 'pos8dBm', 'bypass_pa': '1'},
    {'abs_power': 6, 'gw_output_power': 'neg12dBm', 'bypass_pa': '0'},
    {'abs_power': 10, 'gw_output_power': 'neg8dBm', 'bypass_pa': '0'},
    {'abs_power': 15, 'gw_output_power': 'neg4dBm', 'bypass_pa': '0'},
    {'abs_power': 20, 'gw_output_power': 'pos0dBm', 'bypass_pa': '0'},
    {'abs_power': 21, 'gw_output_power': 'pos2dBm', 'bypass_pa': '0'},
    {'abs_power': 22, 'gw_output_power': 'pos3dBm', 'bypass_pa': '0'}
]
CMDS_WITHOUT_ACK = ['move_to_bootloader', 'mtb', 'reset', 'r', 'ble_sim']
CMDS_WITH_2_ROWS = ['set_energizing_pattern', 'sep']
CMDS_WITH_3_ROWS = ['print_config_extended', 'pce']
GW_START_APP_MSGS = ['Detected Low-to-High peak', 'Start Production Line GW']
GW_TRIGGER_START_APP = ['gateway_app', 'trigger_pl']
for command in CommandDetails:
    if not command.value['status_return']:
        CMDS_WITHOUT_ACK.append(command.value['cmd'])
        CMDS_WITHOUT_ACK.append(command.value['cmd_shortcut'])


class ConfigParam:
    def __init__(self):
        self.energy_pattern = None
        self.received_channel = None
        self.time_profile_on = None
        self.time_profile_period = None
        self.beacons_backoff = None
        self.pacer_val = None
        self.filter = None
        self.pl_delay = None
        self.rssi_thr = None
        self.effective_output_power = None
        self.output_power = None
        self.bypass_pa = None


class ActionType(Enum):
    ALL_SAMPLE = 'all_samples'
    FIRST_SAMPLES = 'first_samples'
    CURRENT_SAMPLES = 'current_samples'


class DataType(Enum):
    RAW = 'raw'
    PACKET_LIST = 'packet_list'
    DECODED = 'decoded_packet'
    TAG_COLLECTION = 'tag_collection'
    DECODED_TAG_COLLECTION = 'decoded_tag_collection'


class DualGWMode(Enum):
    STATIC = 'static'  # the additional gw is on all the time
    MIRROR = 'mirror'  # the additional gw is on when the main gw is on and vice versa
    DYNAMIC = 'dynamic'  # the additional gw s on when the main gw is off and vice versa


class StatType(Enum):
    N_FILTERED_PACKETS = 'n_filtered_packets'
    GW_PACKET_TIME = 'gw_packet_time'


class WiliotGateway(object):
    """
    Wiliot Gateway (GW) API

    * the baud rate is defined to baud value and saved
    * If the port is defined (no None) than automatically try to connect to GW according to the port and baud.
    * If not, Run function FindCOMPorts to find all available ports and saves them
    * If the auto_connect is TRUE, then the function Open is running on each port until a connection is established.

    :type baud: int
    :param baud: the GW baud rate
    :type port: str
    :param port: The GW port if it is already know.
    :type auto_connect: bool
    :param auto_connect: If TRUE, connect automatically to the GW.

    :exception during open serial port process
    """

    def __init__(self, baud=921600, port=None, auto_connect=False, lock_print=None, logger_name=None, verbose=True,
                 socket_host='localhost', socket_port=8202, is_multi_processes=True, log_dir_for_multi_processes=None,
                 mp_reset_time_upon_gw_start=None, np_max_packet_in_buffer_before_error=None, device_name=None,
                 pass_packets=True, allow_reset_time=True):
        """
        :type baud: int
        :param baud: the GW baud rate
        :type port: str or None
        :param port: The GW port if it is already know.
        :type auto_connect: bool
        :param auto_connect: If TRUE, connect automatically to the GW.
        :type lock_print: threading.Lock()
        :param lock_print: used for async printing
        :type logger_name: str
        :param logger_name: the logger name using 'logging' python package add printing information to the log.
                            (the default logger name when using 'logging' is 'root')

        :type verbose: bool
        :param verbose:
        :type socket_host: str
        :param socket_host: for tcp/ip communication with another app, host name
        :type socket_port: int
        :param socket_port: for tcp/ip communication with another app, port number
        :type is_multi_processes: bool
        :param is_multi_processes: if True the listener, the data acquisition is done on a separate process
        :type log_dir_for_multi_processes: str
        :param log_dir_for_multi_processes: for multi-process only - the path where the mp listener is saved
        :type mp_reset_time_upon_gw_start: bool
        :param mp_reset_time_upon_gw_start: for multi-process only - if True, gw start time is reset when
                                            start gw app command is sent
        :type np_max_packet_in_buffer_before_error: int
        :param np_max_packet_in_buffer_before_error: for multi-process only - if buffer contains more than the
                                                     specified number a warning msg is sent
        """
        # Constants:
        self.valid_output_power_vals = valid_output_power_vals

        # initialization attributes:
        # -------------------------- #
        # locking variables:
        self._lock_read_serial = threading.Lock()
        if lock_print is None:
            self._lock_print = threading.Lock()
        else:
            self._lock_print = lock_print

        # flag variable:
        self._is_running_analysis = False
        self.available_data = False
        self.connected = False
        self.reading_exception = False
        self.verbose = verbose

        # serial port variables:
        self._comPortObj = None
        self.port = ''
        self.baud = baud
        self.write_wait_time = 0.001  # [sec]

        # GW variables:
        self.config_param = ConfigParam()
        self.sw_version = ''
        self.hw_version = ''

        # data variables:
        self.exceptions_threads = ['', '']
        self._processed = deque()
        self._port_listener_thread = None

        # multi-processing
        self.multi_process = is_multi_processes
        if self.multi_process:
            queue_handler = QueueHandler()
            cmd_serial_process_q = queue_handler.get_multiprocess_queue(queue_max_size=1000)
            com_rsp_str_input_q = queue_handler.get_multiprocess_queue(queue_max_size=1000)
            com_pkt_str_input_q = queue_handler.get_multiprocess_queue(queue_max_size=1000)
            com_sig_str_input_q = queue_handler.get_multiprocess_queue(queue_max_size=1000)
            connected_event = mp.Event()
            read_error_event = mp.Event()
            self._port_listener_thread = mp.Process(target=SerialProcess,
                                                    args=(cmd_serial_process_q,
                                                          com_rsp_str_input_q,
                                                          com_pkt_str_input_q,
                                                          com_sig_str_input_q,
                                                          connected_event,
                                                          read_error_event,
                                                          log_dir_for_multi_processes,
                                                          mp_reset_time_upon_gw_start,
                                                          np_max_packet_in_buffer_before_error,
                                                          pass_packets,
                                                          allow_reset_time,
                                                          # 'adva_counter'  # FOR SIMULATION ONLY
                                                          ))
            self._port_listener_thread.start()

            self.cmd_serial_process_q = cmd_serial_process_q
            self.com_rsp_str_input_q = com_rsp_str_input_q
            self.com_pkt_str_input_q = com_pkt_str_input_q
            self.com_sig_str_input_q = com_sig_str_input_q
            self.connected_event = connected_event
            self.read_error_event = read_error_event
        else:
            self.cmd_serial_process_q = None
            self.connected_event = None
            self.read_error_event = None
            self.com_rsp_str_input_q = Queue(maxsize=100)
            self.com_pkt_str_input_q = Queue(maxsize=1000)
            self.com_sig_str_input_q = Queue(maxsize=1000)

        self.start_time_lock = threading.Lock()
        self.stop_listen_event = threading.Event()

        self.continuous_listener_enabled = False
        self.start_time = datetime.datetime.now()

        # socket communication:
        self.server_socket = None
        self.client_conn = None
        self.try_to_connect_to_client = False
        self.socket_host = socket_host
        self.socket_port = socket_port
        self.init_socket_connection_thread = None

        # logging:
        if logger_name is None:
            self._do_log = True
            self.logger = logging.getLogger("root")
            if verbose:
                self.logger.setLevel(logging.DEBUG)
            else:
                self.logger.setLevel(logging.INFO)
        else:
            self._do_log = True
            self.logger = logging.getLogger(logger_name)

        # connection:
        # -------------- #
        # connect automatically if port is specified
        if port is not None:
            if self.open_port(port, self.baud):
                self._printing_func("connection was established: {}={}".format(self.hw_version, self.sw_version),
                                    'init')
                self.connected = True
                return

        # if port is None - let's search for all available ports
        self.available_ports = [s.device for s in serial.tools.list_ports.comports()
                                if 'Silicon Labs' in s.description or 'CP210' in s.description]
        if len(self.available_ports) == 0:
            self.available_ports = [s.name for s in serial.tools.list_ports.comports()
                                    if 'Silicon Labs' in s.description or 'CP210' in s.description]
            if len(self.available_ports) == 0:
                self._printing_func("no serial ports were found. please check your connections", "init", True)
                return

        # if user want to connect automatically - connecting to the first available COM with valid gw version
        if auto_connect or device_name is not None:
            for p in self.available_ports:
                try:
                    if self.open_port(p, self.baud):
                        self._printing_func("connection was established: {}={} , port {}".
                                            format(self.hw_version, self.sw_version, p), 'init')
                        self.connected = True
                        if device_name:
                            cur_dev_name = self.write('!get_name', with_ack=True)
                            if device_name.upper() in cur_dev_name['raw'].upper():
                                break
                            self.close_port()
                            self.connected = False
                            self._printing_func(f"connected to {p} but got wrong device name: {cur_dev_name},"
                                                f" moving to the next port", 'init')
                        else:
                            break
                except Exception as e:
                    self._printing_func("tried to connect {} but failed, moving to the next port".format(p), 'init')
            if not self.connected:
                self._printing_func("could not connect to the gateway", 'init')

    def set_logger(self, wanted_logger):
        self.logger = wanted_logger

    def set_verbosity(self, verbose=True):
        self.verbose = verbose

    def check_gw_responds(self, read_timeout=1):
        if self.multi_process:
            max_try = 5  # [sec] <~4 seconds
            version_msg = ''
            for _ in range(max_try):  # try to get ping from gw
                self.cmd_serial_process_q.put({'cmd': SerialProcessState.WRITE, 'data': {'gw_cmd': '!version'}})
                try:
                    version_msg = self.read_specific_message(msg='WILIOT_GW', read_timeout=read_timeout)
                    if version_msg:
                        break
                except Exception as e:
                    continue
            self.clear_rsp_str_input_q()
        else:
            self._write("!version")
            time.sleep(0.1)
            # read GW version:
            version_msg = self.read_specific_message(msg='SW_VER', read_timeout=3*read_timeout)

        return version_msg

    def is_gw_alive(self, delay_time=1):
        time.sleep(delay_time)
        gw_ver = self.check_gw_responds(read_timeout=2)
        return 'WILIOT_GW' in gw_ver

    def open_port(self, port, baud):
        """
        Open a serial connection according to the port and baud
        If the port is open, The GW version is read (All last messages are read since some messages can contains the tag
        packets)
        If the version name is valid (contains 'SW_VER') the GW type (BLE/WIFI/LTI) is saved together with the software
        version. If the version name is invalid, closing the serial port.

        :type  port: str
        :param port: The GW port - mandatory
        :type  baud: int
        :param baud: the GW baud rate - mandatory

        :return: TRUE if GW is connection and FALSE otherwise

        :exception:
        * could not open port 'COMX'... - make sure the baud rate and port are correct
        """
        if self.is_connected():
            self._printing_func("GW is already connected", 'open_port')
            return self.connected
        # open UART connection
        try:
            if self.multi_process:
                version_msg = ''
                self.cmd_serial_process_q.put({'cmd': SerialProcessState.CONNECT, 'data': {'port': port, 'baud': baud}})
                self.connected_event.wait(10)  # wait for few seconds is needed if the gw is already sending packets
                if self.connected_event.is_set():
                    self.connected = True
                    self.connected_event.clear()
                    version_msg = self.check_gw_responds()
                else:
                    self._printing_func('connection failed', 'open_port')
                    self.cmd_serial_process_q.put({'cmd': SerialProcessState.DISCONNECT})
            else:
                self._comPortObj = serial.Serial(port, baud, timeout=0.1)
                time.sleep(0.5)
                if self._comPortObj.isOpen():
                    self.connected = True
                    version_msg = self.check_gw_responds()
                else:
                    self.connected = False
                    return self.connected

            if 'WILIOT_GW' in version_msg:
                self.sw_version = version_msg.split('=', 1)[1].split(' ', 1)[0]
                self.hw_version = version_msg.split('=', 1)[0]
                self.port = port
                self.connected = True
                self.update_version(check_only=True)
                return self.connected
            else:
                # we read all the last lines and cannot find a valid version name
                self._printing_func('serial connection was established but gw version could not be read.\n'
                                    'Check your baud rate and port.\nDisconnecting and closing port', 'open_port')
                self.close_port(True)
                self.connected = False
                return self.connected

        except Exception as e:
            self._printing_func('connection failed', 'open_port')
            raise e

    def _write(self, cmd):
        """
        Check if the cmd is not empty, if not the function adds new lines characters ("\r\n")
        Then try to write the command to the  GW serial port

        :type cmd: str or bytes
        :param cmd: the command for the gw, not including "\r\n" - mandatory
        :return:
        """
        if self.multi_process:
            self._printing_func('not supported while using multi processes', 'write')
            return
        # write a single command - basic command
        if self.connected:
            if isinstance(cmd, str):
                cmd = cmd.encode()
            if self.verbose:
                self._printing_func(cmd.decode(), "GWwrite")
            if cmd != b'':
                if len(cmd) >= 2:  # check last characters
                    if cmd[-2:] != b'\r\n':
                        cmd += b'\r\n'
                else:
                    cmd += b'\r\n'
                if cmd[0:1] != b'!':  # check first character
                    cmd = b'!' + cmd

                try:
                    self._comPortObj.write(cmd)
                except Exception as e:
                    self._printing_func("failed to send the command to GW (check your physical connection:\n{}"
                                        .format(e), 'write')
                    raise e
        else:
            self._printing_func("gateway is not connected. please initiate connection and then send a command", 'write')
        self.quick_wait()  # wait to prevent buffer overflow:

    def write(self, cmd, with_ack=True, max_time=0.100, read_max_time=0.1, must_get_ack=False):
        if not self.is_connected():
            self._printing_func("gateway is not connected. write can not be done", 'write')
        data_in, got_ack = self.write_get_response(cmd, read_max_time=read_max_time)
        if with_ack:
            if data_in is not None and not got_ack:
                t_i = datetime.datetime.now()
                dt = 0
                while not got_ack and dt < max_time:
                    data_in, got_ack = self.write_get_response(cmd, need_to_clear=False, read_max_time=read_max_time)
                    dt = (datetime.datetime.now() - t_i).total_seconds()

                self.clear_rsp_str_input_q()
        # print msg:
        msg = "For cmd {} GW responded with {}".format(cmd, data_in['raw'])
        if "UNSUPPORTED" in data_in['raw'].upper():
            self._printing_func(f"GW responded unsupported to cmd {cmd}, response: {data_in}",
                                'write', log_level=logging.WARNING)
            got_ack = False
        elif got_ack:
            self._printing_func(msg, 'write', log_level=logging.INFO)
        else:
            self._printing_func(f"GW did not respond with command complete event. cmd: {cmd}, response: {data_in}",
                                'write', log_level=logging.INFO)
        if must_get_ack and not got_ack:
            raise GatewayConfigurationError(f'did not get ACK for {cmd}: {data_in}')
        return data_in

    def write_get_response(self, cmd, need_to_clear=True, read_max_time=0.1):
        if need_to_clear:
            self.clear_rsp_str_input_q()
        if self.multi_process:
            self.cmd_serial_process_q.put({'cmd': SerialProcessState.WRITE, 'data': {'gw_cmd': cmd}})
        else:
            self._write(cmd)
        if self.continuous_listener_enabled or self.multi_process:
            try:
                data_in = self.com_rsp_str_input_q.get(timeout=read_max_time)
            except Empty as e:
                data_in = {'raw': '', 'time': 0}
                is_ack = self.is_command_acknowledged(cmd=cmd, rsp=data_in['raw'])
                return data_in, is_ack

            if "command complete event" not in data_in['raw'].lower() and \
                    any([cmd_str in cmd for cmd_str in CMDS_WITH_2_ROWS + CMDS_WITH_3_ROWS]):
                try:
                    data_in_2nd_row = self.com_rsp_str_input_q.get(timeout=read_max_time)
                    data_in['raw'] += '\n{}'.format(data_in_2nd_row['raw'])
                    if any([cmd_str in cmd for cmd_str in CMDS_WITH_3_ROWS]):
                        data_in_3rd_row = self.com_rsp_str_input_q.get(timeout=read_max_time)
                        data_in['raw'] += '\n{}'.format(data_in_3rd_row['raw'])
                except Exception as e:
                    print('could not found a second/third row to gw respond {}'.format(e))

            if "unsupported" in data_in['raw'].lower():
                is_ack = False
            else:
                if isinstance(cmd, bytes):
                    cmd = cmd.decode()
                is_ack = self.is_command_acknowledged(cmd=cmd, rsp=data_in['raw'])

            return data_in, is_ack
        else:
            is_ack = True
            data = self.readline_from_buffer()
            self._printing_func(
                "GW write_get_response {} respond with {} is not supported "
                "without continuous_listener_enabled".format(cmd, data),
                "write_get_response")
            return {'raw': data, 'time': 0}, is_ack

    @staticmethod
    def is_command_acknowledged(cmd, rsp):
        cmd_str = cmd.replace('!', '').split(' ')[0]
        return cmd_str in CMDS_WITHOUT_ACK or "command complete event" in rsp.lower()

    def get_curr_timestamp_in_sec(self):
        return (datetime.datetime.now() - self.start_time).total_seconds()

    def read_specific_message(self, msg, read_timeout=1, clear=False):
        """
        search for specific message in the input buffer
        :type msg: str
        :param msg: the message or part of the message that needed to be read
        :type read_timeout: int
        :param read_timeout: if until read_timeout in seconds the message was not found exit the function
        :return: if specific message has found, return it. if not return an empty string
        """
        if self.continuous_listener_enabled or self.multi_process:
            if clear:
                self.clear_rsp_str_input_q()
            time_start_msg = self.get_curr_timestamp_in_sec()
            dt_check_version = self.get_curr_timestamp_in_sec() - time_start_msg
            while True:  #TODO need to improve this function
                try:
                    timeout = read_timeout - dt_check_version
                    if not self.com_rsp_str_input_q.empty():
                        data_in = self.com_rsp_str_input_q.get(timeout=None)
                    else:  # no messages in Q- wait for message:
                        if timeout > 0:
                            data_in = self.com_rsp_str_input_q.get(timeout=timeout)
                        else:
                            # we read all the last lines and cannot find the specific message till read timeout
                            return ""
                    if msg in data_in['raw']:
                        return data_in['raw']
                    else:
                        if self.verbose and data_in is not None and data_in != '':
                            self._printing_func(
                                "Discard GW data while waiting for specific data:\n {}".format(data_in['raw']),
                                "read_specific_message {}".format(msg))
                        if data_in['time'] > time_start_msg + read_timeout:
                            print("packet time {} is bigger than time: {}".format(data_in['time'],
                                                                                  time_start_msg + read_timeout))
                            return ''
                        dt_check_version = self.get_curr_timestamp_in_sec()
                except Empty as e:
                    return ''
                except Exception as e:
                    raise ValueError("Failed reading messages from rsp Queue!")
        else:
            with self._lock_read_serial:
                time_start_msg = self.get_curr_timestamp_in_sec()
                dt_check_version = self.get_curr_timestamp_in_sec() - time_start_msg
                while dt_check_version < read_timeout:
                    try:
                        data_in = self._comPortObj.readline().decode()
                        if msg in data_in:
                            return data_in
                        else:
                            if self.verbose and data_in is not None and data_in != '':
                                self._printing_func(
                                    "Discard GW data while waiting for specific data:\n {}".format(data_in),
                                    "read_specific_message {}".format(msg))
                    except Exception as e:
                        self.reading_exception = True
                        self._printing_func('could not read line fro serial', func_name='read_specific_message',
                                            log_level=logging.WARNING)
                        pass
                    dt_check_version = self.get_curr_timestamp_in_sec() - time_start_msg

                # we read all the last lines and cannot find the specific message till read timeout
                return ''

    def close_port(self, is_reset=False):
        """
        If is_reset is TRUE, running the Reset function.
        Closing GW serial port

        :type is_reset: bool
        :param is_reset: if TRUE, running the Reset function before closing the port
        :return:
        """
        # close UART connection
        if self.is_connected():
            if is_reset:
                # reset for stop receiving messages from tag.
                try:
                    self.reset_gw()
                except Exception as e:
                    raise e
            try:
                if self.multi_process:
                    self.cmd_serial_process_q.put({'cmd': SerialProcessState.DISCONNECT})
                    self.connected_event.wait(1)
                    if self.connected_event.is_set():
                        self.connected_event.clear()
                        self.connected = False
                else:
                    self.stop_continuous_listener()
                    self._comPortObj.close()
                    self.connected = self._comPortObj.isOpen()
            except Exception as e:
                self._printing_func('Exception during close_port:{}'.format(e), 'close_port')
        else:
            self._printing_func('The gateway is already disconnected', 'close_port')

    def get_read_error_status(self):
        """
        :return True if we got error during reading
        """
        if self.multi_process:
            self.reading_exception = self.read_error_event.is_set()
            self.read_error_event.clear()
        current_reading_exception = self.reading_exception
        self.reading_exception = False  # reset flag
        return current_reading_exception

    def reset_gw(self, reset_gw=True, reset_port=True):
        """
        Reset the GW serial port
        Flush and reset input buffer

        :type reset_gw: bool
        :param reset_gw: if True sends a reset command
        :type reset_port: bool
        :param reset_port: if True reset the serial port
        :return:
        """
        self._printing_func("reset_gw called", "reset_gw")
        if self.is_connected():
            if reset_port:
                try:
                    if self.multi_process:
                        self.cmd_serial_process_q.put({'cmd': SerialProcessState.RESET})
                        self.start_time = datetime.datetime.now()
                    else:
                        self._comPortObj.flush()
                        self.reset_buffer()
                except Exception as e:
                    self._printing_func("Exception during reset port: {}\ncheck the gw physical connection to pc"
                                        .format(e), 'reset_gw')
                    raise e
            if reset_gw:
                try:
                    if self.multi_process:
                        self.cmd_serial_process_q.put({'cmd': SerialProcessState.WRITE, 'data': {'gw_cmd': '!reset'}})
                    else:
                        self._write(b'!reset\r\n')
                except Exception as e:
                    raise e
                time.sleep(.1)
        else:
            self._printing_func("gateway is not connected please initiate connection and then try to reset", 'reset_gw')

    def reset_buffer(self):
        """
        Reset input buffer of the GW serial COM and reset software queue (raw data and processed data)
        :return:
        """
        # reset software buffers:
        self.available_data = False
        # reset serial input buffer:
        if self.is_connected():
            # reset input buffer
            if self.multi_process:
                self.cmd_serial_process_q.put({'cmd': SerialProcessState.RESET})
                self.start_time = datetime.datetime.now()
            else:
                try:
                    if self._comPortObj.in_waiting:
                        self._comPortObj.reset_input_buffer()
                except Exception as e:
                    self._printing_func("Exception during reset_buffer:\n{}".format(e), 'reset_buffer',
                                        log_level=logging.WARNING)
                    raise e
        else:
            self._printing_func("GW is disconnected, can not reset buffer", 'reset_buffer')
        self.clear_pkt_str_input_q()
        self.clear_rsp_str_input_q()

    def stop_gw_app(self):
        is_stopped = True
        rsp = self.write('!cancel', with_ack=True, max_time=0.100)
        if 'Command Complete Event' not in rsp['raw']:
            self._printing_func("Did not get ACK from GW to stop txrx: {}".format(rsp), 'stop_gw_app')
            is_stopped = False
        self.reset_buffer()
        return is_stopped

    def config_gw(self, filter_val=None, pacer_val=None, energy_pattern_val=None, time_profile_val=None,
                  beacons_backoff_val=None, received_channel=None,
                  output_power_val=None, effective_output_power_val=None, sub1g_output_power_val=None,
                  bypass_pa_val=None, pl_delay_val=None, rssi_thr_val=None,
                  max_wait=1, check_validity=False, check_current_config_only=False, start_gw_app=True, with_ack=False,
                  combined_msg=False, whitening_as_rx=False):
        """
        set all the input configuration

        :type filter_val: bool
        :param filter_val: set packet filter.
        :type pacer_val: int
        :param pacer_val: Set pacer interval
        :type energy_pattern_val: int or str
        :param energy_pattern_val: set Energizing Pattern
        :type time_profile_val: list
        :param time_profile_val: set Timing Profile where the first element is the ON value and the
                                 2nd element is the period value.
        :type beacons_backoff_val: int
        :param beacons_backoff_val: Set beacons backoff.
        :type received_channel: int
        :param received_channel: the rx channel.
        :param rssi_thr_val: the rssi threshold of the gw
        :type rssi_thr_val: int
        :param pl_delay_val: the production line delay. if specified the pl is trigger
        :type pl_delay_val: int
        :param effective_output_power_val: the effective output power of the gw according to valid_output_power_vals
        :type effective_output_power_val: int
        :param output_power_val: the gw output power according to the string convention (e.g. pos3dBm)
        :type output_power_val: str
        :param sub1g_output_power_val: the output power of the sub1g gw according to valid_sub1g_output_power
        :type sub1g_output_power_val: int
        :type max_wait: int
        :param max_wait: the time in milliseconds to wait for gw acknowledgement after sending the config command.
        :type check_validity: bool
        :param check_validity: if True, a validity check is done on the configuration parameters
        :type check_current_config_only: bool
        :param check_current_config_only: if True only print the current GW configuration without changing it
        :return: ConfigParam class with all the configuration parameters that were set
        :rtype: ConfigParam
        """

        gateway_output = []
        combined_msg_str = '!gw_config'
        # config write wait time:
        self.write_wait_time = max_wait * 0.001
        # fix input type:
        if time_profile_val is not None and isinstance(time_profile_val, str):
            try:
                time_profile_val = [int(time_profile_val.split(',')[0]), int(time_profile_val.split(',')[1])]
            except Exception as e:
                self._printing_func("time_profile can be a string '5,15' or list of int [5,15]", 'config_gw')
                time_profile_val = None

        # check current configuration:
        if check_current_config_only:
            self.check_current_config()
            return {}
        # start configuration:

        # check the validity of the config parameters:
        if check_validity:
            self._printing_func("unavailable situation", 'config_gw')
            return

        # check if we can merge commands (channel, cycle time, transmit time, energizing pattern):
        if received_channel is not None and time_profile_val is not None and energy_pattern_val is not None \
                and start_gw_app and not whitening_as_rx:
            merge_msg = True
        else:
            merge_msg = False

        # stop gateway app before configuration:
        # if start_gw_app:
        #     self.write('!cancel')

        # set Production Line:
        if pl_delay_val is not None:
            if combined_msg:
                combined_msg_str += ' pl {}'.format(pl_delay_val)
            else:
                gateway_response = self.write('!pl_gw_config 1', with_ack=with_ack)
                gateway_response['command'] = '!pl_gw_config 1'
                gateway_output.append(gateway_response)
                gateway_response = self.write('!set_pl_delay {}'.format(pl_delay_val), with_ack=with_ack)
                gateway_response['command'] = '!set_pl_delay {}'.format(pl_delay_val)
                gateway_output.append(gateway_response)
                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.pl_delay = None
                else:
                    self.config_param.pl_delay = pl_delay_val

        # set rssi threshold:
        if rssi_thr_val is not None:
            if combined_msg:
                combined_msg_str += ' rt {}'.format(rssi_thr_val)
            else:
                gateway_response = self.write('!set_rssi_th {}'.format(rssi_thr_val), with_ack=with_ack)
                gateway_response['command'] = '!set_rssi_th {}'.format(rssi_thr_val)
                gateway_output.append(gateway_response)

                gateway_response = self.write('!send_rssi_config 1', with_ack=with_ack)
                gateway_response['command'] = '!send_rssi_config 1'
                gateway_output.append(gateway_response)

                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.rssi_thr = None
                else:
                    self.config_param.rssi_thr = rssi_thr_val

        # set output power:
        if sub1g_output_power_val is not None:
            if combined_msg:
                combined_msg_str += ' sp {}'.format(sub1g_output_power_val)
            else:
                gateway_response = self.write('!set_sub_1_ghz_power {}'.format(sub1g_output_power_val),
                                              with_ack=with_ack)
                gateway_response['command'] = '!set_sub_1_ghz_power {}'.format(sub1g_output_power_val)
                gateway_output.append(gateway_response)

        if effective_output_power_val is not None:
            valid_output_power_vals_abs_power = [out_p['abs_power'] for out_p in self.valid_output_power_vals]
            abs_output_power_index = valid_output_power_vals_abs_power.index(effective_output_power_val)
            if combined_msg:
                combined_msg_str += ' pa {}'.format(self.valid_output_power_vals[abs_output_power_index]['bypass_pa'])
                combined_msg_str += ' op {}'.format(
                    self.valid_output_power_vals[abs_output_power_index]['gw_output_power'])
            else:
                gateway_response = self.write(
                    '!bypass_pa {}'.format(self.valid_output_power_vals[abs_output_power_index]['bypass_pa']),
                    with_ack=with_ack)
                gateway_response['command'] = '!bypass_pa {}'.format(
                    self.valid_output_power_vals[abs_output_power_index]['bypass_pa'])
                gateway_output.append(gateway_response)

                gateway_response = self.write(
                    '!output_power {}'.format(self.valid_output_power_vals[abs_output_power_index]['gw_output_power']),
                    with_ack=with_ack)
                gateway_response['command'] = '!output_power {}'.format(
                    self.valid_output_power_vals[abs_output_power_index]['gw_output_power'])
                gateway_output.append(gateway_response)

                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.effective_output_power = None
                else:
                    self.config_param.effective_output_power = effective_output_power_val

        else:
            if output_power_val is not None:
                if combined_msg:
                    combined_msg_str += ' op {}'.format(output_power_val)
                else:
                    gateway_response = self.write('!output_power {}'.format(output_power_val), with_ack=with_ack)
                    gateway_response['command'] = '!output_power {}'.format(output_power_val)
                    gateway_output.append(gateway_response)
                    if 'unsupported' in gateway_response['raw'].lower():
                        self.config_param.output_power = None
                    else:
                        self.config_param.output_power = output_power_val

            if bypass_pa_val is not None:
                if combined_msg:
                    combined_msg_str += ' pa {}'.format(bypass_pa_val)
                else:
                    gateway_response = self.write(('!bypass_pa {}'.format(bypass_pa_val)), with_ack=with_ack)
                    gateway_response['command'] = '!bypass_pa {}'.format(bypass_pa_val)
                    gateway_output.append(gateway_response)

        # set filter
        if filter_val is not None:
            if combined_msg:
                combined_msg_str += ' pf {}'.format(int(filter_val))
            else:
                if filter_val:
                    str_f = 'on'
                else:
                    str_f = 'off'
                gateway_response = self.write('!set_packet_filter_' + str_f, with_ack=with_ack)
                gateway_response['command'] = '!set_packet_filter_' + str_f
                gateway_output.append(gateway_response)

                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.filter = None
                else:
                    self.config_param.filter = filter_val

        # set pacer interval
        if pacer_val is not None:
            if combined_msg:
                combined_msg_str += ' pi {}'.format(pacer_val)
            else:
                gateway_response = self.write('!set_pacer_interval {}'.format(pacer_val), with_ack=with_ack)
                gateway_response['command'] = '!set_pacer_interval {}'.format(pacer_val)
                gateway_output.append(gateway_response)

                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.pacer_val = None
                else:
                    self.config_param.pacer_val = pacer_val

        # set Received Channel
        if received_channel is not None and (not merge_msg or combined_msg):
            if combined_msg:
                combined_msg_str += ' sc {}'.format(received_channel)
            else:
                cmd_str = f'!scan_ch {received_channel}'
                if whitening_as_rx:
                    cmd_str += f' {received_channel}'
                gateway_response = self.write(cmd_str, with_ack=with_ack)
                gateway_response['command'] = cmd_str
                gateway_output.append(gateway_response)
                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.received_channel = None
                else:
                    self.config_param.received_channel = received_channel

        # set Time Profile
        if time_profile_val is not None and (not merge_msg or combined_msg):
            if combined_msg:
                combined_msg_str += ' tp {} {}'.format(time_profile_val[1], time_profile_val[0])
            else:
                gateway_response = self.write('!time_profile {} {}'.format(time_profile_val[1], time_profile_val[0]),
                                              with_ack=with_ack)
                gateway_response['command'] = '!time_profile {} {}'.format(time_profile_val[1], time_profile_val[0])
                gateway_output.append(gateway_response)

                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.time_profile_on = None
                    self.config_param.time_profile_period = None
                else:
                    self.config_param.time_profile_on = time_profile_val[0]
                    self.config_param.time_profile_period = time_profile_val[1]

        # set Beacons Backoff:
        if beacons_backoff_val is not None:
            if combined_msg:
                combined_msg_str += ' bb {}'.format(beacons_backoff_val)
            else:
                gateway_response = self.write('!beacons_backoff {}\r\n'.format(beacons_backoff_val), with_ack=with_ack)
                gateway_response['command'] = '!beacons_backoff {}\r\n'.format(beacons_backoff_val)
                gateway_output.append(gateway_response)

                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.beacons_backoff = None
                else:
                    self.config_param.beacons_backoff = beacons_backoff_val

        # set Energizing Pattern:
        if energy_pattern_val is not None and (not merge_msg or combined_msg):
            if combined_msg:
                combined_msg_str += ' ep {}'.format(energy_pattern_val)
            else:
                gateway_response = self.write('!set_energizing_pattern {}'.format(energy_pattern_val),
                                              with_ack=with_ack)
                gateway_response['command'] = '!set_energizing_pattern {}'.format(energy_pattern_val)
                gateway_output.append(gateway_response)
                if 'unsupported' in gateway_response['raw'].lower():
                    self.config_param.energy_pattern = None
                else:
                    self.config_param.energy_pattern = energy_pattern_val

        # starting transmitting + listening:
        if start_gw_app and (not merge_msg or combined_msg):
            if combined_msg:
                combined_msg_str += ' ga'
            else:
                gateway_response = self.write('!gateway_app', with_ack=with_ack)
                gateway_response['command'] = '!gateway_app'
                gateway_output.append(gateway_response)

        # send merge msg if available: (channel, cycle time, transmit time, energizing pattern)
        if merge_msg and not combined_msg:
            gateway_response = self.write(
                '!gateway_app {} {} {} {}'.format(received_channel, time_profile_val[1], time_profile_val[0],
                                                  energy_pattern_val), with_ack=with_ack)
            gateway_response['command'] = '!gateway_app {} {} {} {}'.format(received_channel, time_profile_val[1],
                                                                            time_profile_val[0],
                                                                            energy_pattern_val)
            gateway_output.append(gateway_response)
            if 'unsupported' in gateway_response['raw'].lower():
                self.config_param.energy_pattern = None
                self.config_param.received_channel = None
                self.config_param.time_profile_on = None
                self.config_param.time_profile_period = None
            else:
                self.config_param.energy_pattern = energy_pattern_val
                self.config_param.received_channel = received_channel
                self.config_param.time_profile_on = time_profile_val[0]
                self.config_param.time_profile_period = time_profile_val[1]

        if combined_msg:
            gateway_response = self.write(combined_msg_str, with_ack=with_ack)
            gateway_response['command'] = combined_msg_str
            gateway_output.append(gateway_response)
            if 'unsupported' not in gateway_response['raw'].lower():
                self.config_param.energy_pattern = energy_pattern_val
                self.config_param.received_channel = received_channel
                self.config_param.time_profile_on = time_profile_val[0]
                self.config_param.time_profile_period = time_profile_val[1]
                self.config_param.beacons_backoff = beacons_backoff_val
                self.config_param.pacer_val = pacer_val
                self.config_param.filter = filter_val
                self.config_param.pl_delay = pl_delay_val
                self.config_param.rssi_thr = rssi_thr_val
                self.config_param.effective_output_power = effective_output_power_val
                self.config_param.output_power = output_power_val
                self.config_param.bypass_pa = bypass_pa_val

        self._printing_func("configuration is set", 'config_gw')
        return self.config_param, gateway_output  # return the config parameters

    @staticmethod
    def get_cmds_for_abs_output_power(abs_output_power):
        for output_power in valid_output_power_vals:
            if abs_output_power == output_power['abs_power']:
                return {CommandDetails.output_power: [output_power['gw_output_power']],
                        CommandDetails.bypass_pa: [output_power['bypass_pa']]}
        raise ValueError(f'unsupported absolute output power: {abs_output_power}, please select one of the following: '
                        f'{[p["abs_power"] for p in valid_output_power_vals]}')

    @staticmethod
    def get_cmd_symbol_params(freq_str: str = '1Mhz', preamble_len: int = None) -> List[int]:
        """
        radio mode options:
        RADIO_MODE_MODE_Pos (0UL) /*!< Position of MODE field. */
        RADIO_MODE_MODE_Msk (0xFUL << RADIO_MODE_MODE_Pos) /*!< Bit mask of MODE field. */
        RADIO_MODE_MODE_Nrf_1Mbit (0UL) /*!< 1 Mbit/s Nordic proprietary radio mode */
        RADIO_MODE_MODE_Nrf_2Mbit (1UL) /*!< 2 Mbit/s Nordic proprietary radio mode */
        RADIO_MODE_MODE_Ble_1Mbit (3UL) /*!< 1 Mbit/s BLE */
        RADIO_MODE_MODE_Ble_2Mbit (4UL) /*!< 2 Mbit/s BLE */
        RADIO_MODE_MODE_Ble_LR125Kbit (5UL) /*!< Long range 125 kbit/s TX, 125 kbit/s and 500 kbit/s RX */
        RADIO_MODE_MODE_Ble_LR500Kbit (6UL) /*!< Long range 500 kbit/s TX, 125 kbit/s and 500 kbit/s RX */
        RADIO_MODE_MODE_Ieee802154_250Kbit (15UL) /*!< IEEE 802.15.4-2006 250 kbit/s */

        preamble options
        RADIO_PCNF0_PLEN_Pos (24UL) /*!< Position of PLEN field. */
        RADIO_PCNF0_PLEN_Msk (0x3UL << RADIO_PCNF0_PLEN_Pos) /*!< Bit mask of PLEN field. */
        RADIO_PCNF0_PLEN_8bit (0UL) /*!< 8-bit preamble */
        RADIO_PCNF0_PLEN_16bit (1UL) /*!< 16-bit preamble */
        RADIO_PCNF0_PLEN_32bitZero (2UL) /*!< 32-bit zero preamble - used for IEEE 802.15.4 */
        RADIO_PCNF0_PLEN_LongRange (3UL) /*!< Preamble - used for BLE long range */

        checkout wiliot table:
        https://wiliot.atlassian.net/wiki/spaces/SW/pages/3875930166/BLE5+at+different+flow+versions
        """
        freq_str = freq_str.lower().replace(' ', '').replace('-', '')
        if freq_str == '1mhz':
            radio_mode = 3
        elif freq_str == '2mhz':
            radio_mode = 4
        elif freq_str == '2mhznrf' or freq_str == 'nrf2mhz':
            radio_mode = 1
        else:
            raise NotImplementedError('Only 1Mhz or 2Mhz are supported for symbol frequency')
        if preamble_len is None:
            preamble_len = 16 if '2mhz' in freq_str else 8
        if preamble_len == 8:
            preamble_mode = 0
        elif preamble_len == 16:
            preamble_mode = 1
        else:
            raise NotImplementedError('Only 8 or 16 are supported for preamble length')
        return [radio_mode, preamble_mode]

    def set_configuration(self, cmds=None, start_gw_app=True, with_ack=True,
                          write_max_time=0.1, read_max_time=0.1, allow_bad_config=False, cmds_file_path=None,
                          save_configs=False):
        """
        set all the input configuration

        :param cmds: commands we want to config, each key is CommandDetails command and each value is a list of
                     parameters. e.g. cmds = {CommandDetails.scan_ch: [37], CommandDetails.set_energizing_pattern: [18]}
        :type cmds: dict
        :type start_gw_app: bool
        :param start_gw_app: if True the GW starts to transmit and receive at the end of the configuration
        :type with_ack: bool
        :param with_ack: if True after writing GW command the function waits for the gw ack msg
        :type write_max_time: float
        :param write_max_time: the time in seconds to wait for writing the command to the gw.
        :type read_max_time: float
        :param read_max_time: the time in seconds to wait for gw acknowledgement after sending the config command.
        :type allow_bad_config: bool
        :param allow_bad_config: in default (False raise exception if config was not ack,
                                 if True, print error for the bad configuration but continue to the next config value
        :return: list of dictionary of time, raw and cmd based on the cmds and the received gw response
        :rtype: list
        """
        # config write wait time:
        self.write_wait_time = write_max_time  # relevant only to threading listener and not multi-process
        if cmds_file_path is not None:
            with open(cmds_file_path, 'r') as file:
                init_cmds = json.load(file)
                cmds = {CommandDetails[key]: value for key, value in init_cmds.items()}

        cmds = cmds if cmds is not None else {}
        # check if addition commands need to be sent or edit
        if CommandDetails.time_profile in cmds.keys():
            cmds[CommandDetails.time_profile].sort(reverse=True)
        if CommandDetails.set_pl_delay in cmds.keys():
            cmds[CommandDetails.pl_gw_config] = [1]  # make sure pl is enable
        if start_gw_app and not any('gateway_app' in cmd.name for cmd in cmds.keys()):
            cmds[CommandDetails.gateway_app] = []
            merged_param = [CommandDetails.scan_ch, CommandDetails.time_profile, CommandDetails.set_energizing_pattern]
            if set(merged_param).issubset(cmds.keys()) and (
                    isinstance(cmds[CommandDetails.scan_ch], list) and len(cmds[CommandDetails.scan_ch]) == 1):
                for p in merged_param:
                    cmds[CommandDetails.gateway_app] += cmds[p]
                    del cmds[p]

        # do cmd formatting
        start_app_cmds = []
        all_formatted_cmds = []
        for cmd, args in cmds.items():
            if isinstance(args, list):
                params = [str(arg) for arg in args]
            elif isinstance(args, int) or isinstance(args, str):
                params = [str(args)]
            elif args is None:
                params = []
            else:
                raise ValueError(f'unsupported args type for {cmd.name} [{args} of type: {type(args)}')
            formatted_command = '!' + ' '.join([cmd.name] + params)
            if cmd.name in GW_TRIGGER_START_APP:
                start_app_cmds.append(formatted_command)
            else:
                all_formatted_cmds.append(formatted_command)

        # send commands
        all_formatted_cmds += start_app_cmds
        gateway_output = []
        for formatted_command in all_formatted_cmds:
            gateway_response = self.write(formatted_command, max_time=write_max_time, read_max_time=read_max_time,
                                          with_ack=with_ack, must_get_ack=not allow_bad_config)
            gateway_response['command'] = formatted_command
            gateway_output.append(gateway_response)

        self._printing_func("gw configuration is done", 'config_gw')

        if save_configs:
            cmds_str_keys = {cmd.name: args for cmd, args in cmds.items()}
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            config_file_name = f"gw_configs_{current_time}.json"
            wiliot_dir = WiliotDir()
            logger_dir_path = os.path.join(wiliot_dir.get_wiliot_root_app_dir(), 'local_gateway_configs')
            if not os.path.exists(logger_dir_path):
                os.makedirs(logger_dir_path)
            config_file_path = os.path.join(logger_dir_path, config_file_name)
            with open(config_file_path, 'w') as file:
                json.dump(cmds_str_keys, file, indent=4)
            self._printing_func(f"Configuration saved to {config_file_path}", 'config_save')

        return gateway_output

    def check_current_config(self):
        """
        print the current gw configuration
        :return:
        """
        data_in = self.write("!print_config_extended")
        # read current configuration:
        if data_in != '':
            self._printing_func("current gateway configuration:\n{}".format(data_in), 'config_gw')
            return
        else:
            # we read all the last lines and cannot find a valid message
            self._printing_func("cannot read gateway configuration", 'config_gw')
            return

    @staticmethod
    def run_command(command: str) -> None:
        def run_and_get_output(inner_command):
            process = subprocess.Popen(inner_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            ret_output = ''
            while True:
                output = process.stdout.readline().decode()
                if process.poll() is not None:
                    return ret_output
                if output:
                    ret_output += output.strip()

        print('------------------------Starting to update GW FW------------------------')
        output = run_and_get_output(f'nrfutil -v -v {command}')
        if 'error' in output:
            output = run_and_get_output(f'nrfutil nrf5sdk-tools -v {command}')
        print(output)

    def update_version(self, version="Latest", versions_path="", check_only=False, force_update=False):
        """
        first check if the required version has a matched zip file under the gw versions folder.
        Then, compare the gw version with the required version. if the versions are different,
        then it checks if the required version has a matched zip file under the gw versions folder.
        if the file exists, a version update is done by send the gw to bootloader mode and burn the version
        using nRF utils

        :type versions_path: str
        :param versions_path: the path of the gateway version zip file. If defined, the update is run regardless to the
                              current gw version
        :type version: str
        :param version: the version string in the following format 'x.x.x'.
                        if version is 'Latest' than the latest version is selected
        :type check_only: bool
        :param check_only: if True the function only checks the version but does not update it
        :return: True if GW version is up to date, False if GW version is old and None if a problem occur
        """
        required_version = ''
        if versions_path == "":
            # check available versions:
            try:
                required_version, new_version_path = self.get_latest_version_number(version=version,
                                                                                    versions_path=versions_path)
            except Exception as e:
                raise e
            if not required_version:
                return

            # check if the GW is already with the right version:
            if self.sw_version == required_version and not force_update:
                self._printing_func("Your Gateway is already updated", 'update_version')
                return True
            # The GW need to be updated
            if check_only:
                self._printing_func("Your Gateway needs to be updated", 'update_version')
                return False

            r_major, _, _ = required_version.split('.')
            c_major, _, _ = self.sw_version.split('.')

            if int(r_major) > int(c_major):
                # Major change - need to load boot loader:
                if int(r_major) == 4 and int(c_major) == 3:
                    pass  # no bootloader change was done between these versions
                elif "app" in new_version_path:
                    new_version_path = new_version_path.replace('app', 'sd_bl_gw_app')
                    if not os.path.isfile(new_version_path):
                        raise ValueError(f"Trying to upgrade major version "
                                         f"from {self.sw_version} to {required_version}.Could not find boot loader "
                                         f"version file {new_version_path}")
        else:
            new_version_path = '"{}"'.format(versions_path)  # to avoid failure when path contains spaces

        # a version need to be updated:

        # change the GW to bootloader state
        if self.is_connected():
            self.write('!move_to_bootloader')
            time.sleep(0.1)
            self.close_port()

            # run the nRF Util to burn the version:
            time.sleep(.1)
            # wait until burn was completed
            self._printing_func(f"update version from: {new_version_path}. please wait for approx. 30 seconds...",
                                'update_version')
            command = f'dfu serial  --package {new_version_path} -p {self.port} -fc 0 -b 115200 -t 10'
            self.run_command(command)

            self._printing_func("Rebooting and opening serial port again...", 'update_version')
            time.sleep(5)
            for i in range(5):
                time.sleep(1)
                # open GW again
                if self.open_port(self.port, baud=self.baud):
                    break
            if versions_path == "":
                if self.sw_version == required_version:
                    self._printing_func("Your Gateway is updated", 'update_version')
                    return True
                else:
                    self._printing_func("update failed. please try again", 'update_version')
                    return False
            else:
                # TODO: Add check of the version..
                return True
        else:
            self._printing_func("Gateway is not connected. please initiate connection before update versions",
                                'update_version')
            return False

    def exit_gw_api(self) -> bool:
        """
        check that all threads are terminated and serial com is closed
        :return: if exit success
        """
        exit_success = True
        if self.multi_process:
            self.cmd_serial_process_q.put({'cmd': SerialProcessState.STOP})
            self._port_listener_thread.join(2)
            if self._port_listener_thread.is_alive():
                self._printing_func("listener Process is still running", 'exit_gw_api')
                exit_success = False
        else:
            if self._port_listener_thread is not None:
                if self._port_listener_thread.is_alive():
                    self.stop_continuous_listener()
                    time.sleep(0.2)
                    if self._port_listener_thread.is_alive():
                        self._printing_func("listener thread is still running", 'exit_gw_api')
                        exit_success = False
            if self._comPortObj is not None:
                if self._comPortObj.isOpen():
                    self.close_port()
                    if self._comPortObj.isOpen():
                        self._printing_func("encounter a problem to close serial port", 'exit_gw_api')
                        exit_success = False
        return exit_success

        self.close_socket_connection()
        if self.init_socket_connection_thread is not None and self.init_socket_connection_thread.is_alive():
            self.init_socket_connection_thread.join(5)

    def _printing_func(self, str_to_print, func_name="MISSING", is_info=False, log_level=logging.INFO):
        if self.verbose or not is_info:
            with self._lock_print:
                self.logger.log(log_level, 'GW API: {}: {}'.format(func_name, str_to_print.strip()))

    def is_connected(self):
        if self.multi_process:
            connection_status_changed = self.connected_event.is_set()
            if connection_status_changed:
                self.connected = not self.connected
                self.connected_event.clear()
        return self.connected

    def get_connection_status(self, check_port=False):
        """
        :return: if gateway is connected, return True, the serial port and baud rate used for the connection.
                 if not, return False, and None for port and baud
        """
        if self.is_connected():
            if check_port:
                try:
                    self._write("!version")
                    version_msg = self.read_specific_message(msg='SW_VER', read_timeout=3)
                    # read GW version:
                    if version_msg != '':
                        self.sw_version = version_msg.split('=', 1)[1].split(' ', 1)[0]
                        self.hw_version = version_msg.split('=', 1)[0]
                    else:
                        self._printing_func("gw version could not be achieved")
                        self.close_port()
                        return False, None, None
                except Exception as e:
                    self._printing_func("while checking the gw version an error occurs: {}".format(e))
                    self.close_port()
                    return False, None, None
            return self.connected, self.port, self.baud
        return False, None, None

    def get_gw_version(self):
        """
        :return: the gateway software version, the gw hardware type
        """
        return self.sw_version, self.hw_version

    def get_latest_version_number(self, version="Latest", versions_path=""):
        """
        return the latest version in the gw_version folder or in versions_path if specified

        :type version: str
        :param version: the version string in the following format 'x.x.x'.
                        if version is 'Latest' than the latest version is selected
        :type versions_path: str
        :param versions_path: the folder path of the gateway versions zip files
        :return: the latest available version number to be installed and its path
        """
        # check available versions:
        if versions_path == "":
            versions_path = os.path.join(os.path.dirname(__file__),
                                         'local_gateway_versions')

        try:
            versions_files = [f for f in os.listdir(versions_path) if f.endswith(".zip")]
        except Exception as e:
            self._printing_func("while running update_version function:\n{}\n"
                                "check if the version_path is correct".format(e), 'update_version')
            raise e

        versions_num = []
        first_exception = None
        for version_file in versions_files:
            try:
                version_num = re.match(r'(\d+\.\d+\.\d+)', version_file).groups(1)[0]
                # versions_num.append(int(''.join(version_num)))
                versions_num.append(version_num)
            except Exception as e:

                self._printing_func("version zip file name should begin with x.x.x  Hence {} is not considered "
                                    "as a valid version file".format(version_file), 'update_version')
                first_exception = e
        if not versions_num:
            if first_exception:
                # no valid versions files
                self._printing_func("no valid version files have found - version update failed", 'update_version')
                raise first_exception
            else:
                # empty folder:
                self._printing_func("versions folder is empty - version update failed", 'update_version')
                return None, None
        # select the last version:
        latest_version = [0, 0, 0]
        for ver in versions_num:
            ver_arr = ver.split('.')
            for i, n in enumerate(ver_arr):
                if int(n) > latest_version[i]:
                    latest_version = [int(x) for x in ver_arr]
                    break
                elif int(n) < latest_version[i]:
                    break

        # select the relevant version to load
        if version == "Latest":
            required_version = '.'.join(str(n) for n in latest_version)
        else:
            if version in versions_num:
                required_version = version
            else:
                self._printing_func("no version file matches {} version".format(version), 'update_version')
                return None, None
        file_names_priority = [f"{required_version}_app.zip", f"{required_version}.zip", ]
        file_name = ''
        for file_name in file_names_priority:
            if file_name in versions_files:
                break
        new_version_path = os.path.join(versions_path, file_name)
        return required_version, new_version_path

    def is_rsp_available(self):
        return not self.com_rsp_str_input_q.empty()

    def get_gw_rsp(self):
        try:
            return self.com_rsp_str_input_q.get(timeout=0)
        except Empty:
            return None
    
    def is_signals_available(self):
        return not self.com_sig_str_input_q.empty()

    def get_gw_signal(self):
        try:
            return self.com_sig_str_input_q.get(timeout=0)
        except Empty:
            return None

    def is_data_available(self):
        """
        :return: True if data is available tp get, False otherwise
        """
        if self.continuous_listener_enabled or self.multi_process:
            return not self.com_pkt_str_input_q.empty()
        else:
            return self.available_data

    def _clear_q(self, q_name):
        q = self.__getattribute__(q_name)
        if self.multi_process:
            while True:
                try:
                    rsp = q.get(timeout=0)
                    self._printing_func(f'discarding {q_name} before writing: {rsp}',
                                        'clear_rsp_str_input_q')
                except Empty:
                    break
        else:
            with q.mutex:
                q.queue.clear()

    def clear_pkt_str_input_q(self):
        self._clear_q('com_pkt_str_input_q')

    def clear_rsp_str_input_q(self):
        self._clear_q('com_rsp_str_input_q')

    def clear_sig_str_input_q(self):
        self._clear_q('com_sig_str_input_q')

    def continuous_listener(self):
        """
        An infinite loop with the following stop-conditions:
            wait for stop event
        """
        self._printing_func('continuous_listener in threading mode is deprecate please use is_multi_processes=True', 'continuous_listener', False, logging.WARNING)
        if self.multi_process:
            self._printing_func('not supported with multi processing mode', 'continuous_listener')
            return
        buf = b''
        n_packets = 0
        consecutive_exception_counter = 0
        self._printing_func("continuous_listener Start", 'continuous_listener', True)
        with self.start_time_lock:
            self.start_time = datetime.datetime.now()
        while not self.stop_listen_event.is_set():
            try:
                # if is_stop_conditions():
                #     self.stop_listen_event.set()
                # reading the incoming data:
                data = None
                with self._lock_read_serial:
                    data = self._comPortObj.readline()

                # data handler:
                if b'\n' in data:

                    # check if buffer is full:
                    if self._comPortObj.in_waiting > 1000:
                        self._printing_func("more than 1000 bytes are waiting in the serial port buffer",
                                            'continuous_listener')
                    # get data and check it:
                    buf += data
                    if isinstance(buf, bytes):
                        msg = buf.decode().strip(' \t\n\r')

                        timestamp = datetime.datetime.now() - self.start_time
                        # if self.verbose:
                        #     print(timestamp, " ", msg)
                        msg_dict = {'time': timestamp.total_seconds(), 'raw': msg}

                        if valid_packet_start(msg):
                            if self.com_pkt_str_input_q.full():
                                dummy = self.com_pkt_str_input_q.get()
                                self._printing_func("pkt_str_input_q is full, dropping {}".format(dummy),
                                                    'continuous_listener')
                                self.com_pkt_str_input_q.put(msg_dict)
                            else:
                                n_packets += 1
                                self.available_data = True
                                self.com_pkt_str_input_q.put(msg_dict)
                        else:
                            if self.com_rsp_str_input_q.full():
                                dummy = self.com_rsp_str_input_q.get()# TODO add queue for gw signals
                                self._printing_func("rsp_str_input_q is full, dropping {}".format(dummy),
                                                    'continuous_listener', log_level=logging.DEBUG)
                            self.com_rsp_str_input_q.put(msg_dict)
                            self._printing_func("received msg from GW: {}".format(msg_dict['raw']),
                                                'run_packet_listener', log_level=logging.DEBUG)
                    buf = b''
                else:  # if timeout occurs during packet receiving, concatenate the message until '\n'
                    buf += data

                # complete the loop with no exceptions
                consecutive_exception_counter = 0

            except Exception as e:
                # saving the first exception
                self.reading_exception = True
                if consecutive_exception_counter == 0:
                    self.exceptions_threads[0] = str(e)
                self._printing_func("received: {}\ncomPortListener Exception({}/10):\n{}".
                                    format(data, consecutive_exception_counter, e), 'run_packet_listener')
                consecutive_exception_counter = consecutive_exception_counter + 1
                buf = b''
                if consecutive_exception_counter > 10:
                    self._printing_func("more than 10 Exceptions, stop comPortListener thread",
                                        'run_packet_listener')
                    if self._comPortObj.isOpen():
                        self._comPortObj.close()
                    else:
                        self._printing_func("gateway is not connected. please initiate connection and try to "
                                            "read data again", 'run_packet_listener')
                    return
                else:  # less than 10 successive exceptions
                    if self._comPortObj.isOpen():
                        pass
                    else:
                        self._printing_func("gateway is not connected. please initiate connection and try to "
                                            "read data again", 'run_packet_listener')
                        return

    def start_continuous_listener(self):
        """
        Runs the continuous_listener function as a thread
        """
        # non-blocking
        if not self.multi_process:
            if self._port_listener_thread is not None:
                if self._port_listener_thread.is_alive():
                    self.stop_continuous_listener()
                    self._port_listener_thread.join()

            self.stop_listen_event.clear()
            self._port_listener_thread = threading.Thread(target=self.continuous_listener,
                                                          args=[])
            self._port_listener_thread.start()
            self.continuous_listener_enabled = True
            return

    def stop_continuous_listener(self):
        """
        Set the stop_listen_event flag on
        """
        if not self.multi_process:
            self.stop_listen_event.set()
            self.continuous_listener_enabled = False

    def reset_listener(self):
        """
        Reset the queues and timers related to the listener
        """
        if self.multi_process:
            self.cmd_serial_process_q.put({'cmd': SerialProcessState.RESET})
            self.start_time = datetime.datetime.now()
        else:
            self.reset_start_time()
            self.reset_buffer()
            self.stop_listen_event.clear()

    def reset_start_time(self):
        if self.multi_process:
            self.cmd_serial_process_q.put({'cmd': SerialProcessState.READ})
        with self.start_time_lock:
            self.start_time = datetime.datetime.now()

    @staticmethod
    def get_time_of_controlled_start_app(gw_rsp, start_run_str='Low-to-High'):
        """
        return the time when a start gw msg was received
        :type gw_rsp list
        :param gw_rsp list of all gw responses
        : return the time of the start msg
        :rtype float
        """
        time_start = [float('nan')]
        for rsp in gw_rsp:
            if start_run_str.lower() in rsp['raw'].lower():
                time_start.append(rsp['time'])
        return time_start[-1]

    def _get_q_elements(self, q_name):
        if not self.continuous_listener_enabled and not self.multi_process:
            raise ValueError("please first call start_continuous_listener() "
                             "or run using multi_process=True."
                             "to stop the listener after usage call stop_continuous_listener()")
        q = self.__getattribute__(q_name)
        n = q.qsize()
        all_out = []
        for _ in range(n):
            try:
                data_in = q.get(timeout=0)
                all_out.append(data_in)
            except Empty:
                return all_out
            except Exception as e:
                self._printing_func(f'could not pull element from the {q_name} queue due to: {e}',
                                    '_get_q_elements')
        return all_out

    def get_gw_responses(self):
        """
        This function output all available gw responses and return it as a list of dict {'raw': '', 'time': 0}
        """
        return self._get_q_elements(q_name='com_rsp_str_input_q')

    def get_gw_signals(self):
        """
        This function output all available gw signals and return it as a list of dict {'raw': '', 'time': 0}
        """
        return self._get_q_elements(q_name='com_sig_str_input_q')

    def get_packets(self, action_type=ActionType.ALL_SAMPLE, num_of_packets=None, data_type=DataType.PACKET_LIST,
                    max_time=None, tag_inlay=None, is_blocking=True, send_to_additional_app=False, packet_version=None,
                    logger_name=None):
        """
        Extract packets from the queue, process according to data_type value.
                action_type valid options:
                all_samples: return all available packets.
                first_samples: return all the X first packets (the oldest packets ) according to num_of_packages
        If num_of_packets is larger than the available packets, it will block till num_of_packets packets are available
        if is_clocking is False it shall return empty list/PacketList according to the data_type if not enough packets
        are available in the queue

        :type action_type: ActionType
        :param action_type: {'all_samples','first_samples'}.
                            the method of data extraction (see description).
        :type num_of_packets: int or None
        :param num_of_packets: number of packets to extract
        :type data_type: DataType
        :type max_time: float
        :param max_time: number of seconds to extract packets
        :param data_type: {'raw','packet_list'}.
                          the data type to extract (see description)
        :type tag_inlay: InlayTypes
        :param tag_inlay: inlay type to calculate min tx if decryption is available
        :type is_blocking: bool
        :param is_blocking: if True and num of packet is specified functions waits until it collects all packets
        :type send_to_additional_app: bool
        :type packet_version: str or float
        :param packet_version: to support packets from bridge, user can specified the expected packet version
        :param send_to_additional_app: if True the packets are sent to tcp/ip socket
        :return: processed:
                     a list of dictionaries or on only dictionary (if only one packet has had received)
                     with all the extracted raw or processed data.
                     Dictionary keys of RAW: 'raw','time'
                     Dictionary keys of PROCESSED: 'packet','is_valid_tag_packet','adv_address','group_id','rssi',
                                                   'stat_param','time_from_start','counter_tag'
                PACKET_LIST:
                    Packet_List object
        """
        if not self.continuous_listener_enabled and not self.multi_process:
            raise ValueError("to use get_packet please first call start_continuous_listener() "
                             "or run using multi_process=True."
                             "to stop the listener after usage call stop_continuous_listener()")
        # assign parameters:
        min_expected_packets = num_of_packets

        # init output type:
        if data_type == DataType.RAW:
            packet_list = []
        else:
            packet_list = PacketList(logger_name=logger_name)

        # Check inputs:
        if action_type == action_type.ALL_SAMPLE:
            min_expected_packets = self.com_pkt_str_input_q.qsize()
            if max_time is None:
                num_of_packets = min_expected_packets
            else:
                num_of_packets = None

        elif max_time is None and num_of_packets is None:
            raise ValueError("bad input to get_packets: max_time and num_of_packets are none "
                             "while action type is NOT ALL_SAMPLE")

        elif num_of_packets is not None and is_blocking is False:
            # check if enough packets in the queue
            if num_of_packets > self.com_pkt_str_input_q.qsize():
                self._printing_func("there are not enough packets to extract ({} compare to {})".
                                    format(self.com_pkt_str_input_q.qsize(), num_of_packets), 'get_packets')
                return packet_list

        local_start_time = self.get_curr_timestamp_in_sec()
        num_collected_packets = 0
        timeout_occurred = False
        while not timeout_occurred and (num_of_packets is None or num_collected_packets < num_of_packets):
            data_in = None
            try:
                if max_time is not None:
                    curr_dt = self.get_curr_timestamp_in_sec() - local_start_time
                    timeout = max_time - curr_dt
                    if timeout > 0:
                        if not self.com_pkt_str_input_q.empty():
                            data_in = self.com_pkt_str_input_q.get(timeout=None)
                    else:
                        timeout_occurred = True
                elif not self.com_pkt_str_input_q.empty():  # max_time is None
                    data_in = self.com_pkt_str_input_q.get(timeout=None)
                else:  # queue is empty
                    if not is_blocking or not self._port_listener_thread.is_alive():
                        timeout_occurred = True
                    time.sleep(0.01)

            except Exception as e:
                raise ValueError("Failed reading messages from pkt Queue! {}".format(str(e)))

            # calc output:
            proc_packet = None
            if data_in:
                num_collected_packets += 1
                if data_type == DataType.RAW:
                    proc_packet = data_in
                else: 
                    proc_packet = Packet(data_in["raw"], data_in["time"], inlay_type=tag_inlay,
                                         logger_name=self.logger.name)

            if proc_packet is not None:
                packet_list.append(proc_packet.copy())

        if min_expected_packets and num_collected_packets < min_expected_packets:
            raise ValueError(f"get_packets collected {num_collected_packets} packets,expected minimum "
                             f"of {min_expected_packets}")

        if data_type not in (DataType.RAW, DataType.PACKET_LIST):
            if data_type == DataType.DECODED or data_type == DataType.DECODED_TAG_COLLECTION:
                packet_list = DecryptedPacketList.from_packet_list(packet_list=packet_list,
                                                                   packet_version_by_user=packet_version) 
            if data_type == DataType.TAG_COLLECTION or data_type == DataType.DECODED_TAG_COLLECTION:
                packet_list = packet_list.to_tag_list()

        if send_to_additional_app:
            self.send_data(packet_list)

        return packet_list

    def close_socket_connection(self):
        if self.server_socket is not None:
            try:
                self.client_conn.send(str.encode('STOP_APP'))
            except Exception as e:
                self._printing_func(f'could not send a STOP msg to socket connection due to {e}')
            self.server_socket.close()
        self.try_to_connect_to_client = False
        self.server_socket = None
        self.client_conn = None

    def open_socket_connection(self):
        if (self.server_socket is None or self.client_conn is None) and not self.try_to_connect_to_client:
            self.init_socket_connection_thread = threading.Thread(target=self.init_socket_connection, args=())
            self.init_socket_connection_thread.start()

    def init_socket_connection(self):
        if not self.try_to_connect_to_client:
            self.server_socket = socket.socket()
            self.server_socket.settimeout(5)
            try:
                self.server_socket.bind((self.socket_host, self.socket_port))
            except Exception as e:
                self._printing_func('problem in bind the server socket: {}'.format(e), 'init_socket_connection',
                                    log_level=logging.WARNING)
            self._printing_func('wait for client to connect', 'init_socket_connection')
            self.server_socket.listen(1)  # TODO enable the option to send data to multiple clients
            self.try_to_connect_to_client = True

        try:
            self.client_conn, client_address = self.server_socket.accept()
            self._printing_func('connected to: {}:{}'.format(client_address[0], client_address[1]),
                                'init_socket_connection')
        except socket.timeout:
            pass
        except Exception as e:
            print('while trying to connect to the socket an exception occurs: {}'.format(e))

        self.try_to_connect_to_client = False

    def send_data(self, data_list):
        """

        :param data_list:
        :type data_list: list or PacketList or DecryptedPacketList
        :return:
        :rtype:
        """
        self.open_socket_connection()
        if self.client_conn is None:
            return

        data_to_send = []
        for data in data_list:
            if isinstance(data, dict):
                if 'raw' in data.keys():
                    raw_packet = data.get('packet')
                    if not raw_packet:
                        raise ValueError(f'trying to send invalid raw packet: {data}')

                    if 'time' in data.keys():
                        packet_time = data['time']

                    elif 'time_from_start' in data.keys():
                        packet_time = data['time_from_start']

                    else:
                        raise ValueError('trying to send invalid time: {}'.format(data))

                    data_to_send.append('raw:{}, time:{},'.format(raw_packet, packet_time))

            elif isinstance(data, Packet):
                n_sprinkler = len(data)
                if n_sprinkler == 1:
                    raw_packet = data.get_packet_string(gw_data=True, process_packet=False)
                    packet_time = str(data.gw_data['time_from_start'])
                    data_to_send.append('raw:{}, time:{},'.format(raw_packet, packet_time))
                else:
                    for i in range(n_sprinkler):
                        raw_packet = data.get_packet_string(i=i, gw_data=True, process_packet=False)
                        packet_time = str(data.gw_data['time_from_start'][i])
                        data_to_send.append('raw:{}, time:{},'.format(raw_packet, packet_time))
            else:
                raise ValueError('trying to send data type: {}'.format(type(data)))
        try:
            for data in data_to_send:
                self.client_conn.send(str.encode(data))
        except Exception as e:
            print('during socket sending data an exception occurs: {}'.format(e))
            self.close_socket_connection()

    def quick_wait(self):
        """
        this function replaces the time.sleep(self.write_wait_time) for more accurate wait time
        """
        t_i = datetime.datetime.now()
        dt = datetime.datetime.now() - t_i
        while dt.total_seconds() < self.write_wait_time:
            dt = datetime.datetime.now() - t_i
        return

    def set_gw_output_power_by_index(self, abs_output_power_index, with_ack):
        self.write('!bypass_pa {}'.format(self.valid_output_power_vals[abs_output_power_index]['bypass_pa']),
                   with_ack=with_ack)
        self.write('!output_power {}'.format(self.valid_output_power_vals[abs_output_power_index]['gw_output_power']),
                   with_ack=with_ack)

    def set_gw_max_output_power(self, with_ack=False):
        self.set_gw_output_power_by_index(-1, with_ack)

    def readline_from_buffer(self, timeout=1):
        if self.multi_process:
            self._printing_func('not supported while using multi processes', 'readline')
            return ''
        buf = b''
        msg = ''
        done = False
        local_start_time = self.get_curr_timestamp_in_sec()
        end_time = local_start_time + timeout
        while not done:
            try:
                if self.get_curr_timestamp_in_sec() > end_time and timeout > 0:
                    done = True
                # reading the incoming data:
                with self._lock_read_serial:
                    data = self._comPortObj.readline()
                # data handler:
                if b'\n' in data:
                    # get data and check it:
                    buf += data
                    if isinstance(buf, bytes):
                        msg = buf.decode().strip(' \t\n\r')
                    done = True
                elif data == '':
                    done = True
            except Exception as e:
                self._printing_func(f"Failed to readline with exception {str(e)}")
            if not done:
                time.sleep(0.1)
        return msg

    def send_mini_rx(self, operation, value, sub1g_energy=False, start_gw_app=False, 
                     beacon_duration_us=None, quiet_time_us=None):
        """
        @param operation the mini rx operation based on the enum MiniRXOperations
        @type operation int or MiniRxOperations
        @param value for the selected operation
        @type value int or HarvesterFlowValues or DebugPacketValues or HarvesterTypeValues
        @param sub1g_energy if to add energy in sub1g
        @type sub1g_energy bool
        @param start_gw_app if to send msg to the GW to start transmit and receive
        @type start_gw_app bool
        @type beacon_duration_us int
        @param beacon_duration_us the time in microseconds for each beacon.
        @type quiet_time_us int
        @param quiet_time_us the quiet time in microseconds after each beacon.
        """
        beacon_duration_us = beacon_duration_us if beacon_duration_us is not None else DEFAULT_BEACON_DURATION_US
        quiet_time_us = quiet_time_us if quiet_time_us is not None else DEFAULT_BEACON_QUIET_US
        if isinstance(operation, int):
            if not isinstance(value, int):
                raise ValueError('send_mini_rx: if operation specified as the frequency value (x-freq), '
                                'the value input should be the y-freq as well (integer)')
        else:
            if operation not in mini_rx_map.keys():
                raise ValueError(f'send_mini_rx: operation: {operation} is not supported. '
                                f'please select one of the following: {list(mini_rx_map.key())}')
            op_dict = mini_rx_map[operation]
            operation = op_dict['freq']
            if not isinstance(value, Enum):
                raise ValueError('send_mini_rx: if operation if a ket of mini_rx_map the value must be an enum')
            if value.__class__ != op_dict['operation_values']:
                raise ValueError(f'send_mini_rx: the value: {value} is not part of the '
                                f'optional values: {op_dict["operation_values"].__members__}')
            value = value.value

        beacons_train_cmd = '!beacons_train'
        beacons_train_cmd += f' {int(sub1g_energy)}'
        beacons_train_cmd += f' {get_mini_rx_sequence(x=operation, y=value, beacon_duration_us=beacon_duration_us, quiet_time_us=quiet_time_us)}'
        self.write(cmd=beacons_train_cmd, with_ack=True)
        if start_gw_app:
            self.write(cmd='!gateway_app', with_ack=True)

        return beacons_train_cmd

    def reconnect(self):
        is_connected = self.open_port(port=self.port, baud=self.baud)
        if not is_connected:
            raise ConnectionError('gw-core: could not reconnect to GW')
        self.reset_buffer()
        return is_connected

    # ######## GPIO Function #############

    def set_gw_gpio(self, gpio_configs, is_send=False):
        send_config_str = 'SEND' if is_send else 'SAVE'
        for config in gpio_configs:
            cmd = f'!cmd_gpio {send_config_str} {config["signal_num"]} {config["gpio"]} {config["signal_type"]} ' \
                  f'{config["high_low"]}'
            cmd += f' {config["pulse_time"]}' if 'pulse_time' in config else ''
            self.write(cmd=cmd, with_ack=True, must_get_ack=True)

    def gpio_state(self, gpio='',  state='ON', config=None):
        if gpio == '':
            self.logger.warning('gpio_state got empty gpio, no action is done')
        if config is None:
            config = {'signal_num': 1,
                      'gpio': gpio.replace('.', '').upper(),
                      'signal_type': 'static',
                      'high_low': 1 if state.upper() == 'ON' else 0,
                      }
        self.set_gw_gpio(gpio_configs=[config], is_send=True)

    def pulse(self, gpio='', pulse_duration_ms=None, config=None):
        if config is None:
            config = {'signal_num': 1,
                      'gpio': gpio.replace('.', '').upper(),
                      'signal_type': 'pulse',
                      'high_low': 1,
                      'pulse_time': pulse_duration_ms
                      }
        self.set_gw_gpio(gpio_configs=[config], is_send=True)

    def gpio_send_signal(self, signal):
        self.write(cmd=f'!cmd_gpio SEND {signal}', with_ack=True, must_get_ack=True)

    def set_gw_control_gpio(self, is_controller, gpio, is_inverse, send_msg_only=False):
        if not gpio:
            raise NotImplementedError('gw-core: set_gw_control_gpio: gpio must be a string of the specified gpio, i.e. PO30')
        gpio_str = gpio.replace('.', '').upper()
        if is_controller:
            control_str = 'CONTROL_OUT'
            action_type = int(is_inverse)  # idle state --> 0 = mirror, 1 = inverse
        else:  # controlled by other gw
            control_str = 'CONTROL_IN'
            action_type = int(not send_msg_only)  # 1 = to start gw app, 0 = only send msg
        cmd = f'!cmd_gpio {control_str} {gpio_str} {action_type}'
        self.write(cmd=cmd, with_ack=True, must_get_ack=True)

    def __del__(self):
        if self._port_listener_thread and self._port_listener_thread.is_alive():
            self.exit_gw_api()


if __name__ == '__main__':
    pass
    # print(f"get_time_of_controlled_start_app: {WiliotGateway.get_time_of_controlled_start_app([
    #     {'raw': 'hi', 'time': 0.1}, 
    #     {'raw': 'Detected-Low-to-High', 'time': 0.2}, 
    #     {'raw': 'Detected-High-to-Low', 'time': 0.3},
    #     {'raw': 'Detected-Low-to-High', 'time': 0.4},])}")
    
    # from wiliot_core.local_gateway.extended.configs.mini_rx_operations_values import *
    # print(datetime.datetime.now())
    # gw = WiliotGateway(auto_connect=True, is_multi_processes=True)
    # gw.send_mini_rx(operation='HARVESTER_FLOW', value=HarvesterFlowValues.TRANSMIT_AT_MAX_DCO)
    # gw.send_mini_rx(operation='HARVESTER_TYPE', value=HarvesterTypeValues.X1)
    # if gw.is_connected():
    #     # gw.start_continuous_listener()
    #     gw.reset_gw(reset_port=False)
    #     print(f'is gw alive {gw.is_gw_alive()}')
    #     print(gw.write('!set_tester_mode 1', with_ack=True))
    #     gw.config_gw(energy_pattern_val=18, time_profile_val=[5, 15], effective_output_power_val=22,
    #                  beacons_backoff_val=0)
    # print(datetime.datetime.now())
    # gw.exit_gw_api()
