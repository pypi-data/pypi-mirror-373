from dataclasses import dataclass

from bigeye_sdk.generated.com.bigeye.models.generated import GetDebugQueriesResponse


@dataclass
class MetricDebugQueries:
    metric_id: int
    debug_queries: GetDebugQueriesResponse
