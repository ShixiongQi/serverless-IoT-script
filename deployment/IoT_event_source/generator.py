import datetime
import json
import os
import queue
import requests
import sys
import time
import threading
from cloudevents.http import CloudEvent, to_structured

q = queue.Queue()
url = os.getenv('K_SINK')


def sending_out():
    count = 0
    def post(event,data):
        headers, body = to_structured(event, data_marshaller = str)
        print(body)
        body = json.loads(body.decode())
        headers['Ce-Specversion'] = body.get('specversion')
        headers['Ce-Source'] = body.get('source')
        headers['Ce-Type'] = body.get('type')
        headers['Ce-Id'] = body.get('id')
        headers['ce-time'] = body.get('time')
        headers['content-type'] = 'application/json'
        data['Time'] = body.get('time')
        print(data['Time'])
        r = requests.post(url, data=json.dumps(data), headers=headers)
        print(r)

    while True:
        sensor, reading, timediff = q.get()
        q.task_done()
        print(count, ' ', sensor, ' ', reading, ' ',timediff)
        count += 1
        sec = timediff.total_seconds()
        if sec > 0:
            time.sleep(sec/10)
        if (sensor[0] == 'T'):
            event_type = 'temp'
        elif (sensor[0] == 'M'):
            event_type = 'motion'
        elif (sensor[0] == 'D'):
            event_type = 'door'
        else:
            continue

        attributes = {
                'type': event_type,
                'source': 'com.example.sensor/'+sensor,
        }
        data = {"Sensor": sensor, "Message": reading}
        event = CloudEvent(attributes, data)
        th = threading.Thread(target=post, args=(event,data,))
        th.daemon = True
        th.start()


def parse(data_path):
    today, prev = None, None

    with open(data_path, 'r') as f:
        for line in f:
            date, time, sensor, event = line.split()[0:4]
            time = datetime.datetime.strptime(time, '%H:%M:%S.%f')
            if today is None:
                today = date
            elif date != today:
                return

            if prev is None:
                prev = time

            timediff = time - prev
            if timediff.total_seconds() > 5:
                timediff = datetime.timedelta(seconds=5)

            prev = time
            q.put((sensor, event, timediff))
                

if __name__ == '__main__':
    threading.Thread(target=sending_out).start()
    parse(sys.argv[1])
