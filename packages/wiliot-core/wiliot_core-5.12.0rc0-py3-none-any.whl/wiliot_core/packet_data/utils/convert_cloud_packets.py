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

from wiliot_core.packet_data.config_files.parse_packet import *


class ConvertCloudPacket(object):
    def __init__(self, enriched_packet_row, original_packet=None, first_timestamp=0):
        """
        :param enriched_packet_row is one row from the enrich packet table from DB
        :type enriched_packet_row pd.Series
        """
        self.row = enriched_packet_row
        self.first_time = first_timestamp
        self.packet_length_type = 'UNKNOWN'
        if not ('rawPacket' in self.row.keys() and ('packetVersion' in self.row.keys() or 'flowVersion' in self.row.keys())):
            raise KeyError('cannot convert cloud packet without the following fields: '
                            '[rawPacket and packetVersion] or [rawPacket and flowVersion]')

        flow_ver = self.get_flow_ver()
        self.gw_packet = self.get_gw_data()
        base_fields = self.get_fields_before_payload(original_packet=original_packet, flow_ver=flow_ver)
        packet_out = self.combined_packet_parts(base_fields)
        packet_fixed = self.get_packet_data(packet_out)
        self.base_fields = base_fields
        self.reconstruct_packet = packet_fixed

    def get_reconstruct_packet(self):
        return self.reconstruct_packet

    def get_flow_ver(self):
        flow_ver_hex = '****'
        if 'flowVersion' in self.row:
            flow_ver_hex = str(self.row['flowVersion'])
            flow_ver_hex = flow_ver_hex.upper().replace('.', '').replace('X', '').zfill(FLOW_VER_SIZE)
            if len(flow_ver_hex) != FLOW_VER_SIZE:
                raise ValueError(f'ConvertCloudPacket: get_flow_ver: invlid flow version: {self.row["flowVersion"]}')
        return flow_ver_hex

    def get_fields_before_payload(self, original_packet, flow_ver):
        if original_packet is None:
            adva = flow_ver[:int(FLOW_VER_SIZE/2)] + \
                   ''.join(['*'] * (find_len(packet_data_info, 'adv_address') - FLOW_VER_SIZE)) + \
                   flow_ver[-int(FLOW_VER_SIZE/2):]
            en = ''.join(['*'] * find_len(packet_data_info, 'en'))
            b_type = ''.join(['*'] * find_len(packet_data_info, 'type'))
            e_header = ''.join(['*']) * find_len(packet_data_info, 'extended_header')
            adi = ''.join(['*']) * find_len(packet_data_info, 'adi')
            gw_packet = self.gw_packet
        else:
            adva = original_packet.packet_data['adv_address']
            en = original_packet.packet_data['en']
            b_type = original_packet.packet_data['type']
            e_header = original_packet.packet_data['extended_header'] \
                if 'extended_header' in original_packet.packet_data.keys() else \
                ''.join(['*']) * find_len(packet_data_info, 'extended_header')
            adi = original_packet.packet_data['adi'] \
                if 'adi' in original_packet.packet_data.keys() else \
                ''.join(['*']) * find_len(packet_data_info, 'adi')
            gw_packet = np.take(original_packet.gw_data['gw_packet'], 0)

        return {'adva': adva, 'en': en, 'b_type': b_type, 'e_header': e_header, 'adi': adi, 'gw_packet': gw_packet}

    def get_gw_data(self):
        gw_fields = {}
        gw_data = ''
        if 'rssi' in self.row:
            gw_fields['rssi'] = abs(int(self.row['rssi']))
        if 'timestamp' in self.row:
            gw_fields['gw_clock'] = int(self.row['timestamp']) - self.first_time

        if gw_fields:
            gw_bit_data = ''
            gw_fields['crc_valid'] = 1
            total_bits = 0
            for field, bit_len in gw_bit_structure.items():
                if field in gw_fields.keys():
                    bin_field = bin(int(gw_fields[field]))[2:]
                else:
                    bin_field = '0'
                bin_field = bin_field.zfill(bit_len)
                bin_field = bin_field[-bit_len:]
                gw_bit_data += str(bin_field)
                total_bits += bit_len
            gw_data = hex(int(gw_bit_data, 2))[2:].upper().zfill(int(total_bits / N_BITS_PER_CHAR))
        return gw_data
    
    @staticmethod
    def get_cloud_packet_length_type(packet_in):
        packet_len = len(packet_in)
        if packet_len == BLE_PAYLOAD_LENGTH:
            return 'BLE4_BLE5_PACKET'
        if packet_len == BLE_PAYLOAD_LENGTH - EN_TYPE_LEN:
            return 'BLE4_BLE5_PACKET'
        if packet_len == BLE_DOUBLE_PAYLOAD_LENGTH:
            return 'BLE5_DOUBLE_PACKET'
        estimated_bytes = int(packet_in[:2], 16)
        if estimated_bytes == len(packet_in[2:]) / 2:
            n_bytes = int(packet_in[:2],16) - int(TAG_EXTENDED_PAYLOAD_BYTES, 16)
            return f'BLE5_DOUBLE_PACKET_WITH_SIDE_INFO_{n_bytes}'  # including side info
        return 'UNKNOWN'

    def combined_packet_parts(self, all_fields):
        cloud_packet = str(self.row['rawPacket']).upper()
        if not is_cloud_packet(cloud_packet):
            raise Exception(f'cloud packet must starts with WILIOT_EN_TYPE: {WILIOT_EN_TYPE} or WILIOT_DATA_UID: {WILIOT_DATA_UID}')
        
        if any(cloud_packet.startswith(x) for x in WILIOT_DATA_UID):
            cloud_packet = all_fields['en'] + all_fields['b_type'] + cloud_packet

        self.packet_length_type = self.get_cloud_packet_length_type(cloud_packet)
        if self.packet_length_type == 'BLE4_BLE5_PACKET':
            return all_fields['adva'] + cloud_packet + all_fields['gw_packet']
        
        elif 'BLE5_DOUBLE_PACKET' in self.packet_length_type:
            header = [k for k, v in packet_length_types.items() if v['name'] == 'BLE5-DBL-EXT']
            phy_header = header[0]
            if 'SIDE_INFO' in self.packet_length_type:
                phy_header = header[0][:2] + hex(int(header[0][2:], 16) + int(self.packet_length_type.split('_')[-1]))[2:].upper().zfill(2)
            return phy_header + all_fields['e_header'] + all_fields['adva'] + all_fields['adi'] + cloud_packet + all_fields['gw_packet']
        else:
            raise Exception(f'unsupported packet length: packet length: {packet_len} and supported lengths are: {[BLE_PAYLOAD_LENGTH, BLE_DOUBLE_PAYLOAD_LENGTH]}')

    def get_packet_data(self, packet_out):
        new_packet = packet_out
        if 'decryptedData' in self.row.keys() and 'tagId' in self.row.keys():
            # decrypted data
            dec_tag_id = reverse_data(str(self.row['tagId']))
            dec_payload = str(self.row['decryptedData']).upper()

            type_str = 'BLE5-DBL-EXT' if 'BLE5_DOUBLE_PACKET' in self.packet_length_type else 'LEGACY'
            
            # update fields
            fields_to_update = {'enc_uid': dec_tag_id,
                                'enc_payload': dec_payload,
                                }
            for field, field_value in fields_to_update.items():
                start, length = packet_data_info[field]['index_info'][type_str]
                new_packet = new_packet[:start] + field_value.upper() + new_packet[start + length:]
            
            # zero mic to indicated decrypted packet:
            mic_start, mic_length = packet_data_info['mic']['index_info'][type_str]
            if type_str == 'LEGACY':
                mic_start += 6 # only last 3 bytes used for decryption
                mic_length = 6
            dec_mic = '0' * mic_length
            new_packet = new_packet[:mic_start] + dec_mic + new_packet[mic_start + mic_length:]
        return new_packet
