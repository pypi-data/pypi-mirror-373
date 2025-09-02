from enum import StrEnum

from ..abstract import MitMVisualizationsCreator
from .dashboards import MitMBaselineDashboard
from .types import VisualizationType


common_visualization_creators: dict[VisualizationType, type[MitMVisualizationsCreator]] = {
    VisualizationType.MITM_Baseline: MitMVisualizationsCreator.wrap_dashboard_creator(
        VisualizationType.MITM_Baseline, MitMBaselineDashboard
    ),
}
