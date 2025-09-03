from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.cdeset import Cdeset


T = TypeVar("T", bound="CdesetList")


@_attrs_define
class CdesetList:
    """CdesetList model

    Attributes:
        cdesets (List['Cdeset']):
    """

    cdesets: List["Cdeset"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        cdesets = []
        for cdesets_item_data in self.cdesets:
            cdesets_item = cdesets_item_data.to_dict()
            cdesets.append(cdesets_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "cdesets": cdesets,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CdesetList` from a dict"""
        d = src_dict.copy()
        cdesets = []
        _cdesets = d.pop("cdesets")
        for cdesets_item_data in _cdesets:
            cdesets_item = Cdeset.from_dict(cdesets_item_data)

            cdesets.append(cdesets_item)

        cdeset_list = cls(
            cdesets=cdesets,
        )

        return cdeset_list
