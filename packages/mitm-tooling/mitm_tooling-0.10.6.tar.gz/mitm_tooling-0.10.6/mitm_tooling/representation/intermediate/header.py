import itertools
from collections import defaultdict
from collections.abc import Iterable, Sequence
from functools import cached_property
from typing import Self

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.definition import get_mitm_def
from mitm_tooling.definition.definition_representation import MITM, ConceptName, TypeName
from mitm_tooling.definition.definition_tools import map_col_groups

from ..common import ColumnName, MITMSyntacticError, MITMTypeError, mk_attr_columns, mk_header_file_columns


class HeaderEntry(pydantic.BaseModel):
    """
    This (immutable) model represents a single entry in a `Header`, i.e., a type definition.
    """

    model_config = ConfigDict(frozen=True)

    concept: ConceptName
    kind: str
    type_name: TypeName
    attributes: tuple[ColumnName, ...]
    attribute_dtypes: tuple[MITMDataType, ...]

    @pydantic.model_validator(mode='after')
    def attr_check(self):
        if not len(self.attributes) == len(self.attribute_dtypes):
            raise MITMSyntacticError('Length of specified attributes and their data types differs.')
        return self

    @classmethod
    def of(
        cls,
        mitm: MITM,
        concept: ConceptName,
        type_name: TypeName,
        *attrs: tuple[ColumnName, MITMDataType],
    ) -> Self:
        if (props := get_mitm_def(mitm).get_properties(concept)) is not None:
            attributes, attribute_dtypes = zip(*attrs, strict=False) if attrs else ([], [])
            return cls(
                concept=concept,
                kind=props.key,
                type_name=type_name,
                attributes=tuple(attributes),
                attribute_dtypes=tuple(attribute_dtypes),
            )
        else:
            raise MITMSyntacticError(f'Concept {concept} does not exist in MITM definition {mitm}.')

    @classmethod
    def from_row(cls, row: Sequence[str], mitm: MITM) -> Self:
        kind, type_name = row[0], row[1]
        concept = get_mitm_def(mitm).inverse_concept_key_map.get(kind)
        if not concept:
            raise MITMTypeError(f'Encountered unknown concept key: "{kind}".')

        attrs, attr_dts = [], []
        for a, a_dt in zip(row[slice(2, None, 2)], row[slice(3, None, 2)], strict=False):
            if pd.notna(a) and pd.notna(a_dt):
                attrs.append(a)
                try:
                    mitm_dt = MITMDataType(a_dt.lower()) if a_dt else MITMDataType.Unknown
                    attr_dts.append(mitm_dt)
                except ValueError as e:
                    raise MITMTypeError(f'Encountered unrecognized data type during header import: {a_dt}.') from e

        return HeaderEntry(
            concept=concept, kind=kind, type_name=type_name, attributes=tuple(attrs), attribute_dtypes=tuple(attr_dts)
        )

    def iter_attr_dtype_pairs(self) -> Iterable[tuple[TypeName, MITMDataType]]:
        return zip(self.attributes, self.attribute_dtypes, strict=False)

    @cached_property
    def attr_k(self) -> int:
        return len(self.attributes)

    def to_row(self) -> list[str | None]:
        return [self.kind, self.type_name] + list(
            itertools.chain(*zip(self.attributes, map(str, self.attribute_dtypes), strict=False))
        )

    @cached_property
    def attr_name_map(self) -> dict[ColumnName, ColumnName]:
        return {a_anon: a for a_anon, a in zip(mk_attr_columns(self.attr_k), self.attributes, strict=False)}


def mk_type_table_columns(mitm: MITM, he: HeaderEntry) -> tuple[list[str], dict[str, MITMDataType]]:
    mitm_def = get_mitm_def(mitm)
    concept = he.concept
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
            'attributes': lambda: list(he.iter_attr_dtype_pairs()),
        },
    )

    return list(dts.keys()), dict(dts)


class Header(pydantic.BaseModel):
    """
    This (immutable) model represents the full type information of a MITM data set.
    """

    model_config = ConfigDict(frozen=True)

    mitm: MITM
    header_entries: frozenset[HeaderEntry] = pydantic.Field(default_factory=frozenset)

    @pydantic.model_validator(mode='after')
    def consistency_check(self):
        if len(set((he.kind, he.type_name) for he in self.header_entries)) != len(self.header_entries):
            raise MITMSyntacticError('Duplicate type definition in header.')
        return self

    @classmethod
    def of(cls, mitm: MITM, *header_entries: HeaderEntry) -> Self:
        return cls(mitm=mitm, header_entries=frozenset(header_entries))

    @classmethod
    def from_df(cls, df: pd.DataFrame, mitm: MITM) -> Self:
        return Header(
            mitm=mitm, header_entries=frozenset(HeaderEntry.from_row(row, mitm) for row in df.itertuples(index=False))
        )

    @property
    def max_k(self) -> int:
        return max(map(lambda he: he.attr_k, self.header_entries), default=0)

    def generate_header_df(self) -> pd.DataFrame:
        k = self.max_k
        deduplicated = {}
        for he in self.header_entries:
            deduplicated[(he.kind, he.type_name)] = he
        lol = [he.to_row() for he in deduplicated.values()]
        return pd.DataFrame(data=lol, columns=mk_header_file_columns(k))

    def get(self, concept: ConceptName, type_name: TypeName) -> HeaderEntry | None:
        return self.as_dict.get(concept, {}).get(type_name)

    @cached_property
    def mitm_def(self):
        return get_mitm_def(self.mitm)

    @cached_property
    def as_dict(self) -> dict[ConceptName, dict[TypeName, HeaderEntry]]:
        res = defaultdict(dict)
        for he in self.header_entries:
            res[he.concept][he.type_name] = he
        return dict(res)

    @cached_property
    def as_generalized_dict(self) -> dict[ConceptName, dict[TypeName, HeaderEntry]]:
        mitm_def = get_mitm_def(self.mitm)
        res = defaultdict(dict)
        for he in self.header_entries:
            res[mitm_def.get_parent(he.concept)][he.type_name] = he
        return dict(res)

    @cached_property
    def typed_df_columns(self) -> dict[ConceptName, dict[TypeName, tuple[list[str], dict[str, MITMDataType]]]]:
        return {
            c: {tp: mk_type_table_columns(self.mitm, he) for tp, he in tps.items()} for c, tps in self.as_dict.items()
        }

    def __add__(self, other):
        return Header(mitm=self.mitm, header_entries=self.header_entries | other.header_entries)
