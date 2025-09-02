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


class ScriptSetting(core.Gs2Model):
    trigger_script_id: str = None
    done_trigger_target_type: str = None
    done_trigger_script_id: str = None
    done_trigger_queue_namespace_id: str = None

    def with_trigger_script_id(self, trigger_script_id: str) -> ScriptSetting:
        self.trigger_script_id = trigger_script_id
        return self

    def with_done_trigger_target_type(self, done_trigger_target_type: str) -> ScriptSetting:
        self.done_trigger_target_type = done_trigger_target_type
        return self

    def with_done_trigger_script_id(self, done_trigger_script_id: str) -> ScriptSetting:
        self.done_trigger_script_id = done_trigger_script_id
        return self

    def with_done_trigger_queue_namespace_id(self, done_trigger_queue_namespace_id: str) -> ScriptSetting:
        self.done_trigger_queue_namespace_id = done_trigger_queue_namespace_id
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
    ) -> Optional[ScriptSetting]:
        if data is None:
            return None
        return ScriptSetting()\
            .with_trigger_script_id(data.get('triggerScriptId'))\
            .with_done_trigger_target_type(data.get('doneTriggerTargetType'))\
            .with_done_trigger_script_id(data.get('doneTriggerScriptId'))\
            .with_done_trigger_queue_namespace_id(data.get('doneTriggerQueueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggerScriptId": self.trigger_script_id,
            "doneTriggerTargetType": self.done_trigger_target_type,
            "doneTriggerScriptId": self.done_trigger_script_id,
            "doneTriggerQueueNamespaceId": self.done_trigger_queue_namespace_id,
        }


class TransactionSetting(core.Gs2Model):
    enable_auto_run: bool = None
    enable_atomic_commit: bool = None
    transaction_use_distributor: bool = None
    acquire_action_use_job_queue: bool = None
    distributor_namespace_id: str = None
    key_id: str = None
    queue_namespace_id: str = None

    def with_enable_auto_run(self, enable_auto_run: bool) -> TransactionSetting:
        self.enable_auto_run = enable_auto_run
        return self

    def with_enable_atomic_commit(self, enable_atomic_commit: bool) -> TransactionSetting:
        self.enable_atomic_commit = enable_atomic_commit
        return self

    def with_transaction_use_distributor(self, transaction_use_distributor: bool) -> TransactionSetting:
        self.transaction_use_distributor = transaction_use_distributor
        return self

    def with_acquire_action_use_job_queue(self, acquire_action_use_job_queue: bool) -> TransactionSetting:
        self.acquire_action_use_job_queue = acquire_action_use_job_queue
        return self

    def with_distributor_namespace_id(self, distributor_namespace_id: str) -> TransactionSetting:
        self.distributor_namespace_id = distributor_namespace_id
        return self

    def with_key_id(self, key_id: str) -> TransactionSetting:
        self.key_id = key_id
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> TransactionSetting:
        self.queue_namespace_id = queue_namespace_id
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
    ) -> Optional[TransactionSetting]:
        if data is None:
            return None
        return TransactionSetting()\
            .with_enable_auto_run(data.get('enableAutoRun'))\
            .with_enable_atomic_commit(data.get('enableAtomicCommit'))\
            .with_transaction_use_distributor(data.get('transactionUseDistributor'))\
            .with_acquire_action_use_job_queue(data.get('acquireActionUseJobQueue'))\
            .with_distributor_namespace_id(data.get('distributorNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enableAutoRun": self.enable_auto_run,
            "enableAtomicCommit": self.enable_atomic_commit,
            "transactionUseDistributor": self.transaction_use_distributor,
            "acquireActionUseJobQueue": self.acquire_action_use_job_queue,
            "distributorNamespaceId": self.distributor_namespace_id,
            "keyId": self.key_id,
            "queueNamespaceId": self.queue_namespace_id,
        }


class AcquireActionList(core.Gs2Model):
    acquire_actions: List[AcquireAction] = None

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> AcquireActionList:
        self.acquire_actions = acquire_actions
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
    ) -> Optional[AcquireActionList]:
        if data is None:
            return None
        return AcquireActionList()\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class AcquireAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> AcquireAction:
        self.action = action
        return self

    def with_request(self, request: str) -> AcquireAction:
        self.request = request
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
    ) -> Optional[AcquireAction]:
        if data is None:
            return None
        return AcquireAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class Config(core.Gs2Model):
    key: str = None
    value: str = None

    def with_key(self, key: str) -> Config:
        self.key = key
        return self

    def with_value(self, value: str) -> Config:
        self.value = value
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
    ) -> Optional[Config]:
        if data is None:
            return None
        return Config()\
            .with_key(data.get('key'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
        }


class CurrentCategoryMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentCategoryMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentCategoryMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:idle:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentCategoryMaster]:
        if data is None:
            return None
        return CurrentCategoryMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class Status(core.Gs2Model):
    status_id: str = None
    category_name: str = None
    user_id: str = None
    random_seed: int = None
    idle_minutes: int = None
    next_rewards_at: int = None
    maximum_idle_minutes: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_status_id(self, status_id: str) -> Status:
        self.status_id = status_id
        return self

    def with_category_name(self, category_name: str) -> Status:
        self.category_name = category_name
        return self

    def with_user_id(self, user_id: str) -> Status:
        self.user_id = user_id
        return self

    def with_random_seed(self, random_seed: int) -> Status:
        self.random_seed = random_seed
        return self

    def with_idle_minutes(self, idle_minutes: int) -> Status:
        self.idle_minutes = idle_minutes
        return self

    def with_next_rewards_at(self, next_rewards_at: int) -> Status:
        self.next_rewards_at = next_rewards_at
        return self

    def with_maximum_idle_minutes(self, maximum_idle_minutes: int) -> Status:
        self.maximum_idle_minutes = maximum_idle_minutes
        return self

    def with_created_at(self, created_at: int) -> Status:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Status:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Status:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        category_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:idle:{namespaceName}:user:{userId}:categoryModel:{categoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            categoryName=category_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):user:(?P<userId>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):user:(?P<userId>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):user:(?P<userId>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):user:(?P<userId>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_category_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):user:(?P<userId>.+):categoryModel:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('category_name')

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
    ) -> Optional[Status]:
        if data is None:
            return None
        return Status()\
            .with_status_id(data.get('statusId'))\
            .with_category_name(data.get('categoryName'))\
            .with_user_id(data.get('userId'))\
            .with_random_seed(data.get('randomSeed'))\
            .with_idle_minutes(data.get('idleMinutes'))\
            .with_next_rewards_at(data.get('nextRewardsAt'))\
            .with_maximum_idle_minutes(data.get('maximumIdleMinutes'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statusId": self.status_id,
            "categoryName": self.category_name,
            "userId": self.user_id,
            "randomSeed": self.random_seed,
            "idleMinutes": self.idle_minutes,
            "nextRewardsAt": self.next_rewards_at,
            "maximumIdleMinutes": self.maximum_idle_minutes,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class CategoryModel(core.Gs2Model):
    category_model_id: str = None
    name: str = None
    metadata: str = None
    reward_interval_minutes: int = None
    default_maximum_idle_minutes: int = None
    reward_reset_mode: str = None
    acquire_actions: List[AcquireActionList] = None
    idle_period_schedule_id: str = None
    receive_period_schedule_id: str = None

    def with_category_model_id(self, category_model_id: str) -> CategoryModel:
        self.category_model_id = category_model_id
        return self

    def with_name(self, name: str) -> CategoryModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CategoryModel:
        self.metadata = metadata
        return self

    def with_reward_interval_minutes(self, reward_interval_minutes: int) -> CategoryModel:
        self.reward_interval_minutes = reward_interval_minutes
        return self

    def with_default_maximum_idle_minutes(self, default_maximum_idle_minutes: int) -> CategoryModel:
        self.default_maximum_idle_minutes = default_maximum_idle_minutes
        return self

    def with_reward_reset_mode(self, reward_reset_mode: str) -> CategoryModel:
        self.reward_reset_mode = reward_reset_mode
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireActionList]) -> CategoryModel:
        self.acquire_actions = acquire_actions
        return self

    def with_idle_period_schedule_id(self, idle_period_schedule_id: str) -> CategoryModel:
        self.idle_period_schedule_id = idle_period_schedule_id
        return self

    def with_receive_period_schedule_id(self, receive_period_schedule_id: str) -> CategoryModel:
        self.receive_period_schedule_id = receive_period_schedule_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        category_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:idle:{namespaceName}:model:{categoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            categoryName=category_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):model:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):model:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):model:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_category_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):model:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('category_name')

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
    ) -> Optional[CategoryModel]:
        if data is None:
            return None
        return CategoryModel()\
            .with_category_model_id(data.get('categoryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_reward_interval_minutes(data.get('rewardIntervalMinutes'))\
            .with_default_maximum_idle_minutes(data.get('defaultMaximumIdleMinutes'))\
            .with_reward_reset_mode(data.get('rewardResetMode'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireActionList.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_idle_period_schedule_id(data.get('idlePeriodScheduleId'))\
            .with_receive_period_schedule_id(data.get('receivePeriodScheduleId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoryModelId": self.category_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "rewardIntervalMinutes": self.reward_interval_minutes,
            "defaultMaximumIdleMinutes": self.default_maximum_idle_minutes,
            "rewardResetMode": self.reward_reset_mode,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "idlePeriodScheduleId": self.idle_period_schedule_id,
            "receivePeriodScheduleId": self.receive_period_schedule_id,
        }


class CategoryModelMaster(core.Gs2Model):
    category_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    reward_interval_minutes: int = None
    default_maximum_idle_minutes: int = None
    reward_reset_mode: str = None
    acquire_actions: List[AcquireActionList] = None
    idle_period_schedule_id: str = None
    receive_period_schedule_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_category_model_id(self, category_model_id: str) -> CategoryModelMaster:
        self.category_model_id = category_model_id
        return self

    def with_name(self, name: str) -> CategoryModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> CategoryModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CategoryModelMaster:
        self.metadata = metadata
        return self

    def with_reward_interval_minutes(self, reward_interval_minutes: int) -> CategoryModelMaster:
        self.reward_interval_minutes = reward_interval_minutes
        return self

    def with_default_maximum_idle_minutes(self, default_maximum_idle_minutes: int) -> CategoryModelMaster:
        self.default_maximum_idle_minutes = default_maximum_idle_minutes
        return self

    def with_reward_reset_mode(self, reward_reset_mode: str) -> CategoryModelMaster:
        self.reward_reset_mode = reward_reset_mode
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireActionList]) -> CategoryModelMaster:
        self.acquire_actions = acquire_actions
        return self

    def with_idle_period_schedule_id(self, idle_period_schedule_id: str) -> CategoryModelMaster:
        self.idle_period_schedule_id = idle_period_schedule_id
        return self

    def with_receive_period_schedule_id(self, receive_period_schedule_id: str) -> CategoryModelMaster:
        self.receive_period_schedule_id = receive_period_schedule_id
        return self

    def with_created_at(self, created_at: int) -> CategoryModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> CategoryModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> CategoryModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        category_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:idle:{namespaceName}:model:{categoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            categoryName=category_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):model:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):model:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):model:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_category_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+):model:(?P<categoryName>.+)', grn)
        if match is None:
            return None
        return match.group('category_name')

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
    ) -> Optional[CategoryModelMaster]:
        if data is None:
            return None
        return CategoryModelMaster()\
            .with_category_model_id(data.get('categoryModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_reward_interval_minutes(data.get('rewardIntervalMinutes'))\
            .with_default_maximum_idle_minutes(data.get('defaultMaximumIdleMinutes'))\
            .with_reward_reset_mode(data.get('rewardResetMode'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireActionList.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_idle_period_schedule_id(data.get('idlePeriodScheduleId'))\
            .with_receive_period_schedule_id(data.get('receivePeriodScheduleId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoryModelId": self.category_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "rewardIntervalMinutes": self.reward_interval_minutes,
            "defaultMaximumIdleMinutes": self.default_maximum_idle_minutes,
            "rewardResetMode": self.reward_reset_mode,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "idlePeriodScheduleId": self.idle_period_schedule_id,
            "receivePeriodScheduleId": self.receive_period_schedule_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    receive_script: ScriptSetting = None
    override_acquire_actions_script_id: str = None
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

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
        return self

    def with_receive_script(self, receive_script: ScriptSetting) -> Namespace:
        self.receive_script = receive_script
        return self

    def with_override_acquire_actions_script_id(self, override_acquire_actions_script_id: str) -> Namespace:
        self.override_acquire_actions_script_id = override_acquire_actions_script_id
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
        return 'grn:gs2:{region}:{ownerId}:idle:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):idle:(?P<namespaceName>.+)', grn)
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
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_receive_script(ScriptSetting.from_dict(data.get('receiveScript')))\
            .with_override_acquire_actions_script_id(data.get('overrideAcquireActionsScriptId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "receiveScript": self.receive_script.to_dict() if self.receive_script else None,
            "overrideAcquireActionsScriptId": self.override_acquire_actions_script_id,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }