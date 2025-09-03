from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.item_storage_checksum import ItemStorageChecksum
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="ItemStorage")


@_attrs_define
class ItemStorage:
    """ItemStorage model

    Example:

    >>> model = ItemStorage.from_dict({'checksum': {},
    ...     'size': None,
    ...     'sizeIsEstimate': False,
    ...     'url': 'delfini+datastore://default'})

    Attributes:
        checksum (Union[Unset, ItemStorageChecksum]):
        size (Union[Unset, int]):
        size_is_estimate (Union[Unset, bool]):  Default: False.
        url (Union[Unset, str]):
    """

    checksum: Union[Unset, "ItemStorageChecksum"] = UNSET
    size: Union[Unset, int] = UNSET
    size_is_estimate: Union[Unset, bool] = False
    url: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        checksum: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.checksum, Unset):
            checksum = self.checksum.to_dict()
        size = self.size
        size_is_estimate = self.size_is_estimate
        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if checksum is not UNSET:
            field_dict["checksum"] = checksum
        if size is not UNSET:
            field_dict["size"] = size
        if size_is_estimate is not UNSET:
            field_dict["sizeIsEstimate"] = size_is_estimate
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`ItemStorage` from a dict"""
        d = src_dict.copy()
        _checksum = d.pop("checksum", UNSET)
        checksum: Union[Unset, ItemStorageChecksum]
        if isinstance(_checksum, Unset):
            checksum = UNSET
        else:
            checksum = ItemStorageChecksum.from_dict(_checksum)

        size = d.pop("size", UNSET)

        size_is_estimate = d.pop("sizeIsEstimate", UNSET)

        url = d.pop("url", UNSET)

        item_storage = cls(
            checksum=checksum,
            size=size,
            size_is_estimate=size_is_estimate,
            url=url,
        )

        return item_storage
