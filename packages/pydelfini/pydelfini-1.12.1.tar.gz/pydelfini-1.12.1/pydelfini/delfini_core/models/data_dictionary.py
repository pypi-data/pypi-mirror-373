from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.data_dictionary_source_item import DataDictionarySourceItem
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DataDictionary")


@_attrs_define
class DataDictionary:
    """DataDictionary model

    Attributes:
        source (List[DataDictionarySourceItem]):
        url (str):
        name (Union[Unset, str]):
    """

    source: List[DataDictionarySourceItem]
    url: str
    name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        source = []
        for source_item_data in self.source:
            source_item = source_item_data.value
            source.append(source_item)

        url = self.url
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "source": source,
                "url": url,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataDictionary` from a dict"""
        d = src_dict.copy()
        source = []
        _source = d.pop("source")
        for source_item_data in _source:
            source_item = DataDictionarySourceItem(source_item_data)

            source.append(source_item)

        url = d.pop("url")

        name = d.pop("name", UNSET)

        data_dictionary = cls(
            source=source,
            url=url,
            name=name,
        )

        return data_dictionary
