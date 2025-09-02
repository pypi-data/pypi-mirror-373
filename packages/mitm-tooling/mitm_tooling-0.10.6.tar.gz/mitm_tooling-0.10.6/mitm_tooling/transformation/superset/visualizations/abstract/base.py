from abc import ABC, abstractmethod
from typing import Self

from mitm_tooling.representation.sql import TableName

from ...asset_bundles import NamedChartIdentifierMap, SupersetVisualizationBundle
from ...definitions import (
    ChartIdentifier,
    DashboardIdentifier,
    DatasetIdentifier,
    DatasetIdentifierMap,
    SupersetChartDef,
    SupersetDashboardDef,
)
from ...factories.dashboard import extract_charts

ChartDefCollection = dict[str, SupersetChartDef]
DashboardDefCollection = dict[str, SupersetDashboardDef]


class ChartCreator(ABC):
    """
    Abstract base class for a Superset chart factory.
    """

    @property
    @abstractmethod
    def slice_name(self) -> str:
        """
        The slice/chart name. It is used as the display name in Superset.
        """
        ...

    @abstractmethod
    def build_chart(
        self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier
    ) -> SupersetChartDef: ...

    def mk_chart(
        self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier | None = None
    ) -> SupersetChartDef:
        return self.build_chart(dataset_identifier, chart_identifier or ChartIdentifier(slice_name=self.slice_name))


class ChartCollectionCreator(ABC):
    """
    Abstract base class for a Superset chart collection factory.
    It can be used to bundle a set of charts that are generated dynamically, e.g., a chart per type.
    """

    @property
    @abstractmethod
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]: ...

    def mk_chart_collection(
        self, ds_id_map: DatasetIdentifierMap, ch_id_map: NamedChartIdentifierMap
    ) -> ChartDefCollection:
        res = {}
        for name, (table_name, cc) in self.chart_creators.items():
            ds_id = ds_id_map[table_name]
            ch_id = ch_id_map.get(name)
            res[name] = cc.mk_chart(ds_id, ch_id)
        return res

    @classmethod
    def cls_from_dict(cls: type[Self], arg: dict[str, tuple[TableName, ChartCreator]]) -> type[Self]:
        arg_ = arg

        class ConcreteChartCollectionCreator(cls):
            @property
            def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
                return arg_

        return ConcreteChartCollectionCreator

    @classmethod
    def union(cls, *wrapped_objs: Self) -> Self:
        wrapped_objs_ = wrapped_objs

        class UnionChartCollectionCreator(cls):
            @property
            def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
                return {}

            def mk_chart_collection(
                self, ds_id_map: DatasetIdentifierMap, ch_id_map: NamedChartIdentifierMap
            ) -> ChartDefCollection:
                charts = {}
                for ccc in wrapped_objs_:
                    charts.update(ccc.mk_chart_collection(ds_id_map, ch_id_map))
                return charts

        return UnionChartCollectionCreator()

    @classmethod
    def prefixed(cls, prefix: str, wrapped_obj: Self) -> Self:
        prefix_ = prefix

        class PrefixedChartCollectionCreator(cls):
            @property
            def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
                return {}

            def mk_chart_collection(
                self, ds_id_map: DatasetIdentifierMap, ch_id_map: NamedChartIdentifierMap
            ) -> ChartDefCollection:
                ch_id_map = {k.removeprefix(f'{prefix_}-'): v for k, v in ch_id_map.items()}
                return {f'{prefix_}-{k}': v for k, v in wrapped_obj.mk_chart_collection(ds_id_map, ch_id_map).items()}

        return PrefixedChartCollectionCreator()


class DashboardCreator(ABC):
    """
    Abstract base class for a Superset dashboard factory.
    It uses a `ChartCollectionCreator` to generate candidate charts and then lays them out onto a dashboard.
    """

    @property
    def viz_name(self) -> str:
        return self.__class__.__name__

    @property
    @abstractmethod
    def dashboard_title(self) -> str:
        """
        The dashboard title. It is used as the display name in Superset.
        """
        ...

    @property
    @abstractmethod
    def chart_collection_creator(self) -> ChartCollectionCreator: ...

    @abstractmethod
    def build_dashboard(
        self,
        ds_id_map: DatasetIdentifierMap,
        chart_collection: ChartDefCollection,
        dashboard_identifier: DashboardIdentifier,
    ) -> SupersetDashboardDef: ...

    def mk_dashboard(
        self,
        ds_id_map: DatasetIdentifierMap,
        chart_collection: ChartDefCollection,
        dashboard_identifier: DashboardIdentifier | None = None,
    ) -> SupersetDashboardDef:
        return self.build_dashboard(
            ds_id_map,
            chart_collection,
            dashboard_identifier or DashboardIdentifier(dashboard_title=self.dashboard_title),
        )

    def mk_bundle(
        self,
        ds_id_map: DatasetIdentifierMap,
        ch_id_map: NamedChartIdentifierMap,
        dashboard_identifier: DashboardIdentifier | None = None,
        viz_collection: str = 'default',
    ) -> SupersetVisualizationBundle:
        chart_collection = self.chart_collection_creator.mk_chart_collection(ds_id_map, ch_id_map)
        dashboard = self.mk_dashboard(ds_id_map, chart_collection, dashboard_identifier)
        selected_chart_uuids = extract_charts(dashboard)
        selected_charts = {k: v for k, v in chart_collection.items() if v.uuid in selected_chart_uuids}
        return SupersetVisualizationBundle(
            charts=list(selected_charts.values()),
            dashboards=[dashboard],
            named_charts={name: ch.identifier for name, ch in selected_charts.items()},
            viz_collections={viz_collection: {self.viz_name: dashboard.identifier}},
        )
