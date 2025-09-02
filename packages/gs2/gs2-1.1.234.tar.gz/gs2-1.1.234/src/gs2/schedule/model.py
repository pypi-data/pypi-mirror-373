# Copyright 2016 Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

from __future__ import annotations

import re
from typing import *
from gs2 import core


class LogSetting(core.Gs2Model):
    logging_namespace_id: str = None

    def with_logging_namespace_id(self, logging_namespace_id: str) -> LogSetting:
        self.logging_namespace_id = logging_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[LogSetting]:
        if data is None:
            return None
        return LogSetting()\
            .with_logging_namespace_id(data.get('loggingNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loggingNamespaceId": self.logging_namespace_id,
        }


class GitHubCheckoutSetting(core.Gs2Model):
    api_key_id: str = None
    repository_name: str = None
    source_path: str = None
    reference_type: str = None
    commit_hash: str = None
    branch_name: str = None
    tag_name: str = None

    def with_api_key_id(self, api_key_id: str) -> GitHubCheckoutSetting:
        self.api_key_id = api_key_id
        return self

    def with_repository_name(self, repository_name: str) -> GitHubCheckoutSetting:
        self.repository_name = repository_name
        return self

    def with_source_path(self, source_path: str) -> GitHubCheckoutSetting:
        self.source_path = source_path
        return self

    def with_reference_type(self, reference_type: str) -> GitHubCheckoutSetting:
        self.reference_type = reference_type
        return self

    def with_commit_hash(self, commit_hash: str) -> GitHubCheckoutSetting:
        self.commit_hash = commit_hash
        return self

    def with_branch_name(self, branch_name: str) -> GitHubCheckoutSetting:
        self.branch_name = branch_name
        return self

    def with_tag_name(self, tag_name: str) -> GitHubCheckoutSetting:
        self.tag_name = tag_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GitHubCheckoutSetting]:
        if data is None:
            return None
        return GitHubCheckoutSetting()\
            .with_api_key_id(data.get('apiKeyId'))\
            .with_repository_name(data.get('repositoryName'))\
            .with_source_path(data.get('sourcePath'))\
            .with_reference_type(data.get('referenceType'))\
            .with_commit_hash(data.get('commitHash'))\
            .with_branch_name(data.get('branchName'))\
            .with_tag_name(data.get('tagName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "apiKeyId": self.api_key_id,
            "repositoryName": self.repository_name,
            "sourcePath": self.source_path,
            "referenceType": self.reference_type,
            "commitHash": self.commit_hash,
            "branchName": self.branch_name,
            "tagName": self.tag_name,
        }


class CurrentEventMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentEventMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentEventMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:schedule:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CurrentEventMaster]:
        if data is None:
            return None
        return CurrentEventMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class RepeatSchedule(core.Gs2Model):
    repeat_count: int = None
    current_repeat_start_at: int = None
    current_repeat_end_at: int = None
    last_repeat_end_at: int = None
    next_repeat_start_at: int = None

    def with_repeat_count(self, repeat_count: int) -> RepeatSchedule:
        self.repeat_count = repeat_count
        return self

    def with_current_repeat_start_at(self, current_repeat_start_at: int) -> RepeatSchedule:
        self.current_repeat_start_at = current_repeat_start_at
        return self

    def with_current_repeat_end_at(self, current_repeat_end_at: int) -> RepeatSchedule:
        self.current_repeat_end_at = current_repeat_end_at
        return self

    def with_last_repeat_end_at(self, last_repeat_end_at: int) -> RepeatSchedule:
        self.last_repeat_end_at = last_repeat_end_at
        return self

    def with_next_repeat_start_at(self, next_repeat_start_at: int) -> RepeatSchedule:
        self.next_repeat_start_at = next_repeat_start_at
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RepeatSchedule]:
        if data is None:
            return None
        return RepeatSchedule()\
            .with_repeat_count(data.get('repeatCount'))\
            .with_current_repeat_start_at(data.get('currentRepeatStartAt'))\
            .with_current_repeat_end_at(data.get('currentRepeatEndAt'))\
            .with_last_repeat_end_at(data.get('lastRepeatEndAt'))\
            .with_next_repeat_start_at(data.get('nextRepeatStartAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repeatCount": self.repeat_count,
            "currentRepeatStartAt": self.current_repeat_start_at,
            "currentRepeatEndAt": self.current_repeat_end_at,
            "lastRepeatEndAt": self.last_repeat_end_at,
            "nextRepeatStartAt": self.next_repeat_start_at,
        }


class RepeatSetting(core.Gs2Model):
    repeat_type: str = None
    begin_day_of_month: int = None
    end_day_of_month: int = None
    begin_day_of_week: str = None
    end_day_of_week: str = None
    begin_hour: int = None
    end_hour: int = None
    anchor_timestamp: int = None
    active_days: int = None
    inactive_days: int = None

    def with_repeat_type(self, repeat_type: str) -> RepeatSetting:
        self.repeat_type = repeat_type
        return self

    def with_begin_day_of_month(self, begin_day_of_month: int) -> RepeatSetting:
        self.begin_day_of_month = begin_day_of_month
        return self

    def with_end_day_of_month(self, end_day_of_month: int) -> RepeatSetting:
        self.end_day_of_month = end_day_of_month
        return self

    def with_begin_day_of_week(self, begin_day_of_week: str) -> RepeatSetting:
        self.begin_day_of_week = begin_day_of_week
        return self

    def with_end_day_of_week(self, end_day_of_week: str) -> RepeatSetting:
        self.end_day_of_week = end_day_of_week
        return self

    def with_begin_hour(self, begin_hour: int) -> RepeatSetting:
        self.begin_hour = begin_hour
        return self

    def with_end_hour(self, end_hour: int) -> RepeatSetting:
        self.end_hour = end_hour
        return self

    def with_anchor_timestamp(self, anchor_timestamp: int) -> RepeatSetting:
        self.anchor_timestamp = anchor_timestamp
        return self

    def with_active_days(self, active_days: int) -> RepeatSetting:
        self.active_days = active_days
        return self

    def with_inactive_days(self, inactive_days: int) -> RepeatSetting:
        self.inactive_days = inactive_days
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RepeatSetting]:
        if data is None:
            return None
        return RepeatSetting()\
            .with_repeat_type(data.get('repeatType'))\
            .with_begin_day_of_month(data.get('beginDayOfMonth'))\
            .with_end_day_of_month(data.get('endDayOfMonth'))\
            .with_begin_day_of_week(data.get('beginDayOfWeek'))\
            .with_end_day_of_week(data.get('endDayOfWeek'))\
            .with_begin_hour(data.get('beginHour'))\
            .with_end_hour(data.get('endHour'))\
            .with_anchor_timestamp(data.get('anchorTimestamp'))\
            .with_active_days(data.get('activeDays'))\
            .with_inactive_days(data.get('inactiveDays'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repeatType": self.repeat_type,
            "beginDayOfMonth": self.begin_day_of_month,
            "endDayOfMonth": self.end_day_of_month,
            "beginDayOfWeek": self.begin_day_of_week,
            "endDayOfWeek": self.end_day_of_week,
            "beginHour": self.begin_hour,
            "endHour": self.end_hour,
            "anchorTimestamp": self.anchor_timestamp,
            "activeDays": self.active_days,
            "inactiveDays": self.inactive_days,
        }


class Event(core.Gs2Model):
    event_id: str = None
    name: str = None
    metadata: str = None
    schedule_type: str = None
    absolute_begin: int = None
    absolute_end: int = None
    relative_trigger_name: str = None
    repeat_setting: RepeatSetting = None
    repeat_type: str = None
    repeat_begin_day_of_month: int = None
    repeat_end_day_of_month: int = None
    repeat_begin_day_of_week: str = None
    repeat_end_day_of_week: str = None
    repeat_begin_hour: int = None
    repeat_end_hour: int = None

    def with_event_id(self, event_id: str) -> Event:
        self.event_id = event_id
        return self

    def with_name(self, name: str) -> Event:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> Event:
        self.metadata = metadata
        return self

    def with_schedule_type(self, schedule_type: str) -> Event:
        self.schedule_type = schedule_type
        return self

    def with_absolute_begin(self, absolute_begin: int) -> Event:
        self.absolute_begin = absolute_begin
        return self

    def with_absolute_end(self, absolute_end: int) -> Event:
        self.absolute_end = absolute_end
        return self

    def with_relative_trigger_name(self, relative_trigger_name: str) -> Event:
        self.relative_trigger_name = relative_trigger_name
        return self

    def with_repeat_setting(self, repeat_setting: RepeatSetting) -> Event:
        self.repeat_setting = repeat_setting
        return self

    def with_repeat_type(self, repeat_type: str) -> Event:
        self.repeat_type = repeat_type
        return self

    def with_repeat_begin_day_of_month(self, repeat_begin_day_of_month: int) -> Event:
        self.repeat_begin_day_of_month = repeat_begin_day_of_month
        return self

    def with_repeat_end_day_of_month(self, repeat_end_day_of_month: int) -> Event:
        self.repeat_end_day_of_month = repeat_end_day_of_month
        return self

    def with_repeat_begin_day_of_week(self, repeat_begin_day_of_week: str) -> Event:
        self.repeat_begin_day_of_week = repeat_begin_day_of_week
        return self

    def with_repeat_end_day_of_week(self, repeat_end_day_of_week: str) -> Event:
        self.repeat_end_day_of_week = repeat_end_day_of_week
        return self

    def with_repeat_begin_hour(self, repeat_begin_hour: int) -> Event:
        self.repeat_begin_hour = repeat_begin_hour
        return self

    def with_repeat_end_hour(self, repeat_end_hour: int) -> Event:
        self.repeat_end_hour = repeat_end_hour
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        event_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:schedule:{namespaceName}:event:{eventName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            eventName=event_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_event_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('event_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Event]:
        if data is None:
            return None
        return Event()\
            .with_event_id(data.get('eventId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_schedule_type(data.get('scheduleType'))\
            .with_absolute_begin(data.get('absoluteBegin'))\
            .with_absolute_end(data.get('absoluteEnd'))\
            .with_relative_trigger_name(data.get('relativeTriggerName'))\
            .with_repeat_setting(RepeatSetting.from_dict(data.get('repeatSetting')))\
            .with_repeat_type(data.get('repeatType'))\
            .with_repeat_begin_day_of_month(data.get('repeatBeginDayOfMonth'))\
            .with_repeat_end_day_of_month(data.get('repeatEndDayOfMonth'))\
            .with_repeat_begin_day_of_week(data.get('repeatBeginDayOfWeek'))\
            .with_repeat_end_day_of_week(data.get('repeatEndDayOfWeek'))\
            .with_repeat_begin_hour(data.get('repeatBeginHour'))\
            .with_repeat_end_hour(data.get('repeatEndHour'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eventId": self.event_id,
            "name": self.name,
            "metadata": self.metadata,
            "scheduleType": self.schedule_type,
            "absoluteBegin": self.absolute_begin,
            "absoluteEnd": self.absolute_end,
            "relativeTriggerName": self.relative_trigger_name,
            "repeatSetting": self.repeat_setting.to_dict() if self.repeat_setting else None,
            "repeatType": self.repeat_type,
            "repeatBeginDayOfMonth": self.repeat_begin_day_of_month,
            "repeatEndDayOfMonth": self.repeat_end_day_of_month,
            "repeatBeginDayOfWeek": self.repeat_begin_day_of_week,
            "repeatEndDayOfWeek": self.repeat_end_day_of_week,
            "repeatBeginHour": self.repeat_begin_hour,
            "repeatEndHour": self.repeat_end_hour,
        }


class Trigger(core.Gs2Model):
    trigger_id: str = None
    name: str = None
    user_id: str = None
    triggered_at: int = None
    expires_at: int = None
    created_at: int = None
    revision: int = None

    def with_trigger_id(self, trigger_id: str) -> Trigger:
        self.trigger_id = trigger_id
        return self

    def with_name(self, name: str) -> Trigger:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> Trigger:
        self.user_id = user_id
        return self

    def with_triggered_at(self, triggered_at: int) -> Trigger:
        self.triggered_at = triggered_at
        return self

    def with_expires_at(self, expires_at: int) -> Trigger:
        self.expires_at = expires_at
        return self

    def with_created_at(self, created_at: int) -> Trigger:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Trigger:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        trigger_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:schedule:{namespaceName}:user:{userId}:trigger:{triggerName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            triggerName=trigger_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):user:(?P<userId>.+):trigger:(?P<triggerName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):user:(?P<userId>.+):trigger:(?P<triggerName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):user:(?P<userId>.+):trigger:(?P<triggerName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):user:(?P<userId>.+):trigger:(?P<triggerName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_trigger_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):user:(?P<userId>.+):trigger:(?P<triggerName>.+)', grn)
        if match is None:
            return None
        return match.group('trigger_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Trigger]:
        if data is None:
            return None
        return Trigger()\
            .with_trigger_id(data.get('triggerId'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_triggered_at(data.get('triggeredAt'))\
            .with_expires_at(data.get('expiresAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggerId": self.trigger_id,
            "name": self.name,
            "userId": self.user_id,
            "triggeredAt": self.triggered_at,
            "expiresAt": self.expires_at,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class EventMaster(core.Gs2Model):
    event_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    schedule_type: str = None
    absolute_begin: int = None
    absolute_end: int = None
    relative_trigger_name: str = None
    repeat_setting: RepeatSetting = None
    created_at: int = None
    updated_at: int = None
    revision: int = None
    repeat_type: str = None
    repeat_begin_day_of_month: int = None
    repeat_end_day_of_month: int = None
    repeat_begin_day_of_week: str = None
    repeat_end_day_of_week: str = None
    repeat_begin_hour: int = None
    repeat_end_hour: int = None

    def with_event_id(self, event_id: str) -> EventMaster:
        self.event_id = event_id
        return self

    def with_name(self, name: str) -> EventMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> EventMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> EventMaster:
        self.metadata = metadata
        return self

    def with_schedule_type(self, schedule_type: str) -> EventMaster:
        self.schedule_type = schedule_type
        return self

    def with_absolute_begin(self, absolute_begin: int) -> EventMaster:
        self.absolute_begin = absolute_begin
        return self

    def with_absolute_end(self, absolute_end: int) -> EventMaster:
        self.absolute_end = absolute_end
        return self

    def with_relative_trigger_name(self, relative_trigger_name: str) -> EventMaster:
        self.relative_trigger_name = relative_trigger_name
        return self

    def with_repeat_setting(self, repeat_setting: RepeatSetting) -> EventMaster:
        self.repeat_setting = repeat_setting
        return self

    def with_created_at(self, created_at: int) -> EventMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> EventMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> EventMaster:
        self.revision = revision
        return self

    def with_repeat_type(self, repeat_type: str) -> EventMaster:
        self.repeat_type = repeat_type
        return self

    def with_repeat_begin_day_of_month(self, repeat_begin_day_of_month: int) -> EventMaster:
        self.repeat_begin_day_of_month = repeat_begin_day_of_month
        return self

    def with_repeat_end_day_of_month(self, repeat_end_day_of_month: int) -> EventMaster:
        self.repeat_end_day_of_month = repeat_end_day_of_month
        return self

    def with_repeat_begin_day_of_week(self, repeat_begin_day_of_week: str) -> EventMaster:
        self.repeat_begin_day_of_week = repeat_begin_day_of_week
        return self

    def with_repeat_end_day_of_week(self, repeat_end_day_of_week: str) -> EventMaster:
        self.repeat_end_day_of_week = repeat_end_day_of_week
        return self

    def with_repeat_begin_hour(self, repeat_begin_hour: int) -> EventMaster:
        self.repeat_begin_hour = repeat_begin_hour
        return self

    def with_repeat_end_hour(self, repeat_end_hour: int) -> EventMaster:
        self.repeat_end_hour = repeat_end_hour
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        event_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:schedule:{namespaceName}:event:{eventName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            eventName=event_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_event_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('event_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[EventMaster]:
        if data is None:
            return None
        return EventMaster()\
            .with_event_id(data.get('eventId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_schedule_type(data.get('scheduleType'))\
            .with_absolute_begin(data.get('absoluteBegin'))\
            .with_absolute_end(data.get('absoluteEnd'))\
            .with_relative_trigger_name(data.get('relativeTriggerName'))\
            .with_repeat_setting(RepeatSetting.from_dict(data.get('repeatSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))\
            .with_repeat_type(data.get('repeatType'))\
            .with_repeat_begin_day_of_month(data.get('repeatBeginDayOfMonth'))\
            .with_repeat_end_day_of_month(data.get('repeatEndDayOfMonth'))\
            .with_repeat_begin_day_of_week(data.get('repeatBeginDayOfWeek'))\
            .with_repeat_end_day_of_week(data.get('repeatEndDayOfWeek'))\
            .with_repeat_begin_hour(data.get('repeatBeginHour'))\
            .with_repeat_end_hour(data.get('repeatEndHour'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eventId": self.event_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "scheduleType": self.schedule_type,
            "absoluteBegin": self.absolute_begin,
            "absoluteEnd": self.absolute_end,
            "relativeTriggerName": self.relative_trigger_name,
            "repeatSetting": self.repeat_setting.to_dict() if self.repeat_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
            "repeatType": self.repeat_type,
            "repeatBeginDayOfMonth": self.repeat_begin_day_of_month,
            "repeatEndDayOfMonth": self.repeat_end_day_of_month,
            "repeatBeginDayOfWeek": self.repeat_begin_day_of_week,
            "repeatEndDayOfWeek": self.repeat_end_day_of_week,
            "repeatBeginHour": self.repeat_begin_hour,
            "repeatEndHour": self.repeat_end_hour,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_log_setting(self, log_setting: LogSetting) -> Namespace:
        self.log_setting = log_setting
        return self

    def with_created_at(self, created_at: int) -> Namespace:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Namespace:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Namespace:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:schedule:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):schedule:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Namespace]:
        if data is None:
            return None
        return Namespace()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }