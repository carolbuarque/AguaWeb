import calendar
import datetime as dt
import os
import pandas as pd
import requests
import re
import shutil
from datetime import datetime
from shutil import move
from tempfile import mkdtemp
from zipfile import ZipFile
from bs4 import BeautifulSoup

from .models import SerieOriginal, SerieTemporal, Posto

def criar_temporal(dados, datas, posto):
    """Cria a série temporal"""
    print('criar_temporal')
    cod = posto.id
    dados_temporais = list(zip(datas, dados))
    SerieTemporal.objects.bulk_create([SerieTemporal(Id = cod, data_e_hora = linha[0], posto = posto, dados = linha[1]) for linha in dados_temporais])
    return cod

def cria_serie_original(dados, datas, posto):
    print('criar_serie_original')
    """Cria série original a partir de um DataFrame"""
    Id = criar_temporal(dados, datas, posto)
    print("Criando Série Original para a temporal de ID: "+str(Id))
    o = SerieOriginal.objects.create(posto = posto, serie_temporal_id = Id)
    o.save()
    return o

class Get_Serie(object):
    url_estacao = 'http://hidroweb.ana.gov.br/Estacao.asp?Codigo={0}&CriaArq=true&TipoArq={1}'
    url_arquivo = 'http://hidroweb.ana.gov.br/{0}'

    def montar_url_estacao(self, estacao, tipo=1):
        print('montar_url_estacao')
        return self.url_estacao.format(estacao, tipo)

    def montar_url_arquivo(self, caminho):
        print('montar_url_arquivo')
        return self.url_arquivo.format(caminho)

    def montar_nome_arquivo(self, estacao):
        print('montar_nome_arquivo')
        return u'{0}.zip'.format(estacao)

    def cria_serie(self, estacao, link):
        """Cria série de dados de vazão num diretório temporário e exporta os dados para um DataFrame"""
        print(estacao)
        print(self.estacao)
        r = requests.get(self.montar_url_arquivo(link), stream=True)
        if r.status_code == 200:
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
            print('cria_serie')
            return serie

    def obter_link_arquivo(self, response):
        soup = BeautifulSoup(response.content, "lxml")
        print('obter_link_arquivo')
        return soup.find('a', href=re.compile('^ARQ/'))['href']
    
    def abre_arquivo(self, dirpath):
        filename = str(self.estacao) + '.txt'
        file_path = os.path.join(dirpath,filename)
        print('abre_arquivo')
        with open(file_path) as e:
            lines = e.read().replace(',','.').splitlines()
            del lines[0:17]
        return lines
    
    def extrai_dados(self, line):
        print('extrai_dados')
        col = line.split(";")
        self.consistence = col[1]
        self.data=datetime.strptime(col[2],'%d/%m/%Y')
        self.media_diaria = col[4]
        self.maxima = col[6]
        self.minima = col[7]
        self.media = col[8]
        self.diamaxima = col[9]
        self.diaminima = col[10]
        self.media_anual = col[14]
        self.vazoes = col[16:47]
    
    def separa_data(self):
        print('separa_data')
        d = self.data
        self.mes = self.data.month
        self.ano = self.data.year
        
    def conta_dias(self):
        print('conta_dias')
        self.dia_da_semana, self.dias = calendar.monthrange(self.ano, self.mes)
        
    def separa_vazoes(self):
        print('separa_vazoes')
        s = self.dias
        self.vazoes = self.vazoes[0:s]
        
    def cria_index(self):
        print('cria_index')
        inicio = self.data + dt.timedelta(days = 0.05)
        lista_datas = pd.date_range(start=inicio, periods=self.dias, freq='D', tz = 'America/Maceio')
        lista_consistencia=[self.consistence for i in range (self.dias)]
        arrays = [lista_datas, lista_consistencia]
        tuples = list(zip(*arrays))
        print(tuples)
        self.index = pd.MultiIndex.from_tuples(tuples, names=('Data', 'Consistência'))
        
    def cria_series(self):
        print('cria_series')
        ds = pd.Series(self.vazoes, index = self.index, name = 'Vazao')
        ds_float = pd.to_numeric(ds,errors='coerce',downcast='float')
        self.dados.append(ds_float)
        
    def cria_serie_unica(self):
        """Cria DataFrame com os dados de vazão"""
        print('cria_serie_unica')
        serie_completa = pd.concat(self.dados)
        serie_completa.sort_index(inplace=True)
        duplicatas = serie_completa.reset_index(level=1, drop=True).index.duplicated(keep='last')
        dados_sem_duplicatas = serie_completa[~duplicatas]
        serie = dados_sem_duplicatas.reset_index(level=1, drop=True)
        return serie

    def obtem_info_posto(self, estacao):
        print('obtem_info_posto')
        response = requests.get(self.montar_url_estacao(estacao), stream=True)
        soup = BeautifulSoup(response.content, "lxml")
        try:
            info = {t.text:t.find_next_sibling("td").text for t in soup.findAll("td", {'class':'gridCampo'})}
            a = info['Latitude']
            b = a.replace("-", "")
            c = b.replace(",", ".")
            glat, mlat, slat = c.split(":")
            d = info['Longitude']
            e = d.replace("-", "")
            f = e.replace(",", ".")
            glon, mlon, slon = f.split(":")
            lat = -(float(glat)+float(mlat)/60+float(slat)/3600)
            lon = -(float(glon)+float(mlon)/60+float(slat)/3600)
            lat = format(lat, '.3f')
            lat = float(lat)
            lon = format(lon, '.3f')
            lon = float(lon)
            nome = info['Nome']
            altitude = info['Altitude (m)'].replace(",", ".")
            bacia = str(info['Bacia'])
            latitude = str(lat)
            longitude = str(lon)
            rio = str(info['Rio'])
            area = str(info['Área de Drenagem (km2)'])
            dados = {'nome': nome, 'altitude': altitude, 'bacia':bacia, 'latitude':latitude, 'longitude':longitude, 'rio':rio, 'area':area}
            return dados, False
        except:
            return soup.findAll("p",{'class':'aviso'}),True

    def executar(self, estacao):
        self.estacao = estacao
        self.dados = []
        post_data = {'cboTipoReg': '9'}
        url = self.montar_url_estacao(estacao)
        r = requests.post(url, data=post_data)
        link = self.obter_link_arquivo(r)
        series = self.cria_serie(self.estacao, link)
        datas = series.index
        dados = series.values
        cria_serie_original(dados, datas, estacao)