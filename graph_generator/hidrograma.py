import pandas as pd, numpy as np
import locale
import plotly.figure_factory as FF
import cufflinks as cf
from plotly.offline import plot

def hidrograma(dados_set):
	dados = dados_set.cumsum()
	#df = dados_set.to_dict()
	path = 'C:/Users/Ana Carolina/sites/src/graph_generator/templates/graph_generator/hidrograma.html'
	dados.iplot(filename = path, title='Vazão', xTitle='Tempo', yTitle = 'Vazão', bestfit=True, colors=['pink'], bestfit_colors=['blue'])
	return path
	#figure = iplot(cf.dict.lines().iplot(kind='scatter', asFigure=True))
	#figure['layout']['yaxis1'].update({'title': 'Vazão', 'ticksuffix': ' m³/s'})
	# na sequência insere-se o dicionário no plot
	#plot(figure,filename = 'hidrograma.html')

	# https://plot.ly/ipython-notebooks/cufflinks/
	# https://plot.ly/python/configuration-options/
	# plotly.tools.set_credentials_file(username='cfsouza', api_key='BF3QhM9qpmbCTyP6bms8')

	# Redefinição do layout da figura gerada no cufflinks