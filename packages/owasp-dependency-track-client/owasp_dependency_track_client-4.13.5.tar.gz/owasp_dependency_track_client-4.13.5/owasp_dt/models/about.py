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
    from ..models.framework import Framework


T = TypeVar("T", bound="About")


@_attrs_define
class About:
    """
    Attributes:
        version (Union[Unset, str]):
        timestamp (Union[Unset, str]):
        system_uuid (Union[Unset, str]):
        uuid (Union[Unset, str]):
        application (Union[Unset, str]):
        framework (Union[Unset, Framework]):
    """

    version: Union[Unset, str] = UNSET
    timestamp: Union[Unset, str] = UNSET
    system_uuid: Union[Unset, str] = UNSET
    uuid: Union[Unset, str] = UNSET
    application: Union[Unset, str] = UNSET
    framework: Union[Unset, "Framework"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        timestamp = self.timestamp

        system_uuid = self.system_uuid

        uuid = self.uuid

        application = self.application

        framework: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.framework, Unset):
            framework = self.framework.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version is not UNSET:
            field_dict["version"] = version
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if system_uuid is not UNSET:
            field_dict["systemUuid"] = system_uuid
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if application is not UNSET:
            field_dict["application"] = application
        if framework is not UNSET:
            field_dict["framework"] = framework

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.framework import Framework

        d = dict(src_dict)
        version = d.pop("version", UNSET)

        timestamp = d.pop("timestamp", UNSET)

        system_uuid = d.pop("systemUuid", UNSET)

        uuid = d.pop("uuid", UNSET)

        application = d.pop("application", UNSET)

        _framework = d.pop("framework", UNSET)
        framework: Union[Unset, Framework]
        if isinstance(_framework, Unset):
            framework = UNSET
        else:
            framework = Framework.from_dict(_framework)

        about = cls(
            version=version,
            timestamp=timestamp,
            system_uuid=system_uuid,
            uuid=uuid,
            application=application,
            framework=framework,
        )

        about.additional_properties = d
        return about

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
