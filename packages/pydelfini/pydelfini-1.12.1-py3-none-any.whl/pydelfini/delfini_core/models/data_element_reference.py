from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="DataElementReference")


@_attrs_define
class DataElementReference:
    """URL-based reference to a Delfini Data Element

    Attributes:
        ref (str):
        id (str):
        url (str):
        version (str):
    """

    ref: str
    id: str
    url: str
    version: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        ref = self.ref
        id = self.id
        url = self.url
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "$ref": ref,
                "id": id,
                "url": url,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementReference` from a dict"""
        d = src_dict.copy()
        ref = d.pop("$ref")

        id = d.pop("id")

        url = d.pop("url")

        version = d.pop("version")

        data_element_reference = cls(
            ref=ref,
            id=id,
            url=url,
            version=version,
        )

        return data_element_reference
