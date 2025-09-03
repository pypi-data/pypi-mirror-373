from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="DataElementPermissibleValuesExternalReferenceExternalReference")


@_attrs_define
class DataElementPermissibleValuesExternalReferenceExternalReference:
    """A reference to an external source of permissible values.

    Attributes:
        reference_id (str):
        source (str):
        url (Union[Unset, str]):
    """

    reference_id: str
    source: str
    url: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        reference_id = self.reference_id
        source = self.source
        url = self.url

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "referenceId": reference_id,
                "source": source,
            }
        )
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementPermissibleValuesExternalReferenceExternalReference` from a dict"""
        d = src_dict.copy()
        reference_id = d.pop("referenceId")

        source = d.pop("source")

        url = d.pop("url", UNSET)

        data_element_permissible_values_external_reference_external_reference = cls(
            reference_id=reference_id,
            source=source,
            url=url,
        )

        return data_element_permissible_values_external_reference_external_reference
