import argparse
import subprocess
import requests
import socket
import re
import urlparse
import platform
import ipaddress
from bs4 import BeautifulSoup
import csv
from datetime import datetime

EXCLUSION_LINKS = ['https://www.facebook.com', 'https://www.facebook.it', 'https://www.instagram.com', 'google.com', 'mozilla.org', 'apple.com', 'microsoft.com']
PORTS = ['', '8080', '8081', '5555', '2013', '22222', '2002', '8530', '8531', '9080', '9443']



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



def httpDiscover(ip):
    exposed_sites = []
    for port in PORTS:
        try:
            link = "http://" + ip + ":" + port
            site = requests.get(link, timeout=5)
            if site.content:
                exposed_sites.append(site.url)
        except Exception:
            pass
    return exposed_sites



def get_hostname(ip):
    try:
        hostname = str(socket.gethostbyaddr(ip)[0])
        return hostname
    except Exception:
        return "-------------------------"


def extract_links_from(url):
    responce = requests.get(url)
    return re.findall('(?:href=["\'])(.*?)["\']', responce.content.decode(errors="ignore"))



def extract_src_from(url):
    responce = requests.get(url)
    return re.findall('(?:src=["\'])(.*?)["\']', responce.content.decode(errors="ignore"))



def extract_redirect_from(url):
    responce = requests.get(url)
    return re.findall('(?:url=["\']?)(.*?)["\'\s][,\s]', str(responce.headers))



def crawl(url, ip_sito, page_auth_list=[], exclusion=[], src_in_page={}, first_access=0):
    ip_sito = str(ip_sito)
    # Se e' la prima pagina
    if first_access == 0:
        links =[url]
        page_auth_list = []
        exclusion = EXCLUSION_LINKS[:]
        src_in_page = {}
        first_access = first_access + 1
    # Per le altre pagine invece
    else:
        links = []
        extract_links = extract_links_from(url)
        for element in extract_links:
            if ".css" not in element and "javascript:openWindow" not in element and "javascript:void(0)" not in element:
                links.append(element)
        extract_src = extract_src_from(url)
        for element in extract_src:
            if ".js" not in element and ".gif" not in element and ".jpg" not in element and ".png" not in element and ".jpge" not in element and ".swf" not in element and ".ico" not in element:
                links.append(element)
                src_in_page[url] = element
        extract_redirect = extract_redirect_from(url)
        for element in extract_redirect:
            links.append(element)
    # Per ogni link della pagina
    for link in links:
        temp = link
        link = urlparse.urljoin(url,link)
        if "#" in link:
            link = link.split("#")[0]
        if ip_sito in link and link not in exclusion:
            try:
                exclusion.append(link)
                keywords = ["username", "login", "email", "e-mail", "uname", "user", "password", "pass"]
                site = requests.get(link)
                parser_html = BeautifulSoup(site.content,'html.parser')
                auth_form = parser_html.findAll("form")
                if auth_form:
                    for keyword in keywords:
                        if keyword in site.content:
                            page_auth_list.append(link)
                            try:
                                if len(src_in_page) > 0 and temp in src_in_page[url]:
                                    page_auth_list.append(url)
                            except Exception:
                                pass
                            break
                if "WWW-Authenticate" in site.headers:
                    page_auth_list.append(link)
                crawl(link, ip_sito, page_auth_list, exclusion, src_in_page, first_access)
            except Exception:
                pass
        exclusion.append(link)
    return page_auth_list



def httpNetworkDiscover(ip):
    file = ip.split("/")[0]
    subnet = ip.split("/")[1]
    with open('scan(' + file + "-" + subnet + ').csv', mode='wb') as csv_file:
        net4 = ipaddress.ip_network(unicode(ip), strict=False)
        colonne = ['IP', 'Hostname', 'Criticita\'', 'Portale', 'Pagine con autenticazione']
        writer = csv.DictWriter(csv_file, fieldnames=colonne)
        writer.writeheader()
        print("IP\t\t\t\tHostname\t\t\t\t\tCriticita'\t\tPortale\t\t\t\tPagine con autenticazione\n")
        print"-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
        for host in net4.hosts():
            host = str(host)
            if ping(host) == True:
                portal = httpDiscover(host)
                crawler_search = []
                for page in portal:
                    crawler_search = crawler_search + crawl(page, host)
                hostname = get_hostname(host)
                criticita = "Bassa"
                if portal:
                    criticita = "Media"
                if portal and len(crawler_search) > 0:
                    criticita = "Alta"
                if len(hostname) > 1 and len(hostname) < 7:
                    writer.writerow({'IP': host, 'Hostname': hostname, 'Criticita\'': criticita, 'Portale': str(portal), 'Pagine con autenticazione': str(crawler_search)})
                    print(host + "\t\t\t" + hostname + "\t\t\t\t\t\t" + criticita + "\t\t\t" + str(portal) + "\t\t\t\t" + str(crawler_search))
                elif len(hostname) >= 7 and len(hostname) < 16:
                    writer.writerow({'IP': host, 'Hostname': hostname, 'Criticita\'': criticita, 'Portale': str(portal), 'Pagine con autenticazione': str(crawler_search)})
                    print(host + "\t\t\t" + hostname + "\t\t\t\t\t" + criticita + "\t\t\t" + str(portal) + "\t\t\t\t" + str(crawler_search))
                elif len(hostname) >= 16 and len(hostname) < 24:
                    writer.writerow({'IP': host, 'Hostname': hostname, 'Criticita\'': criticita, 'Portale': str(portal), 'Pagine con autenticazione': str(crawler_search)})
                    print(host + "\t\t\t" + hostname + "\t\t\t\t" + criticita + "\t\t\t" + str(portal) + "\t\t\t\t" + str(crawler_search))
                else:
                    writer.writerow({'IP': host, 'Hostname': hostname, 'Criticita\'': criticita, 'Portale': str(portal), 'Pagine con autenticazione': str(crawler_search)})
                    print(host + "\t\t\t" + hostname + "\t\t\t" + criticita + "\t\t\t" + str(portal) + "\t\t\t\t" + str(crawler_search))
            else:
                print "no ping " + str(host)
        current_time = datetime.now()
        str_time = current_time.strftime("%d/%m/%Y - %H:%M:%S")
        writer.writerow({'IP': "Finish Discover: " + str(str_time), 'Hostname': "---", 'Criticita\'': "---", 'Portale': "---",'Pagine con autenticazione': "---"})
        print("\n\n")
        print("\t\t\t\t\t-------------------------->>>>> Finish Discover: " + str_time + " <<<<<-----------------------------")









# Esegui Http Network Discovery
options = get_arguments()
if platform.system().lower() == 'windows':
    subprocess.call('cls', shell=True)
else:
    subprocess.call(['clear'])
current_time = datetime.now()
str_time = current_time.strftime("%d/%m/%Y - %H:%M:%S")
print("\n\n")
print("\t\t\t\t\t        _   _             __     _                      _        ___ _")
print("\t\t\t\t\t  /\  /\ |_| |_ _ __   /\ \ \___| |___      _____  _ __| | __   /   (_)___  ___ _____   _____ _ __")
print("\t\t\t\t\t / /_/ / __| __| '_ \ /  \/ / _ \ __\ \ /\ / / _ \| '__| |/ /  / /\ / / __|/ __/ _ \ \ / / _ \ '__|")
print("\t\t\t\t\t/ __  /| |_| |_| |_) / /\  /  __/ |_ \ V  V / (_) | |  |   <  / /_//| \__ \ (_| (_) \ V /  __/ |")
print("\t\t\t\t\t\/ /_/  \__|\__| .__/\_\ \/ \___|\__| \_/\_/ \___/|_|  |_|\_\/___,' |_|___/\___\___/ \_/ \___|_|")
print("\t\t\t\t\t               |_|")
print("\t\t\t\t\t--------------------------->>>>> SUBNET TARGET: " + options.ip + " <<<<<---------------------------")
print("\t\t\t\t\t--------------------------->>>>> Start Discover: " + str_time + " <<<<<-----------------")
print("\n\n")
httpNetworkDiscover(options.ip)
print("\n\n")

