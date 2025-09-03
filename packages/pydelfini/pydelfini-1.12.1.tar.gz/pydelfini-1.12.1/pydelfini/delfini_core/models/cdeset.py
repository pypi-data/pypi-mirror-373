from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="Cdeset")


@_attrs_define
class Cdeset:
    """Cdeset model

    Attributes:
        description (str):
        name (str):
        num_cdes (int):
    """

    description: str
    name: str
    num_cdes: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        name = self.name
        num_cdes = self.num_cdes

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "description": description,
                "name": name,
                "num_cdes": num_cdes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Cdeset` from a dict"""
        d = src_dict.copy()
        description = d.pop("description")

        name = d.pop("name")

        num_cdes = d.pop("num_cdes")

        cdeset = cls(
            description=description,
            name=name,
            num_cdes=num_cdes,
        )

        return cdeset
