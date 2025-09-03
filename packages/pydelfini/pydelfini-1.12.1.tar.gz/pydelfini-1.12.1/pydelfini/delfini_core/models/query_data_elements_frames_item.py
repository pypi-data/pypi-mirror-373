from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.item_column import ItemColumn


T = TypeVar("T", bound="QueryDataElementsFramesItem")


@_attrs_define
class QueryDataElementsFramesItem:
    """QueryDataElementsFramesItem model

    Attributes:
        columns (Union[List['ItemColumn'], None]):
        step_name (str):
    """

    columns: Union[List["ItemColumn"], None]
    step_name: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        columns: Union[List[Dict[str, Any]], None]
        if isinstance(self.columns, list):
            columns = []
            for componentsschemasitem_columns_type_0_item_data in self.columns:
                componentsschemasitem_columns_type_0_item = (
                    componentsschemasitem_columns_type_0_item_data.to_dict()
                )
                columns.append(componentsschemasitem_columns_type_0_item)

        else:
            columns = self.columns
        step_name = self.step_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "columns": columns,
                "step_name": step_name,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`QueryDataElementsFramesItem` from a dict"""
        d = src_dict.copy()

        def _parse_columns(data: object) -> Union[List["ItemColumn"], None]:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                componentsschemasitem_columns_type_0 = []
                _componentsschemasitem_columns_type_0 = data
                for (
                    componentsschemasitem_columns_type_0_item_data
                ) in _componentsschemasitem_columns_type_0:
                    componentsschemasitem_columns_type_0_item = ItemColumn.from_dict(
                        componentsschemasitem_columns_type_0_item_data
                    )

                    componentsschemasitem_columns_type_0.append(
                        componentsschemasitem_columns_type_0_item
                    )

                return componentsschemasitem_columns_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List["ItemColumn"], None], data)

        columns = _parse_columns(d.pop("columns"))

        step_name = d.pop("step_name")

        query_data_elements_frames_item = cls(
            columns=columns,
            step_name=step_name,
        )

        return query_data_elements_frames_item
