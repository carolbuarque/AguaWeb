"""Define padrões de URL para graph_generator"""

from django.conf.urls import url

from . import views

urlpatterns = [
    #Página Inicial
    url(r'^$', views.index, name='index'),
    url(r'^nova_serie/$', views.nova_serie, name='nova_serie'),
    url(r'^nova_serie/(?P<posto_id>\d+)/$', views.obtem_info, name='obtem_info'),
    url(r'^nova_serie/serie_info/(?P<posto_id>\d+)/estatisticas/$', views.estatisticas, name='estatisticas'),
    url(r'^nova_serie/serie_info/(?P<posto_id>\d+)/graficos/$', views.hidrograma, name='hidrograma'),
    url(r'^nova_serie/serie_info/(?P<posto_id>\d+)/arquivos/$', views.arquivos, name='arquivos'),
]