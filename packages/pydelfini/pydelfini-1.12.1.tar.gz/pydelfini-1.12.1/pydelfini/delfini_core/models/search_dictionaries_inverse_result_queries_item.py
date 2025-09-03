from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SearchDictionariesInverseResultQueriesItem")


@_attrs_define
class SearchDictionariesInverseResultQueriesItem:
    """SearchDictionariesInverseResultQueriesItem model

    Attributes:
        index (int):
        query (str):
        rank (float):
        validates (Union[Unset, bool]):
    """

    index: int
    query: str
    rank: float
    validates: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        index = self.index
        query = self.query
        rank = self.rank
        validates = self.validates

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "index": index,
                "query": query,
                "rank": rank,
            }
        )
        if validates is not UNSET:
            field_dict["validates"] = validates

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchDictionariesInverseResultQueriesItem` from a dict"""
        d = src_dict.copy()
        index = d.pop("index")

        query = d.pop("query")

        rank = d.pop("rank")

        validates = d.pop("validates", UNSET)

        search_dictionaries_inverse_result_queries_item = cls(
            index=index,
            query=query,
            rank=rank,
            validates=validates,
        )

        return search_dictionaries_inverse_result_queries_item
