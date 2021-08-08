import argparse
import datetime
import requests
import os
import threading
import time

from paho.mqtt import client, properties

prefix = os.getcwd() + '/merl/01'
base = 14

def generate(path, speed, addr, port):
    s, e = [], []
    begin = None
    def on_connect(mqttc, userdata, flags, rc, properties):
        print("Connected with result code ", rc)
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Reconnected to MQTT Broker")
            mqttc.reconnect()

    mqtt_client = client.Client(protocol=client.MQTTv5)
    # mqtt_client = client.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(addr, port=port)
    print('Try to on_connect')

    mqtt_client.loop_start()
    print('MQTT Client Loop started')
    with open(path, 'r') as f:
        for line in f:
            _, start_unix, stop_unix, _ = line.split()
            if begin is not None:
               s.append(int(start_unix) - begin)
            else:
                begin = int(start_unix)
            e.append(int(stop_unix) - begin)
            # print(int(start_unix) - begin, int(stop_unix) - begin)
    print("Dataset initialization done")
    # 2-way merge
    res = []
    ptr1, ptr2 = 0, 0
    while ptr1 < len(s) and ptr2 < len(e):
        if s[ptr1] <= e[ptr2]:
            res.append(0 if len(res) == 0 else s[ptr1] - res[-1])
            ptr1 += 1
        else:
            res.append(0 if len(res) == 0 else e[ptr2] - res[-1])
            ptr2 += 1

    while ptr1 < len(s):
        res.append(0 if len(res) == 0 else s[ptr1] - res[-1])
        ptr1 += 1

    while ptr2 < len(e):
        res.append(0 if len(res) == 0 else e[ptr2] - res[-1])
        ptr2 += 1

    sensor, event_type = 'm', 'motion'
    print("length of res: {}".format(len(res)))
    for r in res:
        print(r)
        # time.sleep(r/speed)
        time.sleep(1)
        # Make Request
        attributes = {
                'type': event_type,
                'source': 'com.example.sensor/'+sensor,
        }
        user_property = properties.Properties(properties.PacketTypes.PUBLISH)
        user_property.UserProperty = list(attributes.items())
        mqtt_client.publish(event_type, '123', properties=user_property)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', action='store', type=str, default='10.244.1.61')
    parser.add_argument('-p', '--port', action='store', type=int, default=1883)
    parser.add_argument('-n', '--number', action='store', type=int)
    parser.add_argument('-s', '--speed', action='store', type=int, default=1)
    args = parser.parse_args()

    if args.number:
        if args.number > 7:
            parser.error('Must be less than 7')
        else:
            threads = []
            for i in range(args.number):
                th = threading.Thread(target=generate, args=('{}{}.txt'.format(prefix, str(base+i)),args.speed, args.addr,args.port,))
                th.start()
                threads.append(th)
            for th in threads:
                th.join()
    else:
        generate(prefix+'14.txt', args.speed, args.addr, args.port)
               
if __name__  ==  '__main__':
    main()
