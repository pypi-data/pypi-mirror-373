from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.highlights import Highlights


T = TypeVar("T", bound="SearchCollectionsResponseHitsItemDataElementsItem")


@_attrs_define
class SearchCollectionsResponseHitsItemDataElementsItem:
    """SearchCollectionsResponseHitsItemDataElementsItem model

    Attributes:
        highlights (Highlights):
        id (str):
        url (str):
        version (str):
    """

    highlights: "Highlights"
    id: str
    url: str
    version: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        highlights = self.highlights.to_dict()
        id = self.id
        url = self.url
        version = self.version

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "highlights": highlights,
                "id": id,
                "url": url,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchCollectionsResponseHitsItemDataElementsItem` from a dict"""
        d = src_dict.copy()
        highlights = Highlights.from_dict(d.pop("highlights"))

        id = d.pop("id")

        url = d.pop("url")

        version = d.pop("version")

        search_collections_response_hits_item_data_elements_item = cls(
            highlights=highlights,
            id=id,
            url=url,
            version=version,
        )

        return search_collections_response_hits_item_data_elements_item
