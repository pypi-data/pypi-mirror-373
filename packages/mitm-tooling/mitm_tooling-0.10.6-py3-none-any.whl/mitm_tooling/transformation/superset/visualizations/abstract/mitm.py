from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Self

from mitm_tooling.representation.intermediate import Header
from mitm_tooling.representation.sql import SQLRepresentationSchema, mk_sql_rep_schema

from ...asset_bundles import MitMDatasetIdentifierBundle, SupersetVisualizationBundle
from ...definitions import DashboardIdentifier, MitMDatasetIdentifier
from .base import DashboardCreator

DashboardCreatorConstructor = Callable[[Header, MitMDatasetIdentifier | None], DashboardCreator]


class MitMDashboardCreator(DashboardCreator, ABC):
    def __init__(
        self,
        header: Header,
        mitm_dataset_identifier: MitMDatasetIdentifier | None = None,
        sql_rep_schema: SQLRepresentationSchema | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.header: Header = header
        self.mitm_dataset_identifier: MitMDatasetIdentifier = mitm_dataset_identifier or MitMDatasetIdentifier()
        self.sql_rep_schema: SQLRepresentationSchema = sql_rep_schema or mk_sql_rep_schema(header)


def find_dash_id(
    mitm_dataset_identifiers: MitMDatasetIdentifierBundle, viz_collection: str, dash_name: str
) -> DashboardIdentifier | None:
    return mitm_dataset_identifiers.viz_id_map.get(viz_collection, {}).get(dash_name)


class MitMVisualizationsCreator(ABC):
    """
    Abstract base class for a Superset visualization factory, specifically for MITM visualizations.
    A visualization consists of a set of charts and dashboards.
    """

    def __init__(self, header: Header, **kwargs):
        super().__init__(**kwargs)
        self.header = header

    @property
    @abstractmethod
    def viz_collection_name(self) -> str: ...

    @property
    @abstractmethod
    def dashboard_creator_constructors(self) -> dict[str, DashboardCreatorConstructor]: ...

    def mk_dashboard_bundles(
        self, mitm_dataset_identifiers: MitMDatasetIdentifierBundle
    ) -> dict[str, SupersetVisualizationBundle]:
        creators: dict[str, DashboardCreator] = {
            name: constr(self.header, mitm_dataset_identifiers.mitm_dataset)
            for name, constr in self.dashboard_creator_constructors.items()
        }
        return {
            name: creator.mk_bundle(
                mitm_dataset_identifiers.ds_id_map,
                mitm_dataset_identifiers.ch_id_map,
                dashboard_identifier=find_dash_id(mitm_dataset_identifiers, self.viz_collection_name, creator.viz_name),
                viz_collection=self.viz_collection_name,
            )
            for name, creator in creators.items()
        }

    def mk_placeholder_bundle(
        self, mitm_dataset_identifiers: MitMDatasetIdentifierBundle
    ) -> SupersetVisualizationBundle:
        from .placeholders import EmptyDashboard

        creators: dict[str, DashboardCreator] = {
            name: constr(self.header, mitm_dataset_identifiers.mitm_dataset)
            for name, constr in self.dashboard_creator_constructors.items()
        }
        return SupersetVisualizationBundle.combine(
            *(
                EmptyDashboard().mk_bundle(
                    mitm_dataset_identifiers.ds_id_map,
                    mitm_dataset_identifiers.ch_id_map,
                    dashboard_identifier=find_dash_id(
                        mitm_dataset_identifiers, self.viz_collection_name, creator.viz_name
                    ),
                    viz_collection=self.viz_collection_name,
                )
                for name, creator in creators.items()
            )
        )

    def mk_bundle(self, mitm_dataset_identifiers: MitMDatasetIdentifierBundle) -> SupersetVisualizationBundle:
        bundle_map = self.mk_dashboard_bundles(mitm_dataset_identifiers)
        return SupersetVisualizationBundle.combine(*bundle_map.values())

    @classmethod
    def wrap_dashboard_creator(
        cls, viz_name: str, dashboard_creator_cls: type[MitMDashboardCreator], dashboard_name: str | None = None
    ) -> type[Self]:
        dashboard_creator_cls_ = dashboard_creator_cls
        viz_name_ = viz_name
        dashboard_name_ = dashboard_name or viz_name_

        class ConcreteVisualizationCreator(cls):
            @property
            def viz_collection_name(self) -> str:
                return viz_name_

            @property
            def dashboard_creator_constructors(self) -> dict[str, DashboardCreatorConstructor]:
                return {dashboard_name_: dashboard_creator_cls_}

        return ConcreteVisualizationCreator
