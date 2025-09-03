from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.collection_access_level import CollectionAccessLevel
from ..models.collection_authorization_update_access_level_action import (
    CollectionAuthorizationUpdateAccessLevelAction,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionAuthorizationUpdateAccessLevel")


@_attrs_define
class CollectionAuthorizationUpdateAccessLevel:
    """CollectionAuthorizationUpdateAccessLevel model

    Attributes:
        action (CollectionAuthorizationUpdateAccessLevelAction):
        new_level (CollectionAccessLevel):
        controlled_group (Union[Unset, str]):
    """

    action: CollectionAuthorizationUpdateAccessLevelAction
    new_level: CollectionAccessLevel
    controlled_group: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        action = self.action.value
        new_level = self.new_level.value
        controlled_group = self.controlled_group

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "action": action,
                "newLevel": new_level,
            }
        )
        if controlled_group is not UNSET:
            field_dict["controlledGroup"] = controlled_group

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionAuthorizationUpdateAccessLevel` from a dict"""
        d = src_dict.copy()
        action = CollectionAuthorizationUpdateAccessLevelAction(d.pop("action"))

        new_level = CollectionAccessLevel(d.pop("newLevel"))

        controlled_group = d.pop("controlledGroup", UNSET)

        collection_authorization_update_access_level = cls(
            action=action,
            new_level=new_level,
            controlled_group=controlled_group,
        )

        return collection_authorization_update_access_level
