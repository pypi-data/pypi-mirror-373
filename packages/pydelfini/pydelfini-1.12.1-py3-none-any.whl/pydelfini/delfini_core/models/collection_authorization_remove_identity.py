from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.collection_authorization_remove_identity_action import (
    CollectionAuthorizationRemoveIdentityAction,
)


T = TypeVar("T", bound="CollectionAuthorizationRemoveIdentity")


@_attrs_define
class CollectionAuthorizationRemoveIdentity:
    """CollectionAuthorizationRemoveIdentity model

    Attributes:
        action (CollectionAuthorizationRemoveIdentityAction):
        identity (str):
    """

    action: CollectionAuthorizationRemoveIdentityAction
    identity: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        action = self.action.value
        identity = self.identity

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "action": action,
                "identity": identity,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionAuthorizationRemoveIdentity` from a dict"""
        d = src_dict.copy()
        action = CollectionAuthorizationRemoveIdentityAction(d.pop("action"))

        identity = d.pop("identity")

        collection_authorization_remove_identity = cls(
            action=action,
            identity=identity,
        )

        return collection_authorization_remove_identity
