from enum import StrEnum

from ..abstract import MitMVisualizationsCreator
from ..common.types import VisualizationType
from .dashboards import BaselineMAEDDashboard, CustomChartMAEDDashboard, ExperimentalMAEDDashboard


maed_visualization_creators: dict[VisualizationType, type[MitMVisualizationsCreator]] = {
    VisualizationType.MAED_Baseline: MitMVisualizationsCreator.wrap_dashboard_creator(
        VisualizationType.MAED_Baseline, BaselineMAEDDashboard
    ),
    VisualizationType.MAED_Experimental: MitMVisualizationsCreator.wrap_dashboard_creator(
        VisualizationType.MAED_Experimental, ExperimentalMAEDDashboard
    ),
    VisualizationType.MAED_CustomChart: MitMVisualizationsCreator.wrap_dashboard_creator(
        VisualizationType.MAED_CustomChart, CustomChartMAEDDashboard
    ),
}
