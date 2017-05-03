from bs4 import BeautifulSoup
import requests
import re


url = 'http://hidroweb.ana.gov.br/HidroWeb.asp?TocItem=1080&TipoReg=7&MostraCon=true&CriaArq=false&TipoArq=0&SerieHist=true'
r = requests.post(url)

def obter_link_arquivo(self, response):
    soup = BeautifulSoup(response.content, "lxml")
    return soup.findAll('a')