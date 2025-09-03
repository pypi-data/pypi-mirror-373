from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.federation_address_or_object_type_2 import FederationAddressOrObjectType2
from ..models.federation_collection_page_type import FederationCollectionPageType
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="FederationCollectionPage")


@_attrs_define
class FederationCollectionPage:
    """FederationCollectionPage model

    Attributes:
        current (Union[Unset, str]):
        first (Union[Unset, str]):
        last (Union[Unset, str]):
        next_ (Union[Unset, str]):
        ordered_items (Union[Unset, List[Union['FederationAddressOrObjectType2', List[str], str]]]):
        prev (Union[Unset, str]):
        total_items (Union[Unset, int]):
        type (Union[Unset, FederationCollectionPageType]):
    """

    current: Union[Unset, str] = UNSET
    first: Union[Unset, str] = UNSET
    last: Union[Unset, str] = UNSET
    next_: Union[Unset, str] = UNSET
    ordered_items: Union[
        Unset, List[Union["FederationAddressOrObjectType2", List[str], str]]
    ] = UNSET
    prev: Union[Unset, str] = UNSET
    total_items: Union[Unset, int] = UNSET
    type: Union[Unset, FederationCollectionPageType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        current = self.current
        first = self.first
        last = self.last
        next_ = self.next_
        ordered_items: Union[Unset, List[Union[Dict[str, Any], List[str], str]]] = UNSET
        if not isinstance(self.ordered_items, Unset):
            ordered_items = []
            for ordered_items_item_data in self.ordered_items:
                ordered_items_item: Union[Dict[str, Any], List[str], str]
                if isinstance(ordered_items_item_data, list):
                    ordered_items_item = ordered_items_item_data

                elif isinstance(
                    ordered_items_item_data, FederationAddressOrObjectType2
                ):
                    ordered_items_item = ordered_items_item_data.to_dict()
                else:
                    ordered_items_item = ordered_items_item_data
                ordered_items.append(ordered_items_item)

        prev = self.prev
        total_items = self.total_items
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if current is not UNSET:
            field_dict["current"] = current
        if first is not UNSET:
            field_dict["first"] = first
        if last is not UNSET:
            field_dict["last"] = last
        if next_ is not UNSET:
            field_dict["next"] = next_
        if ordered_items is not UNSET:
            field_dict["orderedItems"] = ordered_items
        if prev is not UNSET:
            field_dict["prev"] = prev
        if total_items is not UNSET:
            field_dict["totalItems"] = total_items
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`FederationCollectionPage` from a dict"""
        d = src_dict.copy()
        current = d.pop("current", UNSET)

        first = d.pop("first", UNSET)

        last = d.pop("last", UNSET)

        next_ = d.pop("next", UNSET)

        ordered_items = []
        _ordered_items = d.pop("orderedItems", UNSET)
        for ordered_items_item_data in _ordered_items or []:

            def _parse_ordered_items_item(
                data: object,
            ) -> Union["FederationAddressOrObjectType2", List[str], str]:
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
                    Union["FederationAddressOrObjectType2", List[str], str], data
                )

            ordered_items_item = _parse_ordered_items_item(ordered_items_item_data)

            ordered_items.append(ordered_items_item)

        prev = d.pop("prev", UNSET)

        total_items = d.pop("totalItems", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, FederationCollectionPageType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = FederationCollectionPageType(_type)

        federation_collection_page = cls(
            current=current,
            first=first,
            last=last,
            next_=next_,
            ordered_items=ordered_items,
            prev=prev,
            total_items=total_items,
            type=type,
        )

        federation_collection_page.additional_properties = d
        return federation_collection_page

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
