from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.collection_authorization_grant import CollectionAuthorizationGrant


T = TypeVar("T", bound="CollectionAuthorizationPermit")


@_attrs_define
class CollectionAuthorizationPermit:
    """CollectionAuthorizationPermit model"""

    additional_properties: Dict[str, "CollectionAuthorizationGrant"] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""

        field_dict: Dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()
        field_dict.update({})

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionAuthorizationPermit` from a dict"""
        d = src_dict.copy()
        collection_authorization_permit = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = CollectionAuthorizationGrant.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        collection_authorization_permit.additional_properties = additional_properties
        return collection_authorization_permit

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> "CollectionAuthorizationGrant":
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: "CollectionAuthorizationGrant") -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
