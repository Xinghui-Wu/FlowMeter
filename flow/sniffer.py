from scapy.all import *
from scapy.layers.inet import IP
from django.utils import timezone
import ipdb

from flow.models import flow


class Sniffer:
    def __init__(self):
        super(Sniffer, self).__init__()
        self.index = None
        self.device = None
        self.db = ipdb.City('static/backend/ipipfree.ipdb')
        # print(self.db.languages())

    def set_device_by_index(self, index):
        if self.index is None or self.index != index:
            self.index = index
            self.device = dev_from_index(index)
            self.initial_flow_table()

    def save_flow(self, packet):
        ip_packet = packet[IP]
        flow_item = flow(src=ip_packet.src, dst=ip_packet.dst, time=timezone.now(), size=ip_packet.len, address='',
                         app='')
        print(self.db.find(ip_packet.dst, 'CN'))
        flow_item.save()

    def initial_flow_table(self):
        flow.objects.all().delete()

    def sniff(self, timeout=1):
        print('start sniff')
        sniff(count=0, prn=self.save_flow, filter='ip', timeout=timeout, iface=self.device)
