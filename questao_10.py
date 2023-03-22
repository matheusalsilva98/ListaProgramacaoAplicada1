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
Solução Questão 10
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                       QgsFields,
                       QgsField,
                       QgsFeatureSink,
                       QgsProcessingParameterField,
                       QgsFeature,
                       QgsGeometry,
                       QgsProcessingException,
                       QgsSpatialIndex,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterMultipleLayers,
                       QgsWkbTypes,
                       QgsProject,
                       QgsProcessingParameterNumber,
                       QgsMeshSpatialIndex,
                       QgsPointXY,
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.utils import iface
import random
import h3

class GridH3(QgsProcessingAlgorithm):
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

    # Declaração dos parâmetros.

    INPUT = 'INPUT'
    NIVEL_GRID = 'NIVEL_GRID'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return GridH3()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'criagridh3'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Cria Grid H3')

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
        return self.tr("Criar um processing que cria um grid H3 que intersecta todas as feições da camada de entrada.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Parâmetro de entrada.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        # Parâmetro da resolução, nível do grid, declarada como um inteiro.
        self.addParameter(
            QgsProcessingParameterNumber(
                self.NIVEL_GRID,
                self.tr('Nível de grid'),
                type=QgsProcessingParameterNumber.Integer
            )
        )

        # Parâmetro de saída.
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

        # Declarando a variável que irá receber a camada de entrada.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        
        # Declarando a variável do nível do grid que irá receber o valor colocado como inteiro.
        
        nivel_grid = self.parameterAsInt(
            parameters,
            self.NIVEL_GRID,
            context
        )

        # Se a entrada for nula, gerará erro.
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Declarando a variável que irá receber a camada de saída.
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            QgsWkbTypes.Polygon,
            source.sourceCrs()
        )

        # Manda o feedback para o usuário.
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # Se a camada de saída for nula, gerará erro.
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Analisa a barra de progresso, declarando a variável total, para fazer essa analise.
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        
        # Pegando todas as features da camada de entrada.
        features = source.getFeatures()
        
        # Criando a lista abaixo para conseguir armazenar as coordenadas onde temos o mínimo x, o mínimo y, o máximo x e o máximo y e assim determinar os extremos.
        coordExtremidades = [9999999, 999999, -999999, -999999] # Colando valores maiores e menores para serem substituídos.
        xMinimoId = [0]
        yMinimoId = [0]
        xMaximoId = [0]
        yMaximoId = [0]

        for current, feature in enumerate(features):
            # Se o usuário desejar poderá cancelar o progresso.
            if feedback.isCanceled():
                break
                
            # Pegando o bounding Box de cada feição da iteração do for.
            bbox = feature.geometry().boundingBox()
            
            if bbox.xMinimum < coordExtremidades[0]:
                coordExtremidades[0] = bbox.xMinimum
                xMinimoId[0] = feature.id()
                
            if bbox.xMaximum > coordExtremidades[2]:
                coordExtremidades[2] = bbox.xMaximum
                xMaximoId[0] = feature.id()
            
            if bbox.yMinimum < coordExtremidades[1]:
                coordExtremidades[1] = bbox.yMinimum
                yMinimoId[0] = feature.id()
            
            if bbox.yMaximum > coordExtremidades[3]:
                coordExtremidades[3] = bbox.yMaximum
                yMaximoId[0] = feature.id()
            
            
            # Progresso da barra de progresso.
            feedback.setProgress(int(current * total))
        
        # Teremos um quadrilátero no final, com as coordenadas do topo, do ponto mais baixo, do ponto mais a esquerda e do ponto mais a direita, encontrando as coordenadas médias, teremos:
        
        centroAproximado = [(coordExtremidas[0] + coordExtremidades[2])/2, (coordExtremidades[1] + coordextremidades[3])/2]
        
        h3Features = h3.geo_to_h3(centroAproximado[0], centroAproximado[1], nivel_grid) # Latitude, Longitude, Resolução do grid
        
        
        # Adicionando a feature na camada de saída.
        sink.addFeature(feature, QgsFeatureSink.FastInsert)
        
        # Retorno da função como sendo o output.
        return {self.OUTPUT: dest_id}
