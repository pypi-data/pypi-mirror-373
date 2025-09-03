from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="PrqlModule")


@_attrs_define
class PrqlModule:
    """PrqlModule model

    Attributes:
        module_contents (str):
        name (str):
    """

    module_contents: str
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        module_contents = self.module_contents
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "module_contents": module_contents,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`PrqlModule` from a dict"""
        d = src_dict.copy()
        module_contents = d.pop("module_contents")

        name = d.pop("name")

        prql_module = cls(
            module_contents=module_contents,
            name=name,
        )

        return prql_module
