import getpass
import socket
import yaml
import requests
import logging

from threading import Thread
from flask import Flask, request, jsonify
from yaml import SafeLoader
from requests.exceptions import InvalidSchema, ConnectionError
from tqdm import tqdm

app = Flask(__name__)


def reg_ip(lan_ip, server_name):
    with open('address_book.yml', 'r') as f:
        address_book = yaml.load(f, Loader=SafeLoader)

    with open('address_book.yml', 'w') as g:
        address_book[server_name] = lan_ip
        yaml.dump(address_book, g)
    return


def get_myip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 1))
        lan_ip = s.getsockname()[0]
    with open('address_book.yml', 'w') as f:
        address_book = {"myip": lan_ip}
        yaml.dump(address_book, f)
    return lan_ip


# TODO: Implement security later
def valid_signature(signature: str = ""):
    return True


@app.route('/hello', methods=['POST'])
def exchange_details():
    # signature = request.args.get('signature')
    if valid_signature():
        if request.json is None:
            return "request body not found"

        try:
            ip = request.json['ip']
            user = request.json['user']
            reg_ip(ip, user)
            logging.info("Handshake request from ip address: {}, with username: {}".format(ip, user))
            return {"user": my_server_name, "ip": MYIP}
        except KeyError:
            return "invalid keys"
    else:
        return "403 - Unauthorized"


# TODO: refactor with sensor_server
def get_address_book(expected_entries):
    f = open('address_book.yml', 'r')
    book = yaml.load(f, Loader=SafeLoader)
    f.close()
    num_entries = len(book)
    logging.info("Found [" + str(num_entries) + "] entries in address_book.yml")
    return num_entries < expected_entries


async def ping_server(url, i):
    try:
        data = requests.post(url.format(i), timeout=1, json={"ip": MYIP, "user": my_server_name})
        reg_ip(data.json()['ip'], data.json()['user'])
        logging.info("Found " + data.json()['user'] + " at ip address: " + data.json()['ip'])
    except ConnectionError or InvalidSchema:
        logging.debug("Failed to find server at: 192.168.0." + str(i))


async def find_servers(numtry=0):
    url = "http://192.168.0.{}:8202/hello"
    addresses = [i for i in range(1, 64)]
    sub_addr = int(MYIP.split(".")[-1])
    addresses.remove(sub_addr)

    for i in tqdm(addresses):
        await ping_server(url, i)
        if get_address_book(2):
            break
    if get_address_book(2) and numtry < 2:
        print("Initiating another search for servers. Attempt: {}".format(numtry + 1))
        find_servers(numtry + 1)
    
    if numtry == 0:
        print("Search for servers complete!")


my_server_name = getpass.getuser()

log_fmt = '%(asctime)s : %(levelname)s - %(message)s'
logging.basicConfig(filename='directory.log', filemode='w', format=log_fmt, level=logging.DEBUG)

if __name__ == '__main__':
    MYIP = get_myip()
    explorer_thread = Thread(target=find_servers)
    explorer_thread.start()
    app.run(debug=True, host="0.0.0.0", port=8202, use_reloader=False)
