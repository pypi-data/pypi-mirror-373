import datetime
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.federation_address_or_object_type_2 import FederationAddressOrObjectType2
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="FederationActivity")


@_attrs_define
class FederationActivity:
    """FederationActivity model

    Attributes:
        actor (Union['FederationAddressOrObjectType2', List[str], Unset, str]):
        bcc (Union[List[str], Unset, str]):
        bto (Union[List[str], Unset, str]):
        cc (Union[List[str], Unset, str]):
        content (Union[Unset, str]):
        name (Union[Unset, str]):
        object_ (Union['FederationAddressOrObjectType2', List[str], Unset, str]):
        published (Union[Unset, datetime.datetime]):
        target (Union['FederationAddressOrObjectType2', List[str], Unset, str]):
        to (Union[List[str], Unset, str]):
        type (Union[Unset, str]):
    """

    actor: Union["FederationAddressOrObjectType2", List[str], Unset, str] = UNSET
    bcc: Union[List[str], Unset, str] = UNSET
    bto: Union[List[str], Unset, str] = UNSET
    cc: Union[List[str], Unset, str] = UNSET
    content: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    object_: Union["FederationAddressOrObjectType2", List[str], Unset, str] = UNSET
    published: Union[Unset, datetime.datetime] = UNSET
    target: Union["FederationAddressOrObjectType2", List[str], Unset, str] = UNSET
    to: Union[List[str], Unset, str] = UNSET
    type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        actor: Union[Dict[str, Any], List[str], Unset, str]
        if isinstance(self.actor, Unset):
            actor = UNSET
        elif isinstance(self.actor, list):
            actor = self.actor

        elif isinstance(self.actor, FederationAddressOrObjectType2):
            actor = self.actor.to_dict()
        else:
            actor = self.actor
        bcc: Union[List[str], Unset, str]
        if isinstance(self.bcc, Unset):
            bcc = UNSET
        elif isinstance(self.bcc, list):
            bcc = self.bcc

        else:
            bcc = self.bcc
        bto: Union[List[str], Unset, str]
        if isinstance(self.bto, Unset):
            bto = UNSET
        elif isinstance(self.bto, list):
            bto = self.bto

        else:
            bto = self.bto
        cc: Union[List[str], Unset, str]
        if isinstance(self.cc, Unset):
            cc = UNSET
        elif isinstance(self.cc, list):
            cc = self.cc

        else:
            cc = self.cc
        content = self.content
        name = self.name
        object_: Union[Dict[str, Any], List[str], Unset, str]
        if isinstance(self.object_, Unset):
            object_ = UNSET
        elif isinstance(self.object_, list):
            object_ = self.object_

        elif isinstance(self.object_, FederationAddressOrObjectType2):
            object_ = self.object_.to_dict()
        else:
            object_ = self.object_
        published: Union[Unset, str] = UNSET
        if not isinstance(self.published, Unset):
            published = self.published.isoformat()
        target: Union[Dict[str, Any], List[str], Unset, str]
        if isinstance(self.target, Unset):
            target = UNSET
        elif isinstance(self.target, list):
            target = self.target

        elif isinstance(self.target, FederationAddressOrObjectType2):
            target = self.target.to_dict()
        else:
            target = self.target
        to: Union[List[str], Unset, str]
        if isinstance(self.to, Unset):
            to = UNSET
        elif isinstance(self.to, list):
            to = self.to

        else:
            to = self.to
        type = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actor is not UNSET:
            field_dict["actor"] = actor
        if bcc is not UNSET:
            field_dict["bcc"] = bcc
        if bto is not UNSET:
            field_dict["bto"] = bto
        if cc is not UNSET:
            field_dict["cc"] = cc
        if content is not UNSET:
            field_dict["content"] = content
        if name is not UNSET:
            field_dict["name"] = name
        if object_ is not UNSET:
            field_dict["object"] = object_
        if published is not UNSET:
            field_dict["published"] = published
        if target is not UNSET:
            field_dict["target"] = target
        if to is not UNSET:
            field_dict["to"] = to
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`FederationActivity` from a dict"""
        d = src_dict.copy()

        def _parse_actor(
            data: object,
        ) -> Union["FederationAddressOrObjectType2", List[str], Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemasfederation_address_or_object_type_1 = cast(
                    List[str], data
                )

                return componentsschemasfederation_address_or_object_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasfederation_address_or_object_type_2 = (
                    FederationAddressOrObjectType2.from_dict(data)
                )

                return componentsschemasfederation_address_or_object_type_2
            except:  # noqa: E722
                pass
            return cast(
                Union["FederationAddressOrObjectType2", List[str], Unset, str], data
            )

        actor = _parse_actor(d.pop("actor", UNSET))

        def _parse_bcc(data: object) -> Union[List[str], Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemasfederation_address_type_1 = cast(List[str], data)

                return componentsschemasfederation_address_type_1
            except:  # noqa: E722
                pass
            return cast(Union[List[str], Unset, str], data)

        bcc = _parse_bcc(d.pop("bcc", UNSET))

        def _parse_bto(data: object) -> Union[List[str], Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemasfederation_address_type_1 = cast(List[str], data)

                return componentsschemasfederation_address_type_1
            except:  # noqa: E722
                pass
            return cast(Union[List[str], Unset, str], data)

        bto = _parse_bto(d.pop("bto", UNSET))

        def _parse_cc(data: object) -> Union[List[str], Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemasfederation_address_type_1 = cast(List[str], data)

                return componentsschemasfederation_address_type_1
            except:  # noqa: E722
                pass
            return cast(Union[List[str], Unset, str], data)

        cc = _parse_cc(d.pop("cc", UNSET))

        content = d.pop("content", UNSET)

        name = d.pop("name", UNSET)

        def _parse_object_(
            data: object,
        ) -> Union["FederationAddressOrObjectType2", List[str], Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemasfederation_address_or_object_type_1 = cast(
                    List[str], data
                )

                return componentsschemasfederation_address_or_object_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasfederation_address_or_object_type_2 = (
                    FederationAddressOrObjectType2.from_dict(data)
                )

                return componentsschemasfederation_address_or_object_type_2
            except:  # noqa: E722
                pass
            return cast(
                Union["FederationAddressOrObjectType2", List[str], Unset, str], data
            )

        object_ = _parse_object_(d.pop("object", UNSET))

        _published = d.pop("published", UNSET)
        published: Union[Unset, datetime.datetime]
        if isinstance(_published, Unset):
            published = UNSET
        else:
            published = isoparse(_published)

        def _parse_target(
            data: object,
        ) -> Union["FederationAddressOrObjectType2", List[str], Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemasfederation_address_or_object_type_1 = cast(
                    List[str], data
                )

                return componentsschemasfederation_address_or_object_type_1
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasfederation_address_or_object_type_2 = (
                    FederationAddressOrObjectType2.from_dict(data)
                )

                return componentsschemasfederation_address_or_object_type_2
            except:  # noqa: E722
                pass
            return cast(
                Union["FederationAddressOrObjectType2", List[str], Unset, str], data
            )

        target = _parse_target(d.pop("target", UNSET))

        def _parse_to(data: object) -> Union[List[str], Unset, str]:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemasfederation_address_type_1 = cast(List[str], data)

                return componentsschemasfederation_address_type_1
            except:  # noqa: E722
                pass
            return cast(Union[List[str], Unset, str], data)

        to = _parse_to(d.pop("to", UNSET))

        type = d.pop("type", UNSET)

        federation_activity = cls(
            actor=actor,
            bcc=bcc,
            bto=bto,
            cc=cc,
            content=content,
            name=name,
            object_=object_,
            published=published,
            target=target,
            to=to,
            type=type,
        )

        federation_activity.additional_properties = d
        return federation_activity

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
