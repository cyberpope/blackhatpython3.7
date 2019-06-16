#!/bin/python

import os
import struct
from ctypes import *
import socket
from netaddr import IPNetwork, IPAddress
import threading
import time

# Host to listen on
host = '10.8.0.7'

# Subnet to target
subnet = '10.8.0.0/24'

# Magic string, script will be looking for
magic_message = 'PYTHONRULES!'

# IP header
# Needed adjusment STACK URL - https://stackoverflow.com/questions/29306747/python-sniffing-from-black-hat-python-book
# Problem caused by 'because c_ulong is 4 bytes in i386 and 8 in amd64.' - Nizham Mohamed
class IP(Structure):
    _fields_ = [
            ('ihl', c_ubyte, 4),
            ('version', c_ubyte, 4),
            ('tos', c_ubyte),
            ('len', c_ushort),
            ('id', c_ushort),
            ('offset', c_ushort),
            ('ttl', c_ubyte),
            ('protocol_num', c_ubyte),
            ('sum', c_ushort),
            ('src', c_uint32),
            ('dst', c_uint32)
    ]


    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):

        # Map protocol constants to their names
        self.protocol_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}

        # Convert IP address to human readable form
        self.src_address = socket.inet_ntoa(struct.pack('@I', self.src))
        self.dst_address = socket.inet_ntoa(struct.pack('@I', self.dst))

        # Convert protocol to human readable form
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

class ICMP(Structure):

    _fields_ = [
            ('type', c_ubyte),
            ('code', c_ubyte),
            ('checksum', c_ushort),
            ('unused', c_ushort),
            ('next_hop_mtu', c_ushort)
            ]

    def __new__(self, socket_buffer):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass
    
def udp_sender(subnet, magic_message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(magic_message.encode(),('%s' % ip, 65212))
        except:
            pass


if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# Start sending packets
t = threading.Thread(target=udp_sender, args=(subnet, magic_message))
t.start()

try:
    while True:

        # Read in a packet
        raw_buffer = sniffer.recvfrom(65565)[0]

        # Create an IP header from the first 20 bytes of the buffer
        ip_header = IP(raw_buffer[0:20])

        # Print out protocol name and hosts IPs
        print('Protocol: %s %s -> %s' % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))

        # if ICMP
        if ip_header.protocol == 'ICMP':

            # Calculate where ICMP packet starts
            offset = ip_header.ihl * 4

            buf = raw_buffer[offset:offset + sizeof(ICMP)]

            # Create ICMP structure
            icmp_header = ICMP(buf)

            print('ICMP -> Type: %d Code: %d' % (icmp_header.type, icmp_header.code))

            # Chek for ICMP type 3 and code
            if icmp_header.code == 3 and icmp_header.type == 3:

                # Confirm that host is in subnet
                if IPAddress(ip_header.src_address) in IPNetwork(subnet):

                    # Make sure it has magic message
                    if raw_buffer[len(raw_buffer) - len(magic_message):] == magic_message.encode():
                        print('Host Up: %s' % ip_header.src_address)

# Handle CTRL-C
except KeyboardInterrupt:
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
