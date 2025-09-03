from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cache_file_type import CacheFileType
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CacheFile")


@_attrs_define
class CacheFile:
    """CacheFile model

    Attributes:
        base_dir (Union[Unset, str]):
        disk_free_min (Union[Unset, int]):  Default: 4294967296.
        size_max_cacheable (Union[Unset, int]):  Default: 134217728.
        type (Union[Unset, CacheFileType]):
    """

    base_dir: Union[Unset, str] = UNSET
    disk_free_min: Union[Unset, int] = 4294967296
    size_max_cacheable: Union[Unset, int] = 134217728
    type: Union[Unset, CacheFileType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        base_dir = self.base_dir
        disk_free_min = self.disk_free_min
        size_max_cacheable = self.size_max_cacheable
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if base_dir is not UNSET:
            field_dict["base_dir"] = base_dir
        if disk_free_min is not UNSET:
            field_dict["disk_free_min"] = disk_free_min
        if size_max_cacheable is not UNSET:
            field_dict["size_max_cacheable"] = size_max_cacheable
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CacheFile` from a dict"""
        d = src_dict.copy()
        base_dir = d.pop("base_dir", UNSET)

        disk_free_min = d.pop("disk_free_min", UNSET)

        size_max_cacheable = d.pop("size_max_cacheable", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, CacheFileType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = CacheFileType(_type)

        cache_file = cls(
            base_dir=base_dir,
            disk_free_min=disk_free_min,
            size_max_cacheable=size_max_cacheable,
            type=type,
        )

        cache_file.additional_properties = d
        return cache_file

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
