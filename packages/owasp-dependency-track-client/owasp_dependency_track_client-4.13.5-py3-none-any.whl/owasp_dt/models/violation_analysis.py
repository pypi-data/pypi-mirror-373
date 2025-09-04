from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.violation_analysis_analysis_state import ViolationAnalysisAnalysisState
from ..models.violation_analysis_violation_analysis_state import (
    ViolationAnalysisViolationAnalysisState,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.violation_analysis_comment import ViolationAnalysisComment


T = TypeVar("T", bound="ViolationAnalysis")


@_attrs_define
class ViolationAnalysis:
    """
    Attributes:
        analysis_state (ViolationAnalysisAnalysisState):
        analysis_comments (Union[Unset, list['ViolationAnalysisComment']]):
        violation_analysis_state (Union[Unset, ViolationAnalysisViolationAnalysisState]):
        is_suppressed (Union[Unset, bool]):
    """

    analysis_state: ViolationAnalysisAnalysisState
    analysis_comments: Union[Unset, list["ViolationAnalysisComment"]] = UNSET
    violation_analysis_state: Union[Unset, ViolationAnalysisViolationAnalysisState] = (
        UNSET
    )
    is_suppressed: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        analysis_state = self.analysis_state.value

        analysis_comments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.analysis_comments, Unset):
            analysis_comments = []
            for analysis_comments_item_data in self.analysis_comments:
                analysis_comments_item = analysis_comments_item_data.to_dict()
                analysis_comments.append(analysis_comments_item)

        violation_analysis_state: Union[Unset, str] = UNSET
        if not isinstance(self.violation_analysis_state, Unset):
            violation_analysis_state = self.violation_analysis_state.value

        is_suppressed = self.is_suppressed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "analysisState": analysis_state,
            }
        )
        if analysis_comments is not UNSET:
            field_dict["analysisComments"] = analysis_comments
        if violation_analysis_state is not UNSET:
            field_dict["violationAnalysisState"] = violation_analysis_state
        if is_suppressed is not UNSET:
            field_dict["isSuppressed"] = is_suppressed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.violation_analysis_comment import ViolationAnalysisComment

        d = dict(src_dict)
        analysis_state = ViolationAnalysisAnalysisState(d.pop("analysisState"))

        analysis_comments = []
        _analysis_comments = d.pop("analysisComments", UNSET)
        for analysis_comments_item_data in _analysis_comments or []:
            analysis_comments_item = ViolationAnalysisComment.from_dict(
                analysis_comments_item_data
            )

            analysis_comments.append(analysis_comments_item)

        _violation_analysis_state = d.pop("violationAnalysisState", UNSET)
        violation_analysis_state: Union[Unset, ViolationAnalysisViolationAnalysisState]
        if isinstance(_violation_analysis_state, Unset):
            violation_analysis_state = UNSET
        else:
            violation_analysis_state = ViolationAnalysisViolationAnalysisState(
                _violation_analysis_state
            )

        is_suppressed = d.pop("isSuppressed", UNSET)

        violation_analysis = cls(
            analysis_state=analysis_state,
            analysis_comments=analysis_comments,
            violation_analysis_state=violation_analysis_state,
            is_suppressed=is_suppressed,
        )

        violation_analysis.additional_properties = d
        return violation_analysis

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
