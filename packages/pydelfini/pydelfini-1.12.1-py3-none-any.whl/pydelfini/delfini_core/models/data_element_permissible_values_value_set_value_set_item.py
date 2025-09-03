from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.data_element_concept import DataElementConcept
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DataElementPermissibleValuesValueSetValueSetItem")


@_attrs_define
class DataElementPermissibleValuesValueSetValueSetItem:
    """A single permissible value match.

    Attributes:
        value (Union[None, bool, float, int, str]):
        concepts (Union[Unset, List['DataElementConcept']]): Zero or more concepts associated with this individual
            value. Typically, the `appliesTo` field for PV valueSet concepts will be "valueDomain".
        label (Union[Unset, str]): A short, readable summary of this value.
        meaning (Union[Unset, str]): A description of this value's meaning.
    """

    value: Union[None, bool, float, int, str]
    concepts: Union[Unset, List["DataElementConcept"]] = UNSET
    label: Union[Unset, str] = UNSET
    meaning: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        value: Union[None, bool, float, int, str]
        value = self.value
        concepts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.concepts, Unset):
            concepts = []
            for concepts_item_data in self.concepts:
                concepts_item = concepts_item_data.to_dict()
                concepts.append(concepts_item)

        label = self.label
        meaning = self.meaning

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "value": value,
            }
        )
        if concepts is not UNSET:
            field_dict["concepts"] = concepts
        if label is not UNSET:
            field_dict["label"] = label
        if meaning is not UNSET:
            field_dict["meaning"] = meaning

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesValueSetValueSetItem` from a dict"""
        d = src_dict.copy()

        def _parse_value(data: object) -> Union[None, bool, float, int, str]:
            if data is None:
                return data
            return cast(Union[None, bool, float, int, str], data)

        value = _parse_value(d.pop("value"))

        concepts = []
        _concepts = d.pop("concepts", UNSET)
        for concepts_item_data in _concepts or []:
            concepts_item = DataElementConcept.from_dict(concepts_item_data)

            concepts.append(concepts_item)

        label = d.pop("label", UNSET)

        meaning = d.pop("meaning", UNSET)

        data_element_permissible_values_value_set_value_set_item = cls(
            value=value,
            concepts=concepts,
            label=label,
            meaning=meaning,
        )

        return data_element_permissible_values_value_set_value_set_item
