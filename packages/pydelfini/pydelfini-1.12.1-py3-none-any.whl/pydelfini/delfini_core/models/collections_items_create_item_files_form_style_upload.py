import json
from io import BytesIO
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.collections_items_create_item_files_form_style_upload_metadata import (
    CollectionsItemsCreateItemFilesFormStyleUploadMetadata,
)
from ..models.item_column import ItemColumn
from ..models.item_parser import ItemParser
from ..models.item_storage import ItemStorage
from ..models.item_type import ItemType
from ..types import File
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionsItemsCreateItemFilesFormStyleUpload")


@_attrs_define
class CollectionsItemsCreateItemFilesFormStyleUpload:
    """Creation of a new item

    Attributes:
        content (File):
        folder_id (str):  Example: ROOT.
        type (ItemType):
        columns (Union[List['ItemColumn'], None, Unset]):
        metadata (Union[Unset, CollectionsItemsCreateItemFilesFormStyleUploadMetadata]):
        parser (Union['ItemParser', None, Unset]):  Example: {'name': 'auto'}.
        storage (Union['ItemStorage', None, Unset]):  Example: {'checksum': {}, 'size': None, 'sizeIsEstimate': False,
            'url': 'delfini+datastore://default'}.
    """

    content: File
    folder_id: str
    type: ItemType
    columns: Union[List["ItemColumn"], None, Unset] = UNSET
    metadata: Union[
        Unset, "CollectionsItemsCreateItemFilesFormStyleUploadMetadata"
    ] = UNSET
    parser: Union["ItemParser", None, Unset] = UNSET
    storage: Union["ItemStorage", None, Unset] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        content = self.content.to_tuple()

        folder_id = self.folder_id
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
                "content": content,
                "folderId": folder_id,
                "type": type,
            }
        )
        if columns is not UNSET:
            field_dict["columns"] = columns
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if parser is not UNSET:
            field_dict["parser"] = parser
        if storage is not UNSET:
            field_dict["storage"] = storage

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        content = self.content.to_tuple()

        folder_id = (
            self.folder_id
            if isinstance(self.folder_id, Unset)
            else (None, str(self.folder_id).encode(), "text/plain")
        )
        type = (None, str(self.type.value).encode(), "text/plain")
        columns: Union[None, Tuple[None, bytes, str], Unset]
        if isinstance(self.columns, Unset):
            columns = UNSET
        elif isinstance(self.columns, list):
            _temp_columns = []
            for componentsschemasitem_columns_type_0_item_data in self.columns:
                componentsschemasitem_columns_type_0_item = (
                    componentsschemasitem_columns_type_0_item_data.to_dict()
                )
                _temp_columns.append(componentsschemasitem_columns_type_0_item)
            columns = (None, json.dumps(_temp_columns).encode(), "application/json")

        else:
            columns = self.columns
        metadata: Union[Unset, Tuple[None, bytes, str]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = (
                None,
                json.dumps(self.metadata.to_dict()).encode(),
                "application/json",
            )
        parser: Union[None, Tuple[None, bytes, str], Unset]
        if isinstance(self.parser, Unset):
            parser = UNSET
        elif isinstance(self.parser, ItemParser):
            parser = (
                None,
                json.dumps(self.parser.to_dict()).encode(),
                "application/json",
            )
        else:
            parser = self.parser
        storage: Union[None, Tuple[None, bytes, str], Unset]
        if isinstance(self.storage, Unset):
            storage = UNSET
        elif isinstance(self.storage, ItemStorage):
            storage = (
                None,
                json.dumps(self.storage.to_dict()).encode(),
                "application/json",
            )
        else:
            storage = self.storage

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "content": content,
                "folderId": folder_id,
                "type": type,
            }
        )
        if columns is not UNSET:
            field_dict["columns"] = columns
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if parser is not UNSET:
            field_dict["parser"] = parser
        if storage is not UNSET:
            field_dict["storage"] = storage

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsItemsCreateItemFilesFormStyleUpload` from a dict"""
        d = src_dict.copy()
        content = File(payload=BytesIO(d.pop("content")))

        folder_id = d.pop("folderId")

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

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, CollectionsItemsCreateItemFilesFormStyleUploadMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = CollectionsItemsCreateItemFilesFormStyleUploadMetadata.from_dict(
                _metadata
            )

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

        collections_items_create_item_files_form_style_upload = cls(
            content=content,
            folder_id=folder_id,
            type=type,
            columns=columns,
            metadata=metadata,
            parser=parser,
            storage=storage,
        )

        return collections_items_create_item_files_form_style_upload
