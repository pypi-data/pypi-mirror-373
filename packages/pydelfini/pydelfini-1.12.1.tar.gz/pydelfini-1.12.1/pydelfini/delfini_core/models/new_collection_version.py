from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.new_collection_version_metadata import NewCollectionVersionMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="NewCollectionVersion")


@_attrs_define
class NewCollectionVersion:
    """Collection version details

    Attributes:
        description (str): The description of the version
        frozen_release (Union[Unset, bool]): If true, the system will store the current state of all
            link targets and dataviews in the default datastore
             Default: False.
        item_ids (Union[Unset, List[str]]): The items to include in this collection version
        metadata (Union[Unset, NewCollectionVersionMetadata]): Arbitrary user-defined metadata, key-value pairs
    """

    description: str
    frozen_release: Union[Unset, bool] = False
    item_ids: Union[Unset, List[str]] = UNSET
    metadata: Union[Unset, "NewCollectionVersionMetadata"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        frozen_release = self.frozen_release
        item_ids: Union[Unset, List[str]] = UNSET
        if not isinstance(self.item_ids, Unset):
            item_ids = self.item_ids

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "description": description,
            }
        )
        if frozen_release is not UNSET:
            field_dict["frozenRelease"] = frozen_release
        if item_ids is not UNSET:
            field_dict["itemIds"] = item_ids
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`NewCollectionVersion` from a dict"""
        d = src_dict.copy()
        description = d.pop("description")

        frozen_release = d.pop("frozenRelease", UNSET)

        item_ids = cast(List[str], d.pop("itemIds", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, NewCollectionVersionMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = NewCollectionVersionMetadata.from_dict(_metadata)

        new_collection_version = cls(
            description=description,
            frozen_release=frozen_release,
            item_ids=item_ids,
            metadata=metadata,
        )

        return new_collection_version
