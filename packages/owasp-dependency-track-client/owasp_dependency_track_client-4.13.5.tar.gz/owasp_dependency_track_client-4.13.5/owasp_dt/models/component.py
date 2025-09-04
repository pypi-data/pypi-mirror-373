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

from ..models.component_classifier import ComponentClassifier
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.component_property import ComponentProperty
    from ..models.dependency_metrics import DependencyMetrics
    from ..models.external_reference import ExternalReference
    from ..models.license_ import License
    from ..models.organizational_contact import OrganizationalContact
    from ..models.organizational_entity import OrganizationalEntity
    from ..models.project import Project
    from ..models.repository_meta_component import RepositoryMetaComponent
    from ..models.vulnerability import Vulnerability


T = TypeVar("T", bound="Component")


@_attrs_define
class Component:
    """
    Attributes:
        project (Project):
        uuid (UUID):
        authors (Union[Unset, list['OrganizationalContact']]):
        publisher (Union[Unset, str]):
        supplier (Union[Unset, OrganizationalEntity]):
        group (Union[Unset, str]):
        name (Union[Unset, str]):
        version (Union[Unset, str]):
        classifier (Union[Unset, ComponentClassifier]):
        filename (Union[Unset, str]):
        extension (Union[Unset, str]):
        md5 (Union[Unset, str]):
        sha1 (Union[Unset, str]):
        sha256 (Union[Unset, str]):
        sha384 (Union[Unset, str]):
        sha512 (Union[Unset, str]):
        sha3_256 (Union[Unset, str]):
        sha3_384 (Union[Unset, str]):
        sha3_512 (Union[Unset, str]):
        blake2b_256 (Union[Unset, str]):
        blake2b_384 (Union[Unset, str]):
        blake2b_512 (Union[Unset, str]):
        blake3 (Union[Unset, str]):
        cpe (Union[Unset, str]):
        purl (Union[Unset, str]):
        purl_coordinates (Union[Unset, str]):
        swid_tag_id (Union[Unset, str]):
        description (Union[Unset, str]):
        copyright_ (Union[Unset, str]):
        license_ (Union[Unset, str]):
        license_expression (Union[Unset, str]):
        license_url (Union[Unset, str]):
        resolved_license (Union[Unset, License]):
        direct_dependencies (Union[Unset, str]):
        external_references (Union[Unset, list['ExternalReference']]):
        parent (Union[Unset, Component]):
        children (Union[Unset, list['Component']]):
        properties (Union[Unset, list['ComponentProperty']]):
        vulnerabilities (Union[Unset, list['Vulnerability']]):
        last_inherited_risk_score (Union[Unset, float]):
        notes (Union[Unset, str]):
        author (Union[Unset, str]):
        metrics (Union[Unset, DependencyMetrics]):
        repository_meta (Union[Unset, RepositoryMetaComponent]):
        dependency_graph (Union[Unset, list[str]]):
        expand_dependency_graph (Union[Unset, bool]):
        is_internal (Union[Unset, bool]):
    """

    project: "Project"
    uuid: UUID
    authors: Union[Unset, list["OrganizationalContact"]] = UNSET
    publisher: Union[Unset, str] = UNSET
    supplier: Union[Unset, "OrganizationalEntity"] = UNSET
    group: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    classifier: Union[Unset, ComponentClassifier] = UNSET
    filename: Union[Unset, str] = UNSET
    extension: Union[Unset, str] = UNSET
    md5: Union[Unset, str] = UNSET
    sha1: Union[Unset, str] = UNSET
    sha256: Union[Unset, str] = UNSET
    sha384: Union[Unset, str] = UNSET
    sha512: Union[Unset, str] = UNSET
    sha3_256: Union[Unset, str] = UNSET
    sha3_384: Union[Unset, str] = UNSET
    sha3_512: Union[Unset, str] = UNSET
    blake2b_256: Union[Unset, str] = UNSET
    blake2b_384: Union[Unset, str] = UNSET
    blake2b_512: Union[Unset, str] = UNSET
    blake3: Union[Unset, str] = UNSET
    cpe: Union[Unset, str] = UNSET
    purl: Union[Unset, str] = UNSET
    purl_coordinates: Union[Unset, str] = UNSET
    swid_tag_id: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    copyright_: Union[Unset, str] = UNSET
    license_: Union[Unset, str] = UNSET
    license_expression: Union[Unset, str] = UNSET
    license_url: Union[Unset, str] = UNSET
    resolved_license: Union[Unset, "License"] = UNSET
    direct_dependencies: Union[Unset, str] = UNSET
    external_references: Union[Unset, list["ExternalReference"]] = UNSET
    parent: Union[Unset, "Component"] = UNSET
    children: Union[Unset, list["Component"]] = UNSET
    properties: Union[Unset, list["ComponentProperty"]] = UNSET
    vulnerabilities: Union[Unset, list["Vulnerability"]] = UNSET
    last_inherited_risk_score: Union[Unset, float] = UNSET
    notes: Union[Unset, str] = UNSET
    author: Union[Unset, str] = UNSET
    metrics: Union[Unset, "DependencyMetrics"] = UNSET
    repository_meta: Union[Unset, "RepositoryMetaComponent"] = UNSET
    dependency_graph: Union[Unset, list[str]] = UNSET
    expand_dependency_graph: Union[Unset, bool] = UNSET
    is_internal: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project = self.project.to_dict()

        uuid = str(self.uuid)

        authors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authors, Unset):
            authors = []
            for authors_item_data in self.authors:
                authors_item = authors_item_data.to_dict()
                authors.append(authors_item)

        publisher = self.publisher

        supplier: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.supplier, Unset):
            supplier = self.supplier.to_dict()

        group = self.group

        name = self.name

        version = self.version

        classifier: Union[Unset, str] = UNSET
        if not isinstance(self.classifier, Unset):
            classifier = self.classifier.value

        filename = self.filename

        extension = self.extension

        md5 = self.md5

        sha1 = self.sha1

        sha256 = self.sha256

        sha384 = self.sha384

        sha512 = self.sha512

        sha3_256 = self.sha3_256

        sha3_384 = self.sha3_384

        sha3_512 = self.sha3_512

        blake2b_256 = self.blake2b_256

        blake2b_384 = self.blake2b_384

        blake2b_512 = self.blake2b_512

        blake3 = self.blake3

        cpe = self.cpe

        purl = self.purl

        purl_coordinates = self.purl_coordinates

        swid_tag_id = self.swid_tag_id

        description = self.description

        copyright_ = self.copyright_

        license_ = self.license_

        license_expression = self.license_expression

        license_url = self.license_url

        resolved_license: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.resolved_license, Unset):
            resolved_license = self.resolved_license.to_dict()

        direct_dependencies = self.direct_dependencies

        external_references: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.external_references, Unset):
            external_references = []
            for external_references_item_data in self.external_references:
                external_references_item = external_references_item_data.to_dict()
                external_references.append(external_references_item)

        parent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parent, Unset):
            parent = self.parent.to_dict()

        children: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.children, Unset):
            children = []
            for children_item_data in self.children:
                children_item = children_item_data.to_dict()
                children.append(children_item)

        properties: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = []
            for properties_item_data in self.properties:
                properties_item = properties_item_data.to_dict()
                properties.append(properties_item)

        vulnerabilities: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.vulnerabilities, Unset):
            vulnerabilities = []
            for vulnerabilities_item_data in self.vulnerabilities:
                vulnerabilities_item = vulnerabilities_item_data.to_dict()
                vulnerabilities.append(vulnerabilities_item)

        last_inherited_risk_score = self.last_inherited_risk_score

        notes = self.notes

        author = self.author

        metrics: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics.to_dict()

        repository_meta: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.repository_meta, Unset):
            repository_meta = self.repository_meta.to_dict()

        dependency_graph: Union[Unset, list[str]] = UNSET
        if not isinstance(self.dependency_graph, Unset):
            dependency_graph = self.dependency_graph

        expand_dependency_graph = self.expand_dependency_graph

        is_internal = self.is_internal

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project": project,
                "uuid": uuid,
            }
        )
        if authors is not UNSET:
            field_dict["authors"] = authors
        if publisher is not UNSET:
            field_dict["publisher"] = publisher
        if supplier is not UNSET:
            field_dict["supplier"] = supplier
        if group is not UNSET:
            field_dict["group"] = group
        if name is not UNSET:
            field_dict["name"] = name
        if version is not UNSET:
            field_dict["version"] = version
        if classifier is not UNSET:
            field_dict["classifier"] = classifier
        if filename is not UNSET:
            field_dict["filename"] = filename
        if extension is not UNSET:
            field_dict["extension"] = extension
        if md5 is not UNSET:
            field_dict["md5"] = md5
        if sha1 is not UNSET:
            field_dict["sha1"] = sha1
        if sha256 is not UNSET:
            field_dict["sha256"] = sha256
        if sha384 is not UNSET:
            field_dict["sha384"] = sha384
        if sha512 is not UNSET:
            field_dict["sha512"] = sha512
        if sha3_256 is not UNSET:
            field_dict["sha3_256"] = sha3_256
        if sha3_384 is not UNSET:
            field_dict["sha3_384"] = sha3_384
        if sha3_512 is not UNSET:
            field_dict["sha3_512"] = sha3_512
        if blake2b_256 is not UNSET:
            field_dict["blake2b_256"] = blake2b_256
        if blake2b_384 is not UNSET:
            field_dict["blake2b_384"] = blake2b_384
        if blake2b_512 is not UNSET:
            field_dict["blake2b_512"] = blake2b_512
        if blake3 is not UNSET:
            field_dict["blake3"] = blake3
        if cpe is not UNSET:
            field_dict["cpe"] = cpe
        if purl is not UNSET:
            field_dict["purl"] = purl
        if purl_coordinates is not UNSET:
            field_dict["purlCoordinates"] = purl_coordinates
        if swid_tag_id is not UNSET:
            field_dict["swidTagId"] = swid_tag_id
        if description is not UNSET:
            field_dict["description"] = description
        if copyright_ is not UNSET:
            field_dict["copyright"] = copyright_
        if license_ is not UNSET:
            field_dict["license"] = license_
        if license_expression is not UNSET:
            field_dict["licenseExpression"] = license_expression
        if license_url is not UNSET:
            field_dict["licenseUrl"] = license_url
        if resolved_license is not UNSET:
            field_dict["resolvedLicense"] = resolved_license
        if direct_dependencies is not UNSET:
            field_dict["directDependencies"] = direct_dependencies
        if external_references is not UNSET:
            field_dict["externalReferences"] = external_references
        if parent is not UNSET:
            field_dict["parent"] = parent
        if children is not UNSET:
            field_dict["children"] = children
        if properties is not UNSET:
            field_dict["properties"] = properties
        if vulnerabilities is not UNSET:
            field_dict["vulnerabilities"] = vulnerabilities
        if last_inherited_risk_score is not UNSET:
            field_dict["lastInheritedRiskScore"] = last_inherited_risk_score
        if notes is not UNSET:
            field_dict["notes"] = notes
        if author is not UNSET:
            field_dict["author"] = author
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if repository_meta is not UNSET:
            field_dict["repositoryMeta"] = repository_meta
        if dependency_graph is not UNSET:
            field_dict["dependencyGraph"] = dependency_graph
        if expand_dependency_graph is not UNSET:
            field_dict["expandDependencyGraph"] = expand_dependency_graph
        if is_internal is not UNSET:
            field_dict["isInternal"] = is_internal

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.component_property import ComponentProperty
        from ..models.dependency_metrics import DependencyMetrics
        from ..models.external_reference import ExternalReference
        from ..models.license_ import License
        from ..models.organizational_contact import OrganizationalContact
        from ..models.organizational_entity import OrganizationalEntity
        from ..models.project import Project
        from ..models.repository_meta_component import RepositoryMetaComponent
        from ..models.vulnerability import Vulnerability

        d = dict(src_dict)
        project = Project.from_dict(d.pop("project"))

        uuid = UUID(d.pop("uuid"))

        authors = []
        _authors = d.pop("authors", UNSET)
        for authors_item_data in _authors or []:
            authors_item = OrganizationalContact.from_dict(authors_item_data)

            authors.append(authors_item)

        publisher = d.pop("publisher", UNSET)

        _supplier = d.pop("supplier", UNSET)
        supplier: Union[Unset, OrganizationalEntity]
        if isinstance(_supplier, Unset):
            supplier = UNSET
        else:
            supplier = OrganizationalEntity.from_dict(_supplier)

        group = d.pop("group", UNSET)

        name = d.pop("name", UNSET)

        version = d.pop("version", UNSET)

        _classifier = d.pop("classifier", UNSET)
        classifier: Union[Unset, ComponentClassifier]
        if isinstance(_classifier, Unset):
            classifier = UNSET
        else:
            classifier = ComponentClassifier(_classifier)

        filename = d.pop("filename", UNSET)

        extension = d.pop("extension", UNSET)

        md5 = d.pop("md5", UNSET)

        sha1 = d.pop("sha1", UNSET)

        sha256 = d.pop("sha256", UNSET)

        sha384 = d.pop("sha384", UNSET)

        sha512 = d.pop("sha512", UNSET)

        sha3_256 = d.pop("sha3_256", UNSET)

        sha3_384 = d.pop("sha3_384", UNSET)

        sha3_512 = d.pop("sha3_512", UNSET)

        blake2b_256 = d.pop("blake2b_256", UNSET)

        blake2b_384 = d.pop("blake2b_384", UNSET)

        blake2b_512 = d.pop("blake2b_512", UNSET)

        blake3 = d.pop("blake3", UNSET)

        cpe = d.pop("cpe", UNSET)

        purl = d.pop("purl", UNSET)

        purl_coordinates = d.pop("purlCoordinates", UNSET)

        swid_tag_id = d.pop("swidTagId", UNSET)

        description = d.pop("description", UNSET)

        copyright_ = d.pop("copyright", UNSET)

        license_ = d.pop("license", UNSET)

        license_expression = d.pop("licenseExpression", UNSET)

        license_url = d.pop("licenseUrl", UNSET)

        _resolved_license = d.pop("resolvedLicense", UNSET)
        resolved_license: Union[Unset, License]
        if isinstance(_resolved_license, Unset):
            resolved_license = UNSET
        else:
            resolved_license = License.from_dict(_resolved_license)

        direct_dependencies = d.pop("directDependencies", UNSET)

        external_references = []
        _external_references = d.pop("externalReferences", UNSET)
        for external_references_item_data in _external_references or []:
            external_references_item = ExternalReference.from_dict(
                external_references_item_data
            )

            external_references.append(external_references_item)

        _parent = d.pop("parent", UNSET)
        parent: Union[Unset, Component]
        if isinstance(_parent, Unset):
            parent = UNSET
        else:
            parent = Component.from_dict(_parent)

        children = []
        _children = d.pop("children", UNSET)
        for children_item_data in _children or []:
            children_item = Component.from_dict(children_item_data)

            children.append(children_item)

        properties = []
        _properties = d.pop("properties", UNSET)
        for properties_item_data in _properties or []:
            properties_item = ComponentProperty.from_dict(properties_item_data)

            properties.append(properties_item)

        vulnerabilities = []
        _vulnerabilities = d.pop("vulnerabilities", UNSET)
        for vulnerabilities_item_data in _vulnerabilities or []:
            vulnerabilities_item = Vulnerability.from_dict(vulnerabilities_item_data)

            vulnerabilities.append(vulnerabilities_item)

        last_inherited_risk_score = d.pop("lastInheritedRiskScore", UNSET)

        notes = d.pop("notes", UNSET)

        author = d.pop("author", UNSET)

        _metrics = d.pop("metrics", UNSET)
        metrics: Union[Unset, DependencyMetrics]
        if isinstance(_metrics, Unset):
            metrics = UNSET
        else:
            metrics = DependencyMetrics.from_dict(_metrics)

        _repository_meta = d.pop("repositoryMeta", UNSET)
        repository_meta: Union[Unset, RepositoryMetaComponent]
        if isinstance(_repository_meta, Unset):
            repository_meta = UNSET
        else:
            repository_meta = RepositoryMetaComponent.from_dict(_repository_meta)

        dependency_graph = cast(list[str], d.pop("dependencyGraph", UNSET))

        expand_dependency_graph = d.pop("expandDependencyGraph", UNSET)

        is_internal = d.pop("isInternal", UNSET)

        component = cls(
            project=project,
            uuid=uuid,
            authors=authors,
            publisher=publisher,
            supplier=supplier,
            group=group,
            name=name,
            version=version,
            classifier=classifier,
            filename=filename,
            extension=extension,
            md5=md5,
            sha1=sha1,
            sha256=sha256,
            sha384=sha384,
            sha512=sha512,
            sha3_256=sha3_256,
            sha3_384=sha3_384,
            sha3_512=sha3_512,
            blake2b_256=blake2b_256,
            blake2b_384=blake2b_384,
            blake2b_512=blake2b_512,
            blake3=blake3,
            cpe=cpe,
            purl=purl,
            purl_coordinates=purl_coordinates,
            swid_tag_id=swid_tag_id,
            description=description,
            copyright_=copyright_,
            license_=license_,
            license_expression=license_expression,
            license_url=license_url,
            resolved_license=resolved_license,
            direct_dependencies=direct_dependencies,
            external_references=external_references,
            parent=parent,
            children=children,
            properties=properties,
            vulnerabilities=vulnerabilities,
            last_inherited_risk_score=last_inherited_risk_score,
            notes=notes,
            author=author,
            metrics=metrics,
            repository_meta=repository_meta,
            dependency_graph=dependency_graph,
            expand_dependency_graph=expand_dependency_graph,
            is_internal=is_internal,
        )

        component.additional_properties = d
        return component

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
