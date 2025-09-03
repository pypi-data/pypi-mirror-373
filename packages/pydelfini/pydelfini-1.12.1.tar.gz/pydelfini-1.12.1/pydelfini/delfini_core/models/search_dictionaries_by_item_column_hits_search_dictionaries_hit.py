from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.data_element import DataElement
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SearchDictionariesByItemColumnHitsSearchDictionariesHit")


@_attrs_define
class SearchDictionariesByItemColumnHitsSearchDictionariesHit:
    """SearchDictionariesByItemColumnHitsSearchDictionariesHit model

    Attributes:
        element (DataElement): Delfini Data Element
        rank (float):
        validates (Union[Unset, bool]):
    """

    element: "DataElement"
    rank: float
    validates: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        element = self.element.to_dict()
        rank = self.rank
        validates = self.validates

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "element": element,
                "rank": rank,
            }
        )
        if validates is not UNSET:
            field_dict["validates"] = validates

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchDictionariesByItemColumnHitsSearchDictionariesHit` from a dict"""
        d = src_dict.copy()
        element = DataElement.from_dict(d.pop("element"))

        rank = d.pop("rank")

        validates = d.pop("validates", UNSET)

        search_dictionaries_by_item_column_hits_search_dictionaries_hit = cls(
            element=element,
            rank=rank,
            validates=validates,
        )

        return search_dictionaries_by_item_column_hits_search_dictionaries_hit
