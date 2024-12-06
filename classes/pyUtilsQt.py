from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QCheckBox, QPushButton, QWidget, QHBoxLayout, QApplication, QHeaderView)

import sys

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
import os

class dialogEstacoes(QDialog):
    def __init__(self, selecionados, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerar cálculo da Meo")
        print("começou")

        # Layout principal
        layout = QVBoxLayout()

        ########################################################
        # Frame Superior
        frmSuperior = QVBoxLayout()


        frmSuperior.addWidget(QLabel("Escolha a forma de importação:"))
        
        # ComboBox
        self.combobox = QComboBox()
        self.combobox.addItems(["viaCSV", "viaAPI"])
        self.combobox.currentIndexChanged.connect(self.toggle_csv_input)
        frmSuperior.addWidget(self.combobox)


        # LineEdit para caminho do arquivo CSV
        self.folder_path = QLineEdit()
        self.folder_path.setPlaceholderText("Selecione a pasta contendo os arquivos CSV")
        self.folder_path_button = QPushButton("Buscar Pasta")
        self.folder_path_button.clicked.connect(self.select_folder)

        frmSuperior.addWidget(QLabel("Caminho da pasta CSV:"))
        frmSuperior.addWidget(self.folder_path)
        frmSuperior.addWidget(self.folder_path_button)

        layout.addLayout(frmSuperior)
        
        ########################################################
        # Frame Central - QTableWidget para os selecionados
        # Colunas
        # codEstacao: selecionados[0]
        # ufEstacao: selecionados[1]
        # nomeEstacao: selecionados[2]
        # codEstacao: selecionados[5]
        frmCentral = QVBoxLayout()
        self.tbSelecionados = QTableWidget(0, 4)  
        self.tbSelecionados.setHorizontalHeaderLabels(["Código", "UF", "Estação", "Valor da Meo"])

        frmCentral.addWidget(self.tbSelecionados)

        # Adiciona os itens selecionados ao QTableWidget
        self.preencherItens(selecionados)

        # Box inferior
        boxInferior = QHBoxLayout()

        # Checkbox para Atualizar dados (padrão: True)
        self.ckDados = QCheckBox("Atualizar dados")
        self.ckDados.setChecked(True)
        boxInferior.addWidget(self.ckDados)
        
        # Checkbox para Atualizar camada Estacao (padrão: True)
        self.ckCamada = QCheckBox("Atualizar camada Estacao")
        self.ckCamada.setChecked(True)
        boxInferior.addWidget(self.ckCamada)
        
        frmCentral.addLayout(boxInferior)

        layout.addLayout(frmCentral)
        ########################################################
        # Frame Inferior - Botões OK e Cancelar
        frmInferior = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancelar")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        frmInferior.addWidget(self.ok_button)
        frmInferior.addWidget(self.cancel_button)

        layout.addLayout(frmInferior)
        ########################################################

        self.setLayout(layout)

    def preencherItens(self, selecionados):
        """Popula o QTableWidget com os itens selecionados do outro QTableWidget"""
        
        # Definir o número de linhas baseado no total de registros selecionados
        self.tbSelecionados.setRowCount(len(selecionados))

        # Selecionar as colunas desejadas
        for row, item in enumerate(selecionados):
            self.tbSelecionados.setItem(row, 0, QTableWidgetItem(item[0]))
            self.tbSelecionados.setItem(row, 1, QTableWidgetItem(item[1]))
            self.tbSelecionados.setItem(row, 2, QTableWidgetItem(item[2]))
            self.tbSelecionados.setItem(row, 3, QTableWidgetItem(item[5]))

    def toggle_csv_input(self):
        if self.combobox.currentText() == "viaCSV":
            self.folder_path.show()
            self.folder_path_button.show()
        else:
            self.folder_path.hide()
            self.folder_path_button.hide()

    def select_folder(self):
        # Diálogo para selecionar a pasta
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "Selecione a pasta com os arquivos CSV")
        if folder_path:
            self.folder_path.setText(folder_path)
    
    def get_selected_option(self):
        """Retorna a opção selecionada no ComboBox (viaAPI ou viaCSV)"""
        return self.combobox.currentText()

    def obterListaCodEstacao(self):
        """Retorna a lista de códigos da primeira coluna do QTableWidget"""
        codes = []
        for row in range(self.tbSelecionados.rowCount()):
            code_item = self.tbSelecionados.item(row, 0)  # Coluna [0] contém o código
            if code_item:
                codes.append(code_item.text())
        return codes
        
    # def process_data(self):
    #     # Processo de execução
    #     folder = self.folder_path.text()
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
def chamarQDialog(self, selecionados):
    """Função que recebe os dados selecionados e abre o QDialog"""
    dialog = dialogEstacoes(selecionados)
    
    # Executa o diálogo
    if dialog.exec_() == QDialog.Accepted:
        # Obtém a opção selecionada (viaCSV ou viaAPI)
        selected_option = dialog.get_selected_option()
        
        # Obtém a lista de códigos da primeira coluna
        codes = dialog.obterListaCodEstacao()
        
        print(f"Opção selecionada: {selected_option}")
        print(f"Códigos: {codes}")
    else:
        print("Ação cancelada")


#
# Rotina para criar uma QDialog que mostre uma relação de itens que irá executar determinada ação para cada item selecionado
# Está funcionando, mas ainda não apliquei em nenhum código
# Exemplo de uso:
# lista_dados = [("101", "Estação A"),  ("103", "Estação C")]
# cabecalho = ["Código","Nome"]
#
# app = QApplication(sys.argv)
# dialog = TableDialog("Testando", lista_dados,cabecalho)
# dialog.exec_()
#class tabelaDialog(QDialog):
#    def __init__(self, titulo,resultado, cabecalho, a=100, b=100, c=600, d=400,):
#        super().__init__()
#        self.setWindowTitle(titulo)
#        self.setGeometry(a, b, c, d)
#
#        # Layout principal
#        layout = QVBoxLayout()
#
#        # Tabela
#        linhas = len(resultado)
#        colunas = (len(resultado[0])) +1    # +1 é para incluir a coluna selecionar
#
#        self.table = QTableWidget(self)
#        self.table.setRowCount(linhas)
#        self.table.setColumnCount(colunas)
#
#        cabecalho.insert(0, "Selecionar")
#        self.table.setHorizontalHeaderLabels(cabecalho)
#
#        # Adicionar checkbox no cabeçalho para "Selecionar Todos"
#        self.select_all_checkbox = QCheckBox()
#        self.select_all_checkbox.stateChanged.connect(self.select_all_rows)
#
#        # Colocar o checkbox no cabeçalho da primeira coluna
#        header_layout = QHBoxLayout()
#        header_layout.addWidget(self.select_all_checkbox)
#        header_layout.setAlignment(Qt.AlignCenter)
#        header_layout.setContentsMargins(0, 0, 0, 0)
#        header_widget = QWidget()
#        header_widget.setLayout(header_layout)
#        self.table.setCellWidget(0, 0, header_widget)
#
#        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
#
#        # Adicionar dados à tabela
#        for row in range(len(resultado)):
#            # Checkbox na primeira coluna
#            widget = QWidget()
#            checkbox = QCheckBox()
#            layout_checkbox = QHBoxLayout(widget)
#            layout_checkbox.addWidget(checkbox)
#            layout_checkbox.setAlignment(Qt.AlignCenter)
#            layout_checkbox.setContentsMargins(0, 0, 0, 0)
#            widget.setLayout(layout_checkbox)
#            self.table.setCellWidget(row, 0, widget)
#
#            # Adicionar as colunas da linha
#
#            for cont in range(0, len(resultado[0])):
#                self.table.setItem(row, cont+1, QTableWidgetItem(str(resultado[row][cont])))
#
#        # Adicionar tabela ao layout
#        layout.addWidget(self.table)
#
#        # Botão de confirmação para executar ações selecionadas/checadas
#        btn_confirmar = QPushButton("Executar Ações Selecionadas")
#        btn_confirmar.clicked.connect(self.executar_selecionados)
#        layout.addWidget(btn_confirmar)
#
#        self.setLayout(layout)
#
#    def select_all_rows(self, state):
#        """
#        Marca ou desmarca todas as checkboxes dependendo do estado do checkbox no cabeçalho.
#        """
#        for row in range(self.table.rowCount()):
#            checkbox_widget = self.table.cellWidget(row, 0)
#            checkbox = checkbox_widget.layout().itemAt(0).widget()
#            checkbox.setChecked(state == Qt.Checked)
#
#    def executar_selecionados(self):
#        """
#        Executa ações para todas as linhas checadas.
#        """
#        resultado = []
#        for row in range(self.table.rowCount()):
#            checkbox_widget = self.table.cellWidget(row, 0)
#            checkbox = checkbox_widget.layout().itemAt(0).widget()
#
#            # Se o checkbox estiver marcado ou a linha estiver selecionada
#            if checkbox.isChecked():
#                nome_item = self.table.item(row, 1).text()
#                valor_item = self.table.item(row, 2).text()
#                resultado.append((nome_item, valor_item))
#
#        # Exibir ou processar o resultado das ações
#        print("Ações executadas para os seguintes itens:")
#        for item in resultado:
#            print(f"Nome: {item[0]}, Valor: {item[1]}")



# Ainda não está sendo utilizada
# Na função calcularmeo é preciso de um parâmetro que retorne o status do cálculo
# A sugestão é que dentro da função que busca a série mais demorada, crie uma thread
#class GetThread(QThread):
#    # Exemplo para usar a Thread com cálculo da Meo, pois está demorando cerca de 20 minutos, sendo necessário incluir uma barra de progresso
#    # thread = GetCalcularMeoThread(objMeo.calcularMeo, codEstacao)
#    # thread.start()
#    progress = pyqtSignal(int)
#    finished = pyqtSignal()
#
#    def __init__(self, funcao, *args, **kwargs):
#        super().__init__()
#        self.funcao = funcao  # Atribui a função passada
#        self.args = args      # Argumentos posicionais da função
#        self.kwargs = kwargs  # Argumentos nomeados da função
#
#    def run(self):
#        # Chama a função com seus argumentos
#        self.funcao(*self.args, **self.kwargs)
#
#        #cnt=0
#        #while (True):
#        #    cnt+=1
#        #    if cnt==99:
#        #        cnt=0
#        #        time.sleep(0.01)
#        #        self.progress.emit(cnt)
#        
#        self.finished.emit()  # Emite sinal de finalização
#    
#    def stop(self):
#        self.is_running = False
#        self.terminate()
#
#
#