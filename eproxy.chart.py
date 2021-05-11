# -*- coding: utf-8 -*-

from bases.FrameworkServices.SimpleService import SimpleService

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


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.num_lines = self.configuration.get('num_lines', 4)
        # load bpf program
        # self.b = BPF(src_file="eproxy_monitor.c", cflags=["-w", "-DRETURNCODE=%s" % ret, "-DCTXTYPE=%s" % ctxtype, "-DMAPTYPE=\"%s\"" % maptype], device=offload_device)

    @staticmethod
    def check():
        return True

    def get_data(self):
        data = dict()

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
            data[dimension_id] = int(i * 10) +10

            # dimension_id = '-'.join(['ReponseTime', str(IP_list[i])])
            dimension_id = '-'.join(['ReponseTime', str(i)])
            if dimension_id not in self.charts['ReponseTime']:
                self.charts['ReponseTime'].add_dimension([dimension_id])
            # data[dimension_id] = metrics.appResponseTimeInMsecM
            data[dimension_id] = int(i * 100) + 10

        return data
