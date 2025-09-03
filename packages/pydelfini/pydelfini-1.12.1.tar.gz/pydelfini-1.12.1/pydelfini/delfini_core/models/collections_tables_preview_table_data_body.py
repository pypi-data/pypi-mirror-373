from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.item_column import ItemColumn
from ..models.item_parser import ItemParser
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionsTablesPreviewTableDataBody")


@_attrs_define
class CollectionsTablesPreviewTableDataBody:
    """CollectionsTablesPreviewTableDataBody model

    Attributes:
        parser (Union['ItemParser', None]):  Example: {'name': 'auto'}.
        columns (Union[List['ItemColumn'], None, Unset]):
        dataview_definition (Union[Unset, str]): PRQL or SQL code
        max_rows (Union[Unset, int]):  Default: 25.
    """

    parser: Union["ItemParser", None]
    columns: Union[List["ItemColumn"], None, Unset] = UNSET
    dataview_definition: Union[Unset, str] = UNSET
    max_rows: Union[Unset, int] = 25

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        parser: Union[Dict[str, Any], None]
        if isinstance(self.parser, ItemParser):
            parser = self.parser.to_dict()
        else:
            parser = self.parser
        columns: Union[List[Dict[str, Any]], None, Unset]
        if isinstance(self.columns, Unset):
            columns = UNSET
        elif isinstance(self.columns, list):
            columns = []
            for componentsschemasitem_columns_type_0_item_data in self.columns:
                componentsschemasitem_columns_type_0_item = (
                    componentsschemasitem_columns_type_0_item_data.to_dict()
                )
                columns.append(componentsschemasitem_columns_type_0_item)

        else:
            columns = self.columns
        dataview_definition = self.dataview_definition
        max_rows = self.max_rows

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "parser": parser,
            }
        )
        if columns is not UNSET:
            field_dict["columns"] = columns
        if dataview_definition is not UNSET:
            field_dict["dataview_definition"] = dataview_definition
        if max_rows is not UNSET:
            field_dict["max_rows"] = max_rows

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsTablesPreviewTableDataBody` from a dict"""
        d = src_dict.copy()

        def _parse_parser(data: object) -> Union["ItemParser", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasitem_parser_type_0 = ItemParser.from_dict(data)

                return componentsschemasitem_parser_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ItemParser", None], data)

        parser = _parse_parser(d.pop("parser"))

        def _parse_columns(data: object) -> Union[List["ItemColumn"], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
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
            return cast(Union[List["ItemColumn"], None, Unset], data)

        columns = _parse_columns(d.pop("columns", UNSET))

        dataview_definition = d.pop("dataview_definition", UNSET)

        max_rows = d.pop("max_rows", UNSET)

        collections_tables_preview_table_data_body = cls(
            parser=parser,
            columns=columns,
            dataview_definition=dataview_definition,
            max_rows=max_rows,
        )

        return collections_tables_preview_table_data_body
