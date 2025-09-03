from typing import Any
from typing import cast
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define


T = TypeVar("T", bound="Pagination")


@_attrs_define
class Pagination:
    """Pagination model

    Attributes:
        items_per_page (int):
        next_page_url (Union[None, str]):
        total_items (int):
    """

    items_per_page: int
    next_page_url: Union[None, str]
    total_items: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        items_per_page = self.items_per_page
        next_page_url: Union[None, str]
        next_page_url = self.next_page_url
        total_items = self.total_items

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "items_per_page": items_per_page,
                "next_page_url": next_page_url,
                "total_items": total_items,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Pagination` from a dict"""
        d = src_dict.copy()
        items_per_page = d.pop("items_per_page")

        def _parse_next_page_url(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        next_page_url = _parse_next_page_url(d.pop("next_page_url"))

        total_items = d.pop("total_items")

        pagination = cls(
            items_per_page=items_per_page,
            next_page_url=next_page_url,
            total_items=total_items,
        )

        return pagination
