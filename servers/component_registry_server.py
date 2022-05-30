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
from yaspin import yaspin

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
            return {"user": MY_NAME, "ip": MYIP}
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
    return num_entries >= expected_entries


def ping_server(lower, upper, sub_addr):
    base_url = "http://192.168.0.{}:8202/hello"
    
    addresses = [i for i in range(lower, upper)]
    if sub_addr in addresses:
            addresses.remove(sub_addr)

    for i in addresses:
        try:
            if get_address_book(2):
                break
            data = requests.post(base_url.format(i), timeout=1, json={"ip": MYIP, "user": MY_NAME})
            reg_ip(data.json()['ip'], data.json()['user'])
            logging.info("Found " + data.json()['user'] + " at ip address: " + data.json()['ip'])
        except ConnectionError or InvalidSchema:
            logging.debug("Failed to find server at: 192.168.0." + str(i))


def find_servers(num_retries=0, num_threads=4, ip_limit=65, _try_number=0):
    print("Attempt number: {}".format(_try_number+1))

    sub_addr = int(MYIP.split(".")[-1])
    threadpool = []
    poolsize = ip_limit // 4
    pool_index = 1

    with yaspin(text="Searching...", color="yellow") as spinner:
        for _ in range(num_threads):
            threadpool.append(Thread(target=ping_server, args=(pool_index, pool_index + poolsize, sub_addr)))
            pool_index = pool_index + poolsize
        
        for i in range(num_threads):
            threadpool[i].start()

        for i in range(num_threads):
            threadpool[i].join()

    if get_address_book(2) and num_retries > _try_number:
        spinner.stop()
        find_servers(_try_number + 1)
    
    if _try_number == 0:
        print("Search for servers complete!")


log_fmt = '%(asctime)s : %(levelname)s - %(message)s'
logging.basicConfig(filename='directory.log', filemode='w', format=log_fmt, level=logging.DEBUG)


if __name__ == '__main__':
    MYIP = get_myip()
    MY_NAME = getpass.getuser()
    explorer_thread = Thread(target=find_servers)
    explorer_thread.start()
    app.run(debug=True, host="0.0.0.0", port=8052, use_reloader=False)
    
