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


class Stamina(core.Gs2Model):
    stamina_id: str = None
    stamina_name: str = None
    user_id: str = None
    value: int = None
    max_value: int = None
    recover_interval_minutes: int = None
    recover_value: int = None
    overflow_value: int = None
    next_recover_at: int = None
    last_recovered_at: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_stamina_id(self, stamina_id: str) -> Stamina:
        self.stamina_id = stamina_id
        return self

    def with_stamina_name(self, stamina_name: str) -> Stamina:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> Stamina:
        self.user_id = user_id
        return self

    def with_value(self, value: int) -> Stamina:
        self.value = value
        return self

    def with_max_value(self, max_value: int) -> Stamina:
        self.max_value = max_value
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> Stamina:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> Stamina:
        self.recover_value = recover_value
        return self

    def with_overflow_value(self, overflow_value: int) -> Stamina:
        self.overflow_value = overflow_value
        return self

    def with_next_recover_at(self, next_recover_at: int) -> Stamina:
        self.next_recover_at = next_recover_at
        return self

    def with_last_recovered_at(self, last_recovered_at: int) -> Stamina:
        self.last_recovered_at = last_recovered_at
        return self

    def with_created_at(self, created_at: int) -> Stamina:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Stamina:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Stamina:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        stamina_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:stamina:{namespaceName}:user:{userId}:stamina:{staminaName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            staminaName=stamina_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):user:(?P<userId>.+):stamina:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):user:(?P<userId>.+):stamina:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):user:(?P<userId>.+):stamina:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):user:(?P<userId>.+):stamina:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_stamina_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):user:(?P<userId>.+):stamina:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('stamina_name')

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
    ) -> Optional[Stamina]:
        if data is None:
            return None
        return Stamina()\
            .with_stamina_id(data.get('staminaId'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_value(data.get('value'))\
            .with_max_value(data.get('maxValue'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_overflow_value(data.get('overflowValue'))\
            .with_next_recover_at(data.get('nextRecoverAt'))\
            .with_last_recovered_at(data.get('lastRecoveredAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "staminaId": self.stamina_id,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "value": self.value,
            "maxValue": self.max_value,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
            "overflowValue": self.overflow_value,
            "nextRecoverAt": self.next_recover_at,
            "lastRecoveredAt": self.last_recovered_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class RecoverValueTable(core.Gs2Model):
    name: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_name(self, name: str) -> RecoverValueTable:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RecoverValueTable:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> RecoverValueTable:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> RecoverValueTable:
        self.values = values
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
    ) -> Optional[RecoverValueTable]:
        if data is None:
            return None
        return RecoverValueTable()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class RecoverIntervalTable(core.Gs2Model):
    name: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_name(self, name: str) -> RecoverIntervalTable:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RecoverIntervalTable:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> RecoverIntervalTable:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> RecoverIntervalTable:
        self.values = values
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
    ) -> Optional[RecoverIntervalTable]:
        if data is None:
            return None
        return RecoverIntervalTable()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class MaxStaminaTable(core.Gs2Model):
    name: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_name(self, name: str) -> MaxStaminaTable:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> MaxStaminaTable:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> MaxStaminaTable:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> MaxStaminaTable:
        self.values = values
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
    ) -> Optional[MaxStaminaTable]:
        if data is None:
            return None
        return MaxStaminaTable()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class StaminaModel(core.Gs2Model):
    stamina_model_id: str = None
    name: str = None
    metadata: str = None
    recover_interval_minutes: int = None
    recover_value: int = None
    initial_capacity: int = None
    is_overflow: bool = None
    max_capacity: int = None
    max_stamina_table: MaxStaminaTable = None
    recover_interval_table: RecoverIntervalTable = None
    recover_value_table: RecoverValueTable = None

    def with_stamina_model_id(self, stamina_model_id: str) -> StaminaModel:
        self.stamina_model_id = stamina_model_id
        return self

    def with_name(self, name: str) -> StaminaModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> StaminaModel:
        self.metadata = metadata
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> StaminaModel:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> StaminaModel:
        self.recover_value = recover_value
        return self

    def with_initial_capacity(self, initial_capacity: int) -> StaminaModel:
        self.initial_capacity = initial_capacity
        return self

    def with_is_overflow(self, is_overflow: bool) -> StaminaModel:
        self.is_overflow = is_overflow
        return self

    def with_max_capacity(self, max_capacity: int) -> StaminaModel:
        self.max_capacity = max_capacity
        return self

    def with_max_stamina_table(self, max_stamina_table: MaxStaminaTable) -> StaminaModel:
        self.max_stamina_table = max_stamina_table
        return self

    def with_recover_interval_table(self, recover_interval_table: RecoverIntervalTable) -> StaminaModel:
        self.recover_interval_table = recover_interval_table
        return self

    def with_recover_value_table(self, recover_value_table: RecoverValueTable) -> StaminaModel:
        self.recover_value_table = recover_value_table
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        stamina_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:stamina:{namespaceName}:model:{staminaName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            staminaName=stamina_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):model:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):model:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):model:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_stamina_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):model:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('stamina_name')

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
    ) -> Optional[StaminaModel]:
        if data is None:
            return None
        return StaminaModel()\
            .with_stamina_model_id(data.get('staminaModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_is_overflow(data.get('isOverflow'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_max_stamina_table(MaxStaminaTable.from_dict(data.get('maxStaminaTable')))\
            .with_recover_interval_table(RecoverIntervalTable.from_dict(data.get('recoverIntervalTable')))\
            .with_recover_value_table(RecoverValueTable.from_dict(data.get('recoverValueTable')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "staminaModelId": self.stamina_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
            "initialCapacity": self.initial_capacity,
            "isOverflow": self.is_overflow,
            "maxCapacity": self.max_capacity,
            "maxStaminaTable": self.max_stamina_table.to_dict() if self.max_stamina_table else None,
            "recoverIntervalTable": self.recover_interval_table.to_dict() if self.recover_interval_table else None,
            "recoverValueTable": self.recover_value_table.to_dict() if self.recover_value_table else None,
        }


class CurrentStaminaMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentStaminaMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentStaminaMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:stamina:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentStaminaMaster]:
        if data is None:
            return None
        return CurrentStaminaMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class RecoverValueTableMaster(core.Gs2Model):
    recover_value_table_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    experience_model_id: str = None
    values: List[int] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_recover_value_table_id(self, recover_value_table_id: str) -> RecoverValueTableMaster:
        self.recover_value_table_id = recover_value_table_id
        return self

    def with_name(self, name: str) -> RecoverValueTableMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RecoverValueTableMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> RecoverValueTableMaster:
        self.description = description
        return self

    def with_experience_model_id(self, experience_model_id: str) -> RecoverValueTableMaster:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> RecoverValueTableMaster:
        self.values = values
        return self

    def with_created_at(self, created_at: int) -> RecoverValueTableMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> RecoverValueTableMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> RecoverValueTableMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        recover_value_table_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:stamina:{namespaceName}:recoverValueTable:{recoverValueTableName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            recoverValueTableName=recover_value_table_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):recoverValueTable:(?P<recoverValueTableName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):recoverValueTable:(?P<recoverValueTableName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):recoverValueTable:(?P<recoverValueTableName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_recover_value_table_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):recoverValueTable:(?P<recoverValueTableName>.+)', grn)
        if match is None:
            return None
        return match.group('recover_value_table_name')

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
    ) -> Optional[RecoverValueTableMaster]:
        if data is None:
            return None
        return RecoverValueTableMaster()\
            .with_recover_value_table_id(data.get('recoverValueTableId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recoverValueTableId": self.recover_value_table_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class RecoverIntervalTableMaster(core.Gs2Model):
    recover_interval_table_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    experience_model_id: str = None
    values: List[int] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_recover_interval_table_id(self, recover_interval_table_id: str) -> RecoverIntervalTableMaster:
        self.recover_interval_table_id = recover_interval_table_id
        return self

    def with_name(self, name: str) -> RecoverIntervalTableMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RecoverIntervalTableMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> RecoverIntervalTableMaster:
        self.description = description
        return self

    def with_experience_model_id(self, experience_model_id: str) -> RecoverIntervalTableMaster:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> RecoverIntervalTableMaster:
        self.values = values
        return self

    def with_created_at(self, created_at: int) -> RecoverIntervalTableMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> RecoverIntervalTableMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> RecoverIntervalTableMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        recover_interval_table_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:stamina:{namespaceName}:recoverIntervalTable:{recoverIntervalTableName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            recoverIntervalTableName=recover_interval_table_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):recoverIntervalTable:(?P<recoverIntervalTableName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):recoverIntervalTable:(?P<recoverIntervalTableName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):recoverIntervalTable:(?P<recoverIntervalTableName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_recover_interval_table_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):recoverIntervalTable:(?P<recoverIntervalTableName>.+)', grn)
        if match is None:
            return None
        return match.group('recover_interval_table_name')

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
    ) -> Optional[RecoverIntervalTableMaster]:
        if data is None:
            return None
        return RecoverIntervalTableMaster()\
            .with_recover_interval_table_id(data.get('recoverIntervalTableId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recoverIntervalTableId": self.recover_interval_table_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class MaxStaminaTableMaster(core.Gs2Model):
    max_stamina_table_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    experience_model_id: str = None
    values: List[int] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_max_stamina_table_id(self, max_stamina_table_id: str) -> MaxStaminaTableMaster:
        self.max_stamina_table_id = max_stamina_table_id
        return self

    def with_name(self, name: str) -> MaxStaminaTableMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> MaxStaminaTableMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> MaxStaminaTableMaster:
        self.description = description
        return self

    def with_experience_model_id(self, experience_model_id: str) -> MaxStaminaTableMaster:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> MaxStaminaTableMaster:
        self.values = values
        return self

    def with_created_at(self, created_at: int) -> MaxStaminaTableMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> MaxStaminaTableMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> MaxStaminaTableMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        max_stamina_table_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:stamina:{namespaceName}:maxStaminaTable:{maxStaminaTableName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            maxStaminaTableName=max_stamina_table_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):maxStaminaTable:(?P<maxStaminaTableName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):maxStaminaTable:(?P<maxStaminaTableName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):maxStaminaTable:(?P<maxStaminaTableName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_max_stamina_table_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):maxStaminaTable:(?P<maxStaminaTableName>.+)', grn)
        if match is None:
            return None
        return match.group('max_stamina_table_name')

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
    ) -> Optional[MaxStaminaTableMaster]:
        if data is None:
            return None
        return MaxStaminaTableMaster()\
            .with_max_stamina_table_id(data.get('maxStaminaTableId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "maxStaminaTableId": self.max_stamina_table_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class StaminaModelMaster(core.Gs2Model):
    stamina_model_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    recover_interval_minutes: int = None
    recover_value: int = None
    initial_capacity: int = None
    is_overflow: bool = None
    max_capacity: int = None
    max_stamina_table_name: str = None
    recover_interval_table_name: str = None
    recover_value_table_name: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_stamina_model_id(self, stamina_model_id: str) -> StaminaModelMaster:
        self.stamina_model_id = stamina_model_id
        return self

    def with_name(self, name: str) -> StaminaModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> StaminaModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> StaminaModelMaster:
        self.description = description
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> StaminaModelMaster:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> StaminaModelMaster:
        self.recover_value = recover_value
        return self

    def with_initial_capacity(self, initial_capacity: int) -> StaminaModelMaster:
        self.initial_capacity = initial_capacity
        return self

    def with_is_overflow(self, is_overflow: bool) -> StaminaModelMaster:
        self.is_overflow = is_overflow
        return self

    def with_max_capacity(self, max_capacity: int) -> StaminaModelMaster:
        self.max_capacity = max_capacity
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> StaminaModelMaster:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> StaminaModelMaster:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> StaminaModelMaster:
        self.recover_value_table_name = recover_value_table_name
        return self

    def with_created_at(self, created_at: int) -> StaminaModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> StaminaModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> StaminaModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        stamina_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:stamina:{namespaceName}:model:{staminaName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            staminaName=stamina_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):model:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):model:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):model:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_stamina_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+):model:(?P<staminaName>.+)', grn)
        if match is None:
            return None
        return match.group('stamina_name')

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
    ) -> Optional[StaminaModelMaster]:
        if data is None:
            return None
        return StaminaModelMaster()\
            .with_stamina_model_id(data.get('staminaModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_is_overflow(data.get('isOverflow'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "staminaModelId": self.stamina_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
            "initialCapacity": self.initial_capacity,
            "isOverflow": self.is_overflow,
            "maxCapacity": self.max_capacity,
            "maxStaminaTableName": self.max_stamina_table_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
            "recoverValueTableName": self.recover_value_table_name,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    overflow_trigger_script: str = None
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

    def with_overflow_trigger_script(self, overflow_trigger_script: str) -> Namespace:
        self.overflow_trigger_script = overflow_trigger_script
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
        return 'grn:gs2:{region}:{ownerId}:stamina:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stamina:(?P<namespaceName>.+)', grn)
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
            .with_overflow_trigger_script(data.get('overflowTriggerScript'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "overflowTriggerScript": self.overflow_trigger_script,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }