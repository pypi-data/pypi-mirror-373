from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.account import Account
from ..models.pagination import Pagination


T = TypeVar("T", bound="AccountList")


@_attrs_define
class AccountList:
    """AccountList model

    Attributes:
        accounts (List['Account']):
        pagination (Pagination):
    """

    accounts: List["Account"]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        accounts = []
        for accounts_item_data in self.accounts:
            accounts_item = accounts_item_data.to_dict()
            accounts.append(accounts_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accounts": accounts,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AccountList` from a dict"""
        d = src_dict.copy()
        accounts = []
        _accounts = d.pop("accounts")
        for accounts_item_data in _accounts:
            accounts_item = Account.from_dict(accounts_item_data)

            accounts.append(accounts_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        account_list = cls(
            accounts=accounts,
            pagination=pagination,
        )

        return account_list
