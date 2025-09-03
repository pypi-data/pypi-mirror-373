from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.update_user_metadata import UpdateUserMetadata
from ..models.visibility_level import VisibilityLevel
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="UpdateUser")


@_attrs_define
class UpdateUser:
    """Update properties of the user

    Attributes:
        given_name (Union[Unset, str]):
        last_name (Union[Unset, str]):
        metadata (Union[Unset, UpdateUserMetadata]):
        password (Union[Unset, str]):
        user_email (Union[Unset, str]):
        user_name (Union[Unset, str]):
        visibility_level (Union[Unset, VisibilityLevel]):
    """

    given_name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    metadata: Union[Unset, "UpdateUserMetadata"] = UNSET
    password: Union[Unset, str] = UNSET
    user_email: Union[Unset, str] = UNSET
    user_name: Union[Unset, str] = UNSET
    visibility_level: Union[Unset, VisibilityLevel] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        given_name = self.given_name
        last_name = self.last_name
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        password = self.password
        user_email = self.user_email
        user_name = self.user_name
        visibility_level: Union[Unset, str] = UNSET
        if not isinstance(self.visibility_level, Unset):
            visibility_level = self.visibility_level.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if given_name is not UNSET:
            field_dict["given_name"] = given_name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if password is not UNSET:
            field_dict["password"] = password
        if user_email is not UNSET:
            field_dict["user_email"] = user_email
        if user_name is not UNSET:
            field_dict["user_name"] = user_name
        if visibility_level is not UNSET:
            field_dict["visibility_level"] = visibility_level

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`UpdateUser` from a dict"""
        d = src_dict.copy()
        given_name = d.pop("given_name", UNSET)

        last_name = d.pop("last_name", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, UpdateUserMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = UpdateUserMetadata.from_dict(_metadata)

        password = d.pop("password", UNSET)

        user_email = d.pop("user_email", UNSET)

        user_name = d.pop("user_name", UNSET)

        _visibility_level = d.pop("visibility_level", UNSET)
        visibility_level: Union[Unset, VisibilityLevel]
        if isinstance(_visibility_level, Unset):
            visibility_level = UNSET
        else:
            visibility_level = VisibilityLevel(_visibility_level)

        update_user = cls(
            given_name=given_name,
            last_name=last_name,
            metadata=metadata,
            password=password,
            user_email=user_email,
            user_name=user_name,
            visibility_level=visibility_level,
        )

        return update_user
