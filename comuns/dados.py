
import sqlite3
from sqlite3 import Error

import configparser
import inspect
import os
import sqlalchemy
import sqlite3
from sqlite3 import Error

#import sys
#sys.path.insert(1,'../comuns')
import utils


class conexaoSqlalchemy():
    def __init__(self,arquivo):
        """
        Objeto que define as funções relacionados com a conexão do banco de dados usando o framework sqlalchemy
        :param arquivo: nome do arquivo de configuração do tipo ini

        Exemplo:
        objdados = dados.conexaoSqlalchemy('config.ini')

        Se não for conexão local
        objdados = dados.conexaoSqlalchemy('config.ini', local=False)

        """
        self.objArqIni = utils.setupIni(arquivo)

        self.sgdb = self.objArqIni.retValor('setup', 'sgdb')
        self.secaoDb = self.objArqIni.retValor('setup', 'secaoDb')

        self.host = self.objArqIni.retValor(self.secaoDb, 'host')
        self.port = self.objArqIni.retValor(self.secaoDb, 'port')
        self.db = self.objArqIni.retValor(self.secaoDb, 'db')
        self.schema = self.objArqIni.retValor(self.secaoDb, 'schema')

        if self.objArqIni.retValor(self.secaoDb, 'user'):
            self.user = self.objArqIni.retValor(self.secaoDb, 'user', criptografado=True)
        else:
            self.user = None

        if self.objArqIni.retValor(self.secaoDb, 'password'):
            self.pwd = self.objArqIni.retValor(self.secaoDb, 'password', criptografado=True)
        else:
            self.pwd = None

        self.exibirMsg = True

    def conectar(self):
        """
          Estabelecer a conexão com o banco de dados a partir dos parâmetros armazenados em um arquivo de configuração

          ### Informações importantes sobre a função Conectar
          #### A conexão é realizada pelo Sqlalchemy - framework de mapeamento objeto-relacional SQL (ORM) de código aberto
          #### O schema a ser utilizado deve ser informado nos comandos, diferente do psycopg2 onde o schema é definido na conexão
          #### A variável engine está recebendo os dados da conexão, mas a conexão só será estabelecida após o comando engine.connect()

          Para usar esse módulo no Plugin Pymeo, os módulos que não são de origem do QGis devem ser instalados. Ex.: sqlalchemy

          08/08/2024
          Passou a usar a classe utils.setupIni() para simplificar o processo
          A chave usuário do arquivo config.ini deve ser formado por 2 valores separados por |
          A chave senha do arquivo config.ini deve ser formado por 2 valores separados por |

        :return:
        """
        try:
            if self.sgdb == 'postgresql':
                self.engine = sqlalchemy.create_engine(f"{self.sgdb}://{self.user}:{self.pwd}@{self.host}:{self.port}/{self.db}")
                self.con = self.engine.connect()
            elif self.sgdb == 'sqlite':
                self.engine = sqlalchemy.create_engine(f"{self.sgdb}:///{self.db}")
                self.con = sqlite3.connect(f"{self.db}")
                self.cursor = self.con.cursor()
            #self.mensagem = [f"Conexão {self.sgdb} com o banco {self.db} realizada com sucesso!"]
            #print(self.mensagem)
        except Exception as e:
            erro = str(e)
            self.mensagem = [
                f"Problemas ao estabelecer conexão {self.sgdb} com banco de dados {self.db}. Verifique!",
                f"{erro}"
                f"SGDB: {self.sgdb}",
                f"Db: {self.db}",
                f"Porta: {self.port}",
                f"Ip: {self.host}",
                # f"User: {self.user}",
                # f"Pwd: {self.pwd}"
            ]
            utils.gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)
            utils.gerarLog(self.mensagem,
                           inspect.getframeinfo(inspect.currentframe()),
                           self.exibirMsg)
            print(erro)

    def desconectar(self):
        #Ver qual comando é usado para desconectar no sqlalchemy
        self.con.close()

    def testarCnxBD(self):
        try:
            self.conectar()
            return self.con
        except Exception as e:
            #erro = str(e)
            utils.gerarLog(["Problemas na conexão com o banco de dados. Verifique!",
                            f"SGDB: {self.sgdb}",
                            f"Db: {self.db}",
                            f"Porta: {self.port}",
                            f"Ip: {self.host}",
                            f"Usuário: {self.user}"],
                           inspect.getframeinfo(inspect.currentframe()), self.exibirMsg)
            return 0

    # Criar o Banco de Dados definido na criação da conexão (create_engine)
    def criarDB(self):
        try:
            if self.sgdb == 'postgresql':
                if not database_exists(self.engine.url):
                    create_database(self.engine.url)
            elif self.sgdb == 'sqlite':
                 #criarDBSQLite(":memory:")
                 #criarCnxSQLite(r"C:\sqlite\db\dadosabertos.db")
                 #criarCnxSQLite(self.db)
                 self.con = sqlite3.connect(self.db)
        except Exception as e:
            erro = str(e)
            utils.gerarLog([
                f"### Linha: {'{:>4}'.format(inspect.getframeinfo(inspect.currentframe()).lineno)} - Problemas ao tentar criar o banco de dados: {banco}.",
                erro
            ],
                inspect.getframeinfo(inspect.currentframe()), self.exibirMsg)


    # Criar um schema no Banco de Dados usado na conexão (create_engine)
    def criarSchema(self):
        if self.sgdb == 'postgresql':
            self.executarDML(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")

    def criarTabela(self, tabela, campos):

        #print(campos)
        if self.sgdb == 'postgresql':
            sql = f'CREATE TABLE IF NOT EXISTS {self.schema}.{tabela} ('

        if self.sgdb == 'sqlite':
            sql = f'CREATE TABLE IF NOT EXISTS {tabela} ('

        for campo,tipo in campos.items():
            #sql += f'{campo} {tipo} COLLATE pg_catalog."default",'
            sql += f'{campo} {tipo},'

        # Retirar espaços em branco
        sql = sql.strip()

        #Retirar o último caractere (a última vírgula)
        sql = sql[:-1]

        # Incluir o último parênteses no comando create table
        sql += ')'
        self.executarDML(sql)
        
    # Retorna registros
    def executarDQL(self,sql):
        try:
            self.conectar()
            if self.sgdb=='sqlite':
                print(sql)
                res = self.cursor.execute(sql).fetchall()
            else:
                res = self.con.execute(sqlalchemy.sql.text(sql)).fetchall()
            self.desconectar()
            return res
        except Exception as e:
            erro = str(e)
            utils.gerarLog([
                f"Problemas ao executar o comando sql na rotina executarDQL",
                f"{sql}",
                erro
                ],
                inspect.getframeinfo(inspect.currentframe()),
                True)
            utils.gerarLogErro(inspect.getframeinfo(inspect.currentframe()), self.exibirMsg)

    # Executar comandos sql sem retornar registros
    def executarDML(self, sql):
        #  o método text() de sqlalchemy.sql é usada para compor uma instrução textual passada para o banco de dados praticamente inalterada.
        # def executarDML(self,sql,values=None):

        self.conectar()
        try:
            if self.sgdb=='sqlite':
                #self.cursor.execute(sql)
                self.con.execute(sql)
            else:
                sql = sqlalchemy.sql.text(sql)
                self.con.execute(sql)

            self.con.commit()
        except Exception as e:
            erro = str(e)
            utils.gerarLog([
                f"Problemas ao executar o comando sql na rotina executarDQL",
                f"{sql}"
                ],
                inspect.getframeinfo(inspect.currentframe()),
                self.exibirMsg)
            utils.gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)

    def truncar(self,tabela):
        if self.sgdb == 'postgresql':
            self.executarDML(f'TRUNCATE TABLE {tabela} CONTINUE IDENTITY RESTRICT')
        elif self.sgdb == 'sqlite':
            self.executarDML(f'DELETE FROM {tabela}')

    def criarTabelaViaDf(self, tabela, df):
        # Iniciar o comando sql
        sql = f"CREATE TABLE {tabela} ("

        # Criar uma lista com todas as colunas do Dataframe
        colunas = df.columns

        for i, coluna in enumerate(colunas):
            sql += f"{coluna} TEXT"
            if i < len(colunas) - 1:
                sql += ", "

        # Finaliza o comando SQL
        sql += ");"

        self.executarDML(sql)

    def totalRegistros(self,tabela):
        self.conectar()
        if self.sgdb == 'postgresql':
            sql = sqlalchemy.sql.text(f"select count(*) from {tabela}")
            totalreg = self.con.execute(sql)
        self.desconectar()
        return totalreg.scalar()

    # Comentado em 25/06/2024
    # Utilizar a função do arquivo utils.lerArqIni
    def lerArqIni(self):
        pass
    #     try:
    #         # Ler o arquivo config.ini
    #         self.configObj = configparser.ConfigParser(interpolation=None)
    #
    #         ## Verifica se o arquivo ini informado na classe existe
    #         ##### Se o arquivo ini estiver no mesmo diretório do arquivo.py não é necessário incluir o diretório
    #         if os.path.isfile(self.arqini) == True:
    #             try:
    #               self.configObj.read(self.arqini)
    #             except Exception as e:
    #                 erro = str(e)
    #                 print(erro)
    #                 utils.gerarLog([
    #                     f"Problemas ao tentar ler o arquivo de configuração. Verifique!"
    #                 ],
    #                     inspect.getframeinfo(inspect.currentframe()),
    #                     True)
    #                 utils.gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)
    #
    #             try:
    #                 self.sgdb = self.configObj['setup']['sgdb']
    #
    #                 self.host = self.configObj[self.sgdb]['host']
    #                 self.port = self.configObj[self.sgdb]['port']
    #                 self.db = self.configObj[self.sgdb]['db']
    #                 self.schema = self.configObj[self.sgdb]['schema']
    #                 self.pathdownload = self.configObj['url']['pathdownload']
    #
    #                 # print(self.sgdb)
    #                 # print(self.host)
    #                 # print(self.port)
    #                 # print(self.db)
    #                 # print(self.schema)
    #                 # print(self.pathdownload)
    #             except Exception as e:
    #                 erro = str(e)
    #                 print(erro)
    #                 utils.gerarLog([
    #                     f"Problemas nos parâmetros do arquivo de configuração. Verifique!"
    #                 ],
    #                     inspect.getframeinfo(inspect.currentframe()),
    #                     True)
    #                 utils.gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)
    #
    #             try:
    #                 if self.sgdb == 'postgresql':
    #                     # Descriptografar usuário do banco
    #                     self.user = (utils.descriptografarSenha(self.configObj[self.sgdb]['user1'],
    #                                                             self.configObj[self.sgdb]['user2'])).decode('utf-8')
    #                     # Descriptografar senha do banco
    #                     self.pwd = (utils.descriptografarSenha(self.configObj[self.sgdb]['password1'],
    #                                                            self.configObj[self.sgdb]['password2'])).decode('utf-8')
    #             except Exception as e:
    #                 erro = str(e)
    #                 print(erro)
    #                 utils.gerarLog([
    #                     f"Problemas nos parâmetros de usuário e senha. Verifique!"
    #                 ],
    #                     inspect.getframeinfo(inspect.currentframe()),
    #                     True)
    #                 utils.gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)
    #         else:
    #             utils.gerarLog([
    #                 f"Arquivo {self.arqini} não encontrado. Verifique se o nome do arquivo está correto."
    #             ],
    #                 inspect.getframeinfo(inspect.currentframe()),
    #                 True)
    #     except Exception as e:
    #         erro = str(e)
    #         utils.gerarLog([
    #             f"Problemas no arquivo de configuração. Verifique!"
    #             ],
    #             inspect.getframeinfo(inspect.currentframe()),
    #             True)
    #         utils.gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)