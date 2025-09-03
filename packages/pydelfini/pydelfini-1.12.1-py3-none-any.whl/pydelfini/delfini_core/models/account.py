import datetime
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.account_metadata import AccountMetadata
from ..models.visibility_level import VisibilityLevel
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Account")


@_attrs_define
class Account:
    """Account model

    Attributes:
        created_on (datetime.datetime):
        id (str):
        is_personal (bool):
        metadata (AccountMetadata):
        name (str):
        members_group_id (Union[Unset, str]):
        visibility_level (Union[Unset, VisibilityLevel]):
    """

    created_on: datetime.datetime
    id: str
    is_personal: bool
    metadata: "AccountMetadata"
    name: str
    members_group_id: Union[Unset, str] = UNSET
    visibility_level: Union[Unset, VisibilityLevel] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        created_on = self.created_on.isoformat()
        id = self.id
        is_personal = self.is_personal
        metadata = self.metadata.to_dict()
        name = self.name
        members_group_id = self.members_group_id
        visibility_level: Union[Unset, str] = UNSET
        if not isinstance(self.visibility_level, Unset):
            visibility_level = self.visibility_level.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "createdOn": created_on,
                "id": id,
                "isPersonal": is_personal,
                "metadata": metadata,
                "name": name,
            }
        )
        if members_group_id is not UNSET:
            field_dict["membersGroupId"] = members_group_id
        if visibility_level is not UNSET:
            field_dict["visibilityLevel"] = visibility_level

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Account` from a dict"""
        d = src_dict.copy()
        created_on = isoparse(d.pop("createdOn"))

        id = d.pop("id")

        is_personal = d.pop("isPersonal")

        metadata = AccountMetadata.from_dict(d.pop("metadata"))

        name = d.pop("name")

        members_group_id = d.pop("membersGroupId", UNSET)

        _visibility_level = d.pop("visibilityLevel", UNSET)
        visibility_level: Union[Unset, VisibilityLevel]
        if isinstance(_visibility_level, Unset):
            visibility_level = UNSET
        else:
            visibility_level = VisibilityLevel(_visibility_level)

        account = cls(
            created_on=created_on,
            id=id,
            is_personal=is_personal,
            metadata=metadata,
            name=name,
            members_group_id=members_group_id,
            visibility_level=visibility_level,
        )

        return account
