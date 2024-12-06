"""
/***************************************************************************
 Pymeo
    pymeoDados - Agrupar as funções relacionados aos dados específicos do plugin
    
    Para usar esse módulo no Plugin, diversos módulos utilizados pelos 
    módulos dados e utils devem ser instalados, como Fernet
    todo Ver como instalar módulo no QGis durante a execução
 ***************************************************************************/
 #
 #
"""

import configparser
import csv
from datetime import datetime
import inspect
import os
import pandas as pd

import sqlalchemy
import sqlite3
from sqlite3 import Error

import sys
sys.path.insert(1,'./classes')
import apiAna
import calcMeo

sys.path.insert(2,'./comuns')
import utils, utilsPymeo
import dados


class pymeoEstacao():
	def __init__(self, arquivo):
		"""
        Objeto que define as funções relacionados com os dados das estações
        :param arquivo: nome do arquivo de configuração do tipo ini

        Exemplo:
        objdados = pymeoEstacao('config.ini')

        """
		self.exibirMsg = True


		self.objDados = dados.conexaoSqlalchemy(arquivo)
		self.objDados.conectar()

		self.objApiAna = apiAna.hidroWeb()

		self.pathEstacao = f"./estacoes"

		#self.hwExportarDados()

		#self.hwGerarDadosCsv('hw_tb_estacao', 'hw_estacao.csv')

		#self.apiCriarTabela()

		#self.apiExportarDadosViaCsv('hw_estacao.csv')

		#self.apiExportarDadosViaDf('hw_tb_estacao')

		#self.pymeoCriarTabelaEstacao()


	def hwCriarTabelaEstacao(self):
		self.objDados.criarTabela('hw_tb_estacao',
									  {'Codigo': 'text', 'Nome': 'text',
									   'TipoEstacao': 'text',
									   'TipoEstacaoCodigo': 'text',
									   'Operando': 'text',
									   'CodigoAdicional': 'text',
									   'Latitude': 'text',
									   'Longitude': 'text',
									   'Altitude': 'text',
									   'AreaDrenagem': 'text',
									   'Bacia': 'text',
									   'BaciaCodigo': 'text',
									   'SubBacia': 'text',
									   'SubBaciaCodigo': 'text',
									   'Rio': 'text',
									   'RioCodigo': 'text',
									   'UF': 'text',
									   'UFCodigo': 'text',
									   'Municipio': 'text',
									   'MunicipioCodigo': 'text',
									   'Responsavel': 'text',
									   'ResponsavelSigla': 'text',
									   'ResponsavelCodigo': 'text',
									   'ResponsavelUnidade': 'text',
									   'Operadora': 'text',
									   'OperadoraSigla': 'text',
									   'OperadoraCodigo': 'text',
									   'OperadoraUnidade': 'text',
									   'OperadoraRoteiro': 'text',
									   'EscalaNivel': 'text',
									   'EscalaNivelInicio': 'text',
									   'EscalaNivelFim': 'text',
									   'RegistradorNivel': 'text',
									   'RegistradorNivelInicio': 'text',
									   'RegistradorNivelFim': 'text',
									   'MedicaoDescargaLiquida': 'text',
									   'MedicaoDescargaLiquidaInicio': 'text',
									   'MedicaoDescargaLiquidaInicioFim': 'text',
									   'MedicaoDescargaSolida': 'text',
									   'MedicaoDescargaSolidaInicio': 'text',
									   'MedicaoDescargaSolidaFim': 'text',
									   'MedicaoQA': 'text',
									   'MedicaoQAInicio': 'text',
									   'MedicaoQAFim': 'text',
									   'PluviometroConvencional': 'text',
									   'PluviometroConvencionalInicio': 'text',
									   'PluviometroConvencionalFim': 'text',
									   'RegistradorChuva': 'text',
									   'RegistradorChuvaInicio': 'text',
									   'RegistradorChuvaFim': 'text',
									   'TanqueEvaporimetrico': 'text',
									   'TanqueEvaporimetricoInicio': 'text',
									   'TanqueEvaporimetricoFim': 'text',
									   'EstacaoClimatologica': 'text',
									   'EstacaoClimatologicaInicio': 'text',
									   'EstacaoClimatologicaFim': 'text',
									   'EstacaoPiezometria': 'text',
									   'EstacaoPiezometriaInicio': 'text',
									   'EstacaoPiezometriaFim': 'text',
									   'EstacaoTelemetrica': 'text',
									   'EstacaoTelemetricaInicio': 'text',
									   'EstacaoTelemetricaFim': 'text',
									   'RedeBasica': 'text',
									   'RedeEnergetica': 'text',
									   'RedeNavegacao': 'text',
									   'RedeCursoDagua': 'text',
									   'RedeEstrategica': 'text',
									   'RedeCaptacao': 'text',
									   'RedeRHNR': 'text',
									   'RedeQA': 'text',
									   'RedeClasseVazao': 'text',
									   'Descricao': 'text',
									   'Geom': 'text',
									   'x': 'text',
									   'y': 'text'})

	def hwTratarDados(self, df):
		# Retirar os pontos dos valores
		df['Codigo'] = df['Codigo'].str.replace('.', '', regex=False)
		df['MunicipioCodigo'] = df['MunicipioCodigo'].str.replace('.', '', regex=False)
		df['RioCodigo'] = df['RioCodigo'].str.replace('.', '', regex=False)
		df['siglaUf'] = self.sigla

	def hwExportarDados(self, limpar=True):
			try:
				if limpar:
					self.objDados.truncar('hw_tb_estacao')

				if utils.pastaVazia(self.pathEstacao) == 'N':
					for arquivo in os.listdir(self.pathEstacao):
						# ==========================================================================
                        # Identificar o arquivo csv na Pasta \estacoes\*.csv
						nomeArquivo = self.pathEstacao + '\\' + arquivo

						# Gerar Objeto de dados (Dataframe)
						self.df = utils.gerarDf('csv', nomeArquivo, delimitador=';')

						# Dividir o nome do arquivo hw_estacao_UF.csv para pegar a UF no nome do arquivo
						pos1, pos2, pos3 = arquivo.split('_')
						sigla, extensao = pos3.split(('.'))
						self.sigla = sigla[:2]

						self.hwTratarDados(self.df)

						# Gerar dados a partir do Dataframe
						utils.gerarDadosViaDf(self.df, 'hw_tb_estacao', self.objDados)
						mensagem = [f"{arquivo} | {len(self.df)} registros"]
						utils.gerarLog(mensagem,
									   inspect.getframeinfo(inspect.currentframe()),
									   self.exibirMsg)

				else:
					#erro = str(e)
					utils.gerarLog([
									f"### Linha: {'{:>4}'.format(inspect.getframeinfo(inspect.currentframe()).lineno)} - Geral - Pasta de Download (pathdownload) {browser.get('pathdownload')} vazia. Verifique!",
									#erro
									],
									inspect.getframeinfo(inspect.currentframe()),
									self.exibirMsg)
			except Exception as e:
				erro = str(e)
				utils.gerarLog([f"### Linha: {'{:>4}'.format(inspect.getframeinfo(inspect.currentframe()).lineno)} - Problemas tentar exportar o arquivo {arquivo} para o banco {self.objDados.db}",
								erro
								],
							   inspect.getframeinfo(inspect.currentframe()),
							   self.exibirMsg)

	def hwGerarDadosCsv(self, tabela, arquivo):
		#df = pd.read_sql_query(f"SELECT Codigo FROM {tabela} where status_api is not 'True' and siglaUF = 'AP' order by 1", self.objDados.con)
		df = pd.read_sql_query(
			f"SELECT Codigo FROM {tabela} where siglaUF = 'MG' order by 1",
			self.objDados.con)
		# Exportando o DataFrame para um arquivo CSV
		df.to_csv(arquivo, sep=";", encoding='utf-8', header=False, index=False)

	def apiCriarTabela(self):
		self.objApiAna.getDadosHidroInventarioEstacoes(10010000)
		self.objDados.criarTabelaViaDf('api_tb_estacao', self.objApiAna.df)

	def apiExportarDadosViaCsv(self, arquivo):
		cont = 0
		cont2 = 0
		with open(arquivo, mode='r', encoding='utf-8') as arqcsv:
			for linha in csv.reader(arqcsv):
				codigo = linha[0]
				self.objApiAna.getDadosHidroInventarioEstacoes(codigo)
				status = None
				if self.objApiAna.status == 200:
					sql = f"UPDATE hw_tb_estacao SET status_api='True' WHERE Codigo={codigo}"
					utils.gerarDadosViaDf(self.objApiAna.df, 'api_tb_estacao', self.objDados, sql)
				else:
					sql = f"UPDATE hw_tb_estacao SET status_api='False' WHERE Codigo={codigo}"
					self.objDados.executarDML(sql)
				cont = cont+1
				cont2 = cont2+1
				if cont2 == 100:
					print(cont)
					cont2 = 0
		print(cont)


	def apiExportarDadosViaDf(self, tabela):
		# Gerar o dataframe via tabela do banco de dados
		df = pd.read_sql_query(f"SELECT Codigo FROM {tabela} order by 1", self.objDados)

		for codigo in df['Codigo']:
			self.objApiAna.getDadosHidroInventarioEstacoes(codigo)
			print(self.objApiAna.status)
			print(self.objApiAna.statusTexto)
			utils.gerarDadosViaDf(self.objApiAna.df, 'api_tb_estacao', self.objDados, f"UPDATE hw_tb_estacao SET status_api={status} WHERE Codigo={codigo}")
			# UPDATE hw_tb_estacao
			# SET status_api={status_api}
			# WHERE Codigo={codigo}
			print(codigo)

	def pymeoCriarTabelaEstacao(self):
		#data = datetime.now()
		#data.strftime("%d/%m/%Y %H:%M")
		self.objDados.executarDML("CREATE TABLE tb_estacao AS "
								  "SELECT hw.Codigo as codigoEstacao,"
								  "2 as nivelConsistencia,"
								  "hw.Nome as nomeEstacao,"
								  "hw.Operando as operando,"								  
								  "hw.Nome as nomeEstacao,"
								  "0.0 as valorMeo,"
								  "hw.Latitude as Latitude,"
								  "hw.Longitude as Longitude,"
								  "hw.RioCodigo as codigoRio,"
								  "hw.Rio as nomeRio,"
								  "hw.BaciaCodigo as codigoBacia,"
								  "hw.Bacia as nomeBacia,"
								  "hw.SubBaciaCodigo as codigoSubBacia,"
								  "hw.SubBacia as nomeSubBacia,"
								  "hw.siglaUF as siglaUF,"
								  "hw.MunicipioCodigo as codigoMunicipio,"
								  "hw.Municipio as nomeMunicipio,"
								  "hw.status_api as statusApi,"
								  "datetime()  as dtCadastro,"
								  "datetime() as dtAtualizacao "
								  " from hw_tb_estacao hw")

class pymeoSerie():
	def __init__(self, arquivo):
		"""
        Objeto que define as funções relacionados com os dados das estações
        :param arquivo: nome do arquivo de configuração do tipo ini

        Exemplo:
        objdados = pymeoEstacao('config.ini')

        """
		self.exibirMsg = False

		self.objDados = dados.conexaoSqlalchemy(arquivo)
		self.objDados.conectar()

	def gravarValorMeoViaCodigo(self,codigo):
		print(f"{codigo} - Calculando o valor da MEO para a estação")
		objMeo = calcMeo.meo()
		objMeo.calcularMeo(codigo)
		if gravar:
			self.gravarValorMeo(codigo, objMeo.resultado)
			print(f"{codigo} - Valor da meo: {objMeo.resultado} atualizado com sucesso!")
		print("=============================================================================")

	def gravarValorMeoViaCsv(self,arquivo):
		#objSerie = pymeoSerie('config.ini')
		gravar=True
		self.exibirMsg=False
		self.nivelConsistencia=2

		cont = 0
		with open(arquivo, mode='r', encoding='utf-8') as arqcsv:
			for linha in csv.reader(arqcsv):
				cont = cont + 1
				codigo = linha[0]
				print(f"{cont} - {codigo} - {datetime.now()} - Calculando o valor da MEO para a estação")
				try:
					objMeo = calcMeo.meo()
					objMeo.calcularMeo(codigo)
					if gravar:
						self.gravarValorMeo(codigo, objMeo.resultado)
						if len(objMeo.dfMeoDet) > 0:
							objMeo.dfMeoDet.to_sql('tb_meo_det', con=self.objDados.con, if_exists='append', index=False,
												   index_label=None)
						print(f"{cont} - {codigo} - Valor da meo: {objMeo.resultado} atualizado com sucesso!")
				except Exception as e:
					logest = open("logcodigo.txt", "a")
					logest.write(f"{codigo};{objMeo.totalRegSerie};{objMeo.resultado}  \n")
					logest.close()
					if gravar:
						self.gravarValorMeo(codigo, objMeo.resultado)
						if len(objMeo.dfMeoDet) > 0:
							objMeo.dfMeoDet.to_sql('tb_meo_det', con=self.objDados.con, if_exists='append', index=False,
												   index_label=None)
						print(f"{cont} - {codigo} - Valor da meo: {objMeo.resultado}  atualizado com sucesso!")
				print("=============================================================================")

	def gravarValorMeo(self,codigo,valorMeo):
		sql = f"UPDATE tb_estacao SET valorMeo={valorMeo}, nivelConsistencia={self.nivelConsistencia}, dtAtualizacao='{datetime.now()}' WHERE codigoEstacao={codigo}"
		self.objDados.executarDML(sql)




#pymeoEstacao('config.ini')

objSerie = pymeoSerie('config.ini')
# OK objSerie.gravarValorMeoViaCsv('estacao_gravar_AC.csv')
# Ok objSerie.gravarValorMeoViaCsv('estacao_gravar_AP.csv')
# Ok objSerie.gravarValorMeoViaCsv('estacao_gravar_AL.csv')
# Ok objSerie.gravarValorMeoViaCsv('estacao_gravar_AM.csv')
# Ok objSerie.gravarValorMeoViaCsv('estacao_gravar_BA.csv')
# Ok objSerie.gravarValorMeoViaCsv('estacao_gravar_CE.csv')
objSerie.gravarValorMeoViaCsv('estacao_gravar_DF.csv')

# objSerie.gravarValorMeoViaCodigo("19070000")

# Valores calculados em 04/07/2024
# 14840000 -  1484.08
# 14110000 -  2182.54
# 34020000 -   675.3125
# 34040000 -   542.44


# Tempo: 0:01:24.352638

#objHidro = apiAna.hidroWeb()
#objHidro.getDadosHidroInventarioEstacoes(codigo)
#dtInic = objHidro.menorData
#data = datetime.now()
#dtFim = data.strftime("%Y/%m/%d")
#print(objHidro.df.info())
#objHidro.getDadosHidroSerieCotas(dtInic, dtFim, False)

#print("\n Iniciar cálculo \n")
#objMeo = calcMeo.meo(objHidro.df, 2)
#objMeo.prepararDadosObtidosViaApi()
#objMeo.calcular()
#print("Valor da Meo: ", objMeo.resultado)
#print(objMeo.dfMeo.info())

