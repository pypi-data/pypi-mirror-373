from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.datastore import Datastore


T = TypeVar("T", bound="RootGetDatastoresResponse200")


@_attrs_define
class RootGetDatastoresResponse200:
    """RootGetDatastoresResponse200 model

    Attributes:
        datastores (List['Datastore']):
    """

    datastores: List["Datastore"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        datastores = []
        for datastores_item_data in self.datastores:
            datastores_item = datastores_item_data.to_dict()
            datastores.append(datastores_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "datastores": datastores,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`RootGetDatastoresResponse200` from a dict"""
        d = src_dict.copy()
        datastores = []
        _datastores = d.pop("datastores")
        for datastores_item_data in _datastores:
            datastores_item = Datastore.from_dict(datastores_item_data)

            datastores.append(datastores_item)

        root_get_datastores_response_200 = cls(
            datastores=datastores,
        )

        return root_get_datastores_response_200
