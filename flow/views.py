import json
import threading
import time

from django.db.models import Sum
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
        lock.acquire()
        cut_connections = connection.objects.filter(end_time__lt=cut_time, status=True)
        cut_connections.update(status=False)
        lock.release()
        print('Close connection:', cut_connections.count())


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
    result = {'index': index}
    if sniffer.set_device_by_index(index):
        sniff_thread = threading.Thread(target=sniffer.sniff, args=(write_lock,))
        connection_check_thread = threading.Thread(target=connection_check, args=(60, write_lock,))
        sniff_thread.start()
        connection_check_thread.start()
    return HttpResponse(json.dumps(result))


def sniff(request):
    return HttpResponse()


old_time = None


def get_flow(request):
    # Make time slice.
    global old_time
    now_time = timezone.datetime.now()
    if old_time is None:
        old_time = now_time - timezone.timedelta(seconds=1)
    # Make up results.
    # upload_now
    upload_now = 0
    write_lock.acquire()
    up_flows = flow.objects.filter(time__range=(old_time, now_time), upload=True).order_by('time')
    for up_flow in up_flows:
        upload_now += up_flow.size
    write_lock.release()
    # download_now
    download_now = 0
    write_lock.acquire()
    down_flows = flow.objects.filter(time__range=(old_time, now_time), download=True).order_by('time')
    for down_flow in down_flows:
        download_now += down_flow.size
    write_lock.release()
    # upload_history
    upload_history = 0
    write_lock.acquire()
    upload_history_result = flow.objects.filter(upload=True)
    for item in upload_history_result:
        upload_history += item.size
    write_lock.release()
    # download_history
    download_history = 0
    write_lock.acquire()
    download_history_result = flow.objects.filter(download=True)
    for item in download_history_result:
        download_history += item.size
    write_lock.release()
    result = {'upload_flows': None,
              'download_flows': None,
              'upload_now': upload_now,
              'download_now': download_now,
              'upload_history': upload_history,
              'download_history': download_history}
    print('Response result:', 'get_flow')
    old_time = now_time
    return HttpResponse(json.dumps(result))


def address_analyze(request):
    # upload_address
    upload_address = {}
    write_lock.acquire()
    upload_address_results = connection.objects.values('address').filter(upload=True).annotate(
        all_all_size=Sum('all_size'))
    for upload_address_result in upload_address_results:
        upload_address.setdefault(upload_address_result['address'], upload_address_result['all_all_size'])
    write_lock.release()
    # download_address
    download_address = {}
    write_lock.acquire()
    download_address_results = connection.objects.values('address').filter(download=True).annotate(
        all_all_size=Sum('all_size'))
    for download_address_result in download_address_results:
        download_address.setdefault(download_address_result['address'], download_address_result['all_all_size'])
    write_lock.release()
    # Make up result.
    result = {'upload': upload_address,
              'download': download_address}
    print('Response result:', 'address')
    return HttpResponse(json.dumps(result))


def name_analyze(request):
    # upload_app
    upload_app = {}
    write_lock.acquire()
    upload_app_results = connection.objects.values('app').filter(upload=True).annotate(
        all_all_size=Sum('all_size'))
    for upload_app_result in upload_app_results:
        upload_app.setdefault(upload_app_result['app'], upload_app_result['all_all_size'])
    write_lock.release()
    # download_app
    download_app = {}
    write_lock.acquire()
    download_app_results = connection.objects.values('app').filter(download=True).annotate(
        all_all_size=Sum('all_size'))
    for download_app_result in download_app_results:
        download_app.setdefault(download_app_result['app'], download_app_result['all_all_size'])
    write_lock.release()
    # Make up result.
    result = {'upload': upload_app,
              'download': download_app}
    print('Response result:', 'name')
    return HttpResponse(json.dumps(result))


def burst_analyze(request):
    size_margin = 1024
    time_margin_min = 1
    time_margin_max = 10
    max_index = 30
    burst = {}
    index = 0
    write_lock.acquire()
    burst_connections = connection.objects.filter(all_size__gt=size_margin)
    for item in burst_connections:
        if item.start_time + timezone.timedelta(
                seconds=time_margin_min) < item.end_time and item.start_time + timezone.timedelta(
            seconds=time_margin_max) > item.end_time:
            if index < max_index:
                burst.setdefault(index,
                                 [item.src, item.dst, item.all_size, item.status, item.address, item.app, item.upload,
                                  item.download])
                index += 1
                if index == max_index:
                    break
    write_lock.release()
    result = {'burst': burst}
    print('Response result:', 'burst')
    return HttpResponse(json.dumps(result))
