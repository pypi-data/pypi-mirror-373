import pandas as pd
import sqlalchemy as sa

from mitm_tooling.definition import MITM, get_mitm_def
from mitm_tooling.representation.intermediate import Header, HeaderEntry
from mitm_tooling.representation.sql import SchemaName
from mitm_tooling.representation.sql.sql_representation.meta_tables import mk_meta_tables
from mitm_tooling.utilities.python_utils import notna_kwargs, pick_from_mapping
from mitm_tooling.utilities.sql_utils import AnyDBBind, use_db_bind


def mitm_db_into_header(bind: AnyDBBind, override_schema: SchemaName | None = None) -> Header | None:
    """
    Assuming a database with a MITM representation, reads the type information from the meta-tables.

    :param bind: a bind to a database
    :param override_schema: the name of the schema in which the tables are located
    :return: the type information, or None if it failed
    """

    sa_meta = sa.MetaData()
    meta_tables = mk_meta_tables(sa_meta, **notna_kwargs(target_schema=override_schema))
    with use_db_bind(bind) as conn:
        kvs = dict(conn.execute(sa.select(meta_tables.key_value)).all())
        if mitm_str := kvs.get('mitm'):
            mitm: MITM = MITM(mitm_str)
            get_mitm_def(mitm)
            t_left, t_right = meta_tables.types, meta_tables.type_attributes
            j = sa.join(t_left, t_right, isouter=True)

            type_attributes = conn.execute(
                sa.select(
                    *pick_from_mapping(t_left.c, ('kind', 'type', 'concept')),
                    *pick_from_mapping(t_right.c, ('attribute_order', 'attribute_name', 'attribute_dtype')),
                ).select_from(j)
            ).all()
            df = pd.DataFrame.from_records(
                type_attributes,
                columns=['kind', 'type', 'concept', 'attribute_order', 'attribute_name', 'attribute_dtype'],
            )
            hes = []
            for (kind, type_name, concept), idx in df.groupby(['kind', 'type', 'concept']).groups.items():
                attributes_df = (
                    df.loc[idx]
                    .dropna()
                    .sort_values('attribute_order', ascending=True)[['attribute_name', 'attribute_dtype']]
                )
                if len(attributes_df) > 0:
                    attribute_names, attribute_dtypes = zip(*attributes_df.itertuples(index=False), strict=False)
                else:
                    attribute_names, attribute_dtypes = (), ()
                # c = mitm_def.inverse_concept_key_map[kind]
                hes.append(
                    HeaderEntry(
                        concept=concept,
                        kind=kind,
                        type_name=type_name,
                        attributes=tuple(attribute_names),
                        attribute_dtypes=tuple(attribute_dtypes),
                    )
                )

            return Header(mitm=mitm, header_entries=frozenset(hes))
        return None
