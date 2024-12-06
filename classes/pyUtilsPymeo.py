# pyUtilsPymeo.py - Classe em Python com as funções personalizadas a serem utilizadas com os dados e sistemas do Pymeo
#                   Será necessário separar do arquivo utils, pq no utils tem vários módulos que para serem usados
#                   precisam ser instalados no QGis
# Módulos nativos do Python 
import configparser
import datetime
from datetime import datetime
import fnmatch
import glob
import logging
import os
import subprocess
import sys
import time
import traceback
import zipfile

# Módulos específicos para o QGis
from qgis.PyQt.QtCore import Qt, QThread, pyqtSignal
from qgis.PyQt.QtGui import QColor, QFont, QMovie
from qgis.PyQt.QtWidgets import QCheckBox, QComboBox, QDialog, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget

# Módulos desenvolvidos para o Pymeo
from pymeo.classes.calcMeo import meo
from pymeo.classes.apiAna import hidroWeb
from pymeo.config import PATH, PATHARQUIVOS, PATHCOMUNS, PATHEXCEL, PATHCSV, PATHLOG, PATHPYTHON

sys.path.insert(0, PATHCOMUNS)
import utils

# Módulos de terceiros ou bibliotecas externas que precisam ser instalados
## sqlalchemy
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select
except ImportError:
    # Módulo será instalado, senão existir
    subprocess.check_call([PATHPYTHON, "-m", "pip", "install", "selenium"])

# Função para configurar o log usando a biblioteca logging
# identificador: nome que irá definir a origem das mensagens de log podendo ser nome de um módulo, classe ou funcionalidade específica.
def cfgLogger(identificador, arquivo):
    logger = logging.getLogger(identificador)
    logger.setLevel(logging.INFO)
    
    # Criar um manipulador para escrever no arquivo
    handler = logging.FileHandler(arquivo)
    handler.setLevel(logging.INFO)
    
    # Definir o formato do log
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Adiciona o manipulador ao logger
    logger.addHandler(handler)
    
    return logger


class CalcularMeoThread(QThread):
    final = pyqtSignal(int)  # Sinal para indicar que o cálculo terminou
    erro  = pyqtSignal(str)

    def __init__(self, codEstacao, arquivo=None):
        super().__init__()
        
        self.codEstacao = codEstacao
        self.resultado = 0
        self.arquivo = arquivo
        self.origemValorMeo = None

    def run(self):
        try:          
          if self.arquivo:
            # Tipo 1 - Via Csv
            origemValorMeo = 'Via Arquivo Csv'
            if os.path.exists(self.arquivo):
               objMeo = meo(1)    
               objMeo.calcularMeo(self.codEstacao, origem=origemValorMeo, arqCsv=self.arquivo)
               self.resultado = objMeo.resultado
            else:
               self.resultado = -99
               print(f"Arquivo {self.arquivo} não encontrado!")
          else:
            # Tipo 0 - Via api
            origemValorMeo = 'Via Api da ANA'
            objMeo = meo(0)
            objMeo.calcularMeo(self.codEstacao, origem=origemValorMeo, arqCsv=self.arquivo)
            self.resultado = objMeo.resultado
          
          #objMeo.gerarMemoriaCalculo(10100000, 2, 1300.72)
          
          self.final.emit(self.resultado)
        except Exception as e:
          self.erro.emit(str(e))
          print(str(e))

# Criar uma janela para mostrar todas as estações selecionadas e definir as opções de cálculo da MEO
# Se o cálculo será feito via Api ou via Arquivo Csv
# Se irá atualizar os dados
class dialogEstacoes(QDialog):
    def __init__(self, selecionados, parent=None):
        super().__init__(parent)
        
        self.selecionados = selecionados
        
        self.resultado = 0

        self.gerarLayout()
    
    
    def gerarLayout(self):
        self.resize(800, 600) 
                
        ########################################################
        # Criar a interface da classe
        self.setWindowTitle("Gerar cálculo da Meo")
        

        # Layout principal
        self.layout = QVBoxLayout()

        ########################################################
        # Frame Superior
        frmSuperior = QVBoxLayout()

        frmSuperior.addWidget(QLabel("Escolha a origem dos dados"))
        
        # Lista que define a origem dos dados que será usada no cálculo
        # 0 - Via Api da ANA
        # 1 - Via Arquivo Csv (Valor default)
        self.combobox = QComboBox()
        self.combobox.addItems(["Via Api da ANA", "Via Arquivo Csv"])
        self.combobox.setCurrentIndex(1)
        self.combobox.currentIndexChanged.connect(self.toggle_csv_input)
        frmSuperior.addWidget(self.combobox)

        # LineEdit que define o caminho arquivo para a origem de dados do tipo Via Arquivo Csv
        self.pathPastaCsv = QLineEdit()
        self.pathPastaCsv.setPlaceholderText("Selecione a pasta contendo os arquivos CSV")
        self.pathPastaCsv.setText(PATHCSV)
        
        # 
        self.btnPasta = QPushButton("Selecionar Pasta")
        self.btnPasta.clicked.connect(self.selecionarPasta)

        frmSuperior.addWidget(QLabel("Pasta dos arquivos Csv"))
        frmSuperior.addWidget(self.pathPastaCsv)
        frmSuperior.addWidget(self.btnPasta)

        self.layout.addLayout(frmSuperior)
        
        ########################################################
        # Frame Central - QTableWidget para os selecionados
        # Colunas
        # codEstacao: self.selecionados[0]
        # ufEstacao: self.selecionados[1]
        # nomeEstacao: self.selecionados[2]
        # codEstacao: self.selecionados[5]
        frmCentral = QVBoxLayout()
        self.tbSelecionados = QTableWidget(0, 7)  
        self.tbSelecionados.setHorizontalHeaderLabels(["Código", "Rio", "Estação", "Município", "MEO", "Ult. Atualização", "Nova MEO"])

        frmCentral.addWidget(self.tbSelecionados)

        # Adiciona os itens selecionados ao QTableWidget
        self.preencherItens(self.selecionados)

        # Box inferior
        boxInferior = QHBoxLayout()

        # Checkbox para Atualizar dados (padrão: True)
        self.ckDados = QCheckBox("Atualizar dados")
        self.ckDados.setChecked(True)
        boxInferior.addWidget(self.ckDados)
        
        # Checkbox para fazer o download do arquivo CSV caso a origem dos dados seja Via arquivo CSV 
        self.ckDownload = QCheckBox("Download do arquivo Csv")
        self.ckDownload.setChecked(True)
        boxInferior.addWidget(self.ckDownload)
        
        # Checkbox para exportar o cálculo da MEO
        self.ckExportar = QCheckBox("Exportar cálculo da MEO")
        self.ckExportar.setChecked(True)
        boxInferior.addWidget(self.ckExportar)

        frmCentral.addLayout(boxInferior)

        self.layout.addLayout(frmCentral)
        ########################################################
        # Frame Inferior - Botões OK e Cancelar
        frmInferior = QHBoxLayout()
        self.btnOk = QPushButton("OK")
        self.btnCancelar = QPushButton("Cancelar")
        self.btnOk.clicked.connect(self.accept)
        self.btnCancelar.clicked.connect(self.reject)

        frmInferior.addWidget(self.btnOk)
        frmInferior.addWidget(self.btnCancelar)

        self.layout.addLayout(frmInferior)
        ########################################################

        self.setLayout(self.layout)

    def preencherItens(self, selecionados):
        """Preenche a tabela (qtablewidget) com os itens selecionados na tela principal"""
        
        # Definir o número de linhas baseado no total de registros selecionados
        self.tbSelecionados.setRowCount(len(selecionados))

        # Selecionar as colunas desejadas
        for row, item in enumerate(selecionados):
            self.tbSelecionados.setItem(row, 0, QTableWidgetItem(item[0]))
            self.tbSelecionados.setItem(row, 1, QTableWidgetItem(item[1]))
            self.tbSelecionados.setItem(row, 2, QTableWidgetItem(item[2]))
            self.tbSelecionados.setItem(row, 3, QTableWidgetItem(item[3]))
            self.tbSelecionados.setItem(row, 4, QTableWidgetItem(item[4]))
            self.tbSelecionados.setItem(row, 5, QTableWidgetItem(item[5]))
            # self.tbSelecionados.setItem(row, 6, QTableWidgetItem(item[6]))
    
    def calcularMeoDialog(self):
        self.listaValorMeoNovo = []
        self.listaCodEstacao = []
        self.listaArqCsv = []
        for i in range(self.tbSelecionados.rowCount()):
            item = self.tbSelecionados.item(i, 0) 
            if item is not None:  
                self.listaCodEstacao.append(item.text())
                self.listaArqCsv.append(os.path.join(self.pathPastaCsv.text(), f"{item.text()}_Cotas.csv"))

        # 0 - ApiAna
        # 1 - Csv
        origem = self.obterOrigem()
        
        try:
            for codEstacao, arqCsv in zip(self.listaCodEstacao, self.listaArqCsv):
                self.resultado = 0
                self.codEstacao = codEstacao
                
                # Gerar a caixa de diálogo para mostrar o Gif
                gif_dialog = QDialog()
                gif_dialog.setWindowTitle(f"Calculando a MEO da Estação: {codEstacao}")
                gif_dialog.setWindowModality(Qt.ApplicationModal)
                
                gif_label = QLabel(gif_dialog)
                dirImages = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                gif_movie = QMovie(f"{dirImages}\\images\loading.gif")  
                gif_label.setMovie(gif_movie)
                
                layout = QVBoxLayout()
                layout.addWidget(gif_label)
                gif_dialog.setLayout(layout)
                
                # Iniciar o GIF e exibir o diálogo
                gif_movie.start()
                
                #if utils.validarArqUTF8(arqCsv) == False:
                #    utils.formatarArquivo(arqCsv)
                
                
                if origem==0:
                    self.thread = CalcularMeoThread(codEstacao)

                if (origem==1):
                    if os.path.exists(arqCsv)==False:
                        downloadEstacao(codEstacao)
                        
                    self.thread = CalcularMeoThread(codEstacao, arquivo=arqCsv)
                
                
                # Conectar o sinal de conclusão da thread para parar o GIF e fechar o diálogo
                self.thread.final.connect(gif_movie.stop)
                self.thread.final.connect(gif_dialog.accept)
                self.thread.final.connect(self.onCalculoMeoConcluido)
            
                self.thread.start()
                
                gif_dialog.exec_()
                # print(f"Resultado Thread: {self.thread.resultado}")
        except Exception as e:
            erro = str(e)
            tb = traceback.format_exc()
            print(f"Erro {erro} ao executar a Thread. Verifique \n", tb)  

        
    def onCalculoMeoConcluido(self, resultado):
        # Função que é chamada quando o cálculo é concluído
        # Valor do resultado ok
        codigo = self.codEstacao
        valor = self.thread.resultado

        # Percorrendo todas as linhas da tabela
        for i in range(self.tbSelecionados.rowCount()):
            item = self.tbSelecionados.item(i, 0)
            if item is not None and item.text() == codigo:
                self.tbSelecionados.setItem(i, 4, QTableWidgetItem(str(valor)))
        
        self.listaValorMeoNovo.append(valor)
        
        
    def toggle_csv_input(self):
        if self.combobox.currentIndex() == 0:
            self.pathPastaCsv.hide()
            self.btnPasta.hide()
            self.ckDownload.hide()
        else:
            self.pathPastaCsv.show()
            self.btnPasta.show()
            self.ckDownload.show()

    def selecionarPasta(self):
        # Diálogo para selecionar a pasta
        pasta = QFileDialog()
        pathPastaCsv = pasta.getExistingDirectory(self, "Selecione a pasta com os arquivos CSV")
        if pathPastaCsv:
            self.pathPastaCsv.setText(pathPastaCsv)
    
    def obterOrigem(self):
        """Retorna a opção selecionada no ComboBox (viaAPI ou viaCSV)"""
        # 0 - Via Api da ANA
        # 1 - Via Arquivo Csv
        return self.combobox.currentIndex()
        """
    #def obterListaCodEstacao(self):
    #    Retorna a lista de códigos da primeira coluna do QTableWidget
    #    codes = []
    #    for row in range(self.tbSelecionados.rowCount()):
    #        code_item = self.tbSelecionados.item(row, 0)  # Coluna [0] contém o código
    #        if code_item:
    #            codes.append(code_item.text())
    #    return codes
        
    # def process_data(self):
    #     # Processo de execução
    #     folder = self.pathPastaCsv.text()
    #     if not folder:
    #         QMessageBox.warning(self, "Erro", "Por favor, selecione uma pasta contendo os arquivos CSV.")
    #         return
    # 
    #     for row in range(self.tbSelecionados.rowCount()):
    #         code_item = self.tbSelecionados.item(row, 0)  # Coluna [0] contém o código
    #         if code_item:
    #             code = code_item.text()
    #             file_name = os.path.join(folder, f"{code}_2021.csv")
    #             if os.path.exists(file_name):
    #                 # Aqui você pode chamar a ação que deseja executar com o arquivo
    #                 self.execute_action(file_name)
    #             else:
    #                 QMessageBox.warning(self, "Erro", f"Arquivo {file_name} não encontrado.")
    #     self.accept()
    # 
    # def execute_action(self, file_name):
    #     # Sua ação com o arquivo
    #     print(f"Executando ação com o arquivo: {file_name}")

# Exemplo de como chamar o diálogo em outra parte do plugin
#def chamarQDialog(self, selecionados):
#    Função que recebe os dados selecionados e abre o QDialog
#    dialog = dialogEstacoes(selecionados)
#    
#    # Executa o diálogo
#    if dialog.exec_() == QDialog.Accepted:
#        # Obtém a opção selecionada (viaCSV ou viaAPI)
#        selected_option = dialog.obterOrigem()
#        
#        # Obtém a lista de códigos da primeira coluna
#        codes = dialog.obterListaCodEstacao()
#        
#        print(f"Opção selecionada: {selected_option}")
#        print(f"Códigos: {codes}")
#    else:
#        print("Ação cancelada")
#
        """

class dlgArquivosCalculados(QDialog):
    ########################################################
    # Criar a interface da classe que mostra a lista de arquivos calculados
    ########################################################
    #
    # pathArquivos = f"D:\\Desenvolvimento\\QGIS 3.34.4\\apps\\qgis-ltr\\python\\plugins\\pymeo\\arquivos"
    # selecionados = lista de itens da tabela da tela anterior
    #
    # dirArquivos = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\arquivos'))
    # arquivo = f"{PATHARQUIVOS}\\{codEstacao}_{dtAtual}_{utils.limparString(self.nomeRio)}.xlsx"

    def __init__(self, pathArquivos, selecionados):
        """Inicializar a classe dlgArquivosCalculados"""
        super().__init__()
        ########################################################
        # Configuração do layout da janela        
        self.resize(900, 600) 

        self.setWindowTitle("Cálculo da Meo - Arquivos gerados")

        # Layout principal
        self.layout = QVBoxLayout()
        
        self.pathArquivos = pathArquivos
        self.selecionados = selecionados
        
        ########################################################
        # Frame Superior
        frmSuperior = QVBoxLayout()
        
        # Adicionar os elementos que irão compor a layout superior
        # frmSuperior.addWidget(QLabel("Escolha a origem dos dados"))
        
        self.layout.addLayout(frmSuperior)
        
        ########################################################
        # Frame Central
        frmCentral = QVBoxLayout()
        self.tbArquivos = QTableWidget() 
        self.tbArquivos.setColumnCount(7)        
        self.tbArquivos.setHorizontalHeaderLabels(["Selecionar","Código", "UF", "Estação", "MEO", "Arquivo", "Ult. Modificação"])
        
        # Adicionar a tabela a parte central da tela
        frmCentral.addWidget(self.tbArquivos)

        # Adiciona os itens selecionados ao QTableWidget
        self.listarArquivos(self.selecionados)
        
        
        # Botões OK e Cancelar
        # button_layout = QHBoxLayout()
        # ok_button = QPushButton("OK")
        # cancel_button = QPushButton("Cancelar")
        # ok_button.clicked.connect(self.accept)
        # cancel_button.clicked.connect(self.reject)
        # 
        # button_layout.addWidget(ok_button)
        # button_layout.addWidget(cancel_button)
        
        # Adiciona a tabela e os botões ao layout principal
        self.layout.addWidget(self.tbArquivos)
        #layout.addLayout(button_layout)
        self.setLayout(self.layout)
        self.tbArquivos.resizeColumnsToContents()
    
    def listarArquivos(self, selecionados):
        """Preenche a tabela (qtablewidget) com os itens selecionados na tela principal"""
        
        # Definir o número de linhas baseado no total de registros selecionados
        self.tbArquivos.setRowCount(len(selecionados))
        
        # Preenchendo a tabela com as informações
        for linha, item in enumerate(selecionados):
            # Adicionar a coluna checkbox para seleção dos arquivos que serão abertos
            ckItem = QWidget()
            ckBox = QCheckBox()

            ckLayout = QHBoxLayout()
            ckLayout.addWidget(ckBox)
            ckLayout.setAlignment(Qt.AlignCenter)
            ckLayout.setContentsMargins(0, 0, 0, 0)
            
            ckItem.setLayout(ckLayout)
            
            self.tbArquivos.setCellWidget(linha, 0, ckItem)
            
            # Adicionar os itens 
            # Código, UF, Estação, Valor da Meo
                        
            codEstacao = item[0]
            ufEstacao = item[1]
            nomeEstacao = item[2]
            valorMeo = item[5]
            self.tbArquivos.setItem(linha, 1, QTableWidgetItem(item[0]))
            self.tbArquivos.setItem(linha, 2, QTableWidgetItem(item[6]))
            self.tbArquivos.setItem(linha, 3, QTableWidgetItem(item[2]))
            self.tbArquivos.setItem(linha, 4, QTableWidgetItem(item[4]))

            self.tbArquivos.setHorizontalHeaderLabels(["Selecionar","Código", "UF", "Estação", "MEO", "Arquivo", "Ult. Modificação"])

            dtAtual = datetime.now().strftime('%Y%m%d')
            pathArquivo = f"{PATHARQUIVOS}\\{codEstacao}*.xlsx"
            arquivo = self.pesquisarArquivo(pathArquivo)
                        
            if arquivo:
                nomeArquivo = os.path.basename(arquivo)            # Extrai apenas o nome do arquivo
                
                # Obtém o timestamp de modificação do arquivo
                timestamp = os.path.getmtime(arquivo)
                # Converte o timestamp para datetime
                dataHora = datetime.fromtimestamp(timestamp)
                # Formata para o formato brasileiro
                dtArquivo = dataHora.strftime("%d/%m/%Y %H:%M:%S")
                itemArquivo = QTableWidgetItem(nomeArquivo)        # Criar um item de tabela para exibir o nome do arquivo          
                itemArquivo.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled) # Definir o item da tabela como selecionável e habilitado, mas não editável
                itemArquivo.setData(Qt.UserRole, arquivo)      # Armazenar o caminho completo do arquivo como um dado extra no item
                itemArquivo.setForeground(Qt.blue)             # Cor azul para parecer link
                fonte = itemArquivo.font()                     # Obter a fonte atual do item
                fonte.setUnderline(True)                       # Definir o sublinhado
                itemArquivo.setFont(fonte)                     # Aplicar a fonte ao item
                ckBox.setChecked(True)                         # Marcar o ckeckbox do item
                itemArquivo.setForeground(QColor("green"))     # Definir a cor do texto como verde
                self.tbArquivos.setItem(linha, 5, itemArquivo) # Adicionar o item do arquivo configurado na tabela
                self.tbArquivos.setItem(linha, 6, QTableWidgetItem(dtArquivo)) # Adicionar o item do arquivo configurado na tabela
            else:
                nomeArquivo = "Arquivo não encontrado"
                itemArquivo = QTableWidgetItem(nomeArquivo)        # Criar um item de tabela para exibir o nome do arquivo          
                ckBox.setChecked(False)
                itemArquivo.setForeground(QColor("red"))
                # Não vi funcionalidade dos comandos abaixo. Avaliar ao fazer o teste
                #for col in range(6):
                #    self.tbArquivos.itemArquivo(linha, col).setBackground(QColor("#ffcccc"))  # Fundo da linha vermelho claro
                self.tbArquivos.setItem(linha, 5, itemArquivo) # Adicionar o item do arquivo configurado na tabela
                self.tbArquivos.setItem(linha, 6, QTableWidgetItem(""))
            
            # Conecta o clique na célula do arquivo para abrir no Excel
            # Os parâmetros linha e coluna usados na função clickArquivo 
            # são fornecidos pelo evento cellClicked
            self.tbArquivos.cellClicked.connect(self.clickArquivo)
            
    def pesquisarArquivo(self,valor):
        # Usa glob para encontrar arquivos que correspondam ao valor
        arquivos = glob.glob(valor)
        
        # Verifica se algum arquivo foi encontrado
        if arquivos:
            # Ordena os arquivos pelos arquivos mais recentes (data de modificação)
            arquivos.sort(key=os.path.getmtime, reverse=True)
            return arquivos[0]  # Retorna o primeiro arquivo encontrado
        else:
            return None  # Retorna None se nenhum arquivo foi encontrado
    
    def clickArquivo(self, linha, coluna):
        # Obtém o item da célula clicada
        item = self.tbArquivos.item(linha, coluna)
        
        # Obter o ckeckbox da linha clicada
        ckWidget = self.tbArquivos.cellWidget(linha, 0)
        # ItemAt(0) se refere ao primeiro item do layout, que foi o ckeckbox
        checkbox = ckWidget.layout().itemAt(0).widget()
        
        if checkbox.isChecked():
            if item:
                # Obtém o caminho completo do arquivo a partir do UserRole
                pathArquivo = item.data(Qt.UserRole)
                print(pathArquivo)
                
                # Abra o arquivo (substitua pelo código para abrir o Excel)
                if pathArquivo:
                    try:
                        subprocess.Popen([PATHEXCEL, pathArquivo])  # Tenta abrir no Excel
                    except Exception as e:
                        print(f"Erro ao abrir o arquivo: {e}")
        else:
            print("Arquivo não selecionado. Verifique se o arquivo existe")

class downloadEstacao():
    def __init__(self,codigo):
        self.codEstacao = codigo
        
        # Path da pasta onde os arquivos serão baixados
        self.pathDownload = f"{PATHCSV}\\temp"
        if not os.path.exists(self.pathDownload):
            os.makedirs(self.pathDownload)

        self.pathCsv = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\csv'))
        
        # Criar arquivo de log a partir da função cfgLogger que usa a biblioteca logging
        arqlog = f"{PATHLOG}\\{self.codEstacao}.log"
        # Instância do objeto de log
        self.logger = cfgLogger("downloadEstacao", arqlog)

        self.dwnEstacao()
        
        self.extrairCotas()
        
        self.closeLog()
        
    def closeLog(self):
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)
            
    """Função para acessar as séries históricas do Portal Hidroweb e 
       fazer o download do arquivo CSV
    """
    def dwnEstacao(self):
        try:
            
            options = Options()
            options.headless = True  # Executar em modo headless (Ocultar o browser durante a execução do robô)

            # Configurar preferências para a pasta de download
            cfgDownload = webdriver.FirefoxProfile()
            cfgDownload.set_preference("browser.download.folderList", 2)        # Escolher pasta personalizada
            cfgDownload.set_preference("browser.download.dir", self.pathDownload)    # Define o caminho da pasta
            cfgDownload.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/vnd.ms-access,text/plain")  # Exemplo para PDFs, altere conforme necessário
            
            # Adiciona o perfil às opções
            options.profile = cfgDownload
            
            # Inicializa o navegador
            navegador = webdriver.Firefox(options=options)

            #navegador = webdriver.Firefox(options=options)
            
            # todo: Alterar a pasta de download para a pasta de self.pathDownload
                    
            navegador.get("https://www.snirh.gov.br/hidroweb/serieshistoricas")
        
            wait = WebDriverWait(navegador, 10)
        
            tipoEstacao = wait.until(EC.presence_of_element_located((By.ID, "mat-select-0")))
            tipoEstacao.send_keys("Fluviométrica")
        
            codEstacao = wait.until(EC.presence_of_element_located((By.ID, "mat-input-0")))
            codEstacao.send_keys(self.codEstacao)
        
            # btnConsultar = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(.,'search Consultar')]")))
            # btnConsultar = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/mat-sidenav-container/mat-sidenav-content/ng-component/form/ana-card/mat-card/mat-card-content/mat-card-actions/div/div/button[1]")))
            btnConsultar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR , "button.mat-flat-button > span:nth-child(1)")))
            btnConsultar.click()            
        
            time.sleep(3)
            # btnDownloadCsv = wait.until(EC.element_to_be_clickable((By.XPATH, "//mat-tab-body[@id='mat-tab-content-0-0']/div/ana-card/mat-card/mat-card-content/ana-dados-convencionais-list/div/div/table/tbody/tr/td[6]/button/span/mat-icon")))
            btnDownloadCsv = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td.mat-cell:nth-child(6) > button:nth-child(1) > span:nth-child(1) > mat-icon:nth-child(1)")))
            btnDownloadCsv.click()
        
            time.sleep(10)
        
            navegador.quit()
            self.logger.info(f"{datetime.now()} \t {self.codEstacao} \t Download realizado com sucesso")
        except Exception as e:
            erro = traceback.format_exc()  # Captura o traceback completo
            self.logger.error(f"{datetime.now()} \t {self.codEstacao} \t {e} \t {erro} \n")
        
    def extrairCotas(self):
        try:
            # Pasta temporária que será usada para armazenar o arquivo que será extraído
            arquivo = self.pesquisarArquivo(self.pathDownload , self.codEstacao)
        
            if arquivo:    
                pathArqZip = os.path.join(self.pathDownload, arquivo)  # Caminho completo do arquivo ZIP
                dirfinal = os.path.join(self.pathCsv) # Diretório de destino
        
                arqCota = f"{self.codEstacao}_Cotas.csv"
        
                # Verifica se o diretório de destino existe, criando se não existir
                if not os.path.exists(dirfinal):
                    os.makedirs(dirfinal)
        
                # Tenta abrir e extrair o arquivo ZIP
                try:
                    with zipfile.ZipFile(pathArqZip, 'r') as z:
                        # Lista todos os arquivos dentro do ZIP
                        listaArqNoZip = z.namelist()
        
                        # Verifica se o arquivo específico está dentro do ZIP
                        if arqCota in listaArqNoZip:
                            # Extrai apenas o arquivo desejado
                            z.extract(arqCota, dirfinal)
                        else:
                            mensagem = f"Arquivo '{arqCota}' não encontrado no ZIP."
                            self.logger.info(f"{datetime.now()} \t {self.codEstacao} \t {mensagem} \n")
                except zipfile.BadZipFile:
                    erro = "Arquivo ZIP corrompido ou inválido."
                    self.logger.error(f"{datetime.now()} \t {self.codEstacao} \t {erro} \n")
                except Exception as e:
                    erro = traceback.format_exc()
                    self.logger.error(f"{datetime.now()} \t {self.codEstacao} \t {e} \t {erro} \n")
        
                # Excluir o arquivo após sua extração
                os.remove(arquivo)
                
                logging.info(f"{datetime.now()} \t {self.codEstacao} \t Download realizado com sucesso")
            else:
                mensagem = f"Arquivo {arquivo} não encontrado"
                self.logger.info(f"{datetime.now()} \t {self.codEstacao} \t {mensagem} \n")
        except Exception as e:
            # Captura o traceback completo
            erro = traceback.format_exc()  
            self.logger.error(f"{datetime.now()} \t {self.codEstacao} \t {e} \t {erro} \n")
    
    def pesquisarArquivo(self, diretorio, codigo):
        # Listar todos os arquivos no diretório
        for arquivo in os.listdir(diretorio):
            # Verificar se o nome do arquivo corresponde ao padrão e tem a extensão .zip
            if fnmatch.fnmatch(arquivo, f'Estacao_{codigo}_CSV*.zip'):
                return os.path.join(diretorio, arquivo)  # Retorna o primeiro arquivo encontrado
        return None  # Retorna None se nenhum arquivo for encontrado


class AuthApp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.objMeo = meo(0)       # 0 informa que o cálculo será feito via API da Ana
        self.init_ui()
            
    def init_ui(self):
        self.resize(530, 200)
        #self.center()
        
        # Criação do frame principal
        self.frmAut01Sup = QFrame(self)
        self.frmAut01Sup.setFrameShape(QFrame.StyledPanel)
        self.frmAut01Sup.setFrameShadow(QFrame.Raised)

        # Campos de entrada e labels
        self.lbIdentificador = QLabel('Identificador', self.frmAut01Sup)
        self.lbIdentificador.setGeometry(15, 0, 161, 31)

        self.lEdIdentificador = QLineEdit(self.frmAut01Sup)
        self.lEdIdentificador.setGeometry(15, 30, 171, 31)

        self.lbSenha = QLabel('Senha', self.frmAut01Sup)
        self.lbSenha.setGeometry(200, 0, 161, 31)

        self.lEdSenha = QLineEdit(self.frmAut01Sup)
        self.lEdSenha.setGeometry(200, 30, 161, 31)
        self.lEdSenha.setEchoMode(QLineEdit.Password)
        #self.lEdSenha.setPlaceholderText("Password")

        self.pBtGerarToken = QPushButton('Gerar Token', self.frmAut01Sup)
        self.pBtGerarToken.setGeometry(387, 29, 111, 31)
        self.pBtGerarToken.clicked.connect(self.authenticate)

        self.lbToken = QLabel('Token de Autenticação', self.frmAut01Sup)
        self.lbToken.setGeometry(15, 64, 221, 31)

        self.lEdToken = QTextEdit (self.frmAut01Sup)
        self.lEdToken.setGeometry(15, 94, 481, 60)

        # Configuração do layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.frmAut01Sup)

        self.setLayout(main_layout)
        self.setWindowTitle('Autenticação da API Hidroweb')

    def authenticate(self):
        # Obter os valores de usuário e senha
        identificador = self.lEdIdentificador.text()
        senha = self.lEdSenha.text()
        self.lEdToken.setText("")

        try:
            # Enviar a requisição para a API
            if self.lEdIdentificador.text() and self.lEdSenha.text():
                self.objHidroWeb = hidroWeb()
                if self.objHidroWeb.statusLogin==0:
                    self.criarArqCfg(self.lEdIdentificador.text(), self.lEdSenha.text())
                    self.token = self.objHidroWeb.getOAuth(self.lEdIdentificador.text(), self.lEdSenha.text())
                    if self.token:
                        self.lEdToken.setText(self.token)
                    else:
                        self.lEdToken.setText("Token não obtido")
                        print(self.token)
                else:
                    if self.objHidroWeb.statusLogin==1:
                        QMessageBox.warning(self, "Erro", "Usuário ou senha não informado no arquivo de configuração (cfgapiana.ini). Verifique")
                    elif self.objHidroWeb.statusLogin==2:                        
                        msgArqCfg = QMessageBox.warning(
                            self,
                            "Erro",
                            "Arquivo de configuração (cfgapiana.ini) inexistente. Deseja criar um novo?",
                            QMessageBox.Ok | QMessageBox.Cancel
                        )
                        if msgArqCfg == QMessageBox.Ok:
                            self.criarArqCfg(self.lEdIdentificador.text(), self.lEdSenha.text())
                            QMessageBox.warning(self, "Autenticação", "Arquivo de configuração (cfgapiana.ini) criado. O login será validado. Aguarde!")
                            self.authenticate()
            else:
                QMessageBox.warning(self, "Erro", "Informe usuário e senha")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, 'Erro', f'Ocorreu um erro: {e}')
    
    def criarArqCfg(self,usuario,senha):
        config = configparser.ConfigParser()
    
        # Adiciona a seção [apiana] e suas chaves/valores
        config['apiana'] = {
            'identificador': usuario,
            'senha': senha
        }
        
        arquivo = f"{os.path.dirname(__file__)}\\cfgapiana.ini"
    
        # Escreve as configurações no arquivo cfgapiana.ini
        with open(arquivo, 'w') as configfile:
            config.write(configfile)
        
    # Exemplo de uso da classe AuthApp
    #if __name__ == '__main__':
    #    app = QApplication(sys.argv)
    #    window = AuthApp()
    #    window.show()
    #    sys.exit(app.exec_())
