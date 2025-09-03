from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.task_result import TaskResult


T = TypeVar("T", bound="TasksResults")


@_attrs_define
class TasksResults:
    """TasksResults model

    Attributes:
        results (List['TaskResult']):
    """

    results: List["TaskResult"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "results": results,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`TasksResults` from a dict"""
        d = src_dict.copy()
        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = TaskResult.from_dict(results_item_data)

            results.append(results_item)

        tasks_results = cls(
            results=results,
        )

        return tasks_results
