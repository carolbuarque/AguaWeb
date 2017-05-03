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
            #form.save()
            dados = form.cleaned_data
            cod = dados['codigo_ana']
            postos = Posto.objects.filter(codigo_ana=cod)
            series_originais = SerieOriginal.objects.filter(posto=cod)
            series_temporais = SerieTemporal.objects.filter(posto=cod)
            postos.delete()
            series_originais.delete()
            series_temporais.delete()
            #x = len(postos)
            #if postos:
                #nova_entrada = postos.order_by('-updated')[0]
                #Posto.objects.delete() 
                #entradas_antigas.delete()
            #localizacao = Localizacao.objects.get(id=1)
            get = Get_Serie()
            dados, erro = get.obtem_info_posto(cod)
            nome = dados['nome']
            if erro:
                messages.add_message(request, messages.SUCCESS, '%s'%nome)
                render(request, 'graph_generator/new_serie.html', {'aba':'nova', 'form':form})
            posto = Posto.objects.create(codigo_ana=cod, nome=dados['nome'], altitude=dados['altitude'], bacia=dados['bacia'], rio=dados['rio'], area=dados['area'])
            posto.save()
            get.executar(posto)
            #serie = postos[0]
            #q = Series.objects.order_by('-updated')
            #serie = q[0]
            return HttpResponseRedirect(str(posto.id))
    return render(request, 'graph_generator/new_serie.html', {'form': form})
    
def get_info(request, posto_id):
    """Show info about the serie"""
    #codigo_ana = posto_id
    posto = get_object_or_404(Posto, pk=posto_id)
    #get = Get_Serie()
    #dados = get.obtem_info_posto(codigo_ana)
    #serie_de_dados = get.executar(codigo_ana)
    #posto = Info.objects.create(serie=codigo_ana, dados=serie_de_dados, nome=dados['nome'], altitude=dados['altitude'], bacia=dados['bacia'], latitude=dados['latitude'], longitude=dados['longitude'], rio=dados['rio'], area=dados['area'])
    #posto.save()
    #estacao = get_object_or_404(Series, pk=serie_id)
    #numero = estacao.codigo_ana
    #serie = Get_Serie()
    #data = Get_Serie.executar(serie, numero)
    return render(request, 'graph_generator/info.html', {'posto':posto})
    #return render(request, 'graph_generator/info.html', {'data':data, 'estacao':estacao}, )"""

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
    #Show the stats of the series
    #estacao = get_object_or_404(Info, pk=serie_id)
    #serie = estacao.dados
    #new_df = pd.read_json(serie, orient='split')
    #q90 = new_df.quantile(.10)
    return render(request, 'graph_generator/stats.html', {'q90':q90, 'q50':q50})

def charts(request, posto_id):
    """Show the graphs of the series"""
    data_series = get_data_serie(posto_id)
    adress = hidrograma(data_series)
    return render(request, adress)

