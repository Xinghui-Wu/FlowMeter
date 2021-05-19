from django.contrib import admin
from flow.models import device, flow, connection

# Register your models here.
admin.site.register(device)
admin.site.register(flow)
admin.site.register(connection)
