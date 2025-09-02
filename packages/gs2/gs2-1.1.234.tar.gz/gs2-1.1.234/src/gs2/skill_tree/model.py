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


class CurrentTreeMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentTreeMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentTreeMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:skillTree:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentTreeMaster]:
        if data is None:
            return None
        return CurrentTreeMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class Status(core.Gs2Model):
    status_id: str = None
    user_id: str = None
    property_id: str = None
    released_node_names: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_status_id(self, status_id: str) -> Status:
        self.status_id = status_id
        return self

    def with_user_id(self, user_id: str) -> Status:
        self.user_id = user_id
        return self

    def with_property_id(self, property_id: str) -> Status:
        self.property_id = property_id
        return self

    def with_released_node_names(self, released_node_names: List[str]) -> Status:
        self.released_node_names = released_node_names
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
        property_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:skillTree:{namespaceName}:user:{userId}:status:{propertyId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            propertyId=property_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_property_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('property_id')

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
            .with_user_id(data.get('userId'))\
            .with_property_id(data.get('propertyId'))\
            .with_released_node_names(None if data.get('releasedNodeNames') is None else [
                data.get('releasedNodeNames')[i]
                for i in range(len(data.get('releasedNodeNames')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statusId": self.status_id,
            "userId": self.user_id,
            "propertyId": self.property_id,
            "releasedNodeNames": None if self.released_node_names is None else [
                self.released_node_names[i]
                for i in range(len(self.released_node_names))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class NodeModelMaster(core.Gs2Model):
    node_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    release_verify_actions: List[VerifyAction] = None
    release_consume_actions: List[ConsumeAction] = None
    restrain_return_rate: float = None
    premise_node_names: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_node_model_id(self, node_model_id: str) -> NodeModelMaster:
        self.node_model_id = node_model_id
        return self

    def with_name(self, name: str) -> NodeModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> NodeModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> NodeModelMaster:
        self.metadata = metadata
        return self

    def with_release_verify_actions(self, release_verify_actions: List[VerifyAction]) -> NodeModelMaster:
        self.release_verify_actions = release_verify_actions
        return self

    def with_release_consume_actions(self, release_consume_actions: List[ConsumeAction]) -> NodeModelMaster:
        self.release_consume_actions = release_consume_actions
        return self

    def with_restrain_return_rate(self, restrain_return_rate: float) -> NodeModelMaster:
        self.restrain_return_rate = restrain_return_rate
        return self

    def with_premise_node_names(self, premise_node_names: List[str]) -> NodeModelMaster:
        self.premise_node_names = premise_node_names
        return self

    def with_created_at(self, created_at: int) -> NodeModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> NodeModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> NodeModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        node_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:skillTree:{namespaceName}:model:{nodeModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            nodeModelName=node_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):model:(?P<nodeModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):model:(?P<nodeModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):model:(?P<nodeModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_node_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):model:(?P<nodeModelName>.+)', grn)
        if match is None:
            return None
        return match.group('node_model_name')

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
    ) -> Optional[NodeModelMaster]:
        if data is None:
            return None
        return NodeModelMaster()\
            .with_node_model_id(data.get('nodeModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_release_verify_actions(None if data.get('releaseVerifyActions') is None else [
                VerifyAction.from_dict(data.get('releaseVerifyActions')[i])
                for i in range(len(data.get('releaseVerifyActions')))
            ])\
            .with_release_consume_actions(None if data.get('releaseConsumeActions') is None else [
                ConsumeAction.from_dict(data.get('releaseConsumeActions')[i])
                for i in range(len(data.get('releaseConsumeActions')))
            ])\
            .with_restrain_return_rate(data.get('restrainReturnRate'))\
            .with_premise_node_names(None if data.get('premiseNodeNames') is None else [
                data.get('premiseNodeNames')[i]
                for i in range(len(data.get('premiseNodeNames')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodeModelId": self.node_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "releaseVerifyActions": None if self.release_verify_actions is None else [
                self.release_verify_actions[i].to_dict() if self.release_verify_actions[i] else None
                for i in range(len(self.release_verify_actions))
            ],
            "releaseConsumeActions": None if self.release_consume_actions is None else [
                self.release_consume_actions[i].to_dict() if self.release_consume_actions[i] else None
                for i in range(len(self.release_consume_actions))
            ],
            "restrainReturnRate": self.restrain_return_rate,
            "premiseNodeNames": None if self.premise_node_names is None else [
                self.premise_node_names[i]
                for i in range(len(self.premise_node_names))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class NodeModel(core.Gs2Model):
    node_model_id: str = None
    name: str = None
    metadata: str = None
    release_verify_actions: List[VerifyAction] = None
    release_consume_actions: List[ConsumeAction] = None
    return_acquire_actions: List[AcquireAction] = None
    restrain_return_rate: float = None
    premise_node_names: List[str] = None

    def with_node_model_id(self, node_model_id: str) -> NodeModel:
        self.node_model_id = node_model_id
        return self

    def with_name(self, name: str) -> NodeModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> NodeModel:
        self.metadata = metadata
        return self

    def with_release_verify_actions(self, release_verify_actions: List[VerifyAction]) -> NodeModel:
        self.release_verify_actions = release_verify_actions
        return self

    def with_release_consume_actions(self, release_consume_actions: List[ConsumeAction]) -> NodeModel:
        self.release_consume_actions = release_consume_actions
        return self

    def with_return_acquire_actions(self, return_acquire_actions: List[AcquireAction]) -> NodeModel:
        self.return_acquire_actions = return_acquire_actions
        return self

    def with_restrain_return_rate(self, restrain_return_rate: float) -> NodeModel:
        self.restrain_return_rate = restrain_return_rate
        return self

    def with_premise_node_names(self, premise_node_names: List[str]) -> NodeModel:
        self.premise_node_names = premise_node_names
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        node_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:skillTree:{namespaceName}:model:{nodeModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            nodeModelName=node_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):model:(?P<nodeModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):model:(?P<nodeModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):model:(?P<nodeModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_node_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+):model:(?P<nodeModelName>.+)', grn)
        if match is None:
            return None
        return match.group('node_model_name')

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
    ) -> Optional[NodeModel]:
        if data is None:
            return None
        return NodeModel()\
            .with_node_model_id(data.get('nodeModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_release_verify_actions(None if data.get('releaseVerifyActions') is None else [
                VerifyAction.from_dict(data.get('releaseVerifyActions')[i])
                for i in range(len(data.get('releaseVerifyActions')))
            ])\
            .with_release_consume_actions(None if data.get('releaseConsumeActions') is None else [
                ConsumeAction.from_dict(data.get('releaseConsumeActions')[i])
                for i in range(len(data.get('releaseConsumeActions')))
            ])\
            .with_return_acquire_actions(None if data.get('returnAcquireActions') is None else [
                AcquireAction.from_dict(data.get('returnAcquireActions')[i])
                for i in range(len(data.get('returnAcquireActions')))
            ])\
            .with_restrain_return_rate(data.get('restrainReturnRate'))\
            .with_premise_node_names(None if data.get('premiseNodeNames') is None else [
                data.get('premiseNodeNames')[i]
                for i in range(len(data.get('premiseNodeNames')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodeModelId": self.node_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "releaseVerifyActions": None if self.release_verify_actions is None else [
                self.release_verify_actions[i].to_dict() if self.release_verify_actions[i] else None
                for i in range(len(self.release_verify_actions))
            ],
            "releaseConsumeActions": None if self.release_consume_actions is None else [
                self.release_consume_actions[i].to_dict() if self.release_consume_actions[i] else None
                for i in range(len(self.release_consume_actions))
            ],
            "returnAcquireActions": None if self.return_acquire_actions is None else [
                self.return_acquire_actions[i].to_dict() if self.return_acquire_actions[i] else None
                for i in range(len(self.return_acquire_actions))
            ],
            "restrainReturnRate": self.restrain_return_rate,
            "premiseNodeNames": None if self.premise_node_names is None else [
                self.premise_node_names[i]
                for i in range(len(self.premise_node_names))
            ],
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    release_script: ScriptSetting = None
    restrain_script: ScriptSetting = None
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

    def with_release_script(self, release_script: ScriptSetting) -> Namespace:
        self.release_script = release_script
        return self

    def with_restrain_script(self, restrain_script: ScriptSetting) -> Namespace:
        self.restrain_script = restrain_script
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
        return 'grn:gs2:{region}:{ownerId}:skillTree:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):skillTree:(?P<namespaceName>.+)', grn)
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
            .with_release_script(ScriptSetting.from_dict(data.get('releaseScript')))\
            .with_restrain_script(ScriptSetting.from_dict(data.get('restrainScript')))\
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
            "releaseScript": self.release_script.to_dict() if self.release_script else None,
            "restrainScript": self.restrain_script.to_dict() if self.restrain_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }