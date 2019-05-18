#!/bin/python

import os
import struct
from ctypes import *
import socket

# Host to listen on
host = '10.8.0.4'

# IP header
class IP(Structure):
    _fields_ = [
            ('ihl',         c_ubyte, 4),
            ('version',     c_ubyte, 4),
            ('tos',         c_ubyte),
            ('len',         c_ushort),
            ('id',          c_ushort),
            ('offset',      c_ushort),
            ('ttl',         c_ubyte),
            ('protocol_num',c_ubyte),
            ('sum',         c_ushort),
            ('src',         c_ulong),
            ('dst',         c_ulong)
            ]


def __new__(self, socket_buffer=None):
    return self.from_buffer_copy(socket_buffer)

def __init__(self, socket_buffer=None):

    # Map protocol constants to their names
    self.protocol_map = {1:'ICMP', 6:'TCP', 17:'UDP'}

    # Convert IP address to human readable form
    self.src_address = socket.inet_ntoa(struct.pack('<L', self.src))
    self.dst_address = socket.inet_ntoa(struct.pack('<L', self.dst))


