from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_result_results import SearchResultResults


T = TypeVar("T", bound="SearchResult")


@_attrs_define
class SearchResult:
    """
    Attributes:
        results (Union[Unset, SearchResultResults]):
    """

    results: Union[Unset, "SearchResultResults"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        results: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.results, Unset):
            results = self.results.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if results is not UNSET:
            field_dict["results"] = results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_result_results import SearchResultResults

        d = dict(src_dict)
        _results = d.pop("results", UNSET)
        results: Union[Unset, SearchResultResults]
        if isinstance(_results, Unset):
            results = UNSET
        else:
            results = SearchResultResults.from_dict(_results)

        search_result = cls(
            results=results,
        )

        search_result.additional_properties = d
        return search_result

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
