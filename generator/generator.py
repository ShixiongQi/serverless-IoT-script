#!/usr/bin/python3

import argparse
import csv
import json
import os
import threading
import time

from collections import defaultdict
from datetime import datetime
from paho.mqtt import client, properties


def create_sensor(type, data, sensor, protocol, broker, speed=1):
    if protocol == 'mqtt':
        def on_connect(mqttc, userdata, rc):
            print("Connected with result code "+str(rc))
            if rc!=0 :
                mqttc.reconnect()

        mqtt_client = client.Client(protocol=client.MQTTv5)
        print(broker)
        mqtt_client.connect(broker, 30725)
        mqtt_client.on_connect = on_connect
        for d in data:
            user_property = properties.Properties(properties.PacketTypes.PUBLISH)
            propdict = {
                    'specversion': '1.0',
                    'type': type,
                    'source': d[0],
            }
            user_property.UserProperty = list(propdict.items())
            print(user_property.UserProperty)
            mqtt_client.publish(d[0], d[2], properties=user_property)
            time.sleep(d[1]/speed)


def run_agriculture(threads, protocol, broker, speed):
    root = 'data/caf_sensors/Hourly'
    for filename in os.listdir(root):
        with open(os.path.join(root, filename)) as f:
            data = []
            start = None
            next(f)
            for line in f:
                record = line.rstrip('\n').split('\t')
                if record[3] != 'NA':
                    timing = datetime.strptime('{} {}'.format(record[1], record[2]), '%m/%d/%Y %H:%M')
                    diff = 0 if start is None else (timing-start).total_seconds()
                    start = timing
                    data.append([record[0], diff, json.dumps(record[3:])])
            threads.append(threading.Thread(target=create_sensor, args=('agri', data, record[0], protocol, broker, speed, )))
        break


def run_parking(threads, protocol, broker, speed):
    with open('data/garage_data') as f:
        reader = csv.DictReader(f)
        structure = defaultdict(list)
        count, prev = {}, {}
        for line in reader:
            if '.' in line['updatetime']:
                timing = datetime.strptime(line['updatetime'], '%Y-%m-%d %H:%M:%S.%f')
            else:
                timing = datetime.strptime(line['updatetime'], '%Y-%m-%d %H:%M:%S')
            if line['garagecode'] in count:
                diff = abs(count[line['garagecode']] - int(line['gvehiclecount']))
                if diff != 0:
                    timediff = (timing - prev[line['garagecode']]).total_seconds()/diff
                    for i in range(diff):
                        structure[line['garagecode']].append([line['garagecode'], timediff, '1'])
            count[line['garagecode']] = int(line['gvehiclecount'])
            prev[line['garagecode']] = timing

        for park, info in structure.items():
            threads.append(threading.Thread(target=create_sensor, args=('parking', info, park, protocol, broker, speed)))
        
def run_motion(threads, protocol, broker, speed):
    with open('data/0114.txt') as f:
        prev = {}
        sensors = defaultdict(list)
        next(f)
        for line in f:
            record = line.split()
            now = datetime.fromtimestamp(int(record[1][1:-3]))
            if record[0] in prev:
                timediff = (now - prev[record[0]]).total_seconds()
                sensors[record[0]].append([record[0], timediff, '1'])
            else:
                sensors[record[0]].append([record[0], 0, '1'])
            end = datetime.fromtimestamp(int(record[2][1:-3]))
            timediff = (end - now).total_seconds()
            sensors[record[0]].append([record[0], timediff, '0'])
            prev[record[0]] = end

        for name, info in sensors.items():
            threads.append(threading.Thread(target=create_sensor, args=('motion', info, name, protocol, broker, speed,)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset', type=str, action='store')
    parser.add_argument('-p', '--protocol', type=str, action='store', default='mqtt')
    parser.add_argument('-b', '--broker', type=str, action='store', default='128.110.154.201')
    parser.add_argument('-s', '--speed', type=int, action='store', default=1.0)
    args = parser.parse_args()

    threads = []
    if args.dataset == 'agriculture':
        run_agriculture(threads, args.protocol, args.broker, args.speed)
    elif args.dataset == 'motion':
        run_motion(threads, args.protocol, args.broker, args.speed)
    elif args.dataset == 'parking':
        run_parking(threads, args.protocol, args.broker, args.speed)
    else:
        print('No such dataset: ', args.dataset)
        
    print('Running {} threads'.format(len(threads)))
    for thread in threads:
        thread.start()


if __name__ == '__main__':
    main()
