from mitm_tooling.extraction.relational.data_models import SourceDBType
from mitm_tooling.extraction.relational.mapping import ConceptMapping, ForeignRelation
from mitm_tooling.representation.intermediate import Header
from mitm_tooling.representation.sql import SQLRepresentationSchema


def sql_rep_into_mappings(header: Header, sql_rep_schema: SQLRepresentationSchema) -> list[ConceptMapping]:
    """
    Generate a list of `ConceptMappings` from a `Header` and `SQLRepresentationSchema`.
    Can be used to create `Mapping`
    """

    mitm_def = header.mitm_def
    cms = []
    for he in header.header_entries:
        concept_properties, relations = mitm_def.get(he.concept)
        base_table = None
        main_concept = mitm_def.get_parent(he.concept)
        if (type_t := sql_rep_schema.get_type_table(he.concept, he.type_name)) is not None:
            base_table = type_t
        elif (concept_t := sql_rep_schema.get_concept_table(main_concept)) is not None:
            base_table = concept_t
        if base_table is not None:
            cms.append(
                ConceptMapping(
                    mitm=header.mitm,
                    concept=he.concept,
                    base_table=(SourceDBType.OriginalDB, base_table.schema, base_table.name),
                    kind_col='kind' if 'kind' in base_table.columns else None,
                    type_col=concept_properties.typing_concept,
                    identity_columns=list(relations.identity.keys()),
                    inline_relations=list(relations.inline.keys()),
                    foreign_relations={
                        fk_name: ForeignRelation(
                            fk_columns=list(fk_info.fk_relations.keys()),
                            referred_table=(SourceDBType.OriginalDB, target_concept_t.schema, target_concept_t.name),
                        )
                        for fk_name, fk_info in relations.foreign.items()
                        if (target_concept_t := sql_rep_schema.concept_tables.get(fk_info.target_concept)) is not None
                    },
                    attributes=list(he.attributes),
                    attribute_dtypes=list(he.attribute_dtypes),
                )
            )

    return cms
