from abc import ABC
from collections import defaultdict
from typing import Any, Literal

import pydantic

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.definition import ConceptName, TypeName

from ..common import MITMSyntacticError
from .header import Header, HeaderEntry


class Delta(pydantic.BaseModel, ABC):
    kind: Literal['insertion', 'deletion', 'update']


class AttributeDelta(Delta):
    pass


class AttributeUpdate(AttributeDelta):
    kind: Literal['update'] = 'update'
    index: int
    name: str
    dt: MITMDataType


class AttributeInsertion(AttributeUpdate):
    kind: Literal['insertion'] = 'insertion'


class AttributeDeletion(AttributeDelta):
    kind: Literal['deletion'] = 'deletion'
    index: int
    name: str


class RowDelta(Delta):
    pass


class RowInsertion(RowDelta):
    kind: Literal['insertion'] = 'insertion'


class RowDeletion(RowDelta):
    kind: Literal['deletion'] = 'deletion'


class RowUpdate(RowDelta):
    kind: Literal['update'] = 'update'
    affected_identity: tuple[Any, ...]


class TypeDelta(Delta):
    header_entry: HeaderEntry

    @property
    def concept(self) -> ConceptName:
        return self.header_entry.concept

    @property
    def type_name(self) -> TypeName:
        return self.header_entry.type_name


class TypeUpdate(TypeDelta):
    kind: Literal['update'] = 'update'
    deltas: list[AttributeDelta]


class TypeInsertion(TypeDelta):
    kind: Literal['insertion'] = 'insertion'


class TypeDeletion(TypeDelta):
    kind: Literal['deletion'] = 'deletion'


class HeaderDelta(pydantic.BaseModel):
    type_deltas: list[TypeDelta]
    attribute_deltas: dict[ConceptName, dict[TypeName, list[AttributeDelta]]]


def diff_header_entry(a: HeaderEntry, b: HeaderEntry) -> TypeUpdate | None:
    if a.concept != b.concept or a.type_name != b.type_name:
        raise MITMSyntacticError('Cannot diff header entries from different concepts or types.')
    if a == b:
        return None
    deltas = []
    for i, ((attr_a, dt_a), (attr_b, dt_b)) in enumerate(
        zip(
            zip(a.attributes, a.attribute_dtypes, strict=False),
            zip(b.attributes, b.attribute_dtypes, strict=False),
            strict=False,
        )
    ):
        if attr_a != attr_b or dt_a != dt_b:
            deltas.append(AttributeUpdate(index=i, name=attr_b, dt=dt_b))
    k_a, k_b = a.attr_k, b.attr_k
    x = k_b - k_a
    if x > 0:
        for j, (attr_b, dt_b) in zip(
            range(k_a, k_b), zip(b.attributes[k_a:], b.attribute_dtypes[k_a:], strict=False), strict=False
        ):
            deltas.append(AttributeInsertion(index=j, name=attr_b, dt=dt_b))
    elif x < 0:
        for j, (attr_a, _dt_a) in zip(
            range(k_b, k_a), zip(a.attributes[k_b:], a.attribute_dtypes[k_b:], strict=False), strict=False
        ):
            deltas.append(AttributeDeletion(index=j, name=attr_a))
    return TypeUpdate(header_entry=a, deltas=deltas)


def diff_header(a: Header, b: Header) -> HeaderDelta:
    if not a.mitm == b.mitm:
        raise MITMSyntacticError('Cannot diff headers from different MITMs.')
    type_deltas = []
    attribute_deltas = defaultdict(lambda: defaultdict(list))
    for concept, type_dict_a in a.as_dict.items():
        if concept not in b.as_dict:
            type_deltas.extend(TypeDeletion(header_entry=he) for he in type_dict_a.values())
        else:
            type_dict_b = b.as_dict[concept]
            for type_name, he_a in type_dict_a.items():
                if type_name not in type_dict_b:
                    type_deltas.append(TypeDeletion(header_entry=he_a))
                else:
                    he_b = type_dict_b[type_name]
                    td = diff_header_entry(he_a, he_b)
                    if td is not None:
                        type_deltas.append(td)
                        attribute_deltas[concept][type_name].extend(td.deltas)

    for concept, type_dict_b in b.as_dict.items():
        if concept not in a.as_dict:
            type_deltas.extend(TypeInsertion(header_entry=he) for he in type_dict_b.values())
        else:
            type_dict_a = a.as_dict[concept]
            for type_name, he_b in type_dict_b.items():
                if type_name not in type_dict_a:
                    type_deltas.append(TypeInsertion(header_entry=he_b))
                else:
                    # this case should have been handled above
                    pass
    return HeaderDelta(type_deltas=type_deltas, attribute_deltas=attribute_deltas)
