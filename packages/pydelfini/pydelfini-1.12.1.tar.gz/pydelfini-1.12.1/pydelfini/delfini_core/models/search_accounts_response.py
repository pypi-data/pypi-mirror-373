from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.pagination import Pagination
from ..models.search_accounts_response_hits_item import SearchAccountsResponseHitsItem
from ..models.termset import Termset


T = TypeVar("T", bound="SearchAccountsResponse")


@_attrs_define
class SearchAccountsResponse:
    """SearchAccountsResponse model

    Attributes:
        hits (List['SearchAccountsResponseHitsItem']):
        metadata_terms (Termset):
        pagination (Pagination):
        search_terms (Termset):
    """

    hits: List["SearchAccountsResponseHitsItem"]
    metadata_terms: "Termset"
    pagination: "Pagination"
    search_terms: "Termset"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        hits = []
        for hits_item_data in self.hits:
            hits_item = hits_item_data.to_dict()
            hits.append(hits_item)

        metadata_terms = self.metadata_terms.to_dict()
        pagination = self.pagination.to_dict()
        search_terms = self.search_terms.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "hits": hits,
                "metadataTerms": metadata_terms,
                "pagination": pagination,
                "searchTerms": search_terms,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchAccountsResponse` from a dict"""
        d = src_dict.copy()
        hits = []
        _hits = d.pop("hits")
        for hits_item_data in _hits:
            hits_item = SearchAccountsResponseHitsItem.from_dict(hits_item_data)

            hits.append(hits_item)

        metadata_terms = Termset.from_dict(d.pop("metadataTerms"))

        pagination = Pagination.from_dict(d.pop("pagination"))

        search_terms = Termset.from_dict(d.pop("searchTerms"))

        search_accounts_response = cls(
            hits=hits,
            metadata_terms=metadata_terms,
            pagination=pagination,
            search_terms=search_terms,
        )

        return search_accounts_response
