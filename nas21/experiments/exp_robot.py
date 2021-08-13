#!/usr/bin/env python3
import socket, os, argparse

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--addr', action='store', type=str)
parser.add_argument('-p', '--port', action='store', type=int)
parser.add_argument('-t', '--time', action='store', type=str)
parser.add_argument('-n', '--node', action='store', type=str)
args = parser.parse_args()

HOST = args.addr  # The server's hostname or IP address
PORT = args.port        # The port used by the server
print("Host: {}, Port: {}".format(HOST, PORT))

if args.node == 'master': # socket client, sending requests to server to run cpu_measure.sh
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(args.time.encode())
        data = s.recv(1024).decode("utf-8")
    print("Printout from worker: \n", data)
else: # socket server, waiting for requests and run cpu_measure.sh
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                time = conn.recv(1024).decode("utf-8")
                if not time:
                    break
                return_value = os.popen("./cpu_measure.sh " + time).read()
                conn.send(return_value.encode())