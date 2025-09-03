from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..models.collection_authorization_grant import CollectionAuthorizationGrant
from ..models.collection_authorization_inherited import CollectionAuthorizationInherited
from ..models.collection_authorization_permit import CollectionAuthorizationPermit
from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="CollectionAuthorization")


@_attrs_define
class CollectionAuthorization:
    """CollectionAuthorization model

    Attributes:
        controlled_access_groups (List[str]):
        myself (CollectionAuthorizationGrant):
        public (CollectionAuthorizationGrant):
        inherited (Union[Unset, CollectionAuthorizationInherited]):
        permit (Union[Unset, CollectionAuthorizationPermit]):
    """

    controlled_access_groups: List[str]
    myself: "CollectionAuthorizationGrant"
    public: "CollectionAuthorizationGrant"
    inherited: Union[Unset, "CollectionAuthorizationInherited"] = UNSET
    permit: Union[Unset, "CollectionAuthorizationPermit"] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        controlled_access_groups = self.controlled_access_groups

        myself = self.myself.to_dict()
        public = self.public.to_dict()
        inherited: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.inherited, Unset):
            inherited = self.inherited.to_dict()
        permit: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.permit, Unset):
            permit = self.permit.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "controlledAccessGroups": controlled_access_groups,
                "myself": myself,
                "public": public,
            }
        )
        if inherited is not UNSET:
            field_dict["inherited"] = inherited
        if permit is not UNSET:
            field_dict["permit"] = permit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`CollectionAuthorization` from a dict"""
        d = src_dict.copy()
        controlled_access_groups = cast(List[str], d.pop("controlledAccessGroups"))

        myself = CollectionAuthorizationGrant.from_dict(d.pop("myself"))

        public = CollectionAuthorizationGrant.from_dict(d.pop("public"))

        _inherited = d.pop("inherited", UNSET)
        inherited: Union[Unset, CollectionAuthorizationInherited]
        if isinstance(_inherited, Unset):
            inherited = UNSET
        else:
            inherited = CollectionAuthorizationInherited.from_dict(_inherited)

        _permit = d.pop("permit", UNSET)
        permit: Union[Unset, CollectionAuthorizationPermit]
        if isinstance(_permit, Unset):
            permit = UNSET
        else:
            permit = CollectionAuthorizationPermit.from_dict(_permit)

        collection_authorization = cls(
            controlled_access_groups=controlled_access_groups,
            myself=myself,
            public=public,
            inherited=inherited,
            permit=permit,
        )

        return collection_authorization
