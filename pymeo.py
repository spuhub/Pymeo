# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Plugin QGis
 Pymeo
 Gerado por Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-03-08
        copyright            : (C) 2024 by SPU-CGDAG
        email                : cggeo.spu@gestao.gov.br
        git sha              : $Format:%H$
 ***************************************************************************/
 #
 #
"""
# Módulos nativos do Python 
from datetime import datetime
import matplotlib.colors as mcolors
import os.path
import pandas as pd
from pathlib import Path
import subprocess
import sys
import time
import traceback

# Módulos específicos para o QGis
from qgis.core import QgsApplication, QgsCategorizedSymbolRenderer, QgsExpression, QgsFeatureRequest, QgsField, QgsFieldFormatter, QgsFieldFormatterRegistry, QgsMapLayer, QgsProject, QgsRendererCategory, QgsSymbol, QgsVectorLayer
from qgis.gui import QgsMessageBar

from qgis.PyQt.QtCore import Qt, QCoreApplication, QDateTime, QSettings, QTranslator
from qgis.PyQt.QtGui import QIcon, QColor, QMovie
from qgis.PyQt.QtWidgets import QAction, QApplication, QVBoxLayout , QDesktopWidget, QDialog, QDockWidget, QFileDialog, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMenu, QMenuBar, QMessageBox, QProgressBar, QProgressDialog, QStyle, QTableWidgetItem, QToolBar, QWidget
#from qgis.gui import QgsMapTool

# Módulos desenvolvidos para o Pymeo
# from pymeo.classes.calcMeo import meo
# from pymeo.classes.apiAna import hidroWeb
from pymeo.classes.pyUtilsPymeo import dialogEstacoes, AuthApp, dlgArquivosCalculados
from pymeo.config import PATH, PATHARQUIVOS
# Importe o código do arquivo pymeo_dialog.py para a caixa de diálogo
from .pymeo_dialog import dckMainPymeo, dlgGerarMapa



# Módulos de terceiros ou bibliotecas externas que precisam ser instalados
## csv
try:
    import csv
except ImportError:
    # Se o módulo não estiver instalado, instala-o
    dirPython = f"{sys.prefix}\\python.exe"
    subprocess.check_call([dirPython, "-m", "pip", "install", "csv"])

## sqlalchemy
try:
    import sqlalchemy
except ImportError:
    # Se o módulo não estiver instalado, instala-o
    dirPython = f"{sys.prefix}\\python.exe"
    subprocess.check_call([dirPython, "-m", "pip", "install", "sqlalchemy"])

## sqlite
try:
    import sqlite3
except ImportError:
    # Se o módulo não estiver instalado, instala-o
    dirPython = f"{sys.prefix}\\python.exe"
    subprocess.check_call([dirPython, "-m", "pip", "install", "sqlite3"])


    
class pymeoPlugin:
    """Implementação do plug-in QGIS."""

    def __init__(self, iface):
        """Construtor.

        :param iface: Uma instância de interface que será passada para esta classe
            que fornece o gancho pelo qual você pode manipular o QGIS
            aplicação em tempo de execução
        :type iface: QgsInterface
        """
        ##########################################################################
        # Referências necessárias na inicialização da classe
        # Objeto essencial para interagir com o QGIS
        self.iface = iface
        
        # O Painel do tipo dockwidget será associado ao QGIS e criado posteriormente
        self.dockwidget = None
        
        # Garantir que o plugin tenha a referência necessária para interagir com a 
        # área de visualização do mapa desde o início, facilitando a manipulação de dados 
        # e a implementação de funcionalidades que dependem dessa interação.
        self.canvas = iface.mapCanvas()
        
        # Armazenar o caminho do diretório do plugin
        self.plugin_dir = os.path.dirname(__file__)
        
        # Incluir um botão para importar os dados do arquivo para o banco de dados
        # self.importarEstacao('estacao_CEARA.csv')

        # Armazenar o idioma local
        locale = QSettings().value('locale/userLocale')[0:2]
        
        # Armazenar o caminho do diretório do plugin/i18n
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'pymeoPlugin_{}.qm'.format(locale))

        # ???
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declarar atributos de instância
        self.actions = []
        self.menu = self.tr(u'&SPUGeo')

        # Verifique se o plugin foi iniciado pela primeira vez na sessão atual do QGIS
        # Deve ser definido em initGui() para sobreviver às recargas do plugin
        self.first_start = None
        
        # Conectar ao sinal quando uma nova camada é adicionada
        # Conectar um sinal (event) à função novaCamadaAdicionada, 
        # permitindo que essa função seja chamada sempre que novas camadas 
        # são adicionadas ao projeto do QGIS. 
        QgsProject.instance().layersAdded.connect(self.novaCamadaAdicionada)

     # sem inspeção PyMethodMayBeStatic
    def tr(self, message):
        """Obtenha a tradução de uma string usando a API de tradução Qt.

        Nós mesmos implementamos isso, pois não herdamos QObject

        :param message: String para tradução.
        :type message: str, QString

        :returns: Versão traduzida da mensagem
        :rtype: QString
        """
        # sem inspeção PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('pymeoPlugin', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Adicione um ícone à barra de ferramentas.

        :param icon_path: Caminho para o ícone desta ação. Pode ser um recurso
            path (por exemplo, ':/plugins/foo/bar.png') ou um path normal do sistema de arquivos.
        :type icon_path: str

        :param text: Texto que deve ser mostrado nos itens de menu desta ação.
        :type text: str

        :param callback: Função a ser chamada quando a ação é acionada.
        :type callback: function

        :param enabled_flag: Um sinalizador indicando se a ação deve ser habilitada
            por padrão. O padrão é True.
        :type enabled_flag: bool

        :param add_to_menu: Sinalizador indicando se a ação também deve
            ser adicionado ao menu. O padrão é True.
        :type add_to_menu: bool

        :param add_to_toolbar: Sinalizador indicando se a ação também deve
            ser adicionado à barra de ferramentas. O padrão é True.
        :type add_to_toolbar: bool

        :param status_tip: Texto opcional para mostrar em um pop-up quando o ponteiro do mouse
            paira sobre a ação.
        :type status_tip: str

        :param parent: Widget pai para a nova ação. Padrões None.
        :type parent: QWidget

        :param whats_this: Texto opcional para mostrar na barra de status quando o
            o ponteiro do mouse passa sobre a ação.

        :returns: A ação que foi criada. Observe que a ação também é
            adicionado à lista self.actions.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adiciona ícone de plugin à barra de ferramentas Plugins
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Crie as entradas de menu e ícones da barra de ferramentas dentro da GUI do QGIS."""
        icon_path = ':/plugins/pymeo/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'PyMEO 1.0'),
            callback=self.run,
            parent=self.iface.mainWindow())
        
        # Instância da janela principal do Pymeo
        self.dockwidget = dckMainPymeo()

        # Instância da janela para gerar o mapa
        self.qdialogGerarMapa = dlgGerarMapa()
        

        # will be set False in run()
        # será definido como False em run()
        # ???
        self.first_start = True

    # Função que será executada quando o plugin é descarregado
    def unload(self):
        """Remove o item de menu e ícone do plugin da GUI do QGIS."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&SPUGeo'),
                action)
            self.iface.removeToolBarIcon(action)

        # Desconectar o sinal ao descarregar o plugin
        QgsProject.instance().layersAdded.disconnect(self.novaCamadaAdicionada)
        self.first_start = True

            
    def run(self):
        """Método Run que executa todo o trabalho real"""
        # Crie GUI apenas UMA VEZ no retorno de chamada, 
        # para que ela só carregue quando o plugin for iniciado

        # Comentei no dia 12/08/2024, 
        #       Qdo fechava a janela principal e chamava o plugin novamente 
        #       ele só mostrava a tela para gerar o mapa se fizesse o reload do plugin
        #if self.first_start == True:
        #    #self.removerMenu()
        #    self.first_start = False
        #    #self.dockwidget = dckMainPymeo()
        #    #self.dockwidget = dlgGerarMapa()
        self.inicializar()
                        
            
        #self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        #self.dockwidget.show()

    
    def abrirWdPrincipal(self):
        # Fecha a segunda janela
        self.qdialogGerarMapa.accept()  # Ou use close() dependendo do seu caso
        self.gerarMapa()

        # Volta o foco para a janela principal (dockwidget)
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
        self.dockwidget.show()
        self.dockwidget.raise_()
    
    def cancelarWdPrincipal(self):
        self.qdialogGerarMapa.reject()
        
    def cfgDockWidget(self):
        # Outras configurações iniciais do dockwidget
        pass
    
    def removerMenu(self):
        self.iface.vectorMenu().parentWidget().removeAction(self.iface.vectorMenu().menuAction())
        self.iface.vectorMenu().parentWidget().removeAction(self.iface.rasterMenu().menuAction())

    def restaurarMenu(self):
        # todo: Ver qual método que adiciona o menu
        self.iface.vectorMenu().parentWidget().removeAction(self.iface.vectorMenu().menuAction())
        self.iface.vectorMenu().parentWidget().removeAction(self.iface.rasterMenu().menuAction())
    
    def inicPrincipal(self):
        ### Botões
        self.dockwidget.pBtGerarMapa.clicked.connect(lambda: self.gerarMapa())

        # Desabilitar o botão exportar mapa
        # self.pBtExpGrafico.setVisible(False)

        # Ocultar frame da barra de progresso, mostrar quando for usá-la
        self.dockwidget.progresso.setVisible(False)

        # Ocultar os rótulos abaixo dos dados da estação
        self.dockwidget.lbTotReg.setVisible(False)
        
        # Configurações da tabela de dados (self.dockwidget.tblWdEstacao)
        # Título
        self.dockwidget.tblWdEstacao.setWindowTitle("Dados das estações selecionadas")
        # Habilitando a ordenação ao clicar nos títulos das colunas
        self.dockwidget.tblWdEstacao.setSortingEnabled(True)
        self.criarMenuTbWdg(self.dockwidget.tblWdEstacao,
                            ['Atualizar valor da MEO','Atualizar valor da MEO - Todas','Exportar cálculo da MEO'],
                            [self.menuAcaoAtualMeo,self.menuAcaoAtualMeoTodos, self.menuAcaoExpMeo]
                            )

        # Associar ações aos elementos
        self.pesqValor = self.adicionarIconeEdTxt(self.dockwidget.lEdFiltro,QStyle.SP_ArrowRight)
        self.pesqValor.triggered.connect(lambda: self.onPesquisar(self.dockwidget.cbFiltro.currentIndex(), self.dockwidget.lEdFiltro.displayText().upper()))

        # Botão Atualizar valor da MEO
        self.dockwidget.pBtAtualMeo.clicked.connect(self.menuAcaoAtualMeo)   

        # Botão Atualizar valor da Meo - Todas
        self.dockwidget.pBtAtualMeoTodas.clicked.connect(self.menuAcaoAtualMeoTodos)   

        # Botão Exportar Tabela
        # self.dockwidget.pBtExpTabela.clicked.connect(self.menuAcaoExpTabela)   

        # Botão Exportar Cálculo da Meo
        self.dockwidget.pBtExpCalcMeo.clicked.connect(self.menuAcaoExpMeo)  

        # Botão Gerar Mapa - Conecta um botão da dockwidget para abrir a segunda janela
        self.dockwidget.pBtGerarMapa.clicked.connect(self.inicGerarMapa)

        # Botão Exportar Gráfico
        # self.dockwidget.pBtExpGrafico.clicked.connect(self.menuAcaoAtualMeo)   

        # Disponibilizar o acesso a tela de login e senha da Api
        self.dockwidget.tlbtnAutenticacao.clicked.connect(self.acessarAutenticacao)        
        
        # Desabilitar o item do combobox referente a UF, pois a pesquisa demora muito
        self.dockwidget.cbFiltro.setItemData(4, Qt.ItemIsEnabled , Qt.UserRole)

    def acessarAutenticacao(self):
        dlgAutenticacao = AuthApp()
        if dlgAutenticacao.exec_() == QDialog.Accepted:
            print("Cálculo concluído")     
        else:
            print("Ação cancelada")


    def inicGerarMapa(self):
        
        ################################################################################################
        #Configurações da Janela qdialogGerarMapa (qDlgGerMapa)
        # Mudar o foco para o objeto lEdArqShp
        self.qdialogGerarMapa.lEdArqShp.setFocus()
        
        # Atribuir um valor inicial para o objeto lEdArqShp
        self.qdialogGerarMapa.lEdArqShp.setText(self.dirInicial+'\\shp\\BR_UF_2022.shp')
        
        # Atribuir um valor inicial para o objeto lEdArqTxt
        self.qdialogGerarMapa.lEdArqTxt.setText(self.dirInicial+'\\dados\\Estacao.csv')

        # Atribuir um valor inicial para o objeto lEdArqQGis
        self.qdialogGerarMapa.lEdArqQGis.setText(self.dirInicial+'\\qgis\pymeo_hidroweb.qgz')    
        
        # Associar ações aos elementos
        self.abrirArqShp = self.adicionarIconeEdTxt(self.qdialogGerarMapa.lEdArqShp,QStyle.SP_DirOpenIcon)
        self.abrirArqShp.triggered.connect(lambda: self.onabrirArq(self.qdialogGerarMapa.lEdArqShp,self.dirInicial,'Shapefile (*.shp)'))
        
        self.abrirArqTxt = self.adicionarIconeEdTxt(self.qdialogGerarMapa.lEdArqTxt,QStyle.SP_DirOpenIcon)
        self.abrirArqTxt.triggered.connect(lambda: self.onabrirArq(self.qdialogGerarMapa.lEdArqTxt,self.dirInicial,'Texto Delimitado (*.csv *.txt)' ))

        self.abrirArqQGis = self.adicionarIconeEdTxt(self.qdialogGerarMapa.lEdArqQGis,QStyle.SP_DirOpenIcon)
        self.abrirArqQGis.triggered.connect(lambda: self.onabrirArq(self.qdialogGerarMapa.lEdArqQGis,self.dirInicial,'Arquivos QGis (*.qgs *.qgz)'))


        # Conecta um botão na segunda janela para fechar a segunda janela e voltar à principal
        self.qdialogGerarMapa.btnBoxGerarMapa.accepted.connect(self.abrirWdPrincipal)
        self.qdialogGerarMapa.btnBoxGerarMapa.rejected.connect(self.cancelarWdPrincipal)
        
        self.qdialogGerarMapa.show()
        self.qdialogGerarMapa.exec_()

    def inicializar(self):
        ################################################################################################
        # Configurações do Projeto QGis
        self.projeto = QgsProject.instance()

        # Armazenar o diretório padrão do usuário (Informações armazenadas no arquivo de configuração config.py)
        self.dirUser = os.path.expanduser('~')
        self.dirInicial = os.path.dirname(__file__).replace('/', '\\')
        
        #self.habDocks(['IdentifyResultsDock'])
        self.inicGerarMapa()
        self.inicPrincipal()
                        
        ################################################################################################
        # Criar a instância Hidroweb
        # A Hidroweb é a classe relacionada ao Web Service (API) da Agência Nacional das Águas (ANA)
        # self.hidroweb = hidroWeb()


        # Iniciar o plugin nas especificações do Mapa
        # todo: incluir no arquivo de configuração em qual aba o plugin irá iniciar
        
    def acaoElementos(self):
        pass
        # Adicionar um botão a um texto que deseja copiar
        #self.copyToken = self.adicionarIconeEdTxt(selfdockwidget.lEdToken,QStyle.SP_DirOpenIcon)
        #self.dockwidget.pBtGerarToken.clicked.connect(lambda: self.acaoGerarToken())
        #self.copyToken.triggered.connect(lambda: self.onCopyToken(self.dockwidget.lEdToken))

        # Mostrar os dados selecionados ao clicar no ponto, usando uma ferramenta de identificação
        #self.mapTool = MyMapTool(self.canvas, self.selEstacoes)
        #self.canvas.setMapTool(self.mapTool)
        #self.iface.mapCanvas().clicked.connect(self.selEstacoes)

        
    def gerarMapa(self):
        # Adicionar a camada shapefile
        self.adicionarShp()

        # Adicionar a camada de dados do tipo txt ou csv
        self.adicionarTxt()

        # Filtro inicial da camada
        self.adicionarFiltro(self.camada,self.filtro)

        # Definir um nome inicial para o arquivo
        self.salvarComo()

        # Salvar o arquivo com as funcionalidades definidas
        self.salvar()
        
        #self.gerarDados()

        # Fechar o plugin após executar as funcionalidades definidas 
        # Verificar se a opção Fechar o plugin ao Gerar o Mapa está marcada
        #if self.ckfrmWdMapFechar.isChecked():
        #    self.fecharPlugin()
            
        # Fechar o plugin após executar as funcionalidades definidas 
        # Verificar se a opção Fechar o plugin ao Gerar o Mapa está marcada
        #if self.ckfrmWdMapMeo.isChecked():
        #    self.calcularMeo()

    # Adicionar a camada do tipo shapefile com as UFs
    def adicionarShp(self):
        # Remover camada, se existir
        self.camada = "UFs"
        self.removerCamada("UFs")

        uri = f"file:///{self.qdialogGerarMapa.lEdArqShp.displayText()}"
        vlayer = QgsVectorLayer(self.qdialogGerarMapa.lEdArqShp.displayText(), self.camada, "ogr")
        if not vlayer.isValid():
            print("Erro ao adicionar camada shapefile")
        else:
            self.projeto.addMapLayer(vlayer)
            self.definirCoresUFs("UFs")

    # Adicionar a camada do tipo txt ou csv com as UFs
    # todo: ajustar para que seja possível definir os filtros antes de criar a camada
    def adicionarTxt(self):
        # Configuraçoes personalizadas referentes a camada
        self.encoding = 'UTF-8'
        self.delimiter = ';'
        self.decimal = ','
        self.crs = 'EPSG:4674'
        self.x = 'Longitude'
        self.y = 'Latitude'
        self.camada = "Estacao"
        self.filtro = "TipoEstacao = 'Fluviométrica' "
        # Colunas que terão o tipo de dados definidos
        # Foi criado para evitar que a exportação defina a coluna código 47.001 como string e não como float
        self.colunas = "&colType=Codigo:string"

        uri = f"file:///{self.qdialogGerarMapa.lEdArqTxt.displayText()}?encoding={self.encoding}&delimiter={self.delimiter}&decimalPoint={self.decimal}&crs={self.crs}&xField={self.x}&yField={self.y}{self.colunas}"
        
        # Remover camada, se existir
        self.removerCamada("Estacao")
        
        # Adicionar nova camada
        vlayer = QgsVectorLayer(uri, "Estacao", "delimitedtext")
        if not vlayer.isValid():
            print("Erro ao adicionar camada de texto delimitado")
            return
        
        # Adiciona a camada ao projeto
        self.projeto.addMapLayer(vlayer)
        self.dockwidget.tblWdEstacao.setRowCount(0)

        
        # Verifica se a camada foi adicionada com sucesso
        if not QgsProject.instance().mapLayersByName(self.camada):
            print(f"A camada '{self.camada}' não foi adicionada ao projeto.")
            return
        
        self.alterarTituloCampo(self.camada, "codigoEstacao", "Código")

        
    # Filtro inicial da camada
    def adicionarFiltro(self, camada, filtro):
        # Filtrar o atributo na camada informada
        # O índice [0] é para trazer a primeira camada com o nome pesquisado
        #print(self.projeto.instance().mapLayersByName)
        layer = self.projeto.instance().mapLayersByName(camada)[0]
        

        # Filtrar a camada pelo atributo e valor informado
        layer.setSubsetString(filtro)
        pass

    # Definir um nome inicial para o arquivo
    # todo: Quando existir o arquivo, confirmar antes de criar o arquivo com o mesmo nome
    def salvarComo(self):
        self.projeto.write(self.qdialogGerarMapa.lEdArqQGis.displayText())

    # Salvar o arquivo com as funcionalidades definidas
    def salvar(self):
        self.projeto.write()

    def fecharPlugin(self):
        self.close()
        

    # Adicionar um botão ao objeto do tipo QLineEdit
    def adicionarIconeEdTxt(self, campo, icone):
        action = campo.addAction(
             QApplication.style().standardIcon(icone), QLineEdit.TrailingPosition
        )
        return action

    # onabrirArq(self.dockwidget.lEdArqQGis,self.dirInicial,'Arquivos QGis (*.qgs *.qgz)')

    def onabrirArq(self,campo,pathinicial,tipo):
        #campo = self.lEdArqShp
        #pathinicial = "C:/"
        #tipo="Shapefile (*.shp)"
        #print('onabrirArquivo')
        #print(campo,pathinicial,tipo)
    
        filename, ok = QFileDialog.getOpenFileName(
            self.dockwidget,
            "Selecione o arquivo",
            pathinicial,
            tipo
        )
        if filename:
            campo.setText(str(Path(filename)))
    
    #def selEstacoes(self, point):
    #    camada = self.iface.activeLayer()
    #    
    #    if not camada:
    #        self.iface.messageBar().pushMessage("Error", f"Camada {camada} não encontrada", level=Qgis.Critical, duration=duracao)
    #        return
    #    
    #    # Criar uma requisição para identificar feições no ponto clicado
    #    # print(self.canvas.getCoordinateTransform().toMapCoordinates(point))
    #    point = QgsPoint(point.x(), point.y())
    #    resposta = QgsFeatureRequest().setFilterRect(self.canvas.getCoordinateTransform().toMapCoordinates(point))
    #    feicoes = [feat for feat in self.layer.getFeatures(resposta)]
    #            
    #    self.mostrarSelecao(feicoes)
    #
    #def mostrarSelecao(self, feicoes):
    #    self.dockwidget.tblWdEstacao.clear()
    #    
    #    campos = camada.fields()
    #    
    #    #colunas = ['codigoEstacao', 'siglaUF', 'nomeEstacao', 'nomeBacia']
    #    #selecionarColunas = [campos[index] for index in colunas]
    #    #self.dockwidget.tblWdEstacao.setColumnCount(len(selecionarColunas))
    #    #self.dockwidget.tblWdEstacao.setHorizontalHeaderLabels([campo.name() for campo in selecionarColunas])
    #    self.table_widget.setColumnCount(len(campos))
    #    self.table_widget.setHorizontalHeaderLabels([campo.name() for campo in campos])        
    #    
    #    for idxLinha, feicao in enumerate(feicoes):
    #        self.dockwidget.tblWdEstacao.insertRow(idxLinha)
    #        for idxColuna, campo in enumerate(campos):
    #            valor = feicao[campo.name()]
    #            self.dockwidget.tblWdEstacao.setItem(idxLinha, idxColuna, QTableWidgetItem(str(valor)))
    #            # print(campo.name())
    #    self.dockwidget.tblWdEstacao.resizeColumnsToContents()

        
        
    # Gerar os dados que serão mostrados na tablewidgets
    def gerarDados(self):
        nome_camada = 'Estacao'
        id_camada = QgsProject.instance().mapLayersByName(nome_camada)
        
        if not id_camada:
            self.iface.messageBar().pushMessage("Error", f"Camada {nome_camada} não encontrada", level=Qgis.Critical, duration=duracao)
            return
        
        camada = id_camada[0]
        campos = camada.fields()
        #print(campos)
        recursos = camada.getFeatures()
        
        #colunas = ['codigoEstacao', 'siglaUF', 'nomeEstacao', 'Operando', 'nomeBacia']
        #colunas = ['codigoEstacao', 'siglaUF', 'nomeEstacao', 'nomeBacia']
        #selecionarColunas = [campos[index] for index in colunas]
        #print(selecionarColunas)

        
        self.dockwidget.tblWdEstacao.setColumnCount(len(campos))
        self.dockwidget.tblWdEstacao.setHorizontalHeaderLabels([campo.name() for campo in campos])
        #self.dockwidget.tblWdEstacao.setColumnCount(len(selecionarColunas))
        #self.dockwidget.tblWdEstacao.setHorizontalHeaderLabels([campo.name() for campo in selecionarColunas])
        for i, recurso in enumerate(recursos):
            self.dockwidget.tblWdEstacao.insertRow(i)
            for j, index in enumerate(colunas):
                #if campo.name() in selecionarColunas:
                value = recurso[campos[index].name()]
                self.dockwidget.tblWdEstacao.setItem(i, j, QTableWidgetItem(str(value)))
                # print(campo.name())
        self.dockwidget.tblWdEstacao.resizeColumnsToContents()
    
    def novaCamadaAdicionada(self, camadas):
        for camada in camadas:
            if camada.type() == camada.VectorLayer:
                camada.selectionChanged.connect(self.selecaoAlterada)
    
    #############################################################
    # Código inserido em 26/08/2024 - Início
    from qgis.core import QgsProject, QgsFeatureRequest

    # Função para selecionar um ponto com base em um código
    def onPesquisar(self,item,valor):
        # Lista de atributos
        # Código da Estação, Nome da Estação, Nome do Rio, Nome da Subbacia, UF
        atributos = ['codigoEstacao', 'nomeEstacao', 'nomeRio', 'nomeSubBacia', 'siglaUF']
        
        # Obtém a camada de pontos pelo nome
        camada = QgsProject.instance().mapLayersByName('Estacao')[0]
        
        if not camada:
            print("Camada não encontrada.")
            return
    
        # Cria uma expressão para buscar o ponto pelo código
        expressao = f'"{atributos[item]}" = \'{valor}\''
    
        # Cria uma solicitação de recurso com a expressão
        request = QgsFeatureRequest().setFilterExpression(expressao)
    
        # Desmarca qualquer seleção existente
        camada.removeSelection()
    
        # Obtém os IDs dos recursos que correspondem à expressão
        ids = [feat.id() for feat in camada.getFeatures(request)]
    
        # Seleciona os recursos encontrados
        camada.select(ids)
    
        #if ids:
        #    print(f"Ponto com código {codigo} selecionado.")
        #else:
        #    print(f"Nenhum ponto encontrado com o código {codigo}.")
    
    # Exemplo de uso da função
    #codigo_pesquisar = '12360000'
    #selecionar_ponto_por_codigo(codigo_pesquisar)
    # Código inserido em 26/08/2024 - Fim
    #############################################################

    """
    A função selecaoAlterada será executada sempre que a seleção da camada a que estiver associada, for alterada
    """
    #@pyqtSlot()
    def selecaoAlterada(self, selected, deselected, clear_and_select):
        camada = self.iface.activeLayer()
        
        # Remover o filtro da camada
        # camada.setSubsetString("")

        if not camada:
            return

        # Excluir as linhas na tabela
        self.dockwidget.tblWdEstacao.clear()
        self.dockwidget.tblWdEstacao.setRowCount(0)

        # Obter as feições selecionadas
        recursosSelecionados = camada.selectedFeatures()
        totalSelecionados = camada.selectedFeatureCount()
        
        if camada.name()=="UFs":
            if totalSelecionados>0:
                QgsProject.instance().mapLayersByName('Estacao')[0].mapCanvas().zoomToSelected(camada)
                ufSelecionada = recursosSelecionados[0]['SIGLA_UF']
                expressao = f"\"siglaUF\" = '{ufSelecionada}'"
                try:
                    camadaEstacao = QgsProject.instance().mapLayersByName("Estacao")[0]
                    camadaEstacao.setSubsetString(expressao)
                    recursosSelecionados = list(camadaEstacao.getFeatures())
                    totalSelecionados = len(recursosSelecionados)
                except Exception as e:
                    erro = str(e)
                    print("Expressão inválida. Verifique")
                camada = camadaEstacao

        # Definir os campos que serão utilizados no tablewidget 
        campos = ['codigoEstacao', 'nomeRio', 'nomeEstacao', 'nomeMunicipio', 'valorMeo', 'dtAtualizacao', 'siglaUF', 'nivelConsistencia', 'nomeBacia', 'nomeSubBacia', 'operando']
    
        # Definir  o título das colunas
        titulos = ['Código', 'Rio', 'Estação', 'Municipio', 'MEO', 'Atualização', 'UF', 'Nível', 'Nome da Bacia', 'Nome da SubBacia', 'Operando']

        self.dockwidget.tblWdEstacao.setColumnCount(len(campos))
        self.dockwidget.tblWdEstacao.setHorizontalHeaderLabels(titulos)

        # Executar uma ação quando a feição é selecionada
        if recursosSelecionados:
            for recurso in recursosSelecionados:
                idrecurso = recurso.id()
                feicoes = camada.getFeature(idrecurso)

                # Criar um dicionário com o nome dos campos selecionados e seus valores
                atributos = dict(zip(camada.fields().names(), feicoes.attributes()))

                # Obtém o total de linhas para definir a posição que a linha será inserida
                totalLinhas = self.dockwidget.tblWdEstacao.rowCount()
                self.dockwidget.tblWdEstacao.insertRow(totalLinhas)
                
                for idxColuna, campo in enumerate(campos):
                    atributo = atributos.get(campo)
                    if campo in ['dtAtualizacao','dtCadastro']:
                        if atributo:
                            valorFormatado = atributo.toString("dd/MM/yyyy HH:mm:ss")
                        else:
                            valorFormatado = ""
                        self.dockwidget.tblWdEstacao.setItem(totalLinhas, idxColuna, QTableWidgetItem(valorFormatado))
                    else:
                        if atributo is not None:
                            valor = str(atributo)
                        else:
                            valor = ""
                        self.dockwidget.tblWdEstacao.setItem(totalLinhas, idxColuna, QTableWidgetItem(valor))
                
                # Atualizar o tblWdEstacao
                self.dockwidget.tblWdEstacao.resizeColumnsToContents()

            if totalSelecionados==1:
                self.dockwidget.lbTotReg.setText(f"{totalSelecionados} registro")
            else:
                self.dockwidget.lbTotReg.setText(f"{totalSelecionados} registros")
            self.dockwidget.lbTotReg.setVisible(True)
        else:
            self.dockwidget.lbTotReg.setVisible(False)
            self.dockwidget.lbTotReg.setText("")
                
    def removerCamada(self,camada):
        objCamada = QgsProject.instance().mapLayersByName(camada)
        
        if objCamada:
            id = objCamada[0].id()
            QgsProject.instance().removeMapLayer(id)
    """
        Criar um menu para um objeto
        
        objeto: Nome do componente que irá receber o menu
        item  : Lista de itens do menu que serão adicionados
        acao  : Lista de ações que cada item de menu irá executar
    """
    def criarMenuTbWdg(self,objeto,itens,acoes):
        # Ex.: self.criarMenu(self.dockwidget.tblWdEstacao,['Item 1','Item 2'],[acao1, acao2]
        # Criar o objeto menu para o objeto do tipo tablewidget
        def showContextMenu(pos):
            menu = QMenu(objeto)
            # Criar o item do Menu e associar suas ações
            for i, item in enumerate(itens):
                if acoes[i]:
                    menu.addAction(item,acoes[i])
                else:
                    menu.addSeparator()
                #objeto.setMenu(menu)
            menu.exec_(objeto.viewport().mapToGlobal(pos))
        
        # Associar o menu de contexto ao QTableWidget
        objeto.setContextMenuPolicy(Qt.CustomContextMenu)
        objeto.customContextMenuRequested.connect(showContextMenu)

 
    def menuAcaoAtualMeo(self, gerarMemoria=False):
        # Efetuar o cálculo da MEO para as estações selecionadas
        try:
            # Itens selecionados
            selecionados = self.dockwidget.tblWdEstacao.selectedItems()

            ###############################################################################
            # Transformar os itens selecionados em uma estrutura de linhas e colunas
            linhas_selecionadas = {}
            for item in selecionados:
                row = item.row()
                if row not in linhas_selecionadas:
                    linhas_selecionadas[row] = []
                linhas_selecionadas[row].append(item.text())
            
            # Converter as linhas selecionadas em uma lista de listas
            itensSelecionados = [linhas_selecionadas[row] for row in sorted(linhas_selecionadas)]
            ###############################################################################
            dialog = dialogEstacoes(itensSelecionados)
            
            # Chamar a janela para definir as alterações das estações
            if dialog.exec_() == QDialog.Accepted:
                dialog.calcularMeoDialog()
                # Alterar os dados da MEO com base na tabela gerada
                self.atualizarDados('Estacao','codigoEstacao',dialog.listaCodEstacao,'valorMeo',dialog.listaValorMeoNovo, dialog.combobox.currentText())
                # print("Cálculo concluído")
                
            else:
                print("Ação cancelada")
        except Exception as e:
            erro = str(e)
            print(erro)
            tb = traceback.format_exc()
            print(f"Erro {erro} ao executar a Thread. Verifique \n", tb)  
            
              
        #if resposta == QMessageBox.Ok:
        #    pass
        #    #self.atualizar_valor_sqlite(codigo, novo_valor)
        #    #self.gerar_csv_da_tabela()
        #    #self.atualizar_tablewidget(codigo, novo_valor)
        #pass
        
    def menuAcaoAtualMeoTodos(self):
        self.dockwidget.tblWdEstacao.selectAll()
        self.menuAcaoAtualMeo()       
        pass
        
    def menuAcaoExpMeo(self):
        # self.menuAcaoAtualMeo()
        pathArquivos = PATHARQUIVOS
        selecionados = self.dockwidget.tblWdEstacao.selectedItems()
        ###############################################################################
        # Transformar os itens selecionados em uma estrutura de linhas e colunas
        linhas_selecionadas = {}
        for item in selecionados:
            row = item.row()
            if row not in linhas_selecionadas:
                linhas_selecionadas[row] = []
            linhas_selecionadas[row].append(item.text())
        
        # Converter as linhas selecionadas em uma lista de listas
        itensSelecionados = [linhas_selecionadas[row] for row in sorted(linhas_selecionadas)]
        ###############################################################################
        
        objeto = dlgArquivosCalculados(pathArquivos, itensSelecionados)
        if objeto.exec_() == QDialog.Accepted:
           print("Ok")
        else:
            print("Ação cancelada")
                
#            # Itens selecionados
#            selecionados = self.dockwidget.tblWdEstacao.selectedItems()
#
#            codEstacao = selecionados[0].text()
#            valorMeoAnt = selecionados[5].text()
#
#            # self.progQGis()
#            try:
#                #print(os.path.abspath())
#                #dirComuns = os.path.abspath(os.path.join(os.path.dirname(__file__), '../comuns'))
#                objMeo = meo()
#                objMeo.calcularMeo(codEstacao)
#                valorMeoNovo = objMeo.resultado
#                print("Início")
#                objMeo.salvarDfToExcel(
#                    objMeo.dfMeo,
#                    f"calculo_{codEstacao}.xlsx",
#                    planilha=codEstacao,
#                    titulo=f"Memória de cálculo da Estação {codEstacao}"
#                )
#                print("Arquivo gerado")
#            except Exception as e:
#                erro = str(e)
#                print(erro)
#
#            msg = QMessageBox()
#            msg.setIcon(QMessageBox.Question)
#            msg.setWindowTitle("Confirmar atualização")
#            msg.setText(f" Estação: {codEstacao}\n Meo anterior: {valorMeoAnt} \n Meo atual: {valorMeoNovo}")
#            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
#            resposta = msg.exec_()
#
#            if resposta == QMessageBox.Ok:
#                pass
#                # self.atualizar_valor_sqlite(codigo, novo_valor)
#                # self.gerar_csv_da_tabela()
#                # self.atualizar_tablewidget(codigo, novo_valor)

        pass

    def menuAcaoExpTabela(self):
        pass
    
    
    def progQGis(self):
        # Número de etapas
        total_etapas = 100
        
        # Criar um widget personalizado para exibir na barra de mensagens
        progress_widget = QWidget()
        layout = QHBoxLayout()
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        label = QLabel("Processando...")
        
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        progress_widget.setLayout(layout)
    
        # Adicionar o widget à barra de mensagens do QGIS
        self.iface.messageBar().pushWidget(progress_widget, 1)
    
        for i in range(total_etapas):
            time.sleep(1)  # Simulando um processo longo
            progress_bar.setValue(int((i + 1) / total_etapas * 100))
            
        # Finalizar a barra de progresso
        self.iface.messageBar().clearWidgets()        
        
            
    def definirCoresUFs(self,camada):
        camadas = QgsProject.instance().mapLayersByName(camada)

        objCamada = camadas[0]  # Obtém o primeiro item da lista de camadas
        
        categorias = []
        
        ufs = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
            "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
            "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]
        
        # Definindo as cores inicial e final para criar o gradiente
        cor_inicial = "#008000" 
        cor_final = "#FFFF00"  
        
        # Gerando gradiente de cores
        cmap = mcolors.LinearSegmentedColormap.from_list("corPymeo", [cor_inicial, cor_final], N=len(ufs))
        
        # Gerando o dicionário com as cores
        ufCores = {ufs[i]: mcolors.rgb2hex(cmap(i)) for i in range(len(ufs))}

        for uf, cor in ufCores.items():
            simbolo = QgsSymbol.defaultSymbol(objCamada.geometryType())
            simbolo.setColor(QColor(cor))
            categoria = QgsRendererCategory(uf, simbolo, uf)
            categorias.append(categoria)

        # Aplicar o renderizador categorizado à camada
        # campo é o nome do campo que contém as UFs
        campo = 'SIGLA_UF'
        renderizador = QgsCategorizedSymbolRenderer('SIGLA_UF', categorias)
        objCamada.setRenderer(renderizador)
        objCamada.triggerRepaint()
    
    def definirCoresPontos(self,camada):
        pass
        #Definir a cor dos pontos da camada de texto baseado em uma condição
        #from qgis.core import QgsRuleBasedRenderer, QgsSymbol
        #
        ## Supondo que você tenha uma camada de pontos
        #layer = iface.activeLayer()  # ou obtenha a camada de outra forma
        #
        ## Criar regras para verdadeiro e falso
        #root_rule = QgsRuleBasedRenderer.Rule()
        #
        #true_rule = root_rule.clone()
        #true_rule.setLabel("True Condition")
        #true_rule.setFilterExpression('"your_field" = true')
        #true_symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        #true_symbol.setColor(QColor("#FF0000"))  # Cor vermelha para verdadeiro
        #true_rule.setSymbol(true_symbol)
        #
        #false_rule = root_rule.clone()
        #false_rule.setLabel("False Condition")
        #false_rule.setFilterExpression('"your_field" = false')
        #false_symbol = QgsSymbol.defaultSymbol(layer.geometryType())
        #false_symbol.setColor(QColor("#0000FF"))  # Cor azul para falso
        #false_rule.setSymbol(false_symbol)
        #
        ## Aplica o renderizador baseado em regras
        #renderer = QgsRuleBasedRenderer(root_rule)
        #renderer.rootRule().appendChild(true_rule)
        #renderer.rootRule().appendChild(false_rule)
        #layer.setRenderer(renderer)
        #layer.triggerRepaint()
        
        # Usar as mesmas cores no tablewidget
        # item = self.dockwidget.tablewidget.item(0, 0)  # Obtenha o item correspondente
        # item.setBackground(QColor("#FF0000"))  # Use a mesma cor que você definiu para os pontos (por exemplo, vermelho)
    

    def alterarTituloCampo(self, camada, nomecampo, titulo):
        # Obtém a lista de camadas com o nome especificado
        camadas = QgsProject.instance().mapLayersByName(camada)
        
        if not camadas:
            print(f"Camada com o nome '{camada}' não encontrada.")
            return
        
        objCamada = camadas[0]  # Obtém a primeira camada com o nome especificado
        
        # Obtém o provedor de dados da camada
        provedor = objCamada.dataProvider()
        
        # Verifica se o campo existe
        campos = provedor.fields()
        campo_index = campos.indexOf(nomecampo)
        
        if campo_index == -1:
            print(f"Campo '{nomecampo}' não encontrado na camada '{camada}'.")
            return
        
        # Inicia a edição da camada
        objCamada.startEditing()
        
        # Renomeia o campo
        provedor.renameAttributes({campo_index: titulo})
        
        # Atualiza os campos da camada
        objCamada.updateFields()
        
        # Confirma as alterações
        objCamada.commitChanges()
    
    #self.atualizarDados('Estacao','codigoEstacao',[10300000,10200000],'valorMeo',[10999.0,11999.0])
    def atualizarDados(self,camada,campo,listaChaves,campoAlteracao,listaValores,origemCalcMeo):
        # Atualizar os dados no banco de dados
        dirDados = os.path.abspath(os.path.join(os.path.dirname(__file__)))
        sgdb = 'sqlite'
        db = f"{dirDados}\\dados\\pymeo.db"
        engine = sqlalchemy.create_engine(f"{sgdb}:///{db}")
        print(db)
        cnx = sqlite3.connect(f"{db}")
        print('ok2')
        cursor = cnx.cursor()
        
        
        # self.atualizarDados('Estacao','codigoEstacao',dialog.listaCodEstacao,'valorMeo',dialog.listaValorMeoNovo)
                
        for chave, valor in zip(listaChaves, listaValores):
            sql = f"UPDATE tb_estacao SET {campoAlteracao} = {valor}, origem_valorMeo = '{origemCalcMeo}', dtAtualizacao = datetime() where {campo} = {chave}"
            cursor.execute(sql)
            cnx.execute(sql)
        
        cnx.commit()
        
        # Gerar novo arquivo csv
        cursor = cnx.cursor()
        sql = "select * from tb_estacao"
        cursor.execute(sql)
        dados = cursor.fetchall()
        
        # Obter os nomes das colunas
        colunas = [descricao[0] for descricao in cursor.description]
                        
        with open(self.dirInicial+'\\dados\\Estacao.csv', mode='w', newline='') as arqCsv:
            writer = csv.writer(arqCsv, delimiter=';')  # Define o delimitador como ponto e vírgula
            writer.writerow(colunas)
            writer.writerows(dados)                     # Escrever os dados
        
        cnx.close()
        
        # Excluir a camada Estacao existente
        camada = QgsProject.instance().mapLayersByName('Estacao')
        if camada:
            QgsProject.instance().removeMapLayer(camada[0])
            
        # Incluir a camada Estacao com o novo arquivo gerado após alterações nos dados
        self.qdialogGerarMapa.lEdArqTxt.setText(self.dirInicial+'\\dados\\Estacao.csv')
        self.adicionarTxt()
        
    
    # 25/09/2024 - A rotina atualizarAtributo ainda não está funcionando
    # Exemplo: self.atualizarAtributo('Estacao','codigoEstacao',[10300000,10200000],[2999.0,3999.0])
    def atualizarAtributo(self,camada,campo,listaChaves,listaValores):
        camadaId = QgsProject.instance().mapLayersByName(camada)[0]
                
        # Verifica se camada está em modo de edição e confirma a transação
        if not camadaId.isEditable():
            print("Iniciando modo de edição na camada.")
            camadaId.startEditing()
        
        # Verifica se o campo existe na camada
        campoAlteracao = "valorMeo"
        campoIndex = camadaId.fields().indexFromName(campoAlteracao)
        if campoIndex == -1:
            print(f"Erro: Campo '{campoAlteracao}' não encontrado na camada '{camada}'.")
            return
        
        # Verifica o tipo do campo para garantir compatibilidade
        fieldType = camadaId.fields().field(campoIndex).type()
        print(f"Tipo do campo '{campoAlteracao}': {fieldType}")
    
        # Atualiza os atributos das feições
        for chave, valor in zip(listaChaves, listaValores):
            # Verifica se o valor é inteiro e se o campo é do tipo inteiro
            try:
                chave = int(chave)
            except ValueError:
                print(f"Erro: Chave '{chave}' ou valor '{valor}' não são inteiros válidos.")
                continue
            
            # Converte o valor para float, caso necessário
            try:
                valor = float(valor)
            except ValueError:
                print(f"Erro: Valor '{valor}' não é um float válido.")
                continue
            
            # Cria uma expressão para selecionar a feição com base no valor atual do campo
            expressao = QgsExpression(f"{campo} = {chave}")
            requisicao = QgsFeatureRequest(expressao)
            
            # Itera sobre as feições que correspondem à expressão
            for tipo in camadaId.getFeatures(requisicao):
                idTipo = tipo.id()
                print(f"ID Feição: {idTipo}, Campo: {campoIndex}, Valor: {valor}")
                
                # Verifica se o valor é válido para o tipo de campo
                #field = camadaId.fields().field(campoIndex)
                #if not field.isValidValue(valor):
                #    print(f"Erro: Valor '{valor}' é inválido para o campo '{campo}'.")
                #    continue
                
                # Verificar se a feição está sendo editada por outro processo ou trancada
                if not camadaId.isFeatureEditable(tipo):
                    print(f"Erro: Feição com ID {idTipo} não é editável.")
                    continue
                
                # Verificar se o valor a ser inserido é válido para o campo
                field = camadaId.fields().field(campoIndex)
                if not field.isValidValue(valor):
                    print(f"Erro: Valor {valor} não é válido para o campo '{campoAlterado}'.")
                    continue
                
                
                # Atualiza o campo especificado com o valor correspondente
                try:
                    if not camadaId.changeAttributeValue(idTipo, campoIndex, valor):
                        print(f"Erro ao atualizar feição com ID {idTipo}.")
                    else:
                        print(f"Feição com ID {idTipo} atualizando {campoAlteracao} com {valor}")
                except Exception as e:
                    erro = str(e)
                    print(f"Erro {erro}")
                
        
        #camadaId.commitChanges() 
        # Confirma as mudanças na camada
        if not camadaId.commitChanges():
            print("Erro ao salvar alterações.")
        else:
            print("Alterações salvas com sucesso.")
        
    
    ####################################################################################
    # As funções abaixo devem ser movidas para o arquivo correspondente
    # pyUtils.py    - Classe em Python com as funções personalizadas a serem utilizadas qualquer aplicação em Python 
    # pyUtilsQt.py  - Classe em Python com as funções personalizadas a serem utilizadas com a biblioteca PyQt5 (Qt Designer)
    # pyUtilsSpu.py - Classe em Python com as funções personalizadas a serem utilizadas com os dados e sistemas da SPU-CGDAG
    # pyUtilsGis.py - Classe em Python com as funções personalizadas a serem utilizadas com a biblioteca QGis
    # pyUtilsIa.py  - Classe em Python com as funções personalizadas a serem utilizadas com a Inteligência Artificial   
    # pyUtilsPymeo.py - Classe em Python com as funções personalizadas a serem utilizadas com os dados e sistemas do Pymeo
    #                   Será necessário separar do arquivo utils, pq no utils tem vários módulos que para serem usados
    #                   precisam ser instalados no QGis
    # pyMeo.py      - Classe em Python com as funções personalizadas a serem utilizadas para o Plugin Pymeo
    
    
    def progQGis(self):
        #from PyQt5.QtCore import Qt
        #from PyQt5.QtWidgets import QProgressBar, QLabel, QHBoxLayout, QWidget
        #import time

        # Número de etapas
        total_etapas = 100
        
        # Criar um widget personalizado para exibir na barra de mensagens
        progress_widget = QWidget()
        layout = QHBoxLayout()
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        label = QLabel("Processando...")
        
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        progress_widget.setLayout(layout)
    
        # Adicionar o widget à barra de mensagens do QGIS
        self.iface.messageBar().pushWidget(progress_widget, 1)
    
        for i in range(total_etapas):
            time.sleep(1)  # Simulando um processo longo
            progress_bar.setValue(int((i + 1) / total_etapas * 100))
            
        # Finalizar a barra de progresso
        self.iface.messageBar().clearWidgets()      
