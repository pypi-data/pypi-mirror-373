from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.account_create_account_body_metadata import (
    AccountCreateAccountBodyMetadata,
)
from ..models.visibility_level import VisibilityLevel
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="AccountCreateAccountBody")


@_attrs_define
class AccountCreateAccountBody:
    """AccountCreateAccountBody model

    Attributes:
        metadata (AccountCreateAccountBodyMetadata):
        name (str):
        visibility_level (Union[Unset, VisibilityLevel]):
    """

    metadata: "AccountCreateAccountBodyMetadata"
    name: str
    visibility_level: Union[Unset, VisibilityLevel] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        metadata = self.metadata.to_dict()
        name = self.name
        visibility_level: Union[Unset, str] = UNSET
        if not isinstance(self.visibility_level, Unset):
            visibility_level = self.visibility_level.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "metadata": metadata,
                "name": name,
            }
        )
        if visibility_level is not UNSET:
            field_dict["visibilityLevel"] = visibility_level

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`AccountCreateAccountBody` from a dict"""
        d = src_dict.copy()
        metadata = AccountCreateAccountBodyMetadata.from_dict(d.pop("metadata"))

        name = d.pop("name")

        _visibility_level = d.pop("visibilityLevel", UNSET)
        visibility_level: Union[Unset, VisibilityLevel]
        if isinstance(_visibility_level, Unset):
            visibility_level = UNSET
        else:
            visibility_level = VisibilityLevel(_visibility_level)

        account_create_account_body = cls(
            metadata=metadata,
            name=name,
            visibility_level=visibility_level,
        )

        return account_create_account_body
