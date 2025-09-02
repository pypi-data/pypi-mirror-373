from collections.abc import Iterable

from mitm_tooling.representation.intermediate import Header

from .asset_bundles import (
    DatasourceIdentifierBundle,
    MitMDatasetIdentifierBundle,
    SupersetDatasourceBundle,
    SupersetMitMDatasetBundle,
    SupersetVisualizationBundle,
)
from .common import DBConnectionInfo
from .from_intermediate import header_into_mitm_dataset_bundle, header_into_superset_datasource_bundle
from .visualizations.registry import VisualizationType, mk_visualization


def mk_superset_datasource_bundle(
    header: Header, db_conn_info: DBConnectionInfo, identifiers: DatasourceIdentifierBundle | None
) -> SupersetDatasourceBundle:
    return header_into_superset_datasource_bundle(header, db_conn_info, identifiers)


def mk_superset_visualization_bundle(
    header: Header,
    identifiers: MitMDatasetIdentifierBundle,
    visualization_types: Iterable[VisualizationType],
    just_placeholders: bool = False,
) -> SupersetVisualizationBundle:
    return SupersetVisualizationBundle.combine(
        *(
            mk_visualization(vzt, header, identifiers, just_placeholders=just_placeholders)
            for vzt in set(visualization_types)
        )
    )


def mk_superset_mitm_dataset_bundle(
    header: Header,
    db_conn_info: DBConnectionInfo,
    dataset_name: str,
    identifiers: MitMDatasetIdentifierBundle | None = None,
    visualization_types: Iterable[VisualizationType] | None = None,
    just_placeholders: bool = False,
) -> SupersetMitMDatasetBundle:
    mitm_dataset_bundle = header_into_mitm_dataset_bundle(header, db_conn_info, dataset_name, identifiers)
    if visualization_types is not None:
        mitm_dataset_bundle = mitm_dataset_bundle.replace_visualization_bundle(
            mk_superset_visualization_bundle(
                header, mitm_dataset_bundle.identifiers, visualization_types, just_placeholders=just_placeholders
            )
        )

    return mitm_dataset_bundle
