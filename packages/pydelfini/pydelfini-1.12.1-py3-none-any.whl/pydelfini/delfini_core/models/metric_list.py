from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.event_metric import EventMetric
from ..models.metadata_metric import MetadataMetric


T = TypeVar("T", bound="MetricList")


@_attrs_define
class MetricList:
    """MetricList model

    Attributes:
        metrics (List[Union['EventMetric', 'MetadataMetric']]):
    """

    metrics: List[Union["EventMetric", "MetadataMetric"]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item: Dict[str, Any]
            if isinstance(metrics_item_data, MetadataMetric):
                metrics_item = metrics_item_data.to_dict()
            else:
                metrics_item = metrics_item_data.to_dict()

            metrics.append(metrics_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "metrics": metrics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetricList` from a dict"""
        d = src_dict.copy()
        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:

            def _parse_metrics_item(
                data: object,
            ) -> Union["EventMetric", "MetadataMetric"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemasmetric_type_0 = MetadataMetric.from_dict(data)

                    return componentsschemasmetric_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasmetric_type_1 = EventMetric.from_dict(data)

                return componentsschemasmetric_type_1

            metrics_item = _parse_metrics_item(metrics_item_data)

            metrics.append(metrics_item)

        metric_list = cls(
            metrics=metrics,
        )

        return metric_list
