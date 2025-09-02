from mitm_tooling.extraction.relational.data_models import DBMetaInfo
from mitm_tooling.representation.intermediate import Header, MITMData
from mitm_tooling.representation.sql import mk_sql_rep_schema
from mitm_tooling.utilities.python_utils import notna_kwargs


def header_into_db_meta(header: Header, override_schema: str | None = None) -> DBMetaInfo:
    """
    Derive a `DBMetaInfo` object from a `Header` by generating a `SQLRepresentationSchema` and calling `sql_rep_schema_into_db_meta`.
    """
    from .from_sql import sql_rep_schema_into_db_meta

    sql_rep_schema = mk_sql_rep_schema(header, **notna_kwargs(target_schema=override_schema))
    return sql_rep_schema_into_db_meta(sql_rep_schema)


def mitm_data_into_db_meta(mitm_data: MITMData, override_schema: str | None = None) -> DBMetaInfo:
    """
    Derive a `DBMetaInfo` object from `MITMData` by calling `header_into_db_meta` on the dataset header.
    """
    return header_into_db_meta(mitm_data.header, override_schema=override_schema)
