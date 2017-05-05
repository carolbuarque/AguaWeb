import pandas as pd
import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter

from .models import Posto

def hidro(dados_set, posto_id):
	posto = get_object_or_404(Posto, pk=posto_id)
	cod = posto.codigo_ana
	title='Hidrograma da estação nº '+str(cod)
	fig=Figure()
	ax=fig.add_subplot(111)
	x=dados_set.index
	y=dados_set
	ax.plot_date(x, y, '-')
	ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
	ax.set_ylabel('Vazão (m³/s)')
	ax.set_xlabel('Data')
	ax.set_title(title)
	fig.autofmt_xdate()
	canvas=FigureCanvas(fig)
	response=HttpResponse(content_type='image/png')
	canvas.print_png(response)
	return response