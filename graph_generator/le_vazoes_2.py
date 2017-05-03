import pandas as pd, numpy as np
import locale
import cufflinks as cf
import plotly.figure_factory as FF
# https://www.reddit.com/r/IPython/comments/3tibc8/tip_on_how_to_run_plotly_examples_in_offline_mode/
from plotly.offline import plot
import os, zipfile, calendar
# import shelve, send2trash

def	descompacta(filename):
    with zipfile.ZipFile(filename) as zip:
        zip.extract("VAZOES.TXT")
	
def busca_codigo_ana():
	with open("VAZOES.TXT") as vazoes_file:
		for line in vazoes_file:
			if line[0]  != '/' and len(line) != 1:
				new_filename = line.strip().split(';')[0]
				break
	return new_filename

def descompacta_e_renomeia_txts_ana():
	for filename in os.listdir(os.getcwd()):
		if filename[-4:] == ".ZIP":
			descompacta(filename)
			new_filename = busca_codigo_ana()
			if not os.path.exists(new_filename+'.TXT'):
				os.rename("VAZOES.TXT",new_filename+'.TXT')
			else:
				os.remove("VAZOES.TXT")
				# send2trash.send2trash("VAZOES.TXT")

def monta_multIndex(linha, chaves, primeiro_dia_mes, no_dia_mes):
	cons = linha[chaves.index('NivelConsistencia')]
	rng = pd.date_range(start = pd.to_datetime(primeiro_dia_mes, dayfirst = True), periods = no_dia_mes, tz = 'Brazil/East')
	arrays = [rng, [cons] * no_dia_mes]
	tuples = list(zip(*arrays))
	return pd.MultiIndex.from_tuples(tuples, names = ['Data', 'Consistencia'])

def le_como_txt(filename):
	# Procedimento para ler txt e armazenar em Pandas.Series com MultiIndex
	dados_por_mes = []
	with open(filename) as fin:
		proxima_cabecalho = False
		for line in fin:
			if proxima_cabecalho:
					cabecalho = line[2:].strip()[:-1]
					chaves = cabecalho.split(';')
					proxima_cabecalho = False
			if line[0]  != '/' and len(line) != 1:
				linha = line.strip()[:-1].replace(',','.').split(';')
				pos_inicio = chaves.index('Vazao01')

				primeiro_dia_mes = linha[chaves.index('Data')]
				p_dia_mes_dtime = pd.to_datetime(primeiro_dia_mes, dayfirst = True, infer_datetime_format = True)

				# É possível que mês tenha dados apresentados em mais de uma linha
				no_dias_mes = calendar.monthrange(p_dia_mes_dtime.year,p_dia_mes_dtime.month)[1]
				pos_fim = pos_inicio + no_dias_mes
				
				index = monta_multIndex(linha, chaves, primeiro_dia_mes, no_dias_mes)
				valores = map(float, [np.nan if dado == "" else dado for dado in linha[pos_inicio:pos_fim]])
				dados_mes = pd.Series(valores, index = index, name = filename[:-4])
				dados_por_mes.append(dados_mes)
			elif len(line) == 1:
				proxima_cabecalho = True
	return pd.concat(dados_por_mes)

def ordena_e_exclui_duplicatas(dados, opcao = 1):
	''' Esta função seleciona entre só consistido ou com bruto
	Serializa após checar duplicatas'''
	dados.sort_index(level=['Data','Consistencia'], inplace = True)
	if opcao == 1: # bruto_e_consistido
		ordem = dados.copy(deep = True)
		eh_duplicata = ordem.reset_index(level=1,drop=True).index.duplicated(keep='last')
		saida = dados[~eh_duplicata]
	else:# somente consistidos
		try:
			saida = dados.loc['2']
		except KeyError:
			return
	return saida.reset_index(level=1,drop=True)

def prepara_dados_estudo(opcao = 1):
	descompacta_e_renomeia_txts_ana()
	dados_lista = []
	sem_dados_lista = []
	for filename in os.listdir(os.getcwd()):
		leu_serie = True
		if '.json' in filename:
			lidos = pd.read_json(filename, typ = 'series')
			datas, consists = zip(*lidos['index'])
			datas = pd.to_datetime(datas, unit='ns')
			# datas = pd.to_datetime([data for data,consist in lidos['index']], unit='ns')
			# consists = [consist for data,consist in lidos['index']]
			arrays = [datas, consists]
			index = pd.MultiIndex.from_tuples(list(zip(*arrays)), names=['Data', 'Consistencia'])
			dados = pd.Series(lidos['data'],index=index, name = lidos['name'])
			"""elif ('.db.dat' in filename and not os.path.exists(filename[:-4]+'.json')):
					with shelve.open(filename, flag = 'r') as sfile: # somente leitura
						dados_ordenados = sfile['series']
					dados_ordenados.to_json(filename[:-4]+'.json', date_format = 'iso', orient = 'index')
				elif ('.pkl' in filename and not os.path.exists(filename[:-4]+'.db')):"""
			"""
			elif ('.pkl' in filename and not os.path.exists(filename[:-4]+'.json')):
				dados_ordenados = pd.read_pickle(filename)
				dados_ordenados.to_json(filename[:-4]+'.json', date_format = 'iso', orient = 'index')
		elif ('.TXT' in filename and not os.path.exists(filename[:-4]+'.pkl')):
			"""
		elif ('.TXT' in filename and not os.path.exists(filename[:-4]+'.json')):
			dados = le_como_txt(filename)
			#dados_ordenados.to_pickle(filename[:-4]+'.pkl')
			dados.to_json(filename[:-4]+'.json', date_format = 'iso', orient = 'split')
			"""with open(filename[:-4]+'.pkl','wb') as pfile:
				pickle.dump(dados_ordenados, pfile)"""
		else:
			leu_serie = False
		if leu_serie:
			# uniformização de escolha por consistência neste ponto
			dados_ordenados = ordena_e_exclui_duplicatas(dados, opcao)
			if dados_ordenados is not None:
				dados_lista.append(dados_ordenados)
			else:
				sem_dados_lista.append(filename[:-4])
	dados_set = pd.DataFrame(dados_lista).T
	return dados_set, sem_dados_lista



	
def le_ons():
	# http://strftime.org/
	dateparse = lambda x: pd.to_datetime(x, format = '%d/%b/%Y').tz_convert('Brazil/East')
	df = pd.read_excel('..\..\ONS\Vazões_Diárias_1931_2015.xls', header = 5,
					converters={0 : dateparse}) # não reconhece como data index_col
	df = df.drop(0)
	df = df.set_index(' ') # artifício para reconhecer data como índice
	df = df.astype('float64',copy=False)
	return df



# Para gerar sumário de falhas com MultiIndex
# Mensais: dados.isnull().groupby(pd.Grouper(freq='M', level = 0)).sum()
# Obs.: NaN especificam falta do mês nos dados
# Anuais: Substituir NaN de Mensais por número de dias no mês
def prepara_gantt(dados_set):
	# http://stackoverflow.com/questions/22804067/how-to-get-start-and-end-of-ranges-in-pandas
	df = []
	for name, serie in dados_set.iteritems():
		datas = serie.reset_index().dropna(axis=0).index.to_series()
		start = serie[datas[datas.diff(1) != 1].reset_index(drop=True)].index.values
		end = serie[datas[datas.diff(-1) != -1].reset_index(drop=True)].index.values
		periodos = pd.DataFrame({'start': start, 'end': end}, columns=['start', 'end'])
		for linha in periodos.itertuples():
			df.append(dict(Task = serie.name, Description = serie.name + ' - %i' %(linha.Index+1), Start = linha.start, Finish = linha.end, Cor = linha.Index % 2))
	return pd.DataFrame(df)

def gantt(dados):
	preparados = prepara_gantt(dados)
	# http://www.r-graph-gallery.com/121-manage-colors-with-plotly/
	colors = {0 : 'rgb(0,0,0)', 1 : 'rgb(128,128,128)'}
	# https://github.com/plotly/plotly.py/pull/588
	fig = FF.create_gantt(preparados, colors = colors, show_colorbar=False, index_col='Cor', group_tasks=True)
	# https://plot.ly/python/getting-started/
	plot(fig, filename='gantt-string-variable.html')
	
def hidrograma(dados_set):
	# https://plot.ly/ipython-notebooks/cufflinks/
	# https://plot.ly/python/configuration-options/
	# plotly.tools.set_credentials_file(username='cfsouza', api_key='BF3QhM9qpmbCTyP6bms8')

	# Redefinição do layout da figura gerada no cufflinks
	figure = dados_set.iplot(kind='scatter', asFigure=True)
	figure['layout']['yaxis1'].update({'title': 'Vazão', 'ticksuffix': ' m³/s'})
	# na sequência insere-se o dicionário no plot
	plot(figure,filename = 'hidrograma.html')



def identifica_inicio_ano_hidro(dados_set):
	# Gerar o iterador:
	group=dados_set.groupby(pd.Grouper(freq='A'))
	data_menor_p_a = group.idxmin().to_period()
	m_menor_p_a = data_menor_p_a.applymap(lambda x: x.month)
	m_ini_a_h = m_menor_p_a.mode().min()
	return m_menor_p_a, m_ini_a_h

# Acessar informações por meio de cada par chave-dados:
# for key, data in group:
#     print(data.idxmin()) # identifica dia de menor valor em cada ano
#     break

# transformar em um dicionário depois de passar por lista
# dicio=dict(list(group))

#  acessar dados por meio de cada chave (exemplifico a partir da primeira)
# dicio[list(dicio.keys())[0]]

#  Criando um dicionário com DataFrames por ano como chave
# dict_comp = {key.year: dicio[key] for key in dicio.keys()}

#  Pegando só o último ano
# ultimo = dict_comp[2016]

# Para gerar estatísticas com diferentes janelas temporais e MultiIndex
# dados.groupby(pd.Grouper(freq='A-SEP', level='Data')).mean() #Finaliza em setembro de cada ano!

# Para calcular médias móveis
# dados.groupby(pd.Grouper(freq='A-AUG', level='Data')).rolling(window=60).mean() # Pega 60 anteriores

# Seleção de dados por data
# dados.loc[dados.index.get_level_values('Data').year == 2007].head()

if __name__ == '__main__':
	# https://msdn.microsoft.com/en-us/library/39cwe7zf(vs.71).aspx
	locale.setlocale(locale.LC_ALL, 'ptb')
	dados, sem_dados_lista = prepara_dados_estudo()
	"""
	dados = le_ons()
	cf.go_offline()
	gantt(dados)
	hidrograma(dados)
	"""
	m_menor_p_a, m_ini_a_h = identifica_inicio_ano_hidro(dados)