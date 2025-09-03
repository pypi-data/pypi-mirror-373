from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.data_element_concept_applies_to import DataElementConceptAppliesTo


T = TypeVar("T", bound="DataElementConcept")


@_attrs_define
class DataElementConcept:
    """Reference to an entry in a concept repository.

    Attributes:
        applies_to (DataElementConceptAppliesTo):
        name (str): The human-readable definition of the concept.
        origin (str): The repository where this concept can be found, either as a commonly known name, or as a URL.
        origin_id (str): The ID of the concept in the concept repository.
    """

    applies_to: DataElementConceptAppliesTo
    name: str
    origin: str
    origin_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        applies_to = self.applies_to.value
        name = self.name
        origin = self.origin
        origin_id = self.origin_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "appliesTo": applies_to,
                "name": name,
                "origin": origin,
                "originId": origin_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`DataElementConcept` from a dict"""
        d = src_dict.copy()
        applies_to = DataElementConceptAppliesTo(d.pop("appliesTo"))

        name = d.pop("name")

        origin = d.pop("origin")

        origin_id = d.pop("originId")

        data_element_concept = cls(
            applies_to=applies_to,
            name=name,
            origin=origin,
            origin_id=origin_id,
        )

        return data_element_concept
