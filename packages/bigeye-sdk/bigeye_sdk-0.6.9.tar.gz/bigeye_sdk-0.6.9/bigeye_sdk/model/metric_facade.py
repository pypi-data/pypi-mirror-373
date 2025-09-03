from __future__ import annotations

import inspect
import uuid
from dataclasses import field
from typing import List, Union

from pydantic.v1.dataclasses import dataclass

from bigeye_sdk.exceptions.exceptions import InvalidConfigurationException
from bigeye_sdk.functions.metric_functions import get_seconds_from_window_size, get_thresholds_for_metric, \
    is_freshness_metric, get_notification_channels, enforce_lookback_type_defaults, get_grain_seconds, \
    merge_existing_metric_conf, get_freshness_metric_name_for_field, notification_channels_to_simple_str
from bigeye_sdk.functions.table_functions import table_has_metric_time
from bigeye_sdk.generated.com.bigeye.models.generated import Table, MetricConfiguration, TimeInterval, \
    TimeIntervalType, MetricParameter, MetricType, Threshold
from bigeye_sdk.model.base_datawatch_facade import log, DatawatchFacade
from bigeye_sdk.model.protobuf_enum_facade import SimpleMetricCategory
from bigeye_sdk.serializable import YamlSerializable


@dataclass
class SimplePredefinedMetricTemplate(YamlSerializable):
    """
    Provides a simple, reusable, string based metric template for versioning and upserting metrics.  Includes
    methods to convert to and from protobuf CreateMetricRequest objects and fills in reasonable defaults.
    Uses include storing a metric definition once and reusing it multiple times.

    Attributes:
        metric_name:system metric name (name of the predefined metric or the name of the template)  ** The only required attribute. **
        notifications: List of notification channels.  Slack format: @channel or #channel.  Email format: some_user@some_company.com
        thresholds:
        filters:
        group_by:
        user_defined_metric_name: user defined name of metric.  Defaults to system metric name.
        description: the user provided description
        metric_type: SimpleMetricType: Predefined or Template
        default_check_frequency_hours:
        update_schedule: cron schedule.
        delay_at_update:
        timezone:
        should_backfill:
        lookback_type:
        lookback_days:
        window_size:

    Example:
        Define a basic predefined metric:
            metric_name: SUM

        Define more complex metric:
            metric_name: COUNT_NULL
            notifications:
                - bill_stains@cowboy_in_the_coupe_deville.com
                - #obscure_music_references
            thresholds:
                - Constant:
                    upper_bound: 10
                    lower_bound: 2
            filters:
                - 42='the meaning of life'
            group_by:
                - that_other_column
            widnow_size: '1 hour'
    """
    metric_name: str = ""
    notifications: List[str] = field(default_factory=lambda: [])
    thresholds: List[dict] = field(default_factory=lambda: [])
    filters: List[str] = field(default_factory=lambda: [])
    group_by: List[str] = field(default_factory=lambda: [])
    user_defined_metric_name: str = None
    description: str = ""
    metric_type: SimpleMetricCategory = SimpleMetricCategory.PREDEFINED  # the actual metric type
    default_check_frequency_hours: int = 2
    update_schedule: str = None
    delay_at_update: str = "0 minutes"
    timezone: str = "UTC"
    should_backfill: bool = False
    lookback_type: str = None
    lookback_days: int = 2
    window_size: str = "1 day"
    _window_size_seconds = get_seconds_from_window_size(window_size)

    def __post_init__(self):
        if self.user_defined_metric_name is None:
            # Default the user_defined_metric_name to the system metric name.
            self.user_defined_metric_name = self.metric_name

    @classmethod
    def _from_datawatch_object(cls, mc: MetricConfiguration) -> SimplePredefinedMetricTemplate:
        builder = SimplePredefinedMetricTemplate(metric_name=SimpleMetricCategory.get_metric_name(mc.metric_type))
        builder.user_defined_metric_name = mc.name
        builder.description = mc.description
        builder.metric_type = SimpleMetricCategory.get_simple_metric_category(mc.metric_type)
        builder.notifications = notification_channels_to_simple_str(mc.notification_channels)
        builder.thresholds = mc.thresholds
        builder.filters = mc.filters
        builder.group_by = mc.group_bys
        builder.default_check_frequency_hours = mc.schedule_frequency.interval_value
        builder.update_schedule = None
        # TODO finish and test.

        return builder

    def _to_datawatch_object(self,
                             target_table: Table,
                             column_name: str,
                             existing_metric: MetricConfiguration = None) -> MetricConfiguration:
        """
        Converts a SimplePredefinedMetricTemplate to a MetricConfiguration that can be used to upsert a metric to Bigeye API.
        Must include either a column name or an existing metric

        TODO: Break out any remaining logic and unit test.  Currently the table dict makes this harder to test.

        :param target_table: The table object to which the metric will be deployed
        :param column_name: The column name to which the metric will be deployed.
        :param existing_metric: (Optional) Pass the existing MetricConfiguration if updating
        :return:
        """

        new_metric = MetricConfiguration()
        new_metric.name = self.user_defined_metric_name
        new_metric.description = self.description
        new_metric.schedule_frequency = TimeInterval(
            interval_type=TimeIntervalType.HOURS_TIME_INTERVAL_TYPE,
            interval_value=self.default_check_frequency_hours
        )

        new_metric.thresholds = get_thresholds_for_metric(self.metric_name, self.timezone, self.delay_at_update,
                                                          self.update_schedule, self.thresholds)

        new_metric.warehouse_id = target_table.warehouse_id

        new_metric.dataset_id = target_table.id

        metric_time_exists = table_has_metric_time(target_table)

        ifm = is_freshness_metric(self.metric_name)

        new_metric.metric_type = self._enforce_metric_type_constraints(ifm, target_table, column_name)

        new_metric.parameters = [MetricParameter(key="arg1", column_name=column_name)]

        new_metric.notification_channels = get_notification_channels(self.notifications)

        new_metric.filters = self.filters

        new_metric.group_bys = self.group_by

        new_metric.lookback_type = enforce_lookback_type_defaults(predefined_metric_name=self.metric_name,
                                                                  lookback_type=self.lookback_type,
                                                                  metric_time_exists=metric_time_exists
                                                                  )

        new_metric.lookback = TimeInterval(interval_type=TimeIntervalType.DAYS_TIME_INTERVAL_TYPE,
                                           interval_value=self.lookback_days)

        new_metric.grain_seconds = get_grain_seconds(lookback_type=new_metric.lookback_type,
                                                     window_size_seconds=self._window_size_seconds)

        merged = merge_existing_metric_conf(new_metric=new_metric, is_freshness_metric=ifm,
                                            metric_time_exists=metric_time_exists, existing_metric=existing_metric)

        log.debug(merged.to_json())

        return merged

    def _enforce_metric_type_constraints(self,
                                         freshness_metric: bool,
                                         target_table: Table,
                                         column_name: str) -> MetricType:
        """ Enforces constraints for metric types including freshness metrics. """
        if freshness_metric:
            # Enforce correct metric name for field type.
            new_metric_type = get_freshness_metric_name_for_field(target_table, column_name)
            if self.update_schedule is None:
                raise Exception("Update schedule can not be null for freshness schedule thresholds")
        else:
            new_metric_type = self.metric_type.factory(self.metric_name)

        return new_metric_type


@dataclass
class SimpleMetricConfiguration(SimplePredefinedMetricTemplate):
    """
    Versionable Metric Configuration.  Wraps SimplePredefinedMetricTemplate to include warehouse_id, schema_name, table_name and
    column_name.
    """
    warehouse_id: int = None
    schema_name: str = None
    table_name: str = None
    column_name: str = None
    metric_template_id: uuid.UUID = None


@dataclass
class SimpleUpsertMetricRequest(SimpleMetricConfiguration):
    """Request object to upsert a simple metrict tempate to a particular table.  Not intended as a
    versionable object.  Use SimpleMetricConfiguration, SimplePredefinedMetricTemplate, TypewiseMetricConfiguration, SlaMetricConfiguraiton,
    and TableMetricConfiguration are more flexable."""

    from_metric: int = None

    def to_datawatch_object(self, target_table: Table,
                            existing_metric: MetricConfiguration = None) -> MetricConfiguration:
        return self._to_datawatch_object(target_table=target_table,
                                         column_name=self.column_name,
                                         existing_metric=existing_metric)
