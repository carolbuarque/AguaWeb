from django.db import models

from .get_series import Get_Serie
from .stats import Stats

# Create your models here.

class Series(models.Model):
    station = models.CharField(max_length=10)
    #https://docs.djangoproject.com/en/1.10/ref/models/fields/
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    serie = Get_Serie(station)
    q90 = Stats.q90(serie)
    #q50 = Stats.q50(serie)

    def __str__(self):
        return str(self.station)

    def __unicode__(self):
        return str(self.station)