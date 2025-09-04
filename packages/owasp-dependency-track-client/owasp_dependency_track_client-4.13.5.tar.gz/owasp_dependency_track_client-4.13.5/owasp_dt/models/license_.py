from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.license_group import LicenseGroup


T = TypeVar("T", bound="License")


@_attrs_define
class License:
    """
    Attributes:
        uuid (UUID):
        license_groups (Union[Unset, list['LicenseGroup']]):
        name (Union[Unset, str]):
        license_text (Union[Unset, str]):
        standard_license_template (Union[Unset, str]):
        standard_license_header (Union[Unset, str]):
        license_comments (Union[Unset, str]):
        license_id (Union[Unset, str]):
        is_osi_approved (Union[Unset, bool]):
        is_fsf_libre (Union[Unset, bool]):
        is_deprecated_license_id (Union[Unset, bool]):
        is_custom_license (Union[Unset, bool]):
        see_also (Union[Unset, list[str]]):
    """

    uuid: UUID
    license_groups: Union[Unset, list["LicenseGroup"]] = UNSET
    name: Union[Unset, str] = UNSET
    license_text: Union[Unset, str] = UNSET
    standard_license_template: Union[Unset, str] = UNSET
    standard_license_header: Union[Unset, str] = UNSET
    license_comments: Union[Unset, str] = UNSET
    license_id: Union[Unset, str] = UNSET
    is_osi_approved: Union[Unset, bool] = UNSET
    is_fsf_libre: Union[Unset, bool] = UNSET
    is_deprecated_license_id: Union[Unset, bool] = UNSET
    is_custom_license: Union[Unset, bool] = UNSET
    see_also: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = str(self.uuid)

        license_groups: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.license_groups, Unset):
            license_groups = []
            for license_groups_item_data in self.license_groups:
                license_groups_item = license_groups_item_data.to_dict()
                license_groups.append(license_groups_item)

        name = self.name

        license_text = self.license_text

        standard_license_template = self.standard_license_template

        standard_license_header = self.standard_license_header

        license_comments = self.license_comments

        license_id = self.license_id

        is_osi_approved = self.is_osi_approved

        is_fsf_libre = self.is_fsf_libre

        is_deprecated_license_id = self.is_deprecated_license_id

        is_custom_license = self.is_custom_license

        see_also: Union[Unset, list[str]] = UNSET
        if not isinstance(self.see_also, Unset):
            see_also = self.see_also

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
            }
        )
        if license_groups is not UNSET:
            field_dict["licenseGroups"] = license_groups
        if name is not UNSET:
            field_dict["name"] = name
        if license_text is not UNSET:
            field_dict["licenseText"] = license_text
        if standard_license_template is not UNSET:
            field_dict["standardLicenseTemplate"] = standard_license_template
        if standard_license_header is not UNSET:
            field_dict["standardLicenseHeader"] = standard_license_header
        if license_comments is not UNSET:
            field_dict["licenseComments"] = license_comments
        if license_id is not UNSET:
            field_dict["licenseId"] = license_id
        if is_osi_approved is not UNSET:
            field_dict["isOsiApproved"] = is_osi_approved
        if is_fsf_libre is not UNSET:
            field_dict["isFsfLibre"] = is_fsf_libre
        if is_deprecated_license_id is not UNSET:
            field_dict["isDeprecatedLicenseId"] = is_deprecated_license_id
        if is_custom_license is not UNSET:
            field_dict["isCustomLicense"] = is_custom_license
        if see_also is not UNSET:
            field_dict["seeAlso"] = see_also

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.license_group import LicenseGroup

        d = dict(src_dict)
        uuid = UUID(d.pop("uuid"))

        license_groups = []
        _license_groups = d.pop("licenseGroups", UNSET)
        for license_groups_item_data in _license_groups or []:
            license_groups_item = LicenseGroup.from_dict(license_groups_item_data)

            license_groups.append(license_groups_item)

        name = d.pop("name", UNSET)

        license_text = d.pop("licenseText", UNSET)

        standard_license_template = d.pop("standardLicenseTemplate", UNSET)

        standard_license_header = d.pop("standardLicenseHeader", UNSET)

        license_comments = d.pop("licenseComments", UNSET)

        license_id = d.pop("licenseId", UNSET)

        is_osi_approved = d.pop("isOsiApproved", UNSET)

        is_fsf_libre = d.pop("isFsfLibre", UNSET)

        is_deprecated_license_id = d.pop("isDeprecatedLicenseId", UNSET)

        is_custom_license = d.pop("isCustomLicense", UNSET)

        see_also = cast(list[str], d.pop("seeAlso", UNSET))

        license_ = cls(
            uuid=uuid,
            license_groups=license_groups,
            name=name,
            license_text=license_text,
            standard_license_template=standard_license_template,
            standard_license_header=standard_license_header,
            license_comments=license_comments,
            license_id=license_id,
            is_osi_approved=is_osi_approved,
            is_fsf_libre=is_fsf_libre,
            is_deprecated_license_id=is_deprecated_license_id,
            is_custom_license=is_custom_license,
            see_also=see_also,
        )

        license_.additional_properties = d
        return license_

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
