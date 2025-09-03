from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

from attrs import define as _attrs_define

from ..models.prql_module import PrqlModule


T = TypeVar("T", bound="ParsersResolvePrqlModulesResponse200")


@_attrs_define
class ParsersResolvePrqlModulesResponse200:
    """ParsersResolvePrqlModulesResponse200 model

    Attributes:
        modules (List['PrqlModule']):
    """

    modules: List["PrqlModule"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        modules = []
        for modules_item_data in self.modules:
            modules_item = modules_item_data.to_dict()
            modules.append(modules_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "modules": modules,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`ParsersResolvePrqlModulesResponse200` from a dict"""
        d = src_dict.copy()
        modules = []
        _modules = d.pop("modules")
        for modules_item_data in _modules:
            modules_item = PrqlModule.from_dict(modules_item_data)

            modules.append(modules_item)

        parsers_resolve_prql_modules_response_200 = cls(
            modules=modules,
        )

        return parsers_resolve_prql_modules_response_200
