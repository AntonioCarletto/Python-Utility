#! /usr/bin/env python

import scapy.all as scapy
import netfilterqueue


def packet_sniffer(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    # print(scapy_packet.show())
    if scapy_packet[scapy.IP].dst == "83.158.240.200":
        print("Si e' collaegato a Iliad...")
    if scapy_packet[scapy.IP].dst == "157.240.219.35":
        print("Si e' collaegato a Facebook...")
    # if packet.haslayer(scapy.DNS):
    #     qname = packet[scapy.DNSQR].qname
    #     print("qname --> " + str(qname))
    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, packet_sniffer)
queue.run()
