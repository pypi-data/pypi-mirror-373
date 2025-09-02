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


class OverrideBuffRate(core.Gs2Model):
    name: str = None
    rate: float = None

    def with_name(self, name: str) -> OverrideBuffRate:
        self.name = name
        return self

    def with_rate(self, rate: float) -> OverrideBuffRate:
        self.rate = rate
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
    ) -> Optional[OverrideBuffRate]:
        if data is None:
            return None
        return OverrideBuffRate()\
            .with_name(data.get('name'))\
            .with_rate(data.get('rate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "rate": self.rate,
        }


class CurrentBuffMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentBuffMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentBuffMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:buff:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentBuffMaster]:
        if data is None:
            return None
        return CurrentBuffMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class BuffEntryModelMaster(core.Gs2Model):
    buff_entry_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    expression: str = None
    target_type: str = None
    target_model: BuffTargetModel = None
    target_action: BuffTargetAction = None
    priority: int = None
    apply_period_schedule_event_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_buff_entry_model_id(self, buff_entry_model_id: str) -> BuffEntryModelMaster:
        self.buff_entry_model_id = buff_entry_model_id
        return self

    def with_name(self, name: str) -> BuffEntryModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> BuffEntryModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> BuffEntryModelMaster:
        self.metadata = metadata
        return self

    def with_expression(self, expression: str) -> BuffEntryModelMaster:
        self.expression = expression
        return self

    def with_target_type(self, target_type: str) -> BuffEntryModelMaster:
        self.target_type = target_type
        return self

    def with_target_model(self, target_model: BuffTargetModel) -> BuffEntryModelMaster:
        self.target_model = target_model
        return self

    def with_target_action(self, target_action: BuffTargetAction) -> BuffEntryModelMaster:
        self.target_action = target_action
        return self

    def with_priority(self, priority: int) -> BuffEntryModelMaster:
        self.priority = priority
        return self

    def with_apply_period_schedule_event_id(self, apply_period_schedule_event_id: str) -> BuffEntryModelMaster:
        self.apply_period_schedule_event_id = apply_period_schedule_event_id
        return self

    def with_created_at(self, created_at: int) -> BuffEntryModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BuffEntryModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> BuffEntryModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        buff_entry_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:buff:{namespaceName}:model:{buffEntryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            buffEntryName=buff_entry_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+):model:(?P<buffEntryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+):model:(?P<buffEntryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+):model:(?P<buffEntryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_buff_entry_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+):model:(?P<buffEntryName>.+)', grn)
        if match is None:
            return None
        return match.group('buff_entry_name')

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
    ) -> Optional[BuffEntryModelMaster]:
        if data is None:
            return None
        return BuffEntryModelMaster()\
            .with_buff_entry_model_id(data.get('buffEntryModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_expression(data.get('expression'))\
            .with_target_type(data.get('targetType'))\
            .with_target_model(BuffTargetModel.from_dict(data.get('targetModel')))\
            .with_target_action(BuffTargetAction.from_dict(data.get('targetAction')))\
            .with_priority(data.get('priority'))\
            .with_apply_period_schedule_event_id(data.get('applyPeriodScheduleEventId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "buffEntryModelId": self.buff_entry_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "expression": self.expression,
            "targetType": self.target_type,
            "targetModel": self.target_model.to_dict() if self.target_model else None,
            "targetAction": self.target_action.to_dict() if self.target_action else None,
            "priority": self.priority,
            "applyPeriodScheduleEventId": self.apply_period_schedule_event_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class BuffEntryModel(core.Gs2Model):
    buff_entry_model_id: str = None
    name: str = None
    metadata: str = None
    expression: str = None
    target_type: str = None
    target_model: BuffTargetModel = None
    target_action: BuffTargetAction = None
    priority: int = None
    apply_period_schedule_event_id: str = None

    def with_buff_entry_model_id(self, buff_entry_model_id: str) -> BuffEntryModel:
        self.buff_entry_model_id = buff_entry_model_id
        return self

    def with_name(self, name: str) -> BuffEntryModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> BuffEntryModel:
        self.metadata = metadata
        return self

    def with_expression(self, expression: str) -> BuffEntryModel:
        self.expression = expression
        return self

    def with_target_type(self, target_type: str) -> BuffEntryModel:
        self.target_type = target_type
        return self

    def with_target_model(self, target_model: BuffTargetModel) -> BuffEntryModel:
        self.target_model = target_model
        return self

    def with_target_action(self, target_action: BuffTargetAction) -> BuffEntryModel:
        self.target_action = target_action
        return self

    def with_priority(self, priority: int) -> BuffEntryModel:
        self.priority = priority
        return self

    def with_apply_period_schedule_event_id(self, apply_period_schedule_event_id: str) -> BuffEntryModel:
        self.apply_period_schedule_event_id = apply_period_schedule_event_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        buff_entry_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:buff:{namespaceName}:model:{buffEntryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            buffEntryName=buff_entry_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+):model:(?P<buffEntryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+):model:(?P<buffEntryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+):model:(?P<buffEntryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_buff_entry_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+):model:(?P<buffEntryName>.+)', grn)
        if match is None:
            return None
        return match.group('buff_entry_name')

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
    ) -> Optional[BuffEntryModel]:
        if data is None:
            return None
        return BuffEntryModel()\
            .with_buff_entry_model_id(data.get('buffEntryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_expression(data.get('expression'))\
            .with_target_type(data.get('targetType'))\
            .with_target_model(BuffTargetModel.from_dict(data.get('targetModel')))\
            .with_target_action(BuffTargetAction.from_dict(data.get('targetAction')))\
            .with_priority(data.get('priority'))\
            .with_apply_period_schedule_event_id(data.get('applyPeriodScheduleEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "buffEntryModelId": self.buff_entry_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "expression": self.expression,
            "targetType": self.target_type,
            "targetModel": self.target_model.to_dict() if self.target_model else None,
            "targetAction": self.target_action.to_dict() if self.target_action else None,
            "priority": self.priority,
            "applyPeriodScheduleEventId": self.apply_period_schedule_event_id,
        }


class BuffTargetGrn(core.Gs2Model):
    target_model_name: str = None
    target_grn: str = None

    def with_target_model_name(self, target_model_name: str) -> BuffTargetGrn:
        self.target_model_name = target_model_name
        return self

    def with_target_grn(self, target_grn: str) -> BuffTargetGrn:
        self.target_grn = target_grn
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
    ) -> Optional[BuffTargetGrn]:
        if data is None:
            return None
        return BuffTargetGrn()\
            .with_target_model_name(data.get('targetModelName'))\
            .with_target_grn(data.get('targetGrn'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "targetModelName": self.target_model_name,
            "targetGrn": self.target_grn,
        }


class BuffTargetAction(core.Gs2Model):
    target_action_name: str = None
    target_field_name: str = None
    condition_grns: List[BuffTargetGrn] = None
    rate: float = None

    def with_target_action_name(self, target_action_name: str) -> BuffTargetAction:
        self.target_action_name = target_action_name
        return self

    def with_target_field_name(self, target_field_name: str) -> BuffTargetAction:
        self.target_field_name = target_field_name
        return self

    def with_condition_grns(self, condition_grns: List[BuffTargetGrn]) -> BuffTargetAction:
        self.condition_grns = condition_grns
        return self

    def with_rate(self, rate: float) -> BuffTargetAction:
        self.rate = rate
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
    ) -> Optional[BuffTargetAction]:
        if data is None:
            return None
        return BuffTargetAction()\
            .with_target_action_name(data.get('targetActionName'))\
            .with_target_field_name(data.get('targetFieldName'))\
            .with_condition_grns(None if data.get('conditionGrns') is None else [
                BuffTargetGrn.from_dict(data.get('conditionGrns')[i])
                for i in range(len(data.get('conditionGrns')))
            ])\
            .with_rate(data.get('rate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "targetActionName": self.target_action_name,
            "targetFieldName": self.target_field_name,
            "conditionGrns": None if self.condition_grns is None else [
                self.condition_grns[i].to_dict() if self.condition_grns[i] else None
                for i in range(len(self.condition_grns))
            ],
            "rate": self.rate,
        }


class BuffTargetModel(core.Gs2Model):
    target_model_name: str = None
    target_field_name: str = None
    condition_grns: List[BuffTargetGrn] = None
    rate: float = None

    def with_target_model_name(self, target_model_name: str) -> BuffTargetModel:
        self.target_model_name = target_model_name
        return self

    def with_target_field_name(self, target_field_name: str) -> BuffTargetModel:
        self.target_field_name = target_field_name
        return self

    def with_condition_grns(self, condition_grns: List[BuffTargetGrn]) -> BuffTargetModel:
        self.condition_grns = condition_grns
        return self

    def with_rate(self, rate: float) -> BuffTargetModel:
        self.rate = rate
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
    ) -> Optional[BuffTargetModel]:
        if data is None:
            return None
        return BuffTargetModel()\
            .with_target_model_name(data.get('targetModelName'))\
            .with_target_field_name(data.get('targetFieldName'))\
            .with_condition_grns(None if data.get('conditionGrns') is None else [
                BuffTargetGrn.from_dict(data.get('conditionGrns')[i])
                for i in range(len(data.get('conditionGrns')))
            ])\
            .with_rate(data.get('rate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "targetModelName": self.target_model_name,
            "targetFieldName": self.target_field_name,
            "conditionGrns": None if self.condition_grns is None else [
                self.condition_grns[i].to_dict() if self.condition_grns[i] else None
                for i in range(len(self.condition_grns))
            ],
            "rate": self.rate,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    apply_buff_script: ScriptSetting = None
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

    def with_apply_buff_script(self, apply_buff_script: ScriptSetting) -> Namespace:
        self.apply_buff_script = apply_buff_script
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
        return 'grn:gs2:{region}:{ownerId}:buff:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):buff:(?P<namespaceName>.+)', grn)
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
            .with_apply_buff_script(ScriptSetting.from_dict(data.get('applyBuffScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "applyBuffScript": self.apply_buff_script.to_dict() if self.apply_buff_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }