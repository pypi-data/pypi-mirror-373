from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="CollectionCdeStatsItemDistribItem")


@_attrs_define
class CollectionCdeStatsItemDistribItem:
    """CollectionCdeStatsItemDistribItem model

    Attributes:
        having_num_cdes (int):
        num_items (int):
    """

    having_num_cdes: int
    num_items: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        having_num_cdes = self.having_num_cdes
        num_items = self.num_items

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "havingNumCdes": having_num_cdes,
                "numItems": num_items,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionCdeStatsItemDistribItem` from a dict"""
        d = src_dict.copy()
        having_num_cdes = d.pop("havingNumCdes")

        num_items = d.pop("numItems")

        collection_cde_stats_item_distrib_item = cls(
            having_num_cdes=having_num_cdes,
            num_items=num_items,
        )

        return collection_cde_stats_item_distrib_item
