from __future__ import annotations

import itertools

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.definition import MITM, ConceptName, get_mitm_def
from mitm_tooling.definition.definition_tools import map_col_groups


def guess_k_of_header_df(df):
    return sum(1 for c in df.columns if c.startswith('a_') and not c.startswith('a_dt'))


def mk_header_file_columns(k: int) -> list[str]:
    return ['kind', 'type'] + list(itertools.chain(*((f'a_{i}', f'a_dt_{i}') for i in range(1, k + 1))))


def mk_concept_file_header(mitm: MITM, concept: ConceptName, k: int) -> tuple[list[str], dict[str, MITMDataType]]:
    mitm_def = get_mitm_def(mitm)
    _, dts = map_col_groups(
        mitm_def,
        concept,
        {
            'kind': lambda: ('kind', MITMDataType.Text),
            'type': lambda: (mitm_def.get_properties(concept).typing_concept, MITMDataType.Text),
            'identity': lambda: mitm_def.resolve_identity_type(concept).items(),
            'inline': lambda: mitm_def.resolve_inlined_types(concept).items(),
            'foreign': lambda: [
                (name, dt)
                for fk_types in mitm_def.resolve_foreign_types(concept).values()
                for name, dt in fk_types.items()
            ],
            'attributes': lambda: [(f'a_{i}', MITMDataType.Unknown) for i in range(1, k + 1)],
        },
    )

    return list(dts.keys()), dict(dts)


def mk_attr_columns(k: int) -> list[str]:
    return [f'a_{i}' for i in range(1, k + 1)]
