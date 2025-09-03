from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.collection_cde_stats_item_distrib_item import (
    CollectionCdeStatsItemDistribItem,
)
from ..models.collection_cde_stats_per_cde import CollectionCdeStatsPerCde
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionCdeStats")


@_attrs_define
class CollectionCdeStats:
    """CollectionCdeStats model

    Attributes:
        per_cde (CollectionCdeStatsPerCde): A map of each CDE url in the requested CDE set to the
            number of items that contain that CDE.
        item_distrib (Union[Unset, List['CollectionCdeStatsItemDistribItem']]): Represents the number of items that have
            a given number of
            CDEs out of the requested set.
    """

    per_cde: "CollectionCdeStatsPerCde"
    item_distrib: Union[Unset, List["CollectionCdeStatsItemDistribItem"]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        per_cde = self.per_cde.to_dict()
        item_distrib: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.item_distrib, Unset):
            item_distrib = []
            for item_distrib_item_data in self.item_distrib:
                item_distrib_item = item_distrib_item_data.to_dict()
                item_distrib.append(item_distrib_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "perCde": per_cde,
            }
        )
        if item_distrib is not UNSET:
            field_dict["itemDistrib"] = item_distrib

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionCdeStats` from a dict"""
        d = src_dict.copy()
        per_cde = CollectionCdeStatsPerCde.from_dict(d.pop("perCde"))

        item_distrib = []
        _item_distrib = d.pop("itemDistrib", UNSET)
        for item_distrib_item_data in _item_distrib or []:
            item_distrib_item = CollectionCdeStatsItemDistribItem.from_dict(
                item_distrib_item_data
            )

            item_distrib.append(item_distrib_item)

        collection_cde_stats = cls(
            per_cde=per_cde,
            item_distrib=item_distrib,
        )

        return collection_cde_stats
