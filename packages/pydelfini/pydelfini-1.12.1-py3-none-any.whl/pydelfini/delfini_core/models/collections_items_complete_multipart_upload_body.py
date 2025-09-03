from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.collections_items_complete_multipart_upload_body_action import (
    CollectionsItemsCompleteMultipartUploadBodyAction,
)
from ..models.collections_items_complete_multipart_upload_body_checksum import (
    CollectionsItemsCompleteMultipartUploadBodyChecksum,
)
from ..models.collections_items_complete_multipart_upload_body_parts_item import (
    CollectionsItemsCompleteMultipartUploadBodyPartsItem,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionsItemsCompleteMultipartUploadBody")


@_attrs_define
class CollectionsItemsCompleteMultipartUploadBody:
    """CollectionsItemsCompleteMultipartUploadBody model

    Attributes:
        parts (List['CollectionsItemsCompleteMultipartUploadBodyPartsItem']):
        upload_id (str):
        upload_key (str):
        url (str):
        action (Union[Unset, CollectionsItemsCompleteMultipartUploadBodyAction]):
        checksum (Union[Unset, CollectionsItemsCompleteMultipartUploadBodyChecksum]):
    """

    parts: List["CollectionsItemsCompleteMultipartUploadBodyPartsItem"]
    upload_id: str
    upload_key: str
    url: str
    action: Union[Unset, CollectionsItemsCompleteMultipartUploadBodyAction] = UNSET
    checksum: Union[
        Unset, "CollectionsItemsCompleteMultipartUploadBodyChecksum"
    ] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        parts = []
        for parts_item_data in self.parts:
            parts_item = parts_item_data.to_dict()
            parts.append(parts_item)

        upload_id = self.upload_id
        upload_key = self.upload_key
        url = self.url
        action: Union[Unset, str] = UNSET
        if not isinstance(self.action, Unset):
            action = self.action.value

        checksum: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.checksum, Unset):
            checksum = self.checksum.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "parts": parts,
                "uploadId": upload_id,
                "uploadKey": upload_key,
                "url": url,
            }
        )
        if action is not UNSET:
            field_dict["action"] = action
        if checksum is not UNSET:
            field_dict["checksum"] = checksum

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsItemsCompleteMultipartUploadBody` from a dict"""
        d = src_dict.copy()
        parts = []
        _parts = d.pop("parts")
        for parts_item_data in _parts:
            parts_item = CollectionsItemsCompleteMultipartUploadBodyPartsItem.from_dict(
                parts_item_data
            )

            parts.append(parts_item)

        upload_id = d.pop("uploadId")

        upload_key = d.pop("uploadKey")

        url = d.pop("url")

        _action = d.pop("action", UNSET)
        action: Union[Unset, CollectionsItemsCompleteMultipartUploadBodyAction]
        if isinstance(_action, Unset):
            action = UNSET
        else:
            action = CollectionsItemsCompleteMultipartUploadBodyAction(_action)

        _checksum = d.pop("checksum", UNSET)
        checksum: Union[Unset, CollectionsItemsCompleteMultipartUploadBodyChecksum]
        if isinstance(_checksum, Unset):
            checksum = UNSET
        else:
            checksum = CollectionsItemsCompleteMultipartUploadBodyChecksum.from_dict(
                _checksum
            )

        collections_items_complete_multipart_upload_body = cls(
            parts=parts,
            upload_id=upload_id,
            upload_key=upload_key,
            url=url,
            action=action,
            checksum=checksum,
        )

        return collections_items_complete_multipart_upload_body
