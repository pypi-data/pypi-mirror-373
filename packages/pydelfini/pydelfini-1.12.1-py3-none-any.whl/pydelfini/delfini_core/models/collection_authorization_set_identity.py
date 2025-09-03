from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.authorized_actions_item import AuthorizedActionsItem
from ..models.collection_authorization_set_identity_action import (
    CollectionAuthorizationSetIdentityAction,
)
from ..models.collection_role import CollectionRole
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionAuthorizationSetIdentity")


@_attrs_define
class CollectionAuthorizationSetIdentity:
    """CollectionAuthorizationSetIdentity model

    Attributes:
        action (CollectionAuthorizationSetIdentityAction):
        identity (str):
        actions (Union[Unset, List[AuthorizedActionsItem]]):
        role (Union[Unset, CollectionRole]):
    """

    action: CollectionAuthorizationSetIdentityAction
    identity: str
    actions: Union[Unset, List[AuthorizedActionsItem]] = UNSET
    role: Union[Unset, CollectionRole] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        action = self.action.value
        identity = self.identity
        actions: Union[Unset, List[str]] = UNSET
        if not isinstance(self.actions, Unset):
            actions = []
            for componentsschemasauthorized_actions_item_data in self.actions:
                componentsschemasauthorized_actions_item = (
                    componentsschemasauthorized_actions_item_data.value
                )
                actions.append(componentsschemasauthorized_actions_item)

        role: Union[Unset, str] = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "action": action,
                "identity": identity,
            }
        )
        if actions is not UNSET:
            field_dict["actions"] = actions
        if role is not UNSET:
            field_dict["role"] = role

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionAuthorizationSetIdentity` from a dict"""
        d = src_dict.copy()
        action = CollectionAuthorizationSetIdentityAction(d.pop("action"))

        identity = d.pop("identity")

        actions = []
        _actions = d.pop("actions", UNSET)
        for componentsschemasauthorized_actions_item_data in _actions or []:
            componentsschemasauthorized_actions_item = AuthorizedActionsItem(
                componentsschemasauthorized_actions_item_data
            )

            actions.append(componentsschemasauthorized_actions_item)

        _role = d.pop("role", UNSET)
        role: Union[Unset, CollectionRole]
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = CollectionRole(_role)

        collection_authorization_set_identity = cls(
            action=action,
            identity=identity,
            actions=actions,
            role=role,
        )

        return collection_authorization_set_identity
