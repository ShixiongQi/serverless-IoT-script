import argparse
import datetime
import requests
import os
import threading
import time

from cloudevents.http import CloudEvent, to_structured
from paho.mqtt import client, properties

prefix = os.getcwd() + '/merl/01'
base = 14

def generate(path, speed, addr, port, day, http):
    s, e = [], []
    begin = None
    def on_connect(mqttc, userdata, flags, rc, properties):
        # print("Connected with result code ", rc)
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Reconnected to MQTT Broker")
            mqttc.reconnect()

    if not http:
        mqtt_client = client.Client(protocol=client.MQTTv5)
        # mqtt_client = client.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.connect(addr, port=port)
        # print('Try to on_connect')

        mqtt_client.loop_start()
    # print('MQTT Client Loop started')
    with open(path, 'r') as f:
        for line in f:
            _, start_unix, stop_unix, _ = line.split()
            s.append(start_unix)
            # print(int(start_unix) - begin, int(stop_unix) - begin)
    # print("Dataset initialization done")
    # print("Total {} records".format(len(s)))
    # print("Average records per second: {}".format(float(len(s)/1728000))) # 20 days in total
    # print("Use {} day(s) data".format(day))
    s.sort()
    # 2-way merge
    res = []
    begin = int(s[0])
    for u in s:
        detal_t = float(int(u) - begin)/1000
        if detal_t < 86400 * int(day):
            res.append(detal_t)

    sleep_t = []
    for i in range(0, len(res)):
        if i == 0:
            sleep_t.append(res[i])
        else:
            sleep_t.append(res[i]-res[i-1])
    sensor, event_type = 'm', 'motion'
    print("Total {} events within {} day(s). The average event generation rate is {} events/second".format(len(res), day, len(res)/(86400 * int(day))))
    print("Event rate (after scaling): {}".format( len(res)/(86400 * int(day)) * speed ))
    print("Time to complete all the events: {} seconds".format((86400 * int(day)) / speed))
    print("\n* * * * * * * EVENT GENERATION BEGIN, remember starting your experiment robot (master)!! * * * * * *")

    def post(addr, port, event):
        headers, body = to_structured(event, data_marshaller = str)
        addr = os.getenv('INGRESS_HOST', addr)
        port = os.getenv('INGRESS_PORT', port)
        headers['Host'] = 'helloworld-go.default.example.com'
        r = requests.post('http://{}:{}'.format(addr, port), data=body, headers=headers)

    for r in sleep_t:
        # print(r)
        time.sleep(r/speed)
        attributes = {
                'type': event_type,
                'source': 'com.example.sensor/'+sensor,
        }
        if http:
            event = CloudEvent(attributes, '123')
            th = threading.Thread(target=post, args=(addr, port, event,))
            th.daemon = True
            th.start()
        else:
            user_property = properties.Properties(properties.PacketTypes.PUBLISH)
            user_property.UserProperty = list(attributes.items())
            mqtt_client.publish(event_type, '123', properties=user_property)
    exit("All the events in {} day(s) have been sent out".format(day))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', action='store', type=str, default='10.244.1.61')
    parser.add_argument('-p', '--port', action='store', type=int, default=1883)
    parser.add_argument('-n', '--number', action='store', type=int)
    parser.add_argument('-s', '--speed', action='store', type=int, default=1)
    parser.add_argument('-d', '--day', action='store', type=int, default=1)
    parser.add_argument('--http', action='store_true', default=False)
    args = parser.parse_args()

    if args.number:
        if args.number > 7:
            parser.error('Must be less than 7')
        else:
            threads = []
            for i in range(args.number):
                th = threading.Thread(target=generate, args=('{}{}.txt'.format(prefix, str(base + i)), args.speed, args.addr, args.port, args.day, args.http))
                th.start()
                threads.append(th)
            for th in threads:
                th.join()
    else:
        generate(prefix+'14.txt', args.speed, args.addr, args.port, args.day, args.http)
               
if __name__  ==  '__main__':
    main()
