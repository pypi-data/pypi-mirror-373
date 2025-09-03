from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Identity")


@_attrs_define
class Identity:
    """Identity model

    Attributes:
        fqda (str):
        primary_id (str):
        user_name (str):
        is_local_user (Union[Unset, bool]):  Default: True.
    """

    fqda: str
    primary_id: str
    user_name: str
    is_local_user: Union[Unset, bool] = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        fqda = self.fqda
        primary_id = self.primary_id
        user_name = self.user_name
        is_local_user = self.is_local_user

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "fqda": fqda,
                "primary_id": primary_id,
                "user_name": user_name,
            }
        )
        if is_local_user is not UNSET:
            field_dict["is_local_user"] = is_local_user

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Identity` from a dict"""
        d = src_dict.copy()
        fqda = d.pop("fqda")

        primary_id = d.pop("primary_id")

        user_name = d.pop("user_name")

        is_local_user = d.pop("is_local_user", UNSET)

        identity = cls(
            fqda=fqda,
            primary_id=primary_id,
            user_name=user_name,
            is_local_user=is_local_user,
        )

        return identity
