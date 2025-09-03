from __future__ import annotations

import uuid
from typing import List, Dict, Tuple

from bigeye_sdk.functions.search_and_match_functions import fuzzy_match_lists
from bigeye_sdk.functions.table_functions import get_table_column_id
from bigeye_sdk.generated.com.bigeye.models.generated import ComparisonColumnMapping, ColumnApplicableMetricTypes, \
    TableApplicableMetricTypes, IdAndDisplayName, Table
from bigeye_sdk.model.protobuf_message_facade import (
    SimpleColumnMapping
)


def build_ccm(scm: SimpleColumnMapping, source_table: Table, target_table: Table) -> ComparisonColumnMapping:
    cm = ComparisonColumnMapping()
    cm.source_column = IdAndDisplayName(id=get_table_column_id(source_table, scm.source_column_name),
                                        display_name=scm.source_column_name)
    cm.target_column = IdAndDisplayName(id=get_table_column_id(target_table, scm.target_column_name),
                                        display_name=scm.target_column_name)
    cm.metrics = [m.to_datawatch_object() for m in scm.metrics]
    return cm


def infer_column_mappings(source_metric_types: TableApplicableMetricTypes,
                          target_metric_types: TableApplicableMetricTypes) -> List[ComparisonColumnMapping]:
    # TODO add fuzzy matching here too.
    """
    Used to infer column mappings, based on TableApplicableMetricTypes.

    :param source_metric_types: The TableApplicableMetricTypes of the source table
    :param target_metric_types: The TableApplicableMetricTypes of the target table

    :returns: List[ComparisonColumnMapping]

    >>> infer_column_mappings(source_metric_types=smt, target_metric_types=tmt)
    [ComparisonColumnMapping(source_column=IdAndDisplayName(id=29128800, display_name='id'), target_column=IdAndDisplayName(id=29128800, display_name='id'), metrics=[MetricType(predefined_metric=PredefinedMetric(metric_name=<PredefinedMetricName.COUNT_NULL: 2>), template_metric=TemplateMetric(template_id=0, aggregation_type=0, template_name=''), is_metadata_metric=False, is_table_metric=False)], user_defined=False)]
    """
    sct: Dict[str, ColumnApplicableMetricTypes] = {
        i.column.display_name.lower(): i
        for i in source_metric_types.applicable_metric_types
    }

    tct: Dict[str, ColumnApplicableMetricTypes] = {
        i.column.display_name.lower(): i
        for i in target_metric_types.applicable_metric_types
    }

    matched = fuzzy_match_lists(list(sct.keys()), list(tct.keys()), 85)

    column_mappings: List[ComparisonColumnMapping] = [
        ComparisonColumnMapping(source_column=sct[m[0]].column, target_column=tct[m[1]].column,
                                metrics=sct[m[0]].applicable_metric_types)
        for m in matched
        if sct[m[0]].applicable_metric_types == tct[m[1]].applicable_metric_types
    ]

    return column_mappings


def match_tables_by_name(source_tables: List[Table], target_tables: List[Table]) -> Dict[str, Tuple[int, int]]:
    """
    Creates a dictionary of table ids keyed by a delta name
    :param source_tables: list of source Table objects
    :param target_tables: list of target Table objects
    :return: Dict[delta_name:str, Tuple[source_table_id, target_table_id]
    """
    sourced: Dict[str, Table] = {t.name.lower(): t for t in target_tables}
    targetd: Dict[str, Table] = {t.name.lower(): t for t in source_tables}

    # TODO match columns too.
    matched = fuzzy_match_lists(sourced.keys(), targetd.keys(), 96)

    r: Dict[str, Tuple[int, int]] = {}

    for m in matched:
        st: Table = sourced[m[0]]
        tt: Table = targetd[m[1]]
        k = f"(suggested_delta) {st.schema_name}.{st.name} -> {tt.schema_name}.{tt.name} - {str(uuid.uuid4())}"
        r[k] = st.id, tt.id

    return r


if __name__ == "__main__":
    import doctest

    globs = locals()
    template = {
        "id": 1883035,
        "applicableMetricTypes": [
            {
                "column": {
                    "id": 29128800,
                    "displayName": "id"
                },
                "applicableMetricTypes": [
                    {
                        "predefinedMetric": {
                            "metricName": "COUNT_NULL"
                        },
                        "isMetadataMetric": False,
                        "isTableMetric": False
                    }
                ]
            }
        ]
    }
    globs['smt'] = TableApplicableMetricTypes().from_dict(template)
    globs['tmt'] = TableApplicableMetricTypes().from_dict(template)

    doctest.testmod(globs=globs)
