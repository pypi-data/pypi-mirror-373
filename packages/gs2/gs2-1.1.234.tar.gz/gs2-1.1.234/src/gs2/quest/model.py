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


class QuestModel(core.Gs2Model):
    quest_model_id: str = None
    name: str = None
    metadata: str = None
    contents: List[Contents] = None
    challenge_period_event_id: str = None
    first_complete_acquire_actions: List[AcquireAction] = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    failed_acquire_actions: List[AcquireAction] = None
    premise_quest_names: List[str] = None

    def with_quest_model_id(self, quest_model_id: str) -> QuestModel:
        self.quest_model_id = quest_model_id
        return self

    def with_name(self, name: str) -> QuestModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> QuestModel:
        self.metadata = metadata
        return self

    def with_contents(self, contents: List[Contents]) -> QuestModel:
        self.contents = contents
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> QuestModel:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_first_complete_acquire_actions(self, first_complete_acquire_actions: List[AcquireAction]) -> QuestModel:
        self.first_complete_acquire_actions = first_complete_acquire_actions
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> QuestModel:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> QuestModel:
        self.consume_actions = consume_actions
        return self

    def with_failed_acquire_actions(self, failed_acquire_actions: List[AcquireAction]) -> QuestModel:
        self.failed_acquire_actions = failed_acquire_actions
        return self

    def with_premise_quest_names(self, premise_quest_names: List[str]) -> QuestModel:
        self.premise_quest_names = premise_quest_names
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        quest_group_name,
        quest_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:quest:{namespaceName}:group:{questGroupName}:quest:{questName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            questGroupName=quest_group_name,
            questName=quest_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_quest_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('quest_group_name')

    @classmethod
    def get_quest_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('quest_name')

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
    ) -> Optional[QuestModel]:
        if data is None:
            return None
        return QuestModel()\
            .with_quest_model_id(data.get('questModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_contents(None if data.get('contents') is None else [
                Contents.from_dict(data.get('contents')[i])
                for i in range(len(data.get('contents')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_first_complete_acquire_actions(None if data.get('firstCompleteAcquireActions') is None else [
                AcquireAction.from_dict(data.get('firstCompleteAcquireActions')[i])
                for i in range(len(data.get('firstCompleteAcquireActions')))
            ])\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_failed_acquire_actions(None if data.get('failedAcquireActions') is None else [
                AcquireAction.from_dict(data.get('failedAcquireActions')[i])
                for i in range(len(data.get('failedAcquireActions')))
            ])\
            .with_premise_quest_names(None if data.get('premiseQuestNames') is None else [
                data.get('premiseQuestNames')[i]
                for i in range(len(data.get('premiseQuestNames')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "questModelId": self.quest_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "contents": None if self.contents is None else [
                self.contents[i].to_dict() if self.contents[i] else None
                for i in range(len(self.contents))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "firstCompleteAcquireActions": None if self.first_complete_acquire_actions is None else [
                self.first_complete_acquire_actions[i].to_dict() if self.first_complete_acquire_actions[i] else None
                for i in range(len(self.first_complete_acquire_actions))
            ],
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "failedAcquireActions": None if self.failed_acquire_actions is None else [
                self.failed_acquire_actions[i].to_dict() if self.failed_acquire_actions[i] else None
                for i in range(len(self.failed_acquire_actions))
            ],
            "premiseQuestNames": None if self.premise_quest_names is None else [
                self.premise_quest_names[i]
                for i in range(len(self.premise_quest_names))
            ],
        }


class QuestGroupModel(core.Gs2Model):
    quest_group_model_id: str = None
    name: str = None
    metadata: str = None
    quests: List[QuestModel] = None
    challenge_period_event_id: str = None

    def with_quest_group_model_id(self, quest_group_model_id: str) -> QuestGroupModel:
        self.quest_group_model_id = quest_group_model_id
        return self

    def with_name(self, name: str) -> QuestGroupModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> QuestGroupModel:
        self.metadata = metadata
        return self

    def with_quests(self, quests: List[QuestModel]) -> QuestGroupModel:
        self.quests = quests
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> QuestGroupModel:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        quest_group_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:quest:{namespaceName}:group:{questGroupName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            questGroupName=quest_group_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_quest_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('quest_group_name')

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
    ) -> Optional[QuestGroupModel]:
        if data is None:
            return None
        return QuestGroupModel()\
            .with_quest_group_model_id(data.get('questGroupModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_quests(None if data.get('quests') is None else [
                QuestModel.from_dict(data.get('quests')[i])
                for i in range(len(data.get('quests')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "questGroupModelId": self.quest_group_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "quests": None if self.quests is None else [
                self.quests[i].to_dict() if self.quests[i] else None
                for i in range(len(self.quests))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class CompletedQuestList(core.Gs2Model):
    completed_quest_list_id: str = None
    user_id: str = None
    quest_group_name: str = None
    complete_quest_names: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_completed_quest_list_id(self, completed_quest_list_id: str) -> CompletedQuestList:
        self.completed_quest_list_id = completed_quest_list_id
        return self

    def with_user_id(self, user_id: str) -> CompletedQuestList:
        self.user_id = user_id
        return self

    def with_quest_group_name(self, quest_group_name: str) -> CompletedQuestList:
        self.quest_group_name = quest_group_name
        return self

    def with_complete_quest_names(self, complete_quest_names: List[str]) -> CompletedQuestList:
        self.complete_quest_names = complete_quest_names
        return self

    def with_created_at(self, created_at: int) -> CompletedQuestList:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> CompletedQuestList:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> CompletedQuestList:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        quest_group_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:quest:{namespaceName}:user:{userId}:completed:group:{questGroupName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            questGroupName=quest_group_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):completed:group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):completed:group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):completed:group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):completed:group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_quest_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):completed:group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('quest_group_name')

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
    ) -> Optional[CompletedQuestList]:
        if data is None:
            return None
        return CompletedQuestList()\
            .with_completed_quest_list_id(data.get('completedQuestListId'))\
            .with_user_id(data.get('userId'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_complete_quest_names(None if data.get('completeQuestNames') is None else [
                data.get('completeQuestNames')[i]
                for i in range(len(data.get('completeQuestNames')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "completedQuestListId": self.completed_quest_list_id,
            "userId": self.user_id,
            "questGroupName": self.quest_group_name,
            "completeQuestNames": None if self.complete_quest_names is None else [
                self.complete_quest_names[i]
                for i in range(len(self.complete_quest_names))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Progress(core.Gs2Model):
    progress_id: str = None
    user_id: str = None
    transaction_id: str = None
    quest_model_id: str = None
    random_seed: int = None
    rewards: List[Reward] = None
    failed_rewards: List[Reward] = None
    metadata: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_progress_id(self, progress_id: str) -> Progress:
        self.progress_id = progress_id
        return self

    def with_user_id(self, user_id: str) -> Progress:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> Progress:
        self.transaction_id = transaction_id
        return self

    def with_quest_model_id(self, quest_model_id: str) -> Progress:
        self.quest_model_id = quest_model_id
        return self

    def with_random_seed(self, random_seed: int) -> Progress:
        self.random_seed = random_seed
        return self

    def with_rewards(self, rewards: List[Reward]) -> Progress:
        self.rewards = rewards
        return self

    def with_failed_rewards(self, failed_rewards: List[Reward]) -> Progress:
        self.failed_rewards = failed_rewards
        return self

    def with_metadata(self, metadata: str) -> Progress:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> Progress:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Progress:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Progress:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:quest:{namespaceName}:user:{userId}:progress'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):progress', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):progress', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):progress', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):user:(?P<userId>.+):progress', grn)
        if match is None:
            return None
        return match.group('user_id')

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
    ) -> Optional[Progress]:
        if data is None:
            return None
        return Progress()\
            .with_progress_id(data.get('progressId'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_quest_model_id(data.get('questModelId'))\
            .with_random_seed(data.get('randomSeed'))\
            .with_rewards(None if data.get('rewards') is None else [
                Reward.from_dict(data.get('rewards')[i])
                for i in range(len(data.get('rewards')))
            ])\
            .with_failed_rewards(None if data.get('failedRewards') is None else [
                Reward.from_dict(data.get('failedRewards')[i])
                for i in range(len(data.get('failedRewards')))
            ])\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "progressId": self.progress_id,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
            "questModelId": self.quest_model_id,
            "randomSeed": self.random_seed,
            "rewards": None if self.rewards is None else [
                self.rewards[i].to_dict() if self.rewards[i] else None
                for i in range(len(self.rewards))
            ],
            "failedRewards": None if self.failed_rewards is None else [
                self.failed_rewards[i].to_dict() if self.failed_rewards[i] else None
                for i in range(len(self.failed_rewards))
            ],
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Reward(core.Gs2Model):
    action: str = None
    request: str = None
    item_id: str = None
    value: int = None

    def with_action(self, action: str) -> Reward:
        self.action = action
        return self

    def with_request(self, request: str) -> Reward:
        self.request = request
        return self

    def with_item_id(self, item_id: str) -> Reward:
        self.item_id = item_id
        return self

    def with_value(self, value: int) -> Reward:
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
    ) -> Optional[Reward]:
        if data is None:
            return None
        return Reward()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))\
            .with_item_id(data.get('itemId'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
            "itemId": self.item_id,
            "value": self.value,
        }


class Contents(core.Gs2Model):
    metadata: str = None
    complete_acquire_actions: List[AcquireAction] = None
    weight: int = None

    def with_metadata(self, metadata: str) -> Contents:
        self.metadata = metadata
        return self

    def with_complete_acquire_actions(self, complete_acquire_actions: List[AcquireAction]) -> Contents:
        self.complete_acquire_actions = complete_acquire_actions
        return self

    def with_weight(self, weight: int) -> Contents:
        self.weight = weight
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
    ) -> Optional[Contents]:
        if data is None:
            return None
        return Contents()\
            .with_metadata(data.get('metadata'))\
            .with_complete_acquire_actions(None if data.get('completeAcquireActions') is None else [
                AcquireAction.from_dict(data.get('completeAcquireActions')[i])
                for i in range(len(data.get('completeAcquireActions')))
            ])\
            .with_weight(data.get('weight'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata,
            "completeAcquireActions": None if self.complete_acquire_actions is None else [
                self.complete_acquire_actions[i].to_dict() if self.complete_acquire_actions[i] else None
                for i in range(len(self.complete_acquire_actions))
            ],
            "weight": self.weight,
        }


class CurrentQuestMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentQuestMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentQuestMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:quest:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentQuestMaster]:
        if data is None:
            return None
        return CurrentQuestMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class QuestModelMaster(core.Gs2Model):
    quest_model_id: str = None
    quest_group_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    contents: List[Contents] = None
    challenge_period_event_id: str = None
    first_complete_acquire_actions: List[AcquireAction] = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    failed_acquire_actions: List[AcquireAction] = None
    premise_quest_names: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_quest_model_id(self, quest_model_id: str) -> QuestModelMaster:
        self.quest_model_id = quest_model_id
        return self

    def with_quest_group_name(self, quest_group_name: str) -> QuestModelMaster:
        self.quest_group_name = quest_group_name
        return self

    def with_name(self, name: str) -> QuestModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> QuestModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> QuestModelMaster:
        self.metadata = metadata
        return self

    def with_contents(self, contents: List[Contents]) -> QuestModelMaster:
        self.contents = contents
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> QuestModelMaster:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_first_complete_acquire_actions(self, first_complete_acquire_actions: List[AcquireAction]) -> QuestModelMaster:
        self.first_complete_acquire_actions = first_complete_acquire_actions
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> QuestModelMaster:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> QuestModelMaster:
        self.consume_actions = consume_actions
        return self

    def with_failed_acquire_actions(self, failed_acquire_actions: List[AcquireAction]) -> QuestModelMaster:
        self.failed_acquire_actions = failed_acquire_actions
        return self

    def with_premise_quest_names(self, premise_quest_names: List[str]) -> QuestModelMaster:
        self.premise_quest_names = premise_quest_names
        return self

    def with_created_at(self, created_at: int) -> QuestModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> QuestModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> QuestModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        quest_group_name,
        quest_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:quest:{namespaceName}:group:{questGroupName}:quest:{questName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            questGroupName=quest_group_name,
            questName=quest_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_quest_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('quest_group_name')

    @classmethod
    def get_quest_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+):quest:(?P<questName>.+)', grn)
        if match is None:
            return None
        return match.group('quest_name')

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
    ) -> Optional[QuestModelMaster]:
        if data is None:
            return None
        return QuestModelMaster()\
            .with_quest_model_id(data.get('questModelId'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_contents(None if data.get('contents') is None else [
                Contents.from_dict(data.get('contents')[i])
                for i in range(len(data.get('contents')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_first_complete_acquire_actions(None if data.get('firstCompleteAcquireActions') is None else [
                AcquireAction.from_dict(data.get('firstCompleteAcquireActions')[i])
                for i in range(len(data.get('firstCompleteAcquireActions')))
            ])\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_failed_acquire_actions(None if data.get('failedAcquireActions') is None else [
                AcquireAction.from_dict(data.get('failedAcquireActions')[i])
                for i in range(len(data.get('failedAcquireActions')))
            ])\
            .with_premise_quest_names(None if data.get('premiseQuestNames') is None else [
                data.get('premiseQuestNames')[i]
                for i in range(len(data.get('premiseQuestNames')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "questModelId": self.quest_model_id,
            "questGroupName": self.quest_group_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "contents": None if self.contents is None else [
                self.contents[i].to_dict() if self.contents[i] else None
                for i in range(len(self.contents))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "firstCompleteAcquireActions": None if self.first_complete_acquire_actions is None else [
                self.first_complete_acquire_actions[i].to_dict() if self.first_complete_acquire_actions[i] else None
                for i in range(len(self.first_complete_acquire_actions))
            ],
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "failedAcquireActions": None if self.failed_acquire_actions is None else [
                self.failed_acquire_actions[i].to_dict() if self.failed_acquire_actions[i] else None
                for i in range(len(self.failed_acquire_actions))
            ],
            "premiseQuestNames": None if self.premise_quest_names is None else [
                self.premise_quest_names[i]
                for i in range(len(self.premise_quest_names))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class QuestGroupModelMaster(core.Gs2Model):
    quest_group_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    challenge_period_event_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_quest_group_model_id(self, quest_group_model_id: str) -> QuestGroupModelMaster:
        self.quest_group_model_id = quest_group_model_id
        return self

    def with_name(self, name: str) -> QuestGroupModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> QuestGroupModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> QuestGroupModelMaster:
        self.metadata = metadata
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> QuestGroupModelMaster:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_created_at(self, created_at: int) -> QuestGroupModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> QuestGroupModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> QuestGroupModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        quest_group_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:quest:{namespaceName}:group:{questGroupName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            questGroupName=quest_group_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_quest_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+):group:(?P<questGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('quest_group_name')

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
    ) -> Optional[QuestGroupModelMaster]:
        if data is None:
            return None
        return QuestGroupModelMaster()\
            .with_quest_group_model_id(data.get('questGroupModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "questGroupModelId": self.quest_group_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "challengePeriodEventId": self.challenge_period_event_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    start_quest_script: ScriptSetting = None
    complete_quest_script: ScriptSetting = None
    failed_quest_script: ScriptSetting = None
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

    def with_start_quest_script(self, start_quest_script: ScriptSetting) -> Namespace:
        self.start_quest_script = start_quest_script
        return self

    def with_complete_quest_script(self, complete_quest_script: ScriptSetting) -> Namespace:
        self.complete_quest_script = complete_quest_script
        return self

    def with_failed_quest_script(self, failed_quest_script: ScriptSetting) -> Namespace:
        self.failed_quest_script = failed_quest_script
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
        return 'grn:gs2:{region}:{ownerId}:quest:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):quest:(?P<namespaceName>.+)', grn)
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
            .with_start_quest_script(ScriptSetting.from_dict(data.get('startQuestScript')))\
            .with_complete_quest_script(ScriptSetting.from_dict(data.get('completeQuestScript')))\
            .with_failed_quest_script(ScriptSetting.from_dict(data.get('failedQuestScript')))\
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
            "startQuestScript": self.start_quest_script.to_dict() if self.start_quest_script else None,
            "completeQuestScript": self.complete_quest_script.to_dict() if self.complete_quest_script else None,
            "failedQuestScript": self.failed_quest_script.to_dict() if self.failed_quest_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
            "revision": self.revision,
        }