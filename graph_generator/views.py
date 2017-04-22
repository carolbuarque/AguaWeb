from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .forms import SerieForm

def index(request):
    """A página inicial de graph_generator"""
    return render(request, 'graph_generator/index.html')

def new_serie(request):
    """Add a new serie number"""
    if request.method != 'POST':
        form = SerieForm()
    else:
        form = SerieForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('graph_generator:series'))

    context = {'form': form}
    return render(request, 'graph_generator/new_serie.html', context)

