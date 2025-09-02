from collections.abc import Iterable

from mitm_tooling.definition import MITM
from mitm_tooling.representation.intermediate import Header

from ..asset_bundles import MitMDatasetIdentifierBundle
from ..visualizations.abstract import MitMVisualizationsCreator, SupersetVisualizationBundle
from .common.registry import common_visualization_creators, VisualizationType
from .maed.registry import maed_visualization_creators


mitm_visualization_creators: dict[MITM, dict[VisualizationType, type[MitMVisualizationsCreator]]] = {
    MITM.MAED: common_visualization_creators | maed_visualization_creators
}


def get_visualization_types(mitm: MITM) -> set[VisualizationType]:
    return set(mitm_visualization_creators.get(mitm, {}).keys())


def get_visualization_creator(
    mitm: MITM, visualization_type: VisualizationType
) -> type[MitMVisualizationsCreator] | None:
    if creators := mitm_visualization_creators.get(mitm):
        if (creator := creators.get(visualization_type)) is not None:
            return creator
    return None


def mk_visualization(
    visualization_type: VisualizationType,
    header: Header,
    identifiers: MitMDatasetIdentifierBundle,
    just_placeholders: bool = False,
) -> SupersetVisualizationBundle | None:
    if (creator_cls := get_visualization_creator(header.mitm, visualization_type)) is not None:
        creator = creator_cls(header)
        if just_placeholders:
            return creator.mk_placeholder_bundle(identifiers)
        else:
            return creator.mk_bundle(identifiers)
    return None


def mk_visualizations(
    visualization_types: Iterable[VisualizationType],
    header: Header,
    identifiers: MitMDatasetIdentifierBundle,
    just_placeholders: bool = False,
) -> dict[VisualizationType, SupersetVisualizationBundle]:
    return {
        vt: viz
        for vt in set(visualization_types)
        if ((viz := mk_visualization(vt, header, identifiers, just_placeholders=just_placeholders)) is not None)
    }
