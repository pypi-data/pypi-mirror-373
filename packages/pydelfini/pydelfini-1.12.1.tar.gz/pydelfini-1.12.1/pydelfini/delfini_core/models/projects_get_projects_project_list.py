from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.pagination import Pagination
from ..models.project import Project


T = TypeVar("T", bound="ProjectsGetProjectsProjectList")


@_attrs_define
class ProjectsGetProjectsProjectList:
    """ProjectsGetProjectsProjectList model

    Attributes:
        pagination (Pagination):
        projects (List['Project']):
    """

    pagination: "Pagination"
    projects: List["Project"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        pagination = self.pagination.to_dict()
        projects = []
        for projects_item_data in self.projects:
            projects_item = projects_item_data.to_dict()
            projects.append(projects_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "pagination": pagination,
                "projects": projects,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`ProjectsGetProjectsProjectList` from a dict"""
        d = src_dict.copy()
        pagination = Pagination.from_dict(d.pop("pagination"))

        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = Project.from_dict(projects_item_data)

            projects.append(projects_item)

        projects_get_projects_project_list = cls(
            pagination=pagination,
            projects=projects,
        )

        return projects_get_projects_project_list
