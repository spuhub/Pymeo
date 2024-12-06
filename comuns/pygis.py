# Referências
# https://docs.qgis.org/3.28/pdf/pt_BR/QGIS-3.28-PyQGISDeveloperCookbook-pt_BR.pdf
# Listar campos da camada em um QListWidget https://gis.stackexchange.com/questions/346062/fields-layer-listed-into-a-qlistwidget-in-pyqgis

    # Mostrar uma barra de progresso no QGis
    # Testado em 13/08/2024
    def progQGis(self):
        from PyQt5.QtCore import Qt
        from PyQt5.QtWidgets import QProgressBar, QLabel, QHBoxLayout, QWidget
        import time
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
        
    def listarCampos(camada):
        for field in camada.fields():
            print(field.name(), field.typeName())
    
    def selecionarFeicao(camada):
        # Todas
        camada.selectAll()
        
        # Por expressão
        camada.selectByExpression('"Class"=\'B52\' and "Heading" > 10 and "Heading" <70',QgsVectorLayer.SetSelection)
        
        # Alterar a cor da feição selecionada
        iface.mapCanvas().setSelectionColor( QColor("red") )
        
        # Selecionar por recursos
        selecao = []
        feature = next(camada.getFeatures())
        
        if feature:
            selecao.append(feature.Codigo())
            
        camada.select(selecao)
        
        # Limpar seleção
        camada.removeSelection()
        
        # Mostrar feições selcionadas
        total = camada.selectedFeatureCount()
        
        selecao = camada.selectedFeatures()
        for feature in selecao:
            # do whatever you need with the feature
            # print(layer.fields().indexOf('Codigo'))
            # Mostra o código da estação
            print(feature[0])          # ou
            print (feature['Codigo'])
            # Mostra o nome da estação
            print(feature[1])          # ou
            print (feature['Nome'])
        
        # Mostrar feições selecionadas dentro de uma área
        areaInteresse = QgsRectangle(450290,400520, 450750,400780)
        
        resultado = QgsFeatureRequest().setFilterRect(areaInteresse)
        
        # ou baseada em um filtro
        exp = QgsExpression('location_name ILIKE \'%Lake%\'')
        resultado = QgsFeatureRequest(exp)

        
        for feature in camada.getFeatures(resultado):
            pass
        
        # Fazer referência ao atributo por índice
        print(feature[1])
        
        selected_ids = layer.selectedFeatureIds()
        
        #Crie uma camada de memória a partir de IDs de recursos selecionados
        from qgis.core import QgsFeatureRequest

        memory_layer = layer.materialize(QgsFeatureRequest().setFilterFids(layer.selectedFeatureIds()))
        QgsProject.instance().addMapLayer(memory_layer)

    def OcultarColuna():
        from qgis.core import QgsEditorWidgetSetup

        def fieldVisibility (layer,fname):
            setup = QgsEditorWidgetSetup('Hidden', {})
            for i, column in enumerate(layer.fields()):
                if column.name()==fname:
                    layer.setEditorWidgetSetup(idx, setup)
                    break
                else:
                    continue

        
    def mostrarDados(camada):
        # Mostrar algumas informações de cada feição
        layer = iface.activeLayer()
        features = layer.getFeatures()
        
        for feature in features:
            geom = feature.geometry()
            geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
            
            if geom.type() == QgsWkbTypes.PointGeometry:
                if geomSingleType:
                    x = geom.asPoint()
                    print("Point: ", x)
                else:
                    x = geom.asMultiPoint()
                    print("MultiPoint: ", x)
            elif geom.type() == QgsWkbTypes.LineGeometry:
                if geomSingleType:
                    x = geom.asPolyline()
                    print("Line: ", x, "length: ", geom.length())
                else:
                    x = geom.asMultiPolyline()
                    print("MultiLine: ", x, "length: ", geom.length())
            elif geom.type() == QgsWkbTypes.PolygonGeometry:
                if geomSingleType:
                    x = geom.asPolygon()
                    print("Polygon: ", x, "Area: ", geom.area())
                else:
                    x = geom.asMultiPolygon()
                    print("MultiPolygon: ", x, "Area: ", geom.area())
            else:
                print("Unknown or invalid geometry")
            attrs = feature.attributes()
            print(attrs)
            break

    def addAtributo(self,nomecampo,tipo,comprimento,precisao):
        # Ex.: addAtributo('valor_meo', QVariant.Double, len=5, prec=2])
        indiceCampo = layer.fields().indexOf(nomecampo)
        
        if indiceCampo == -1:
            provedor = layer.dataProvider()
            provedor.addAttributes([QgsField(nomecampo, tipo, len=comprimento, prec=precisao])
            layer.updateFields()
    
    def alterarValorCampo(self,nomecampo,valorcampo):
        indiceCampo = layer.fields().indexOf(nomecampo)
        
        if indiceCampo > -1:
            layer.startEditing()        #Habilitar edição (Simula o clique no lápis)
            
            atributos = layer.getFeatures()
            for atributo in atributos:
                codigo   = atributo.codigo()          # campo que será usado como chave
                provedor.changeAttributeValues({codigo:valorcampo})
    
    def listarCamadas():
        layers_list = {}
        for l in QgsProject.instance().mapLayers().values():
            layers_list[l.name()] = l
        
        print(layers_list)
    
    def resumoCamada(self,camada):
        print(QgsProject.instance().mapLayersByName(camada)[0])
        

    def mostrarMensagem(mensagem, duracao=1):
        # Níveis: Info, Warning, Critical, Sucess
        iface.messageBar().pushMessage("Error", mensagem, level=Qgis.Critical, duration=duracao)
    
    # Barra de mensagens em minha própria caixa de diálogo
    def msgDialog():
        class MyDialog(QDialog):
            def __init__(self):
                QDialog.__init__(self)
                self.bar = QgsMessageBar()
                self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
                self.setLayout(QGridLayout())
                self.layout().setContentsMargins(0, 0, 0, 0)
                self.buttonbox = QDialogButtonBox(QDialogButtonBox.Ok)
                self.buttonbox.accepted.connect(self.run)
                self.layout().addWidget(self.buttonbox, 0, 0, 2, 1)
                self.layout().addWidget(self.bar, 0, 0, 1, 1)
            def run(self):
                self.bar.pushMessage("Hello", "World", level=Qgis.Info)
            
            myDlg = MyDialog()
            myDlg.show()
     
     # Barra de progresso em uma barra de mensagens
     def progMsg():
        import time
        from qgis.PyQt.QtWidgets import QProgressBar
        from qgis.PyQt.QtCore import *
        progressMessageBar = iface.messageBar().createMessage("Doing something boring...")
        progress = QProgressBar()
        progress.setMaximum(10)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        iface.messageBar().pushWidget(progressMessageBar, Qgis.Info)
        
        for i in range(10):
        time.sleep(1)
        progress.setValue(i + 1)
        
        iface.messageBar().clearWidgets()

    def progIntMsg():
        vlayer = iface.activeLayer()
        
        count = vlayer.featureCount()
        features = vlayer.getFeatures()
        
        for i, feature in enumerate(features):
        # do something time-consuming here
        print('.') # printing should give enough time to present the progress
        
        percent = i / float(count) * 100
        # iface.mainWindow().statusBar().showMessage("Processed {} %".
        format(int(percent)))
        iface.statusBarIface().showMessage("Processed {} %".format(int(percent)))
        
        iface.statusBarIface().clearMessage()
        
    def removerBarra():
        toolbar = iface.helpToolBar()
        parent = toolbar.parentWidget()
        parent.removeToolBar(toolbar)

    def adicionarBarra():
        # and add again
        parent.addToolBar(toolbar)
        
    def removerBarraAcao():
        actions = iface.attributesToolBar().actions()
        iface.attributesToolBar().clear()
        iface.attributesToolBar().addAction(actions[4])
        iface.attributesToolBar().addAction(actions[3])
    
    def removerMenu():
        # for example Help Menu
        menu = iface.helpMenu()
        menubar = menu.parentWidget()
        menubar.removeAction(menu.menuAction())
        
        # and add again
        menubar.addAction(menu.menuAction())
    
    def alterarCorTela():
        from qgis.PyQt.QtCore import Qt

        iface.mapCanvas().setCanvasColor(Qt.black)
        iface.mapCanvas().refresh()
        
    def obterNomeCamada():
        from qgis.core import QgsVectorLayer
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "layer name you like", "memory")
        QgsProject.instance().addMapLayer(layer)
        
        layers_names = []
        for layer in QgsProject.instance().mapLayers().values():
            layers_names.append(layer.name())
        
        print("layers TOC = {}".format(layers_names))
        
        # Ou
        layers_names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
        print("layers TOC = {}".format(layers_names))