from django.db import models

class Posto(models.Model):
    codigo_ana = models.CharField(max_length=10)
    #localizacao = models.ForeignKey(Localizacao)
    #https://docs.djangoproject.com/en/1.10/ref/models/fields/
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    nome = models.CharField(max_length=100, default = None)
    altitude = models.CharField(max_length=100, default = None)
    bacia = models.CharField(max_length=100, default = None)
    rio = models.CharField(max_length=100, default = None)
    area = models.CharField(max_length=100, default = None)
    latitude = models.CharField(max_length=100, default = None)
    longitude = models.CharField(max_length=100, default = None)

    def __str__(self):
        return str(self.codigo_ana)

    def __unicode__(self):
        return str(self.codigo_ana)

    def get_absolute_url(self):
        return "/%i/" %self.codigo_ana

DEFAULT_POSTO = 1

class SerieTemporal(models.Model):
    Id = models.IntegerField(unique=False)
    dados = models.FloatField(null=True)
    data_e_hora = models.DateTimeField(verbose_name='Data e Hora', unique=False)
    posto = models.ForeignKey(Posto, null=True, on_delete=models.CASCADE)
    #nivel_consistencia = models.IntegerField(verbose_name="Nível de Consistência", null=False, default=None)
    class Meta:
        unique_together = (("Id","data_e_hora","posto"),)
        verbose_name_plural = "Séries Temporais"
        verbose_name = "Série Temporal"


class SerieOriginal(models.Model):
    posto = models.ForeignKey(Posto, null=True, on_delete=models.CASCADE)
    serie_temporal_id = models.IntegerField(null=True)

"""class Stats(models.Model):
    q90 = models.ForeignKey(Series, default=DEFAULT_SERIE)"""

