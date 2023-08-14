import random
import string
import requests
import csv
import argparse
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

def generate_random_string(length):
    letters_and_digits = string.ascii_lowercase + string.digits
    random_string = ''.join(random.choice(letters_and_digits) for _ in range(length))
    return random_string + ".onion"

def make_http_request(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = f"Richiesta riuscita per {url}"
            return result, url
        else:
            result = f"La richiesta per {url} ha restituito lo stato: {response.status_code}"
            return result, None
    except requests.exceptions.RequestException as e:
        result = f"Si è verificato un errore durante la richiesta per {url}: {e}"
        return result, None

def write_to_log_and_csv(message, url, protocol):
    with open("log.txt", "a") as log_file:
        log_file.write(message + "\n")
    if url and protocol:
        with open("http_responses.csv", "a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([url, protocol])

def signal_handler(signal, frame):
    print("\nInterrompendo lo script...")
    sys.exit(0)

# Gestione dell'interruzione da tastiera (CTRL + C)
signal.signal(signal.SIGINT, signal_handler)

# Gestione degli argomenti della riga di comando
parser = argparse.ArgumentParser(description="Script per effettuare chiamate HTTP e HTTPS a siti web casuali.")
parser.add_argument("-l", "--length", type=int, choices=[16, 56], default=16, help="Lunghezza della stringa casuale (16 o 56)")
parser.add_argument("-r", "--requests", type=int, default=float('inf'), help="Numero di chiamate da effettuare (default: infinito)")
args = parser.parse_args()

# Funzione per eseguire chiamate HTTP/HTTPS
def process_request(url):
    http_url = "http://" + url
    https_url = "https://" + url

    result_http, _ = make_http_request(http_url)
    result_https, _ = make_http_request(https_url)

    return result_http, result_https, http_url, https_url

# Ciclo di chiamate HTTP e HTTPS con ThreadPool
try:
    with ThreadPoolExecutor() as executor:
        for result_http, result_https, http_url, https_url in executor.map(process_request, [generate_random_string(args.length) for _ in range(args.requests)]):
            if result_http:
                write_to_log_and_csv(result_http, http_url, "http")
            if result_https:
                write_to_log_and_csv(result_https, https_url, "https")
except KeyboardInterrupt:
    print("\nInterrompendo lo script...")
