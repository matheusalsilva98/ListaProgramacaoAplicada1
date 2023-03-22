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
Solução Questão 6
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

class FeicaoDuplicadas(QgsProcessingAlgorithm):
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
    ATRIBUTOS = 'ATRIBUTOS'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return FeicaoDuplicadas()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'feicaoduplicadas'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Feição Duplicada')

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
        return self.tr("Analisa as feições duplicadas da camada de entrada, analisando de acordo com determinados atributos, colocando em uma nova camada tal feição.")

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
        
        self.addParameter(
            QgsProcessingParameterField(
                self.ATRIBUTOS,
                self.tr('ATRIBUTOS'),
                None,
                self.INPUT,
                QgsProcessingParameterField.Any,
                allowMultiple=True,
                optional=False,
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

        # Declarando a variável que irá receber a entrada.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        
        # Declarando a variável que irá recber os campos dos atributos a serem analisados.
        atributos = self.parameterAsFields(
            parameters,
            self.ATRIBUTOS,
            context
        )
        
        # Criando o atributo flag para as features de saída, do tipo string.
        fields = QgsFields()
        fields.append(QgsField("flag", QVariant.String))

        # Se a entrada for nula gerar erro.
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Declarando as variáveis que irá receber o output.
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            source.wkbType(),
            source.sourceCrs()
        )

        # feedback para o usuário.
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # Verifica se a sink é nula, caso seja gera erro.
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Computa o número de passos até ser finalizado o processo de execução.
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        
        # Pegando todos os atributos da camada de entrada:
        listaAtributosSource = source.fields().names()
        
        # Pegando os índices correspondentes dos atributos selecionados em relação ao principal:
        indices = []
        for i in range(len(listaAtributosSource)):
            if listaAtributosSource[i] in atributos:
                indices.append(i)
            else:
                continue
        
        # Criando uma função que compara a feature analisada com a feature do QgsSpatialIndex
        def comparaAtributos (feature, fid):
            """
            Compara os atributos selecionados pelo usuário da feature atual do for e da feature 
            correspondente ao fid, indece do QgsSpatialIndex.
            """
            atributosFeature = []
            atributosFid = []
            for featureFid in source.getFeatures():
                if featureFid.id() == fid:
                    for i in indices:
                        atributosFeature.append(feature.attribute(i))
                        atributosFid.append(featureFid.attribute(i))
                else:
                    continue
            if atributosFeature == atributosFid:
                return True
            else:
                return False

        for current, feature in enumerate(features):
            # Se o usuário desejar pode cancelar o processo.
            if feedback.isCanceled():
                break
            
            index = QgsSpatialIndex(source.getFeatures(), flags=QgsSpatialIndex.FlagStoreFeatureGeometries)
            for fid in index.intersects(feature.geometry().boundingBox()):
                # Se estiver analisando a mesma feature, faz continue.
                if fid == feature.id():
                    continue
                fgeom = index.geometry(fid)
                if fgeom.intersects(feature.geometry()):
                    if fgeom.equals(feature.geometry()):
                        # Comparando os campos dos atributos:
                        if comparaAtributos(feature, fid):
                            flagFeature = QgsFeature(fields)
                            flagFeature.setGeometry(QgsGeometry.fromWkt(feature.geometry().asWkt()))
                            flagFeature['flag'] = f"Feições da camada {source.sourceName()} com {source.allFeatureIds()} possuem mesmo conjunto de atributos."
                            sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)
                    else: 
                        continue

            # Aumenta a porcentagem do feedback do processo.
            feedback.setProgress(int(current * total))

        # Retorno da função com o output
        return {self.OUTPUT: dest_id}
