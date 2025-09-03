import datetime
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define
from dateutil.parser import isoparse

from ..models.item_column import ItemColumn
from ..models.item_metadata import ItemMetadata
from ..models.item_parser import ItemParser
from ..models.item_sensitivity_labels import ItemSensitivityLabels
from ..models.item_status import ItemStatus
from ..models.item_storage import ItemStorage
from ..models.item_type import ItemType
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="Item")


@_attrs_define
class Item:
    """A single item's metadata

    Attributes:
        created_on (datetime.datetime):
        id (str):
        name (str): Item name
        path (str): Slash-delimited item path
        type (ItemType):
        columns (Union[List['ItemColumn'], None, Unset]):
        folder_id (Union[Unset, str]): Item ID of parent folder, or ROOT Example: ROOT.
        metadata (Union[Unset, ItemMetadata]): Arbitrary metadata as key-value string pairs
        parser (Union['ItemParser', None, Unset]):  Example: {'name': 'auto'}.
        sensitivity_labels (Union[Unset, ItemSensitivityLabels]):
        status (Union[Unset, ItemStatus]):
        storage (Union['ItemStorage', None, Unset]):  Example: {'checksum': {}, 'size': None, 'sizeIsEstimate': False,
            'url': 'delfini+datastore://default'}.
    """

    created_on: datetime.datetime
    id: str
    name: str
    path: str
    type: ItemType
    columns: Union[List["ItemColumn"], None, Unset] = UNSET
    folder_id: Union[Unset, str] = UNSET
    metadata: Union[Unset, "ItemMetadata"] = UNSET
    parser: Union["ItemParser", None, Unset] = UNSET
    sensitivity_labels: Union[Unset, "ItemSensitivityLabels"] = UNSET
    status: Union[Unset, "ItemStatus"] = UNSET
    storage: Union["ItemStorage", None, Unset] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        created_on = self.created_on.isoformat()
        id = self.id
        name = self.name
        path = self.path
        type = self.type.value
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
        folder_id = self.folder_id
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()
        parser: Union[Dict[str, Any], None, Unset]
        if isinstance(self.parser, Unset):
            parser = UNSET
        elif isinstance(self.parser, ItemParser):
            parser = self.parser.to_dict()
        else:
            parser = self.parser
        sensitivity_labels: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.sensitivity_labels, Unset):
            sensitivity_labels = self.sensitivity_labels.to_dict()
        status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()
        storage: Union[Dict[str, Any], None, Unset]
        if isinstance(self.storage, Unset):
            storage = UNSET
        elif isinstance(self.storage, ItemStorage):
            storage = self.storage.to_dict()
        else:
            storage = self.storage

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "createdOn": created_on,
                "id": id,
                "name": name,
                "path": path,
                "type": type,
            }
        )
        if columns is not UNSET:
            field_dict["columns"] = columns
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if parser is not UNSET:
            field_dict["parser"] = parser
        if sensitivity_labels is not UNSET:
            field_dict["sensitivityLabels"] = sensitivity_labels
        if status is not UNSET:
            field_dict["status"] = status
        if storage is not UNSET:
            field_dict["storage"] = storage

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`Item` from a dict"""
        d = src_dict.copy()
        created_on = isoparse(d.pop("createdOn"))

        id = d.pop("id")

        name = d.pop("name")

        path = d.pop("path")

        type = ItemType(d.pop("type"))

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

        folder_id = d.pop("folderId", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ItemMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ItemMetadata.from_dict(_metadata)

        def _parse_parser(data: object) -> Union["ItemParser", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasitem_parser_type_0 = ItemParser.from_dict(data)

                return componentsschemasitem_parser_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ItemParser", None, Unset], data)

        parser = _parse_parser(d.pop("parser", UNSET))

        _sensitivity_labels = d.pop("sensitivityLabels", UNSET)
        sensitivity_labels: Union[Unset, ItemSensitivityLabels]
        if isinstance(_sensitivity_labels, Unset):
            sensitivity_labels = UNSET
        else:
            sensitivity_labels = ItemSensitivityLabels.from_dict(_sensitivity_labels)

        _status = d.pop("status", UNSET)
        status: Union[Unset, ItemStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ItemStatus.from_dict(_status)

        def _parse_storage(data: object) -> Union["ItemStorage", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemasitem_storage_type_0 = ItemStorage.from_dict(data)

                return componentsschemasitem_storage_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ItemStorage", None, Unset], data)

        storage = _parse_storage(d.pop("storage", UNSET))

        item = cls(
            created_on=created_on,
            id=id,
            name=name,
            path=path,
            type=type,
            columns=columns,
            folder_id=folder_id,
            metadata=metadata,
            parser=parser,
            sensitivity_labels=sensitivity_labels,
            status=status,
            storage=storage,
        )

        return item
