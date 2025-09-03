from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.highlights_metadata import HighlightsMetadata
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Highlights")


@_attrs_define
class Highlights:
    """Highlights model

    Attributes:
        metadata (HighlightsMetadata):
        name (List[str]): A sequence of strings. The odd-numbered zero-based indices
            should be highlighted.
        description (Union[Unset, List[str]]): A sequence of strings. The odd-numbered zero-based indices
            should be highlighted.
        tags (Union[Unset, List[List[str]]]):
    """

    metadata: "HighlightsMetadata"
    name: List[str]
    description: Union[Unset, List[str]] = UNSET
    tags: Union[Unset, List[List[str]]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        metadata = self.metadata.to_dict()
        name = self.name

        description: Union[Unset, List[str]] = UNSET
        if not isinstance(self.description, Unset):
            description = self.description

        tags: Union[Unset, List[List[str]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data

                tags.append(tags_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "metadata": metadata,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Highlights` from a dict"""
        d = src_dict.copy()
        metadata = HighlightsMetadata.from_dict(d.pop("metadata"))

        name = cast(List[str], d.pop("name"))

        description = cast(List[str], d.pop("description", UNSET))

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in _tags or []:
            tags_item = cast(List[str], tags_item_data)

            tags.append(tags_item)

        highlights = cls(
            metadata=metadata,
            name=name,
            description=description,
            tags=tags,
        )

        return highlights
