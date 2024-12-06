import configparser
from datetime import datetime, time, timedelta
from dateutil import parser
import os
import pandas as pd
import requests
import time

"""


Autores
Regina Celia Enedina Pereira Gomes da Silva

"""


# Hidro Webservice
# https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html
#
# Hidrometereológicos
# https://www.snirh.gov.br/dadoshidrometereologicos/swagger-ui/index.html
#
#
# Outros links relacionados a Webservice
# https://telemetriaws1.ana.gov.br/ServiceANA.asmx
#
# E-mail: regina.silva@gestao.gov.br
#
# Importante
#
# 1. Entender a diferença entre telemetria e dados convencionais
# 2. Diferenciar os níveis de consistência
#
#
# Observações
# O Token de autenticação expira em 10 minutos
#
# Dúvidas
# Onde podemos conseguir o metadados da Api
#
# Divergências
# Estação analisada = 12360000
#   Hidroweb: Arquivo MDB   1666 registros
#   Hidroweb: Arquivo txt   1693 registros
#   Hidroweb: Arquivo csv   1693 registros
#   ANA Webservices:
#   Spu Api:                 956
# Arquivo baixado através
#
# Reunião com a ANA
# Divergências das informações
# Os dados disponibilizados via Api são os mesmos disponibilizados via Hidroweb?
#
#

class hidroWeb():
    """
    Classe hidroWeb()
    Obtém os dados da API Hidro Webservice
    https://www.ana.gov.br/hidrowebservice/swagger-ui/index.html#

    Orientações sobre o uso da API
    https://www.ana.gov.br/hidrowebservice/manual

    Endpoints contemplados pela Classe
        getOAuth
        EstacoesTelemetricas/OAUth/v1
        Retorna o token de acesso

        getDadosHidroInventarioEstacoes
        EstacoesTelemetricas/HidroInventarioEstacoes/v1
        Retorna o inventário das estações cadastradas na base Hidro

        getDadosHidroSerieCotas
        EstacoesTelemetricas/HidroSerieCotas/v1
        Retorna as séries históricas das estações convencionais (coleta manual)

    Requisitos
        Usuário e senha de acesso a API
    """

    def __init__(self, arqcfg="cfgapiana.ini"):
        """Identificador
           Código do usuário

           Senha
           Senha do usuário fornecida,inicialmente, pela ANA

           Token
           Token gerado pelo endpoint EstacoesTelemetricas/OAUth/v1 para autorizar o acesso aos demais endpoints

           Validade
           Validade do token

           Consulta
           Armazena o nome do endpoint

           Status
           Armazena a resposta da chamada HTTP
        """
        
        self.identificador = ""
        self.senha = ""
        self.token = None
        self.validade = datetime.now()

        self.resposta = None
        self.consulta = None
        self.dfEstacao = pd.DataFrame()
        
        self.statusLogin = None
        
        self.dirClasse = os.path.dirname(__file__)
        
        if self.validarLogin(f"{self.dirClasse}\\{arqcfg}")==0:
            self.getOAuth(self.identificador,self.senha)
        else:
            print("Problemas ao efetuar o login. Verifique.")
        
        self.PATHLOG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\logs'))
        
    
    def validarLogin(self,arquivo):
        self.statusLogin = 0
        if os.path.isfile(arquivo):
            config = configparser.ConfigParser()
            config.read(arquivo)
            
            secao = "apiana"
            if config.has_section(secao):
                self.identificador = f"{config.get(secao, "identificador")}"
                self.senha = f"{config.get(secao, "senha")}"
            else:
                self.statusLogin = 1
        else:
            print(f"Arquivo de configuração {arquivo} não existe.")
            self.statusLogin = 2
        
        return self.statusLogin
            
    def getOAuth(self,usuario,pwd):
        inicio = time.time()
    
        if self.tokenVencido()==True:
            url = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas/OAUth/v1"
            self.identificador = usuario
            self.senha = pwd
            headers = {"accept": "*/*", "Identificador": self.identificador, "Senha": self.senha}

            resultado = requests.get(url, headers=headers)
            self.status = resultado.status_code
            self.statusTexto(int(self.status))
            
            print(self.status, self.identificador, self.senha)

            if int(str(self.status)[0]) <= 3:
                self.dados = resultado.json()
                self.token = self.dados['items']["tokenautenticacao"]
                self.validade = (parser.parse(self.dados['items']["validade"])).replace(tzinfo=None)
            else:
                self.dados = {}
        else:
            pass
            # print("Token dentro da validade")
        fim = time.time()
        self.calcularTempo(inicio,fim)
        return self.token

    def tokenVencido(self):
        """
          tokenVencido
          Método que verifica se o token expirou
        """
        status = False
        if (self.validade)<=(datetime.now()):
            status = True
        return status

    def getDados(self,url,parametros,origem=None):
        """Método que retorna os dados gerados pelo endpoint

        Formato da resposta padrão
        {
          "status": "100 CONTINUE",
          "code": 0,
          "message": "string",
          "items": {}
        }

        Parãmetros
        Campos utilizados para filtrar a pesquisa no formato de um dicionário do Python

        Exemplo de valores para os parâmetros
        parametros = {"Código da Estação": 12360000}
        parametros = {"Código da Estação": 12360000,"Data Inicial": "2021-04-21"}

        Dados
        Dados obtidos na resposta pela pesquisa no formato json

        Df
        Itens obtidos na resposta pela pesquisa no formato de um dataframe do Pandas

        """

        if self.tokenVencido():
            self.getOAuth(self.identificador,self.senha)

        headers = {}
        headers["accept"] = "*/*"
        headers["Authorization"] = f"Bearer {self.token}"
        
        inicio = datetime.now()

        resultado = requests.get(url, params=parametros, headers=headers)
        
        fim =  datetime.now()

        self.status = resultado.status_code
        self.statusTexto(int(self.status))
        #print(parametros, self.status, self.token, self.validade)
        # if self.status==200:
        if int(str(self.status)[0]) <= 3:
            # print(resultado.json())
            self.dados = resultado.json()
            self.df = pd.DataFrame(self.dados['items'])
        else:
            self.dados = None
            self.df = pd.DataFrame()
            print("Status ", self.status,"Parâmetros: ", parametros)
        
        self.gerarLogEndpoint(self.identificador,self.status,url,parametros,headers,inicio,fim,len(self.df.index),origem)
        
        

    ########################################################################################################################################
    # Funções geradas para Api da Ana
    # Cada função irá criar os dados que serão utilizados na função getDados()
    # A função getDados() retorna o código do status da resposta, o texto da resposta e os itens gerados pela Api nos formatos json e dataframe que poderá ser usado da forma que o usuário desejar
    # self.status = resultado.status_code
    # self.statusTexto(int(self.status))
    # self.dados = resultado.json()
    # self.df    = pd.DataFrame(self.dados['items'])

    def getDadosHidroInventarioEstacoes(self,codEstacao, origem=None):
        """
            # /EstacoesTelemetricas/HidroInventarioEstacoes/v1
            # Inventário das estações virtuais (estimação por satélite) cadastradas na base HidroSat
            # Não há limitação de busca por requisição

            # Parâmetros obrigatórios
            #### Código da Estação
            # Parâmetros opcionais
            #### Data Atualização Inicial (yyyy-MM-dd)
            #### Data Atualização Final (yyyy-MM-dd)
            
            # Campos de resposta
            Bacia_Nome
            Estacao_Nome
            Latitude
            Longitude
            Municipio_Nome
            Operando: 1
            Tipo_Estacao: Fluviometrica
            UF_Estacao
            
        :param codEstacao:
        Código da Estação
        :return: dados e df
        """
        url = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas/HidroInventarioEstacoes/v1"
        self.codEstacao = codEstacao
        parametros = {}
        parametros["Código da Estação"] = codEstacao

        self.consulta = 'HidroInventarioEstacoes'
        self.getDados(url,parametros,origem=origem)
        
        if int(str(self.status)[0]) <= 3:
            self.dfEstacao = self.df
            
            # Obter a menor data de referência entre uma lista de campos do tipo data
            # Esse código foi necessário para usar esse menor valor como data inicial na getDadosHidroSerieCotas, qdo a data inicial não for informada
            datas = datas = pd.Series(
                        self.df["Data_Periodo_Climatologica_Fim"].tolist() +
                        self.df["Data_Periodo_Climatologica_Fim"].tolist() +
                        self.df["Data_Periodo_Climatologica_Inicio"].tolist() +
                        self.df["Data_Periodo_Desc_Liquida_Fim"].tolist() +
                        self.df["Data_Periodo_Desc_liquida_Inicio"].tolist() +
                        self.df["Data_Periodo_Escala_Fim"].tolist() +
                        self.df["Data_Periodo_Escala_Inicio"].tolist() +
                        self.df["Data_Periodo_Piezometria_Fim"].tolist() +
                        self.df["Data_Periodo_Piezometria_Inicio"].tolist() +
                        self.df["Data_Periodo_Pluviometro_Fim"].tolist() +
                        self.df["Data_Periodo_Pluviometro_Inicio"].tolist() +
                        self.df["Data_Periodo_Qual_Agua_Fim"].tolist() +
                        self.df["Data_Periodo_Qual_Agua_Inicio"].tolist() +
                        self.df["Data_Periodo_Registrador_Chuva_Fim"].tolist() +
                        self.df["Data_Periodo_Registrador_Chuva_Inicio"].tolist() +
                        self.df["Data_Periodo_Registrador_Nivel_Fim"].tolist() +
                        self.df["Data_Periodo_Registrador_Nivel_Inicio"].tolist() +
                        self.df["Data_Periodo_Sedimento_Inicio"].tolist() +
                        self.df["Data_Periodo_Sedimento_fim"].tolist() +
                        self.df["Data_Periodo_Tanque_Evapo_Fim"].tolist() +
                        self.df["Data_Periodo_Tanque_Evapo_Inicio"].tolist() +
                        self.df["Data_Periodo_Telemetrica_Fim"].tolist() +
                        self.df["Data_Periodo_Telemetrica_Inicio"].tolist() +
                        self.df["Data_Ultima_Atualizacao"].tolist()
                        )
            
    
            # Remove valores nulos
            datasValidas = datas.dropna()
    
            if not datasValidas.empty:  # Verifica se há datas válidas na lista
                self.menorData = datasValidas.min()
            else:
                self.menorData = None
        else:
            print("Resposta", self.status)


    def getDadosHidroInventarioEstacoesLista(self,listaEstacao):
        """
        Gerar um dataframe com os dados obtidos através de uma lista de código de estação informado

        :param listaEstacao:
        Exemplo
        listaEstacao = [12360000, 47568000]
        
        :return:
        """
        df_temp = pd.DataFrame()
        for estacao in listaEstacao:
            self.getDadosHidroInventarioEstacoes(estacao)
            df_temp = pd.concat([self.df, df_temp], ignore_index=True)

        self.df = df_temp
        self.dados = self.df.to_json()
                
        #if int(str(self.status)[0]) <= 3:
        #    self.dfEstacao['codEstacao'] = codEstacao
        #    self.dfEstacao['nomeEstacao'] = self.dados['items'][0]["Estacao_Nome"]
        #    self.dfEstacao['codRio'] = self.dados['items'][0]["Rio_Codigo"]
        #    self.dfEstacao['nomeRio'] = self.dados['items'][0]["Rio_Nome"]
        #    self.dfEstacao['codMunicipio'] = self.dados['items'][0]["Municipio_Codigo"]
        #    self.dfEstacao['nomeMunicipio'] = self.dados['items'][0]["Municipio_Nome"]
        #    self.dfEstacao['codBacia'] = self.dados['items'][0]["codigobacia"]
        #    self.dfEstacao['nomeBacia'] = self.dados['items'][0]["Bacia_Nome"]
        #    self.dfEstacao['ufEstacao'] = self.dados['items'][0]["UF_Estacao"]
        #    self.dfEstacao['latEstacao'] = self.dados['items'][0]["Latitude"]
        #    self.dfEstacao['longEstacao'] = self.dados['items'][0]["Longitude"]
        #    self.dfEstacao['statusEstacao'] = self.dados['items'][0]["Operando"]
        #    self.dfEstacao['tipoEstacao'] = self.dados['items'][0]["Tipo_Estacao"]
        #    self.dfEstacao['siglaResponsavel'] = self.dados['items'][0]["Responsavel_Sigla"]
        #    self.dfEstacao['siglaOperadora'] = self.dados['items'][0]["Operadora_Sigla"]

        
    # 12/09/2024
    # Alterado para poder usar a barra de progresso durante a execução da função
    # De: def getDadosHidroSerieCotas(self, dtInicial, dtFinal, exibirMsg):
    # Para: def getDadosHidroSerieCotas(self, dtInicial, dtFinal, exibirMsg, thread=None):
    def getDadosHidroSerieCotas(self, dtInicial, dtFinal, exibirMsg, thread=None, origem=None):
        # O parâmetro exibirMsg foi inserido em 11/08/2024
        """
            # /EstacoesTelemetricas/HidroSerieCotas/v1
            # Séries de estações virtuais (HidroSat)
            # Parâmetros obrigatórios

            #### Código da Estação
            #### Tipo Filtro Data - Opções: DATA_LEITURA ou DATA_ULTIMA_ATUALIZACAO
            #### Período - Limitado a 366 dias por requisição
            ####### Data Inicial (yyyy-MM-dd)
            ####### Data Final (yyyy-MM-dd)
            # Parâmetros opcionais
            #### Intervalo de horas
            ######## Horário Inicial (00:00:00)
            ######## Horário Final (00:00:00)

        :param dtInicial:
        :param dtFinal:
        :param exibirMsg
        :return:
        """
        url = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas/HidroSerieCotas/v1"
        parametros = {}
        parametros["Código da Estação"] = self.codEstacao
        parametros["Tipo Filtro Data"] = "DATA_LEITURA"

        self.consulta = 'HidroSerieCotas'

        try:
            self.dtInicial = parser.parse(dtInicial)
            self.dtFinal = parser.parse(dtFinal)
        except:
            print("Período da série: ",dtInicial,dtFinal)

        dtInicial = self.dtInicial
        dtFinal = self.dtFinal
        data = dtInicial

        dias = abs((dtFinal - dtInicial).days)
        prazo = timedelta(days=366)

        df_temp = pd.DataFrame()
        # Hora que iniciou a busca das séries de dados
        self.horaInic = datetime.now() 
        
        # Início
        # 12/09/2024
        # Incluído para poder usar a barra de progresso durante a execução da função
        total_loops = dias // 366 + 1
        loop_count  = 0
        # Fim
        
        while dias > 366:
            if dias > 366:
                data = dtFinal - prazo
            time.sleep(1)
            dias = abs((data - dtInicial).days)
            

            parametros["Data Inicial (yyyy-MM-dd)"] = data.strftime("%Y-%m-%d")
            parametros["Data Final (yyyy-MM-dd)"] = dtFinal.strftime("%Y-%m-%d")
            self.getDados(url, parametros, origem)
            #print("getDadosHidroSerieCotas: ",self.status, len(self.df), dtInicial, data, dtFinal)
            
            if len(self.df)>0:
                if exibirMsg:
                    print("Intervalo de datas da série: ",self.codEstacao, dtInicial, data, dtFinal, "Total registros: ", len(self.df))
                df_temp = pd.concat([self.df, df_temp], ignore_index=True)
                
            
            dtFinal = data - timedelta(days=1)
            
            # Início
            # 12/09/2024
            # Incluído para poder usar a barra de progresso durante a execução da função
            # Atualizar a barra de progresso
            loop_count += 1
            if thread is not None:
                progress_value = int((loop_count / total_loops) * 100)
                self.thread.progress.emit(progress_value)
            # Fim
                
            #if exibirMsg:
            #    print(f"Data                : {data}") 
            #    print(f"Data Inicial        : {dtInicial}") 
            #    print(f"Data Final          : {dtFinal}")
            #    print(f"Registros do período: {len(self.df)}")
            #    print(f"Registros acumulado : {len(self.df)}")
            #    print(f"Dias                : {dias}")
            #    print(f"Horário             : {datetime.now()}")
            #    print("===========================================================================")

        parametros["Data Inicial (yyyy-MM-dd)"] = dtInicial.strftime("%Y-%m-%d")
        parametros["Data Final (yyyy-MM-dd)"] = dtFinal.strftime("%Y-%m-%d")
        self.getDados(url, parametros, origem)
        df_temp = pd.concat([self.df, df_temp], ignore_index=True)
        self.df = df_temp
        self.dados = self.df.to_json()
        # Hora que finalizou a busca das séries de dados
        self.horaFim = datetime.now()
        self.tempo = self.horaFim - self.horaInic
        if exibirMsg:
            print(f"Tempo: {self.tempo}")
        
        if thread is not None:
            self.thread.progress.emit(100)  # Progresso completo
            



    # /EstacoesTelemetricas/HidroinfoanaSerieTelemetricaDetalhada/v1
    # Séries das estações telemétricas
    # Parâmetros obrigatórios
    #### Código da Estação
    #### Tipo Filtro Data - Opções: DATA_LEITURA,
    #### Período - Limitado a 366 dias por requisição
    ####### Data Inicial (yyyy-MM-dd)
    ####### Data Final (yyyy-MM-dd)
    # Parâmetros opcionais
    #### Intervalo de horas
    ######## Horário Inicial (00:00:00)
    ######## Horário Final (00:00:00)

    #def getDadosHidroinfoanaSerieTelemetricaDetalhada(self,parametros):
    def getDadosHidroinfoanaSerieTelemetricaDetalhada(self,dtInicial,dtFinal,origem=None):
        url = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas/HidroinfoanaSerieTelemetricaDetalhada/v1"
        parametros = {}
        parametros["Código da Estação"] = self.codEstacao
        parametros["Tipo Filtro Data"]  = "DATA_LEITURA"
        parametros["Data Inicial (yyyy-MM-dd)"] = f"{dtInicial}"
        parametros["Data Final (yyyy-MM-dd)"] = dtFinal

        self.consulta = 'HidroinfoanaSerieTelemetricaDetalhada'
        self.getDados(url,parametros,origem)

    # Retornar o nome das colunas do dataframe
    def dadosItens(self,df):
        for chave in df:
            print(f"{chave} TEXT,")
            #print(chave)

    ########################################################################################################33

    # https://www.rfc-editor.org/rfc/rfc2068#section-6.1
    def statusTexto(self,status):
        if status>=100 and status<=199: # Respostas informativas
            resposta="Resposta informativa"
        elif status>=200 and status<=299: # Respostas bem-sucedidas
            resposta="Solicitação realizada com sucesso"
            # 200 - Ok
            # 201 - Create
        elif status>=300 and status<=399: # Respostas indicando que houve redirecionamento da URL
            resposta = "O servidor conseguiu processar, mas a resposta pode ter sido redirecionada."
            # 300 - Multiple Choice
            # 301 - Moved Permanently
            # 302 - Found
            # 303 - See Other
            # 304 - Not Modified
            # 305 - Use Proxy
            # 306 - unused
            # 307 - Temporary Redirect
            # 308 - Permanent Redirect
            # 30
        elif status>=400 and status<=499: # Respostas relacionadas a erro do cliente
            resposta = "Erro na requisição do cliente. Verifique a URL e os dados de autenticação"
            # 400 - Bad Request  - Requisição contém algum erro
            # 401 - Unauthorized - Acesso negado pois requer autenticação, falta de credencial ou inválida
            # 403 - Forbidden    - Acesso negado pois requer autorização. A credencial é válida, mas o usuário não tem permissão para acessar o recurso
            # 404 - Not Found    - Recurso inexistente
        elif status>=500 and status<=599: # Respostas relacionadas a erro do servidor
            resposta = "A requisição do servidor. Possivelmente os dados do cliente estão corretos, mas o servidor não conseguiu processar"
            # 503 - Service Unavailable         - Servidor em manutenção ou sobrecarregado
            # 505 - HTTP Version Not Supported  - Versão do servidor não suportada, acontece qdo fazemos requisição
            #                                     usando o HTTP2, mas o servidor suporta apenas a 1.1
        else:
            resposta = "Resposta não identificada"

        self.resposta = resposta
    
    def calcularTempo(self,inicio,fim):
        # Calcula o tempo total decorrido
        self.tempo = fim - inicio
        
    def salvarDfToCsv(self,df,arquivo):
        df.to_csv(arquivo,sep=';', header=True, )
        
    def gerarLogEndpoint(self,identificador,status,url,parametros,headers,inicio,fim,registros,origem, tipo="getdados"):
        log = open(f"{self.PATHLOG}\\log_apiana.txt", "a")
        
        texto = []
        
        self.calcularTempo(inicio,fim)
        
        texto.append(f"{tipo}")
        texto.append(f"{datetime.now()}")
        texto.append(f"{origem}")
        texto.append(f"{identificador}")
        texto.append(f"{status}")
        texto.append(f"{url}")
        #texto.append(f"{headers}")
        texto.append(f"{parametros}")
        texto.append(f"{inicio}")
        texto.append(f"{fim}")
        texto.append(f"{self.tempo}")
        texto.append(f"{registros}")
        
        for mensagem in texto:
            log.write(f"{mensagem} \t")
        log.write("\n")
        

        log.close()


#print(datetime.now())
#objteste = hidroWeb("cfgapiana.ini")
#objteste.getDadosHidroInventarioEstacoes("10100000")
#objteste.getDadosHidroSerieCotas("1992-08-01", "1993-08-02", True)
#print(datetime.now())
# objteste.dadosItens(objteste.df)
# objteste.atualizarTabela(cnx,'tbl_estacoes','ana',objteste.df)

