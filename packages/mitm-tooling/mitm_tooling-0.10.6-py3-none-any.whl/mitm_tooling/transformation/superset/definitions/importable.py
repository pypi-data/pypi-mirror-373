from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import pydantic

from .chart import SupersetChartDef
from .constants import StrDatetime, SupersetDefFile
from .core import BaseSupersetDefinition
from .dashboard import SupersetDashboardDef
from .database import SupersetDatabaseDef
from .dataset import SupersetDatasetDef
from .mitm_dataset import SupersetMitMDatasetDef


class MetadataType(StrEnum):
    Database = 'Database'
    SqlaTable = 'SqlaTable'
    Slice = 'Slice'
    Chart = 'Chart'
    Dashboard = 'Dashboard'
    Assets = 'assets'
    MitMDataset = 'MitMDataset'


class SupersetDefFolder(BaseSupersetDefinition, ABC):
    @property
    @abstractmethod
    def folder_dict(self) -> dict[str, Any]:
        pass


class SupersetMetadataDef(SupersetDefFile):
    model_config = pydantic.ConfigDict(use_enum_values=True)

    type: MetadataType
    version: str = '1.0.0'
    timestamp: StrDatetime = pydantic.Field(default_factory=lambda: datetime.now(UTC))

    @property
    def filename(self) -> str:
        return 'metadata'


class SupersetAssetsImport(SupersetDefFolder):
    databases: list[SupersetDatabaseDef] | None = None
    datasets: list[SupersetDatasetDef] | None = None
    charts: list[SupersetChartDef] | None = None
    dashboards: list[SupersetDashboardDef] | None = None
    metadata: SupersetMetadataDef = pydantic.Field(default_factory=SupersetMetadataDef)

    @property
    def folder_dict(self) -> dict[str, Any]:
        folder_dict: dict[str, SupersetDefFile] = {'.': self.metadata}
        dbs = {}
        if self.databases:
            dbs |= {db.uuid: db.database_name for db in self.databases}
            folder_dict['databases'] = [db for db in self.databases]
        if self.datasets:
            db_dss = defaultdict(list)
            for ds in self.datasets:
                db_dss[dbs.get(ds.database_uuid, 'unknown_db')].append(ds)
            folder_dict['datasets'] = db_dss
        if self.charts:
            folder_dict['charts'] = self.charts
        if self.dashboards:
            folder_dict['dashboards'] = self.dashboards
        return {'my_import': folder_dict}


class SupersetMitMDatasetImport(SupersetDefFolder):
    mitm_datasets: list[SupersetMitMDatasetDef] | None
    base_assets: SupersetAssetsImport | None
    metadata: SupersetMetadataDef = pydantic.Field(
        default_factory=lambda: SupersetMetadataDef(type=MetadataType.MitMDataset)
    )

    @property
    def folder_dict(self) -> dict[str, Any]:
        asset_folder_dict = self.base_assets.folder_dict if self.base_assets else {'my_import': {}}
        asset_folder_dict['my_import']['.'] = self.metadata
        dbs = {}
        if self.base_assets.databases:
            dbs = {db.uuid: db.database_name for db in self.base_assets.databases}
        if self.mitm_datasets:
            mitm_dss = defaultdict(list)
            for mitm_ds in self.mitm_datasets:
                mitm_dss[dbs[mitm_ds.database_uuid]].append(mitm_ds)
            asset_folder_dict['my_import']['mitm_datasets'] = mitm_dss
        return asset_folder_dict
