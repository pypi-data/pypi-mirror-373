from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.error import Error
from ..models.table_data_model import TableDataModel
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Table")


@_attrs_define
class Table:
    """Dataview summary

    Attributes:
        description (str):
        errors (List['Error']):
        name (str):
        data_model (Union[Unset, TableDataModel]):
    """

    description: str
    errors: List["Error"]
    name: str
    data_model: Union[Unset, "TableDataModel"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        description = self.description
        errors = []
        for errors_item_data in self.errors:
            errors_item = errors_item_data.to_dict()
            errors.append(errors_item)

        name = self.name
        data_model: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.data_model, Unset):
            data_model = self.data_model.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "description": description,
                "errors": errors,
                "name": name,
            }
        )
        if data_model is not UNSET:
            field_dict["data_model"] = data_model

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Table` from a dict"""
        d = src_dict.copy()
        description = d.pop("description")

        errors = []
        _errors = d.pop("errors")
        for errors_item_data in _errors:
            errors_item = Error.from_dict(errors_item_data)

            errors.append(errors_item)

        name = d.pop("name")

        _data_model = d.pop("data_model", UNSET)
        data_model: Union[Unset, TableDataModel]
        if isinstance(_data_model, Unset):
            data_model = UNSET
        else:
            data_model = TableDataModel.from_dict(_data_model)

        table = cls(
            description=description,
            errors=errors,
            name=name,
            data_model=data_model,
        )

        return table
