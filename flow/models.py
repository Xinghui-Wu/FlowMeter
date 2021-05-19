from django.db import models


# Create your models here.
class device(models.Model):
    index = models.PositiveIntegerField()
    description = models.CharField(max_length=256)


class flow(models.Model):
    src = models.GenericIPAddressField(db_index=True)
    dst = models.GenericIPAddressField(db_index=True)
    time = models.DateTimeField()
    size = models.PositiveIntegerField()
    address = models.CharField(max_length=64)
    app = models.CharField(max_length=256)


class connection(models.Model):
    src = models.GenericIPAddressField(db_index=True)
    dst = models.GenericIPAddressField(db_index=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    all_size = models.PositiveIntegerField()
    status = models.BooleanField()
