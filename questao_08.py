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
Solução Questão 8
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
                       QgsProcessingParameterFeatureSink)
from qgis import processing
from qgis.utils import iface
import random

class VerticesNaoCompartilhados(QgsProcessingAlgorithm):
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
    COMPARACAO = 'COMPARACAO'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return VerticesNaoCompartilhados()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'verticesnaocompartilhados'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Vértices Não Compartilhados')

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
        return self.tr("identifica vértices não compartilhados em intersecções de elementos das camadas de entrada do tipo linha ou polígono.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Adicionando as características do nosso parâmetro de input, entrada, que pode ser do tipo polígono ou linha.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorLine, QgsProcessing.TypeVectorPolygon]
            )
        )
        
        # Parâmetro da camada de comparação que vai ser escolhida pelo usuário podendo ser do tipo linha ou poligono.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.COMPARACAO,
                self.tr('Comparation layer'),
                [QgsProcessing.TypeVectorLine, QgsProcessing.TypeVectorPolygon]
            )
        )

        # Adicionando as características do nosso parâmetro de saída.
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
        
        # Declarando a variável responsável pela camada de comparação.
        comparacao = self.parameterAsSource(
            parameters,
            self.COMPARACAO,
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
            QgsWkbTypes.Point,
            source.sourceCrs()
        )

        # feedback para o usuário.
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # Se a camada saída for nula gerar erro.
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Forma de analisar a faixa de progresso.
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        # Pegando as features das camadas de entrada, como é uma lista de camadas e apenas duas sendo comparadas, temos uma lista de duas.
        features1 = source.getFeatures()
        features2 = comparacao.getFeatures()

        for current, feature in enumerate(features1):
            # Caso o usuário deseje, cancelar o processo de progresso do algoritmo.
            if feedback.isCanceled():
                break
        
            # Pegando o Bounding Box de cada feature presente na segunda camada que se passa no input, para analisar para cada feature, mas apenas no retângulo próximo
            index = QgsSpatialIndex(features2, flags=QgsSpatialIndex.FlagStoreFeatureGeometries)
            
            flagFeature = QgsFeature(fields) # Criando a feição com o atributo 'flag'
            
            # Fazendo uma iteração for, para conseguirmos adquiriros índices de todos os componentes que se tocam entre si, da primeira e da segunda camada.
            for fid in index.intersects(feature.geometry().boundingBox()):
                fgeom = index.geometry(fid) # Guardando em uma variável a geometria correspondente ao indice.
                
                # Analisando se o feature da primeira camada toca o feature da segunda camada:
                if fgeom.touches(feature.geometry()):
                    for vertice in (fgeom.intersection(feature.geometry())).vertices():
                        # Pegando cada vertice da intersecção do feature da primeira camada com o da segunda camada:
                        flagFeature.setGeometry(QgsGeometry.fromWkt(vertice.asWkt()))
                        # Adicinando o campo do atributo 'flag' do tipo string abaixo.
                        flagFeature['flag'] = 'Vértice não compartilhado não compartilhado na intersecção das camadas de entrada.'
                        # Adicionando a feature Point na camada de saída que respeita as características da intersecção.
                        sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)
                
                # Analisando se o feature da primeira camada cruza o feature da segunda camada:
                elif fgeom.crosses(feature.geometry()):
                    for vertice in (fgeom.intersection(feature.geometry())).vertices():
                        # Pegando cada vertice da intersecção do feature da primeira camada com o da segunda camada:
                        flagFeature.setGeometry(QgsGeometry.fromWkt(vertice.asWkt()))
                        # Adicinando o campo do atributo 'flag' do tipo string abaixo.
                        flagFeature['flag'] = 'Vértice não compartilhado não compartilhado na intersecção das camadas de entrada.'
                        # Adicionando a feature Point na camada de saída que respeita as características da intersecção.
                        sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)

            # Progresso da barra, como feedback para o usuário.
            feedback.setProgress(int(current * total))
        
        # O retorno da nossa função é o output.
        return {self.OUTPUT: dest_id}
