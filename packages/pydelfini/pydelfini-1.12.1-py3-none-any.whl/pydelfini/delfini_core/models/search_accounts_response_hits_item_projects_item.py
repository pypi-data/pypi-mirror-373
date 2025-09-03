from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.highlights import Highlights


T = TypeVar("T", bound="SearchAccountsResponseHitsItemProjectsItem")


@_attrs_define
class SearchAccountsResponseHitsItemProjectsItem:
    """SearchAccountsResponseHitsItemProjectsItem model

    Attributes:
        description (str):
        highlights (Highlights):
        id (str):
        name (str):
    """

    description: str
    highlights: "Highlights"
    id: str
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        highlights = self.highlights.to_dict()
        id = self.id
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "description": description,
                "highlights": highlights,
                "id": id,
                "name": name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchAccountsResponseHitsItemProjectsItem` from a dict"""
        d = src_dict.copy()
        description = d.pop("description")

        highlights = Highlights.from_dict(d.pop("highlights"))

        id = d.pop("id")

        name = d.pop("name")

        search_accounts_response_hits_item_projects_item = cls(
            description=description,
            highlights=highlights,
            id=id,
            name=name,
        )

        return search_accounts_response_hits_item_projects_item
