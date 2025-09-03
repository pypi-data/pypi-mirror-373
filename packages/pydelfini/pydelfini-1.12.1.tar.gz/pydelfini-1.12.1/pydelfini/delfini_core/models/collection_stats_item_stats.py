from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.collection_stats_item_stats_additional_property import (
    CollectionStatsItemStatsAdditionalProperty,
)


T = TypeVar("T", bound="CollectionStatsItemStats")


@_attrs_define
class CollectionStatsItemStats:
    """CollectionStatsItemStats model"""

    additional_properties: Dict[
        str, "CollectionStatsItemStatsAdditionalProperty"
    ] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionStatsItemStats` from a dict"""
        d = src_dict.copy()
        collection_stats_item_stats = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = CollectionStatsItemStatsAdditionalProperty.from_dict(
                prop_dict
            )

            additional_properties[prop_name] = additional_property

        collection_stats_item_stats.additional_properties = additional_properties
        return collection_stats_item_stats

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "CollectionStatsItemStatsAdditionalProperty":
        return self.additional_properties[key]

    def __setitem__(
        self, key: str, value: "CollectionStatsItemStatsAdditionalProperty"
    ) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
