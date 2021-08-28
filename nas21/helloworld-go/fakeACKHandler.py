import argparse
import datetime
import requests
import os
import threading
import time

from http.server import HTTPServer, BaseHTTPRequestHandler

counter = 0

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', action='store', type=str, default='10.244.1.61')
parser.add_argument('--httpport', action='store', type=int, default=65432)
args = parser.parse_args()

addr = args.addr

class ackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global counter
        counter = counter + 1
        time.sleep(0.00001)

def run(server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
    server_address = ("10.10.1.1", args.httpport)
    httpd = server_class(server_address, ackHandler)

    start_ticks = time.time()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        end_ticks = time.time()
        print("RPS: ", counter/(end_ticks - start_ticks))

def main():
    try:
        run()      
    except KeyboardInterrupt:
        print("Stop the fake ack handler")

if __name__  ==  '__main__':
    main()