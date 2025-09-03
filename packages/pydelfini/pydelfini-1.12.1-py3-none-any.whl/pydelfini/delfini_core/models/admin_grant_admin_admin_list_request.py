from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.admin_grants import AdminGrants


T = TypeVar("T", bound="AdminGrantAdminAdminListRequest")


@_attrs_define
class AdminGrantAdminAdminListRequest:
    """AdminGrantAdminAdminListRequest model

    Attributes:
        grants (List['AdminGrants']):
    """

    grants: List["AdminGrants"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        grants = []
        for grants_item_data in self.grants:
            grants_item = grants_item_data.to_dict()
            grants.append(grants_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "grants": grants,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AdminGrantAdminAdminListRequest` from a dict"""
        d = src_dict.copy()
        grants = []
        _grants = d.pop("grants")
        for grants_item_data in _grants:
            grants_item = AdminGrants.from_dict(grants_item_data)

            grants.append(grants_item)

        admin_grant_admin_admin_list_request = cls(
            grants=grants,
        )

        return admin_grant_admin_admin_list_request
