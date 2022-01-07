import os
import socket
import pickle
import sys
import time
import numpy as np
import yaml
import logging

from threading import Thread
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from yaml.loader import SafeLoader

from configurations import SSSConstants, SensorData, SignedObject
import adafruit_dht


def get_pk():
    f = open("rpi-data-server.pem", 'rb')
    pk = serialization.load_pem_private_key(f.read(), password=bytes(sys.argv[1], 'utf-8'))
    f.close()
    return pk


def sign_payload(payload):
    byte_stream = pickle.dumps(payload)
    signature = private_key.sign(
        byte_stream,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def get_sensor_readings():
    global previous_ot
    global previous_oh
    global previous_it
    global previous_ih
    payload = SensorData()
    ts = time.ctime()
    payload.set_timestamp(ts)
    try:
        outside_temp = outside_dht_sensor.temperature
        previous_ot = outside_temp
    except RuntimeError:
        outside_temp = previous_ot
    payload.set_outside_temp(outside_temp)

    try:
        outside_humidity = outside_dht_sensor.humidity
        previous_oh = outside_humidity
    except RuntimeError:
        outside_humidity = previous_oh
    payload.set_outside_humidity(outside_humidity)

    try:
        inside_temp = inside_dht_sensor.temperature
        previous_it = inside_temp
    except RuntimeError:
        inside_temp = previous_it
    payload.set_inside_temp(inside_temp)

    try:
        inside_humidity = inside_dht_sensor.humidity
        previous_ih = inside_humidity
    except RuntimeError:
        inside_humidity = previous_ih
    payload.set_inside_humidity(inside_humidity)
    payload_signature = sign_payload(payload)
    return SignedObject(payload, payload_signature)


def calculate_sleeptime(curr_time, freq):
    return freq - curr_time % freq


def sampling_delay(freq):
    boot_time = time.ctime()
    t0 = int(boot_time[17:19])
    sleep_time = calculate_sleeptime(t0, freq)
    time.sleep(sleep_time)


def is_time_2_store(freq, sf):
    boot_time = time.ctime()
    curr_time = int(boot_time[14:16]) * 60 + int(boot_time[17:19])
    time_delta = calculate_sleeptime(curr_time, freq)
    return time_delta <= sf * 1.5


def get_address_book():
    f = open('address_book.yml', 'r')
    book = yaml.load(f, Loader=SafeLoader)
    f.close()
    return book


def get_db_connection_str():
    server_usr = "server44"
    pwd = os.environ['MONGO_PWD']
    addr = address_book['mongo_server']
    return "mongodb://{}:{}@{}".format(server_usr, pwd, addr)


def save2db(packet: SensorData):
    mongo_connection = get_db_connection_str()
    client = MongoClient(mongo_connection, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command('ping')
        greenhouse_db = client["GreenHouse-v1"]
        test_collection = greenhouse_db["test"]
        test_collection.insert_one(packet.toJSON())
    except ServerSelectionTimeoutError:
        logging.error("MongoDB Server could not establish connection")


def run_data_acquisition():
    global data_packet
    while True:
        data_packet = get_sensor_readings()
        if is_time_2_store(db_freq, sample_freq):
            sampling_delay(sample_freq)
            data_packet = get_sensor_readings()
            save2db(data_packet.get_og_object())
        sampling_delay(sample_freq)


def run_server():
    global data_packet
    client, addr = server_socket.accept()
    while True:
        client.recv(1024)
        serialized_dp = pickle.dumps(data_packet)
        client.send(serialized_dp)


log_fmt = '%(asctime)s : %(levelname)s - %(message)s'
logging.basicConfig(filename='rpi-sensors.log', filemode='w', format=log_fmt, level=logging.INFO)

server_socket = socket.socket()
server_socket.bind(("", SSSConstants.port))
server_socket.listen(SSSConstants.num_expect_conn)

private_key = get_pk()
address_book = get_address_book()

outside_dht_sensor = adafruit_dht.DHT11(17)
inside_dht_sensor = adafruit_dht.DHT11(18)

db_freq = 15 * 60
sample_freq = 6

previous_ot = 0
previous_oh = 0
previous_it = 0
previous_ih = 0

data_packet = None

if __name__ == "__main__":
    ss_thread = Thread(target=run_server)
    da_thread = Thread(target=run_data_acquisition)
    ss_thread.start()
    da_thread.start()
