"""Interactions with collections, items, and data tables"""
import abc
import os.path
from collections.abc import Iterator
from datetime import datetime
from typing import Any
from typing import BinaryIO
from typing import cast
from typing import Literal
from typing import Optional
from typing import overload
from typing import TextIO
from typing import TYPE_CHECKING
from typing import Union

import pandas as pd
import pyarrow as pa
from tqdm.auto import tqdm

from . import item_io
from .delfini_core import AuthenticatedClient as CoreAuthClient
from .delfini_core import Paginator
from .delfini_core.api.collections import collections_delete_collection_version
from .delfini_core.api.items import collections_items_list_items
from .delfini_core.api.tables import collections_tables_get_table_data
from .delfini_core.models import Collection
from .delfini_core.models import CollectionsItemsListItemsResponse200
from .delfini_core.models import Item
from .delfini_core.models import ItemParser
from .delfini_core.models import ItemType
from .delfini_core.models import TableData
from .delfini_core.types import UNSET


def pyarrow_schema_from_json_schema(js: dict[str, Any]) -> pa.Schema:
    """Build a PyArrow schema from a JSON schema.

    Args:
        js: JSON schema as dict

    """
    schema_parts = []
    for field, definition in js["properties"].items():
        field_s: dict[str, Any] = {"name": field}
        js_type = definition.get("type")
        js_format = definition.get("format")
        if js_type == "integer":
            field_s["type"] = pa.int64()
        elif js_type == "number":
            field_s["type"] = pa.float64()
        elif js_type == "string":
            if js_format == "date":
                field_s["type"] = pa.date32()
            elif js_format == "time":
                field_s["type"] = pa.time32()
            elif js_format == "datetime":
                field_s["type"] = pa.timestamp("s")
            elif js_format == "duration":
                field_s["type"] = pa.duration("s")
            else:
                field_s["type"] = pa.string()
        elif js_type == "boolean":
            field_s["type"] = pa.bool_()

        if "type" not in field_s:
            raise Exception(f"not yet supporting JSON schema: {definition}")

        # TODO: add data element ref
        field_s["metadata"] = {"dataElement": "..."}

        schema_parts.append(pa.field(**field_s))

    return pa.schema(schema_parts)


class FolderMixin(abc.ABC):
    """Folder interaction methods as a mixin class.

    This class is used by :py:class:`DelfiniCollection` and
    :py:class:`DelfiniFolder`.

    """

    def __init__(
        self,
        collection: "DelfiniCollection",
        full_path: Optional[str],
        core: CoreAuthClient,
    ) -> None:
        self._top = collection
        self._path = full_path
        self._client = core

    @property
    @abc.abstractmethod
    def id(self) -> str:
        raise NotImplementedError

    def _join_path(self, append: str) -> str:
        if self._path is None:
            return append
        return os.path.join(self._path, append)

    def folder(self, folder_name: str) -> "DelfiniFolder":
        """Open the named folder.

        Args:
            folder_name (str): the name of the folder to open
        """
        model = collections_items_list_items.sync(
            client=self._client,
            collection_id=self._top.id,
            version_id=self._top.version_id,
            in_path=UNSET if self._path is None else self._path,
            in_folder="ROOT" if self._path is None else UNSET,
            name=folder_name,
            type=[ItemType.FOLDER],
        )
        if len(model.items) != 1:
            raise Exception(f"folder not found: {folder_name}")
        return DelfiniFolder(self._top, self, model.items[0], self._client)

    def new_folder(self, folder_name: str) -> "DelfiniFolder":
        """Create a new folder.

        Args:
            folder_name (str): the name of the folder to create
        """
        within_folder_id = "ROOT" if self._top.id == self.id else self.id
        folder = item_io.new_folder(
            self._top.id,
            self._top.version_id,
            folder_name,
            self._client,
            within_folder_id=within_folder_id,
        )
        return DelfiniFolder(self._top, self, folder, self._client)

    def new_empty_file(self, file_name: str) -> "DelfiniItem":
        """Create a new, empty file.

        Args:
            file_name (str): the name of the file to create
        """
        within_folder_id = "ROOT" if self._top.id == self.id else self.id
        item = item_io.new_empty_item(
            self._top.id,
            self._top.version_id,
            file_name,
            "file",
            self._client,
            within_folder_id=within_folder_id,
        )
        return DelfiniItem(self._top, self, item, self._client)

    def __getitem__(self, item_path: str) -> "DelfiniItem":
        """Retrieve an item in this folder.

        Relative paths are supported, such as ``folder_a/folder_b/item_c``.
        """
        if "/" in item_path:
            folder_name, path_remain = item_path.split("/", 1)
            return self.folder(folder_name)[path_remain]

        model = collections_items_list_items.sync(
            client=self._client,
            collection_id=self._top.id,
            version_id=self._top.version_id,
            in_path=UNSET if self._path is None else self._path,
            in_folder="ROOT" if self._path is None else UNSET,
            name=item_path,
        )
        if len(model.items) != 1:
            if self._path is None:
                msg = f"in top level, item not found: {item_path}"
            else:
                msg = f"in folder {self._path}, item not found: {item_path}"
            raise Exception(msg)
        return DelfiniItem(self._top, self, model.items[0], self._client)

    def __iter__(self) -> Iterator["DelfiniItem"]:
        """Iterate over all items in this folder."""
        paginator = Paginator[CollectionsItemsListItemsResponse200](
            collections_items_list_items,
            self._client,
        )
        kwargs = {"collection_id": self._top.id, "version_id": self._top.version_id}
        if self._path is None:
            kwargs["in_folder"] = "ROOT"
        else:
            kwargs["in_path"] = self._path

        for item_page in paginator.paginate(**kwargs):
            for item in item_page.items:
                yield DelfiniItem(self._top, self, item, self._client)

    def walk(self) -> Iterator["DelfiniItem"]:
        """Iterate over all items in this folder, and all subfolders."""
        for item in self:
            yield item
            if isinstance(item, DelfiniFolder):
                yield from item

    def get_table(self, item_path: str) -> pd.DataFrame:
        """Retrieve the tabular contents of an item as a :py:class:`pd.DataFrame`.

        Args:
            item_path:
                The path to the item relative to the current folder.
                Accepts slashes ('/') for items in subfolders.

        """
        return self[item_path].table()

    def write_table(
        self,
        item_path: str,
        dataframe: pd.DataFrame,
        format: Literal["csv", "parquet"] = "csv",
        **kwargs: Any,
    ) -> None:
        """Write a :py:class:`pd.DataFrame` to the named item.

        Args:
            item_path:
                The path to the item relative to the current folder.
                Accepts slashes ('/') for items in subfolders.

            dataframe: The dataframe to be written.

            format: One of the supported formats (``csv`` or ``parquet``).

            **kwargs:
                Any other arguments to be passed to the Pandas export
                function. See the documentation for
                :py:func:`pd.DataFrame.to_csv` or
                :py:func:`pd.DataFrame.to_parquet` for valid
                arguments.

        """
        metadata = {
            "Content-Type": {
                "csv": "text/csv",
                "parquet": "application/vnd.apache.parquet",
            }[format]
        }
        with self._top.open(item_path, "wb", parser=format, metadata=metadata) as fp:
            if format == "csv":
                kwargs.setdefault("index", False)
                dataframe.to_csv(fp, mode="wb", **kwargs)
            elif format == "parquet":
                dataframe.to_parquet(fp, **kwargs)


if TYPE_CHECKING:
    ColumnsType = Union[pd.Series[type[object]], pa.Schema]
else:
    ColumnsType = Union[pd.Series, pa.Schema]


class DelfiniCollection(FolderMixin):
    """Represents a collection on a Delfini instance.

    Typically created by one of the collection methods in
    :py:class:`pydelfini.client.DelfiniClient`.

    In addition to collection-specific attributes and methods, this
    class also behaves as a folder (representing the top level of the
    collection's folder structure). See :py:class:`FolderMixin` for
    those methods.

    """

    def __init__(self, model: Collection, core: CoreAuthClient) -> None:
        self._model = model
        FolderMixin.__init__(self, self, None, core)

    @property
    def name(self) -> str:
        """Collection name"""
        return self._model.name

    @property
    def id(self) -> str:
        """Collection internal ID"""
        return self._model.id

    @property
    def version_id(self) -> str:
        """Current version ID"""
        return self._model.version_id

    @property
    def description(self) -> str:
        """Collection text description"""
        return self._model.description

    @property
    def created_on(self) -> datetime:
        """Datetime when collection was created"""
        return self._model.created_on

    def __repr__(self) -> str:
        return (
            f"<DelfiniCollection: name={self.name} version={self.version_id}"
            f" id={self.id}>"
        )

    def delete_collection(self) -> None:
        """Deletes the entire collection, permanently.

        You cannot delete the LIVE version of a collection if there
        exist other versions of the collection.

        """
        collections_delete_collection_version.sync(
            self.id, self.version_id, client=self._client
        )

    @overload
    def open(self, item_path: str, mode: Literal["r"]) -> TextIO:
        ...

    @overload
    def open(self, item_path: str, mode: Literal["rb"]) -> BinaryIO:
        ...

    @overload
    def open(
        self,
        item_path: str,
        mode: Literal["w"],
        *,
        parser: Optional[str] = None,
        columns: Optional[ColumnsType] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> TextIO:
        ...

    @overload
    def open(
        self,
        item_path: str,
        mode: Literal["wb"],
        *,
        parser: Optional[str] = None,
        columns: Optional[ColumnsType] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> BinaryIO:
        ...

    def open(
        self,
        item_path: str,
        mode: item_io.ItemIOModes = "r",
        *,
        parser: Optional[str] = None,
        columns: Optional[ColumnsType] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> Union[BinaryIO, TextIO]:
        r"""Open an item for reading or writing.

        When writing an item, it is important to use the returned
        file-like object either in a context manager or else call its
        :py:func:`close` method when writing is complete, otherwise
        the full contents of the file may not be written.

        Suggested usage::

            with collection.open('new-item', 'wb') as fp:
                fp.write(b'my item content, as much as I have\n')

        Args:
            item_path:
                The path to the item relative to the top level of the
                collection. Accepts slashes ('/') for items located in
                subfolders.

            mode:
                One of the following values, depending on the desired
                interaction mode:

                * ``r`` - reading, text mode
                * ``rb`` - reading, binary mode
                * ``w`` - writing, text mode
                * ``wb`` - writing, binary mode

            parser:
                If writing, optionally specify the item parser type.
                Typical values for this would be ``csv`` or
                ``parquet``.

            columns:
                If writing, optionally specify the item column schema.
                Requires ``parser`` to be set.

            metadata:
                If writing, optionally specify the item metadata.
                Typical values for this would be something like
                ``{"content-type": "text-csv"}``.

        Returns:
            A file-like interface, either :py:class:`BinaryIO` or
            :py:class:`TextIO` depending on whether the file was to be
            opened in binary or text mode. When writing, the return
            will be an instance of
            :py:class:`.item_io.DelfiniItemCreatorBinary` or
            :py:class:`.item_io.DelfiniItemCreatorText`.

        """
        # when reading, the item needs to exist, so this is the quickest way
        if mode in ("r", "rb"):
            return self[item_path].open(mode)

        elif mode in ("w", "wb"):
            _columns = None  # TODO: convert column schema
            _parser = ItemParser(name=parser) if parser else None
            _metadata = metadata

            if "/" in item_path:
                folder_path, item_name = item_path.rsplit("/", 1)
                folder_id = self[folder_path].id
            else:
                item_name = item_path
                folder_id = "ROOT"

            if mode == "w":
                return item_io.DelfiniItemCreatorText(
                    self.id,
                    self.version_id,
                    item_name,
                    self._client,
                    folder_id=folder_id,
                    type="file",
                    columns=_columns,
                    parser=_parser,
                    metadata=_metadata,
                )

            elif mode == "wb":
                return item_io.DelfiniItemCreatorBinary(
                    self.id,
                    self.version_id,
                    item_name,
                    self._client,
                    folder_id=folder_id,
                    type="file",
                    columns=_columns,
                    parser=_parser,
                    metadata=_metadata,
                )

        raise Exception("mode not found")


class DelfiniItem:
    """Represents an item within a collection."""

    #: Collection that contains this item
    collection: DelfiniCollection

    #: Folder that contains this item
    in_folder: FolderMixin

    def __new__(
        cls,
        collection: DelfiniCollection,
        in_folder: FolderMixin,
        model: Item,
        core: CoreAuthClient,
    ) -> "DelfiniItem":
        if model.type == ItemType.FOLDER and cls is DelfiniItem:
            # Automatically create an instance of DelfiniFolder when
            # the item is a folder
            return DelfiniFolder.__new__(
                DelfiniFolder, collection, in_folder, model, core
            )
        return super().__new__(cls)

    def __init__(
        self,
        collection: DelfiniCollection,
        in_folder: FolderMixin,
        model: Item,
        core: CoreAuthClient,
    ) -> None:
        self.collection = collection
        self.in_folder = in_folder
        self._model = model
        self._client = core

    @property
    def name(self) -> str:
        """Item name"""
        return self._model.name

    @property
    def path(self) -> str:
        """Item fully qualified path"""
        return self.in_folder._join_path(self.name)

    @property
    def id(self) -> str:
        """Item internal ID"""
        return self._model.id

    @property
    def type(self) -> ItemType:
        """Item type (``file``, ``folder``, ``dataview``, etc.)"""
        return self._model.type

    @property
    def created_on(self) -> datetime:
        """Datetime item was created"""
        return self._model.created_on

    def __repr__(self) -> str:
        return (
            f"<DelfiniItem: name={self.name} path={self.path} type={self.type}"
            f" id={self.id}>"
        )

    @overload
    def open(self, mode: item_io.ItemBinaryModes) -> BinaryIO:
        ...

    @overload
    def open(self, mode: item_io.ItemTextModes) -> TextIO:
        ...

    def open(self, mode: item_io.ItemIOModes = "r") -> Union[BinaryIO, TextIO]:
        r"""Open this item for reading or writing.

        When writing an item, it is important to use the returned
        file-like object either in a context manager or else call its
        :py:func:`close` method when writing is complete, otherwise
        the full contents of the file may not be written.

        Suggested usage::

            with item.open('wb') as fp:
                fp.write(b'my item content, as much as I have\n')

        Args:
            mode:
                One of the following values, depending on the desired
                interaction mode:

                * ``r`` - reading, text mode
                * ``rb`` - reading, binary mode
                * ``w`` - writing, text mode
                * ``wb`` - writing, binary mode

        Returns:
            A file-like interface, either :py:class:`BinaryIO` or
            :py:class:`TextIO` depending on whether the file was to be
            opened in binary or text mode. When writing, the return
            will be an instance of
            :py:class:`.item_io.DelfiniItemWriterBinary` or
            :py:class:`.item_io.DelfiniItemWriterText`.

        """
        if mode == "rb" or mode == "r":
            return item_io.read_item(
                mode,
                self.collection.id,
                self.collection.version_id,
                self.id,
                self._client,
            )

        elif mode == "wb":
            return item_io.DelfiniItemWriterBinary(
                self.collection.id, self.collection.version_id, self.id, self._client
            )

        elif mode == "w":
            return item_io.DelfiniItemWriterText(
                self.collection.id, self.collection.version_id, self.id, self._client
            )

    def table(self) -> pd.DataFrame:
        """Retrieve the tabular contents of this item as a :py:class:`pd.DataFrame`."""

        schema_metadata = {}

        def _get_data() -> Iterator[pa.RecordBatch]:
            nonlocal schema_metadata

            paginator = Paginator[TableData](
                collections_tables_get_table_data, self._client
            )
            kwargs = {
                "collection_id": self.collection.id,
                "version_id": self.collection.version_id,
                "table_name": self.id,
            }

            with tqdm(desc=f"Loading {self.path}") as pbar:
                for item_page in paginator.paginate(**kwargs):
                    schema_metadata = item_page.data_model.to_dict()
                    yield pa.RecordBatch.from_pylist(
                        [row.to_dict() for row in item_page.data],
                        schema=pyarrow_schema_from_json_schema(schema_metadata),
                    )
                    pbar.total = item_page.pagination.total_items
                    pbar.update(len(item_page.data))

        df = pa.Table.from_batches(_get_data()).to_pandas()

        props = schema_metadata["properties"]
        rename_map = {
            key: props[key]["description"]
            for key in props
            if "description" in props[key]
        }

        df.rename(columns=rename_map, inplace=True)

        return cast(pd.DataFrame, df)


class DelfiniFolder(DelfiniItem, FolderMixin):
    """Represents a folder within a collection.

    Note that folders cannot be opened as data streams, so the
    :py:meth:`open` method will always return :py:exc:`OSError`.

    """

    def __init__(
        self,
        collection: DelfiniCollection,
        in_folder: FolderMixin,
        model: Item,
        core: CoreAuthClient,
    ) -> None:
        DelfiniItem.__init__(self, collection, in_folder, model, core)
        FolderMixin.__init__(self, collection, in_folder._join_path(model.name), core)

    def __repr__(self) -> str:
        return (
            f"<DelfiniFolder: name={self.name} path={self.path} type={self.type}"
            f" id={self.id}>"
        )

    @overload
    def open(self, mode: item_io.ItemBinaryModes) -> BinaryIO:
        ...

    @overload
    def open(self, mode: item_io.ItemTextModes) -> TextIO:
        ...

    def open(self, mode: item_io.ItemIOModes = "r") -> Union[BinaryIO, TextIO]:
        """N/A - folders cannot be opened.

        Raises: :py:exc:`OSError` always
        """
        raise OSError("cannot open folders")
