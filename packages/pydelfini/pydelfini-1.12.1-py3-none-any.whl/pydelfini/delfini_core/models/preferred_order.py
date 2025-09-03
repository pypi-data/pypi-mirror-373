from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="PreferredOrder")


@_attrs_define
class PreferredOrder:
    """PreferredOrder model

    Attributes:
        order (List[str]):
    """

    order: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        order = self.order

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "order": order,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`PreferredOrder` from a dict"""
        d = src_dict.copy()
        order = cast(List[str], d.pop("order"))

        preferred_order = cls(
            order=order,
        )

        return preferred_order
