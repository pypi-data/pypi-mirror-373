from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="MetricEvent")


@_attrs_define
class MetricEvent:
    """MetricEvent model

    Attributes:
        description (str):
        dimensions (List[str]):
        name (str):
        value_units (str):
    """

    description: str
    dimensions: List[str]
    name: str
    value_units: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        dimensions = self.dimensions

        name = self.name
        value_units = self.value_units

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "description": description,
                "dimensions": dimensions,
                "name": name,
                "value_units": value_units,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetricEvent` from a dict"""
        d = src_dict.copy()
        description = d.pop("description")

        dimensions = cast(List[str], d.pop("dimensions"))

        name = d.pop("name")

        value_units = d.pop("value_units")

        metric_event = cls(
            description=description,
            dimensions=dimensions,
            name=name,
            value_units=value_units,
        )

        return metric_event
