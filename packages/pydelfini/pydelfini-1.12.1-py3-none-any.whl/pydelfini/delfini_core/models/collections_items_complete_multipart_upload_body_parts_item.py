from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="CollectionsItemsCompleteMultipartUploadBodyPartsItem")


@_attrs_define
class CollectionsItemsCompleteMultipartUploadBodyPartsItem:
    """CollectionsItemsCompleteMultipartUploadBodyPartsItem model

    Attributes:
        e_tag (str):
        part_number (int):
    """

    e_tag: str
    part_number: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        e_tag = self.e_tag
        part_number = self.part_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "ETag": e_tag,
                "PartNumber": part_number,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsItemsCompleteMultipartUploadBodyPartsItem` from a dict"""
        d = src_dict.copy()
        e_tag = d.pop("ETag")

        part_number = d.pop("PartNumber")

        collections_items_complete_multipart_upload_body_parts_item = cls(
            e_tag=e_tag,
            part_number=part_number,
        )

        return collections_items_complete_multipart_upload_body_parts_item
