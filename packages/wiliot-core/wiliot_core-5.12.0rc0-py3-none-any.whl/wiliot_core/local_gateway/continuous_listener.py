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

import serial # type: ignore
from serial import SerialException # type: ignore
import time
from multiprocessing import Process, Event
from queue import Empty
from enum import Enum
import datetime
import logging
import os
from wiliot_core.utils.utils import WiliotDir, valid_packet_start

PACKET_BYTE = 100  # number of char
GW_START_CMD = 'gateway_app'
GW_SIGNALS_MSGS = ['Detected High-to-Low peak', 'Detected Low-to-High peak']


class SerialProcessState(Enum):
    CONNECT = 'connect'
    WRITE = 'write'
    READ = 'read'
    DISCONNECT = 'disconnect'
    RESET = 'reset'
    STOP = 'stop'
    IDLE = 'idle'


class SerialProcess:
    """
    connect - connect to serial, return if connected (connected event)
    write - write command to serial, return the gw respond (add to rsp q)
    read - read specific msg from serial, return the gw respond (add to rsp/packet q)
    disconnect - close serial port, return if connected (connected event)
    reset - reset serial buffer
    check - number of bytes waiting in buffer (n_bytes Value
    stop - stop the process
    """
    def __init__(self, cmd_q, gw_rsp_q, packets_q, signals_q, change_connection_status, error_event,
                 log_dir_path=None, reset_time_upon_gw_start=False, n_max_packet_before_error=2,
                 pass_packets=True, allow_reset_time=True):
        """

        :param cmd_q: queue of commands to the listener including cmd = the state in the state machine,
                      and data if needed
        :type cmd_q: Queue
        :param gw_rsp_q: the listener put into this queue the gw responds
        :type gw_rsp_q: Queue
        :param packets_q: the listener put into this queue the packets received from gw
        :type packets_q: Queue
        :param signals_q: the listener put into this queue the signals (gpio) received from gw
        :type signals_q: Queue
        :param change_connection_status: listener set this event if there was a change in the connection status
        :type change_connection_status: Event
        :param error_event: listener set this event if an error occurs during run
        :type error_event: Event
        :param log_dir_path: the logging directory
        :type log_dir_path: str
        :param reset_time_upon_gw_start: if True the packet time will be reset upon sending the gw start command
        :type reset_time_upon_gw_start: bool or None
        :param n_max_packet_before_error: the number of packets in the buffer to send a warning msg
        :type n_max_packet_before_error: int or None
        :param pass_packets: if true the packets are pass into a q, else only logged
        :type pass_packets: bool
        """
        # serial port variables:
        self._comPortObj = None
        self.write_wait_time = 0.001  # [sec]
        self.cmd_q = cmd_q
        self.gw_rsp_q = gw_rsp_q
        self.packets_q = packets_q
        self.signals_q = signals_q
        self.change_connection_status = change_connection_status
        self.error_event = error_event
        self.connected = False
        self.gw_start_time = datetime.datetime.now()
        self.reset_time_upon_gw_start = reset_time_upon_gw_start if reset_time_upon_gw_start is not None else False
        self.n_max_packet_before_error = n_max_packet_before_error if n_max_packet_before_error is not None else 2
        self.buf = b''
        self.pass_packets = pass_packets
        self.allow_reset_time = allow_reset_time

        # set logging:
        self.logger = logging.getLogger('WiliotListener')

        self.set_logger(log_dir_path)
        # start run:
        self.run_sm()

    def set_logger(self, logger_dir_path):
        formatter = logging.Formatter('%(asctime)s,%(msecs)03d %(name)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        if logger_dir_path is None:
            wiliot_dir = WiliotDir()
            logger_dir_path = os.path.join(wiliot_dir.get_wiliot_root_app_dir(), 'wiliot_continuous_listener')
        if not os.path.isdir(logger_dir_path):
            os.mkdir(logger_dir_path)
        logger_name = 'listener_log_{}.log'.format(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        logger_path = os.path.join(logger_dir_path, logger_name)
        file_handler = logging.FileHandler(logger_path, mode='a')
        file_formatter = logging.Formatter('%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s', '%H:%M:%S')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(logging.DEBUG)

    def run_sm(self):
        while True:
            try:
                cmd = self.cmd_q.get(timeout=0)
                state = cmd['cmd']
            except Empty:
                cmd = None
                state = SerialProcessState.IDLE

            if state == SerialProcessState.CONNECT:
                self.connect(port=cmd['data']['port'], baud=cmd['data']['baud'])
            elif state == SerialProcessState.WRITE:
                self.write(gw_cmd=cmd['data']['gw_cmd'])
                self.read()
            elif state == SerialProcessState.READ:
                self._reset_time()
                self.read()
            elif state == SerialProcessState.DISCONNECT:
                self.disconnect()
            elif state == SerialProcessState.RESET:
                self.reset()
                self._reset_time()
            elif state == SerialProcessState.STOP:
                self.disconnect()
                break
            elif state == SerialProcessState.IDLE:
                if self.connected:
                    self.read()
                else:
                    time.sleep(0.1)
                    continue
        self.logger.info('serial process state machine is done')

    def connect(self, port, baud):
        if self.connected:
            self.change_connection_status.set()
        else:
            try:
                self._comPortObj = serial.Serial(port, baud, timeout=0.001)
                for i in range(5):
                    if self._comPortObj.isOpen():
                        break
                    time.sleep(0.1)
                    self._comPortObj = serial.Serial(port, baud, timeout=0.001)
                if self._comPortObj.isOpen():
                    self.change_connection_status.set()
                    self.connected = True
                    self.logger.info(f'Connected to port: {port}')
            except SerialException as e:
                self.logger.warning(f'Exception during connection to port {port}: {e}')

    def disconnect(self):
        if self.connected:
            try:
                self._comPortObj.close()
                self.change_connection_status.set()
                self.connected = False
            except SerialException as e:
                self.logger.warning('Exception during disconnect from serial: {e}')

    def write(self, gw_cmd):
        if self.connected:
            if isinstance(gw_cmd, str):
                gw_cmd = gw_cmd.encode()
            if gw_cmd != b'':
                if len(gw_cmd) >= 2:  # check last characters
                    if gw_cmd[-2:] != b'\r\n':
                        gw_cmd += b'\r\n'
                else:
                    gw_cmd += b'\r\n'
                if gw_cmd[0:1] != b'!':  # check first character
                    gw_cmd = b'!' + gw_cmd

                try:
                    self._comPortObj.write(gw_cmd)
                    self.logger.debug(f'sent msg {gw_cmd}')
                    if self.reset_time_upon_gw_start and GW_START_CMD in gw_cmd.decode():
                        self._reset_time()
                        self.logger.info(f"listener reset time for {gw_cmd}")
                except Exception as e:
                    self.logger.warning(f"failed to send the command to GW (check your physical connection:\n{e}")

    def reset(self):
        if self.connected:
            try:
                self._comPortObj.flush()  # wait until all data is written to the comport
                if self._comPortObj.in_waiting:
                    self.logger.warning(f'flush input buffer with {self._comPortObj.in_waiting} bytes waiting')
                    self._comPortObj.reset_input_buffer()
            except Exception as e:
                self.logger.warning(f'Exception during reset port: {e}')
    
    @staticmethod
    def is_gw_signal(msg):
        return any([gw_signal_msg in msg for gw_signal_msg in GW_SIGNALS_MSGS])
    
    def _safe_put(self, q_name, msg_dict):
        q = self.__getattribute__(q_name)
        if q.full():
            dummy = q.get()
            self.logger.warning(f"{q_name} is full, dropping {dummy}")
        q.put(msg_dict)

    def _process_packet(self, msg_dict):
        return msg_dict

    def _reset_time(self):
        if self.allow_reset_time:
            self.gw_start_time = datetime.datetime.now()

    def read(self):
        if self.connected:
            try:
                data = self._comPortObj.readline()
                self.buf += data
                if b'\n' in data:
                    msg = self.buf.decode().strip(' \t\n\r')
                    packet_time = datetime.datetime.now() - self.gw_start_time
                    msg_dict = {'time': packet_time.total_seconds(), 'raw': msg}
                    self.logger.debug(f"got msg {msg_dict}")
                    if valid_packet_start(msg):
                        # got a packet
                        msg_dict = self._process_packet(msg_dict)
                        if self.pass_packets:
                            self._safe_put('packets_q', msg_dict)
                    
                    elif self.is_gw_signal(msg):
                        # got signal
                        self._safe_put('signals_q', msg_dict)
                    
                    else:
                        # got a responds
                        self._safe_put('gw_rsp_q', msg_dict)
                    
                    self.buf = b''

                # check buffer status:
                if self._comPortObj.in_waiting > self.n_max_packet_before_error * PACKET_BYTE:
                    self.logger.warning(f'buffer contains {self._comPortObj.in_waiting} bytes')
            except serial.SerialException as e:
                self.logger.warning(f'Serial Exception during reading: {e}')
                if 'PermissionError' in str(e):
                    self.logger.warning('disconnecting')
                    self.disconnect()
            except Exception as e:
                self.error_event.set()
                self.logger.warning(f'problem during reading: {e} at packet {self.buf}. reset buffer')
                self.reset()
                self.buf = b''


if __name__ == '__main__':
    from wiliot_core.utils.utils import QueueHandler

    
    available_ports = [s.device for s in serial.tools.list_ports.comports()
                       if 'Silicon Labs' in s.description or 'CP210' in s.description]
    if len(available_ports) == 0:
        raise ConnectionError('Bridge is not connected')
    queue_handler = QueueHandler()
    commands = queue_handler.get_multiprocess_queue(queue_max_size=100)
    gw_rsp = queue_handler.get_multiprocess_queue(queue_max_size=100)
    packets = queue_handler.get_multiprocess_queue(queue_max_size=100)
    signals = queue_handler.get_multiprocess_queue(queue_max_size=100)
    connection_status = Event()
    event_error = Event()

    p_thread = Process(target=SerialProcess, args=(commands, gw_rsp, packets, signals, connection_status, event_error,
                                                   None, True, 4))
    p_thread.start()
    time.sleep(1)
    commands.put({'cmd': SerialProcessState.CONNECT, 'data': {'port': available_ports[0], 'baud': 921600}})
    connection_status.wait(3)
    if connection_status.is_set():
        print('connected')
        commands.put({'cmd': SerialProcessState.WRITE, 'data': {'gw_cmd': '!version'}})
        try:
            version_msg = gw_rsp.get(timeout=1)
            print('got rsp: {}'.format(version_msg))
        except Empty:
            print('empty')
        commands.put({'cmd': SerialProcessState.WRITE, 'data': {'gw_cmd': '!gateway_app'}})
        time.sleep(5)
        commands.put({'cmd': SerialProcessState.WRITE, 'data': {'gw_cmd': '!reset'}})
        print(f'packet queue size: {packets.qsize()}')
        for _ in range(packets.qsize()):
            print(packets.get())
    else:
        print('problem during connection')
        print(f'packet queue size: {packets.qsize()}')
    commands.put({'cmd': SerialProcessState.STOP})
    print('wait from process to end...')
    p_thread.join()
    print('done')
