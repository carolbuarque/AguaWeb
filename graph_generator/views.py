from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
import pandas

from .hidrograma import hidro
from .get_data_serie import get_data_serie
from .get_series import Get_Serie
from .forms import FormCriaPosto
from .models import Posto, SerieOriginal, SerieTemporal

def index(request):
    """A página inicial de graph_generator"""
    return render(request, 'graph_generator/index.html')

def nova_serie(request):
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
                render(request, 'graph_generator/nova_serie.html', {'aba':'nova', 'form':form})
            posto = Posto.objects.create(codigo_ana=cod, nome=dados['nome'], altitude=dados['altitude'], bacia=dados['bacia'], rio=dados['rio'], area=dados['area'], latitude=dados['latitude'], longitude=dados['longitude'])
            posto.save()
            get.executar(posto)
            return HttpResponseRedirect(str(posto.id))
    return render(request, 'graph_generator/nova_serie.html', {'form': form})
    
def obtem_info(request, posto_id):
    """Show info about the serie"""
    posto = get_object_or_404(Posto, pk=posto_id)
    return render(request, 'graph_generator/info.html', {'posto':posto})

def estatisticas(request, posto_id):
    data_series = get_data_serie(posto_id)
    q90 = float( '%.3f' % ( data_series.quantile(q=0.1) ) )
    q50 = float( '%.3f' % ( data_series.quantile(q=0.5) ) )
    media = float( '%.3f' % ( data_series.mean() ) )
    minima = float( '%.3f' % ( data_series.min() ) )
    maxima = float( '%.3f' % ( data_series.max() ) )
    vazao_max_out = float( '%.3f' % ( 0.9*q90 ) )
    print(type(media))
    return render(request, 'graph_generator/estatisticas.html', {'q90':q90, 'q50':q50, 'media':media, 'maxima':maxima, 'minima':minima, 'vazao_max_out':vazao_max_out})

def hidrograma(request, posto_id):
    """Show the graphs of the series"""
    data_series = get_data_serie(posto_id)
    response = hidro(data_series, posto_id)
    return response

def arquivos(request, posto_id):
    data_series = get_data_serie(posto_id)
    json_file = data_series.to_json(path_or_buf=None, date_format='iso')
    response = HttpResponse(json_file, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=export.json'
    return response