from ...definitions import DashboardIdentifier, DatasetIdentifierMap, SupersetDashboardDef
from .base import ChartCollectionCreator, ChartDefCollection, DashboardCreator

NoChartsCreator = ChartCollectionCreator.cls_from_dict({})


class EmptyDashboard(DashboardCreator):
    @property
    def chart_collection_creator(self) -> ChartCollectionCreator:
        return NoChartsCreator()

    @property
    def dashboard_title(self) -> str:
        return 'Empty Dashboard'

    def build_dashboard(
        self,
        ds_id_map: DatasetIdentifierMap,
        chart_collection: ChartDefCollection,
        dashboard_identifier: DashboardIdentifier,
    ) -> SupersetDashboardDef:
        from ...factories.dashboard_constructors import DASH, HEADER

        d = DASH(self.dashboard_title, HEADER('PLACEHOLDER'))

        from mitm_tooling.transformation.superset.factories.dashboard import mk_dashboard_def

        return mk_dashboard_def(
            dashboard_identifier.dashboard_title,
            position_data=d(),
            description='An empty placeholder dashboard',
            uuid=dashboard_identifier.uuid,
        )
