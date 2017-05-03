from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template import loader

import pandas as pd

from .hidrograma import hidrograma
from .get_series import Get_Serie
from .forms import FormCriaPosto
from .models import Posto, SerieOriginal, SerieTemporal

def index(request):
    """A página inicial de graph_generator"""
    return render(request, 'graph_generator/index.html')

def new_serie(request):
    """Add a new serie number"""
    if request.method != 'POST':
        form = FormCriaPosto()
    else:
        form = FormCriaPosto(request.POST)
        if form.is_valid():
            dados = form.cleaned_data
            cod = dados['codigo_ana']

            postos = Posto.objects.filter(codigo_ana=cod)
            series_originais = SerieOriginal.objects.filter(posto=cod)
            series_temporais = SerieTemporal.objects.filter(posto=cod)
            postos.delete()
            series_originais.delete()
            series_temporais.delete()

            get = Get_Serie()
            dados, erro = get.obtem_info_posto(cod)
            if erro:
                #messages.add_message(request, messages.SUCCESS, '%s'%nome)
                render(request, 'graph_generator/new_serie.html', {'aba':'nova', 'form':form})
            posto = Posto.objects.create(codigo_ana=cod, nome=dados['nome'], altitude=dados['altitude'], bacia=dados['bacia'], rio=dados['rio'], area=dados['area'], latitude=dados['latitude'], longitude=dados['longitude'])
            posto.save()
            get.executar(posto)
            return HttpResponseRedirect(str(posto.id))
    return render(request, 'graph_generator/new_serie.html', {'form': form})
    
def get_info(request, posto_id):
    """Show info about the serie"""
    posto = get_object_or_404(Posto, pk=posto_id)
    return render(request, 'graph_generator/info.html', {'posto':posto})

def get_data_serie(posto_id):
    serie = {}
    postos = SerieTemporal.objects.filter(Id = posto_id)
    for posto in postos:
        serie[posto.data_e_hora] = posto.dados
    data_series = pd.Series(data=serie)
    print(data_series)
    return data_series

def stats(request, posto_id):
    data_series = get_data_serie(posto_id)
    q90 = data_series.quantile(q=0.10)
    q50 = data_series.quantile(q=0.5)
    media = data_series.mean()
    minima = data_series.min()
    maxima = data_series.max()
    return render(request, 'graph_generator/stats.html', {'q90':q90, 'q50':q50, 'media':media, 'maxima':maxima, 'minima':minima})

def charts(request, posto_id):
    """Show the graphs of the series"""
    data_series = get_data_serie(posto_id)
    hidrograma(data_series)
    return render(request, 'graph_generator/hidrograma.html')

