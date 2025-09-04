from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.notification_rule_notification_level import (
    NotificationRuleNotificationLevel,
)
from ..models.notification_rule_notify_on_item import NotificationRuleNotifyOnItem
from ..models.notification_rule_scope import NotificationRuleScope
from ..models.notification_rule_trigger_type import NotificationRuleTriggerType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.notification_publisher import NotificationPublisher
    from ..models.project import Project
    from ..models.tag import Tag
    from ..models.team import Team


T = TypeVar("T", bound="NotificationRule")


@_attrs_define
class NotificationRule:
    """
    Attributes:
        name (str):
        scope (NotificationRuleScope):
        trigger_type (NotificationRuleTriggerType):
        uuid (UUID):
        enabled (Union[Unset, bool]):
        notify_children (Union[Unset, bool]):
        log_successful_publish (Union[Unset, bool]):
        notification_level (Union[Unset, NotificationRuleNotificationLevel]):
        projects (Union[Unset, list['Project']]):
        tags (Union[Unset, list['Tag']]):
        teams (Union[Unset, list['Team']]):
        notify_on (Union[Unset, list[NotificationRuleNotifyOnItem]]):
        message (Union[Unset, str]):
        publisher (Union[Unset, NotificationPublisher]):
        publisher_config (Union[Unset, str]):
        schedule_last_triggered_at (Union[Unset, int]): When the schedule last triggered, as UNIX epoch timestamp in
            milliseconds
        schedule_next_trigger_at (Union[Unset, int]): When the schedule triggers next, as UNIX epoch timestamp in
            milliseconds
        schedule_cron (Union[Unset, str]): Schedule of this rule as cron expression. Must not be set for rules with
            trigger type EVENT.
        schedule_skip_unchanged (Union[Unset, bool]): Whether to skip emitting a scheduled notification if it doesn't
            contain any changes since its last emission. Must not be set for rules with trigger type EVENT.
    """

    name: str
    scope: NotificationRuleScope
    trigger_type: NotificationRuleTriggerType
    uuid: UUID
    enabled: Union[Unset, bool] = UNSET
    notify_children: Union[Unset, bool] = UNSET
    log_successful_publish: Union[Unset, bool] = UNSET
    notification_level: Union[Unset, NotificationRuleNotificationLevel] = UNSET
    projects: Union[Unset, list["Project"]] = UNSET
    tags: Union[Unset, list["Tag"]] = UNSET
    teams: Union[Unset, list["Team"]] = UNSET
    notify_on: Union[Unset, list[NotificationRuleNotifyOnItem]] = UNSET
    message: Union[Unset, str] = UNSET
    publisher: Union[Unset, "NotificationPublisher"] = UNSET
    publisher_config: Union[Unset, str] = UNSET
    schedule_last_triggered_at: Union[Unset, int] = UNSET
    schedule_next_trigger_at: Union[Unset, int] = UNSET
    schedule_cron: Union[Unset, str] = UNSET
    schedule_skip_unchanged: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        scope = self.scope.value

        trigger_type = self.trigger_type.value

        uuid = str(self.uuid)

        enabled = self.enabled

        notify_children = self.notify_children

        log_successful_publish = self.log_successful_publish

        notification_level: Union[Unset, str] = UNSET
        if not isinstance(self.notification_level, Unset):
            notification_level = self.notification_level.value

        projects: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.projects, Unset):
            projects = []
            for projects_item_data in self.projects:
                projects_item = projects_item_data.to_dict()
                projects.append(projects_item)

        tags: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.to_dict()
                tags.append(tags_item)

        teams: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.teams, Unset):
            teams = []
            for teams_item_data in self.teams:
                teams_item = teams_item_data.to_dict()
                teams.append(teams_item)

        notify_on: Union[Unset, list[str]] = UNSET
        if not isinstance(self.notify_on, Unset):
            notify_on = []
            for notify_on_item_data in self.notify_on:
                notify_on_item = notify_on_item_data.value
                notify_on.append(notify_on_item)

        message = self.message

        publisher: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.publisher, Unset):
            publisher = self.publisher.to_dict()

        publisher_config = self.publisher_config

        schedule_last_triggered_at = self.schedule_last_triggered_at

        schedule_next_trigger_at = self.schedule_next_trigger_at

        schedule_cron = self.schedule_cron

        schedule_skip_unchanged = self.schedule_skip_unchanged

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "scope": scope,
                "triggerType": trigger_type,
                "uuid": uuid,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if notify_children is not UNSET:
            field_dict["notifyChildren"] = notify_children
        if log_successful_publish is not UNSET:
            field_dict["logSuccessfulPublish"] = log_successful_publish
        if notification_level is not UNSET:
            field_dict["notificationLevel"] = notification_level
        if projects is not UNSET:
            field_dict["projects"] = projects
        if tags is not UNSET:
            field_dict["tags"] = tags
        if teams is not UNSET:
            field_dict["teams"] = teams
        if notify_on is not UNSET:
            field_dict["notifyOn"] = notify_on
        if message is not UNSET:
            field_dict["message"] = message
        if publisher is not UNSET:
            field_dict["publisher"] = publisher
        if publisher_config is not UNSET:
            field_dict["publisherConfig"] = publisher_config
        if schedule_last_triggered_at is not UNSET:
            field_dict["scheduleLastTriggeredAt"] = schedule_last_triggered_at
        if schedule_next_trigger_at is not UNSET:
            field_dict["scheduleNextTriggerAt"] = schedule_next_trigger_at
        if schedule_cron is not UNSET:
            field_dict["scheduleCron"] = schedule_cron
        if schedule_skip_unchanged is not UNSET:
            field_dict["scheduleSkipUnchanged"] = schedule_skip_unchanged

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.notification_publisher import NotificationPublisher
        from ..models.project import Project
        from ..models.tag import Tag
        from ..models.team import Team

        d = dict(src_dict)
        name = d.pop("name")

        scope = NotificationRuleScope(d.pop("scope"))

        trigger_type = NotificationRuleTriggerType(d.pop("triggerType"))

        uuid = UUID(d.pop("uuid"))

        enabled = d.pop("enabled", UNSET)

        notify_children = d.pop("notifyChildren", UNSET)

        log_successful_publish = d.pop("logSuccessfulPublish", UNSET)

        _notification_level = d.pop("notificationLevel", UNSET)
        notification_level: Union[Unset, NotificationRuleNotificationLevel]
        if isinstance(_notification_level, Unset):
            notification_level = UNSET
        else:
            notification_level = NotificationRuleNotificationLevel(_notification_level)

        projects = []
        _projects = d.pop("projects", UNSET)
        for projects_item_data in _projects or []:
            projects_item = Project.from_dict(projects_item_data)

            projects.append(projects_item)

        tags = []
        _tags = d.pop("tags", UNSET)
        for tags_item_data in _tags or []:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        teams = []
        _teams = d.pop("teams", UNSET)
        for teams_item_data in _teams or []:
            teams_item = Team.from_dict(teams_item_data)

            teams.append(teams_item)

        notify_on = []
        _notify_on = d.pop("notifyOn", UNSET)
        for notify_on_item_data in _notify_on or []:
            notify_on_item = NotificationRuleNotifyOnItem(notify_on_item_data)

            notify_on.append(notify_on_item)

        message = d.pop("message", UNSET)

        _publisher = d.pop("publisher", UNSET)
        publisher: Union[Unset, NotificationPublisher]
        if isinstance(_publisher, Unset):
            publisher = UNSET
        else:
            publisher = NotificationPublisher.from_dict(_publisher)

        publisher_config = d.pop("publisherConfig", UNSET)

        schedule_last_triggered_at = d.pop("scheduleLastTriggeredAt", UNSET)

        schedule_next_trigger_at = d.pop("scheduleNextTriggerAt", UNSET)

        schedule_cron = d.pop("scheduleCron", UNSET)

        schedule_skip_unchanged = d.pop("scheduleSkipUnchanged", UNSET)

        notification_rule = cls(
            name=name,
            scope=scope,
            trigger_type=trigger_type,
            uuid=uuid,
            enabled=enabled,
            notify_children=notify_children,
            log_successful_publish=log_successful_publish,
            notification_level=notification_level,
            projects=projects,
            tags=tags,
            teams=teams,
            notify_on=notify_on,
            message=message,
            publisher=publisher,
            publisher_config=publisher_config,
            schedule_last_triggered_at=schedule_last_triggered_at,
            schedule_next_trigger_at=schedule_next_trigger_at,
            schedule_cron=schedule_cron,
            schedule_skip_unchanged=schedule_skip_unchanged,
        )

        notification_rule.additional_properties = d
        return notification_rule

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
