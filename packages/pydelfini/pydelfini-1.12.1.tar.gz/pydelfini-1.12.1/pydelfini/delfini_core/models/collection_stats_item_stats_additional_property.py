from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.collection_stats_item_stats_additional_property_num_failed import (
    CollectionStatsItemStatsAdditionalPropertyNumFailed,
)


T = TypeVar("T", bound="CollectionStatsItemStatsAdditionalProperty")


@_attrs_define
class CollectionStatsItemStatsAdditionalProperty:
    """CollectionStatsItemStatsAdditionalProperty model

    Attributes:
        num_failed (CollectionStatsItemStatsAdditionalPropertyNumFailed):
        num_full_data_elements (int):
        num_items (int):
        num_partial_data_elements (int):
        num_tabular (int):
        size_bytes (int):
    """

    num_failed: "CollectionStatsItemStatsAdditionalPropertyNumFailed"
    num_full_data_elements: int
    num_items: int
    num_partial_data_elements: int
    num_tabular: int
    size_bytes: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        num_failed = self.num_failed.to_dict()
        num_full_data_elements = self.num_full_data_elements
        num_items = self.num_items
        num_partial_data_elements = self.num_partial_data_elements
        num_tabular = self.num_tabular
        size_bytes = self.size_bytes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "numFailed": num_failed,
                "numFullDataElements": num_full_data_elements,
                "numItems": num_items,
                "numPartialDataElements": num_partial_data_elements,
                "numTabular": num_tabular,
                "sizeBytes": size_bytes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionStatsItemStatsAdditionalProperty` from a dict"""
        d = src_dict.copy()
        num_failed = CollectionStatsItemStatsAdditionalPropertyNumFailed.from_dict(
            d.pop("numFailed")
        )

        num_full_data_elements = d.pop("numFullDataElements")

        num_items = d.pop("numItems")

        num_partial_data_elements = d.pop("numPartialDataElements")

        num_tabular = d.pop("numTabular")

        size_bytes = d.pop("sizeBytes")

        collection_stats_item_stats_additional_property = cls(
            num_failed=num_failed,
            num_full_data_elements=num_full_data_elements,
            num_items=num_items,
            num_partial_data_elements=num_partial_data_elements,
            num_tabular=num_tabular,
            size_bytes=size_bytes,
        )

        return collection_stats_item_stats_additional_property
