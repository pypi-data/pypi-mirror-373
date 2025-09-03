from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.error import Error
from ..models.pagination import Pagination
from ..models.table_data_data_item import TableDataDataItem
from ..models.table_data_data_model import TableDataDataModel


T = TypeVar("T", bound="TableData")


@_attrs_define
class TableData:
    """Dataview contents

    Attributes:
        data (List['TableDataDataItem']):
        data_model (TableDataDataModel):
        errors (List['Error']):
        pagination (Pagination):
    """

    data: List["TableDataDataItem"]
    data_model: "TableDataDataModel"
    errors: List["Error"]
    pagination: "Pagination"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        data_model = self.data_model.to_dict()
        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        pagination = self.pagination.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data": data,
                "data_model": data_model,
                "errors": errors,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TableData` from a dict"""
        d = src_dict.copy()
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = TableDataDataItem.from_dict(data_item_data)

            data.append(data_item)

        data_model = TableDataDataModel.from_dict(d.pop("data_model"))

        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = Error.from_dict(errors_item_data)

            errors.append(errors_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        table_data = cls(
            data=data,
            data_model=data_model,
            errors=errors,
            pagination=pagination,
        )

        return table_data
