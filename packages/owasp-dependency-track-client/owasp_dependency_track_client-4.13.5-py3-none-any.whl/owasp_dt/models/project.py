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

from ..models.project_classifier import ProjectClassifier
from ..models.project_collection_logic import ProjectCollectionLogic
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.external_reference import ExternalReference
    from ..models.organizational_contact import OrganizationalContact
    from ..models.organizational_entity import OrganizationalEntity
    from ..models.project_metadata import ProjectMetadata
    from ..models.project_metrics import ProjectMetrics
    from ..models.project_property import ProjectProperty
    from ..models.project_version import ProjectVersion
    from ..models.tag import Tag
    from ..models.team import Team


T = TypeVar("T", bound="Project")


@_attrs_define
class Project:
    """
    Attributes:
        authors (Union[Unset, list['OrganizationalContact']]):
        publisher (Union[Unset, str]):
        manufacturer (Union[Unset, OrganizationalEntity]):
        supplier (Union[Unset, OrganizationalEntity]):
        group (Union[Unset, str]):
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        version (Union[Unset, str]):
        classifier (Union[Unset, ProjectClassifier]):
        collection_logic (Union[Unset, ProjectCollectionLogic]):
        collection_tag (Union[Unset, Tag]):
        cpe (Union[Unset, str]):
        purl (Union[Unset, str]):
        swid_tag_id (Union[Unset, str]):
        direct_dependencies (Union[Unset, str]):
        uuid (Union[Unset, UUID]):
        parent (Union[Unset, Project]):
        children (Union[None, Unset, list['Project']]):
        properties (Union[Unset, list['ProjectProperty']]):
        tags (Union[Unset, list['Tag']]):
        last_bom_import (Union[Unset, int]): UNIX epoch timestamp in milliseconds
        last_bom_import_format (Union[Unset, str]):
        last_inherited_risk_score (Union[Unset, float]):
        last_vulnerability_analysis (Union[Unset, int]): UNIX epoch timestamp in milliseconds
        active (Union[Unset, bool]):
        is_latest (Union[Unset, bool]):
        access_teams (Union[Unset, list['Team']]):
        external_references (Union[Unset, list['ExternalReference']]):
        metadata (Union[Unset, ProjectMetadata]):
        versions (Union[Unset, list['ProjectVersion']]):
        author (Union[Unset, str]):
        metrics (Union[Unset, ProjectMetrics]):
        bom_ref (Union[Unset, str]):
    """

    authors: Union[Unset, list["OrganizationalContact"]] = UNSET
    publisher: Union[Unset, str] = UNSET
    manufacturer: Union[Unset, "OrganizationalEntity"] = UNSET
    supplier: Union[Unset, "OrganizationalEntity"] = UNSET
    group: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    version: Union[Unset, str] = UNSET
    classifier: Union[Unset, ProjectClassifier] = UNSET
    collection_logic: Union[Unset, ProjectCollectionLogic] = UNSET
    collection_tag: Union[Unset, "Tag"] = UNSET
    cpe: Union[Unset, str] = UNSET
    purl: Union[Unset, str] = UNSET
    swid_tag_id: Union[Unset, str] = UNSET
    direct_dependencies: Union[Unset, str] = UNSET
    uuid: Union[Unset, UUID] = UNSET
    parent: Union[Unset, "Project"] = UNSET
    children: Union[None, Unset, list["Project"]] = UNSET
    properties: Union[Unset, list["ProjectProperty"]] = UNSET
    tags: Union[Unset, list["Tag"]] = UNSET
    last_bom_import: Union[Unset, int] = UNSET
    last_bom_import_format: Union[Unset, str] = UNSET
    last_inherited_risk_score: Union[Unset, float] = UNSET
    last_vulnerability_analysis: Union[Unset, int] = UNSET
    active: Union[Unset, bool] = UNSET
    is_latest: Union[Unset, bool] = UNSET
    access_teams: Union[Unset, list["Team"]] = UNSET
    external_references: Union[Unset, list["ExternalReference"]] = UNSET
    metadata: Union[Unset, "ProjectMetadata"] = UNSET
    versions: Union[Unset, list["ProjectVersion"]] = UNSET
    author: Union[Unset, str] = UNSET
    metrics: Union[Unset, "ProjectMetrics"] = UNSET
    bom_ref: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authors: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.authors, Unset):
            authors = []
            for authors_item_data in self.authors:
                authors_item = authors_item_data.to_dict()
                authors.append(authors_item)

        publisher = self.publisher

        manufacturer: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.manufacturer, Unset):
            manufacturer = self.manufacturer.to_dict()

        supplier: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.supplier, Unset):
            supplier = self.supplier.to_dict()

        group = self.group

        name = self.name

        description = self.description

        version = self.version

        classifier: Union[Unset, str] = UNSET
        if not isinstance(self.classifier, Unset):
            classifier = self.classifier.value

        collection_logic: Union[Unset, str] = UNSET
        if not isinstance(self.collection_logic, Unset):
            collection_logic = self.collection_logic.value

        collection_tag: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.collection_tag, Unset):
            collection_tag = self.collection_tag.to_dict()

        cpe = self.cpe

        purl = self.purl

        swid_tag_id = self.swid_tag_id

        direct_dependencies = self.direct_dependencies

        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        parent: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.parent, Unset):
            parent = self.parent.to_dict()

        children: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.children, Unset):
            children = UNSET
        elif isinstance(self.children, list):
            children = []
            for children_type_0_item_data in self.children:
                children_type_0_item = children_type_0_item_data.to_dict()
                children.append(children_type_0_item)

        else:
            children = self.children

        properties: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.properties, Unset):
            properties = []
            for properties_item_data in self.properties:
                properties_item = properties_item_data.to_dict()
                properties.append(properties_item)

        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)

        last_bom_import = self.last_bom_import

        last_bom_import_format = self.last_bom_import_format

        last_inherited_risk_score = self.last_inherited_risk_score

        last_vulnerability_analysis = self.last_vulnerability_analysis

        active = self.active

        is_latest = self.is_latest

        access_teams: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.access_teams, Unset):
            access_teams = []
            for access_teams_item_data in self.access_teams:
                access_teams_item = access_teams_item_data.to_dict()
                access_teams.append(access_teams_item)

        external_references: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.external_references, Unset):
            external_references = []
            for external_references_item_data in self.external_references:
                external_references_item = external_references_item_data.to_dict()
                external_references.append(external_references_item)

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        versions: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.versions, Unset):
            versions = []
            for versions_item_data in self.versions:
                versions_item = versions_item_data.to_dict()
                versions.append(versions_item)

        author = self.author

        metrics: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metrics, Unset):
            metrics = self.metrics.to_dict()

        bom_ref = self.bom_ref

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if authors is not UNSET:
            field_dict["authors"] = authors
        if publisher is not UNSET:
            field_dict["publisher"] = publisher
        if manufacturer is not UNSET:
            field_dict["manufacturer"] = manufacturer
        if supplier is not UNSET:
            field_dict["supplier"] = supplier
        if group is not UNSET:
            field_dict["group"] = group
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if version is not UNSET:
            field_dict["version"] = version
        if classifier is not UNSET:
            field_dict["classifier"] = classifier
        if collection_logic is not UNSET:
            field_dict["collectionLogic"] = collection_logic
        if collection_tag is not UNSET:
            field_dict["collectionTag"] = collection_tag
        if cpe is not UNSET:
            field_dict["cpe"] = cpe
        if purl is not UNSET:
            field_dict["purl"] = purl
        if swid_tag_id is not UNSET:
            field_dict["swidTagId"] = swid_tag_id
        if direct_dependencies is not UNSET:
            field_dict["directDependencies"] = direct_dependencies
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if parent is not UNSET:
            field_dict["parent"] = parent
        if children is not UNSET:
            field_dict["children"] = children
        if properties is not UNSET:
            field_dict["properties"] = properties
        if tags is not UNSET:
            field_dict["tags"] = tags
        if last_bom_import is not UNSET:
            field_dict["lastBomImport"] = last_bom_import
        if last_bom_import_format is not UNSET:
            field_dict["lastBomImportFormat"] = last_bom_import_format
        if last_inherited_risk_score is not UNSET:
            field_dict["lastInheritedRiskScore"] = last_inherited_risk_score
        if last_vulnerability_analysis is not UNSET:
            field_dict["lastVulnerabilityAnalysis"] = last_vulnerability_analysis
        if active is not UNSET:
            field_dict["active"] = active
        if is_latest is not UNSET:
            field_dict["isLatest"] = is_latest
        if access_teams is not UNSET:
            field_dict["accessTeams"] = access_teams
        if external_references is not UNSET:
            field_dict["externalReferences"] = external_references
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if versions is not UNSET:
            field_dict["versions"] = versions
        if author is not UNSET:
            field_dict["author"] = author
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if bom_ref is not UNSET:
            field_dict["bomRef"] = bom_ref

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.external_reference import ExternalReference
        from ..models.organizational_contact import OrganizationalContact
        from ..models.organizational_entity import OrganizationalEntity
        from ..models.project_metadata import ProjectMetadata
        from ..models.project_metrics import ProjectMetrics
        from ..models.project_property import ProjectProperty
        from ..models.project_version import ProjectVersion
        from ..models.tag import Tag
        from ..models.team import Team

        d = dict(src_dict)
        authors = []
        _authors = d.pop("authors", UNSET)
        for authors_item_data in _authors or []:
            authors_item = OrganizationalContact.from_dict(authors_item_data)

            authors.append(authors_item)

        publisher = d.pop("publisher", UNSET)

        _manufacturer = d.pop("manufacturer", UNSET)
        manufacturer: Union[Unset, OrganizationalEntity]
        if isinstance(_manufacturer, Unset):
            manufacturer = UNSET
        else:
            manufacturer = OrganizationalEntity.from_dict(_manufacturer)

        _supplier = d.pop("supplier", UNSET)
        supplier: Union[Unset, OrganizationalEntity]
        if isinstance(_supplier, Unset):
            supplier = UNSET
        else:
            supplier = OrganizationalEntity.from_dict(_supplier)

        group = d.pop("group", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        version = d.pop("version", UNSET)

        _classifier = d.pop("classifier", UNSET)
        classifier: Union[Unset, ProjectClassifier]
        if isinstance(_classifier, Unset):
            classifier = UNSET
        else:
            classifier = ProjectClassifier(_classifier)

        _collection_logic = d.pop("collectionLogic", UNSET)
        collection_logic: Union[Unset, ProjectCollectionLogic]
        if isinstance(_collection_logic, Unset):
            collection_logic = UNSET
        else:
            collection_logic = ProjectCollectionLogic(_collection_logic)

        _collection_tag = d.pop("collectionTag", UNSET)
        collection_tag: Union[Unset, Tag]
        if isinstance(_collection_tag, Unset):
            collection_tag = UNSET
        else:
            collection_tag = Tag.from_dict(_collection_tag)

        cpe = d.pop("cpe", UNSET)

        purl = d.pop("purl", UNSET)

        swid_tag_id = d.pop("swidTagId", UNSET)

        direct_dependencies = d.pop("directDependencies", UNSET)

        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        _parent = d.pop("parent", UNSET)
        parent: Union[Unset, Project]
        if isinstance(_parent, Unset):
            parent = UNSET
        else:
            parent = Project.from_dict(_parent)

        def _parse_children(data: object) -> Union[None, Unset, list["Project"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                children_type_0 = []
                _children_type_0 = data
                for children_type_0_item_data in _children_type_0:
                    children_type_0_item = Project.from_dict(children_type_0_item_data)

                    children_type_0.append(children_type_0_item)

                return children_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["Project"]], data)

        children = _parse_children(d.pop("children", UNSET))

        properties = []
        _properties = d.pop("properties", UNSET)
        for properties_item_data in _properties or []:
            properties_item = ProjectProperty.from_dict(properties_item_data)

            properties.append(properties_item)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in _tags or []:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        last_bom_import = d.pop("lastBomImport", UNSET)

        last_bom_import_format = d.pop("lastBomImportFormat", UNSET)

        last_inherited_risk_score = d.pop("lastInheritedRiskScore", UNSET)

        last_vulnerability_analysis = d.pop("lastVulnerabilityAnalysis", UNSET)

        active = d.pop("active", UNSET)

        is_latest = d.pop("isLatest", UNSET)

        access_teams = []
        _access_teams = d.pop("accessTeams", UNSET)
        for access_teams_item_data in _access_teams or []:
            access_teams_item = Team.from_dict(access_teams_item_data)

            access_teams.append(access_teams_item)

        external_references = []
        _external_references = d.pop("externalReferences", UNSET)
        for external_references_item_data in _external_references or []:
            external_references_item = ExternalReference.from_dict(
                external_references_item_data
            )

            external_references.append(external_references_item)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ProjectMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ProjectMetadata.from_dict(_metadata)

        versions = []
        _versions = d.pop("versions", UNSET)
        for versions_item_data in _versions or []:
            versions_item = ProjectVersion.from_dict(versions_item_data)

            versions.append(versions_item)

        author = d.pop("author", UNSET)

        _metrics = d.pop("metrics", UNSET)
        metrics: Union[Unset, ProjectMetrics]
        if isinstance(_metrics, Unset):
            metrics = UNSET
        else:
            metrics = ProjectMetrics.from_dict(_metrics)

        bom_ref = d.pop("bomRef", UNSET)

        project = cls(
            authors=authors,
            publisher=publisher,
            manufacturer=manufacturer,
            supplier=supplier,
            group=group,
            name=name,
            description=description,
            version=version,
            classifier=classifier,
            collection_logic=collection_logic,
            collection_tag=collection_tag,
            cpe=cpe,
            purl=purl,
            swid_tag_id=swid_tag_id,
            direct_dependencies=direct_dependencies,
            uuid=uuid,
            parent=parent,
            children=children,
            properties=properties,
            tags=tags,
            last_bom_import=last_bom_import,
            last_bom_import_format=last_bom_import_format,
            last_inherited_risk_score=last_inherited_risk_score,
            last_vulnerability_analysis=last_vulnerability_analysis,
            active=active,
            is_latest=is_latest,
            access_teams=access_teams,
            external_references=external_references,
            metadata=metadata,
            versions=versions,
            author=author,
            metrics=metrics,
            bom_ref=bom_ref,
        )

        project.additional_properties = d
        return project

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
