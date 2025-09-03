from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionsItemsInitiateMultipartUploadBody")


@_attrs_define
class CollectionsItemsInitiateMultipartUploadBody:
    """CollectionsItemsInitiateMultipartUploadBody model

    Attributes:
        size (int):
        datastore (Union[Unset, str]):  Default: 'delfini+datastore://default'.
        num_parts (Union[Unset, int]):
    """

    size: int
    datastore: Union[Unset, str] = "delfini+datastore://default"
    num_parts: Union[Unset, int] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        size = self.size
        datastore = self.datastore
        num_parts = self.num_parts

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "size": size,
            }
        )
        if datastore is not UNSET:
            field_dict["datastore"] = datastore
        if num_parts is not UNSET:
            field_dict["numParts"] = num_parts

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsItemsInitiateMultipartUploadBody` from a dict"""
        d = src_dict.copy()
        size = d.pop("size")

        datastore = d.pop("datastore", UNSET)

        num_parts = d.pop("numParts", UNSET)

        collections_items_initiate_multipart_upload_body = cls(
            size=size,
            datastore=datastore,
            num_parts=num_parts,
        )

        return collections_items_initiate_multipart_upload_body
