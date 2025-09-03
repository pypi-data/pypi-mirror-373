from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Bundle")


@_attrs_define
class Bundle:
    """Bundle model

    Attributes:
        elements (List[str]):
        id (str):
        name (str):
        version (Union[Unset, str]):
    """

    elements: List[str]
    id: str
    name: str
    version: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        elements = self.elements

        id = self.id
        name = self.name
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "elements": elements,
                "id": id,
                "name": name,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Bundle` from a dict"""
        d = src_dict.copy()
        elements = cast(List[str], d.pop("elements"))

        id = d.pop("id")

        name = d.pop("name")

        version = d.pop("version", UNSET)

        bundle = cls(
            elements=elements,
            id=id,
            name=name,
            version=version,
        )

        return bundle
