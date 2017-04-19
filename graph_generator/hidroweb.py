import os
import tkinter
import sys
import requests
import re
import shutil
import zipfile
from bs4 import BeautifulSoup
from tkinter.filedialog import askopenfile

from . import models

root    = tkinter.Tk()
entrada = tkinter.filedialog.askopenfile(mode='r')    
root.destroy()

BeautifulSoup("html.parser")

if (entrada == None): 
    sair = input('\tArquivo de entrada nao selecionado. \n\t\tPressione enter para sair.\n')
    sys.exit()

pathname = os.path.dirname(entrada.name) #define o path de trabalho igual ao do arquivo de entrada
os.chdir(pathname)  #muda caminho de trabalho.
Pastaatual=os.getcwd()


VALORES = []
result = []

while True:
 
    conteudo_linha = entrada.read().split("\n")
    VALORES.append(conteudo_linha)
        
    if (len(conteudo_linha) <= 1):
        break
 
print (VALORES, '\n')

class Hidroweb(object):

    url_estacao = 'http://hidroweb.ana.gov.br/Estacao.asp?Codigo={0}&CriaArq=true&TipoArq={1}'
    url_arquivo = 'http://hidroweb.ana.gov.br/{0}'

    def __init__(self, estacoes):
        self.estacoes = estacoes

    def montar_url_estacao(self, estacao, tipo=1):
        return self.url_estacao.format(estacao, tipo)

    def montar_url_arquivo(self, caminho):
        return self.url_arquivo.format(caminho)

    def montar_nome_arquivo(self, estacao):
        return u'{0}.zip'.format(estacao)

    def salvar_arquivo_texto(self, estacao, link):
        r = requests.get(self.montar_url_arquivo(link), stream=True)
        if r.status_code == 200:
            with open(self.montar_nome_arquivo(estacao), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

            os.mktempdir(str(estacao))

            for name in zipp.namelist():
                zipp.extract(name,Pastaatual+'\\'+str(estacao)+'\\')
            filezip.close()

            filename=str(estacao)+'.txt' #nome do arquivo
            os.chdir(str(estacao)) #muda o diretorio para a pasta especifica da estacao
            os.rename('VAZOES.txt',filename) #renomeia o arquivo para o numero da estacao
            shutil.move(filename, r'C:\Users\Ana Carolina') #move o arquivo
            os.chdir(r'C:\Users\Ana Carolina') #retornar ao diretório original

            print ('** %s ** (baixado)' % estacao, )
        else:
            print ('** %s ** (problema)' % estacao, )


    def obter_link_arquivo(self, response):
        soup = BeautifulSoup(response.content)
        try:
            soup.find('a', href=re.compile('^ARQ/'))['href']
            return soup.find('a', href=re.compile('^ARQ/'))['href']
            #soup.find('b', href.re.compile())
            s = '<td class="gridCampo" nowrap>Latitude</td>'
            soup =  BeautifulSoup(s)
            td = soup.find('td') 
            td.contents
            result.append(td)

        except Exception:
            print("Dados nao encontrados deste tipo nesta estacao")
            pass

    def executar(self):
        post_data = {'cboTipoReg': '9'}
        r = requests.post(self.montar_url_estacao(est), data=post_data)
        link = self.obter_link_arquivo(r)
        self.salvar_arquivo_texto(est, link)

if __name__ == '__main__':
    estacao = station
    hid = Hidroweb(estacao)
    hid.executar()