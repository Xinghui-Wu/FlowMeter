import json
import threading
import time

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from scapy.all import *

from flow.models import device, flow, connection
from flow.sniffer import Sniffer

sniffer = Sniffer()
write_lock = threading.Semaphore(1)


def connection_check(timeout, lock):
    while True:
        cut_time = timezone.now()
        time.sleep(timeout)
        cut_connections = connection.objects.filter(end_time__lt=cut_time, status=True)
        print('Close connection:', cut_connections.count())
        lock.acquire()
        cut_connections.update(status=False)
        lock.release()


# Create your views here.
def flow_view(request):
    device.objects.all().delete()
    for item in conf.ifaces.data:
        dev = conf.ifaces.data[item]
        device_item = device(index=dev.index, description=dev.description)
        device_item.save()
    device_list = device.objects.all().order_by('index')
    return render(request, 'flow.html', {'device_list': device_list})


def select_device(request):
    index = request.GET.get('device_index')
    sniffer.set_device_by_index(index)
    result = {'index': index}
    sniff_thread = threading.Thread(target=sniffer.sniff, args=(write_lock,))
    connection_check_thread = threading.Thread(target=connection_check, args=(1, write_lock,))
    sniff_thread.start()
    connection_check_thread.start()
    return HttpResponse(json.dumps(result))


def sniff(request):
    return HttpResponse()


def get_flow(request):
    pass


def address_analyze(request):
    pass


def name_analyze(request):
    pass


def burst_analyze(request):
    pass
