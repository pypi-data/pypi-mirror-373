from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.collections_tables_get_table_data_elements_response_200_element_map import (
    CollectionsTablesGetTableDataElementsResponse200ElementMap,
)
from ..models.collections_tables_get_table_data_elements_response_200_error_map import (
    CollectionsTablesGetTableDataElementsResponse200ErrorMap,
)


T = TypeVar("T", bound="CollectionsTablesGetTableDataElementsResponse200")


@_attrs_define
class CollectionsTablesGetTableDataElementsResponse200:
    """CollectionsTablesGetTableDataElementsResponse200 model

    Attributes:
        element_map (CollectionsTablesGetTableDataElementsResponse200ElementMap):
        error_map (CollectionsTablesGetTableDataElementsResponse200ErrorMap):
    """

    element_map: "CollectionsTablesGetTableDataElementsResponse200ElementMap"
    error_map: "CollectionsTablesGetTableDataElementsResponse200ErrorMap"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        element_map = self.element_map.to_dict()
        error_map = self.error_map.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "elementMap": element_map,
                "errorMap": error_map,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsTablesGetTableDataElementsResponse200` from a dict"""
        d = src_dict.copy()
        element_map = (
            CollectionsTablesGetTableDataElementsResponse200ElementMap.from_dict(
                d.pop("elementMap")
            )
        )

        error_map = CollectionsTablesGetTableDataElementsResponse200ErrorMap.from_dict(
            d.pop("errorMap")
        )

        collections_tables_get_table_data_elements_response_200 = cls(
            element_map=element_map,
            error_map=error_map,
        )

        return collections_tables_get_table_data_elements_response_200
