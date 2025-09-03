from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.datastore_type import DatastoreType


T = TypeVar("T", bound="Datastore")


@_attrs_define
class Datastore:
    """Public view on a datastore

    Attributes:
        enabled (bool):
        name (str):
        num_objects (int):
        size_bytes (int):
        type (DatastoreType):
        url (str):
    """

    enabled: bool
    name: str
    num_objects: int
    size_bytes: int
    type: DatastoreType
    url: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        enabled = self.enabled
        name = self.name
        num_objects = self.num_objects
        size_bytes = self.size_bytes
        type = self.type.value
        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "enabled": enabled,
                "name": name,
                "num_objects": num_objects,
                "size_bytes": size_bytes,
                "type": type,
                "url": url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Datastore` from a dict"""
        d = src_dict.copy()
        enabled = d.pop("enabled")

        name = d.pop("name")

        num_objects = d.pop("num_objects")

        size_bytes = d.pop("size_bytes")

        type = DatastoreType(d.pop("type"))

        url = d.pop("url")

        datastore = cls(
            enabled=enabled,
            name=name,
            num_objects=num_objects,
            size_bytes=size_bytes,
            type=type,
            url=url,
        )

        return datastore
