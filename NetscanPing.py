import scapy.all as scapy
import argparse
import subprocess
import platform
import ipaddress

if platform.system().lower() == 'windows':
    subprocess.call('cls', shell=True)
else:
    subprocess.call(['clear'])
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

def ping(host):
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', host]
    status = 1
    try:
        process = subprocess.check_output(command)
        if process and "destinazione non raggiungibile" not in process and "unreachable" not in process:
            status = 0
    except Exception:
        status = 1
    return status == 0


def get_hostname(ip):
    try:
        hostname = str(socket.gethostbyaddr(ip)[0])
        return hostname
    except Exception:
        return "-------------------------"

def stampa_risultato(ip):
    net4 = ipaddress.ip_network(unicode(ip), strict=False)
    print("IP\t\t\t\tHostname\n----------------------------------------------------")
    for host in net4.hosts():
        host = str(host)
        hostname = get_hostname(host)
        if ping(host) == True:
            print(host + "\t\t\t" + hostname)

options = get_arguments()
stampa_risultato(options.ip)

print("\n\n\n")