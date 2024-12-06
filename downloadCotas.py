from datetime import datetime
import fnmatch
import glob
import os
import zipfile

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import sqlalchemy
import sqlite3
import time

import sys
dirComuns = "D:/Desenvolvimento/QGIS 3.34.4/apps/qgis-ltr/python/plugins/pymeo/classes"
sys.path.insert(0, dirComuns)
from calcMeo import meo

def dwnEstacao(codigo):
    #options = Options()
    # Ocultar o browser durante a execução do robô
    #options.headless = True

    #navegador = webdriver.Firefox(options=options)
    navegador = webdriver.Firefox()

    navegador.get("https://www.snirh.gov.br/hidroweb/serieshistoricas")

    wait = WebDriverWait(navegador, 10)

    tipoEstacao = wait.until(EC.presence_of_element_located((By.ID, "mat-select-0")))
    tipoEstacao.send_keys("Fluviométrica")

    codEstacao = wait.until(EC.presence_of_element_located((By.ID, "mat-input-0")))
    codEstacao.send_keys(codigo)

    btnConsultar = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'search Consultar')]")))
    btnConsultar.click()

    time.sleep(3)
    btnDownloadCsv = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-tab-body[@id='mat-tab-content-0-0']/div/ana-card/mat-card/mat-card-content/ana-dados-convencionais-list/div/div/table/tbody/tr/td[6]/button/span/mat-icon")))
    btnDownloadCsv.click()

    time.sleep(10)

    navegador.quit()

def pesquisarArquivo(diretorio, codigo):
    # Listar todos os arquivos no diretório
    for arquivo in os.listdir(diretorio):
        # Verificar se o nome do arquivo corresponde ao padrão e tem a extensão .zip
        if fnmatch.fnmatch(arquivo, f'Estacao_{codigo}_CSV*.zip'):
            return os.path.join(diretorio, arquivo)  # Retorna o primeiro arquivo encontrado
    return None  # Retorna None se nenhum arquivo for encontrado

def extrairCotas(codigo, arqfile):
    # Pasta temporária que será usada para armazenar o arquivo que será extraído
    diretorio = f"C:/Users/regin/Downloads"
    arquivo = pesquisarArquivo(diretorio, codigo)

    if arquivo:
        #print(f"Arquivo encontrado: {arquivo}")

        caminho_arquivo_zip = os.path.join(diretorio, arquivo)  # Caminho completo do arquivo ZIP
        dirfinal = f"C:/Users/regin/Downloads/Temp/Estacoes"  # Diretório de destino

        nome_arquivo_cotas = f"{codigo}_Cotas.csv"

        # Verifica se o diretório de destino existe, e cria se não existir
        if not os.path.exists(dirfinal):
            os.makedirs(dirfinal)

        # Tenta abrir e extrair o arquivo ZIP
        try:
            with zipfile.ZipFile(caminho_arquivo_zip, 'r') as z:
                # Lista todos os arquivos dentro do ZIP
                arquivos_no_zip = z.namelist()

                # Verifica se o arquivo específico está dentro do ZIP
                if nome_arquivo_cotas in arquivos_no_zip:
                    # Extrai apenas o arquivo desejado
                    z.extract(nome_arquivo_cotas, dirfinal)
                    #print(f"Arquivo '{nome_arquivo_cotas}' extraído com sucesso em {dirfinal}")
                else:
                    arqfile.write(f"Arquivo '{nome_arquivo_cotas}' não encontrado no ZIP.")
        except zipfile.BadZipFile:
            arqfile.write("Erro: Arquivo ZIP corrompido ou inválido.")
        except Exception as e:
            arqfile.write(f"Erro ao extrair o arquivo: {e}")

        # Excluir o arquivo após sua extração
        os.remove(arquivo)
    else:
        arqfile.write(f"{codigo}: Arquivo  {arquivo} não encontrado")



def atualizarDados(codigo):
    arquivo = f"C:/Users/regin/Downloads/Temp/Estacoes/{codigo}_Cotas.csv"
    objMeo = meo(1)
    objMeo.calcularMeo(codigo, arqCsv=arquivo)
    valor = objMeo.resultado

    sgdb = 'sqlite'
    db = f"D:\\Desenvolvimento\\QGIS 3.34.4\\apps\\qgis-ltr\\python\\plugins\\pymeo\\dados\\pymeo.db"
    engine = sqlalchemy.create_engine(f"{sgdb}:///{db}")
    cnx = sqlite3.connect(f"{db}")
    cursor = cnx.cursor()

    sql = f"UPDATE tb_estacao SET valorMeo = {valor}, origem_valorMeo = 'Via Arquivo Csv', dtAtualizacao = datetime() where codigoEstacao = {codigo}"
    #print(sql)
    cursor.execute(sql)
    cnx.execute(sql)

    cnx.commit()


# dwnEstacao("10100000")
# extrairCotas("10100000")

# select codigoEstacao, valorMeo, origem_valorMeo  from tb_estacao
# where valorMeo <= 0
# order by 1


with open('logDonwloadCotas.txt', 'w') as arqlog:
    arqlog.write("============================================================\n")
    arqlog.write("Início do download dos Csv das estações listadas no arquivo estacao.txt \n")
    arqlog.write("============================================================\n")
    arqlog.write("\n")
    arqlog.write("\n")

arqlog.close()

with open('estacao.txt', 'r') as arquivo:
    linhas = arquivo.readlines()
    for linha in linhas:
        arqlog = open('logDonwloadCotas.txt', 'a')
        # Remover os espaços da linha
        codigo = linha.strip()
        arqlog.write(f"{datetime.now()} \t")
        arqlog.write(f"{codigo} \t")
        try:
            dwnEstacao(codigo)
            arqlog.write(f"Download realizado \t")
        except Exception as e:  # Captura qualquer tipo de erro
            arqlog.write(f"Problemas ao realizar o download: {e} \n")

        try:
            extrairCotas(codigo,arqlog)
            arqlog.write(f"Extração realizada \t")
        except Exception as e:  # Captura qualquer tipo de erro
            arqlog.write(f"Problemas ao realizar a extração: {e} \n")

        try:
            atualizarDados(codigo)
            arqlog.write(f"Atualização de dados realizada \t")
        except Exception as e:  # Captura qualquer tipo de erro
            arqlog.write(f"Problemas ao realizar a atualização dos dados: {e} \n")

        arqlog.write("\n")
        arqlog.close()

