"""
/***************************************************************************
 Pymeo
    dadosPymeo - Agrupar as funções relacionados aos dados específicos do plugin
 ***************************************************************************/
 #
 #
"""
import sqlite3
from sqlite3 import Error

import configparser
import inspect
import os

import pandas as pd
import sqlalchemy
import sqlite3
from sqlite3 import Error

#import sys
#sys.path.insert(1,'../comuns')
import utils
import dados


class conexaoPymeo():
	def __init__(self,arqini,arqcsv=None,criarDB=False,criarTb=False):
		self.objDados = dados.conexaoSqlalchemy(arqini)

		self.objDados.conectar()

		if criarDB:
			self.objDados.criarDB()

		if criarTb:
			self.criarTabelaEstacao()

		self.pd = pd.DataFrame()

		if arqcsv is not None:
			self.df = pd.read_csv(arqcsv, delimiter=';', encoding='utf-8', engine='c')
			self.exportar(self.df,'tb_estacao')

	def criarTabelaEstacao(self):
		self.objDados.criarTabela('tb_estacao', {'Codigo': 'text', 'Nome': 'text',
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
	def exportar(self, df, tabela):
		try:
			print('Exportando')
			df.to_sql(tabela, con=self.objDados.con, if_exists='append', index=False)
			print('Ok')
		except Exception as e:
			erro = str(e)
			print(erro)
			self.mensagem = [
                f"Problemas ao estabelecer conexão com banco de dados.!",
                erro,
                #f"Tabela: {self.tabela}",
                #f"Con: {self.cnx.con}",
                #f"Schema: {self.schema}",
            ]

conexaoPymeo('../config.ini', '../dados/estacao.csv', criarTb=True)