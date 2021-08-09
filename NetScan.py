#!/usr/bin/env python

import scapy.all as scapy
import argparse
import subprocess

subprocess.call(["clear"])
print("\n\n")
print(" _______          __   _________")
print(" \      \   _____/  |_/   _____/ ____ _____    ____")
print(" /   |   \_/ __ \   __\_____  \_/ ___\\\\__  \  /    \\")
print("/    |    \  ___/|  | /        \  \___ / __ \|   |  \\")
print("\____|__  /\___  >__|/_______  /\___  >____  /___|  /")
print("        \/     \/            \/     \/     \/     \/ ")
print("\n\n")

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="ip", help="IP o intervallo di IP da analizzare nella rete")
    options = parser.parse_args()
    if not options.ip:
        parser.error("\n[-] Per favore, specifica un IP o un intervallo di IP, usa --help per maggiori informazioni.")
    return options

def scan(ip):
    richiesta_arp = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    richista_arp_in_broadcast = broadcast/richiesta_arp
    lista_risposte = scapy.srp(richista_arp_in_broadcast, timeout=1, verbose=False)[0]
    lista_client = []
    for client in lista_risposte:
        client_dict = {"ip":client[1].psrc, "mac":client[1].hwsrc}
        lista_client.append(client_dict)
    return lista_client


def stampa_risultato(lista_risultati):
    print("IP\t\t\t\tMACAddress\n----------------------------------------------------")
    for client in lista_risultati:
        print(client["ip"] + "\t\t\t" + client["mac"])

options = get_arguments()
lista_scan = scan(options.ip)
stampa_risultato(lista_scan)

print("\n\n\n")

