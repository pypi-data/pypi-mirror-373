from typing import Any
from typing import Dict
from typing import Type
from typing import TypeVar
from typing import Union

from attrs import define as _attrs_define

from ..types import UNSET
from ..types import Unset


T = TypeVar("T", bound="QueryDataElementRequest")


@_attrs_define
class QueryDataElementRequest:
    """QueryDataElementRequest model

    Attributes:
        query (str):
        parser_name (Union[Unset, str]):
    """

    query: str
    parser_name: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dict"""
        query = self.query
        parser_name = self.parser_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "query": query,
            }
        )
        if parser_name is not UNSET:
            field_dict["parserName"] = parser_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Create an instance of :py:class:`QueryDataElementRequest` from a dict"""
        d = src_dict.copy()
        query = d.pop("query")

        parser_name = d.pop("parserName", UNSET)

        query_data_element_request = cls(
            query=query,
            parser_name=parser_name,
        )

        return query_data_element_request
