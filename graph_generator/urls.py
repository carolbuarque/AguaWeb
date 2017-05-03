"""Define padrões de URL para graph_generator"""

from django.conf.urls import url

from . import views

urlpatterns = [
    #Página Inicial
    url(r'^$', views.index, name='index'),
    url(r'^new_serie/$', views.new_serie, name='new_serie'),
    url(r'^new_serie/(?P<posto_id>\d+)/$', views.get_info, name='get_info'),
    url(r'^new_serie/serie_info/(?P<posto_id>\d+)/stats/$', views.stats, name='stats'),
    url(r'^new_serie/serie_info/(?P<posto_id>\d+)/charts/$', views.charts, name='charts'),
]