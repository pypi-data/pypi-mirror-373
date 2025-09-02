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


class ReceiveStatus(core.Gs2Model):
    receive_status_id: str = None
    bonus_model_name: str = None
    user_id: str = None
    received_steps: List[bool] = None
    last_received_at: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_receive_status_id(self, receive_status_id: str) -> ReceiveStatus:
        self.receive_status_id = receive_status_id
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> ReceiveStatus:
        self.bonus_model_name = bonus_model_name
        return self

    def with_user_id(self, user_id: str) -> ReceiveStatus:
        self.user_id = user_id
        return self

    def with_received_steps(self, received_steps: List[bool]) -> ReceiveStatus:
        self.received_steps = received_steps
        return self

    def with_last_received_at(self, last_received_at: int) -> ReceiveStatus:
        self.last_received_at = last_received_at
        return self

    def with_created_at(self, created_at: int) -> ReceiveStatus:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ReceiveStatus:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> ReceiveStatus:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        bonus_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:loginReward:{namespaceName}:user:{userId}:status:{bonusModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            bonusModelName=bonus_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_bonus_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('bonus_model_name')

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
    ) -> Optional[ReceiveStatus]:
        if data is None:
            return None
        return ReceiveStatus()\
            .with_receive_status_id(data.get('receiveStatusId'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_user_id(data.get('userId'))\
            .with_received_steps(None if data.get('receivedSteps') is None else [
                data.get('receivedSteps')[i]
                for i in range(len(data.get('receivedSteps')))
            ])\
            .with_last_received_at(data.get('lastReceivedAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receiveStatusId": self.receive_status_id,
            "bonusModelName": self.bonus_model_name,
            "userId": self.user_id,
            "receivedSteps": None if self.received_steps is None else [
                self.received_steps[i]
                for i in range(len(self.received_steps))
            ],
            "lastReceivedAt": self.last_received_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Reward(core.Gs2Model):
    acquire_actions: List[AcquireAction] = None

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> Reward:
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
    ) -> Optional[Reward]:
        if data is None:
            return None
        return Reward()\
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


class BonusModel(core.Gs2Model):
    bonus_model_id: str = None
    name: str = None
    metadata: str = None
    mode: str = None
    period_event_id: str = None
    reset_hour: int = None
    repeat: str = None
    rewards: List[Reward] = None
    missed_receive_relief: str = None
    missed_receive_relief_verify_actions: List[VerifyAction] = None
    missed_receive_relief_consume_actions: List[ConsumeAction] = None

    def with_bonus_model_id(self, bonus_model_id: str) -> BonusModel:
        self.bonus_model_id = bonus_model_id
        return self

    def with_name(self, name: str) -> BonusModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> BonusModel:
        self.metadata = metadata
        return self

    def with_mode(self, mode: str) -> BonusModel:
        self.mode = mode
        return self

    def with_period_event_id(self, period_event_id: str) -> BonusModel:
        self.period_event_id = period_event_id
        return self

    def with_reset_hour(self, reset_hour: int) -> BonusModel:
        self.reset_hour = reset_hour
        return self

    def with_repeat(self, repeat: str) -> BonusModel:
        self.repeat = repeat
        return self

    def with_rewards(self, rewards: List[Reward]) -> BonusModel:
        self.rewards = rewards
        return self

    def with_missed_receive_relief(self, missed_receive_relief: str) -> BonusModel:
        self.missed_receive_relief = missed_receive_relief
        return self

    def with_missed_receive_relief_verify_actions(self, missed_receive_relief_verify_actions: List[VerifyAction]) -> BonusModel:
        self.missed_receive_relief_verify_actions = missed_receive_relief_verify_actions
        return self

    def with_missed_receive_relief_consume_actions(self, missed_receive_relief_consume_actions: List[ConsumeAction]) -> BonusModel:
        self.missed_receive_relief_consume_actions = missed_receive_relief_consume_actions
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        bonus_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:loginReward:{namespaceName}:bonusModel:{bonusModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            bonusModelName=bonus_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):bonusModel:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):bonusModel:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):bonusModel:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_bonus_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):bonusModel:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('bonus_model_name')

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
    ) -> Optional[BonusModel]:
        if data is None:
            return None
        return BonusModel()\
            .with_bonus_model_id(data.get('bonusModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_mode(data.get('mode'))\
            .with_period_event_id(data.get('periodEventId'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_repeat(data.get('repeat'))\
            .with_rewards(None if data.get('rewards') is None else [
                Reward.from_dict(data.get('rewards')[i])
                for i in range(len(data.get('rewards')))
            ])\
            .with_missed_receive_relief(data.get('missedReceiveRelief'))\
            .with_missed_receive_relief_verify_actions(None if data.get('missedReceiveReliefVerifyActions') is None else [
                VerifyAction.from_dict(data.get('missedReceiveReliefVerifyActions')[i])
                for i in range(len(data.get('missedReceiveReliefVerifyActions')))
            ])\
            .with_missed_receive_relief_consume_actions(None if data.get('missedReceiveReliefConsumeActions') is None else [
                ConsumeAction.from_dict(data.get('missedReceiveReliefConsumeActions')[i])
                for i in range(len(data.get('missedReceiveReliefConsumeActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bonusModelId": self.bonus_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "mode": self.mode,
            "periodEventId": self.period_event_id,
            "resetHour": self.reset_hour,
            "repeat": self.repeat,
            "rewards": None if self.rewards is None else [
                self.rewards[i].to_dict() if self.rewards[i] else None
                for i in range(len(self.rewards))
            ],
            "missedReceiveRelief": self.missed_receive_relief,
            "missedReceiveReliefVerifyActions": None if self.missed_receive_relief_verify_actions is None else [
                self.missed_receive_relief_verify_actions[i].to_dict() if self.missed_receive_relief_verify_actions[i] else None
                for i in range(len(self.missed_receive_relief_verify_actions))
            ],
            "missedReceiveReliefConsumeActions": None if self.missed_receive_relief_consume_actions is None else [
                self.missed_receive_relief_consume_actions[i].to_dict() if self.missed_receive_relief_consume_actions[i] else None
                for i in range(len(self.missed_receive_relief_consume_actions))
            ],
        }


class CurrentBonusMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentBonusMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentBonusMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:loginReward:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentBonusMaster]:
        if data is None:
            return None
        return CurrentBonusMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class BonusModelMaster(core.Gs2Model):
    bonus_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    mode: str = None
    period_event_id: str = None
    reset_hour: int = None
    repeat: str = None
    rewards: List[Reward] = None
    missed_receive_relief: str = None
    missed_receive_relief_verify_actions: List[VerifyAction] = None
    missed_receive_relief_consume_actions: List[ConsumeAction] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_bonus_model_id(self, bonus_model_id: str) -> BonusModelMaster:
        self.bonus_model_id = bonus_model_id
        return self

    def with_name(self, name: str) -> BonusModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> BonusModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> BonusModelMaster:
        self.metadata = metadata
        return self

    def with_mode(self, mode: str) -> BonusModelMaster:
        self.mode = mode
        return self

    def with_period_event_id(self, period_event_id: str) -> BonusModelMaster:
        self.period_event_id = period_event_id
        return self

    def with_reset_hour(self, reset_hour: int) -> BonusModelMaster:
        self.reset_hour = reset_hour
        return self

    def with_repeat(self, repeat: str) -> BonusModelMaster:
        self.repeat = repeat
        return self

    def with_rewards(self, rewards: List[Reward]) -> BonusModelMaster:
        self.rewards = rewards
        return self

    def with_missed_receive_relief(self, missed_receive_relief: str) -> BonusModelMaster:
        self.missed_receive_relief = missed_receive_relief
        return self

    def with_missed_receive_relief_verify_actions(self, missed_receive_relief_verify_actions: List[VerifyAction]) -> BonusModelMaster:
        self.missed_receive_relief_verify_actions = missed_receive_relief_verify_actions
        return self

    def with_missed_receive_relief_consume_actions(self, missed_receive_relief_consume_actions: List[ConsumeAction]) -> BonusModelMaster:
        self.missed_receive_relief_consume_actions = missed_receive_relief_consume_actions
        return self

    def with_created_at(self, created_at: int) -> BonusModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BonusModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> BonusModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        bonus_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:loginReward:{namespaceName}:bonusModel:{bonusModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            bonusModelName=bonus_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):bonusModel:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):bonusModel:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):bonusModel:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_bonus_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+):bonusModel:(?P<bonusModelName>.+)', grn)
        if match is None:
            return None
        return match.group('bonus_model_name')

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
    ) -> Optional[BonusModelMaster]:
        if data is None:
            return None
        return BonusModelMaster()\
            .with_bonus_model_id(data.get('bonusModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_mode(data.get('mode'))\
            .with_period_event_id(data.get('periodEventId'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_repeat(data.get('repeat'))\
            .with_rewards(None if data.get('rewards') is None else [
                Reward.from_dict(data.get('rewards')[i])
                for i in range(len(data.get('rewards')))
            ])\
            .with_missed_receive_relief(data.get('missedReceiveRelief'))\
            .with_missed_receive_relief_verify_actions(None if data.get('missedReceiveReliefVerifyActions') is None else [
                VerifyAction.from_dict(data.get('missedReceiveReliefVerifyActions')[i])
                for i in range(len(data.get('missedReceiveReliefVerifyActions')))
            ])\
            .with_missed_receive_relief_consume_actions(None if data.get('missedReceiveReliefConsumeActions') is None else [
                ConsumeAction.from_dict(data.get('missedReceiveReliefConsumeActions')[i])
                for i in range(len(data.get('missedReceiveReliefConsumeActions')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bonusModelId": self.bonus_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "mode": self.mode,
            "periodEventId": self.period_event_id,
            "resetHour": self.reset_hour,
            "repeat": self.repeat,
            "rewards": None if self.rewards is None else [
                self.rewards[i].to_dict() if self.rewards[i] else None
                for i in range(len(self.rewards))
            ],
            "missedReceiveRelief": self.missed_receive_relief,
            "missedReceiveReliefVerifyActions": None if self.missed_receive_relief_verify_actions is None else [
                self.missed_receive_relief_verify_actions[i].to_dict() if self.missed_receive_relief_verify_actions[i] else None
                for i in range(len(self.missed_receive_relief_verify_actions))
            ],
            "missedReceiveReliefConsumeActions": None if self.missed_receive_relief_consume_actions is None else [
                self.missed_receive_relief_consume_actions[i].to_dict() if self.missed_receive_relief_consume_actions[i] else None
                for i in range(len(self.missed_receive_relief_consume_actions))
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
    receive_script: ScriptSetting = None
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
        return 'grn:gs2:{region}:{ownerId}:loginReward:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):loginReward:(?P<namespaceName>.+)', grn)
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
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }