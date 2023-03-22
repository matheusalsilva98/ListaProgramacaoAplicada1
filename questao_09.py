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
Solução Questão 9
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
                       QgsProcessingParameterField,
                       QgsProcessingParameterFeatureSource,
                       QgsWkbTypes,
                       QgsProcessingParameterFeatureSink)
from qgis import processing


class LinhasConectadas(QgsProcessingAlgorithm):
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
    ATRIBUTOS = 'ATRIBUTOS'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LinhasConectadas()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'linhasconectadas'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Linhas Conectadas')

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
        return self.tr("Analisa os atributos das linhas conectadas e verifica os atributos dessas linhas para saber se são iguais.")

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
                [QgsProcessing.TypeVectorLine] # O input tem que necessariamente ser apenas do tipo linha, que é o objetivo da verificação.
            )
        )
        
        # Parãmetro de atributos.
        self.addParameter(
            QgsProcessingParameterField(
                self.ATRIBUTOS,
                self.tr('ATRIBUTOS'),
                None,
                self.INPUT,
                QgsProcessingParameterField.Any,
                allowMultiple=True,
                optional=True
            )
        )

        # Parãmetro de saída.
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer'),
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

        # Se a entrada for nula gerar erro.
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        
        # Definindo a variável fields para criar o campo do atributo 'flag'
        fields = QgsFields()
        fields.append(QgsField("flag", QVariant.String))
        
        # Definindo as características da nossa camada de saída.
        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields, # Vamos criar um campo de atributo para a camada de saída para retornar os id's das camadas que estão conectadas e possuem o mesmo atributo.
            QgsWkbTypes.Point, # Retorna uma camada do tipo ponto, diferente da camada de entrada (apenas linha).
            source.sourceCrs()
        )

        # Enviar para o usuário o feedback.
        feedback.pushInfo('CRS is {}'.format(source.sourceCrs().authid()))
        
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

        # Verifica se a sink é nula, caso seja gera erro.
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
        
        # Encontrando a razão do 100 no número de feature presentes no INPUT, para definir o feedback para o usuário.
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        
        # Pegando as features com o método getFeatures().
        features = source.getFeatures()
        pontos = []
        for current, feat in enumerate(features):
            # Parada sob comando do usuário pode ser cancelado o processo.
            if feedback.isCanceled():
                break
                
            # Pegando o Bounding Box de cada feature, para analisar para cada feature, mas apenas no retângulo próximo
            index = QgsSpatialIndex(source.getFeatures(), flags=QgsSpatialIndex.FlagStoreFeatureGeometries)
            for fid in index.intersects(feat.geometry().boundingBox()): # Retorna os ID's onde o feat cruza o Bounding Box para pegar o contexto espacial
                if fid == feat.id(): # Ignora os seus próprios valores.
                    continue
                fgeom = index.geometry(fid) # Guardando em uma variável a geometria correspondente ao indice.
                
                # Criando uma função que compara as geometrias já existentes com a nova para ver se não está sendo inserido novos pontos
                def pontoEquals(fgeom, feat, listaPontos):
                    """
                    Analisando se o ponto já foi inserido com o metódo equals() do QgsGeometry, analisando se
                    o ponto já está inserido na lista de Pontos que é nosso terceiro argumento.
                    """
                    x = fgeom.intersection(feat.geometry())
                    booleanCoord = True
                    for ponto in listaPontos:
                        if x.equals(ponto):
                            booleanCoord = False
                        else:
                            continue
                    return booleanCoord
                    
                # Verificando se as geometrias estão se intersectando.
                if fgeom.intersects(feat.geometry()): # Checando as intersecções entre as geometrias.
                    engine = QgsGeometry.createGeometryEngine(fgeom.constGet())
                    # Verificando se a intersecção é de uma borda de uma LineString com outra borda de outra LineString.
                    if (engine.relate(feat.geometry().constGet()) == 'FF1F00102'):
                        flagFeature = QgsFeature(fields) # Criando a feição com o atributo 'flag'
                        # Verificando com a função criada, para observar se já há o ponto.
                        if pontoEquals(fgeom, feat, pontos):
                            if comparaAtributos(feat, fid):
                                pontos.append(fgeom.intersection(feat.geometry()))
                                flagFeature.setGeometry(QgsGeometry.fromWkt((fgeom.intersection(feat.geometry())).asWkt())) # Pegando apenas os pontos e atribuindo à feição os pontos de intersecção.
                                flagFeature['flag'] = f'Feições da camada {source.sourceName()} de id1={fid} e id2 = {feat.id()} estão conectadas e possuem mesmo conjunto de atributos.'
                                # Adicionando a feature na camada de saída
                                sink.addFeature(flagFeature, QgsFeatureSink.FastInsert)

            # Barra de progresso do nosso projeto.
            feedback.setProgress(int(current * total))

        # O retorno da função, retornando nossa saída.
        return {self.OUTPUT: dest_id}
