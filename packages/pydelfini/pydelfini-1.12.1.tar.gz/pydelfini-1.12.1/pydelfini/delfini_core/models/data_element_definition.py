from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.data_element_definition_definition_type import (
    DataElementDefinitionDefinitionType,
)
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DataElementDefinition")


@_attrs_define
class DataElementDefinition:
    """A single definition applicable to this data element.

    Attributes:
        definition_type (DataElementDefinitionDefinitionType):
        text (str):
        other_type (Union[Unset, str]):
        source (Union[Unset, str]):
    """

    definition_type: DataElementDefinitionDefinitionType
    text: str
    other_type: Union[Unset, str] = UNSET
    source: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        definition_type = self.definition_type.value
        text = self.text
        other_type = self.other_type
        source = self.source

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "definitionType": definition_type,
                "text": text,
            }
        )
        if other_type is not UNSET:
            field_dict["otherType"] = other_type
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementDefinition` from a dict"""
        d = src_dict.copy()
        definition_type = DataElementDefinitionDefinitionType(d.pop("definitionType"))

        text = d.pop("text")

        other_type = d.pop("otherType", UNSET)

        source = d.pop("source", UNSET)

        data_element_definition = cls(
            definition_type=definition_type,
            text=text,
            other_type=other_type,
            source=source,
        )

        return data_element_definition
