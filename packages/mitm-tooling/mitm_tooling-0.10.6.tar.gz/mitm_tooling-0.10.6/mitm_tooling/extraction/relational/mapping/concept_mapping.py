from collections.abc import Iterable
from functools import cached_property
from typing import Self

import pandas as pd
import pydantic
import sqlalchemy as sa
from pydantic import Field

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.definition import MITM, ConceptName, RelationName, get_mitm_def
from mitm_tooling.definition.definition_tools import map_col_groups
from mitm_tooling.representation import ColumnName
from mitm_tooling.representation.intermediate import HeaderEntry
from mitm_tooling.utilities.python_utils import ExtraInfoExc, normalize_into_dict
from mitm_tooling.utilities.sql_utils import AnyDBBind, use_db_bind

from ..data_models import (
    AnyTableIdentifier,
    DBMetaInfo,
    Queryable,
    SourceDBType,
    TableIdentifier,
    TableMetaInfo,
    VirtualView,
)
from ..transformation.db_transformation import TableNotFoundException, TableTransforms, col_by_name
from ..transformation.df_transformation import transform_df
from .validation_models import IndividualMappingValidationContext, MappingGroupValidationContext


class ColumnContentProvider(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    column_name: str
    static_value: str | None = None
    is_present_in_table: bool = False
    column_element: sa.ColumnElement

    @classmethod
    def from_tuple(
        cls, tup: tuple[str, sa.ColumnElement], is_present_in_table: bool, static_value: str | None = None
    ) -> Self:
        return ColumnContentProvider(
            column_name=tup[0],
            column_element=tup[1],
            is_present_in_table=is_present_in_table,
            static_value=static_value,
        )

    @classmethod
    def from_static(cls, name: str, value: str, dt: MITMDataType = MITMDataType.Text) -> Self:
        ce = sa.literal(value, dt.sa_sql_type_cls).label(name)
        return ColumnContentProvider(column_name=name, column_element=ce, is_present_in_table=False, static_value=value)


class HeaderEntryProvider(pydantic.BaseModel):
    concept: ConceptName
    table_meta: TableMetaInfo
    kind_provider: ColumnContentProvider
    type_provider: ColumnContentProvider
    attributes: list[ColumnName]
    attribute_dtypes: list[MITMDataType]

    @property
    def type_arity(self):
        return len(self.attributes)

    def apply_db(self, bind: AnyDBBind) -> list[HeaderEntry]:
        with use_db_bind(bind) as conn:
            distinct = conn.execute(
                sa.select(self.kind_provider.column_element, self.type_provider.column_element).distinct()
            ).all()
        return self.apply_iterable(((kind, type_name) for kind, type_name in distinct))

    def apply_df(self, df: pd.DataFrame) -> list[HeaderEntry]:
        iterable = None
        if (k := self.kind_provider.static_value) is not None and (t := self.type_provider.static_value) is not None:
            iterable = ((k, t),)
        elif (k := self.kind_provider.static_value) is not None:
            iterable = set((k, t) for t in df.loc[:, self.type_provider.column_name])
        elif (t := self.type_provider.static_value) is not None:
            iterable = set((k, t) for k in df.loc[:, self.kind_provider.column_name])
        else:
            iterable = set(
                df.loc[:, [self.kind_provider.column_name, self.type_provider.column_name]].itertuples(
                    index=False, name=None
                )
            )
        return self.apply_iterable(iterable)

    def apply_iterable(self, distinct: Iterable[tuple[str, str]]) -> list[HeaderEntry]:
        return [
            HeaderEntry(
                concept=self.concept,
                kind=kind,
                type_name=type_name,
                attributes=tuple(self.attributes),
                attribute_dtypes=tuple(self.attribute_dtypes),
            )
            for kind, type_name in distinct
        ]


class InstancesPostProcessor(pydantic.BaseModel):
    transforms: list[TableTransforms] = pydantic.Field(default_factory=list)

    def apply_df(self, df: pd.DataFrame):
        return transform_df(df, self.transforms)


class InstancesProvider(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    virtual_view: VirtualView

    def apply_db(self, bind: AnyDBBind) -> pd.DataFrame:
        tm = self.virtual_view.table_meta
        with use_db_bind(bind) as conn:
            results = conn.execute(tm.queryable_source.select()).all()
        df = pd.DataFrame.from_records(results, columns=list(tm.columns))
        return df

    def apply_db_chunked(self, bind: AnyDBBind, chunk_size: int = 100_000) -> Iterable[pd.DataFrame]:
        tm = self.virtual_view.table_meta
        with use_db_bind(bind) as conn:
            results = conn.execute(tm.queryable_source.select()).partitions(chunk_size)
            for result_chunk in results:
                yield pd.DataFrame.from_records(result_chunk, columns=list(tm.columns))


class DataProvider(pydantic.BaseModel):
    """
    This model represents a data provider for instances and types of a MITM concept.
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    instance_provider: InstancesProvider
    instance_postprocessor: InstancesPostProcessor
    header_entry_provider: HeaderEntryProvider


class StaticValidableGroup:
    def validate_static(self, context: MappingGroupValidationContext) -> None:
        raise NotImplementedError


class StaticValidableIndividual:
    def validate_static(self, context: IndividualMappingValidationContext) -> None:
        raise NotImplementedError


class IdentityProvider(StaticValidableIndividual, pydantic.BaseModel):
    identity_columns: dict[RelationName, ColumnName] = Field(default_factory=dict)

    def validate_static(self, context: IndividualMappingValidationContext) -> None:
        vr = context.vr
        vr.include_check(
            set(self.identity_columns.keys()) == set(context.relevant_relations.identity.keys()),
            'identity columns are not mapped mapped as defined',
        )
        vr.include_check(
            set(self.identity_columns.values()) <= context.examined_table_meta.col_set,
            'identity columns not present in table',
        )


class InlineRelationsProvider(StaticValidableIndividual, pydantic.BaseModel):
    inline_relations: dict[RelationName, ColumnName] = Field(default_factory=dict)

    def validate_static(self, context: IndividualMappingValidationContext) -> None:
        vr = context.vr
        vr.include_check(
            set(self.inline_relations.keys()) == set(context.relevant_relations.inline.keys()),
            'inline relations columns are not mapped as defined',
        )
        vr.include_check(
            set(self.inline_relations.values()) <= context.examined_table_meta.col_set,
            'inline relations columns not present in table',
        )


class ForeignRelation(pydantic.BaseModel):
    fk_columns: dict[RelationName, ColumnName] | list[ColumnName]
    referred_table: AnyTableIdentifier

    @cached_property
    def fk_columns_(self) -> dict[RelationName, ColumnName]:
        return normalize_into_dict(self.fk_columns)


class ForeignRelationsProvider(StaticValidableIndividual, pydantic.BaseModel):
    foreign_relations: dict[RelationName, ForeignRelation] = Field(default_factory=dict)

    def validate_static(self, context: IndividualMappingValidationContext) -> None:
        vr = context.vr
        vr.include_check(
            set(self.foreign_relations.keys()) == set(context.relevant_relations.foreign.keys()),
            'not precisely the specified foreign relations are mapped',
        )
        for q, rel in self.foreign_relations.items():
            fk_rel_info = context.relevant_relations.foreign.get(q, None)
            if fk_rel_info is None:
                vr.failed('there is no foreign relation declaration of this name in the definition')
                return

            target_concept = fk_rel_info.target_concept
            fk_rel_def = fk_rel_info.fk_relations
            # fk_def = context.relevant_relations.foreign_relations_to_concept(target_concept)

            vr.include_check(
                set(rel.fk_columns_.keys()) == set(fk_rel_def.keys()), 'foreign key columns do not match definition'
            )
            vr.include_check(
                set(rel.fk_columns_.values()) <= set(context.examined_table_meta.columns),
                'foreign key columns not present in table',
            )

            vr.include_check(
                TableIdentifier.resolve_id(rel.referred_table, context.db_metas) is not None,
                'target table does not exist in db schema',
            )

            if rel.referred_table not in context.gvr.successes.get(target_concept, []):
                vr.failed('there is no valid mapping of the target table to the declared target concept')


class ConceptMappingException(ExtraInfoExc):
    pass


class ConceptMapping(StaticValidableGroup, pydantic.BaseModel):
    """
    This model represents a mapping of a database table to a MITM concept.
    Specifically, it records how the columns in the table correspond to the ones required by the concept in the specified MITM.

    Given database schema information, it can be validated and produce a SQL selectable source of instances of the concept (in the format of the intermediate representation).
    """

    mitm: MITM
    concept: ConceptName

    base_table: AnyTableIdentifier
    kind_col: ColumnName | None = None
    type_col: ColumnName

    identity_columns: dict[RelationName, ColumnName] | list[ColumnName] = Field(default_factory=dict)
    inline_relations: dict[RelationName, ColumnName] | list[ColumnName] = Field(default_factory=dict)
    foreign_relations: dict[RelationName, ForeignRelation] = Field(default_factory=dict)

    attributes: list[ColumnName] = Field(default_factory=list)
    attribute_dtypes: list[MITMDataType] = Field(default_factory=list)

    @cached_property
    def identity_provider(self) -> IdentityProvider:
        return IdentityProvider(identity_columns=normalize_into_dict(self.identity_columns))

    @cached_property
    def inline_relations_provider(self) -> InlineRelationsProvider:
        return InlineRelationsProvider(inline_relations=normalize_into_dict(self.inline_relations))

    @cached_property
    def foreign_relations_provider(self) -> ForeignRelationsProvider:
        return ForeignRelationsProvider(foreign_relations=self.foreign_relations)

    def get_k(self) -> int:
        return len(self.attribute_dtypes)

    def validate_static(self, context: MappingGroupValidationContext) -> None:
        ctxt = context.derive_individual(
            claimed_concept=self.concept, examined_table=TableIdentifier.from_any(self.base_table)
        )
        vr = ctxt.vr
        table_meta = ctxt.examined_table_meta
        if table_meta is None:
            vr.failed('table not present in db schema')
            return

        vr.include_check(not ctxt.is_base_concept, 'base concepts cannot be mapped explicitly')
        if ctxt.is_abstract_concept:
            vr.include_check(self.kind_col is not None, 'abstract concepts need a column defining their kind')
        if self.kind_col is not None:
            vr.include_check(
                self.kind_col in table_meta.col_set, f'specified kind column ({self.kind_col}) not present in table'
            )

        vr.include_check(
            self.type_col in table_meta.col_set, f'specified type column ({self.type_col}) not present in table'
        )

        self.identity_provider.validate_static(ctxt)
        self.inline_relations_provider.validate_static(ctxt)
        self.foreign_relations_provider.validate_static(ctxt)

        vr.include_check(
            ctxt.relevant_properties.permit_attributes or len(self.attributes) == 0,
            'this concept does not permit attributes',
        )
        vr.include_check(
            len(self.attributes) == len(self.attribute_dtypes),
            'number of declared attribute data types not equal to attributes',
        )
        vr.include_check(set(self.attributes) <= table_meta.col_set, 'attribute columns not present in table')

        # TODO validate data types

        context.include_individual(ctxt)

    def apply(self, db_metas: dict[SourceDBType, DBMetaInfo]) -> tuple[HeaderEntryProvider, Queryable]:
        mitm_def = get_mitm_def(self.mitm)
        concept_properties = mitm_def.get_properties(self.concept)

        table_meta = TableIdentifier.resolve_id(self.base_table, db_metas)
        if table_meta is None:
            raise TableNotFoundException(
                f'Base table {self.base_table} not found for export request: {self.mitm}:{self.concept}'
            )

        base_queryable = table_meta.queryable_source

        def make_type_col() -> tuple[str, sa.ColumnElement]:
            return concept_properties.typing_concept, sa.label(
                concept_properties.typing_concept, col_by_name(base_queryable, self.type_col, raise_on_missing=True)
            )

        def make_kind_col() -> tuple[str, sa.ColumnElement]:
            ce = None
            if self.kind_col is not None:
                ce = sa.label('kind', col_by_name(base_queryable, self.kind_col, raise_on_missing=True))
            else:
                ce = sa.literal_column(f'"{concept_properties.key}"', MITMDataType.Text.sa_sql_type).label('kind')
            return 'kind', ce

        def make_identity_cols() -> list[tuple[str, sa.ColumnElement]]:
            return [
                (q, sa.label(q, col_by_name(base_queryable, col, raise_on_missing=True)))
                for q, col in self.identity_provider.identity_columns.items()
            ]

        def make_inline_relation_cols() -> list[tuple[str, sa.ColumnElement]]:
            return [
                (q, sa.label(q, col_by_name(base_queryable, col, raise_on_missing=True)))
                for q, col in self.inline_relations_provider.inline_relations.items()
            ]

        def make_foreign_relation_cols() -> list[tuple[str, sa.ColumnElement]]:
            foreign_relation_cols = []
            for fk_rel in self.foreign_relations_provider.foreign_relations.values():
                for q, col in fk_rel.fk_columns_.items():
                    foreign_relation_cols.append(
                        (q, sa.label(q, col_by_name(base_queryable, col, raise_on_missing=True)))
                    )
            return foreign_relation_cols

        def make_attribute_cols() -> list[tuple[str, sa.ColumnElement]]:
            return [
                (f'a_{i}', sa.label(f'a_{i}', col_by_name(base_queryable, a, raise_on_missing=True)))
                for i, a in enumerate(self.attributes, 1)
            ]

        selected_columns, created_columns = map_col_groups(
            mitm_def,
            self.concept,
            {
                'kind': make_kind_col,
                'type': make_type_col,
                'identity': make_identity_cols,
                'inline': make_inline_relation_cols,
                'foreign': make_foreign_relation_cols,
                'attributes': make_attribute_cols,
            },
        )

        queryable = sa.select(*selected_columns).select_from(base_queryable).subquery()

        header_entry_provider = HeaderEntryProvider(
            concept=self.concept,
            table_meta=table_meta,
            kind_provider=ColumnContentProvider.from_tuple(
                make_kind_col(), 'kind' in created_columns, concept_properties.key
            ),
            type_provider=ColumnContentProvider.from_tuple(
                make_type_col(), concept_properties.typing_concept in created_columns
            ),
            attributes=self.attributes,
            attribute_dtypes=self.attribute_dtypes,
        )
        return header_entry_provider, queryable
