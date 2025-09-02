from abc import ABC
from collections.abc import Callable, Collection

from mitm_tooling.definition import ConceptName, TypeName
from mitm_tooling.representation.intermediate import Header, HeaderEntry
from mitm_tooling.representation.sql import SQLRepresentationSchema, TableName

from ..abstract import ChartCollectionCreator, ChartCreator
from .charts import (
    TypeAttributesTableChart,
    TypeCountsTableChart,
    TypesTableChart,
)


class PerTypeChartCollection(ChartCollectionCreator, ABC):
    def __init__(self, concepts: Collection[ConceptName], sql_rep_schema: SQLRepresentationSchema):
        super().__init__()
        self.concepts = set(concepts)
        self.sql_rep_schema = sql_rep_schema


class PerTypeWithHeaderChartCollection(ChartCollectionCreator, ABC):
    def __init__(self, concepts: Collection[ConceptName], header: Header, sql_rep_schema: SQLRepresentationSchema):
        super().__init__()
        self.concepts = set(concepts)
        self.header = header
        self.sql_rep_schema = sql_rep_schema
        assert all(
            t in self.header.as_dict[c]
            for c in self.concepts
            for t in self.sql_rep_schema.type_tables.get(c, {}).keys()
        )


def per_type_charts(
    suffix: str, chart_factory: Callable[[ConceptName, TypeName], ChartCreator]
) -> type[PerTypeChartCollection]:
    class CustomPerTypeChartCollection(PerTypeChartCollection):
        @property
        def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
            ccs = {}
            for concept in self.concepts:
                for type_name, tbl in self.sql_rep_schema.type_tables.get(concept, {}).items():
                    ccs[f'{concept}-{type_name}-{suffix}'] = (tbl.name, chart_factory(concept, type_name))
            return ccs

    return CustomPerTypeChartCollection


def per_type_with_header_charts(
    suffix: str, chart_factory: Callable[[HeaderEntry], ChartCreator]
) -> type[PerTypeWithHeaderChartCollection]:
    class CustomPerTypeWithHeaderChartCollection(PerTypeWithHeaderChartCollection):
        @property
        def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
            ccs = {}
            for concept in self.concepts:
                for type_name, tbl in self.sql_rep_schema.type_tables.get(concept, {}).items():
                    he = self.header.get(concept, type_name)
                    ccs[f'{concept}-{type_name}-{suffix}'] = (tbl.name, chart_factory(he))
            return ccs

    return CustomPerTypeWithHeaderChartCollection


class HeaderMetaTablesCollection(ChartCollectionCreator):
    def __init__(self, header: Header, sql_rep_schema: SQLRepresentationSchema):
        super().__init__()
        self.header = header
        self.sql_rep_schema = sql_rep_schema
        assert self.sql_rep_schema.meta_tables.type_attributes is not None

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        types_tbl_name = self.sql_rep_schema.meta_tables.types.name
        type_attrs_tbl_name = self.sql_rep_schema.meta_tables.type_attributes.name
        ccs = {}
        ccs['header-types-table'] = (types_tbl_name, TypesTableChart())
        ccs['header-counts-table'] = (types_tbl_name, TypeCountsTableChart())
        for c, type_map in self.header.as_dict.items():
            for type_name in type_map:
                ccs[f'{c}-{type_name}-attributes-table'] = (
                    type_attrs_tbl_name,
                    TypeAttributesTableChart(self.header.mitm, c, type_name),
                )
        return ccs
