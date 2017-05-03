import pandas as pd, numpy as np
import locale
import plotly.figure_factory as FF
from plotly.offline import plot

def prepara_gantt(dados_set, posto_id):
    df = []
    #datas = serie.reset_index().dropna(axis=0).index.to_series()
    datas = dados_set.index
    list_datas = datas.tolist()
    start = list_datas[0]
    end = list_datas[-1]
    periodos = pd.DataFrame({'start': start, 'end': end}, columns=['start', 'end'], index=[0])
    for linha in periodos.itertuples():
        df.append(dict(Task = str(posto_id), Description = str(posto_id) + ' - %i' %(linha.Index+1), Start = linha.start, Finish = linha.end, Cor = linha.Index % 2))
    return pd.DataFrame(df)

def gantt(dados, posto_id):
    preparados = prepara_gantt(dados, posto_id)
    colors = {0 : 'rgb(0,0,0)', 1 : 'rgb(128,128,128)'}
    fig = FF.create_gantt(preparados, colors = colors, show_colorbar=False, index_col='Cor', group_tasks=True)
    adress = 'gantt-string-variable.html'
    plot(fig, filename=adress)
    return adress

	# http://www.r-graph-gallery.com/121-manage-colors-with-plotly/
	# https://github.com/plotly/plotly.py/pull/588
    # https://plot.ly/python/getting-started/
	# http://stackoverflow.com/questions/22804067/how-to-get-start-and-end-of-ranges-in-pandas