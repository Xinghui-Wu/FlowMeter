from django.db import models


# Create your models here.
class device(models.Model):
    index = models.PositiveIntegerField()
    description = models.CharField(max_length=256)


class flow(models.Model):
    src = models.GenericIPAddressField()
    dst = models.GenericIPAddressField()
    time = models.DateTimeField()
    size = models.PositiveIntegerField()


class connection(models.Model):
    src = models.GenericIPAddressField()
    dst = models.GenericIPAddressField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    all_size = models.PositiveIntegerField()
    status = models.BooleanField(db_index=True)
    address = models.CharField(max_length=64, db_index=True)
    app = models.CharField(max_length=256, db_index=True)
    upload = models.BooleanField(db_index=True)
    download = models.BooleanField(db_index=True)
