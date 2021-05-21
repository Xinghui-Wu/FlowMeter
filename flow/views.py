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
        lock.release()
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
    connection_check_thread = threading.Thread(target=connection_check, args=(60, write_lock,))
    sniff_thread.start()
    connection_check_thread.start()
    return HttpResponse(json.dumps(result))


def sniff(request):
    return HttpResponse()


def get_flow(request):
    # Make time slice.
    last_max = 30
    step = 5
    now_time = timezone.datetime.now()
    last_time = now_time - timezone.timedelta(seconds=last_max)
    temp_time = now_time - timezone.timedelta(seconds=1)
    time_cuts = [last_time + timezone.timedelta(seconds=i) for i in range(0, last_max + 1, step)]
    # Get flow data.
    write_lock.acquire()
    up_flows = flow.objects.filter(time__range=(time_cuts[0], time_cuts[-1]), upload=True).order_by('time')
    down_flows = flow.objects.filter(time__range=(time_cuts[0], time_cuts[-1]), download=True).order_by('time')
    write_lock.release()
    # Make up results.
    # upload_flows & upload_now
    upload_flows = {}
    upload_now = 0
    index = 0
    all_size = 0
    for up_flow in up_flows:
        if up_flow.time < time_cuts[index + 1]:
            all_size += up_flow.size
        else:
            upload_flows.setdefault(str(index), all_size)
            index += 1
            all_size = up_flow.size
        if up_flow.time > temp_time:
            upload_now += up_flow.size
    upload_flows.setdefault(str(index), all_size)
    # download_flows & download_now
    download_flows = {}
    download_now = 0
    index = 0
    all_size = 0
    for down_flow in down_flows:
        if down_flow.time < time_cuts[index + 1]:
            all_size += down_flow.size
        else:
            download_flows.setdefault(str(index), all_size)
            index += 1
            all_size = down_flow.size
        if down_flow.time > temp_time:
            download_now += down_flow.size
    download_flows.setdefault(str(index), all_size)
    # upload_history
    write_lock.acquire()
    upload_history_result = flow.objects.filter(upload=True)
    write_lock.release()
    upload_history = 0
    for item in upload_history_result:
        upload_history += item.size
    # download_history
    write_lock.acquire()
    download_history_result = flow.objects.filter(download=True)
    write_lock.release()
    download_history = 0
    for item in download_history_result:
        download_history += item.size
    result = {'upload_flows': upload_flows,
              'download_flows': download_flows,
              'upload_now': upload_now,
              'download_now': download_now,
              'upload_history': upload_history,
              'download_history': download_history}
    print('Response result:', 'get_flow')
    return HttpResponse(json.dumps(result))


def address_analyze(request):
    # upload_address
    write_lock.acquire()
    upload_address_results = connection.objects.values('address').filter(upload=True).annotate(
        all_all_size=Sum('all_size'))
    write_lock.release()
    upload_address = {}
    for upload_address_result in upload_address_results:
        upload_address.setdefault(upload_address_result['address'], upload_address_result['all_all_size'])
    # download_address
    write_lock.acquire()
    download_address_results = connection.objects.values('address').filter(download=True).annotate(
        all_all_size=Sum('all_size'))
    write_lock.release()
    download_address = {}
    for download_address_result in download_address_results:
        download_address.setdefault(download_address_result['address'], download_address_result['all_all_size'])
    # Make up result.
    result = {'upload': upload_address,
              'download': download_address}
    print('Response result:', 'address')
    return HttpResponse(json.dumps(result))


def name_analyze(request):
    # upload_app
    write_lock.acquire()
    upload_app_results = connection.objects.values('app').filter(upload=True).annotate(
        all_all_size=Sum('all_size'))
    write_lock.release()
    upload_app = {}
    for upload_app_result in upload_app_results:
        upload_app.setdefault(upload_app_result['app'], upload_app_result['all_all_size'])
    # download_app
    write_lock.acquire()
    download_app_results = connection.objects.values('app').filter(download=True).annotate(
        all_all_size=Sum('all_size'))
    write_lock.release()
    download_app = {}
    for download_app_result in download_app_results:
        download_app.setdefault(download_app_result['app'], download_app_result['all_all_size'])
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
    write_lock.acquire()
    burst_connections = connection.objects.filter(all_size__gt=size_margin)
    write_lock.release()
    burst = {}
    index = 0
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
    result = {'burst': burst}
    print('Response result:', 'burst')
    return HttpResponse(json.dumps(result))
