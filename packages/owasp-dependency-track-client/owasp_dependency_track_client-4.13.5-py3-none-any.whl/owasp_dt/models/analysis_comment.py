from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AnalysisComment")


@_attrs_define
class AnalysisComment:
    """
    Attributes:
        timestamp (int): UNIX epoch timestamp in milliseconds
        comment (str):
        commenter (Union[Unset, str]):
    """

    timestamp: int
    comment: str
    commenter: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp = self.timestamp

        comment = self.comment

        commenter = self.commenter

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timestamp": timestamp,
                "comment": comment,
            }
        )
        if commenter is not UNSET:
            field_dict["commenter"] = commenter

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        timestamp = d.pop("timestamp")

        comment = d.pop("comment")

        commenter = d.pop("commenter", UNSET)

        analysis_comment = cls(
            timestamp=timestamp,
            comment=comment,
            commenter=commenter,
        )

        analysis_comment.additional_properties = d
        return analysis_comment

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
