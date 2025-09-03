from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.new_project_metadata import NewProjectMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="NewProject")


@_attrs_define
class NewProject:
    """NewProject model

    Attributes:
        account_id (str):
        description (str):
        name (str):
        metadata (Union[Unset, NewProjectMetadata]):
    """

    account_id: str
    description: str
    name: str
    metadata: Union[Unset, "NewProjectMetadata"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account_id = self.account_id
        description = self.description
        name = self.name
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "account_id": account_id,
                "description": description,
                "name": name,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`NewProject` from a dict"""
        d = src_dict.copy()
        account_id = d.pop("account_id")

        description = d.pop("description")

        name = d.pop("name")

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, NewProjectMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = NewProjectMetadata.from_dict(_metadata)

        new_project = cls(
            account_id=account_id,
            description=description,
            name=name,
            metadata=metadata,
        )

        return new_project
