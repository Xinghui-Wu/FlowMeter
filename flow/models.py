from django.db import models


# Create your models here.
class device(models.Model):
    index = models.PositiveIntegerField()
    description = models.CharField(max_length=256)
