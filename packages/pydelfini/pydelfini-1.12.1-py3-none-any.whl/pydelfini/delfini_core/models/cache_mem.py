from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cache_mem_type import CacheMemType
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CacheMem")


@_attrs_define
class CacheMem:
    """CacheMem model

    Attributes:
        cache_max (Union[Unset, int]):  Default: 1073741824.
        type (Union[Unset, CacheMemType]):
    """

    cache_max: Union[Unset, int] = 1073741824
    type: Union[Unset, CacheMemType] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        cache_max = self.cache_max
        type: Union[Unset, str] = UNSET
        if not isinstance(self.type, Unset):
            type = self.type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cache_max is not UNSET:
            field_dict["cache_max"] = cache_max
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CacheMem` from a dict"""
        d = src_dict.copy()
        cache_max = d.pop("cache_max", UNSET)

        _type = d.pop("type", UNSET)
        type: Union[Unset, CacheMemType]
        if isinstance(_type, Unset):
            type = UNSET
        else:
            type = CacheMemType(_type)

        cache_mem = cls(
            cache_max=cache_max,
            type=type,
        )

        cache_mem.additional_properties = d
        return cache_mem

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
