from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="MetadataTags")


@_attrs_define
class MetadataTags:
    """MetadataTags model

    Attributes:
        tags (List[str]):
    """

    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        tags = self.tags

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "tags": tags,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`MetadataTags` from a dict"""
        d = src_dict.copy()
        tags = cast(List[str], d.pop("tags"))

        metadata_tags = cls(
            tags=tags,
        )

        return metadata_tags
