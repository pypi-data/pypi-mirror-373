from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.pagination import Pagination
from ..models.user import User


T = TypeVar("T", bound="UserGetUsersResponse200")


@_attrs_define
class UserGetUsersResponse200:
    """UserGetUsersResponse200 model

    Attributes:
        pagination (Pagination):
        users (List['User']):
    """

    pagination: "Pagination"
    users: List["User"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        pagination = self.pagination.to_dict()
        users = []
        for users_item_data in self.users:
            users_item = users_item_data.to_dict()
            users.append(users_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "pagination": pagination,
                "users": users,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`UserGetUsersResponse200` from a dict"""
        d = src_dict.copy()
        pagination = Pagination.from_dict(d.pop("pagination"))

        users = []
        _users = d.pop("users")
        for users_item_data in _users:
            users_item = User.from_dict(users_item_data)

            users.append(users_item)

        user_get_users_response_200 = cls(
            pagination=pagination,
            users=users,
        )

        return user_get_users_response_200
