import datetime
from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.collection_access_level import CollectionAccessLevel
from ..models.collection_metadata import CollectionMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Collection")


@_attrs_define
class Collection:
    """Core collection properties, with IDs

    Attributes:
        access_level (CollectionAccessLevel):
        account_id (str): The account containing this collection
        created_on (datetime.datetime):
        description (str): The collection's full description
        id (str):
        name (str): The collection's short human-readable name
        version_id (str): The collection's version, or LIVE if it is editable
        default_datastore (Union[Unset, str]):
        metadata (Union[Unset, CollectionMetadata]): Arbitrary user-defined metadata, key-value pairs
        project_id (Union[Unset, str]): The project containing this collection, if set
    """

    access_level: CollectionAccessLevel
    account_id: str
    created_on: datetime.datetime
    description: str
    id: str
    name: str
    version_id: str
    default_datastore: Union[Unset, str] = UNSET
    metadata: Union[Unset, "CollectionMetadata"] = UNSET
    project_id: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        access_level = self.access_level.value
        account_id = self.account_id
        created_on = self.created_on.isoformat()
        description = self.description
        id = self.id
        name = self.name
        version_id = self.version_id
        default_datastore = self.default_datastore
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        project_id = self.project_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accessLevel": access_level,
                "account_id": account_id,
                "createdOn": created_on,
                "description": description,
                "id": id,
                "name": name,
                "versionId": version_id,
            }
        )
        if default_datastore is not UNSET:
            field_dict["defaultDatastore"] = default_datastore
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if project_id is not UNSET:
            field_dict["projectId"] = project_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Collection` from a dict"""
        d = src_dict.copy()
        access_level = CollectionAccessLevel(d.pop("accessLevel"))

        account_id = d.pop("account_id")

        created_on = isoparse(d.pop("createdOn"))

        description = d.pop("description")

        id = d.pop("id")

        name = d.pop("name")

        version_id = d.pop("versionId")

        default_datastore = d.pop("defaultDatastore", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CollectionMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CollectionMetadata.from_dict(_metadata)

        project_id = d.pop("projectId", UNSET)

        collection = cls(
            access_level=access_level,
            account_id=account_id,
            created_on=created_on,
            description=description,
            id=id,
            name=name,
            version_id=version_id,
            default_datastore=default_datastore,
            metadata=metadata,
            project_id=project_id,
        )

        return collection
