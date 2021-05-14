#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bases.FrameworkServices.SimpleService import SimpleService
# Dependencies for ebpf
from bcc import BPF
# import pyroute2
# import time
# import sys

# flags = 0
'''
def usage():
    print("Usage: {0} [-S] <ifdev>".format(sys.argv[0]))
    print("       -S: use skb mode\n")
    print("       -H: use hardware offload mode\n")
    print("e.g.: {0} eth0\n".format(sys.argv[0]))
    exit(1)
'''

priority = 1

ORDER = [
    'RequestCount',
    'ReponseTime'
]

CHARTS = {
    'RequestCount': {
        'options': [None, 'The number of request', '', 'Request Count', 'xxx', 'line'],
        'lines': [
            # ['random1']
        ]
    },
    'ReponseTime': {
        'options': [None, 'response latency', '', 'Reponse Time', 'yyy', 'line'],
        'lines': [
            # ['random1']
        ]
    }
}

# bpf_text = """
# #include <uapi/linux/bpf.h>
# BPF_TABLE(percpu_array, uint32_t, long, metrics_map, 256);
# """

ret = "XDP_DROP"
ctxtype = "xdp_md"
offload_device = None
maptype = "percpu_array"
# load BPF program
b = BPF(text = """
#include <uapi/linux/bpf.h>
BPF_TABLE(MAPTYPE, uint32_t, long, metrics_map, 256);
int xdp_prog1(struct CTXTYPE *ctx) {
    // drop packets
    int rc = RETURNCODE; // let pass XDP_PASS or redirect to tx via XDP_TX
    long *value;
    uint32_t index = 0;
    value = metrics_map.lookup(&index);
    if (value)
        __sync_fetch_and_add(value, 1);
    return rc;
}
""", cflags=["-w", "-DRETURNCODE=%s" % ret, "-DCTXTYPE=%s" % ctxtype, "-DMAPTYPE=\"%s\"" % maptype], device=offload_device)

class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.num_lines = self.configuration.get('num_lines', 4)
        # load bpf program
        # self.b = BPF(src_file="eproxy_monitor.c", cflags=["-w", "-DRETURNCODE=%s" % ret, "-DCTXTYPE=%s" % ctxtype, "-DMAPTYPE=\"%s\"" % maptype], device=offload_device)
        # self.b = BPF(text = bpf_text)
        self.metrics_map = b.get_table("metrics_map")
        self.prev = [0] * 256


    @staticmethod
    def check():
        return True

    def get_data(self):
        data = dict()
        print("Get eBPF map data")
        delta = 0
        for k in self.metrics_map.keys():
            val = self.metrics_map[k].value if maptype == "array" else self.metrics_map.sum(k).value
            i = k.value
            if val:
                delta = val - self.prev[i]
                self.prev[i] = val
                # print("{}: {} pkt/s".format(i, delta))
        # Get the Pod IP
        # IP_list = []
        # num_lines = len(IP_list)
        for i in range(0, self.num_lines):
            # use IP_list[i] to lookup eBPF map
            # Get metrics.appRequestCountM
            # Get metrics.appResponseTimeInMsecM
            # dimension_id = '-'.join(['RequestCount', str(IP_list[i])])
            dimension_id = '-'.join(['RequestCount', str(i)])
            if dimension_id not in self.charts['RequestCount']:
                self.charts['RequestCount'].add_dimension([dimension_id])
            # data[dimension_id] = metrics.appRequestCountM
            data[dimension_id] = int(i * 10) + delta

            # dimension_id = '-'.join(['ReponseTime', str(IP_list[i])])
            dimension_id = '-'.join(['ReponseTime', str(i)])
            if dimension_id not in self.charts['ReponseTime']:
                self.charts['ReponseTime'].add_dimension([dimension_id])
            # data[dimension_id] = metrics.appResponseTimeInMsecM
            data[dimension_id] = int(i * 100) + delta

        return data
