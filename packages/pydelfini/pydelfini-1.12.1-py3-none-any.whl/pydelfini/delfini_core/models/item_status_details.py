from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.item_status_detail import ItemStatusDetail
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="ItemStatusDetails")


@_attrs_define
class ItemStatusDetails:
    """ItemStatusDetails model

    Attributes:
        parser (Union[Unset, ItemStatusDetail]):
        storage (Union[Unset, ItemStatusDetail]):
        validator (Union[Unset, ItemStatusDetail]):
    """

    parser: Union[Unset, "ItemStatusDetail"] = UNSET
    storage: Union[Unset, "ItemStatusDetail"] = UNSET
    validator: Union[Unset, "ItemStatusDetail"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        parser: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.parser, Unset):
            parser = self.parser.to_dict()
        storage: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.storage, Unset):
            storage = self.storage.to_dict()
        validator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.validator, Unset):
            validator = self.validator.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if parser is not UNSET:
            field_dict["parser"] = parser
        if storage is not UNSET:
            field_dict["storage"] = storage
        if validator is not UNSET:
            field_dict["validator"] = validator

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`ItemStatusDetails` from a dict"""
        d = src_dict.copy()
        _parser = d.pop("parser", UNSET)
        parser: Union[Unset, ItemStatusDetail]
        if isinstance(_parser, Unset):
            parser = UNSET
        else:
            parser = ItemStatusDetail.from_dict(_parser)

        _storage = d.pop("storage", UNSET)
        storage: Union[Unset, ItemStatusDetail]
        if isinstance(_storage, Unset):
            storage = UNSET
        else:
            storage = ItemStatusDetail.from_dict(_storage)

        _validator = d.pop("validator", UNSET)
        validator: Union[Unset, ItemStatusDetail]
        if isinstance(_validator, Unset):
            validator = UNSET
        else:
            validator = ItemStatusDetail.from_dict(_validator)

        item_status_details = cls(
            parser=parser,
            storage=storage,
            validator=validator,
        )

        return item_status_details
