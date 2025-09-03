from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="TermsetAdditionalPropertyItem")


@_attrs_define
class TermsetAdditionalPropertyItem:
    """TermsetAdditionalPropertyItem model

    Attributes:
        docs (int):
        term (str):
    """

    docs: int
    term: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        docs = self.docs
        term = self.term

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "docs": docs,
                "term": term,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TermsetAdditionalPropertyItem` from a dict"""
        d = src_dict.copy()
        docs = d.pop("docs")

        term = d.pop("term")

        termset_additional_property_item = cls(
            docs=docs,
            term=term,
        )

        return termset_additional_property_item
