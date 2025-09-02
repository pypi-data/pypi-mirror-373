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


class TargetCounterModel(core.Gs2Model):
    counter_name: str = None
    scope_type: str = None
    reset_type: str = None
    condition_name: str = None
    value: int = None

    def with_counter_name(self, counter_name: str) -> TargetCounterModel:
        self.counter_name = counter_name
        return self

    def with_scope_type(self, scope_type: str) -> TargetCounterModel:
        self.scope_type = scope_type
        return self

    def with_reset_type(self, reset_type: str) -> TargetCounterModel:
        self.reset_type = reset_type
        return self

    def with_condition_name(self, condition_name: str) -> TargetCounterModel:
        self.condition_name = condition_name
        return self

    def with_value(self, value: int) -> TargetCounterModel:
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
    ) -> Optional[TargetCounterModel]:
        if data is None:
            return None
        return TargetCounterModel()\
            .with_counter_name(data.get('counterName'))\
            .with_scope_type(data.get('scopeType'))\
            .with_reset_type(data.get('resetType'))\
            .with_condition_name(data.get('conditionName'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counterName": self.counter_name,
            "scopeType": self.scope_type,
            "resetType": self.reset_type,
            "conditionName": self.condition_name,
            "value": self.value,
        }


class ScopedValue(core.Gs2Model):
    scope_type: str = None
    reset_type: str = None
    condition_name: str = None
    value: int = None
    next_reset_at: int = None
    updated_at: int = None

    def with_scope_type(self, scope_type: str) -> ScopedValue:
        self.scope_type = scope_type
        return self

    def with_reset_type(self, reset_type: str) -> ScopedValue:
        self.reset_type = reset_type
        return self

    def with_condition_name(self, condition_name: str) -> ScopedValue:
        self.condition_name = condition_name
        return self

    def with_value(self, value: int) -> ScopedValue:
        self.value = value
        return self

    def with_next_reset_at(self, next_reset_at: int) -> ScopedValue:
        self.next_reset_at = next_reset_at
        return self

    def with_updated_at(self, updated_at: int) -> ScopedValue:
        self.updated_at = updated_at
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
    ) -> Optional[ScopedValue]:
        if data is None:
            return None
        return ScopedValue()\
            .with_scope_type(data.get('scopeType'))\
            .with_reset_type(data.get('resetType'))\
            .with_condition_name(data.get('conditionName'))\
            .with_value(data.get('value'))\
            .with_next_reset_at(data.get('nextResetAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scopeType": self.scope_type,
            "resetType": self.reset_type,
            "conditionName": self.condition_name,
            "value": self.value,
            "nextResetAt": self.next_reset_at,
            "updatedAt": self.updated_at,
        }


class MissionTaskModelMaster(core.Gs2Model):
    mission_task_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    verify_complete_type: str = None
    target_counter: TargetCounterModel = None
    verify_complete_consume_actions: List[VerifyAction] = None
    complete_acquire_actions: List[AcquireAction] = None
    challenge_period_event_id: str = None
    premise_mission_task_name: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None
    counter_name: str = None
    target_reset_type: str = None
    target_value: int = None

    def with_mission_task_id(self, mission_task_id: str) -> MissionTaskModelMaster:
        self.mission_task_id = mission_task_id
        return self

    def with_name(self, name: str) -> MissionTaskModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> MissionTaskModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> MissionTaskModelMaster:
        self.description = description
        return self

    def with_verify_complete_type(self, verify_complete_type: str) -> MissionTaskModelMaster:
        self.verify_complete_type = verify_complete_type
        return self

    def with_target_counter(self, target_counter: TargetCounterModel) -> MissionTaskModelMaster:
        self.target_counter = target_counter
        return self

    def with_verify_complete_consume_actions(self, verify_complete_consume_actions: List[VerifyAction]) -> MissionTaskModelMaster:
        self.verify_complete_consume_actions = verify_complete_consume_actions
        return self

    def with_complete_acquire_actions(self, complete_acquire_actions: List[AcquireAction]) -> MissionTaskModelMaster:
        self.complete_acquire_actions = complete_acquire_actions
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> MissionTaskModelMaster:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_premise_mission_task_name(self, premise_mission_task_name: str) -> MissionTaskModelMaster:
        self.premise_mission_task_name = premise_mission_task_name
        return self

    def with_created_at(self, created_at: int) -> MissionTaskModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> MissionTaskModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> MissionTaskModelMaster:
        self.revision = revision
        return self

    def with_counter_name(self, counter_name: str) -> MissionTaskModelMaster:
        self.counter_name = counter_name
        return self

    def with_target_reset_type(self, target_reset_type: str) -> MissionTaskModelMaster:
        self.target_reset_type = target_reset_type
        return self

    def with_target_value(self, target_value: int) -> MissionTaskModelMaster:
        self.target_value = target_value
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        mission_group_name,
        mission_task_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}:group:{missionGroupName}:missionTaskModelMaster:{missionTaskName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            missionGroupName=mission_group_name,
            missionTaskName=mission_task_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModelMaster:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModelMaster:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModelMaster:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_mission_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModelMaster:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('mission_group_name')

    @classmethod
    def get_mission_task_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModelMaster:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('mission_task_name')

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
    ) -> Optional[MissionTaskModelMaster]:
        if data is None:
            return None
        return MissionTaskModelMaster()\
            .with_mission_task_id(data.get('missionTaskId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_verify_complete_type(data.get('verifyCompleteType'))\
            .with_target_counter(TargetCounterModel.from_dict(data.get('targetCounter')))\
            .with_verify_complete_consume_actions(None if data.get('verifyCompleteConsumeActions') is None else [
                VerifyAction.from_dict(data.get('verifyCompleteConsumeActions')[i])
                for i in range(len(data.get('verifyCompleteConsumeActions')))
            ])\
            .with_complete_acquire_actions(None if data.get('completeAcquireActions') is None else [
                AcquireAction.from_dict(data.get('completeAcquireActions')[i])
                for i in range(len(data.get('completeAcquireActions')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_premise_mission_task_name(data.get('premiseMissionTaskName'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))\
            .with_counter_name(data.get('counterName'))\
            .with_target_reset_type(data.get('targetResetType'))\
            .with_target_value(data.get('targetValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "missionTaskId": self.mission_task_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "verifyCompleteType": self.verify_complete_type,
            "targetCounter": self.target_counter.to_dict() if self.target_counter else None,
            "verifyCompleteConsumeActions": None if self.verify_complete_consume_actions is None else [
                self.verify_complete_consume_actions[i].to_dict() if self.verify_complete_consume_actions[i] else None
                for i in range(len(self.verify_complete_consume_actions))
            ],
            "completeAcquireActions": None if self.complete_acquire_actions is None else [
                self.complete_acquire_actions[i].to_dict() if self.complete_acquire_actions[i] else None
                for i in range(len(self.complete_acquire_actions))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "premiseMissionTaskName": self.premise_mission_task_name,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
            "counterName": self.counter_name,
            "targetResetType": self.target_reset_type,
            "targetValue": self.target_value,
        }


class MissionTaskModel(core.Gs2Model):
    mission_task_id: str = None
    name: str = None
    metadata: str = None
    verify_complete_type: str = None
    target_counter: TargetCounterModel = None
    verify_complete_consume_actions: List[VerifyAction] = None
    complete_acquire_actions: List[AcquireAction] = None
    challenge_period_event_id: str = None
    premise_mission_task_name: str = None
    counter_name: str = None
    target_reset_type: str = None
    target_value: int = None

    def with_mission_task_id(self, mission_task_id: str) -> MissionTaskModel:
        self.mission_task_id = mission_task_id
        return self

    def with_name(self, name: str) -> MissionTaskModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> MissionTaskModel:
        self.metadata = metadata
        return self

    def with_verify_complete_type(self, verify_complete_type: str) -> MissionTaskModel:
        self.verify_complete_type = verify_complete_type
        return self

    def with_target_counter(self, target_counter: TargetCounterModel) -> MissionTaskModel:
        self.target_counter = target_counter
        return self

    def with_verify_complete_consume_actions(self, verify_complete_consume_actions: List[VerifyAction]) -> MissionTaskModel:
        self.verify_complete_consume_actions = verify_complete_consume_actions
        return self

    def with_complete_acquire_actions(self, complete_acquire_actions: List[AcquireAction]) -> MissionTaskModel:
        self.complete_acquire_actions = complete_acquire_actions
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> MissionTaskModel:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_premise_mission_task_name(self, premise_mission_task_name: str) -> MissionTaskModel:
        self.premise_mission_task_name = premise_mission_task_name
        return self

    def with_counter_name(self, counter_name: str) -> MissionTaskModel:
        self.counter_name = counter_name
        return self

    def with_target_reset_type(self, target_reset_type: str) -> MissionTaskModel:
        self.target_reset_type = target_reset_type
        return self

    def with_target_value(self, target_value: int) -> MissionTaskModel:
        self.target_value = target_value
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        mission_group_name,
        mission_task_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}:group:{missionGroupName}:missionTaskModel:{missionTaskName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            missionGroupName=mission_group_name,
            missionTaskName=mission_task_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModel:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModel:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModel:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_mission_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModel:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('mission_group_name')

    @classmethod
    def get_mission_task_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+):missionTaskModel:(?P<missionTaskName>.+)', grn)
        if match is None:
            return None
        return match.group('mission_task_name')

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
    ) -> Optional[MissionTaskModel]:
        if data is None:
            return None
        return MissionTaskModel()\
            .with_mission_task_id(data.get('missionTaskId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_complete_type(data.get('verifyCompleteType'))\
            .with_target_counter(TargetCounterModel.from_dict(data.get('targetCounter')))\
            .with_verify_complete_consume_actions(None if data.get('verifyCompleteConsumeActions') is None else [
                VerifyAction.from_dict(data.get('verifyCompleteConsumeActions')[i])
                for i in range(len(data.get('verifyCompleteConsumeActions')))
            ])\
            .with_complete_acquire_actions(None if data.get('completeAcquireActions') is None else [
                AcquireAction.from_dict(data.get('completeAcquireActions')[i])
                for i in range(len(data.get('completeAcquireActions')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_premise_mission_task_name(data.get('premiseMissionTaskName'))\
            .with_counter_name(data.get('counterName'))\
            .with_target_reset_type(data.get('targetResetType'))\
            .with_target_value(data.get('targetValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "missionTaskId": self.mission_task_id,
            "name": self.name,
            "metadata": self.metadata,
            "verifyCompleteType": self.verify_complete_type,
            "targetCounter": self.target_counter.to_dict() if self.target_counter else None,
            "verifyCompleteConsumeActions": None if self.verify_complete_consume_actions is None else [
                self.verify_complete_consume_actions[i].to_dict() if self.verify_complete_consume_actions[i] else None
                for i in range(len(self.verify_complete_consume_actions))
            ],
            "completeAcquireActions": None if self.complete_acquire_actions is None else [
                self.complete_acquire_actions[i].to_dict() if self.complete_acquire_actions[i] else None
                for i in range(len(self.complete_acquire_actions))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "premiseMissionTaskName": self.premise_mission_task_name,
            "counterName": self.counter_name,
            "targetResetType": self.target_reset_type,
            "targetValue": self.target_value,
        }


class MissionGroupModel(core.Gs2Model):
    mission_group_id: str = None
    name: str = None
    metadata: str = None
    tasks: List[MissionTaskModel] = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None
    complete_notification_namespace_id: str = None
    anchor_timestamp: int = None
    days: int = None

    def with_mission_group_id(self, mission_group_id: str) -> MissionGroupModel:
        self.mission_group_id = mission_group_id
        return self

    def with_name(self, name: str) -> MissionGroupModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> MissionGroupModel:
        self.metadata = metadata
        return self

    def with_tasks(self, tasks: List[MissionTaskModel]) -> MissionGroupModel:
        self.tasks = tasks
        return self

    def with_reset_type(self, reset_type: str) -> MissionGroupModel:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> MissionGroupModel:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> MissionGroupModel:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> MissionGroupModel:
        self.reset_hour = reset_hour
        return self

    def with_complete_notification_namespace_id(self, complete_notification_namespace_id: str) -> MissionGroupModel:
        self.complete_notification_namespace_id = complete_notification_namespace_id
        return self

    def with_anchor_timestamp(self, anchor_timestamp: int) -> MissionGroupModel:
        self.anchor_timestamp = anchor_timestamp
        return self

    def with_days(self, days: int) -> MissionGroupModel:
        self.days = days
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        mission_group_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}:group:{missionGroupName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            missionGroupName=mission_group_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_mission_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('mission_group_name')

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
    ) -> Optional[MissionGroupModel]:
        if data is None:
            return None
        return MissionGroupModel()\
            .with_mission_group_id(data.get('missionGroupId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_tasks(None if data.get('tasks') is None else [
                MissionTaskModel.from_dict(data.get('tasks')[i])
                for i in range(len(data.get('tasks')))
            ])\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_complete_notification_namespace_id(data.get('completeNotificationNamespaceId'))\
            .with_anchor_timestamp(data.get('anchorTimestamp'))\
            .with_days(data.get('days'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "missionGroupId": self.mission_group_id,
            "name": self.name,
            "metadata": self.metadata,
            "tasks": None if self.tasks is None else [
                self.tasks[i].to_dict() if self.tasks[i] else None
                for i in range(len(self.tasks))
            ],
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
            "completeNotificationNamespaceId": self.complete_notification_namespace_id,
            "anchorTimestamp": self.anchor_timestamp,
            "days": self.days,
        }


class CounterModel(core.Gs2Model):
    counter_id: str = None
    name: str = None
    metadata: str = None
    scopes: List[CounterScopeModel] = None
    challenge_period_event_id: str = None

    def with_counter_id(self, counter_id: str) -> CounterModel:
        self.counter_id = counter_id
        return self

    def with_name(self, name: str) -> CounterModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CounterModel:
        self.metadata = metadata
        return self

    def with_scopes(self, scopes: List[CounterScopeModel]) -> CounterModel:
        self.scopes = scopes
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> CounterModel:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        counter_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}:counter:{counterName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            counterName=counter_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_counter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):counter:(?P<counterName>.+)', grn)
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
    ) -> Optional[CounterModel]:
        if data is None:
            return None
        return CounterModel()\
            .with_counter_id(data.get('counterId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_scopes(None if data.get('scopes') is None else [
                CounterScopeModel.from_dict(data.get('scopes')[i])
                for i in range(len(data.get('scopes')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counterId": self.counter_id,
            "name": self.name,
            "metadata": self.metadata,
            "scopes": None if self.scopes is None else [
                self.scopes[i].to_dict() if self.scopes[i] else None
                for i in range(len(self.scopes))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class CurrentMissionMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentMissionMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentMissionMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentMissionMaster]:
        if data is None:
            return None
        return CurrentMissionMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class Counter(core.Gs2Model):
    counter_id: str = None
    user_id: str = None
    name: str = None
    values: List[ScopedValue] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_counter_id(self, counter_id: str) -> Counter:
        self.counter_id = counter_id
        return self

    def with_user_id(self, user_id: str) -> Counter:
        self.user_id = user_id
        return self

    def with_name(self, name: str) -> Counter:
        self.name = name
        return self

    def with_values(self, values: List[ScopedValue]) -> Counter:
        self.values = values
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
        counter_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}:user:{userId}:counter:{counterName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            counterName=counter_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_counter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):counter:(?P<counterName>.+)', grn)
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
            .with_user_id(data.get('userId'))\
            .with_name(data.get('name'))\
            .with_values(None if data.get('values') is None else [
                ScopedValue.from_dict(data.get('values')[i])
                for i in range(len(data.get('values')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counterId": self.counter_id,
            "userId": self.user_id,
            "name": self.name,
            "values": None if self.values is None else [
                self.values[i].to_dict() if self.values[i] else None
                for i in range(len(self.values))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    mission_complete_script: ScriptSetting = None
    counter_increment_script: ScriptSetting = None
    receive_rewards_script: ScriptSetting = None
    complete_notification: NotificationSetting = None
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

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
        return self

    def with_mission_complete_script(self, mission_complete_script: ScriptSetting) -> Namespace:
        self.mission_complete_script = mission_complete_script
        return self

    def with_counter_increment_script(self, counter_increment_script: ScriptSetting) -> Namespace:
        self.counter_increment_script = counter_increment_script
        return self

    def with_receive_rewards_script(self, receive_rewards_script: ScriptSetting) -> Namespace:
        self.receive_rewards_script = receive_rewards_script
        return self

    def with_complete_notification(self, complete_notification: NotificationSetting) -> Namespace:
        self.complete_notification = complete_notification
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
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+)', grn)
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
            .with_mission_complete_script(ScriptSetting.from_dict(data.get('missionCompleteScript')))\
            .with_counter_increment_script(ScriptSetting.from_dict(data.get('counterIncrementScript')))\
            .with_receive_rewards_script(ScriptSetting.from_dict(data.get('receiveRewardsScript')))\
            .with_complete_notification(NotificationSetting.from_dict(data.get('completeNotification')))\
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
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "missionCompleteScript": self.mission_complete_script.to_dict() if self.mission_complete_script else None,
            "counterIncrementScript": self.counter_increment_script.to_dict() if self.counter_increment_script else None,
            "receiveRewardsScript": self.receive_rewards_script.to_dict() if self.receive_rewards_script else None,
            "completeNotification": self.complete_notification.to_dict() if self.complete_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
            "revision": self.revision,
        }


class MissionGroupModelMaster(core.Gs2Model):
    mission_group_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None
    anchor_timestamp: int = None
    days: int = None
    complete_notification_namespace_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_mission_group_id(self, mission_group_id: str) -> MissionGroupModelMaster:
        self.mission_group_id = mission_group_id
        return self

    def with_name(self, name: str) -> MissionGroupModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> MissionGroupModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> MissionGroupModelMaster:
        self.description = description
        return self

    def with_reset_type(self, reset_type: str) -> MissionGroupModelMaster:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> MissionGroupModelMaster:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> MissionGroupModelMaster:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> MissionGroupModelMaster:
        self.reset_hour = reset_hour
        return self

    def with_anchor_timestamp(self, anchor_timestamp: int) -> MissionGroupModelMaster:
        self.anchor_timestamp = anchor_timestamp
        return self

    def with_days(self, days: int) -> MissionGroupModelMaster:
        self.days = days
        return self

    def with_complete_notification_namespace_id(self, complete_notification_namespace_id: str) -> MissionGroupModelMaster:
        self.complete_notification_namespace_id = complete_notification_namespace_id
        return self

    def with_created_at(self, created_at: int) -> MissionGroupModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> MissionGroupModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> MissionGroupModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        mission_group_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}:group:{missionGroupName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            missionGroupName=mission_group_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_mission_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):group:(?P<missionGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('mission_group_name')

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
    ) -> Optional[MissionGroupModelMaster]:
        if data is None:
            return None
        return MissionGroupModelMaster()\
            .with_mission_group_id(data.get('missionGroupId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_anchor_timestamp(data.get('anchorTimestamp'))\
            .with_days(data.get('days'))\
            .with_complete_notification_namespace_id(data.get('completeNotificationNamespaceId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "missionGroupId": self.mission_group_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
            "anchorTimestamp": self.anchor_timestamp,
            "days": self.days,
            "completeNotificationNamespaceId": self.complete_notification_namespace_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class CounterScopeModel(core.Gs2Model):
    scope_type: str = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None
    condition_name: str = None
    condition: VerifyAction = None
    anchor_timestamp: int = None
    days: int = None

    def with_scope_type(self, scope_type: str) -> CounterScopeModel:
        self.scope_type = scope_type
        return self

    def with_reset_type(self, reset_type: str) -> CounterScopeModel:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> CounterScopeModel:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> CounterScopeModel:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> CounterScopeModel:
        self.reset_hour = reset_hour
        return self

    def with_condition_name(self, condition_name: str) -> CounterScopeModel:
        self.condition_name = condition_name
        return self

    def with_condition(self, condition: VerifyAction) -> CounterScopeModel:
        self.condition = condition
        return self

    def with_anchor_timestamp(self, anchor_timestamp: int) -> CounterScopeModel:
        self.anchor_timestamp = anchor_timestamp
        return self

    def with_days(self, days: int) -> CounterScopeModel:
        self.days = days
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
    ) -> Optional[CounterScopeModel]:
        if data is None:
            return None
        return CounterScopeModel()\
            .with_scope_type(data.get('scopeType'))\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_condition_name(data.get('conditionName'))\
            .with_condition(VerifyAction.from_dict(data.get('condition')))\
            .with_anchor_timestamp(data.get('anchorTimestamp'))\
            .with_days(data.get('days'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scopeType": self.scope_type,
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
            "conditionName": self.condition_name,
            "condition": self.condition.to_dict() if self.condition else None,
            "anchorTimestamp": self.anchor_timestamp,
            "days": self.days,
        }


class CounterModelMaster(core.Gs2Model):
    counter_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    scopes: List[CounterScopeModel] = None
    challenge_period_event_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_counter_id(self, counter_id: str) -> CounterModelMaster:
        self.counter_id = counter_id
        return self

    def with_name(self, name: str) -> CounterModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CounterModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> CounterModelMaster:
        self.description = description
        return self

    def with_scopes(self, scopes: List[CounterScopeModel]) -> CounterModelMaster:
        self.scopes = scopes
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> CounterModelMaster:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_created_at(self, created_at: int) -> CounterModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> CounterModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> CounterModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        counter_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}:counter:{counterName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            counterName=counter_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):counter:(?P<counterName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_counter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):counter:(?P<counterName>.+)', grn)
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
    ) -> Optional[CounterModelMaster]:
        if data is None:
            return None
        return CounterModelMaster()\
            .with_counter_id(data.get('counterId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_scopes(None if data.get('scopes') is None else [
                CounterScopeModel.from_dict(data.get('scopes')[i])
                for i in range(len(data.get('scopes')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "counterId": self.counter_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "scopes": None if self.scopes is None else [
                self.scopes[i].to_dict() if self.scopes[i] else None
                for i in range(len(self.scopes))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class NotificationSetting(core.Gs2Model):
    gateway_namespace_id: str = None
    enable_transfer_mobile_notification: bool = None
    sound: str = None

    def with_gateway_namespace_id(self, gateway_namespace_id: str) -> NotificationSetting:
        self.gateway_namespace_id = gateway_namespace_id
        return self

    def with_enable_transfer_mobile_notification(self, enable_transfer_mobile_notification: bool) -> NotificationSetting:
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        return self

    def with_sound(self, sound: str) -> NotificationSetting:
        self.sound = sound
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
    ) -> Optional[NotificationSetting]:
        if data is None:
            return None
        return NotificationSetting()\
            .with_gateway_namespace_id(data.get('gatewayNamespaceId'))\
            .with_enable_transfer_mobile_notification(data.get('enableTransferMobileNotification'))\
            .with_sound(data.get('sound'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gatewayNamespaceId": self.gateway_namespace_id,
            "enableTransferMobileNotification": self.enable_transfer_mobile_notification,
            "sound": self.sound,
        }


class Complete(core.Gs2Model):
    complete_id: str = None
    user_id: str = None
    mission_group_name: str = None
    completed_mission_task_names: List[str] = None
    received_mission_task_names: List[str] = None
    next_reset_at: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_complete_id(self, complete_id: str) -> Complete:
        self.complete_id = complete_id
        return self

    def with_user_id(self, user_id: str) -> Complete:
        self.user_id = user_id
        return self

    def with_mission_group_name(self, mission_group_name: str) -> Complete:
        self.mission_group_name = mission_group_name
        return self

    def with_completed_mission_task_names(self, completed_mission_task_names: List[str]) -> Complete:
        self.completed_mission_task_names = completed_mission_task_names
        return self

    def with_received_mission_task_names(self, received_mission_task_names: List[str]) -> Complete:
        self.received_mission_task_names = received_mission_task_names
        return self

    def with_next_reset_at(self, next_reset_at: int) -> Complete:
        self.next_reset_at = next_reset_at
        return self

    def with_created_at(self, created_at: int) -> Complete:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Complete:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Complete:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        mission_group_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:mission:{namespaceName}:user:{userId}:group:{missionGroupName}:complete'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            missionGroupName=mission_group_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):group:(?P<missionGroupName>.+):complete', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):group:(?P<missionGroupName>.+):complete', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):group:(?P<missionGroupName>.+):complete', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):group:(?P<missionGroupName>.+):complete', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_mission_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):mission:(?P<namespaceName>.+):user:(?P<userId>.+):group:(?P<missionGroupName>.+):complete', grn)
        if match is None:
            return None
        return match.group('mission_group_name')

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
    ) -> Optional[Complete]:
        if data is None:
            return None
        return Complete()\
            .with_complete_id(data.get('completeId'))\
            .with_user_id(data.get('userId'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_completed_mission_task_names(None if data.get('completedMissionTaskNames') is None else [
                data.get('completedMissionTaskNames')[i]
                for i in range(len(data.get('completedMissionTaskNames')))
            ])\
            .with_received_mission_task_names(None if data.get('receivedMissionTaskNames') is None else [
                data.get('receivedMissionTaskNames')[i]
                for i in range(len(data.get('receivedMissionTaskNames')))
            ])\
            .with_next_reset_at(data.get('nextResetAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "completeId": self.complete_id,
            "userId": self.user_id,
            "missionGroupName": self.mission_group_name,
            "completedMissionTaskNames": None if self.completed_mission_task_names is None else [
                self.completed_mission_task_names[i]
                for i in range(len(self.completed_mission_task_names))
            ],
            "receivedMissionTaskNames": None if self.received_mission_task_names is None else [
                self.received_mission_task_names[i]
                for i in range(len(self.received_mission_task_names))
            ],
            "nextResetAt": self.next_reset_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }