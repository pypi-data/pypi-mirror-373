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


class LimitModel(core.Gs2Model):
    limit_model_id: str = None
    name: str = None
    metadata: str = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None
    anchor_timestamp: int = None
    days: int = None

    def with_limit_model_id(self, limit_model_id: str) -> LimitModel:
        self.limit_model_id = limit_model_id
        return self

    def with_name(self, name: str) -> LimitModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> LimitModel:
        self.metadata = metadata
        return self

    def with_reset_type(self, reset_type: str) -> LimitModel:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> LimitModel:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> LimitModel:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> LimitModel:
        self.reset_hour = reset_hour
        return self

    def with_anchor_timestamp(self, anchor_timestamp: int) -> LimitModel:
        self.anchor_timestamp = anchor_timestamp
        return self

    def with_days(self, days: int) -> LimitModel:
        self.days = days
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        limit_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:limit:{namespaceName}:limit:{limitName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            limitName=limit_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):limit:(?P<limitName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):limit:(?P<limitName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):limit:(?P<limitName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_limit_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):limit:(?P<limitName>.+)', grn)
        if match is None:
            return None
        return match.group('limit_name')

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
    ) -> Optional[LimitModel]:
        if data is None:
            return None
        return LimitModel()\
            .with_limit_model_id(data.get('limitModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_anchor_timestamp(data.get('anchorTimestamp'))\
            .with_days(data.get('days'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "limitModelId": self.limit_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
            "anchorTimestamp": self.anchor_timestamp,
            "days": self.days,
        }


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


class CurrentLimitMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentLimitMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentLimitMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:limit:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentLimitMaster]:
        if data is None:
            return None
        return CurrentLimitMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class LimitModelMaster(core.Gs2Model):
    limit_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None
    anchor_timestamp: int = None
    days: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_limit_model_id(self, limit_model_id: str) -> LimitModelMaster:
        self.limit_model_id = limit_model_id
        return self

    def with_name(self, name: str) -> LimitModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> LimitModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> LimitModelMaster:
        self.metadata = metadata
        return self

    def with_reset_type(self, reset_type: str) -> LimitModelMaster:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> LimitModelMaster:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> LimitModelMaster:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> LimitModelMaster:
        self.reset_hour = reset_hour
        return self

    def with_anchor_timestamp(self, anchor_timestamp: int) -> LimitModelMaster:
        self.anchor_timestamp = anchor_timestamp
        return self

    def with_days(self, days: int) -> LimitModelMaster:
        self.days = days
        return self

    def with_created_at(self, created_at: int) -> LimitModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> LimitModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> LimitModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        limit_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:limit:{namespaceName}:limit:{limitName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            limitName=limit_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):limit:(?P<limitName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):limit:(?P<limitName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):limit:(?P<limitName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_limit_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):limit:(?P<limitName>.+)', grn)
        if match is None:
            return None
        return match.group('limit_name')

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
    ) -> Optional[LimitModelMaster]:
        if data is None:
            return None
        return LimitModelMaster()\
            .with_limit_model_id(data.get('limitModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_anchor_timestamp(data.get('anchorTimestamp'))\
            .with_days(data.get('days'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "limitModelId": self.limit_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
            "anchorTimestamp": self.anchor_timestamp,
            "days": self.days,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Counter(core.Gs2Model):
    counter_id: str = None
    limit_name: str = None
    name: str = None
    user_id: str = None
    count: int = None
    next_reset_at: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_counter_id(self, counter_id: str) -> Counter:
        self.counter_id = counter_id
        return self

    def with_limit_name(self, limit_name: str) -> Counter:
        self.limit_name = limit_name
        return self

    def with_name(self, name: str) -> Counter:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> Counter:
        self.user_id = user_id
        return self

    def with_count(self, count: int) -> Counter:
        self.count = count
        return self

    def with_next_reset_at(self, next_reset_at: int) -> Counter:
        self.next_reset_at = next_reset_at
        return self

    def with_created_at(self, created_at: int) -> Counter:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Counter:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Counter:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        limit_name,
        counter_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:limit:{namespaceName}:user:{userId}:limit:{limitName}:counter:{counterName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            limitName=limit_name,
            counterName=counter_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):user:(?P<userId>.+):limit:(?P<limitName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):user:(?P<userId>.+):limit:(?P<limitName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):user:(?P<userId>.+):limit:(?P<limitName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):user:(?P<userId>.+):limit:(?P<limitName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_limit_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):user:(?P<userId>.+):limit:(?P<limitName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('limit_name')

    @classmethod
    def get_counter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+):user:(?P<userId>.+):limit:(?P<limitName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('counter_name')

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
    ) -> Optional[Counter]:
        if data is None:
            return None
        return Counter()\
            .with_counter_id(data.get('counterId'))\
            .with_limit_name(data.get('limitName'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_count(data.get('count'))\
            .with_next_reset_at(data.get('nextResetAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counterId": self.counter_id,
            "limitName": self.limit_name,
            "name": self.name,
            "userId": self.user_id,
            "count": self.count,
            "nextResetAt": self.next_reset_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
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
        return 'grn:gs2:{region}:{ownerId}:limit:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):limit:(?P<namespaceName>.+)', grn)
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