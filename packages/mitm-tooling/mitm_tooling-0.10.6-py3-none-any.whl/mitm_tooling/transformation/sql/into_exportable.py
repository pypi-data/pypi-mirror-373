from mitm_tooling.definition import ConceptName
from mitm_tooling.extraction.relational.data_models import TableMetaInfo, VirtualView
from mitm_tooling.extraction.relational.mapping import DataProvider, Exportable, HeaderEntryProvider, InstancesProvider
from mitm_tooling.extraction.relational.mapping.concept_mapping import ColumnContentProvider, InstancesPostProcessor
from mitm_tooling.representation.common import MITMTypeError
from mitm_tooling.representation.intermediate import Header
from mitm_tooling.representation.sql import SQLRepresentationSchema
from mitm_tooling.representation.sql.sql_representation.common import has_type_tables


def sql_rep_into_exportable(header: Header, sql_rep_schema: SQLRepresentationSchema) -> Exportable:
    """
    Create an `Exportable` from a `Header` by binding the concepts and types to the tables specified in the `SQLRepresentationSchema`.
    """

    data_providers: dict[ConceptName, list[DataProvider]] = {}
    mitm_def = header.mitm_def
    for he in header.header_entries:
        props = mitm_def.get_properties(he.concept)

        if has_type_tables(mitm_def, he.concept):
            sa_table = sql_rep_schema.get_type_table(he.concept, he.type_name)
        else:
            sa_table = sql_rep_schema.get_concept_table(he.concept)

        if sa_table is not None:
            tm = TableMetaInfo.from_sa_table(sa_table)
            typing_concept = props.typing_concept
            if he.concept not in data_providers:
                data_providers[he.concept] = []

            data_providers[he.concept].append(
                DataProvider(
                    instance_provider=InstancesProvider(
                        virtual_view=VirtualView(table_meta=tm, from_clause=sa_table, sa_table=sa_table)
                    ),
                    header_entry_provider=HeaderEntryProvider(
                        concept=he.concept,
                        table_meta=tm,
                        kind_provider=ColumnContentProvider.from_static('kind', he.kind),
                        type_provider=ColumnContentProvider.from_static(typing_concept, he.type_name),
                        attributes=list(he.attributes),
                        attribute_dtypes=list(he.attribute_dtypes),
                    ),
                    instance_postprocessor=InstancesPostProcessor(),
                )
            )
        else:
            raise MITMTypeError(f'Type {he.concept}:{he.type_name} is not present in the SQL representation schema.')

    return Exportable(mitm=header.mitm, data_providers=data_providers)
