from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.dictionary_search_options_options import DictionarySearchOptionsOptions
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DictionarySearchOptions")


@_attrs_define
class DictionarySearchOptions:
    """DictionarySearchOptions model

    Attributes:
        source (str):
        options (Union[Unset, DictionarySearchOptionsOptions]):
    """

    source: str
    options: Union[Unset, "DictionarySearchOptionsOptions"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        source = self.source
        options: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "source": source,
            }
        )
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DictionarySearchOptions` from a dict"""
        d = src_dict.copy()
        source = d.pop("source")

        _options = d.pop("options", UNSET)
        options: Union[Unset, DictionarySearchOptionsOptions]
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = DictionarySearchOptionsOptions.from_dict(_options)

        dictionary_search_options = cls(
            source=source,
            options=options,
        )

        return dictionary_search_options
