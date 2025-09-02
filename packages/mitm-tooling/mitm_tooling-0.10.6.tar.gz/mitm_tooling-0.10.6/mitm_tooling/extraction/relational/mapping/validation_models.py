from __future__ import annotations

from typing import Self

import pydantic
from pydantic import Field

from mitm_tooling.definition import MITM, ConceptName, ConceptProperties, MITMDefinition, OwnedRelations, get_mitm_def
from mitm_tooling.utilities.python_utils import inner_list_concat

from ..data_models.db_meta import DBMetaInfo, TableMetaInfo
from ..data_models.table_identifiers import SourceDBType, TableIdentifier


class IndividualMappingValidationContext(pydantic.BaseModel):
    parent: MappingGroupValidationContext
    claimed_concept: ConceptName
    examined_table: TableIdentifier
    vr: IndividualValidationResult

    @property
    def mitm_def(self) -> MITMDefinition:
        return self.parent.mitm_def

    @property
    def examined_table_meta(self) -> TableMetaInfo:
        return TableIdentifier.resolve_id(self.examined_table, self.db_metas)

    @property
    def db_metas(self) -> dict[SourceDBType, DBMetaInfo]:
        return self.parent.db_metas

    @property
    def gvr(self) -> GroupValidationResult:
        return self.parent.gvr

    @property
    def is_main_concept(self) -> bool:
        return self.claimed_concept in self.mitm_def.main_concepts

    @property
    def is_abstract_concept(self) -> bool:
        return self.claimed_concept in self.mitm_def.abstract_concepts

    @property
    def is_sub_concept(self) -> bool:
        return self.claimed_concept in self.mitm_def.parent_concept_map

    @property
    def is_base_concept(self) -> bool:
        return self.claimed_concept in self.mitm_def.base_concepts

    @property
    def relevant_relations(self) -> OwnedRelations:
        return self.mitm_def.get_relations(self.claimed_concept)

    @property
    def relevant_properties(self) -> ConceptProperties:
        return self.mitm_def.get_properties(self.claimed_concept)


class MappingGroupValidationContext(pydantic.BaseModel):
    mitm_def: MITMDefinition
    db_metas: dict[SourceDBType, DBMetaInfo]
    gvr: GroupValidationResult

    @classmethod
    def for_mitm(cls, mitm: MITM, db_metas: dict[SourceDBType, DBMetaInfo]):
        mitm_def = get_mitm_def(mitm)
        return MappingGroupValidationContext(mitm_def=mitm_def, db_metas=db_metas, gvr=GroupValidationResult())

    def derive_individual(self, claimed_concept: ConceptName, examined_table: TableIdentifier):
        return IndividualMappingValidationContext(
            parent=self, claimed_concept=claimed_concept, examined_table=examined_table, vr=self.gvr.new_individual()
        )

    def include_individual(self, ctxt: IndividualMappingValidationContext):
        self.gvr.include_individual(ctxt.claimed_concept, ctxt.examined_table, ctxt.vr)


class IndividualValidationResult(pydantic.BaseModel):
    is_valid: bool = Field(default=True)
    violations: list[str] = Field(default_factory=list)

    def ok(self):
        pass

    def failed(self, violation: str = None):
        self.is_valid = False
        if violation is not None:
            self.violations.append(violation)

    def include_check(self, check: bool, violation_message: str):
        if not check:
            self.failed(violation_message)


class GroupValidationResult(pydantic.BaseModel):
    individual_validations: dict[ConceptName, list[tuple[TableIdentifier, IndividualValidationResult]]] = Field(
        default_factory=dict
    )

    @pydantic.computed_field()
    @property
    def is_valid(self) -> bool:
        return all(vr.is_valid for li in self.individual_validations.values() for tid, vr in li)

    @staticmethod
    def new_individual() -> IndividualValidationResult:
        return IndividualValidationResult()

    @property
    def successes(self) -> dict[ConceptName, list[TableIdentifier]]:
        return {c: [tid for tid, vr in li if vr.is_valid] for c, li in self.individual_validations.items()}

    def include_individual(self, concept: ConceptName, tid: TableIdentifier, vr: IndividualValidationResult):
        if concept not in self.individual_validations:
            self.individual_validations[concept] = []
        self.individual_validations[concept].append((tid, vr))

    def merge(self, other: Self) -> Self:
        return self.__class__(
            individual_validations=inner_list_concat(self.individual_validations, other.individual_validations)
        )


class ExtendedGroupValidationResult(GroupValidationResult):
    @pydantic.computed_field()
    @property
    def violations(self) -> list[tuple[ConceptName, TableIdentifier, list[str]]]:
        return [(c, tid, vr.violations) for c, li in self.individual_validations.items() for tid, vr in li]
