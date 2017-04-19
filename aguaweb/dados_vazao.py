import calendar
import os 
import datetime
import pandas as pd

class Estacoes(object):
    def __init__(self, estacao):
        self.id = estacao
        self.dados = []
        
    def __str__(self):
        return '%.8d' % (self.id)
        
    def abre_arquivo(self):
        filename = str(self.id) + '.txt'
        with open(filename) as e:
            lines = e.read().replace(',','.').splitlines()
            del lines[0:17]
        return lines
    
    def extrai_dados(self, line):
        col = line.split(";")
        self.consistence = col[1]
        self.data = col[2]
        self.media_diaria = col[4]
        self.maxima = col[6]
        self.minima = col[7]
        self.media = col[8]
        self.diamaxima = col[9]
        self.diaminima = col[10]
        self.media_anual = col[14]
        self.vazoes = col[16:47]

    def separa_data(self):
        d = self.data
        self.data_formatada = datetime.datetime.strptime(d, "%d/%m/%Y")
        self.mes = self.data_formatada.month
        self.ano = self.data_formatada.year
    
    def conta_dias(self):
        self.dia_da_semana, self.dias = calendar.monthrange(self.ano, self.mes)
        
    def separa_vazoes(self):
        s = self.dias
        self.vazoes = self.vazoes[0:s]

    def cria_index(self):
        lista_datas = pd.date_range(self.data, periods=self.dias, freq='D')
        lista_consistencia = [self.consistence for i in range (self.dias)]
        arrays = [lista_datas, lista_consistencia]
        tuples = list(zip(*arrays))
        self.index = pd.MultiIndex.from_tuples(tuples,names=['Data','Consistencia'])
                
    #def cria_linha(self):
        #self.linha = self.vazoes
       #self.linha = [self.id, self.mes, self.ano] + self.vazoes
        #self.dados += self.linha
        
    def cria_series(self):
        ds = pd.Series(self.vazoes, index = self.index, name = 'Vazao')
        ds_float = pd.to_numeric(ds,errors='coerce',downcast='float')
        self.dados.append(ds_float)
    
    def cria_serie_unica(self):
        serie_completa = pd.concat(self.dados)
        serie_completa.sort_index(level=['Data','Consistencia'], inplace=True)
        duplicatas=serie_completa.reset_index(level=1, drop=True).index.duplicated(keep='last')
        dados_sem_duplicatas = serie_completa[~duplicatas]
        self.serie = dados_sem_duplicatas.reset_index(level=1, drop=True)
        return self.serie
          
    def executar(self):
        lines = self.abre_arquivo()
        for line in lines:
            self.extrai_dados(line)
            self.separa_data()
            self.conta_dias()
            self.separa_vazoes()
            self.cria_index()
            self.cria_series()
        serie = self.cria_serie_unica()
        return serie
        #serie_por_ano = serie_com_index_unico.groupby(serie_com_index_unico.index.year)
        #return serie_por_ano
            
numeros = []
for file in os.listdir(r'C:\Users\Ana Carolina\Documents\TCC'):
    if file.endswith(".txt"):
        numero = str(file)
        numero_int = int(numero.strip('.txt'))
        numeros.append(numero_int)
        
series = {}
        
if __name__ == '__main__':
    estacoes = numeros
    for estacao in estacoes:
        est = Estacoes(estacao)
        serie = est.executar()
        key = str(estacao)
        series[key]=serie
    df = pd.DataFrame.from_dict(series)
    out = df.to_json(orient='index', date_format='iso')
    with open(r'C:\Users\Ana Carolina\Documents\series.txt', 'w') as f:
        f.write(out)

vazoes_de_referencia = {}

for name, serie in series.items():
    percentil = serie.quantile(.10)
    key = name.title()
    vazoes_de_referencia[key]=percentil