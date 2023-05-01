# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 16:46:43 2023

@author: Aicenter01
"""
import time
from datetime import datetime
import random
from sys import exit

import global_var
import influxdb_client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

bucket = "mqtt_test"
org = "AICenter"
token = "SiypSP65QQTgYRePo0Wg-lNGyzona_02vl4ebV8H9Q28pxHFlWIOTlS-RgPPwzntJF8wpxXCLTMrfXKo0Yx1aw=="
#token = "AGvkvMIW_-1TrSEsbk-yizvyudVE3lFDx2QjugnQ8hNXEun5yY1ORhbDI_SUrTw3Aqh5g-3VCzTT0dVnwv1I0Q=="
url="http://localhost:8086"

client = InfluxDBClient(
   url=url,
   token=token,
   org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)

while True:
    
    start = time.monotonic()
    ecg = random.randint(30, 150)
    ppg = random.randint(30, 150)

    delta = time.monotonic() - start
    print("time : ", delta)
    try:
        if delta < 0.01:
            time.sleep(0.01 - delta)
        write_api.write(bucket=bucket, org=org, record=[Point("test2").tag("room", 1).field("ECG", ecg).field("PPG", ppg)])
        #ecg_list.append(ecg)
        #ppg_list.append(ppg)
        
    except KeyboardInterrupt:
        exit()


#p = influxdb_client.Point("test2").tag("room", 1).field("ECG", 5).field("PPG", 4).field("ECG", 6).field("PPG", 15)

#多項參數寫入
#write_api.write(bucket=bucket, org=org, record=[Point("test2").tag("room", 1).field("ECG", 15).field("PPG", 87), Point("test2").tag("room", 1).field("ECG", 19).field("PPG", 88)])
def write_measurements(device_id):
    influxdb_client = InfluxDBClient(url=config.get('APP', 'INFLUX_URL'),
                                     token=config.get('APP', 'INFLUX_TOKEN'),
                                     org=config.get('APP', 'INFLUX_ORG'))
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    virtual_device = Sensor()
    coord = virtual_device.geo()
    point = Point("environment") \
        .tag("device", device_id) \
        .tag("TemperatureSensor", "virtual_bme280") \
        .tag("HumiditySensor", "virtual_bme280") \
        .tag("PressureSensor", "virtual_bme280") \
        .field("Temperature", virtual_device.generate_measurement()) \
        .field("Humidity", virtual_device.generate_measurement()) \
        .field("Pressure", virtual_device.generate_measurement()) \
        .field("Lat", coord['latitude']) \
        .field("Lon", coord['latitude']) \
        .time(datetime.utcnow())
    print(f"Writing: {point.to_line_protocol()}")
    client_response = write_api.write(bucket=config.get('APP', 'INFLUX_BUCKET'), record=point)
    # write() returns None on success
    if client_response is None:
        # TODO Maybe also return the data that was written
        return device_id
    # Return None on failure
    return None