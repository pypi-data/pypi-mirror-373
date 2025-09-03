"""File-like (stream) read and write on items"""
import io
import os
import threading
from collections.abc import Iterable
from collections.abc import Iterator
from types import TracebackType
from typing import BinaryIO
from typing import Literal
from typing import Optional
from typing import overload
from typing import TextIO
from typing import TYPE_CHECKING
from typing import Union

if TYPE_CHECKING:
    from typing_extensions import Buffer

from .delfini_core import AuthenticatedClient as CoreAuthClient
from .delfini_core.api.items import collections_items_create_item
from .delfini_core.api.items import collections_items_get_item_data
from .delfini_core.api.items import collections_items_put_item_data
from .delfini_core.models import CollectionsItemsCreateItemFilesFormStyleUpload
from .delfini_core.models import CollectionsItemsCreateItemFilesFormStyleUploadMetadata
from .delfini_core.models import CollectionsItemsCreateItemJsonNewItemRequest
from .delfini_core.models import Item
from .delfini_core.models import ItemColumn
from .delfini_core.models import ItemParser
from .delfini_core.models import ItemStorage
from .delfini_core.models import ItemType
from .delfini_core.types import File
from .delfini_core.types import UNSET

ItemReadModes = Literal["r", "rb"]
ItemWriteModes = Literal["w", "wb"]
ItemBinaryModes = Literal["rb", "wb"]
ItemTextModes = Literal["r", "w"]
ItemIOModes = Literal[ItemReadModes, ItemWriteModes]


# When doing stream IO on items (reading and writing bytes), one of
# the challenging goals is to try to read and write directly from the
# HTTP stream; that is, to avoid buffering the data into a secondary
# stream that the user interacts with. This is important because it
# minimizes memory usage and latency from copying large amounts of
# data.
#
# When reading items, direct access to the item's stream is
# straightforward, since the httpx client used by delfini_core returns
# a `payload` that can be treated directly as a stream. The only
# detail is to support both binary and text modes of interaction,
# however that is easily handled with io.TextIOWrapper.
#
# However, it's much harder when writing the item. The httpx client
# can accept a stream when submitting the item data, but the user also
# needs a stream to write to. Rather than buffering the user's write
# content in memory via something like io.BytesIO, we do it the UNIX
# way -- we create a _pipe_, give the httpx client the read end of the
# pipe, and give the user the write end. Then, the API call is run in
# a thread so that the pipe does not fill up and block. In order to
# manage the thread, the user should be sure to either `close()` the
# file handle when finished, or else use it in a context manager
# block.


@overload
def read_item(
    mode: Literal["r"],
    collection_id: str,
    version_id: str,
    item_id: str,
    client: CoreAuthClient,
) -> TextIO:
    ...


@overload
def read_item(
    mode: Literal["rb"],
    collection_id: str,
    version_id: str,
    item_id: str,
    client: CoreAuthClient,
) -> BinaryIO:
    ...


def read_item(
    mode: ItemReadModes,
    collection_id: str,
    version_id: str,
    item_id: str,
    client: CoreAuthClient,
) -> Union[BinaryIO, TextIO]:
    """Read the contents (binary or text mode) of an item.

    This is typically called by the high-level client libraries in
    :py:mod:`pydelfini.collections`.

    """
    response = collections_items_get_item_data.sync(
        collection_id=collection_id,
        version_id=version_id,
        item_id=item_id,
        client=client,
    )
    if mode == "rb":
        return response.payload
    else:
        return io.TextIOWrapper(response.payload)


class DelfiniItemWriterCore:
    def __init__(
        self, collection_id: str, version_id: str, item_id: str, client: CoreAuthClient
    ) -> None:
        self.collection_id = collection_id
        self.version_id = version_id
        self.item_id = item_id
        self._client = client
        self._exc: Optional[BaseException] = None

        # Create a pipe - read side is for the API client, write side
        # is for the user
        read_side, write_side = os.pipe()
        self._binary_stream = open(write_side, "wb")
        read_stream = open(read_side, "rb")

        # Patch out the fileno method on the read stream so that httpx
        # doesn't think this is a real file and lets us treat it as a
        # streaming body.
        read_stream.fileno = self.fileno  # type: ignore[method-assign]

        # The API call needs to be in a thread so that it can consume
        # the read side of the pipe without the write side blocking
        self._thread = threading.Thread(
            target=self._call_api, kwargs={"stream": read_stream}
        )
        self._thread.start()

    def _call_api(self, stream: BinaryIO) -> None:
        try:
            collections_items_put_item_data.sync(
                self.collection_id,
                self.version_id,
                self.item_id,
                client=self._client,
                body=File(payload=stream),
            )
        except BaseException as e:
            self._exc = e

    def __exit__(
        self,
        typ: Optional[type[BaseException]],
        val: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self._binary_stream.close()
        self._thread.join()

        if self._exc:
            raise self._exc

    def close(self) -> None:
        """Close and flush the stream, completing the file write."""
        self.__exit__(None, None, None)

    def __del__(self) -> None:
        self.close()

    def fileno(self) -> int:
        """N/A - not a real file

        Raises:
            OSError: always

        """
        raise OSError("not a real file")

    def flush(self) -> None:
        self._binary_stream.flush()

    def isatty(self) -> bool:
        """Always False"""
        return False

    def readable(self) -> bool:
        """Always False"""
        return False

    def writable(self) -> bool:
        """Always True"""
        return True

    def seekable(self) -> bool:
        """Always False"""
        return False

    def seek(self, offset: int, whence: int = 0) -> int:
        """N/A - not a real file

        Raises:
            OSError: always

        """
        raise OSError("not a real file")

    def tell(self) -> int:
        return self._binary_stream.tell()

    def truncate(self, size: Optional[int] = None) -> int:
        """N/A - not a real file

        Raises:
            OSError: always

        """
        raise OSError("not a real file")


class DelfiniItemWriterBinary(DelfiniItemWriterCore, BinaryIO):
    r"""File-like interface for writing binary data to items.

    It is important to either use this in a context manager or else
    call the :py:func:`close` method when writing is complete,
    otherwise the full contents of the file may not be written.

    Suggested usage::

        with item.open('wb') as fp:
            fp.write(b'my item content, as much as I have\n')

    """

    def __enter__(self) -> BinaryIO:
        return self._binary_stream

    def __iter__(self) -> Iterator[bytes]:
        raise OSError("cannot read")

    def __next__(self) -> bytes:
        raise OSError("cannot read")

    def read(self, n: int = -1) -> bytes:
        """N/A - cannot read

        Raises:
            OSError: always

        """
        raise OSError("cannot read")

    def readline(self, limit: int = -1) -> bytes:
        """N/A - cannot read

        Raises:
            OSError: always

        """
        raise OSError("cannot read")

    def readlines(self, hint: int = -1) -> list[bytes]:
        """N/A - cannot read

        Raises:
            OSError: always

        """
        raise OSError("cannot read")

    def write(self, s: Union[bytes, "Buffer"]) -> int:
        """Write to the stream.

        Args:
            s: content to write

        Returns:
            number of bytes written
        """
        return self._binary_stream.write(s)

    def writelines(self, lines: Union[Iterable[bytes], Iterable["Buffer"]]) -> None:
        """Write lines to the stream.

        Args:
            lines: iterable of lines (bytes or Buffer) to write

        """
        return self._binary_stream.writelines(lines)


class DelfiniItemWriterText(DelfiniItemWriterCore, TextIO):
    r"""File-like interface for writing text data to items.

    It is important to either use this in a context manager or else
    call the :py:func:`close` method when writing is complete,
    otherwise the full contents of the file may not be written.

    Suggested usage::

        with item.open('w') as fp:
            fp.write('my item content, as much as I have\n')

    """

    def __init__(
        self, collection_id: str, version_id: str, item_id: str, client: CoreAuthClient
    ) -> None:
        super().__init__(collection_id, version_id, item_id, client)
        self._text_stream = io.TextIOWrapper(self._binary_stream)

    def __enter__(self) -> TextIO:
        return self._text_stream

    def __exit__(
        self,
        typ: Optional[type[BaseException]],
        val: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        self._text_stream.close()
        super().__exit__(typ, val, tb)

    def __iter__(self) -> Iterator[str]:
        raise OSError("cannot read")

    def __next__(self) -> str:
        raise OSError("cannot read")

    def read(self, n: int = -1) -> str:
        """N/A - cannot read

        Raises:
            OSError: always

        """
        raise OSError("cannot read")

    def readline(self, limit: int = -1) -> str:
        """N/A - cannot read

        Raises:
            OSError: always

        """
        raise OSError("cannot read")

    def readlines(self, hint: int = -1) -> list[str]:
        """N/A - cannot read

        Raises:
            OSError: always

        """
        raise OSError("cannot read")

    def write(self, s: str) -> int:
        """Write to the stream.

        Args:
            s: content to write

        Returns:
            number of characters written
        """
        return self._text_stream.write(s)

    def writelines(self, lines: Iterable[str]) -> None:
        """Write lines to the stream.

        Args:
            lines: iterable of lines (str) to write

        """
        return self._text_stream.writelines(lines)


class DelfiniItemCreatorCore(DelfiniItemWriterCore):
    def __init__(
        self,
        collection_id: str,
        version_id: str,
        item_name: str,
        client: CoreAuthClient,
        folder_id: str = "ROOT",
        type: Literal["file", "dataview", "dictionary"] = "file",
        columns: Optional[list[ItemColumn]] = None,
        metadata: Optional[dict[str, str]] = None,
        parser: Optional[ItemParser] = None,
        storage: Optional[ItemStorage] = None,
    ) -> None:
        self.item_name = item_name
        self.item_folder_id = folder_id
        self.item_type = type
        self.item_columns = columns
        self.item_metadata = metadata
        self.item_parser = parser
        self.item_storage = storage
        super().__init__(collection_id, version_id, "_pending_close", client)

    def _call_api(self, stream: BinaryIO) -> None:
        try:
            request = CollectionsItemsCreateItemFilesFormStyleUpload(
                content=File(payload=stream, file_name=self.item_name),
                folder_id=self.item_folder_id,
                type=ItemType[self.item_type.upper()],
                columns=self.item_columns if self.item_columns else UNSET,
                metadata=(
                    CollectionsItemsCreateItemFilesFormStyleUploadMetadata.from_dict(
                        self.item_metadata
                    )
                    if self.item_metadata
                    else UNSET
                ),
                parser=self.item_parser if self.item_parser else UNSET,
                storage=self.item_storage if self.item_storage else UNSET,
            )
            item = collections_items_create_item.sync(
                self.collection_id,
                self.version_id,
                body=request,
                client=self._client,
            )
            self.item_id = item.id
        except BaseException as e:
            print("caught exception:", e)
            self._exc = e


class DelfiniItemCreatorBinary(DelfiniItemCreatorCore, DelfiniItemWriterBinary):
    r"""File-like interface for creating a new item in binary mode.

    It is important to either use this in a context manager or else
    call the :py:func:`close` method when writing is complete,
    otherwise the full contents of the file may not be written.

    Suggested usage::

        with collection.open('new-item', 'wb') as fp:
            fp.write(b'my item content, as much as I have\n')

    """
    pass


class DelfiniItemCreatorText(DelfiniItemCreatorCore, DelfiniItemWriterText):
    r"""File-like interface for creating a new item in text mode.

    It is important to either use this in a context manager or else
    call the :py:func:`close` method when writing is complete,
    otherwise the full contents of the file may not be written.

    Suggested usage::

        with collection.open('new-item', 'w') as fp:
            fp.write('my item content, as much as I have\n')

    """
    pass


def new_empty_item(
    collection_id: str,
    version_id: str,
    name: str,
    type: Literal["file", "folder", "dataview", "dictionary"],
    client: CoreAuthClient,
    within_folder_id: str = "ROOT",
) -> Item:
    request = CollectionsItemsCreateItemJsonNewItemRequest(
        name=name,
        type=ItemType[type.upper()],
        folder_id=within_folder_id,
    )
    item = collections_items_create_item.sync(
        collection_id, version_id, body=request, client=client
    )
    return item


def new_folder(
    collection_id: str,
    version_id: str,
    name: str,
    client: CoreAuthClient,
    within_folder_id: str = "ROOT",
) -> Item:
    return new_empty_item(
        collection_id,
        version_id,
        name,
        "folder",
        client,
        within_folder_id=within_folder_id,
    )
