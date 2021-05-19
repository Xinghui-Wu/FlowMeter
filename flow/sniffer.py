from scapy.all import *
from scapy.layers.inet import IP
from django.utils import timezone

from flow.models import flow


def save_flow(packet):
    ip_packet = packet[IP]
    flow_item = flow(src=ip_packet.src, dst=ip_packet.dst, time=timezone.now(), size=ip_packet.len, address='', app='')
    flow_item.save()


def initial_flow_table():
    flow.objects.all().delete()


class Sniffer:
    def __init__(self):
        super(Sniffer, self).__init__()
        self.index = None
        self.device = None

    def set_device_by_index(self, index):
        if self.index is None or self.index != index:
            self.index = index
            self.device = dev_from_index(index)
            initial_flow_table()

    def sniff(self, timeout=1):
        print('start sniff')
        sniff(count=0, prn=save_flow, filter='ip', timeout=timeout, iface=self.device)
