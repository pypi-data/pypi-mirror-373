from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.error import Error
from ..models.pagination import Pagination
from ..models.table import Table


T = TypeVar("T", bound="CollectionsTablesListTablesResponse200")


@_attrs_define
class CollectionsTablesListTablesResponse200:
    """CollectionsTablesListTablesResponse200 model

    Attributes:
        errors (List['Error']):
        pagination (Pagination):
        tables (List['Table']):
    """

    errors: List["Error"]
    pagination: "Pagination"
    tables: List["Table"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        pagination = self.pagination.to_dict()
        tables = []
        for tables_item_data in self.tables:
            tables_item = tables_item_data.to_dict()
            tables.append(tables_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "errors": errors,
                "pagination": pagination,
                "tables": tables,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsTablesListTablesResponse200` from a dict"""
        d = src_dict.copy()
        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = Error.from_dict(errors_item_data)

            errors.append(errors_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        tables = []
        _tables = d.pop("tables")
        for tables_item_data in _tables:
            tables_item = Table.from_dict(tables_item_data)

            tables.append(tables_item)

        collections_tables_list_tables_response_200 = cls(
            errors=errors,
            pagination=pagination,
            tables=tables,
        )

        return collections_tables_list_tables_response_200
