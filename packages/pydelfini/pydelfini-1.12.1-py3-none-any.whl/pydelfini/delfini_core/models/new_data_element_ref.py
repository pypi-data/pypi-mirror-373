from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="NewDataElementRef")


@_attrs_define
class NewDataElementRef:
    """NewDataElementRef model

    Attributes:
        ref (str):
    """

    ref: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        ref = self.ref

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "$ref": ref,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`NewDataElementRef` from a dict"""
        d = src_dict.copy()
        ref = d.pop("$ref")

        new_data_element_ref = cls(
            ref=ref,
        )

        return new_data_element_ref
