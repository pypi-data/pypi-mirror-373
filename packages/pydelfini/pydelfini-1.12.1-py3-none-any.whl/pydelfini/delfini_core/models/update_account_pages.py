from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="UpdateAccountPages")


@_attrs_define
class UpdateAccountPages:
    """UpdateAccountPages model

    Attributes:
        collection_id (str):
        item_ids (List[str]):
        version_id (str):
    """

    collection_id: str
    item_ids: List[str]
    version_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        collection_id = self.collection_id
        item_ids = self.item_ids

        version_id = self.version_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "collection_id": collection_id,
                "item_ids": item_ids,
                "version_id": version_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`UpdateAccountPages` from a dict"""
        d = src_dict.copy()
        collection_id = d.pop("collection_id")

        item_ids = cast(List[str], d.pop("item_ids"))

        version_id = d.pop("version_id")

        update_account_pages = cls(
            collection_id=collection_id,
            item_ids=item_ids,
            version_id=version_id,
        )

        return update_account_pages
