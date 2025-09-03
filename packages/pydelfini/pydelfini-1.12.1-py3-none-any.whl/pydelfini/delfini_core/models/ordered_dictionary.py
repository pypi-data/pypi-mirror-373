from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.data_element import DataElement
from ..models.data_element_bundle import DataElementBundle
from ..models.pagination import Pagination


T = TypeVar("T", bound="OrderedDictionary")


@_attrs_define
class OrderedDictionary:
    """OrderedDictionary model

    Attributes:
        entries (List[Union['DataElement', 'DataElementBundle']]):
        pagination (Pagination):
    """

    entries: List[Union["DataElement", "DataElementBundle"]]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        entries = []
        for entries_item_data in self.entries:
            entries_item: Dict[str, Any]
            if isinstance(entries_item_data, DataElement):
                entries_item = entries_item_data.to_dict()
            else:
                entries_item = entries_item_data.to_dict()

            entries.append(entries_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "entries": entries,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`OrderedDictionary` from a dict"""
        d = src_dict.copy()
        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:

            def _parse_entries_item(
                data: object,
            ) -> Union["DataElement", "DataElementBundle"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    entries_item_type_0 = DataElement.from_dict(data)

                    return entries_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                entries_item_type_1 = DataElementBundle.from_dict(data)

                return entries_item_type_1

            entries_item = _parse_entries_item(entries_item_data)

            entries.append(entries_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        ordered_dictionary = cls(
            entries=entries,
            pagination=pagination,
        )

        return ordered_dictionary
