from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element_permissible_values_external_reference_external_reference import (
    DataElementPermissibleValuesExternalReferenceExternalReference,
)


T = TypeVar("T", bound="DataElementPermissibleValuesExternalReference")


@_attrs_define
class DataElementPermissibleValuesExternalReference:
    """DataElementPermissibleValuesExternalReference model

    Attributes:
        external_reference (DataElementPermissibleValuesExternalReferenceExternalReference): A reference to an external
            source of permissible values.
    """

    external_reference: "DataElementPermissibleValuesExternalReferenceExternalReference"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        external_reference = self.external_reference.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "externalReference": external_reference,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesExternalReference` from a dict"""
        d = src_dict.copy()
        external_reference = (
            DataElementPermissibleValuesExternalReferenceExternalReference.from_dict(
                d.pop("externalReference")
            )
        )

        data_element_permissible_values_external_reference = cls(
            external_reference=external_reference,
        )

        return data_element_permissible_values_external_reference
