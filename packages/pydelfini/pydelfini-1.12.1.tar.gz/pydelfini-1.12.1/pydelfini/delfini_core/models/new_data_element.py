from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.data_element_concept import DataElementConcept
from ..models.data_element_definition import DataElementDefinition
from ..models.data_element_permissible_values_date_time_format import (
    DataElementPermissibleValuesDateTimeFormat,
)
from ..models.data_element_permissible_values_external_reference import (
    DataElementPermissibleValuesExternalReference,
)
from ..models.data_element_permissible_values_number_range import (
    DataElementPermissibleValuesNumberRange,
)
from ..models.data_element_permissible_values_text_range import (
    DataElementPermissibleValuesTextRange,
)
from ..models.data_element_permissible_values_value_set import (
    DataElementPermissibleValuesValueSet,
)
from ..models.new_data_element_data_type import NewDataElementDataType
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="NewDataElement")


@_attrs_define
class NewDataElement:
    """Delfini Data Element

    Attributes:
        data_type (NewDataElementDataType): The data type valid for this data element.
        name (str): The title or name of the data element.
        concepts (Union[Unset, List['DataElementConcept']]): Linked concepts for the data element.
        definition (Union[Unset, List['DataElementDefinition']]): Any definitions that describe or inform the context of
            the data element.
        permissible_values (Union[Unset, List[Union['DataElementPermissibleValuesDateTimeFormat',
            'DataElementPermissibleValuesExternalReference', 'DataElementPermissibleValuesNumberRange',
            'DataElementPermissibleValuesTextRange', 'DataElementPermissibleValuesValueSet']]]): Describes the values that
            this data element properly represents.
        permit_null (Union[Unset, bool]): If true, nulls will not cause validation failures. Default: False.
        sensitivity (Union[Unset, bool]): Whether this data element references sensitive data (PHI, PII, etc.)
    """

    data_type: NewDataElementDataType
    name: str
    concepts: Union[Unset, List["DataElementConcept"]] = UNSET
    definition: Union[Unset, List["DataElementDefinition"]] = UNSET
    permissible_values: Union[
        Unset,
        List[
            Union[
                "DataElementPermissibleValuesDateTimeFormat",
                "DataElementPermissibleValuesExternalReference",
                "DataElementPermissibleValuesNumberRange",
                "DataElementPermissibleValuesTextRange",
                "DataElementPermissibleValuesValueSet",
            ]
        ],
    ] = UNSET
    permit_null: Union[Unset, bool] = False
    sensitivity: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        data_type = self.data_type.value
        name = self.name
        concepts: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.concepts, Unset):
            concepts = []
            for concepts_item_data in self.concepts:
                concepts_item = concepts_item_data.to_dict()
                concepts.append(concepts_item)

        definition: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.definition, Unset):
            definition = []
            for definition_item_data in self.definition:
                definition_item = definition_item_data.to_dict()
                definition.append(definition_item)

        permissible_values: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.permissible_values, Unset):
            permissible_values = []
            for permissible_values_item_data in self.permissible_values:
                permissible_values_item: Dict[str, Any]
                if isinstance(
                    permissible_values_item_data,
                    DataElementPermissibleValuesNumberRange,
                ):
                    permissible_values_item = permissible_values_item_data.to_dict()
                elif isinstance(
                    permissible_values_item_data, DataElementPermissibleValuesTextRange
                ):
                    permissible_values_item = permissible_values_item_data.to_dict()
                elif isinstance(
                    permissible_values_item_data,
                    DataElementPermissibleValuesDateTimeFormat,
                ):
                    permissible_values_item = permissible_values_item_data.to_dict()
                elif isinstance(
                    permissible_values_item_data, DataElementPermissibleValuesValueSet
                ):
                    permissible_values_item = permissible_values_item_data.to_dict()
                else:
                    permissible_values_item = permissible_values_item_data.to_dict()

                permissible_values.append(permissible_values_item)

        permit_null = self.permit_null
        sensitivity = self.sensitivity

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dataType": data_type,
                "name": name,
            }
        )
        if concepts is not UNSET:
            field_dict["concepts"] = concepts
        if definition is not UNSET:
            field_dict["definition"] = definition
        if permissible_values is not UNSET:
            field_dict["permissibleValues"] = permissible_values
        if permit_null is not UNSET:
            field_dict["permitNull"] = permit_null
        if sensitivity is not UNSET:
            field_dict["sensitivity"] = sensitivity

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`NewDataElement` from a dict"""
        d = src_dict.copy()
        data_type = NewDataElementDataType(d.pop("dataType"))

        name = d.pop("name")

        concepts = []
        _concepts = d.pop("concepts", UNSET)
        for concepts_item_data in _concepts or []:
            concepts_item = DataElementConcept.from_dict(concepts_item_data)

            concepts.append(concepts_item)

        definition = []
        _definition = d.pop("definition", UNSET)
        for definition_item_data in _definition or []:
            definition_item = DataElementDefinition.from_dict(definition_item_data)

            definition.append(definition_item)

        permissible_values = []
        _permissible_values = d.pop("permissibleValues", UNSET)
        for permissible_values_item_data in _permissible_values or []:

            def _parse_permissible_values_item(
                data: object,
            ) -> Union[
                "DataElementPermissibleValuesDateTimeFormat",
                "DataElementPermissibleValuesExternalReference",
                "DataElementPermissibleValuesNumberRange",
                "DataElementPermissibleValuesTextRange",
                "DataElementPermissibleValuesValueSet",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemasdata_element_permissible_values_type_0 = (
                        DataElementPermissibleValuesNumberRange.from_dict(data)
                    )

                    return componentsschemasdata_element_permissible_values_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemasdata_element_permissible_values_type_1 = (
                        DataElementPermissibleValuesTextRange.from_dict(data)
                    )

                    return componentsschemasdata_element_permissible_values_type_1
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemasdata_element_permissible_values_type_2 = (
                        DataElementPermissibleValuesDateTimeFormat.from_dict(data)
                    )

                    return componentsschemasdata_element_permissible_values_type_2
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemasdata_element_permissible_values_type_3 = (
                        DataElementPermissibleValuesValueSet.from_dict(data)
                    )

                    return componentsschemasdata_element_permissible_values_type_3
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasdata_element_permissible_values_type_4 = (
                    DataElementPermissibleValuesExternalReference.from_dict(data)
                )

                return componentsschemasdata_element_permissible_values_type_4

            permissible_values_item = _parse_permissible_values_item(
                permissible_values_item_data
            )

            permissible_values.append(permissible_values_item)

        permit_null = d.pop("permitNull", UNSET)

        sensitivity = d.pop("sensitivity", UNSET)

        new_data_element = cls(
            data_type=data_type,
            name=name,
            concepts=concepts,
            definition=definition,
            permissible_values=permissible_values,
            permit_null=permit_null,
            sensitivity=sensitivity,
        )

        return new_data_element
