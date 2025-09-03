from __future__ import annotations

import json
from dataclasses import dataclass

from bigeye_sdk.generated.com.bigeye.models.generated import Collection, MetricInfoList


@dataclass
class CollectionMetrics:
    """TODO: move to proto?  Reusing Message because it has nice features for converting json camel -> snake."""
    collection: Collection
    metrics: MetricInfoList

    def as_dict(self) -> dict:
        return {"collection": self.collection.to_dict(), "metrics": self.metrics.to_dict()}

    @classmethod
    def from_json(cls, sla_metrics_json: str) -> CollectionMetrics:
        d = json.loads(sla_metrics_json)
        r = CollectionMetrics(collection=Collection().from_dict(d['collection']), metrics=MetricInfoList().from_dict(d['metrics']))
        return r

