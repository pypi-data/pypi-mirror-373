from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionsItemsCopyItemBody")


@_attrs_define
class CollectionsItemsCopyItemBody:
    """CollectionsItemsCopyItemBody model

    Attributes:
        source_url (str):  Example: delfini://example.com/collection/version/item-id.
        folder_id (Union[Unset, str]):  Example: ROOT.
        name (Union[Unset, str]):
    """

    source_url: str
    folder_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        source_url = self.source_url
        folder_id = self.folder_id
        name = self.name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "sourceUrl": source_url,
            }
        )
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionsItemsCopyItemBody` from a dict"""
        d = src_dict.copy()
        source_url = d.pop("sourceUrl")

        folder_id = d.pop("folderId", UNSET)

        name = d.pop("name", UNSET)

        collections_items_copy_item_body = cls(
            source_url=source_url,
            folder_id=folder_id,
            name=name,
        )

        return collections_items_copy_item_body
