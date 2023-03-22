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
Solução Questão 4
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
import random

class PontosAleatorios(QgsProcessingAlgorithm):
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
    RAIO_BUFFER = 'RAIO_BUFFER' # Parâmetro do raio do buffer aplicado.
    NUM_PONTOS = 'NUM_PONTOS' # Número de pontos que se deseja gerar.
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PontosAleatorios()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'pontosaleatorios'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Gera Pontos Aleatórios')

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
        return self.tr("Gera pontos aleatórios na vizinhança das feições, e estes contém o id da feição mais próxima.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # Camada de input
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        # Adicionando o parâmetro do raio do buffer (double)
        self.addParameter(
            QgsProcessingParameterNumber(
                self.RAIO_BUFFER,
                self.tr('raio do buffer'),
                type=QgsProcessingParameterNumber.Double
            )
        )
        # Adicionando o parâmetro da quantida de pontos (inteiro)
        self.addParameter(
            QgsProcessingParameterNumber(
                self.NUM_PONTOS,
                self.tr('quantidade de pontos'),
                type=QgsProcessingParameterNumber.Integer
            )
        )

        # Nosso output
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

        # Os parâmetros de entrada
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        # O parâmetro do raio do buffer
        raio = self.parameterAsDouble(
            parameters,
            self.RAIO_BUFFER,
            context
        )
        # O parâmetro da quantidade de pontos aleatórios
        num_pontos = self.parameterAsInt(
            parameters,
            self.NUM_PONTOS,
            context
        )

        # Se a entrada for nula, gerar um erro.
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Criando a variável para a criação do atributo 'id' que irá resultar no 'id' da feição mais próxima.
        fields = QgsFields()
        fields.append(QgsField("id", QVariant.Int))
        
        # Definindo os parâmetros da camada de saída.
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Point, # Nosso output são pontos, e com isso devemos colocar o wkbType associado ao Ponto.
            source.sourceCrs()
        )

        # Informar o usuário do progresso.
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))

        # Se a saída for nula, gerar erro.
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Número de passos que será feitos para dar o feedback para o usuário.
        total = 100.0 / num_pontos if num_pontos else 0
        
        # Pegando todas as feições da camada de entrada
        features = source.getFeatures()
        
        # Variável com o número de pontos gerados:
        numeroPontos = 0
        
        # Criando uma lista com as tuplas que relacionam as feições da camada e um indice gerado pelo enumerate.
        tuplasIndiceFeicao = [(indice, feicao) for indice, feicao in enumerate(features)]
        
        # Pegando o máximo indice que reflete na quantidade de feições que se tem:
        tamanhoLista = len(tuplasIndiceFeicao)
        maxIndice = tuplasIndiceFeicao[tamanhoLista - 1][0] # Pega o ultimo indice, que é o máximo
        
        # Criando um while que tem fim apenas quando atinge a quantida de pontos aleatórios colocados pelo usuário
        while numeroPontos != num_pontos:
            if feedback.isCanceled():
                break
                
            # Gerando um float que está compreendido entre 0 e 1 para multiplar o buffer para colocar o ponto
            randomFloat = random.random()
            
            # Gerando um inteiro que esteja no intervalo de 0 até o máximo índice
            randomInteiro = random.randint(0, maxIndice)
            
            # Pegando a feição correspondente do inteiro random que foi gerado acima:
            feicao = tuplasIndiceFeicao[randomInteiro][1]
            
            # Pegando o bounding box da feição selecionado ao acaso:
            bbox = feicao.geometry().boundingBox()
            
            # Coordenadas x e y do ponto que vai ser inserido
            xAleatorio = bbox.xMinimum() + randomFloat * raio
            yAleatorio = bbox.yMinimum() + randomFloat * raio
            
            # Criando uma nova feature, com o campo fields do tipo inteiro, adiciona o ponto de acordo com a coordenada.
            flagFeature = QgsFeature(fields)
            flagFeature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(xAleatorio, yAleatorio)))
            flagFeature['id'] = f'{feicao.id()}'
            
            # Adiciona na camada de saída a feature alterada.
            sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)
            
            # Soma um valor na variável numeroPontos:
            numeroPontos += 1
            
            # Progresso do processo.
            feedback.setProgress(int(numeroPontos * total))



        return {self.OUTPUT: dest_id}
