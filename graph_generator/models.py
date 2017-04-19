from django.db import models

#from .choices import *

# Create your models here.

class Series(models.Model):
    station = models.CharField(max_length=10)
    #https://docs.djangoproject.com/en/1.10/ref/models/fields/
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    #empty_datetime = models.DateTimeFiel(auto_now=False, auto_now_add=False)
    #stats = models.MultipleChoiceField(choices=STATS_CHOICES)
    #graph = models.MultipleChoiceField(choices=GRAPH_CHOICES)

    def __str__(self):
        return str(self.station)

    def __unicode__(self):
        return str(self.station)

    def temp_series(self):
        

