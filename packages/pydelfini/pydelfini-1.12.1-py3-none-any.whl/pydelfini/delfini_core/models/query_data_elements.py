from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.query_data_elements_element_map import QueryDataElementsElementMap
from ..models.query_data_elements_error_map import QueryDataElementsErrorMap
from ..models.query_data_elements_frames_item import QueryDataElementsFramesItem


T = TypeVar("T", bound="QueryDataElements")


@_attrs_define
class QueryDataElements:
    """QueryDataElements model

    Attributes:
        element_map (QueryDataElementsElementMap):
        error_map (QueryDataElementsErrorMap):
        frames (List['QueryDataElementsFramesItem']):
    """

    element_map: "QueryDataElementsElementMap"
    error_map: "QueryDataElementsErrorMap"
    frames: List["QueryDataElementsFramesItem"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        element_map = self.element_map.to_dict()
        error_map = self.error_map.to_dict()
        frames = []
        for frames_item_data in self.frames:
            frames_item = frames_item_data.to_dict()
            frames.append(frames_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "elementMap": element_map,
                "errorMap": error_map,
                "frames": frames,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`QueryDataElements` from a dict"""
        d = src_dict.copy()
        element_map = QueryDataElementsElementMap.from_dict(d.pop("elementMap"))

        error_map = QueryDataElementsErrorMap.from_dict(d.pop("errorMap"))

        frames = []
        _frames = d.pop("frames")
        for frames_item_data in _frames:
            frames_item = QueryDataElementsFramesItem.from_dict(frames_item_data)

            frames.append(frames_item)

        query_data_elements = cls(
            element_map=element_map,
            error_map=error_map,
            frames=frames,
        )

        return query_data_elements
