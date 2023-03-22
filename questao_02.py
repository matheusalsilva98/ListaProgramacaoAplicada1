# -*- coding: utf-8 -*-

"""
/***************************************************************************
Lista de exercícios de Programação Aplicada
Grupo 3
Alunos:
 - Al Alves Silva
 - Al Romeu
 - Al Samuel
 - Al Silva
Solução Questão 2
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFields,
                       QgsField,
                       QgsFeatureSink,
                       QgsFeature,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsSpatialIndex,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterMultipleLayers,
                       QgsWkbTypes,
                       QgsProject,
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.utils import iface


class AgrupamentoGrupo(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Parâmetro de entrada.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return AgrupamentoGrupo()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'agrupamentogrupo'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Agrupamento em Grupo Separado por Vetor')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Solução Grupo 3')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return '3'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Separa as entradas vetoriais de acordo com o tipo de grupo.")
        
    
    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # As entradas serão armazenadas na lista criada abaixo:
        source = self.parameterAsLayerList(
            parameters,
            self.INPUT,
            context
        )

        # Se a entrada for nula gera um erro:
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Todos os grupos nomeados em um dicionário que poderemos acessar pela sua key, númerica.
        tiposGrupos = {
            0: "MEU_GRUPO",
            1: "Ponto",
            2: "Linha",
            3: "Área",
            4: "Imagem"
        }
        
        # Camadas selecionadas armazendas em uma lista:
        listaCamadasSelecionadas = iface.layerTreeView().selectedLayers()
        
        # Nomes das camadas selecionadas armazendas em uma lista:
        nomesCamadasSelecionadas = [i.name() for i in listaCamadasSelecionadas]
        
        
        root = QgsProject.instance().layerTreeRoot()
        # Camadas presentes no nosso projeto:
        listaCamadasProjeto = QgsProject.instance().layerTreeRoot().children()
        
        # Nomes das camadas presentes no nosso projeto:
        nomesCamadasProjeto = [i.name() for i in listaCamadasProjeto]
        
        # Colocando em uma lista chamada de indices quais indices estão selecionadas:
        indices = []
        for i in range(len(nomesCamadasProjeto)):
            if nomesCamadasProjeto[i] not in nomesCamadasSelecionadas:
                continue
            else:
                indices.append(i)
        
        # Adicionando os grupos no projeto
        def adicionandoGrupo(i):
            """
            Vai retornar o valor da chave correspondete 'i' para usar na adição de grupos
            """
            return root.addGroup(tiposGrupos[i])
            
        # Adicionando na camada principal
        def camadaMeuGrupo(x):
            """
            Vai inserir na camada 'MEU GRUPO' todas as camadas
            """
            clone = x.clone()
            groupAdd1.insertChildNode(0, clone)
            root.removeChildNode(x)
        
        # Passar cada elemento da lista root para adicionar no grupo certo
        def camadaEmGrupo(x):
            """
            Vai verificar qual é o elemento e vai o adicionar em um determinado grupo de acordo com o seu nome.
            """
            clone = x.clone()
            try:
                if x.layer().wkbType() in [0, 1, 4]:
                    groupAdd2.insertChildNode(0, clone)
                elif x.layer().wkbType() in [2, 5]:
                    groupAdd3.insertChildNode(0, clone)
                elif x.layer().wkbType() in [3, 6]:
                    cloneGrupo = groupAdd4.clone()
            except:
                groupAdd5.insertChildNode(0, clone)
            root.removeChildNode(x)
        
        # Pegando todas as camadas presentes no projeto e colocando numa lista:

        
        # Adicionando os grupos.
        groupAdd1 = adicionandoGrupo(0)
        groupAdd2 = adicionandoGrupo(1)
        groupAdd3 = adicionandoGrupo(2)
        groupAdd4 = adicionandoGrupo(3)
        groupAdd5 = adicionandoGrupo(4)
        
        # Iteração sob os indices que correspondem as camadas selecionadas pelo mouse.
        for i in indices:
            camadaEmGrupo(listaCamadasProjeto[i])
        
        # Definindo uma função que vai inserir no grupo 1, que é o grupo principal (MEU_GRUPO), colocando todo o projeto dentro desse.
        def camadaNoMeuGrupo(x):
            """
            A função vai clonar o argumento, inserir no grupo MEU_GRUPO, e vai remover o anterior.
            """
            clone = x.clone()
            groupAdd1.insertChildNode(0, clone)
            root.removeChildNode(x)
        
        # Aplicando a função acima:
        camadaNoMeuGrupo(groupAdd2)
        camadaNoMeuGrupo(groupAdd3)  
        camadaNoMeuGrupo(groupAdd4)  
        camadaNoMeuGrupo(groupAdd5)  
        
        return {self.OUTPUT: [i.id() for i in source]}
