from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.analysis_request_analysis_justification import (
    AnalysisRequestAnalysisJustification,
)
from ..models.analysis_request_analysis_response import AnalysisRequestAnalysisResponse
from ..models.analysis_request_analysis_state import AnalysisRequestAnalysisState
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnalysisRequest")


@_attrs_define
class AnalysisRequest:
    """
    Attributes:
        component (str):
        vulnerability (str):
        project (Union[Unset, str]):
        analysis_state (Union[Unset, AnalysisRequestAnalysisState]):
        analysis_justification (Union[Unset, AnalysisRequestAnalysisJustification]):
        analysis_response (Union[Unset, AnalysisRequestAnalysisResponse]):
        analysis_details (Union[Unset, str]):
        comment (Union[Unset, str]):
        is_suppressed (Union[Unset, bool]):
        suppressed (Union[Unset, bool]):
    """

    component: str
    vulnerability: str
    project: Union[Unset, str] = UNSET
    analysis_state: Union[Unset, AnalysisRequestAnalysisState] = UNSET
    analysis_justification: Union[Unset, AnalysisRequestAnalysisJustification] = UNSET
    analysis_response: Union[Unset, AnalysisRequestAnalysisResponse] = UNSET
    analysis_details: Union[Unset, str] = UNSET
    comment: Union[Unset, str] = UNSET
    is_suppressed: Union[Unset, bool] = UNSET
    suppressed: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        component = self.component

        vulnerability = self.vulnerability

        project = self.project

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

        comment = self.comment

        is_suppressed = self.is_suppressed

        suppressed = self.suppressed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "component": component,
                "vulnerability": vulnerability,
            }
        )
        if project is not UNSET:
            field_dict["project"] = project
        if analysis_state is not UNSET:
            field_dict["analysisState"] = analysis_state
        if analysis_justification is not UNSET:
            field_dict["analysisJustification"] = analysis_justification
        if analysis_response is not UNSET:
            field_dict["analysisResponse"] = analysis_response
        if analysis_details is not UNSET:
            field_dict["analysisDetails"] = analysis_details
        if comment is not UNSET:
            field_dict["comment"] = comment
        if is_suppressed is not UNSET:
            field_dict["isSuppressed"] = is_suppressed
        if suppressed is not UNSET:
            field_dict["suppressed"] = suppressed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        component = d.pop("component")

        vulnerability = d.pop("vulnerability")

        project = d.pop("project", UNSET)

        _analysis_state = d.pop("analysisState", UNSET)
        analysis_state: Union[Unset, AnalysisRequestAnalysisState]
        if isinstance(_analysis_state, Unset):
            analysis_state = UNSET
        else:
            analysis_state = AnalysisRequestAnalysisState(_analysis_state)

        _analysis_justification = d.pop("analysisJustification", UNSET)
        analysis_justification: Union[Unset, AnalysisRequestAnalysisJustification]
        if isinstance(_analysis_justification, Unset):
            analysis_justification = UNSET
        else:
            analysis_justification = AnalysisRequestAnalysisJustification(
                _analysis_justification
            )

        _analysis_response = d.pop("analysisResponse", UNSET)
        analysis_response: Union[Unset, AnalysisRequestAnalysisResponse]
        if isinstance(_analysis_response, Unset):
            analysis_response = UNSET
        else:
            analysis_response = AnalysisRequestAnalysisResponse(_analysis_response)

        analysis_details = d.pop("analysisDetails", UNSET)

        comment = d.pop("comment", UNSET)

        is_suppressed = d.pop("isSuppressed", UNSET)

        suppressed = d.pop("suppressed", UNSET)

        analysis_request = cls(
            component=component,
            vulnerability=vulnerability,
            project=project,
            analysis_state=analysis_state,
            analysis_justification=analysis_justification,
            analysis_response=analysis_response,
            analysis_details=analysis_details,
            comment=comment,
            is_suppressed=is_suppressed,
            suppressed=suppressed,
        )

        analysis_request.additional_properties = d
        return analysis_request

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
