from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.analysis_analysis_justification import AnalysisAnalysisJustification
from ..models.analysis_analysis_response import AnalysisAnalysisResponse
from ..models.analysis_analysis_state import AnalysisAnalysisState
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.analysis_comment import AnalysisComment


T = TypeVar("T", bound="Analysis")


@_attrs_define
class Analysis:
    """
    Attributes:
        analysis_state (Union[Unset, AnalysisAnalysisState]):
        analysis_justification (Union[Unset, AnalysisAnalysisJustification]):
        analysis_response (Union[Unset, AnalysisAnalysisResponse]):
        analysis_details (Union[Unset, str]):
        analysis_comments (Union[Unset, list['AnalysisComment']]):
        is_suppressed (Union[Unset, bool]):
    """

    analysis_state: Union[Unset, AnalysisAnalysisState] = UNSET
    analysis_justification: Union[Unset, AnalysisAnalysisJustification] = UNSET
    analysis_response: Union[Unset, AnalysisAnalysisResponse] = UNSET
    analysis_details: Union[Unset, str] = UNSET
    analysis_comments: Union[Unset, list["AnalysisComment"]] = UNSET
    is_suppressed: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        analysis_state: Union[Unset, str] = UNSET
        if not isinstance(self.analysis_state, Unset):
            analysis_state = self.analysis_state.value

        analysis_justification: Union[Unset, str] = UNSET
        if not isinstance(self.analysis_justification, Unset):
            analysis_justification = self.analysis_justification.value

        analysis_response: Union[Unset, str] = UNSET
        if not isinstance(self.analysis_response, Unset):
            analysis_response = self.analysis_response.value

        analysis_details = self.analysis_details

        analysis_comments: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.analysis_comments, Unset):
            analysis_comments = []
            for analysis_comments_item_data in self.analysis_comments:
                analysis_comments_item = analysis_comments_item_data.to_dict()
                analysis_comments.append(analysis_comments_item)

        is_suppressed = self.is_suppressed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if analysis_state is not UNSET:
            field_dict["analysisState"] = analysis_state
        if analysis_justification is not UNSET:
            field_dict["analysisJustification"] = analysis_justification
        if analysis_response is not UNSET:
            field_dict["analysisResponse"] = analysis_response
        if analysis_details is not UNSET:
            field_dict["analysisDetails"] = analysis_details
        if analysis_comments is not UNSET:
            field_dict["analysisComments"] = analysis_comments
        if is_suppressed is not UNSET:
            field_dict["isSuppressed"] = is_suppressed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.analysis_comment import AnalysisComment

        d = dict(src_dict)
        _analysis_state = d.pop("analysisState", UNSET)
        analysis_state: Union[Unset, AnalysisAnalysisState]
        if isinstance(_analysis_state, Unset):
            analysis_state = UNSET
        else:
            analysis_state = AnalysisAnalysisState(_analysis_state)

        _analysis_justification = d.pop("analysisJustification", UNSET)
        analysis_justification: Union[Unset, AnalysisAnalysisJustification]
        if isinstance(_analysis_justification, Unset):
            analysis_justification = UNSET
        else:
            analysis_justification = AnalysisAnalysisJustification(
                _analysis_justification
            )

        _analysis_response = d.pop("analysisResponse", UNSET)
        analysis_response: Union[Unset, AnalysisAnalysisResponse]
        if isinstance(_analysis_response, Unset):
            analysis_response = UNSET
        else:
            analysis_response = AnalysisAnalysisResponse(_analysis_response)

        analysis_details = d.pop("analysisDetails", UNSET)

        analysis_comments = []
        _analysis_comments = d.pop("analysisComments", UNSET)
        for analysis_comments_item_data in _analysis_comments or []:
            analysis_comments_item = AnalysisComment.from_dict(
                analysis_comments_item_data
            )

            analysis_comments.append(analysis_comments_item)

        is_suppressed = d.pop("isSuppressed", UNSET)

        analysis = cls(
            analysis_state=analysis_state,
            analysis_justification=analysis_justification,
            analysis_response=analysis_response,
            analysis_details=analysis_details,
            analysis_comments=analysis_comments,
            is_suppressed=is_suppressed,
        )

        analysis.additional_properties = d
        return analysis

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
