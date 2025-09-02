from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

from mitm_tooling.definition import MITM
from mitm_tooling.representation.df import MITMDataFrames
from mitm_tooling.representation.intermediate import MITMData

if TYPE_CHECKING:
    from pm4py.objects.ocel.obj import OCEL


def mitm_dataframes_into_pm4py_ocel(mitm_dataframes: MITMDataFrames) -> OCEL:
    assert mitm_dataframes.header.mitm == MITM.OCED
    dfs = mitm_dataframes.dfs
    from pm4py.objects.ocel.obj import OCEL, constants

    events = pd.concat(list(dfs['event'].values()), ignore_index=True).rename(
        columns={
            'ocel_id': constants.DEFAULT_EVENT_ID,
            'time': constants.DEFAULT_EVENT_TIMESTAMP,
            'type': constants.DEFAULT_EVENT_ACTIVITY,
        }
    )

    objects = pd.concat(list(dfs['object'].values()), ignore_index=True).rename(
        columns={
            'ocel_id': constants.DEFAULT_OBJECT_ID,
            'type': constants.DEFAULT_OBJECT_TYPE,
        }
    )

    e2o = pd.concat(list(dfs['e2o'].values()), ignore_index=True).rename(
        columns={
            'qualifier': constants.DEFAULT_QUALIFIER,
            'event_id': constants.DEFAULT_EVENT_ID,
            'activity': constants.DEFAULT_EVENT_ACTIVITY,
            'object_id': constants.DEFAULT_OBJECT_ID,
            'object_type': constants.DEFAULT_OBJECT_TYPE,
        }
    )

    o2o = pd.concat(list(dfs['o2o'].values()), ignore_index=True).rename(
        columns={
            'qualifier': constants.DEFAULT_QUALIFIER,
            'source_id': constants.DEFAULT_OBJECT_ID,
            'source_type': constants.DEFAULT_OBJECT_TYPE,
            'target_id': constants.DEFAULT_OBJECT_ID + '_2',
            'target_type': constants.DEFAULT_OBJECT_TYPE + '_2',
        }
    )

    return OCEL(events=events, objects=objects, relations=e2o, o2o=o2o)


def mitm_data_into_pm4py_ocel(mitm_data: MITMData) -> OCEL:
    from mitm_tooling.transformation.df import mitm_data_into_mitm_dataframes

    return mitm_dataframes_into_pm4py_ocel(mitm_data_into_mitm_dataframes(mitm_data))
