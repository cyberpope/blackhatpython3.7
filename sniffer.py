#!/bin/python

import os
import socket

# Host to listen on - modify to accept CLI args
host = '10.8.0.4'

# Create raw socket and bind it to the public interface
if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

sniffer.bind((host, 0))

# Include IP headers in the capture
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# If Win send and IOCTL (input/output control) to set up promiscuous mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

# Read in a single packet
print(sniffer.recvfrom(65565))

# If Win turn off promiscuous mode
if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket_RCVALL_OFF)
