import argparse
import datetime
import requests
import os
import threading
import time

from paho.mqtt import client, properties
from threading import Thread
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

counter = 0
delay = []
def on_connect(mqttc, userdata, flags, rc, properties):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Reconnected to MQTT Broker")
        mqttc.reconnect()

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', action='store', type=str, default='10.244.1.61')
parser.add_argument('-m', '--mqttport', action='store', type=int, default=1883)
parser.add_argument('--httpport', action='store', type=int, default=65432)
args = parser.parse_args()

addr = args.addr
port = args.mqttport

mqtt_client = client.Client(protocol=client.MQTTv5)
mqtt_client.on_connect = on_connect
mqtt_client.connect(addr, port=port)
mqtt_client.loop_start()
sensor, event_type = 'm', 'motion'
attributes = {
        'type': event_type,
        'source': 'com.example.sensor/'+sensor,
}
user_property = properties.Properties(properties.PacketTypes.PUBLISH)
user_property.UserProperty = list(attributes.items())

class ackHandler(BaseHTTPRequestHandler):
    def setup(self):
        BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(2)
    def do_GET(self):
        global counter
        counter = counter + 1
        mqtt_client.publish(event_type, args.httpport, properties=user_property)
        delay.append(time.time())
        #time.sleep(0.0012)

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ("10.10.1.1", args.httpport)
    httpd = server_class(server_address, ackHandler)

    mqtt_client.publish(event_type, args.httpport, properties=user_property)
    start_ticks = time.time()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        end_ticks = time.time()
        print("RPS: ", counter/(end_ticks - start_ticks))
        tpr = []
        for i in range(1, len(delay)):
            tpr.append(delay[i] - delay[i-1])
        print(sum(tpr)/len(tpr))

def main():
    try:
        run()      
    except KeyboardInterrupt:
        print("Stop the ack handler")

if __name__  ==  '__main__':
    main()
