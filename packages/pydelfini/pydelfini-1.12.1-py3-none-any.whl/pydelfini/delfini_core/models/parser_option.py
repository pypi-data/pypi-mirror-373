from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.parser_option_type import ParserOptionType
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="ParserOption")


@_attrs_define
class ParserOption:
    """ParserOption model

    Attributes:
        type (ParserOptionType):
        allow_null (Union[Unset, bool]):  Default: False.
        choices (Union[Unset, List[Any]]):
        default (Union[Unset, Any]):
        description (Union[Unset, str]):
    """

    type: ParserOptionType
    allow_null: Union[Unset, bool] = False
    choices: Union[Unset, List[Any]] = UNSET
    default: Union[Unset, Any] = UNSET
    description: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        type = self.type.value
        allow_null = self.allow_null
        choices: Union[Unset, List[Any]] = UNSET
        if not isinstance(self.choices, Unset):
            choices = self.choices

        default = self.default
        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "type": type,
            }
        )
        if allow_null is not UNSET:
            field_dict["allow_null"] = allow_null
        if choices is not UNSET:
            field_dict["choices"] = choices
        if default is not UNSET:
            field_dict["default"] = default
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`ParserOption` from a dict"""
        d = src_dict.copy()
        type = ParserOptionType(d.pop("type"))

        allow_null = d.pop("allow_null", UNSET)

        choices = cast(List[Any], d.pop("choices", UNSET))

        default = d.pop("default", UNSET)

        description = d.pop("description", UNSET)

        parser_option = cls(
            type=type,
            allow_null=allow_null,
            choices=choices,
            default=default,
            description=description,
        )

        return parser_option
