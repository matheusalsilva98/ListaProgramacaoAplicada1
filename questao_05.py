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
Solução Questão 5
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
                       QgsProcessingParameterNumber,
                       QgsMeshSpatialIndex,
                       QgsPointXY,
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.utils import iface

class VerticesDuplicados(QgsProcessingAlgorithm):
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

    # Parametros de entrada

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return VerticesDuplicados()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'verticesduplicados'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Vértices Duplicados')

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
        return self.tr("Gera pontos onde temos vértices duplicados, para indicar onde estes se localizam.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
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

        # Colocando na variável 'source' o input do usuário.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )

        # Se source é nulo gera erro.
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Criando uma variável para armazenar o atributo que será criado para o nosso output
        fields = QgsFields()
        fields.append(QgsField("flag", QVariant.String))
        
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Point, # Retorna uma camada do tipo ponto indicando os vértices duplos.
            source.sourceCrs()
        )

        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # Se o sink não foi criado, ou seja, é nulo, vai gerar um erro.
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Criando a variável total para analisar o progresso da execução.
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        
        # Criando uma variável que será uma lista para armazenar os pontos que correspondem aos vértices das feições:
        listaCoorFeic = []

        for current, feature in enumerate(features):
            # Se o usuário quiser cancelar o processo.
            if feedback.isCanceled():
                break
            
            # Pega os vértices das feições.
            vertice = feature.geometry().vertices().next().asWkt()
            if vertice not in listaCoorFeic:
                listaCoorFeic.append(vertice)
            else:
                # Criando a feição do tipo ponto para receber as coordenadas do ponto:
                flagFeature = QgsFeature(fields)
                flagFeature.setGeometry(QgsGeometry.fromWkt(vertice))
                
                # Adicionando ao atributo 'flag' e o seu valor correspondente:
                flagFeature['flag'] = f"Vértice duplicado na feição de id {feature.id()} da camada {source.sourceName()}"
                
                # Adiciona o ponto correspondente ao vértice duplicado no sink
                sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)

                # Update the progress bar
                feedback.setProgress(int(current * total))

        # Retorna a camada de output para o usuário.
        return {self.OUTPUT: dest_id}
