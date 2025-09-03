import datetime
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.group_metadata import GroupMetadata
from ..models.visibility_level import VisibilityLevel


T = TypeVar("T", bound="Group")


@_attrs_define
class Group:
    """Group model

    Attributes:
        account_linked (bool):
        controlled_access (bool):
        created_on (datetime.datetime):
        id (str):
        metadata (GroupMetadata):
        name (str):
        visibility_level (VisibilityLevel):
    """

    account_linked: bool
    controlled_access: bool
    created_on: datetime.datetime
    id: str
    metadata: "GroupMetadata"
    name: str
    visibility_level: VisibilityLevel

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account_linked = self.account_linked
        controlled_access = self.controlled_access
        created_on = self.created_on.isoformat()
        id = self.id
        metadata = self.metadata.to_dict()
        name = self.name
        visibility_level = self.visibility_level.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accountLinked": account_linked,
                "controlledAccess": controlled_access,
                "createdOn": created_on,
                "id": id,
                "metadata": metadata,
                "name": name,
                "visibilityLevel": visibility_level,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Group` from a dict"""
        d = src_dict.copy()
        account_linked = d.pop("accountLinked")

        controlled_access = d.pop("controlledAccess")

        created_on = isoparse(d.pop("createdOn"))

        id = d.pop("id")

        metadata = GroupMetadata.from_dict(d.pop("metadata"))

        name = d.pop("name")

        visibility_level = VisibilityLevel(d.pop("visibilityLevel"))

        group = cls(
            account_linked=account_linked,
            controlled_access=controlled_access,
            created_on=created_on,
            id=id,
            metadata=metadata,
            name=name,
            visibility_level=visibility_level,
        )

        return group
