from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Error")


@_attrs_define
class Error:
    """Error model

    Attributes:
        detail (str):
        title (str):
        source (Union[Unset, str]):
    """

    detail: str
    title: str
    source: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        detail = self.detail
        title = self.title
        source = self.source

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "detail": detail,
                "title": title,
            }
        )
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Error` from a dict"""
        d = src_dict.copy()
        detail = d.pop("detail")

        title = d.pop("title")

        source = d.pop("source", UNSET)

        error = cls(
            detail=detail,
            title=title,
            source=source,
        )

        return error
