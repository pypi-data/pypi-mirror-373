import datetime
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.collection_stats_item_stats import CollectionStatsItemStats


T = TypeVar("T", bound="CollectionStats")


@_attrs_define
class CollectionStats:
    """CollectionStats model

    Attributes:
        item_stats (CollectionStatsItemStats):
        newest_item_date (datetime.datetime):
        oldest_item_date (datetime.datetime):
    """

    item_stats: "CollectionStatsItemStats"
    newest_item_date: datetime.datetime
    oldest_item_date: datetime.datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        item_stats = self.item_stats.to_dict()
        newest_item_date = self.newest_item_date.isoformat()
        oldest_item_date = self.oldest_item_date.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "itemStats": item_stats,
                "newestItemDate": newest_item_date,
                "oldestItemDate": oldest_item_date,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionStats` from a dict"""
        d = src_dict.copy()
        item_stats = CollectionStatsItemStats.from_dict(d.pop("itemStats"))

        newest_item_date = isoparse(d.pop("newestItemDate"))

        oldest_item_date = isoparse(d.pop("oldestItemDate"))

        collection_stats = cls(
            item_stats=item_stats,
            newest_item_date=newest_item_date,
            oldest_item_date=oldest_item_date,
        )

        return collection_stats
