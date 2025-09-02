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


class UnleashRateEntryModel(core.Gs2Model):
    grade_value: int = None
    need_count: int = None

    def with_grade_value(self, grade_value: int) -> UnleashRateEntryModel:
        self.grade_value = grade_value
        return self

    def with_need_count(self, need_count: int) -> UnleashRateEntryModel:
        self.need_count = need_count
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
    ) -> Optional[UnleashRateEntryModel]:
        if data is None:
            return None
        return UnleashRateEntryModel()\
            .with_grade_value(data.get('gradeValue'))\
            .with_need_count(data.get('needCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gradeValue": self.grade_value,
            "needCount": self.need_count,
        }


class Material(core.Gs2Model):
    material_item_set_id: str = None
    count: int = None

    def with_material_item_set_id(self, material_item_set_id: str) -> Material:
        self.material_item_set_id = material_item_set_id
        return self

    def with_count(self, count: int) -> Material:
        self.count = count
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
    ) -> Optional[Material]:
        if data is None:
            return None
        return Material()\
            .with_material_item_set_id(data.get('materialItemSetId'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "materialItemSetId": self.material_item_set_id,
            "count": self.count,
        }


class BonusRate(core.Gs2Model):
    rate: float = None
    weight: int = None

    def with_rate(self, rate: float) -> BonusRate:
        self.rate = rate
        return self

    def with_weight(self, weight: int) -> BonusRate:
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
    ) -> Optional[BonusRate]:
        if data is None:
            return None
        return BonusRate()\
            .with_rate(data.get('rate'))\
            .with_weight(data.get('weight'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rate": self.rate,
            "weight": self.weight,
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
        return 'grn:gs2:{region}:{ownerId}:enhance:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+)', grn)
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


class Progress(core.Gs2Model):
    progress_id: str = None
    user_id: str = None
    rate_name: str = None
    name: str = None
    property_id: str = None
    experience_value: int = None
    rate: float = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_progress_id(self, progress_id: str) -> Progress:
        self.progress_id = progress_id
        return self

    def with_user_id(self, user_id: str) -> Progress:
        self.user_id = user_id
        return self

    def with_rate_name(self, rate_name: str) -> Progress:
        self.rate_name = rate_name
        return self

    def with_name(self, name: str) -> Progress:
        self.name = name
        return self

    def with_property_id(self, property_id: str) -> Progress:
        self.property_id = property_id
        return self

    def with_experience_value(self, experience_value: int) -> Progress:
        self.experience_value = experience_value
        return self

    def with_rate(self, rate: float) -> Progress:
        self.rate = rate
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
        return 'grn:gs2:{region}:{ownerId}:enhance:{namespaceName}:user:{userId}:progress'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):user:(?P<userId>.+):progress', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):user:(?P<userId>.+):progress', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):user:(?P<userId>.+):progress', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):user:(?P<userId>.+):progress', grn)
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
            .with_rate_name(data.get('rateName'))\
            .with_name(data.get('name'))\
            .with_property_id(data.get('propertyId'))\
            .with_experience_value(data.get('experienceValue'))\
            .with_rate(data.get('rate'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "progressId": self.progress_id,
            "userId": self.user_id,
            "rateName": self.rate_name,
            "name": self.name,
            "propertyId": self.property_id,
            "experienceValue": self.experience_value,
            "rate": self.rate,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class UnleashRateModelMaster(core.Gs2Model):
    unleash_rate_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    target_inventory_model_id: str = None
    grade_model_id: str = None
    grade_entries: List[UnleashRateEntryModel] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_unleash_rate_model_id(self, unleash_rate_model_id: str) -> UnleashRateModelMaster:
        self.unleash_rate_model_id = unleash_rate_model_id
        return self

    def with_name(self, name: str) -> UnleashRateModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> UnleashRateModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UnleashRateModelMaster:
        self.metadata = metadata
        return self

    def with_target_inventory_model_id(self, target_inventory_model_id: str) -> UnleashRateModelMaster:
        self.target_inventory_model_id = target_inventory_model_id
        return self

    def with_grade_model_id(self, grade_model_id: str) -> UnleashRateModelMaster:
        self.grade_model_id = grade_model_id
        return self

    def with_grade_entries(self, grade_entries: List[UnleashRateEntryModel]) -> UnleashRateModelMaster:
        self.grade_entries = grade_entries
        return self

    def with_created_at(self, created_at: int) -> UnleashRateModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> UnleashRateModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> UnleashRateModelMaster:
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
        return 'grn:gs2:{region}:{ownerId}:enhance:{namespaceName}:unleashRateModelMaster:{rateName}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):unleashRateModelMaster:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):unleashRateModelMaster:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):unleashRateModelMaster:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):unleashRateModelMaster:(?P<rateName>.+)', grn)
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
    ) -> Optional[UnleashRateModelMaster]:
        if data is None:
            return None
        return UnleashRateModelMaster()\
            .with_unleash_rate_model_id(data.get('unleashRateModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_target_inventory_model_id(data.get('targetInventoryModelId'))\
            .with_grade_model_id(data.get('gradeModelId'))\
            .with_grade_entries(None if data.get('gradeEntries') is None else [
                UnleashRateEntryModel.from_dict(data.get('gradeEntries')[i])
                for i in range(len(data.get('gradeEntries')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unleashRateModelId": self.unleash_rate_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "targetInventoryModelId": self.target_inventory_model_id,
            "gradeModelId": self.grade_model_id,
            "gradeEntries": None if self.grade_entries is None else [
                self.grade_entries[i].to_dict() if self.grade_entries[i] else None
                for i in range(len(self.grade_entries))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class UnleashRateModel(core.Gs2Model):
    unleash_rate_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    target_inventory_model_id: str = None
    grade_model_id: str = None
    grade_entries: List[UnleashRateEntryModel] = None

    def with_unleash_rate_model_id(self, unleash_rate_model_id: str) -> UnleashRateModel:
        self.unleash_rate_model_id = unleash_rate_model_id
        return self

    def with_name(self, name: str) -> UnleashRateModel:
        self.name = name
        return self

    def with_description(self, description: str) -> UnleashRateModel:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UnleashRateModel:
        self.metadata = metadata
        return self

    def with_target_inventory_model_id(self, target_inventory_model_id: str) -> UnleashRateModel:
        self.target_inventory_model_id = target_inventory_model_id
        return self

    def with_grade_model_id(self, grade_model_id: str) -> UnleashRateModel:
        self.grade_model_id = grade_model_id
        return self

    def with_grade_entries(self, grade_entries: List[UnleashRateEntryModel]) -> UnleashRateModel:
        self.grade_entries = grade_entries
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rate_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:enhance:{namespaceName}:unleashRateModel:{rateName}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):unleashRateModel:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):unleashRateModel:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):unleashRateModel:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):unleashRateModel:(?P<rateName>.+)', grn)
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
    ) -> Optional[UnleashRateModel]:
        if data is None:
            return None
        return UnleashRateModel()\
            .with_unleash_rate_model_id(data.get('unleashRateModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_target_inventory_model_id(data.get('targetInventoryModelId'))\
            .with_grade_model_id(data.get('gradeModelId'))\
            .with_grade_entries(None if data.get('gradeEntries') is None else [
                UnleashRateEntryModel.from_dict(data.get('gradeEntries')[i])
                for i in range(len(data.get('gradeEntries')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unleashRateModelId": self.unleash_rate_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "targetInventoryModelId": self.target_inventory_model_id,
            "gradeModelId": self.grade_model_id,
            "gradeEntries": None if self.grade_entries is None else [
                self.grade_entries[i].to_dict() if self.grade_entries[i] else None
                for i in range(len(self.grade_entries))
            ],
        }


class RateModelMaster(core.Gs2Model):
    rate_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    target_inventory_model_id: str = None
    acquire_experience_suffix: str = None
    material_inventory_model_id: str = None
    acquire_experience_hierarchy: List[str] = None
    experience_model_id: str = None
    bonus_rates: List[BonusRate] = None
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

    def with_target_inventory_model_id(self, target_inventory_model_id: str) -> RateModelMaster:
        self.target_inventory_model_id = target_inventory_model_id
        return self

    def with_acquire_experience_suffix(self, acquire_experience_suffix: str) -> RateModelMaster:
        self.acquire_experience_suffix = acquire_experience_suffix
        return self

    def with_material_inventory_model_id(self, material_inventory_model_id: str) -> RateModelMaster:
        self.material_inventory_model_id = material_inventory_model_id
        return self

    def with_acquire_experience_hierarchy(self, acquire_experience_hierarchy: List[str]) -> RateModelMaster:
        self.acquire_experience_hierarchy = acquire_experience_hierarchy
        return self

    def with_experience_model_id(self, experience_model_id: str) -> RateModelMaster:
        self.experience_model_id = experience_model_id
        return self

    def with_bonus_rates(self, bonus_rates: List[BonusRate]) -> RateModelMaster:
        self.bonus_rates = bonus_rates
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
        return 'grn:gs2:{region}:{ownerId}:enhance:{namespaceName}:rateModelMaster:{rateName}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):rateModelMaster:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):rateModelMaster:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):rateModelMaster:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):rateModelMaster:(?P<rateName>.+)', grn)
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
            .with_target_inventory_model_id(data.get('targetInventoryModelId'))\
            .with_acquire_experience_suffix(data.get('acquireExperienceSuffix'))\
            .with_material_inventory_model_id(data.get('materialInventoryModelId'))\
            .with_acquire_experience_hierarchy(None if data.get('acquireExperienceHierarchy') is None else [
                data.get('acquireExperienceHierarchy')[i]
                for i in range(len(data.get('acquireExperienceHierarchy')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_bonus_rates(None if data.get('bonusRates') is None else [
                BonusRate.from_dict(data.get('bonusRates')[i])
                for i in range(len(data.get('bonusRates')))
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
            "targetInventoryModelId": self.target_inventory_model_id,
            "acquireExperienceSuffix": self.acquire_experience_suffix,
            "materialInventoryModelId": self.material_inventory_model_id,
            "acquireExperienceHierarchy": None if self.acquire_experience_hierarchy is None else [
                self.acquire_experience_hierarchy[i]
                for i in range(len(self.acquire_experience_hierarchy))
            ],
            "experienceModelId": self.experience_model_id,
            "bonusRates": None if self.bonus_rates is None else [
                self.bonus_rates[i].to_dict() if self.bonus_rates[i] else None
                for i in range(len(self.bonus_rates))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class RateModel(core.Gs2Model):
    rate_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    target_inventory_model_id: str = None
    acquire_experience_suffix: str = None
    material_inventory_model_id: str = None
    acquire_experience_hierarchy: List[str] = None
    experience_model_id: str = None
    bonus_rates: List[BonusRate] = None

    def with_rate_model_id(self, rate_model_id: str) -> RateModel:
        self.rate_model_id = rate_model_id
        return self

    def with_name(self, name: str) -> RateModel:
        self.name = name
        return self

    def with_description(self, description: str) -> RateModel:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> RateModel:
        self.metadata = metadata
        return self

    def with_target_inventory_model_id(self, target_inventory_model_id: str) -> RateModel:
        self.target_inventory_model_id = target_inventory_model_id
        return self

    def with_acquire_experience_suffix(self, acquire_experience_suffix: str) -> RateModel:
        self.acquire_experience_suffix = acquire_experience_suffix
        return self

    def with_material_inventory_model_id(self, material_inventory_model_id: str) -> RateModel:
        self.material_inventory_model_id = material_inventory_model_id
        return self

    def with_acquire_experience_hierarchy(self, acquire_experience_hierarchy: List[str]) -> RateModel:
        self.acquire_experience_hierarchy = acquire_experience_hierarchy
        return self

    def with_experience_model_id(self, experience_model_id: str) -> RateModel:
        self.experience_model_id = experience_model_id
        return self

    def with_bonus_rates(self, bonus_rates: List[BonusRate]) -> RateModel:
        self.bonus_rates = bonus_rates
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        rate_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:enhance:{namespaceName}:rateModel:{rateName}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):rateModel:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):rateModel:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):rateModel:(?P<rateName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_rate_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+):rateModel:(?P<rateName>.+)', grn)
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
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_target_inventory_model_id(data.get('targetInventoryModelId'))\
            .with_acquire_experience_suffix(data.get('acquireExperienceSuffix'))\
            .with_material_inventory_model_id(data.get('materialInventoryModelId'))\
            .with_acquire_experience_hierarchy(None if data.get('acquireExperienceHierarchy') is None else [
                data.get('acquireExperienceHierarchy')[i]
                for i in range(len(data.get('acquireExperienceHierarchy')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_bonus_rates(None if data.get('bonusRates') is None else [
                BonusRate.from_dict(data.get('bonusRates')[i])
                for i in range(len(data.get('bonusRates')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rateModelId": self.rate_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "targetInventoryModelId": self.target_inventory_model_id,
            "acquireExperienceSuffix": self.acquire_experience_suffix,
            "materialInventoryModelId": self.material_inventory_model_id,
            "acquireExperienceHierarchy": None if self.acquire_experience_hierarchy is None else [
                self.acquire_experience_hierarchy[i]
                for i in range(len(self.acquire_experience_hierarchy))
            ],
            "experienceModelId": self.experience_model_id,
            "bonusRates": None if self.bonus_rates is None else [
                self.bonus_rates[i].to_dict() if self.bonus_rates[i] else None
                for i in range(len(self.bonus_rates))
            ],
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    enhance_script: ScriptSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    enable_direct_enhance: bool = None
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

    def with_enhance_script(self, enhance_script: ScriptSetting) -> Namespace:
        self.enhance_script = enhance_script
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

    def with_enable_direct_enhance(self, enable_direct_enhance: bool) -> Namespace:
        self.enable_direct_enhance = enable_direct_enhance
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
        return 'grn:gs2:{region}:{ownerId}:enhance:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):enhance:(?P<namespaceName>.+)', grn)
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
            .with_enhance_script(ScriptSetting.from_dict(data.get('enhanceScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_enable_direct_enhance(data.get('enableDirectEnhance'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "enhanceScript": self.enhance_script.to_dict() if self.enhance_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "enableDirectEnhance": self.enable_direct_enhance,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
            "revision": self.revision,
        }