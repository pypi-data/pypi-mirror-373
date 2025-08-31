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
import numpy as np
import pandas as pd


access_address = 'D6BE898E'


def de2bi(d, n):
    d = np.array(d)
    d = np.reshape(d, (1, -1))
    power = np.flipud(2 ** np.arange(n))

    g = np.zeros((np.shape(d)[1], n))

    for i, num in enumerate(d[0]):
        g[i] = num * np.ones((1, n))
    b = np.floor((g % (2 * power)) / power)
    return b


def generate_ble_scrambler(channel, seed_length):
    lfsr_fifo = list(de2bi(channel, 6)[0])  # , 'left-msb'
    lfsr_fifo = list(map(int, lfsr_fifo))

    lfsr_fifo.insert(0, 1)

    assert (len(lfsr_fifo) == 7)

    scrambler_seed = np.zeros((seed_length, 1))

    i=0
    for jj in range(seed_length):
        cur_i = 8*int(jj/8)+(7-(jj%8))
        scrambler_seed[cur_i] = lfsr_fifo[-1]
        next_stage = np.zeros(len(lfsr_fifo))
        next_stage[0] = lfsr_fifo[-1]
        next_stage[1] = lfsr_fifo[0]
        next_stage[2] = lfsr_fifo[1]
        next_stage[3] = lfsr_fifo[2]
        next_stage[4] = (bool(lfsr_fifo[3]) ^ bool(lfsr_fifo[-1]))
        next_stage[5] = lfsr_fifo[4]
        next_stage[6] = lfsr_fifo[5]

        lfsr_fifo = next_stage
    scrambler_seed = pd.DataFrame(scrambler_seed, dtype=int)
    return scrambler_seed

def load_json_packets(packets):
    all_packets = packets['raw'].to_list()
    all_packets = [packet.split('(')[-1].split(')')[0].strip('"') for packet in all_packets]
    all_packets_bits = [[float(bit) for bit in bin(int(packet, 16))[2:].zfill(len(packet) * 4)] for packet in all_packets]
    tx_time_data = packets['time'].astype(float).to_list()
    channels = packets['channel'].astype(int).to_list()
    tx_time_data = np.array(tx_time_data)

    out = pd.DataFrame({'packet_whiten': all_packets, 'packet_whiten_bits': all_packets_bits, 'channel': channels, 'time_from_start': tx_time_data})
    return out


def crc_check(packet):
    packet_bits = []
    for b in range(0, len(packet), 2):
        bin_w = bin(int(packet[b:b+2], 16))[2:].zfill(8)
        packet_bits += [int(bin_w[8-1-ii]) for ii in range(8)]
    
    seed = bin(int('AAAAAA', 16))[2:].zfill(8*3)
    fifo_v = [int(b) for b in seed]
    for p_b in packet_bits:
        new_bit_0 = p_b ^ fifo_v[-1]
        new_fifo = [
            new_bit_0,
            fifo_v[0] ^ new_bit_0,
            fifo_v[1],
            fifo_v[2] ^ new_bit_0,
            fifo_v[3] ^ new_bit_0,
            fifo_v[4],
            fifo_v[5] ^ new_bit_0,
            fifo_v[6],
            fifo_v[7],
            fifo_v[8] ^ new_bit_0,
            fifo_v[9] ^ new_bit_0,
        ]
        new_fifo += fifo_v[10:23]

        fifo_v = new_fifo
    return sum(fifo_v) == 0


def get_dewhiten_packet(packet_hex, packet_bits, channel):
    num_bits = len(packet_bits)
    num_unwhiten_chars = packet_hex.find(access_address.lower())+len(access_address)
    num_unwhiten_bits = num_unwhiten_chars * 4
    scrambler_seed = generate_ble_scrambler(channel, num_bits - num_unwhiten_bits)

    est_bits_v = packet_bits[num_unwhiten_bits:]
    est_bits_v = pd.DataFrame(est_bits_v, dtype=int)
    descrambled_data_v = scrambler_seed ^ est_bits_v
    data_s = ''
    for qq in range(0, num_bits - num_unwhiten_bits, 8):
        x = descrambled_data_v[qq:qq+8].transpose()
        x_string = x.to_string(header=False, index=False, index_names=False)
        x_string = x_string.replace(' ', '')
        curr_hex = f'{int(x_string,2):02x}'
        data_s = data_s + curr_hex

    if not crc_check(data_s):
        print(f'packet: {data_s.upper()} did not passed crc check')
    
    return data_s


def dewhitening_packets(packets_df):

    df_out = load_json_packets(packets_df)
    data_s = df_out.apply(lambda x: get_dewhiten_packet(packet_hex=x['packet_whiten'], packet_bits=x['packet_whiten_bits'], channel=x['channel']), axis=1)
    encrypted_data = data_s.apply(lambda x: x[0:-6].upper())
    df_out.insert(loc=0, column='raw_packet', value=encrypted_data) 
    
    return df_out


if __name__ == '__main__':
    from wiliot_core import DecryptedPacketList
    path = r"C:\Users\shunit\Downloads\packets.json"
    packets_df = pd.read_json(path)
    packets_df_out = dewhitening_packets(packets_df=packets_df)
    print(packets_df_out.head(15))
    p = DecryptedPacketList()
    p = p.import_packet_df(packet_df=packets_df_out)
    p.to_csv(r"C:\Users\shunit\Downloads\packets_out.csv")
