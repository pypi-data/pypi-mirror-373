from __future__ import annotations

from typing import List, Optional, Any, TypeVar, Union

from pydantic.v1 import Field

from bigeye_sdk.bigconfig_validation.yaml_model_base import (
    YamlModelWithValidatorContext,
)
from bigeye_sdk.exceptions.exceptions import InvalidConfigurationException
from bigeye_sdk.functions.helpers import has_either_ids_or_names
from bigeye_sdk.model.protobuf_message_facade import (
    SimpleNamedSchedule,
    SimpleColumnMapping,
    SimpleColumnPair,
    SimplePredefinedMetric,
    SimpleNotificationChannel,
)
from bigeye_sdk.serializable import File

DELTA_CONFIGURATION_FILE = TypeVar(
    "DELTA_CONFIGURATION_FILE", bound="DeltaConfigurationFile"
)


# TODO: Add deltas to bigconfig
class DeltaConfigurationFile(File):
    pass


class SimpleTargetTableComparison(YamlModelWithValidatorContext):
    target_table_id: Optional[int] = None
    fq_target_table_name: Optional[str] = None
    delta_column_mapping: Optional[List[SimpleColumnMapping]] = Field(
        default_factory=lambda: []
    )
    all_column_metrics: Optional[List[SimplePredefinedMetric]] = Field(
        default_factory=lambda: []
    )
    group_bys: Optional[List[SimpleColumnPair]] = Field(default_factory=lambda: [])
    source_filters: Optional[List[str]] = Field(default_factory=lambda: [])
    target_filters: Optional[List[str]] = Field(default_factory=lambda: [])
    tolerance: Optional[float] = 0.0


# TODO combine this with the rest of the protobuf message facade and create to_datawatch and from_datawatch methods
class SimpleDeltaConfiguration(YamlModelWithValidatorContext):
    """
    The Simple Delta Configuration is a Yaml serializable configuration file used to configure and version deltas in as
    a file.  The CLI and SDK client methods accept Simple Delta Configurations either individually or as lists -- see
    SimpleDeltaConfigurationList.

    Attributes:
        delta_id: The system generated Delta ID
        delta_name: The user configurable name of the delta.
        source_table_id: The system generated source table ID.  Either include the ID or the fully qualified name.
        fq_source_table_name: The fully qualified source table name.  Either include theID or the fully qualified name.
        target_table_id: The system generated source table ID.  Either include the ID or the fully qualified name.
        fq_target_table_name: The fully qualified source table name.  Either include theID or the fully qualified name.
        delta_column_mapping: A column mapping, including list of metrics, conforming to the SimpleColumnMapping class.
        all_column_metrics: A list of metrics that will be applied to all columns in the Delta.
        group_bys: A list of group bys conforming to the SimpleColumnPair class
        source_filters: A list of string filters to apply to the source table.
        target_filters: A list of string filters to apply to the target table.
        cron_schedule: A cron schedule conforming to the SimpleNamedSchedule class.

    """

    delta_name: str
    delta_id: Optional[int] = None
    source_table_id: Optional[int] = None
    fq_source_table_name: Optional[str] = None
    target_table_id: Optional[int] = None
    fq_target_table_name: Optional[str] = None
    delta_column_mapping: Optional[List[SimpleColumnMapping]] = Field(
        default_factory=lambda: []
    )
    all_column_metrics: Optional[List[SimplePredefinedMetric]] = Field(
        default_factory=lambda: []
    )
    group_bys: Optional[List[SimpleColumnPair]] = Field(default_factory=lambda: [])
    source_filters: Optional[List[str]] = Field(default_factory=lambda: [])
    target_filters: Optional[List[str]] = Field(default_factory=lambda: [])
    tolerance: Optional[float] = 0.0
    cron_schedule: SimpleNamedSchedule = None
    notification_channels: Optional[List[SimpleNotificationChannel]] = Field(
        default_factory=lambda: []
    )
    target_table_comparisons: Optional[List[SimpleTargetTableComparison]] = Field(
        default_factory=lambda: []
    )

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.__verify_config()

    def __verify_config(self):
        all_valid = True
        if not self.target_table_comparisons:
            self.target_table_comparisons = [
                SimpleTargetTableComparison(
                    tolerance=self.tolerance,
                    target_table_id=self.target_table_id,
                    fq_target_table_name=self.fq_target_table_name,
                    delta_column_mapping=self.delta_column_mapping,
                    all_column_metrics=self.all_column_metrics,
                    group_bys=self.group_bys,
                    source_filters=self.source_filters,
                    target_filters=self.target_filters,
                )
            ]
        for c in self.target_table_comparisons:
            all_valid = (
                c.target_table_id is not None or c.fq_target_table_name is not None
            )
        if (
            not has_either_ids_or_names(self.source_table_id, self.fq_source_table_name)
            or not all_valid
        ):
            raise InvalidConfigurationException(
                f"Delta name: {self.delta_name} Must include a fully qualified table name or "
                f"id for source and targets."
            )


class SimpleDeltaConfigurationFile(
    DeltaConfigurationFile, type="DELTA_CONFIGURATION_FILE"
):
    deltas: Optional[List[SimpleDeltaConfiguration]] = None
