from collections.abc import Sequence

from mitm_tooling.definition import MITM, ConceptName, RelationName, TypeName
from mitm_tooling.representation.intermediate import HeaderEntry

from ..common.charts import (
    ConceptCountTS,
    InstanceCountBigNumber,
    InstanceCountsHorizon,
    NumericAttributesTS,
    RelationPie,
    TypeAvgCountTS,
)


class MAEDConceptCountTS(ConceptCountTS):
    def __init__(
        self,
        concept: ConceptName,
        groupby_relations: Sequence[RelationName] = ('object',),
        time_relation: RelationName = 'time',
    ):
        super().__init__(
            mitm=MITM.MAED, concept=concept, groupby_relations=groupby_relations, time_relation=time_relation
        )


class MAEDRelationPie(RelationPie):
    def __init__(self, concept: ConceptName, relation: RelationName):
        super().__init__(mitm=MITM.MAED, concept=concept, relation=relation)


class MAEDInstanceCountBigNumber(InstanceCountBigNumber):
    def __init__(self, concept: ConceptName, type_name: TypeName, time_relation: RelationName | None = 'time'):
        super().__init__(mitm=MITM.MAED, concept=concept, type_name=type_name, time_relation=time_relation)


class MAEDInstanceCountsHorizon(InstanceCountsHorizon):
    def __init__(
        self,
        concept: ConceptName,
        time_relation: RelationName = 'time',
        additional_groupby_relations: Sequence[RelationName] = ('object',),
    ):
        super().__init__(
            mitm=MITM.MAED,
            concept=concept,
            time_relation=time_relation,
            additional_groupby_relations=additional_groupby_relations,
        )


class MAEDNumericAttributesTS(NumericAttributesTS):
    def __init__(
        self,
        header_entry: HeaderEntry,
        groupby_relations: Sequence[RelationName] = ('object',),
        time_relation: RelationName = 'time',
    ):
        super().__init__(
            mitm=MITM.MAED, header_entry=header_entry, groupby_relations=groupby_relations, time_relation=time_relation
        )


class MAEDTypeAvgCountTS(TypeAvgCountTS):
    def __init__(
        self,
        concept: ConceptName,
        type_name: TypeName,
        groupby_relations: Sequence[RelationName] = ('object',),
        time_relation: RelationName = 'time',
    ):
        super().__init__(
            mitm=MITM.MAED,
            concept=concept,
            type_name=type_name,
            groupby_relations=groupby_relations,
            time_relation=time_relation,
        )
