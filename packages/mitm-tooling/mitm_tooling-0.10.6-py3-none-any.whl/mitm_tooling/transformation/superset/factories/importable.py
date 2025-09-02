from ..definitions import (
    MetadataType,
    SupersetAssetsImport,
    SupersetChartDef,
    SupersetDashboardDef,
    SupersetDatabaseDef,
    SupersetDatasetDef,
    SupersetMetadataDef,
    SupersetMitMDatasetDef,
    SupersetMitMDatasetImport,
)


def mk_metadata(metadata_type: MetadataType) -> SupersetMetadataDef:
    return SupersetMetadataDef(type=metadata_type or MetadataType.Assets)


def mk_assets_import(
    databases: list[SupersetDatabaseDef] = None,
    datasets: list[SupersetDatasetDef] = None,
    charts: list[SupersetChartDef] = None,
    dashboards: list[SupersetDashboardDef] = None,
    metadata_type: MetadataType = MetadataType.Assets,
) -> SupersetAssetsImport:
    return SupersetAssetsImport(
        databases=databases,
        datasets=datasets,
        charts=charts,
        dashboards=dashboards,
        metadata=mk_metadata(metadata_type),
    )


def mk_mitm_dataset_import(
    mitm_datasets: list[SupersetMitMDatasetDef],
    base_assets: SupersetAssetsImport,
    metadata_type: MetadataType = MetadataType.MitMDataset,
) -> SupersetMitMDatasetImport:
    return SupersetMitMDatasetImport(
        mitm_datasets=mitm_datasets, base_assets=base_assets, metadata=mk_metadata(metadata_type)
    )
