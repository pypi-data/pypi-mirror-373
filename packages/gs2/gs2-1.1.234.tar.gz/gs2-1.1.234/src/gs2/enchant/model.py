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


class RarityParameterValue(core.Gs2Model):
    name: str = None
    resource_name: str = None
    resource_value: int = None

    def with_name(self, name: str) -> RarityParameterValue:
        self.name = name
        return self

    def with_resource_name(self, resource_name: str) -> RarityParameterValue:
        self.resource_name = resource_name
        return self

    def with_resource_value(self, resource_value: int) -> RarityParameterValue:
        self.resource_value = resource_value
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
    ) -> Optional[RarityParameterValue]:
        if data is None:
            return None
        return RarityParameterValue()\
            .with_name(data.get('name'))\
            .with_resource_name(data.get('resourceName'))\
            .with_resource_value(data.get('resourceValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "resourceName": self.resource_name,
            "resourceValue": self.resource_value,
        }


class BalanceParameterValue(core.Gs2Model):
    name: str = None
    value: int = None

    def with_name(self, name: str) -> BalanceParameterValue:
        self.name = name
        return self

    def with_value(self, value: int) -> BalanceParameterValue:
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
    ) -> Optional[BalanceParameterValue]:
        if data is None:
            return None
        return BalanceParameterValue()\
            .with_name(data.get('name'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
        }


class RarityParameterValueModel(core.Gs2Model):
    name: str = None
    metadata: str = None
    resource_name: str = None
    resource_value: int = None
    weight: int = None

    def with_name(self, name: str) -> RarityParameterValueModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RarityParameterValueModel:
        self.metadata = metadata
        return self

    def with_resource_name(self, resource_name: str) -> RarityParameterValueModel:
        self.resource_name = resource_name
        return self

    def with_resource_value(self, resource_value: int) -> RarityParameterValueModel:
        self.resource_value = resource_value
        return self

    def with_weight(self, weight: int) -> RarityParameterValueModel:
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
    ) -> Optional[RarityParameterValueModel]:
        if data is None:
            return None
        return RarityParameterValueModel()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_resource_name(data.get('resourceName'))\
            .with_resource_value(data.get('resourceValue'))\
            .with_weight(data.get('weight'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "resourceName": self.resource_name,
            "resourceValue": self.resource_value,
            "weight": self.weight,
        }


class RarityParameterCountModel(core.Gs2Model):
    count: int = None
    weight: int = None

    def with_count(self, count: int) -> RarityParameterCountModel:
        self.count = count
        return self

    def with_weight(self, weight: int) -> RarityParameterCountModel:
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
    ) -> Optional[RarityParameterCountModel]:
        if data is None:
            return None
        return RarityParameterCountModel()\
            .with_count(data.get('count'))\
            .with_weight(data.get('weight'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "count": self.count,
            "weight": self.weight,
        }


class BalanceParameterValueModel(core.Gs2Model):
    name: str = None
    metadata: str = None

    def with_name(self, name: str) -> BalanceParameterValueModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> BalanceParameterValueModel:
        self.metadata = metadata
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
    ) -> Optional[BalanceParameterValueModel]:
        if data is None:
            return None
        return BalanceParameterValueModel()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
        }


class RarityParameterStatus(core.Gs2Model):
    rarity_parameter_status_id: str = None
    user_id: str = None
    parameter_name: str = None
    property_id: str = None
    parameter_values: List[RarityParameterValue] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_rarity_parameter_status_id(self, rarity_parameter_status_id: str) -> RarityParameterStatus:
        self.rarity_parameter_status_id = rarity_parameter_status_id
        return self

    def with_user_id(self, user_id: str) -> RarityParameterStatus:
        self.user_id = user_id
        return self

    def with_parameter_name(self, parameter_name: str) -> RarityParameterStatus:
        self.parameter_name = parameter_name
        return self

    def with_property_id(self, property_id: str) -> RarityParameterStatus:
        self.property_id = property_id
        return self

    def with_parameter_values(self, parameter_values: List[RarityParameterValue]) -> RarityParameterStatus:
        self.parameter_values = parameter_values
        return self

    def with_created_at(self, created_at: int) -> RarityParameterStatus:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> RarityParameterStatus:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> RarityParameterStatus:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        parameter_name,
        property_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:enchant:{namespaceName}:user:{userId}:rarity:{parameterName}:{propertyId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            parameterName=parameter_name,
            propertyId=property_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):rarity:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):rarity:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):rarity:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):rarity:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_parameter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):rarity:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('parameter_name')

    @classmethod
    def get_property_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):rarity:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
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
    ) -> Optional[RarityParameterStatus]:
        if data is None:
            return None
        return RarityParameterStatus()\
            .with_rarity_parameter_status_id(data.get('rarityParameterStatusId'))\
            .with_user_id(data.get('userId'))\
            .with_parameter_name(data.get('parameterName'))\
            .with_property_id(data.get('propertyId'))\
            .with_parameter_values(None if data.get('parameterValues') is None else [
                RarityParameterValue.from_dict(data.get('parameterValues')[i])
                for i in range(len(data.get('parameterValues')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rarityParameterStatusId": self.rarity_parameter_status_id,
            "userId": self.user_id,
            "parameterName": self.parameter_name,
            "propertyId": self.property_id,
            "parameterValues": None if self.parameter_values is None else [
                self.parameter_values[i].to_dict() if self.parameter_values[i] else None
                for i in range(len(self.parameter_values))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class BalanceParameterStatus(core.Gs2Model):
    balance_parameter_status_id: str = None
    user_id: str = None
    parameter_name: str = None
    property_id: str = None
    parameter_values: List[BalanceParameterValue] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_balance_parameter_status_id(self, balance_parameter_status_id: str) -> BalanceParameterStatus:
        self.balance_parameter_status_id = balance_parameter_status_id
        return self

    def with_user_id(self, user_id: str) -> BalanceParameterStatus:
        self.user_id = user_id
        return self

    def with_parameter_name(self, parameter_name: str) -> BalanceParameterStatus:
        self.parameter_name = parameter_name
        return self

    def with_property_id(self, property_id: str) -> BalanceParameterStatus:
        self.property_id = property_id
        return self

    def with_parameter_values(self, parameter_values: List[BalanceParameterValue]) -> BalanceParameterStatus:
        self.parameter_values = parameter_values
        return self

    def with_created_at(self, created_at: int) -> BalanceParameterStatus:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BalanceParameterStatus:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> BalanceParameterStatus:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        parameter_name,
        property_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:enchant:{namespaceName}:user:{userId}:balance:{parameterName}:{propertyId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            parameterName=parameter_name,
            propertyId=property_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):balance:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):balance:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):balance:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):balance:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_parameter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):balance:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('parameter_name')

    @classmethod
    def get_property_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):user:(?P<userId>.+):balance:(?P<parameterName>.+):(?P<propertyId>.+)', grn)
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
    ) -> Optional[BalanceParameterStatus]:
        if data is None:
            return None
        return BalanceParameterStatus()\
            .with_balance_parameter_status_id(data.get('balanceParameterStatusId'))\
            .with_user_id(data.get('userId'))\
            .with_parameter_name(data.get('parameterName'))\
            .with_property_id(data.get('propertyId'))\
            .with_parameter_values(None if data.get('parameterValues') is None else [
                BalanceParameterValue.from_dict(data.get('parameterValues')[i])
                for i in range(len(data.get('parameterValues')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "balanceParameterStatusId": self.balance_parameter_status_id,
            "userId": self.user_id,
            "parameterName": self.parameter_name,
            "propertyId": self.property_id,
            "parameterValues": None if self.parameter_values is None else [
                self.parameter_values[i].to_dict() if self.parameter_values[i] else None
                for i in range(len(self.parameter_values))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class CurrentParameterMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentParameterMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentParameterMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:enchant:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentParameterMaster]:
        if data is None:
            return None
        return CurrentParameterMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class RarityParameterModelMaster(core.Gs2Model):
    rarity_parameter_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    maximum_parameter_count: int = None
    parameter_counts: List[RarityParameterCountModel] = None
    parameters: List[RarityParameterValueModel] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_rarity_parameter_model_id(self, rarity_parameter_model_id: str) -> RarityParameterModelMaster:
        self.rarity_parameter_model_id = rarity_parameter_model_id
        return self

    def with_name(self, name: str) -> RarityParameterModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> RarityParameterModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> RarityParameterModelMaster:
        self.metadata = metadata
        return self

    def with_maximum_parameter_count(self, maximum_parameter_count: int) -> RarityParameterModelMaster:
        self.maximum_parameter_count = maximum_parameter_count
        return self

    def with_parameter_counts(self, parameter_counts: List[RarityParameterCountModel]) -> RarityParameterModelMaster:
        self.parameter_counts = parameter_counts
        return self

    def with_parameters(self, parameters: List[RarityParameterValueModel]) -> RarityParameterModelMaster:
        self.parameters = parameters
        return self

    def with_created_at(self, created_at: int) -> RarityParameterModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> RarityParameterModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> RarityParameterModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        parameter_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:enchant:{namespaceName}:model:rarity:{parameterName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            parameterName=parameter_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:rarity:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:rarity:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:rarity:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_parameter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:rarity:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('parameter_name')

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
    ) -> Optional[RarityParameterModelMaster]:
        if data is None:
            return None
        return RarityParameterModelMaster()\
            .with_rarity_parameter_model_id(data.get('rarityParameterModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_maximum_parameter_count(data.get('maximumParameterCount'))\
            .with_parameter_counts(None if data.get('parameterCounts') is None else [
                RarityParameterCountModel.from_dict(data.get('parameterCounts')[i])
                for i in range(len(data.get('parameterCounts')))
            ])\
            .with_parameters(None if data.get('parameters') is None else [
                RarityParameterValueModel.from_dict(data.get('parameters')[i])
                for i in range(len(data.get('parameters')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rarityParameterModelId": self.rarity_parameter_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "maximumParameterCount": self.maximum_parameter_count,
            "parameterCounts": None if self.parameter_counts is None else [
                self.parameter_counts[i].to_dict() if self.parameter_counts[i] else None
                for i in range(len(self.parameter_counts))
            ],
            "parameters": None if self.parameters is None else [
                self.parameters[i].to_dict() if self.parameters[i] else None
                for i in range(len(self.parameters))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class RarityParameterModel(core.Gs2Model):
    rarity_parameter_model_id: str = None
    name: str = None
    metadata: str = None
    maximum_parameter_count: int = None
    parameter_counts: List[RarityParameterCountModel] = None
    parameters: List[RarityParameterValueModel] = None

    def with_rarity_parameter_model_id(self, rarity_parameter_model_id: str) -> RarityParameterModel:
        self.rarity_parameter_model_id = rarity_parameter_model_id
        return self

    def with_name(self, name: str) -> RarityParameterModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RarityParameterModel:
        self.metadata = metadata
        return self

    def with_maximum_parameter_count(self, maximum_parameter_count: int) -> RarityParameterModel:
        self.maximum_parameter_count = maximum_parameter_count
        return self

    def with_parameter_counts(self, parameter_counts: List[RarityParameterCountModel]) -> RarityParameterModel:
        self.parameter_counts = parameter_counts
        return self

    def with_parameters(self, parameters: List[RarityParameterValueModel]) -> RarityParameterModel:
        self.parameters = parameters
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        parameter_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:enchant:{namespaceName}:model:rarity:{parameterName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            parameterName=parameter_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:rarity:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:rarity:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:rarity:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_parameter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:rarity:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('parameter_name')

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
    ) -> Optional[RarityParameterModel]:
        if data is None:
            return None
        return RarityParameterModel()\
            .with_rarity_parameter_model_id(data.get('rarityParameterModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_maximum_parameter_count(data.get('maximumParameterCount'))\
            .with_parameter_counts(None if data.get('parameterCounts') is None else [
                RarityParameterCountModel.from_dict(data.get('parameterCounts')[i])
                for i in range(len(data.get('parameterCounts')))
            ])\
            .with_parameters(None if data.get('parameters') is None else [
                RarityParameterValueModel.from_dict(data.get('parameters')[i])
                for i in range(len(data.get('parameters')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rarityParameterModelId": self.rarity_parameter_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "maximumParameterCount": self.maximum_parameter_count,
            "parameterCounts": None if self.parameter_counts is None else [
                self.parameter_counts[i].to_dict() if self.parameter_counts[i] else None
                for i in range(len(self.parameter_counts))
            ],
            "parameters": None if self.parameters is None else [
                self.parameters[i].to_dict() if self.parameters[i] else None
                for i in range(len(self.parameters))
            ],
        }


class BalanceParameterModelMaster(core.Gs2Model):
    balance_parameter_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    total_value: int = None
    initial_value_strategy: str = None
    parameters: List[BalanceParameterValueModel] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_balance_parameter_model_id(self, balance_parameter_model_id: str) -> BalanceParameterModelMaster:
        self.balance_parameter_model_id = balance_parameter_model_id
        return self

    def with_name(self, name: str) -> BalanceParameterModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> BalanceParameterModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> BalanceParameterModelMaster:
        self.metadata = metadata
        return self

    def with_total_value(self, total_value: int) -> BalanceParameterModelMaster:
        self.total_value = total_value
        return self

    def with_initial_value_strategy(self, initial_value_strategy: str) -> BalanceParameterModelMaster:
        self.initial_value_strategy = initial_value_strategy
        return self

    def with_parameters(self, parameters: List[BalanceParameterValueModel]) -> BalanceParameterModelMaster:
        self.parameters = parameters
        return self

    def with_created_at(self, created_at: int) -> BalanceParameterModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BalanceParameterModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> BalanceParameterModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        parameter_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:enchant:{namespaceName}:model:balance:{parameterName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            parameterName=parameter_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:balance:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:balance:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:balance:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_parameter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:balance:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('parameter_name')

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
    ) -> Optional[BalanceParameterModelMaster]:
        if data is None:
            return None
        return BalanceParameterModelMaster()\
            .with_balance_parameter_model_id(data.get('balanceParameterModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_total_value(data.get('totalValue'))\
            .with_initial_value_strategy(data.get('initialValueStrategy'))\
            .with_parameters(None if data.get('parameters') is None else [
                BalanceParameterValueModel.from_dict(data.get('parameters')[i])
                for i in range(len(data.get('parameters')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "balanceParameterModelId": self.balance_parameter_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "totalValue": self.total_value,
            "initialValueStrategy": self.initial_value_strategy,
            "parameters": None if self.parameters is None else [
                self.parameters[i].to_dict() if self.parameters[i] else None
                for i in range(len(self.parameters))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class BalanceParameterModel(core.Gs2Model):
    balance_parameter_model_id: str = None
    name: str = None
    metadata: str = None
    total_value: int = None
    initial_value_strategy: str = None
    parameters: List[BalanceParameterValueModel] = None

    def with_balance_parameter_model_id(self, balance_parameter_model_id: str) -> BalanceParameterModel:
        self.balance_parameter_model_id = balance_parameter_model_id
        return self

    def with_name(self, name: str) -> BalanceParameterModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> BalanceParameterModel:
        self.metadata = metadata
        return self

    def with_total_value(self, total_value: int) -> BalanceParameterModel:
        self.total_value = total_value
        return self

    def with_initial_value_strategy(self, initial_value_strategy: str) -> BalanceParameterModel:
        self.initial_value_strategy = initial_value_strategy
        return self

    def with_parameters(self, parameters: List[BalanceParameterValueModel]) -> BalanceParameterModel:
        self.parameters = parameters
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        parameter_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:enchant:{namespaceName}:model:balance:{parameterName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            parameterName=parameter_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:balance:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:balance:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:balance:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_parameter_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+):model:balance:(?P<parameterName>.+)', grn)
        if match is None:
            return None
        return match.group('parameter_name')

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
    ) -> Optional[BalanceParameterModel]:
        if data is None:
            return None
        return BalanceParameterModel()\
            .with_balance_parameter_model_id(data.get('balanceParameterModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_total_value(data.get('totalValue'))\
            .with_initial_value_strategy(data.get('initialValueStrategy'))\
            .with_parameters(None if data.get('parameters') is None else [
                BalanceParameterValueModel.from_dict(data.get('parameters')[i])
                for i in range(len(data.get('parameters')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "balanceParameterModelId": self.balance_parameter_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "totalValue": self.total_value,
            "initialValueStrategy": self.initial_value_strategy,
            "parameters": None if self.parameters is None else [
                self.parameters[i].to_dict() if self.parameters[i] else None
                for i in range(len(self.parameters))
            ],
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
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
        return 'grn:gs2:{region}:{ownerId}:enchant:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enchant:(?P<namespaceName>.+)', grn)
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
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }