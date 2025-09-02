from uuid import UUID

from mitm_tooling.extraction.relational.data_models import DBMetaInfo
from mitm_tooling.extraction.relational.data_models.db_meta import DBMetaInfoBase
from mitm_tooling.extraction.relational.db import sa_reflect

from .asset_bundles import (
    DatasourceIdentifierBundle,
    MitMDatasetIdentifierBundle,
    SupersetDatasourceBundle,
    SupersetMitMDatasetBundle,
    SupersetVisualizationBundle,
)
from .common import DBConnectionInfo, MitMDatasetInfo, SQLiteFileOrEngine, _mk_sqlite_engine
from .factories.database import mk_database
from .factories.dataset import mk_dataset
from .factories.mitm_dataset import mk_mitm_dataset


def db_meta_into_superset_datasource_bundle(
    db_meta: DBMetaInfoBase, db_conn_info: DBConnectionInfo, identifiers: DatasourceIdentifierBundle | None = None
) -> SupersetDatasourceBundle:
    sqlalchemy_uri = db_conn_info.sql_alchemy_uri
    db_name = db_conn_info.db_name
    dialect = db_conn_info.dialect_cls()
    identifiers = identifiers or DatasourceIdentifierBundle()

    database = mk_database(
        name=db_name, sqlalchemy_uri=sqlalchemy_uri, uniquify_name=True, uuid=identifiers.database_uuid
    )

    database_uuid = database.uuid
    datasets = []
    ds_id_map = identifiers.ds_id_map or {}

    def ds_uuid(tn: str) -> UUID | None:
        if (ds_id := ds_id_map.get(tn)) is not None:
            return ds_id.uuid
        else:
            return None

    for _schema_name, schema_tables in db_meta.db_structure.items():
        for table_name, tm in schema_tables.items():
            datasets.append(mk_dataset(tm, database_uuid, dialect=dialect, uuid=ds_uuid(table_name)))

    return SupersetDatasourceBundle(database=database, datasets=datasets)


def db_meta_into_mitm_dataset_bundle(
    db_meta: DBMetaInfoBase,
    db_conn_info: DBConnectionInfo,
    dataset_info: MitMDatasetInfo,
    identifiers: MitMDatasetIdentifierBundle | None = None,
) -> SupersetMitMDatasetBundle:
    identifiers = identifiers or MitMDatasetIdentifierBundle()

    datasource_bundle = db_meta_into_superset_datasource_bundle(db_meta, db_conn_info, identifiers)

    mitm_dataset = mk_mitm_dataset(
        dataset_info.dataset_name,
        dataset_info.mitm,
        uuid=identifiers.mitm_dataset_uuid,
        header=dataset_info.header,
        database_uuid=datasource_bundle.database_uuid,
        table_uuids=datasource_bundle.dataset_uuids,
    )

    viz_bundle = SupersetVisualizationBundle(named_charts=identifiers.ch_id_map, viz_collections=identifiers.viz_id_map)
    return SupersetMitMDatasetBundle(
        mitm_dataset=mitm_dataset, datasource_bundle=datasource_bundle, visualization_bundle=viz_bundle
    )


def db_into_superset_datasource_bundle(
    arg: SQLiteFileOrEngine, db_conn_info: DBConnectionInfo, identifiers: DatasourceIdentifierBundle | None = None
) -> SupersetDatasourceBundle:
    identifiers = identifiers or DatasourceIdentifierBundle()

    engine = _mk_sqlite_engine(arg)

    meta, _ = sa_reflect(engine, allowed_schemas=[db_conn_info.schema_name])
    db_meta = DBMetaInfo.from_sa_meta(meta, default_schema=db_conn_info.schema_name)

    return db_meta_into_superset_datasource_bundle(db_meta, db_conn_info, identifiers)


def db_into_mitm_dataset_bundle(
    arg: SQLiteFileOrEngine,
    db_conn_info: DBConnectionInfo,
    dataset_info: MitMDatasetInfo,
    identifiers: MitMDatasetIdentifierBundle | None = None,
) -> SupersetMitMDatasetBundle:
    identifiers = identifiers or MitMDatasetIdentifierBundle()

    datasource_bundle = db_into_superset_datasource_bundle(arg, db_conn_info, identifiers)
    mitm_dataset = mk_mitm_dataset(
        dataset_info.dataset_name,
        dataset_info.mitm,
        uuid=identifiers.mitm_dataset_uuid,
        header=dataset_info.header,
        database_uuid=datasource_bundle.database_uuid,
        table_uuids=datasource_bundle.dataset_uuids,
    )
    viz_bundle = SupersetVisualizationBundle(named_charts=identifiers.ch_id_map, viz_collections=identifiers.viz_id_map)
    return SupersetMitMDatasetBundle(
        mitm_dataset=mitm_dataset, datasource_bundle=datasource_bundle, visualization_bundle=viz_bundle
    )
