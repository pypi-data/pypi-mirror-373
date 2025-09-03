from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.authorized_actions_item import AuthorizedActionsItem
from ..models.collection_role import CollectionRole
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionAuthorizationGrant")


@_attrs_define
class CollectionAuthorizationGrant:
    """CollectionAuthorizationGrant model

    Attributes:
        actions (List[AuthorizedActionsItem]):
        role (Union[Unset, CollectionRole]):
    """

    actions: List[AuthorizedActionsItem]
    role: Union[Unset, CollectionRole] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
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
                "actions": actions,
            }
        )
        if role is not UNSET:
            field_dict["role"] = role

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionAuthorizationGrant` from a dict"""
        d = src_dict.copy()
        actions = []
        _actions = d.pop("actions")
        for componentsschemasauthorized_actions_item_data in _actions:
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

        collection_authorization_grant = cls(
            actions=actions,
            role=role,
        )

        return collection_authorization_grant
