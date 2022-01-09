import os
import socket
import pickle
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
    pk = serialization.load_pem_private_key(f.read(), password=bytes(os.environ['RPI_SERVER_PWD'], 'utf-8'))
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


def probe_dht11(dht_sensor, previous_temp, previous_humidity):
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
    except RuntimeError or OverflowError as err:
        # this error occurs a lot so don't log it.
        # No solution currently exists according to manufacturer.
        temperature = previous_temp
        humidity = previous_humidity
    except OverflowError as ofe:
        temperature = previous_temp
        humidity = previous_humidity
        logging.error("Inside temp sensor failed - " + str(ofe))
    except Exception as e:
        temperature = previous_temp
        humidity = previous_humidity
        print(str(e))
    return temperature, humidity


def get_sensor_readings():
    global previous_ot
    global previous_oh
    global previous_it
    global previous_ih
    payload = SensorData()
    ts = time.ctime()
    payload.set_timestamp(ts)

    outside_temp, outside_humidity = probe_dht11(outside_dht_sensor, previous_ot, previous_oh)
    inside_temp, inside_humidity = probe_dht11(inside_dht_sensor, previous_it, previous_ih)
    previous_ot, previous_oh, previous_it, previous_ih = outside_temp, outside_humidity, inside_temp, inside_humidity

    payload.set_outside_temp(outside_temp)
    payload.set_outside_humidity(outside_humidity)

    payload.set_inside_temp(inside_temp)
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


def retry_protocol(packet: SensorData):
    num_tries = 3
    delay = 3 * 60
    is_success = False
    for i in range(1, num_tries + 1):
        time.sleep(delay)
        is_success = save2db(packet, retry=False, try_num=i)
        if is_success:
            logging.info("Reconnection to MongoDB server successful at attempt {}".format(i))
            break
    if not is_success:
        f = open('lost-data.txt', 'a+')
        f.write(str(packet.toJSON()) + "\n")
        f.close()


def save2db(packet: SensorData, retry, try_num=0):
    mongo_connection = get_db_connection_str()
    client = MongoClient(mongo_connection, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command('ping')
        greenhouse_db = client["GreenHouse-v1"]
        test_collection = greenhouse_db["test"]
        test_collection.insert_one(packet.toJSON())
        return True
    except ServerSelectionTimeoutError:
        logging.error("MongoDB Server could not establish connection | try num: {}".format(try_num))
        if retry:
            logging.info("Reconnection thread started")
            reconnect_thread = Thread(target=retry_protocol, args=[packet])
            reconnect_thread.start()
        return False


def run_data_acquisition():
    global data_packet
    while True:
        data_packet = get_sensor_readings()
        if is_time_2_store(db_freq, sample_freq):
            sampling_delay(sample_freq)
            data_packet = get_sensor_readings()
            save2db(data_packet.get_og_object(), retry=True)
        sampling_delay(sample_freq)


def run_server():
    global data_packet
    while True:
        client, addr = server_socket.accept()
        serialized_dp = pickle.dumps(data_packet)
        client.send(serialized_dp)
        client.close()


log_fmt = '%(asctime)s : %(levelname)s - %(message)s'
logging.basicConfig(filename='rpi-sensors.log', filemode='w', format=log_fmt, level=logging.INFO)

server_socket = socket.socket()
server_socket.bind(("", SSSConstants.port))
server_socket.listen(SSSConstants.num_expect_conn)

private_key = get_pk()
address_book = get_address_book()

inside_dht_sensor = adafruit_dht.DHT11(17)
outside_dht_sensor = adafruit_dht.DHT11(18)

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
