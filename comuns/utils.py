# Módulos nativos do Python 
import configparser
from datetime import datetime, timedelta
import inspect
import os
import pandas as pd
import requests
import shutil
import subprocess
import sys
import time
import traceback

# Módulos de terceiros ou bibliotecas externas que precisam ser instalados
## cryptography
try:
    from cryptography.fernet import Fernet
except ImportError:
    # Se o módulo não estiver instalado, instala-o
    dirPython = f"{sys.prefix}\\python.exe"
    subprocess.check_call([dirPython, "-m", "pip", "install", "cryptography"])
    
## selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service as ChromeService
except ImportError:
    # Se o módulo não estiver instalado, instala-o
    dirPython = f"{sys.prefix}\\python.exe"
    subprocess.check_call([dirPython, "-m", "pip", "install", "selenium"])
    

class setupIni():
    def __init__(self, arquivo):
        self.ckArquivo(arquivo)
        self.exibirMsg=True

    def ckArquivo(self, arquivo):
        if os.path.isfile(arquivo):
            self.config = configparser.ConfigParser()
            self.config.read(arquivo)
            self.status = True
        else:
            self.status = False
            print(f"Arquivo de configuração {arquivo} não existe")

    def ckSecao(self, secao):
        return self.config.has_section(secao)

    def ckChave(self, secao, chave):
        return self.config.has_option(secao, chave)

    def retValor(self, secao, chave, criptografado=False):
        if self.status and self.ckSecao(secao) and self.ckChave(secao, chave):
            valor = self.config.get(secao, chave)
            if criptografado and not valor:
                return descriptografar(valor)
            else:
                return valor
        else:
            return None

    def listaChaves(self, secao, excluir=None):
        lista = []
        if secao in self.config:
            for chave in self.config[secao]:
                if excluir is None or chave not in excluir:
                    lista.append(chave)

        return lista


# Manter essa função até migrar todos as rotinas para usar a classe setupIni() como utilizado no arquivo pymeoDados.py
def lerArqIni(arquivo):
    try:
        # Ler o arquivo config.ini
        config_obj = configparser.ConfigParser(interpolation=None)

        try:
            ## Verifica se o arquivo ini existe
            #### Se o arquivo ini estiver no mesmo diretório do arquivo.py não é necessário incluir o diretório
            if os.path.isfile(arquivo) == True:
                config_obj.read(arquivo)
            else:
                gerarLog([
                    "Arquivo config.ini não encontrado. Verifique se o arquivo está no mesmo diretório do arquivo executável"],
                    inspect.getframeinfo(inspect.currentframe()), True)
            
            try:
                #### Seção Database
                dbIniDB = config_obj["setup"]["sgdb"]

                if dbIniDB == 'sqlite':
                    usuario_banco = ''.decode('utf-8')
                    senha_banco = ''.decode('utf-8')
                else:
                    try:
                        # Descriptografar usuário do banco
                        user1 = config_obj[f"{dbIniDB}"][f"{dbIniDB}_user1"]
                        user2 = config_obj[f"{dbIniDB}"][f"{dbIniDB}_user2"]
                        usuario_banco = descriptografarSenha(user1, user2)
                    except Exception as e:
                        erro = str(e)
                        gerarLog([f"Problemas no parâmetro usuário do banco de dados. Verifique!"],inspect.getframeinfo(inspect.currentframe()),True)
                        gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)

                    try:
                        # Descriptografar senha do banco
                        password1 = config_obj[f"{dbIniDB}"][f"{dbIniDB}_password1"]
                        password2 = config_obj[f"{dbIniDB}"][f"{dbIniDB}_password2"]
                        senha_banco = descriptografarSenha(password1, password2)
                    except Exception as e:
                        erro = str(e)
                        gerarLog([f"Problemas no parâmetro senha do banco de dados. Verifique!"],inspect.getframeinfo(inspect.currentframe()),True)
                        gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)


                ##### Seção Browser
                dbIni = "url"
                if secaoExiste('url', config_obj):
                    try:
                        # Descriptografar usuário da URL
                        # usuario_url = descriptografarSenha(dbIni['url_user1'], dbIni['url_user2'])
                        user1 = config_obj[f"{dbIni}"][f"{dbIni}_user1"]
                        user2 = config_obj[f"{dbIni}"][f"{dbIni}_user2"]
                        usuario_url = descriptografarSenha(user1, user2)
                    except Exception as e:
                        erro = str(e)
                        gerarLog([f"Problemas no parâmetro usuário da URL. Verifique!"],
                                 inspect.getframeinfo(inspect.currentframe()), True)
                        gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)

                    try:
                        # Descriptografar senha da URL
                        # senha_url = descriptografarSenha(dbIni['url_password1'], dbIni['url_password1'])
                        password1 = config_obj[f"{dbIni}"][f"{dbIni}_password1"]
                        password2 = config_obj[f"{dbIni}"][f"{dbIni}_password2"]
                        senha_url = descriptografarSenha(password1, password2)
                    except Exception as e:
                        erro = str(e)
                        gerarLog([f"Problemas no parâmetro senha do usuário da URL. Verifique!"],
                                 inspect.getframeinfo(inspect.currentframe()), True)
                        gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)

                    vbrowser_padrao   = config_obj[f"{dbIni}"]['browser_padrao'].lower()
                    vpathchromedriver = config_obj[f"{dbIni}"]["pathchromedriver"]
                    vpathdownload = config_obj[f"{dbIni}"]["pathdownload"]
                    vurlprincipal = config_obj[f"{dbIni}"]["urlprincipal"]
                    vurlsecundaria = config_obj[f"{dbIni}"]["urlsecundaria"]
                    vuser_url = usuario_url.decode('utf-8')
                    vpwd_url = senha_url.decode('utf-8')
                else:
                    usuario_url=''.decode('utf-8')
                    senha_url=''.decode('utf-8')
                    vbrowser_padrao   = ''
                    vpathchromedriver = ''
                    vpathdownload =''
                    vurlprincipal = ''
                    vurlsecundaria = ''
                    vuser_url = ''
                    vpwd_url = ''

                resultado = {}
                try:
                    resultado = dict(sgdb=dbIniDB,
                                 db=config_obj[f"{dbIniDB}"][f"{dbIniDB}_db"],
                                 host=config_obj[f"{dbIniDB}"][f"{dbIniDB}_host"],
                                 port=config_obj[f"{dbIniDB}"][f"{dbIniDB}_port"],
                                 schema=config_obj[f"{dbIniDB}"][f"{dbIniDB}_schema"],
                                 user_banco=usuario_banco.decode('utf-8'),
                                 pwd_banco=senha_banco.decode('utf-8'),
                                 browser_padrao=vbrowser_padrao,
                                 pathchromedriver=vpathchromedriver,
                                 pathdownload=vpathdownload,
                                 urlprincipal=vurlprincipal,
                                 urlsecundaria=vurlsecundaria,
                                 user_url=vuser_url,
                                 pwd_url=vpwd_url)
                except Exception as e:
                    erro = str(e)
                    gerarLog([erro,f"Problemas ao gerar o resultado da leitura do arquivo ini. Verifique!"],
                                 inspect.getframeinfo(inspect.currentframe()), True)

                return resultado
            except Exception as e:
                erro = str(e)
                gerarLog([erro,f"Problemas nos parâmetros do arquivo de configuração. Verifique!"],
                         inspect.getframeinfo(inspect.currentframe()),
                         True)
                gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)
                
                
        except Exception as e:
            erro = str(e)
            gerarLog([erro,f"Problemas ao tentar ler o arquivo de configuração. Verifique!"],
                     inspect.getframeinfo(inspect.currentframe()),
                     True)
            gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)

        # self.host = self.configObj[self.sgdb]['host']
    except Exception as e:
        erro = str(e)
        gerarLog([
            f"Problemas no arquivo de configuração. Verifique!"
        ],
            inspect.getframeinfo(inspect.currentframe()),
            True)
        gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)


def gerarLog(texto,frame,status):
    try:
        data = retornarDataHoraAtual()
        # Retornar a linha formatada com 4 dígitos
        linha = '{:>4}'.format(frame.lineno)

        arquivo = frame.filename
        funcao = frame.function

        #contexto = inspect.getframeinfo(inspect.currentframe()).code_context
        #indice = inspect.getframeinfo(inspect.currentframe()).index
        #posicao = inspect.getframeinfo(inspect.currentframe()).positions

        # Abrir ou criar arquivo de log
        log = open("log.txt", "a")

        # Gravar texto no arquivo de log
        for mensagem in texto:
            log.write(f"{data} : {arquivo} ({funcao}) - Linha: {linha} \n ")
            log.write('{:>18}'.format(' '))
            log.write(f"{mensagem} \n")
            # Mostrar o texto na tela
            if status == True:
                print(mensagem)

        log.close()

    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "ERROS DO PYTHON:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        log.write("" + pymsg + "\n")
        log.close()

# Tratamento de erro
def gerarLogErro(frame,erro):
    try:
        data = retornarDataHoraAtual()
        # Retornar a linha formatada com 4 dígitos
        linha = '{:>4}'.format(frame.lineno)
        arquivo = frame.filename
        funcao = frame.function

        log = open("logErro.txt", "a")
        log.write("----------------------------" + "\n")
        log.write("----------------------------" + "\n")
        log.write(f"{data} : {arquivo} ({funcao}) - Linha: {linha} \n ")
        log.write('{:>18}'.format(' '))
        log.write(f"{erro} \n")

        # erro
        log.write(f"Descrição do erro:  {str(erro)} {traceback.format_exc()} \n")
        log.close()
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = f"Erros do Python : \n Traceback info: \n {tbinfo} \n {str(sys.exc_info()[1])}"
        log.write("" + pymsg + "\n")
        log.close()

# Retornar data e hora atual sem segundos
def retornarDataHoraAtual():
    data = datetime.now()
    return data.strftime("%d/%m/%Y %H:%M")

def compactar(arquivo,arquivos):
    z = zipfile.ZipFile(arquivo, 'w', zipfile.ZIP_DEFLATED)
    ##Criar uma estrutura para incluir o vetor de arquivos
    #z.write('config.ini')
    #z.write('results.txt')
    z.close()

def descompactar(arquivo,pasta):
    z = zipfile.ZipFile(arquivo, 'r')
    #print(arquivo)

    #Extrair arquivos no diretório atual
    #z.extractall()

    #Extrair arquivos no diretório especificado
    #print("pasta: ",pasta)
    z.extract(arquivo,pasta)

    #Extrair um arquivo específico
    #z.extract('data/US.txt', path='diretorio_de_saida')

    #Extrair com senha
    #z.extractall(pwd='SECRET2020')

    z.close()

def criptografarSenha(senha):
    ### Gerar chave
    chave = Fernet.generate_key()

    ### Criptografar senha usando chave gerada
    chaveRef = Fernet(chave)
    senhaBytes = bytes(senha, 'utf-8')  # convert into byte
    senhaCript = chaveRef.encrypt(senhaBytes)

    chave1 = chave.decode('utf-8')
    chave2 = senhaCript.decode('utf-8')

    return chave1,chave2
# Manter essa função até migrar todas para descriptografar
def descriptografarSenha(chave,senhaCript):
    encpwdbyt = bytes(senhaCript, 'utf-8')
    refKeybyt = bytes(chave, 'utf-8')

    # use the key and encrypt pwd
    keytouse = Fernet(refKeybyt)
    myPass = (keytouse.decrypt(encpwdbyt))
    #print(myPass)

    return myPass

def descriptografar(valor):
    # O valor a ser descriptografado deve ser composto por 2 valores separados por | (Ver função criptografar)
    chave,senhaCript = valor.split('|')
    encpwdbyt = bytes(senhaCript, 'utf-8')
    refKeybyt = bytes(chave, 'utf-8')

    # use the key and encrypt pwd
    keytouse = Fernet(refKeybyt)
    myPass = (keytouse.decrypt(encpwdbyt))
    #print(myPass)

    return myPass

def pastaVazia(pasta):
    #path = "D:/Pycharm projects/GeeksforGeeks/Nikhil"
    dir = os.listdir(pasta)
    if len(dir) == 0:
        return 'S'
    else:
        return 'N'

def criarPasta(pasta):
    try:
        if os.path.exists(pasta):
            # os.rmdir(pasta) rmdir apaga apenas se a pasta estiver vazia
            ## CUIDADO: O comando abaixo apaga a pasta antes de criar uma nova
            shutil.rmtree(pasta)

        os.makedirs(pasta)
    except Exception as e:
        erro = str(e)
        # print(erro)
        gerarLogErro(inspect.getframeinfo(inspect.currentframe()),erro)

# =====================================================================
# Funções relacionadas a páginas HTML
class configUrl():
    def __init__(self, browser, pathdownload):
        self.configBrowser(browser, pathdownload)
        #print("Navegador", self.navegador)

    def abrirUrl(self, url):
        if self.testarUrl(url) == 1:
            self.navegador.get(url)
            time.sleep(5)
        else:
            gerarLog([
                f"Url {url} não disponível. Verifique!"
            ],
                inspect.getframeinfo(inspect.currentframe()),
                False)

    def fecharUrl(self):
        self.navegador.quit()

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
    def testarUrl(self, url):
        statusHTTP = requests.get(url).status_code
        if statusHTTP == 200:
            # Url disponível
            return 1
        else:
            # Url não disponível
            return 0

    def altPastaDownload(self):
        pass

    def configBrowser(self, browser, pathdownload):
        try:
            self.browser = browser
            self.pathdownload = pathdownload

            if self.browser == "chrome":
                options = webdriver.ChromeOptions()
                options.add_argument('--ignore-certificate-errors')
                # service = ChromeService(executable_path=self.configObj['url']['pathchromedriver'])  # todo verificar na pasta informada se tem o chromedriver instalado, caso não tenha, instalar
                self.navegador = webdriver.Chrome(service=service, options=options)
            elif self.browser == "firefox":
                options = webdriver.FirefoxOptions()
                # options.add_argument('--ignore-certificate-errors')
                ## Definir diretório padrão para download - Apenas para o Firefox
                # options.set_preference("browser.download.folderList", 2)
                # options.set_preference("browser.download.dir", self.pathdownload)
                options.set_preference("browser.download.folderList", 2)
                options.set_preference("browser.download.dir", self.pathdownload)
                self.navegador = webdriver.Firefox(options=options)
                self.navegador = webdriver.Firefox(options=options)
            elif self.browser == "edge":
                options = webdriver.EdgeOptions()
                options.add_argument('--ignore-certificate-errors')
                self.navegador = webdriver.Edge(options=options)
            elif self.browser == "ie":
                options = webdriver.IeOptions()
                options.add_argument('--ignore-certificate-errors')
                self.navegador = webdriver.Ie(options=options)
        except Exception as e:
            erro = str(e)
            gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)


# Verificar qual programa é usado e substituir pela classe spuUrl
# def navegadorAbrir():
#     try:
#         browser = lerArqIni("config.ini")
#
#         # Criar pasta temporária para download
#         criarPasta(browser.get('pathdownload'))
#
#         if browser.get('browser_padrao') == "chrome":
#             options = webdriver.ChromeOptions()
#             options.add_argument('--ignore-certificate-errors')
#             # options.add_argument('accept_insecure_certs=true') #TODO: Ver como usa a opção accept_insecure_certs para ignorar o certificado
#             service = ChromeService(executable_path=browser.get(
#                 'pathchromedriver'))  # todo verificar na pasta informada se tem o chromedriver instalado, caso não tenha, instalar
#             navegador = webdriver.Chrome(service=service, options=options)
#         elif browser.get('browser_padrao') == "firefox":
#             options = webdriver.FirefoxOptions()
#             # options.add_argument('--ignore-certificate-errors')
#             ## Definir diretório padrão para download - Apenas para o Firefox
#             options.set_preference("browser.download.folderList", 2)
#             options.set_preference("browser.download.dir", browser.get('pathdownload'))
#             navegador = webdriver.Firefox(options=options)
#         elif browser.get('browser_padrao') == "edge":
#             options = webdriver.EdgeOptions()
#             options.add_argument('--ignore-certificate-errors')
#             navegador = webdriver.Edge(options=options)
#         elif browser.get('browser_padrao') == "ie":
#             options = webdriver.IeOptions()
#             options.add_argument('--ignore-certificate-errors')
#             navegador = webdriver.Ie(options=options)
#         return navegador
#     except Exception as e:
#         erro = str(e)
#         # print(erro)
#         gerarLogErro(inspect.getframeinfo(inspect.currentframe()), erro)


def validarSenha(senha):
    """
    Validar a senha
    Condições
    Com mais de 8 caracteres
    Possuir pelo menos 1 número
    Possuir pelo menos 1 caractere

    Retorna True ou False
    :param senha: 
    :return:
    """
    if len(senha) < 8:
        return False
    elif not any(char.isdigit() for char in senha):
        return False
    elif not any(char.isalpha() for char in senha):
        return False
    else:
        return True

def exportarArquivo(df,nomeArquivo,exportar,colunas,log):
    pass

# Converter string
def string_to_snake_case(string):
    # Usar a função em um dataframe
    # df.columns = [string_to_snake_case(column) for column in df.columns]
    import re

    string = re.sub("/", " ", string)  # substitui / por espaço
    string = re.sub(" +", " ", string)  # substitui múltiplos espaços por um espaço
    string = re.sub(" ", "_", string)  # substitui espaço por _
    string = re.sub("([a-z0-9])([A-Z])", r"\1_\2", string)  # adiciona _ entre letras minúsculas e maiúsculas
    return string.lower()


def verArqini(arquivo):
    lerArqIni(arquivo)
    parametros = lerArqIni(arquivo)
    sgdb = parametros['sgdb']
    db = parametros['db']
    host = parametros['host']
    port = parametros['port']
    schema = parametros['schema']
    user = parametros['user_banco']
    pwd = parametros['pwd_banco']
    print(f"Database {sgdb}")
    print(f"Banco {db}")
    print(f"Schema {schema}")
    print(f"Host {host}")
    print(f"Porta {port}")
    print(f"User {user}")
    print(f"Pwd {pwd}")

def secaoExiste(secao,arquivo):
    if secao in arquivo:
        return True
    else:
        return False

def gerarDf(tipo, arquivo, planilha=None, delimitador="\t", formato='utf-8', ignorarLinhas=0):
    df = pd.DataFrame()
    try:
        if tipo == 'csv':
            if formato=='utf-8' and validarArqUTF8(arquivo)==False:
                formatarArquivo(arquivo)
            df = pd.read_csv(arquivo, delimiter=delimitador, encoding=formato, skiprows=ignorarLinhas, engine='c')
        elif tipo == 'xlsx':
            df = pd.read_excel(arquivo, engine='openpyxl', sheet_name=planilha)
    except Exception as e:
        erro = str(e)
        gerarLog(
                        [f"### Linha: {'{:>4}'.format(inspect.getframeinfo(inspect.currentframe()).lineno)} - Erro ao tentar criar o dataframe a partir do arquivo {arquivo}.",
                         erro
                         ],
                        inspect.getframeinfo(inspect.currentframe()),
                        True)
    return df

def gerarDadosViaDf(df, tabela, cnx, sql=None):
    # O sql é um parâmetro opcional que pode ser executado durante a atualização dos dados. Ver o exemplo em pymeoDados.py
    try:
        df.to_sql(tabela, con=cnx.con, if_exists='append', index=False)
        if sql is not None:
            cnx.executarDML(sql)
    except Exception as e:
        erro = str(e)
        gerarLog(
                        [f"### Linha: {'{:>4}'.format(inspect.getframeinfo(inspect.currentframe()).lineno)} - Problemas ao tentar exportar a tabela {tabela} a partir do Dataframe.",
                         erro
                         ],
                        inspect.getframeinfo(inspect.currentframe()),
                        True)

# Função que identifica se o arquivo está no formato UTF-8, caso não esteja deverá ser executado a função formatarArquivo
def validarArqUTF8(arquivo):
    try:
        # Abre o arquivo para leitura em modo texto com codificação UTF-8
        with open(arquivo, 'r', encoding='utf-8') as arqtemp:
            # Ler o conteúdo do arquivo
            arqtemp.read()
        return True  # Se não ocorrer nenhum erro, o arquivo está em UTF-8
    except UnicodeDecodeError:
        # Se ocorrer um erro de decodificação, o arquivo não está em UTF-8
        return False
    except FileNotFoundError:
        print(f"Arquivo '{arquivo}' não encontrado.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
        return None

# Copiar o arquivo no formato UTF-8 para eliminar sujeiras que estavam prejudicando a exportação
def formatarArquivo(arquivo):
    with open(arquivo, 'r', encoding='utf-16') as tmporigem:
        conteudo = tmporigem.read()

    # Nome do arquivo sem o caminho e sem a extensão
    arq1, _ = os.path.splitext(os.path.basename(arquivo))
    # Novo arquivo que irá receber o conteúdo no formato UTF-8
    arq2 = f"{arq1}_copia.csv"

    with open(arq2, 'w', encoding='utf-8') as tmpdestino:
        tmpdestino.write(conteudo)

    # Copia o arquivo no formato UTF-8 para o arquivo anterior
    shutil.copy(arq2, arquivo)

def limparString(text):
    try:
        import re
        import unicodedata
    except ImportError:
        # Instalar o módulo caso não esteja
        dirPython = f"{sys.prefix}\\python.exe"
        subprocess.check_call([dirPython, "-m", "pip", "install", "re"])
        subprocess.check_call([dirPython, "-m", "pip", "install", "unicodedata"])
    
    """
    Remove acentos, substitui espaços por underscores e remove caracteres não alfanuméricos.

    Args:
    - text (str): A string de entrada que precisa ser limpa.

    Returns:
    - str: A string limpa com letras sem acento, números e underscores.
    """
    # Normaliza a string, separando os caracteres acentuados de seus diacríticos
    text = unicodedata.normalize('NFD', text)
    # Remove os diacríticos (acentos) mantendo apenas os caracteres básicos
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    # Substitui espaços por underscores
    text = text.replace(' ', '_')
    text = text.replace('-', '_')
    # Remove caracteres que não são letras, números ou _
    text = re.sub(r'[^A-Za-z0-9_]', '', text)
    return text
    
    
#verArqini('config.ini')

