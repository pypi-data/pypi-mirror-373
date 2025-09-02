import logging
import os
import pathlib

from mitm_tooling.utilities.io_utils import FilePath, dump_serialized, load_pydantic

from .definition_representation import MITM, MITMDefinition, MITMDefinitionFile

logger = logging.getLogger(__name__)

mitm_definitions: dict[MITM, MITMDefinition] = {}
mitm_definition_files = {MITM.MAED: 'maed.yaml', MITM.OCED: 'oced.yaml'}  # MITM.DPPD: 'dppd.yaml'


def load_definitions():
    for m, fn in mitm_definition_files.items():
        p = pathlib.Path(__file__).parent.joinpath(fn).resolve()
        mitm_definitions[m] = load_pydantic(MITMDefinitionFile, p).to_definition()


def write_mitm_def_schema(path: FilePath):
    path = os.path.join(path, 'mitm-def-schema.yaml')
    arg = MITMDefinitionFile.model_json_schema(by_alias=True)
    dump_serialized(arg, path, use_yaml=True)


def get_mitm_def(mitm: MITM) -> MITMDefinition | None:
    if mitm not in mitm_definitions:
        logger.error(f'Attempted to access non-existent MITM definition: {mitm}.')
        return None
    return mitm_definitions[mitm]


load_definitions()
