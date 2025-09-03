from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.item_type import ItemType
from ..models.parser_options import ParserOptions
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Parser")


@_attrs_define
class Parser:
    """Parser definition

    Attributes:
        item_types (List[ItemType]):
        name (str):
        options (Union[Unset, ParserOptions]):
    """

    item_types: List[ItemType]
    name: str
    options: Union[Unset, "ParserOptions"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        item_types = []
        for item_types_item_data in self.item_types:
            item_types_item = item_types_item_data.value
            item_types.append(item_types_item)

        name = self.name
        options: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "item_types": item_types,
                "name": name,
            }
        )
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Parser` from a dict"""
        d = src_dict.copy()
        item_types = []
        _item_types = d.pop("item_types")
        for item_types_item_data in _item_types:
            item_types_item = ItemType(item_types_item_data)

            item_types.append(item_types_item)

        name = d.pop("name")

        _options = d.pop("options", UNSET)
        options: Union[Unset, ParserOptions]
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = ParserOptions.from_dict(_options)

        parser = cls(
            item_types=item_types,
            name=name,
            options=options,
        )

        return parser
