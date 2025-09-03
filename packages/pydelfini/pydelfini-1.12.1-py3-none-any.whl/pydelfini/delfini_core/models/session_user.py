from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.identity import Identity
from ..models.operations import Operations
from ..models.session_user_metadata import SessionUserMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="SessionUser")


@_attrs_define
class SessionUser:
    """SessionUser model

    Attributes:
        identity (Identity):
        metadata (SessionUserMetadata):
        name (str):
        account_id (Union[Unset, str]):
        email (Union[Unset, str]):
        has_operations (Union[Unset, List[Operations]]):
        image (Union[Unset, str]):
    """

    identity: "Identity"
    metadata: "SessionUserMetadata"
    name: str
    account_id: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    has_operations: Union[Unset, List[Operations]] = UNSET
    image: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        identity = self.identity.to_dict()
        metadata = self.metadata.to_dict()
        name = self.name
        account_id = self.account_id
        email = self.email
        has_operations: Union[Unset, List[str]] = UNSET
        if not isinstance(self.has_operations, Unset):
            has_operations = []
            for has_operations_item_data in self.has_operations:
                has_operations_item = has_operations_item_data.value
                has_operations.append(has_operations_item)

        image = self.image

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "identity": identity,
                "metadata": metadata,
                "name": name,
            }
        )
        if account_id is not UNSET:
            field_dict["account_id"] = account_id
        if email is not UNSET:
            field_dict["email"] = email
        if has_operations is not UNSET:
            field_dict["has_operations"] = has_operations
        if image is not UNSET:
            field_dict["image"] = image

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SessionUser` from a dict"""
        d = src_dict.copy()
        identity = Identity.from_dict(d.pop("identity"))

        metadata = SessionUserMetadata.from_dict(d.pop("metadata"))

        name = d.pop("name")

        account_id = d.pop("account_id", UNSET)

        email = d.pop("email", UNSET)

        has_operations = []
        _has_operations = d.pop("has_operations", UNSET)
        for has_operations_item_data in _has_operations or []:
            has_operations_item = Operations(has_operations_item_data)

            has_operations.append(has_operations_item)

        image = d.pop("image", UNSET)

        session_user = cls(
            identity=identity,
            metadata=metadata,
            name=name,
            account_id=account_id,
            email=email,
            has_operations=has_operations,
            image=image,
        )

        return session_user
