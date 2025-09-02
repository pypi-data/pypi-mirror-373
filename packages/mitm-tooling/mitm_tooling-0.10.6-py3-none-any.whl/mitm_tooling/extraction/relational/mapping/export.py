from __future__ import annotations

import itertools
from collections.abc import Iterator
from typing import TYPE_CHECKING

import pandas as pd
import pydantic
import sqlalchemy as sa
from pydantic import ConfigDict

from mitm_tooling.definition import MITM, ConceptName, get_mitm_def
from mitm_tooling.representation.common import mk_concept_file_header
from mitm_tooling.representation.intermediate import (
    Header,
    HeaderEntry,
    MITMData,
    StreamingConceptData,
    StreamingMITMData,
)
from mitm_tooling.utilities.sql_utils import AnyDBBind

from ..data_models import DBMetaInfo, SourceDBType, TableIdentifier, VirtualView
from ..transformation import PostProcessing
from ..transformation.db_transformation import TableNotFoundException
from .concept_mapping import (
    ConceptMapping,
    ConceptMappingException,
    DataProvider,
    InstancesPostProcessor,
    InstancesProvider,
)

STREAMING_CHUNK_SIZE = 100_000

if TYPE_CHECKING:
    pass


class Exportable(pydantic.BaseModel):
    """
    This model represents an ETL export of (mapped) MITM data from a relational database.
    The `data_providers` attribute is a dictionary mapping concept names to lists of `DataProviders`.
    A `DataProvider` represents a source of instances for a specific concept in the form a `VirtualView`, a post-processing pipeline, and a `HeaderEntryProvider`.

    The `Exportable` is not bound to a specific database connection but rather represents an ETL pipeline from a relational DB to MITM Data.
    By providing a bind to a database, it can be used to generate `MITMData` and `StreamingMITMData`, or be exported to a zip file. (also in a fully streamed fashion)
    The header data can also be generated without necessarily querying all the instances.
    In contrast to `StreamingMITMData`, the `Exportable` is expected to be reusable, i.e., its data sources are not read-once.

    Note:
        This model is not serializable as it contains `VirtualViews` which contain SQLAlchemy objects.
        Essentially, it is indirectly bound to specific database metadata.
        Consider `StandaloneDBMapping` for a serializable representation that can be turned into an `Exportable`.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    data_providers: dict[ConceptName, list[DataProvider]]
    filename: str | None = None

    @property
    def generalized_data_providers(self) -> dict[ConceptName, list[DataProvider]]:
        mitm_def = get_mitm_def(self.mitm)

        temp = {}
        for c, dps in self.data_providers.items():
            main_concept = mitm_def.get_parent(c)
            if main_concept not in temp:
                temp[main_concept] = []
            temp[main_concept].extend(dps)

        return temp

    def generate_header(self, bind: AnyDBBind) -> Header:
        header_entries = []
        for _, dps in self.data_providers.items():
            for dp in dps:
                header_entries.extend(dp.header_entry_provider.apply_db(bind))
        return Header(mitm=self.mitm, header_entries=frozenset(header_entries))

    def generate_mitm_data(self, bind: AnyDBBind) -> MITMData:
        header_entries = []

        tables = {}
        for c, dps in self.generalized_data_providers.items():
            dfs = []
            for dp in dps:
                df = dp.instance_provider.apply_db(bind)
                df = dp.instance_postprocessor.apply_df(df)
                dfs.append(df)
                header_entries += dp.header_entry_provider.apply_df(df)

            tables[c] = pd.concat(dfs, axis='index', ignore_index=True)

        header = Header(mitm=self.mitm, header_entries=frozenset(header_entries))

        return MITMData(header=header, concept_dfs=tables)

    def generate_streaming_mitm_data(
        self, bind: AnyDBBind, streaming_chunk_size: int = STREAMING_CHUNK_SIZE
    ) -> StreamingMITMData:
        data_sources = {}

        for main_concept, dps in self.generalized_data_providers.items():
            k = max(dp.header_entry_provider.type_arity for dp in dps)
            concept_file_columns = mk_concept_file_header(self.mitm, main_concept, k)[0]
            structure_df = pd.DataFrame(columns=concept_file_columns)

            chunk_iterators = []
            for dp in dps:

                def local_iter(
                    dp: DataProvider = dp, columns=tuple(concept_file_columns)
                ) -> Iterator[tuple[pd.DataFrame, list[HeaderEntry]]]:
                    for df_chunk in dp.instance_provider.apply_db_chunked(bind, streaming_chunk_size):
                        df_chunk = dp.instance_postprocessor.apply_df(df_chunk)
                        hes = dp.header_entry_provider.apply_df(df_chunk)
                        # this does nothing more than adding NaN columns to fill up to the number of attributes in the concept file (k)
                        df_chunk = df_chunk.reindex(columns=list(columns), copy=False)
                        yield df_chunk, hes

                chunk_iterators.append(local_iter())

            data_sources[main_concept] = StreamingConceptData(
                structure_df=structure_df, chunk_iterators=chunk_iterators
            )

        return StreamingMITMData(mitm=self.mitm, data_sources=data_sources)

    def bind(self, bind: AnyDBBind) -> BoundExportable:
        return BoundExportable(bind=bind, exportable=self)


class BoundExportable(pydantic.BaseModel):
    """
    An `Exportable` that is bound to a specific database connection.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    bind: AnyDBBind
    exportable: Exportable

    def generate_header(self) -> Header:
        return self.exportable.generate_header(self.bind)

    def generate_mitm_data(self) -> MITMData:
        return self.exportable.generate_mitm_data(self.bind)

    def generate_streaming_mitm_data(self, streaming_chunk_size: int = STREAMING_CHUNK_SIZE) -> StreamingMITMData:
        return self.exportable.generate_streaming_mitm_data(self.bind, streaming_chunk_size=streaming_chunk_size)


class MappingExport(pydantic.BaseModel):
    """
    This model represents a mapping of relational data to MITM data, including optional post processing.
    It is used as an intermediate representation for an ETL pipeline that is yet to be bound to specific database metadata.
    """

    mitm: MITM
    concept_mappings: list[ConceptMapping]
    post_processing: PostProcessing | None = None
    filename: str | None = None

    def apply(self, db_metas: dict[SourceDBType, DBMetaInfo]) -> Exportable:
        data_providers: dict[ConceptName, list[DataProvider]] = {}

        meta = sa.MetaData(schema='export')
        for i, concept_mapping in enumerate(self.concept_mappings):
            if concept_mapping.mitm != self.mitm:
                continue

            try:
                header_entry_provider, q = concept_mapping.apply(db_metas)
            except TableNotFoundException as e:
                raise ConceptMappingException('Concept Mapping failed.') from e

            # mitm_def = get_mitm_def(self.mitm)
            # main_concept = mitm_def.get_parent(concept_mapping.concept)
            concept = concept_mapping.concept

            vv = VirtualView.from_from_clause(f'{concept}_{i}', q, meta, schema='export')
            instances_provider = InstancesProvider(virtual_view=vv)

            pp_transforms = []
            if self.post_processing is not None:
                pp_transforms = list(
                    itertools.chain(
                        tpp.transforms
                        for tpp in self.post_processing.table_postprocessing
                        if TableIdentifier.check_equal(tpp.target_table, concept_mapping.base_table)
                    )
                )
            post_processor = InstancesPostProcessor(transforms=pp_transforms)

            if concept not in data_providers:
                data_providers[concept] = []
            data_providers[concept].append(
                DataProvider(
                    instance_provider=instances_provider,
                    instance_postprocessor=post_processor,
                    header_entry_provider=header_entry_provider,
                )
            )

        return Exportable(mitm=self.mitm, data_providers=data_providers, filename=self.filename)
