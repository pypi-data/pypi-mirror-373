from collections.abc import Sequence

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.definition import MITM, ConceptName, RelationName, TypeName, get_mitm_def
from mitm_tooling.representation.intermediate import HeaderEntry
from mitm_tooling.utilities.identifiers import naive_pluralize

from ...definitions import (
    ChartIdentifier,
    DatasetIdentifier,
    FilterOperator,
    SupersetAggregate,
    SupersetChartDef,
)
from ...factories.core import mk_adhoc_filter, mk_adhoc_metric, mk_adhoc_metrics, mk_metric
from ...factories.generic_charts import (
    mk_agg_table_chart,
    mk_avg_count_time_series_chart,
    mk_big_number_chart,
    mk_horizon_chart,
    mk_metric_time_series_chart,
    mk_pie_chart,
    mk_raw_table_chart,
    mk_time_series_bar_chart,
)
from ..abstract import ChartCreator


class TypeCountsTableChart(ChartCreator):
    @property
    def slice_name(self) -> str:
        return 'Header Type Counts'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_agg_table_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            metrics=[mk_adhoc_metric('type', SupersetAggregate.COUNT)],
            groupby=['kind', 'concept'],
            uuid=chart_identifier.uuid,
        )


class TypesTableChart(ChartCreator):
    @property
    def slice_name(self) -> str:
        return 'Header Types'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_raw_table_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            ['kind', 'concept', 'type'],
            orderby=[('kind', True), ('type', True)],
            uuid=chart_identifier.uuid,
        )


class ConceptTypesTableChart(ChartCreator):
    def __init__(self, mitm: MITM, concept: ConceptName):
        self.concept = concept
        self.props = get_mitm_def(mitm).get_properties(concept)

    @property
    def slice_name(self) -> str:
        return f'{self.concept.title()} Types'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_raw_table_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            ['type', 'attribute_name'],
            filters=[mk_adhoc_filter('kind', FilterOperator.EQUALS, self.props.key)],
            orderby=[('type', True)],
            uuid=chart_identifier.uuid,
        )


class TypeAttributesTableChart(ChartCreator):
    def __init__(self, mitm: MITM, concept: ConceptName, type_name: TypeName):
        self.concept = concept
        self.type_name = type_name
        self.props = get_mitm_def(mitm).get_properties(concept)

    @property
    def slice_name(self) -> str:
        return f'{self.type_name.title()} Attributes'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_raw_table_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            ['attribute_name', 'attribute_dtype'],
            filters=[
                mk_adhoc_filter('kind', FilterOperator.EQUALS, self.props.key),
                mk_adhoc_filter('type', FilterOperator.EQUALS, self.type_name),
            ],
            orderby=[('attribute_order', True)],
            uuid=chart_identifier.uuid,
        )


class TypeAvgCountTS(ChartCreator):
    """
    A chart that shows the average count of a particular type over time.
    E.g., average number of events per day.
    This time series can be faceted by the groupby relations.
    """

    def __init__(
        self,
        mitm: MITM,
        concept: ConceptName,
        type_name: TypeName,
        groupby_relations: Sequence[RelationName] | None = None,
        time_relation: RelationName = 'time',
    ):
        self.concept = concept
        self.type_name = type_name
        self.groupby_relations = list(groupby_relations) if groupby_relations is not None else []
        self.time_relation = time_relation
        props, rels = get_mitm_def(mitm).get(concept)
        self.props = props
        self.relations = rels
        defined_relations = set(self.relations.relation_names)
        assert set(self.groupby_relations) <= defined_relations
        assert self.time_relation in self.relations.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.type_name.title()} Count Time Series'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_avg_count_time_series_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            groupby_cols=self.groupby_relations,
            time_col=self.time_relation,
            uuid=chart_identifier.uuid,
        )


class NumericAttributesTS(ChartCreator):
    def __init__(
        self,
        mitm: MITM,
        header_entry: HeaderEntry,
        groupby_relations: Sequence[RelationName] | None = None,
        time_relation: RelationName = 'time',
    ):
        self.header_entry = header_entry
        self.groupby_relations = list(groupby_relations) if groupby_relations is not None else []
        self.time_relation = time_relation
        props, rels = get_mitm_def(mitm).get(header_entry.concept)
        self.props = props
        self.relations = rels
        defined_relations = set(self.relations.relation_names)
        assert set(self.groupby_relations) <= defined_relations
        assert self.time_relation in self.relations.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.header_entry.type_name.title()} Time Series'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_metric_time_series_chart(
            chart_identifier.slice_name,
            mk_adhoc_metrics(
                [
                    a
                    for a, dt in zip(self.header_entry.attributes, self.header_entry.attribute_dtypes, strict=False)
                    if dt == MITMDataType.Numeric
                ]
            ),
            dataset_identifier,
            groupby_cols=self.groupby_relations,
            time_col=self.time_relation,
            uuid=chart_identifier.uuid,
        )


class InstanceCountsHorizon(ChartCreator):
    def __init__(
        self,
        mitm: MITM,
        concept: ConceptName,
        time_relation: RelationName = 'time',
        additional_groupby_relations: Sequence[RelationName] | None = None,
    ):
        self.concept = concept
        self.time_relation = time_relation
        self.additional_groupby_relations = additional_groupby_relations
        props, rels = get_mitm_def(mitm).get(concept)
        self.props = props
        assert self.time_relation in rels.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.concept.title()} Horizon'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        # I am counting on the fact that every programmatically created dataset has a COUNT(*) metric
        # alternatively, use mk_adhoc_metric(self.props.typing_concept, SupersetAggregate.COUNT)
        count_metric = mk_metric('*', SupersetAggregate.COUNT).metric_name
        groupby = [self.props.typing_concept]
        if self.additional_groupby_relations is not None:
            groupby.extend(self.additional_groupby_relations)
        return mk_horizon_chart(
            chart_identifier.slice_name,
            [count_metric],
            dataset_identifier,
            groupby_cols=groupby,
            time_col=self.time_relation,
        )


class InstanceCountBigNumber(ChartCreator):
    def __init__(
        self, mitm: MITM, concept: ConceptName, type_name: TypeName, time_relation: RelationName | None = 'time'
    ):
        self.type_name = type_name
        self.time_relation = time_relation
        props, rels = get_mitm_def(mitm).get(concept)
        self.props = props
        if self.time_relation:
            assert self.time_relation in rels.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.type_name.title()} Instances'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        count_metric = mk_metric('*', SupersetAggregate.COUNT).metric_name
        return mk_big_number_chart(
            chart_identifier.slice_name,
            count_metric,
            dataset_identifier,
            agg='sum',
            time_col=self.time_relation,
            uuid=chart_identifier.uuid,
        )


class RelationPie(ChartCreator):
    def __init__(self, mitm: MITM, concept: ConceptName, relation: RelationName):
        self.relation = relation
        assert relation in get_mitm_def(mitm).get_relations(concept).relation_names

    @property
    def slice_name(self) -> str:
        return naive_pluralize(self.relation).title()

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_pie_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            col=self.relation,
            dt=MITMDataType.Text,
            groupby_cols=[self.relation],
            uuid=chart_identifier.uuid,
        )


class ConceptCountTS(ChartCreator):
    def __init__(
        self,
        mitm: MITM,
        concept: ConceptName,
        groupby_relations: Sequence[RelationName] | None = None,
        time_relation: RelationName = 'time',
    ):
        self.concept = concept
        self.groupby_relations = list(groupby_relations) if groupby_relations is not None else []
        self.time_relation = time_relation
        props, rels = get_mitm_def(mitm).get(concept)
        self.props = props
        self.relations = rels
        defined_relations = set(self.relations.relation_names)
        assert set(self.groupby_relations) <= defined_relations
        assert self.time_relation in self.relations.relation_names

    @property
    def slice_name(self) -> str:
        return f'{self.concept.title()} Counts'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        filters = [mk_adhoc_filter('kind', FilterOperator.EQUALS, self.props.key)] if self.props.is_sub else None
        return mk_time_series_bar_chart(
            chart_identifier.slice_name,
            dataset_identifier,
            self.props.typing_concept,
            MITMDataType.Text,
            x_col=self.time_relation,
            groupby_cols=self.groupby_relations,
            filters=filters,
            uuid=chart_identifier.uuid,
        )
