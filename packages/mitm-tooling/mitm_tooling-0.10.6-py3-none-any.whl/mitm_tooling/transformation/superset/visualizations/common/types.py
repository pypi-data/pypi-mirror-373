from enum import StrEnum


class VisualizationType(StrEnum):
    MITM_Baseline = 'mitm-baseline'

    MAED_Baseline = 'maed-baseline'
    MAED_Experimental = 'maed-experimental'
    MAED_CustomChart = 'maed-custom-chart'
