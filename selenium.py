# -*- coding: utf-8 -*-
"""Scripts para importação Decks Newave e Decomp da CCEE."""
import time
import pandas as pd
from datetime import datetime as dt

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL_ACERVO_CCEE = "https://www.ccee.org.br/acervo-ccee"

def pesquisa_acervo_ccee(texto: str,
                         data_ini: str,
                         data_fin: str,
                         chromedriver_path: str,
                         webdriver_prefs=None):
    """
    Realiza a pesquisa avançada no Acervo CCE, pela data de publicação.

    Parametros
    ----------
    texto : str
        Texto da pesquisa.
    data_ini : str
        Data inicial do período formato "dd/mm/YYYY".
    data_fin : str
        Data final do período formato "dd/mm/YYYY".
    chromedriver_path : str
        Caminho do chromedriver.
    webdriver_prefs : dict, optional
        webdriver prefs. The default is None.

    Returns
    -------
    decks : dict
        Dicionario da descrição dos arquivos e links de download.

    """
    service = Service(executable_path=chromedriver_path)
    options = Options()
    options.add_argument("--headless")
    if webdriver_prefs:
        options.add_experimental_option("prefs", webdriver_prefs)

    # Abre o site
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(URL_ACERVO_CCEE)


    data_ini = dt.strptime(data_ini, format("%d/%m/%Y"))
    data_fin = dt.strptime(data_fin, format("%d/%m/%Y"))

    # Digita o texto no campo de pesquisa
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(
        (By.ID,'keyword'))).send_keys(texto)

    # Clica na seta de datas
    element = driver.find_element(
        By.XPATH,
        '//*[@id="portlet_org_ccee_acervo_portlet_CCEEAcervoPortlet_INSTANCE_tixm"]/div/div[2]/div/div[1]/div[1]/div[1]/div/button[2]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)

    # Seleciona "Data de publicação"
    element = driver.find_element(
        By.XPATH,
        '//*[@id="portlet_org_ccee_acervo_portlet_CCEEAcervoPortlet_INSTANCE_tixm"]/div/div[2]/div/div[1]/div[1]/div[1]/div/ul/li[5]/span')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)

    # Apaga Data inicial pre estabelecida (CRTL+A, DELL)
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(
        (By.XPATH,'//*[@id="initialDateAcervo"]'))
        ).send_keys(Keys.CONTROL + "a", Keys.DELETE)
    time.sleep(1)

    # Insere a Data inicial do periodo desejado
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(
        (By.XPATH,'//*[@id="initialDateAcervo"]'))
        ).send_keys(data_ini.strftime("%d/%m/%Y"))

    # Apaga Data final pre estabelecida (CRTL+A, DELL)
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(
        (By.XPATH,'//*[@id="finalDateAcervo"]'))
        ).send_keys(Keys.CONTROL + "a", Keys.DELETE)
    time.sleep(1)

    # Insere a Data final do periodo desejado
    WebDriverWait(driver,20).until(EC.visibility_of_element_located(
        (By.XPATH,'//*[@id="finalDateAcervo"]'))
        ).send_keys(data_fin.strftime("%d/%m/%Y"))
    time.sleep(1)

    # Clica no botão "Filtrar" para realizar a pesquisa
    element = driver.find_element(
        By.XPATH,
        '//*[@id="filtrar"]')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)
    time.sleep(2)

    # Clica na seta de Resultados por pagina
    element = driver.find_element(
        By.XPATH,
        '//*[@id="portlet_org_ccee_acervo_portlet_CCEEAcervoPortlet_INSTANCE_tixm"]/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]/button')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)

    # Seleciona o valor 100
    element = driver.find_element(
        By.XPATH,
        '//*[@id="portlet_org_ccee_acervo_portlet_CCEEAcervoPortlet_INSTANCE_tixm"]/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]/ul/li[3]/span')
    driver.execute_script("arguments[0].scrollIntoView();", element)
    driver.execute_script("arguments[0].click();", element)

    time.sleep(2)
    # Pega todos os arquivos
    cards = driver.find_elements(By.CLASS_NAME, "col")

    # Cria um dicionario de links e descrições do arquivo
    decks = {}
    titulo = []
    data_ref = []
    info = []
    links = []
    data_publi = []
    hashs = []
    tamanho = []
    descricao = []
    for card in cards:
        link = card.find_elements(By.TAG_NAME, 'a')
        if link:
            titulo.append(link[0].text)
            data_ref.append(card.find_element(By.CLASS_NAME, "refer").text.rsplit(' ',1)[-1])
            info.append(card.find_element(By.CLASS_NAME, "card-text").text)
            links.append(link[0].get_attribute("href"))
            data_publi.append(card.find_element(By.CLASS_NAME, "card-published").text.rsplit(' ',1)[-1])
            hashs.append(card.find_element(By.CLASS_NAME, "bold-light.card-hash").text.rsplit(' ',1)[-1])
            tamanho.append(card.find_element(By.CLASS_NAME, "bold-light.card-pdf-size").text.rsplit(' ',1)[-1])
            descricao.append(card.text)

    decks = {'nome': titulo,
             'data': data_ref,
             'info': info,
             'link': links,
             'data_publi': data_publi,
             'hash': hashs,
             'tamanho': tamanho,
             'descrição': descricao}
    decks = pd.DataFrame(decks)

    return decks
# -*- coding: utf-8 -*-
"""Script para importação dos Decks Newave."""

from pathlib import Path
from datetime import datetime as dt
from datetime import timedelta
from abc import ABC, abstractmethod
import requests

from dados_ccee.infomercado.acervo_ccee.buscador_acervo_ccee import pesquisa_acervo_ccee

VERIFY_SSL = False
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
    )


class DownloadCCEEBase(ABC):
    """Classe base para download de arquivos do acervo CCEE."""

    # Os 2 Decorators(@) abaixo são usados juntos
    # para definir propriedades abstratas da classe
    @property
    @abstractmethod
    def texto(self):
        """Texto que será pesquisado no acervo CCEE."""

    @property
    @abstractmethod
    def nome(self):
        """Nome do arquivo no acervo CCE."""

    @property
    @abstractmethod
    def info(self):
        """Descrição do arquivo."""

    def __init__(self,
                 chromedriver_path,
                 pasta_download: str,
                 periodo: str or list):
        """
        Faz o download do deck de entrada do Newave para um determinado mês.

        Parâmetros
        ----------
        chromedriver_path : str
            Caminho do chromedriver.
        pasta_download : str
            Pasta em que sera salvo o deck
        periodo : str ou list
            str: mês desejado no formato "mm/YYYY" ex:  "11/2022"
            list: lista com as datas iniciais e finais do periodo
                  formato: ['data_inicial', 'data_final']
                  ex: ['28/01/2022', '31/06/2022']
        """
        self.chromedriver_path = chromedriver_path
        self.pasta_download = Path(pasta_download)
        if isinstance(periodo, list):
            if len(periodo) == 2:
                self.data_ini = dt.strptime(periodo[0], "%d/%m/%Y")
                self.data_fin = dt.strptime(periodo[1], "%d/%m/%Y")
            else:
                raise Exception("periodo informado inválido! inserir no" +
                                " formato: ['data_inicial', 'data_final'] "+
                                " ex: ['28/01/2022', '31/06/2022']")
        elif isinstance(periodo, str):
            self.mes = dt.strptime(periodo, "%m/%Y")
        else:
            raise Exception("Periodo informado inválido!")


    def download(self):
        """Faz o download do ou dos decks."""
        if self.mes:
            self.data_ini = self.mes - timedelta(days=40)
            self.data_fin = self.mes + timedelta(days=40)

        decks = pesquisa_acervo_ccee(self.texto,
                                     self.data_ini.strftime("%d/%m/%Y"),
                                     self.data_fin.strftime("%d/%m/%Y"),
                                     self.chromedriver_path)

        if self.mes and self.nome and self.info:
            decks_filtrados = decks[(decks['data']==self.mes.strftime("%m/%Y")) &
                                    (decks['nome']==self.nome) &
                                    (decks['info']==self.info)]

        elif self.mes and self.nome:
            decks_filtrados = decks[(decks['data']==self.mes.strftime("%m/%Y")) &
                                    (decks['info']==self.nome)]

        elif self.mes and self.info:
            decks_filtrados = decks[(decks['data']==self.mes.strftime("%m/%Y")) &
                                    (decks['info']==self.info)]

        elif self.nome and self.info:
            decks_filtrados = decks[(decks['nome']==self.nome) &
                                    (decks['info'].str.contains(self.info))]

        elif self.mes:
            decks_filtrados = decks[decks['data']==self.mes.strftime("%m/%Y")]

        elif self.nome:
            decks_filtrados = decks[decks['info']==self.nome]

        elif self.info:
            decks_filtrados = decks[decks['info']==self.info]

        else:
            decks_filtrados =  decks

        for i in range(len(decks_filtrados)):
            filename_data = dt.strptime(decks_filtrados.iloc[i]['data'], "%m/%Y")
            filename_data = filename_data.strftime("%m-%Y")
            filename = f"{decks_filtrados.iloc[i]['nome']} - {filename_data}.zip"
            full_path = self.pasta_download / filename
            response = requests.get(decks_filtrados.iloc[i]['link'],
                                    verify=VERIFY_SSL)
            with open(full_path, "wb") as file:
                file.write(response.content)


class DeckNWEntrada(DownloadCCEEBase):
    """Classe para download do Deck de entrada do Newave."""

    texto = "Deck de Preços - Newave"
    nome = "Deck de Preços - Newave"
    info = "Conjunto de arquivos para cálculo do Newave."


class DeckNWCompleto(DownloadCCEEBase):
    """Classe para download do Deck completo (entrada e saída) do Newave."""

    texto = "Processo de Dados do Resultado do Newave"
    nome = "Processo de Dados do Resultado do Newave"
    info = "Todos os dados resultantes do processamento do modelo."


class DeckNWPreliminar(DownloadCCEEBase):
    """Classe para download do Deck de entrada Preliminar do Newave."""

    texto = "Deck de Preços - Newave"
    nome = "Deck de Preços - Newave Preliminar"
    info = "Conjunto de arquivos para cálculo do Newave."


class DeckNWSombra(DownloadCCEEBase):
    """Classe para download do Deck para calculo do Newave Sombra."""

    texto = "Deck de Preços - Newave"
    nome = "Deck de Preços - Newave"
    info = None


class DeckDecomp(DownloadCCEEBase):
    """Classe para download do Deck para calculo do Decomp."""

    texto = "Deck de Preços - Decomp"
    nome = "Deck de Preços - Decomp"
    info =	"Conjunto de arquivos para cálculo do Decomp."


class DeckDecompSombra(DownloadCCEEBase):
    """Classe para download do Deck para calculo do Decomp Sombra."""

    texto = "Deck de Preços - Decomp"
    nome = "Deck de Preços - Decomp"
    info =	None
