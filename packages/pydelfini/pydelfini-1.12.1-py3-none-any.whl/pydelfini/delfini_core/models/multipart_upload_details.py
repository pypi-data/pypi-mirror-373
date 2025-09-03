from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.multipart_upload_details_target_urls import (
    MultipartUploadDetailsTargetUrls,
)


T = TypeVar("T", bound="MultipartUploadDetails")


@_attrs_define
class MultipartUploadDetails:
    """MultipartUploadDetails model

    Attributes:
        target_urls (MultipartUploadDetailsTargetUrls): A mapping of byte ranges ("<start>-<end>", inclusive) to target
            URLs.
        upload_id (str):
        upload_key (str):
        url (str):
    """

    target_urls: "MultipartUploadDetailsTargetUrls"
    upload_id: str
    upload_key: str
    url: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        target_urls = self.target_urls.to_dict()
        upload_id = self.upload_id
        upload_key = self.upload_key
        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "targetUrls": target_urls,
                "uploadId": upload_id,
                "uploadKey": upload_key,
                "url": url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MultipartUploadDetails` from a dict"""
        d = src_dict.copy()
        target_urls = MultipartUploadDetailsTargetUrls.from_dict(d.pop("targetUrls"))

        upload_id = d.pop("uploadId")

        upload_key = d.pop("uploadKey")

        url = d.pop("url")

        multipart_upload_details = cls(
            target_urls=target_urls,
            upload_id=upload_id,
            upload_key=upload_key,
            url=url,
        )

        return multipart_upload_details
