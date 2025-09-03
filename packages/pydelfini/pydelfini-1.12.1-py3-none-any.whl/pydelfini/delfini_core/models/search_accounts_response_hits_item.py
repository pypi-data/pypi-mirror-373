from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.account import Account
from ..models.highlights import Highlights
from ..models.search_accounts_response_hits_item_projects_item import (
    SearchAccountsResponseHitsItemProjectsItem,
)


T = TypeVar("T", bound="SearchAccountsResponseHitsItem")


@_attrs_define
class SearchAccountsResponseHitsItem:
    """SearchAccountsResponseHitsItem model

    Attributes:
        account (Account):
        highlights (Highlights):
        projects (List['SearchAccountsResponseHitsItemProjectsItem']):
        score (float):
    """

    account: "Account"
    highlights: "Highlights"
    projects: List["SearchAccountsResponseHitsItemProjectsItem"]
    score: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        account = self.account.to_dict()
        highlights = self.highlights.to_dict()
        projects = []
        for projects_item_data in self.projects:
            projects_item = projects_item_data.to_dict()
            projects.append(projects_item)

        score = self.score

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "account": account,
                "highlights": highlights,
                "projects": projects,
                "score": score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`SearchAccountsResponseHitsItem` from a dict"""
        d = src_dict.copy()
        account = Account.from_dict(d.pop("account"))

        highlights = Highlights.from_dict(d.pop("highlights"))

        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = SearchAccountsResponseHitsItemProjectsItem.from_dict(
                projects_item_data
            )

            projects.append(projects_item)

        score = d.pop("score")

        search_accounts_response_hits_item = cls(
            account=account,
            highlights=highlights,
            projects=projects,
            score=score,
        )

        return search_accounts_response_hits_item
