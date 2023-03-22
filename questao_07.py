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
Solução Questão 7
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

class HolesMenoresTol(QgsProcessingAlgorithm):
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
    TOLERANCIA = 'TOLERANCIA' # Colocando o parâmetro de tolerância do valor da área do buraco.
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return HolesMenoresTol()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'holesmenoresquetolerancia'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Holes Menores Tolerância')

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
        return self.tr("Identifica os holes menores que uma tolerência e os remove.")

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
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        
        # Parâmetro de tolerância.
        self.addParameter(
            QgsProcessingParameterNumber(
                self.TOLERANCIA,
                self.tr('TOLERANCIA'),
                type=QgsProcessingParameterNumber.Double
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

        # Armazenando a entrada na variável source
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        
        # Armazenando a tolerância em uma variável:
        tol = self.parameterAsDouble(
            parameters,
            self.TOLERANCIA,
            context
        )

        # Verificando se a entrada é nula ou não.
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Armazenando os dados de saída no sink:
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            source.fields(),
            source.wkbType(),
            source.sourceCrs()
        )

        # Manda informação para o usuário:
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # Se a saída for nula gera erro:
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Criação de uma variável para verificar o progresso.
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Opção para o usuário cancelar o processo:
            if feedback.isCanceled():
                break
            # Coordenadas do poligono com os holes:
            poligonoComHoles = feature.geometry().asWkt()
            # Verifcando os polígonos menores que uma certa tolerância
            poligonoTolerancia = feature.geometry().removeInteriorRings(tol).asWkt()
            
            if len(poligonoTolerancia) <= len(poligonoComHoles) + 6:
                flagFeature = QgsFeature()
                flagFeature.setGeometry(QgsGeometry.fromWkt(poligonoTolerancia))
                sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)
            # Feedback na barra de progresso da interface para o usuário:
            feedback.setProgress(int(current * total))

        # Retorno da função, o output:
        return {self.OUTPUT: dest_id}
