import datetime
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.project_metadata import ProjectMetadata


T = TypeVar("T", bound="Project")


@_attrs_define
class Project:
    """Project model

    Attributes:
        account_id (str):
        collections (List[str]):
        created_on (datetime.datetime):
        description (str):
        id (str):
        metadata (ProjectMetadata):
        name (str):
    """

    account_id: str
    collections: List[str]
    created_on: datetime.datetime
    description: str
    id: str
    metadata: "ProjectMetadata"
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account_id = self.account_id
        collections = self.collections

        created_on = self.created_on.isoformat()
        description = self.description
        id = self.id
        metadata = self.metadata.to_dict()
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "account_id": account_id,
                "collections": collections,
                "createdOn": created_on,
                "description": description,
                "id": id,
                "metadata": metadata,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Project` from a dict"""
        d = src_dict.copy()
        account_id = d.pop("account_id")

        collections = cast(List[str], d.pop("collections"))

        created_on = isoparse(d.pop("createdOn"))

        description = d.pop("description")

        id = d.pop("id")

        metadata = ProjectMetadata.from_dict(d.pop("metadata"))

        name = d.pop("name")

        project = cls(
            account_id=account_id,
            collections=collections,
            created_on=created_on,
            description=description,
            id=id,
            metadata=metadata,
            name=name,
        )

        return project
