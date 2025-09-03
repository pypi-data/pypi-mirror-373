import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="FederationAddressOrObjectType2")


@_attrs_define
class FederationAddressOrObjectType2:
    """FederationAddressOrObjectType2 model

    Attributes:
        content (Union[Unset, str]):
        name (Union[Unset, str]):
        published (Union[Unset, datetime.datetime]):
        type (Union[Unset, str]):
    """

    content: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    published: Union[Unset, datetime.datetime] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        content = self.content
        name = self.name
        published: Union[Unset, str] = UNSET
        if not isinstance(self.published, Unset):
            published = self.published.isoformat()
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content is not UNSET:
            field_dict["content"] = content
        if name is not UNSET:
            field_dict["name"] = name
        if published is not UNSET:
            field_dict["published"] = published
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`FederationAddressOrObjectType2` from a dict"""
        d = src_dict.copy()
        content = d.pop("content", UNSET)

        name = d.pop("name", UNSET)

        _published = d.pop("published", UNSET)
        published: Union[Unset, datetime.datetime]
        if isinstance(_published, Unset):
            published = UNSET
        else:
            published = isoparse(_published)

        type = d.pop("type", UNSET)

        federation_address_or_object_type_2 = cls(
            content=content,
            name=name,
            published=published,
            type=type,
        )

        federation_address_or_object_type_2.additional_properties = d
        return federation_address_or_object_type_2

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
