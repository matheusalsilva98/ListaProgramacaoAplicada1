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
Solução Questão 1
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

class VisibilidadeEntrada(QgsProcessingAlgorithm):
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

    # Parâmetros de entrada.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return VisibilidadeEntrada()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'visibilidadeentrada'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Visibilidade das Camadas')

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
        return self.tr("Vai deixar marcada apenas a camada selecionada, todas as outras serão desativadas.")

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

        
        # Criando uma lista com elementos QgsLayerTreeLayer de cada camada presente no projeto.
        listaCamadas = QgsProject.instance().layerTreeRoot().children()
        
        # Pegando os nomes de cada camada presente e armazenando em uma lista.
        listaNomes = [i.name() for i in listaCamadas]
        
        # Verificando se o usuário colocou entrada.
        if not bool(iface.activeLayer()):
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Pegando o nome da camada selecionada.
        nomeCamadaSelecionada = iface.activeLayer().name()
        
        # Iteração que analisa para cada camada presente na lista de camadas criado, e verifica se está selecionado mantém marcado, caso contrário desmarca.
        for camada in listaCamadas:
            if camada.name() != nomeCamadaSelecionada:
                camada.setItemVisibilityChecked(False)
            else:
                camada.setItemVisibilityChecked(True)

        return {self.OUTPUT: [i.id() for i in source]}
