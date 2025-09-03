from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="CollectionsDictionariesCopyToCdesetBody")


@_attrs_define
class CollectionsDictionariesCopyToCdesetBody:
    """CollectionsDictionariesCopyToCdesetBody model

    Attributes:
        description (str):
        name (str):
    """

    description: str
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "description": description,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsDictionariesCopyToCdesetBody` from a dict"""
        d = src_dict.copy()
        description = d.pop("description")

        name = d.pop("name")

        collections_dictionaries_copy_to_cdeset_body = cls(
            description=description,
            name=name,
        )

        return collections_dictionaries_copy_to_cdeset_body
