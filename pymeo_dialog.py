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
# Padrão de nomenclatura inicial dos elementos GUI
# lb   - QLabel
# lEd  - QLineEdit
# pBt  - QPushButton
# tab  - QWidget
# tbW  - QTabWidget
# tbVw - QTableView
# tEd  - QTextEdit
###################################################################################################
# Importação definida pela Equipe de Desenvolvimento
# import datetime
# import pandas as pd
# from qgis.core import QgsVectorLayer, QgsProject
# from qgis.PyQt.QtWidgets import QApplication, QDesktopWidget, QDialog, QHeaderView, QLineEdit, QTableWidgetItem, QStyle
from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtWidgets import QDialog, QDockWidget
from qgis.PyQt import uic

###################################################################################################
import os

###################################################################################################
# Arquivo responsável pela importação das interfaces gráficas
# Os arquivos .ui serão utilizados no arquivo pymeo.py
###################################################################################################
# Carregar o arquivo da interface gráfica que será utilizada para gerar o cálculo
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pymeo_dialog_base.ui'))

# Carregar o arquivo da interface gráfica que será utilizada na abertura do plugin
FORM_GERARMAPA, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'pymeo_dialog_gerar_mapa.ui'))


class dckMainPymeo(QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    

    def __init__(self, parent=None):
        """Constructor."""
        super(dckMainPymeo, self).__init__(parent)
        ###################################################################################################
        # A classe QgsProject cria um novo projeto - Lê e grava novos projetos
        # QgsProject.instance() Cria uma nova instância do projeto

        # Configure a interface do usuário do Designer por meio de FORM_CLASS.
        # Depois de self.setupUi() você pode acessar qualquer objeto de designer que esteja fazendo
        # self.<objectname>, e você pode usar slots de conexão automática - consulte
        # Desativado: http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # https://het.as.utexas.edu/HET/Software/html/designer-using-a-ui-file.html
        # widgets-and-dialogs-with-auto-connect
        # Configura a classe para receber objetos *.ui
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
        
class dlgGerarMapa(QDialog, FORM_GERARMAPA):

    closingPlugin = pyqtSignal()
    

    def __init__(self, parent=None):
        """Constructor."""
        super(dlgGerarMapa, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
        
