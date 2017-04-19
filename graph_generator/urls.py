"""Define padrões de URL para graph_generator"""

from django.conf.urls import url

from . import views

urlpatterns = [
    #Página Inicial
    url(r'^$', views.index, name='index'),
    url(r'^new_serie/$', views.new_serie, name='new_serie'),
]