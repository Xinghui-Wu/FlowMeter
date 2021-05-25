from scapy.all import *
from scapy.layers.http import HTTP
from scapy.layers.inet import IP, TCP, UDP
from django.utils import timezone
import ipdb

from flow.models import flow, connection


class Sniffer:
    def __init__(self):
        super(Sniffer, self).__init__()
        self.index = None
        self.device = None
        self.ips = None
        self.db = ipdb.City('static/backend/ipipfree.ipdb')
        self.lock = None

    def initial_flow_table(self):
        flow.objects.all().delete()
        connection.objects.all().delete()

    def set_device_by_index(self, index):
        if self.index is None or self.index != index:
            self.index = index
            self.device = dev_from_index(index)
            self.ips = ['127.0.0.1']
            if self.device.ip not in self.ips:
                self.ips.append(self.device.ip)
            # print(self.ips)
            self.initial_flow_table()
            return True
        else:
            return False

    def is_localhost(self, ip):
        if ip in self.ips:
            return True
        cuts = ip.split('.')
        if int(cuts[0]) >= 224:
            return True
        return False

    def process_flow(self, packet):
        ip_packet = packet[IP]
        src = ip_packet.src
        dst = ip_packet.dst
        time = timezone.now()
        size = ip_packet.len
        upload = False
        download = False
        if self.is_localhost(src):
            upload = True
        if self.is_localhost(dst):
            download = True
        # Save flow.
        flow_item = flow(src=src, dst=dst, time=time, size=size, upload=upload, download=download)
        self.lock.acquire()
        flow_item.save()
        # Check connection.
        connections = connection.objects.filter(src=src, dst=dst, status=True).order_by('start_time')
        if connections.exists():
            # Check whether the number of connection is more than one.
            num = connections.count()
            connection_final = connections.first()
            self.lock.release()
            if num > 1:
                connection_final.all_size = 0
                for connection_item in connections:
                    connection_final.all_size += connection_item.all_size
                connection_final.end_time = time
                connection_final.all_size += size
                self.lock.acquire()
                connections.delete()
                connection_final.save()
                self.lock.release()
            elif num == 1:
                # Update end_time and all_size.
                new_end_time = time
                new_all_size = connection_final.all_size + size
                self.lock.acquire()
                connections.update(end_time=new_end_time, all_size=new_all_size)
                self.lock.release()
        else:
            self.lock.release()
            # Create new connection.
            # address
            address_query = dst
            if download and not upload:
                address_query = src
            address = None
            address_result = self.db.find(address_query, 'CN')
            if address_result[0] != '中国':
                address = address_result[0]
            else:
                address = address_result[1]
            # app
            app = ip_packet.proto
            if ip_packet.haslayer(TCP):
                tcp_packet = ip_packet[TCP]
                if upload:
                    app = tcp_packet.sport
                elif download:
                    app = tcp_packet.dport
            elif ip_packet.haslayer(UDP):
                udp_packet = ip_packet[UDP]
                if upload:
                    app = udp_packet.sport
                elif download:
                    app = udp_packet.dport
            # Save connection.
            connection_item = connection(src=src, dst=dst, start_time=time, end_time=time, all_size=size, status=True,
                                         address=address, app=app, upload=upload, download=download)
            self.lock.acquire()
            connection_item.save()
            self.lock.release()

    def sniff(self, lock):
        print('Start sniff.')
        self.lock = lock
        sniff(count=0, prn=self.process_flow, filter='ip', iface=self.device)
        print('End sniff.')
