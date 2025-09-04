from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.repository_meta_component_repository_type import (
    RepositoryMetaComponentRepositoryType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="RepositoryMetaComponent")


@_attrs_define
class RepositoryMetaComponent:
    """
    Attributes:
        repository_type (RepositoryMetaComponentRepositoryType):
        name (str):
        latest_version (str):
        published (int): UNIX epoch timestamp in milliseconds
        last_check (int): UNIX epoch timestamp in milliseconds
        namespace (Union[Unset, str]):
    """

    repository_type: RepositoryMetaComponentRepositoryType
    name: str
    latest_version: str
    published: int
    last_check: int
    namespace: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository_type = self.repository_type.value

        name = self.name

        latest_version = self.latest_version

        published = self.published

        last_check = self.last_check

        namespace = self.namespace

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repositoryType": repository_type,
                "name": name,
                "latestVersion": latest_version,
                "published": published,
                "lastCheck": last_check,
            }
        )
        if namespace is not UNSET:
            field_dict["namespace"] = namespace

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repository_type = RepositoryMetaComponentRepositoryType(d.pop("repositoryType"))

        name = d.pop("name")

        latest_version = d.pop("latestVersion")

        published = d.pop("published")

        last_check = d.pop("lastCheck")

        namespace = d.pop("namespace", UNSET)

        repository_meta_component = cls(
            repository_type=repository_type,
            name=name,
            latest_version=latest_version,
            published=published,
            last_check=last_check,
            namespace=namespace,
        )

        repository_meta_component.additional_properties = d
        return repository_meta_component

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
