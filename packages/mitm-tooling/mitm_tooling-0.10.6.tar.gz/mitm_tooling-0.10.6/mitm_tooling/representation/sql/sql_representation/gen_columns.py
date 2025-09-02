from __future__ import annotations

from collections.abc import Generator

import sqlalchemy as sa

from mitm_tooling.definition import MITM, ConceptName

from .common import (
    MitMConceptColumnGenerator,
    mk_within_concept_id_col_name,
)


def gen_within_concept_id_col(mitm: MITM, concept: ConceptName) -> Generator[tuple[str, sa.Column], None, None]:
    n = mk_within_concept_id_col_name(mitm, concept)
    yield n, sa.Column(n, sa.Integer, nullable=False, unique=True)


# for typing
column_generators: tuple[MitMConceptColumnGenerator, ...] = (gen_within_concept_id_col,)
