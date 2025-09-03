from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define


T = TypeVar("T", bound="CollectionMoveDatastore")


@_attrs_define
class CollectionMoveDatastore:
    """CollectionMoveDatastore model

    Attributes:
        destination_datastore (str):
    """

    destination_datastore: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        destination_datastore = self.destination_datastore

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "destinationDatastore": destination_datastore,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionMoveDatastore` from a dict"""
        d = src_dict.copy()
        destination_datastore = d.pop("destinationDatastore")

        collection_move_datastore = cls(
            destination_datastore=destination_datastore,
        )

        return collection_move_datastore
