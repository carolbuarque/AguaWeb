import calendar
import datetime
import os
import pandas as pd
import requests
import re
import shutil
from shutil import move
from tempfile import mkdtemp
from zipfile import ZipFile
from bs4 import BeautifulSoup

#from . import models

class Get_Serie(object):

    url_estacao = 'http://hidroweb.ana.gov.br/Estacao.asp?Codigo={0}&CriaArq=true&TipoArq={1}'
    url_arquivo = 'http://hidroweb.ana.gov.br/{0}'

    def __init__(self, estacao):
        self.estacao = estacao
        self.dados = [] 

    def montar_url_estacao(self, estacao, tipo=1):
        return self.url_estacao.format(estacao, tipo)

    def montar_url_arquivo(self, caminho):
        return self.url_arquivo.format(caminho)

    def montar_nome_arquivo(self, estacao):
        return u'{0}.zip'.format(estacao)

    def cria_serie(self, estacao, link):
        print(estacao)
        print(self.estacao)
        r = requests.get(self.montar_url_arquivo(link), stream=True)
        if r.status_code == 200:
            #filename = self.montar_nome_arquivo(estacao)
            with open(self.montar_nome_arquivo(estacao), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                
            temp_dir = mkdtemp()
            filezip = open(str(estacao)+'.zip', 'rb')
            zipp = ZipFile(filezip)
            for name in zipp.namelist():
                zipp.extract(name,temp_dir)
            filezip.close()
   
            file_path = os.path.join(temp_dir,'VAZOES.txt')
            new_filename = str(estacao)+'.txt'
            new_file_path = os.path.join(temp_dir,new_filename)
            os.rename(file_path,new_file_path)
            
            lines = self.abre_arquivo(temp_dir)
            for line in lines:
                self.extrai_dados(line)
                self.separa_data()
                self.conta_dias()
                self.separa_vazoes()
                self.cria_index()
                self.cria_series()
            serie = self.cria_serie_unica()
            return serie


    def obter_link_arquivo(self, response):
        soup = BeautifulSoup(response.content, "lxml")
        return soup.find('a', href=re.compile('^ARQ/'))['href']
    
    def abre_arquivo(self, dirpath):
        filename = str(self.estacao) + '.txt'
        file_path = os.path.join(dirpath,filename)
        with open(file_path) as e:
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
        post_data = {'cboTipoReg': '9'}
        est = self.estacao
        r = requests.post(self.montar_url_estacao(est), data=post_data)
        link = self.obter_link_arquivo(r)
        return self.cria_serie(self.estacao, link)
        

if __name__ == '__main__':
    hid = Hidroweb(estacao)
    r = hid.executar()