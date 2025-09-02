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


class VerifyAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> VerifyAction:
        self.action = action
        return self

    def with_request(self, request: str) -> VerifyAction:
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
    ) -> Optional[VerifyAction]:
        if data is None:
            return None
        return VerifyAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class ConsumeAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> ConsumeAction:
        self.action = action
        return self

    def with_request(self, request: str) -> ConsumeAction:
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
    ) -> Optional[ConsumeAction]:
        if data is None:
            return None
        return ConsumeAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
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


class LogRate(core.Gs2Model):
    base: float = None
    logs: List[float] = None

    def with_base(self, base: float) -> LogRate:
        self.base = base
        return self

    def with_logs(self, logs: List[float]) -> LogRate:
        self.logs = logs
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
    ) -> Optional[LogRate]:
        if data is None:
            return None
        return LogRate()\
            .with_base(data.get('base'))\
            .with_logs(None if data.get('logs') is None else [
                data.get('logs')[i]
                for i in range(len(data.get('logs')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base": self.base,
            "logs": None if self.logs is None else [
                self.logs[i]
                for i in range(len(self.logs))
            ],
        }


class LogCost(core.Gs2Model):
    base: float = None
    adds: List[float] = None
    subs: List[float] = None

    def with_base(self, base: float) -> LogCost:
        self.base = base
        return self

    def with_adds(self, adds: List[float]) -> LogCost:
        self.adds = adds
        return self

    def with_subs(self, subs: List[float]) -> LogCost:
        self.subs = subs
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
    ) -> Optional[LogCost]:
        if data is None:
            return None
        return LogCost()\
            .with_base(data.get('base'))\
            .with_adds(None if data.get('adds') is None else [
                data.get('adds')[i]
                for i in range(len(data.get('adds')))
            ])\
            .with_subs(None if data.get('subs') is None else [
                data.get('subs')[i]
                for i in range(len(data.get('subs')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "base": self.base,
            "adds": None if self.adds is None else [
                self.adds[i]
                for i in range(len(self.adds))
            ],
            "subs": None if self.subs is None else [
                self.subs[i]
                for i in range(len(self.subs))
            ],
        }


class Await(core.Gs2Model):
    await_id: str = None
    user_id: str = None
    rate_name: str = None
    name: str = None
    count: int = None
    skip_seconds: int = None
    config: List[Config] = None
    acquirable_at: int = None
    exchanged_at: int = None
    created_at: int = None
    revision: int = None

    def with_await_id(self, await_id: str) -> Await:
        self.await_id = await_id
        return self

    def with_user_id(self, user_id: str) -> Await:
        self.user_id = user_id
        return self

    def with_rate_name(self, rate_name: str) -> Await:
        self.rate_name = rate_name
        return self

    def with_name(self, name: str) -> Await:
        self.name = name
        return self

    def with_count(self, count: int) -> Await:
        self.count = count
        return self

    def with_skip_seconds(self, skip_seconds: int) -> Await:
        self.skip_seconds = skip_seconds
        return self

    def with_config(self, config: List[Config]) -> Await:
        self.config = config
        return self

    def with_acquirable_at(self, acquirable_at: int) -> Await:
        self.acquirable_at = acquirable_at
        return self

    def with_exchanged_at(self, exchanged_at: int) -> Await:
        self.exchanged_at = exchanged_at
        return self

    def with_created_at(self, created_at: int) -> Await:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Await:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        await_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}:user:{userId}:await:{awaitName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            awaitName=await_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_await_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):user:(?P<userId>.+):await:(?P<awaitName>.+)', grn)
        if match is None:
            return None
        return match.group('await_name')

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
    ) -> Optional[Await]:
        if data is None:
            return None
        return Await()\
            .with_await_id(data.get('awaitId'))\
            .with_user_id(data.get('userId'))\
            .with_rate_name(data.get('rateName'))\
            .with_name(data.get('name'))\
            .with_count(data.get('count'))\
            .with_skip_seconds(data.get('skipSeconds'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_acquirable_at(data.get('acquirableAt'))\
            .with_exchanged_at(data.get('exchangedAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "awaitId": self.await_id,
            "userId": self.user_id,
            "rateName": self.rate_name,
            "name": self.name,
            "count": self.count,
            "skipSeconds": self.skip_seconds,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "acquirableAt": self.acquirable_at,
            "exchangedAt": self.exchanged_at,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class CurrentRateMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentRateMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentRateMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentRateMaster]:
        if data is None:
            return None
        return CurrentRateMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class IncrementalRateModelMaster(core.Gs2Model):
    incremental_rate_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    consume_action: ConsumeAction = None
    calculate_type: str = None
    base_value: int = None
    coefficient_value: int = None
    calculate_script_id: str = None
    exchange_count_id: str = None
    maximum_exchange_count: int = None
    acquire_actions: List[AcquireAction] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_incremental_rate_model_id(self, incremental_rate_model_id: str) -> IncrementalRateModelMaster:
        self.incremental_rate_model_id = incremental_rate_model_id
        return self

    def with_name(self, name: str) -> IncrementalRateModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> IncrementalRateModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> IncrementalRateModelMaster:
        self.metadata = metadata
        return self

    def with_consume_action(self, consume_action: ConsumeAction) -> IncrementalRateModelMaster:
        self.consume_action = consume_action
        return self

    def with_calculate_type(self, calculate_type: str) -> IncrementalRateModelMaster:
        self.calculate_type = calculate_type
        return self

    def with_base_value(self, base_value: int) -> IncrementalRateModelMaster:
        self.base_value = base_value
        return self

    def with_coefficient_value(self, coefficient_value: int) -> IncrementalRateModelMaster:
        self.coefficient_value = coefficient_value
        return self

    def with_calculate_script_id(self, calculate_script_id: str) -> IncrementalRateModelMaster:
        self.calculate_script_id = calculate_script_id
        return self

    def with_exchange_count_id(self, exchange_count_id: str) -> IncrementalRateModelMaster:
        self.exchange_count_id = exchange_count_id
        return self

    def with_maximum_exchange_count(self, maximum_exchange_count: int) -> IncrementalRateModelMaster:
        self.maximum_exchange_count = maximum_exchange_count
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> IncrementalRateModelMaster:
        self.acquire_actions = acquire_actions
        return self

    def with_created_at(self, created_at: int) -> IncrementalRateModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> IncrementalRateModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> IncrementalRateModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rate_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}:incremental:model:{rateName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rateName=rate_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):incremental:model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):incremental:model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):incremental:model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):incremental:model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('rate_name')

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
    ) -> Optional[IncrementalRateModelMaster]:
        if data is None:
            return None
        return IncrementalRateModelMaster()\
            .with_incremental_rate_model_id(data.get('incrementalRateModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_consume_action(ConsumeAction.from_dict(data.get('consumeAction')))\
            .with_calculate_type(data.get('calculateType'))\
            .with_base_value(data.get('baseValue'))\
            .with_coefficient_value(data.get('coefficientValue'))\
            .with_calculate_script_id(data.get('calculateScriptId'))\
            .with_exchange_count_id(data.get('exchangeCountId'))\
            .with_maximum_exchange_count(data.get('maximumExchangeCount'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incrementalRateModelId": self.incremental_rate_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "consumeAction": self.consume_action.to_dict() if self.consume_action else None,
            "calculateType": self.calculate_type,
            "baseValue": self.base_value,
            "coefficientValue": self.coefficient_value,
            "calculateScriptId": self.calculate_script_id,
            "exchangeCountId": self.exchange_count_id,
            "maximumExchangeCount": self.maximum_exchange_count,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class IncrementalRateModel(core.Gs2Model):
    incremental_rate_model_id: str = None
    name: str = None
    metadata: str = None
    consume_action: ConsumeAction = None
    calculate_type: str = None
    base_value: int = None
    coefficient_value: int = None
    calculate_script_id: str = None
    exchange_count_id: str = None
    maximum_exchange_count: int = None
    acquire_actions: List[AcquireAction] = None

    def with_incremental_rate_model_id(self, incremental_rate_model_id: str) -> IncrementalRateModel:
        self.incremental_rate_model_id = incremental_rate_model_id
        return self

    def with_name(self, name: str) -> IncrementalRateModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> IncrementalRateModel:
        self.metadata = metadata
        return self

    def with_consume_action(self, consume_action: ConsumeAction) -> IncrementalRateModel:
        self.consume_action = consume_action
        return self

    def with_calculate_type(self, calculate_type: str) -> IncrementalRateModel:
        self.calculate_type = calculate_type
        return self

    def with_base_value(self, base_value: int) -> IncrementalRateModel:
        self.base_value = base_value
        return self

    def with_coefficient_value(self, coefficient_value: int) -> IncrementalRateModel:
        self.coefficient_value = coefficient_value
        return self

    def with_calculate_script_id(self, calculate_script_id: str) -> IncrementalRateModel:
        self.calculate_script_id = calculate_script_id
        return self

    def with_exchange_count_id(self, exchange_count_id: str) -> IncrementalRateModel:
        self.exchange_count_id = exchange_count_id
        return self

    def with_maximum_exchange_count(self, maximum_exchange_count: int) -> IncrementalRateModel:
        self.maximum_exchange_count = maximum_exchange_count
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> IncrementalRateModel:
        self.acquire_actions = acquire_actions
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rate_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}:incremental:model:{rateName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rateName=rate_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):incremental:model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):incremental:model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):incremental:model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):incremental:model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('rate_name')

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
    ) -> Optional[IncrementalRateModel]:
        if data is None:
            return None
        return IncrementalRateModel()\
            .with_incremental_rate_model_id(data.get('incrementalRateModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_consume_action(ConsumeAction.from_dict(data.get('consumeAction')))\
            .with_calculate_type(data.get('calculateType'))\
            .with_base_value(data.get('baseValue'))\
            .with_coefficient_value(data.get('coefficientValue'))\
            .with_calculate_script_id(data.get('calculateScriptId'))\
            .with_exchange_count_id(data.get('exchangeCountId'))\
            .with_maximum_exchange_count(data.get('maximumExchangeCount'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incrementalRateModelId": self.incremental_rate_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "consumeAction": self.consume_action.to_dict() if self.consume_action else None,
            "calculateType": self.calculate_type,
            "baseValue": self.base_value,
            "coefficientValue": self.coefficient_value,
            "calculateScriptId": self.calculate_script_id,
            "exchangeCountId": self.exchange_count_id,
            "maximumExchangeCount": self.maximum_exchange_count,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class RateModelMaster(core.Gs2Model):
    rate_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    timing_type: str = None
    lock_time: int = None
    acquire_actions: List[AcquireAction] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_rate_model_id(self, rate_model_id: str) -> RateModelMaster:
        self.rate_model_id = rate_model_id
        return self

    def with_name(self, name: str) -> RateModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> RateModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> RateModelMaster:
        self.metadata = metadata
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> RateModelMaster:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> RateModelMaster:
        self.consume_actions = consume_actions
        return self

    def with_timing_type(self, timing_type: str) -> RateModelMaster:
        self.timing_type = timing_type
        return self

    def with_lock_time(self, lock_time: int) -> RateModelMaster:
        self.lock_time = lock_time
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> RateModelMaster:
        self.acquire_actions = acquire_actions
        return self

    def with_created_at(self, created_at: int) -> RateModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> RateModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> RateModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rate_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}:model:{rateName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rateName=rate_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('rate_name')

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
    ) -> Optional[RateModelMaster]:
        if data is None:
            return None
        return RateModelMaster()\
            .with_rate_model_id(data.get('rateModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_timing_type(data.get('timingType'))\
            .with_lock_time(data.get('lockTime'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rateModelId": self.rate_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "timingType": self.timing_type,
            "lockTime": self.lock_time,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class RateModel(core.Gs2Model):
    rate_model_id: str = None
    name: str = None
    metadata: str = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    timing_type: str = None
    lock_time: int = None
    acquire_actions: List[AcquireAction] = None

    def with_rate_model_id(self, rate_model_id: str) -> RateModel:
        self.rate_model_id = rate_model_id
        return self

    def with_name(self, name: str) -> RateModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RateModel:
        self.metadata = metadata
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> RateModel:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> RateModel:
        self.consume_actions = consume_actions
        return self

    def with_timing_type(self, timing_type: str) -> RateModel:
        self.timing_type = timing_type
        return self

    def with_lock_time(self, lock_time: int) -> RateModel:
        self.lock_time = lock_time
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> RateModel:
        self.acquire_actions = acquire_actions
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rate_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}:model:{rateName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rateName=rate_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+):model:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('rate_name')

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
    ) -> Optional[RateModel]:
        if data is None:
            return None
        return RateModel()\
            .with_rate_model_id(data.get('rateModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_timing_type(data.get('timingType'))\
            .with_lock_time(data.get('lockTime'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rateModelId": self.rate_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "timingType": self.timing_type,
            "lockTime": self.lock_time,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    enable_direct_exchange: bool = None
    enable_await_exchange: bool = None
    transaction_setting: TransactionSetting = None
    exchange_script: ScriptSetting = None
    incremental_exchange_script: ScriptSetting = None
    acquire_await_script: ScriptSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    queue_namespace_id: str = None
    key_id: str = None
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

    def with_enable_direct_exchange(self, enable_direct_exchange: bool) -> Namespace:
        self.enable_direct_exchange = enable_direct_exchange
        return self

    def with_enable_await_exchange(self, enable_await_exchange: bool) -> Namespace:
        self.enable_await_exchange = enable_await_exchange
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
        return self

    def with_exchange_script(self, exchange_script: ScriptSetting) -> Namespace:
        self.exchange_script = exchange_script
        return self

    def with_incremental_exchange_script(self, incremental_exchange_script: ScriptSetting) -> Namespace:
        self.incremental_exchange_script = incremental_exchange_script
        return self

    def with_acquire_await_script(self, acquire_await_script: ScriptSetting) -> Namespace:
        self.acquire_await_script = acquire_await_script
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

    def with_queue_namespace_id(self, queue_namespace_id: str) -> Namespace:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> Namespace:
        self.key_id = key_id
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
        return 'grn:gs2:{region}:{ownerId}:exchange:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):exchange:(?P<namespaceName>.+)', grn)
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
            .with_enable_direct_exchange(data.get('enableDirectExchange'))\
            .with_enable_await_exchange(data.get('enableAwaitExchange'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_exchange_script(ScriptSetting.from_dict(data.get('exchangeScript')))\
            .with_incremental_exchange_script(ScriptSetting.from_dict(data.get('incrementalExchangeScript')))\
            .with_acquire_await_script(ScriptSetting.from_dict(data.get('acquireAwaitScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "enableDirectExchange": self.enable_direct_exchange,
            "enableAwaitExchange": self.enable_await_exchange,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "exchangeScript": self.exchange_script.to_dict() if self.exchange_script else None,
            "incrementalExchangeScript": self.incremental_exchange_script.to_dict() if self.incremental_exchange_script else None,
            "acquireAwaitScript": self.acquire_await_script.to_dict() if self.acquire_await_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
            "revision": self.revision,
        }