from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.collection_authorization_remove_identity import (
    CollectionAuthorizationRemoveIdentity,
)
from ..models.collection_authorization_set_identity import (
    CollectionAuthorizationSetIdentity,
)
from ..models.collection_authorization_update_access_level import (
    CollectionAuthorizationUpdateAccessLevel,
)


T = TypeVar("T", bound="CollectionAuthorizationChange")


@_attrs_define
class CollectionAuthorizationChange:
    """CollectionAuthorizationChange model

    Attributes:
        req (Union['CollectionAuthorizationRemoveIdentity', 'CollectionAuthorizationSetIdentity',
            'CollectionAuthorizationUpdateAccessLevel']):
    """

    req: Union[
        "CollectionAuthorizationRemoveIdentity",
        "CollectionAuthorizationSetIdentity",
        "CollectionAuthorizationUpdateAccessLevel",
    ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        req: Dict[str, Any]
        if isinstance(self.req, CollectionAuthorizationSetIdentity):
            req = self.req.to_dict()
        elif isinstance(self.req, CollectionAuthorizationRemoveIdentity):
            req = self.req.to_dict()
        else:
            req = self.req.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "req": req,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionAuthorizationChange` from a dict"""
        d = src_dict.copy()

        def _parse_req(
            data: object,
        ) -> Union[
            "CollectionAuthorizationRemoveIdentity",
            "CollectionAuthorizationSetIdentity",
            "CollectionAuthorizationUpdateAccessLevel",
        ]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                req_type_0 = CollectionAuthorizationSetIdentity.from_dict(data)

                return req_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                req_type_1 = CollectionAuthorizationRemoveIdentity.from_dict(data)

                return req_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            req_type_2 = CollectionAuthorizationUpdateAccessLevel.from_dict(data)

            return req_type_2

        req = _parse_req(d.pop("req"))

        collection_authorization_change = cls(
            req=req,
        )

        return collection_authorization_change
