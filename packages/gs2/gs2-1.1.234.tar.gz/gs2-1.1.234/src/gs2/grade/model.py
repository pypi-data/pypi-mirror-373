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


class CurrentGradeMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentGradeMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentGradeMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:grade:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentGradeMaster]:
        if data is None:
            return None
        return CurrentGradeMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class AcquireActionRate(core.Gs2Model):
    name: str = None
    mode: str = None
    rates: List[float] = None
    big_rates: List[str] = None

    def with_name(self, name: str) -> AcquireActionRate:
        self.name = name
        return self

    def with_mode(self, mode: str) -> AcquireActionRate:
        self.mode = mode
        return self

    def with_rates(self, rates: List[float]) -> AcquireActionRate:
        self.rates = rates
        return self

    def with_big_rates(self, big_rates: List[str]) -> AcquireActionRate:
        self.big_rates = big_rates
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
    ) -> Optional[AcquireActionRate]:
        if data is None:
            return None
        return AcquireActionRate()\
            .with_name(data.get('name'))\
            .with_mode(data.get('mode'))\
            .with_rates(None if data.get('rates') is None else [
                data.get('rates')[i]
                for i in range(len(data.get('rates')))
            ])\
            .with_big_rates(None if data.get('bigRates') is None else [
                data.get('bigRates')[i]
                for i in range(len(data.get('bigRates')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "mode": self.mode,
            "rates": None if self.rates is None else [
                self.rates[i]
                for i in range(len(self.rates))
            ],
            "bigRates": None if self.big_rates is None else [
                self.big_rates[i]
                for i in range(len(self.big_rates))
            ],
        }


class GradeEntryModel(core.Gs2Model):
    metadata: str = None
    rank_cap_value: int = None
    property_id_regex: str = None
    grade_up_property_id_regex: str = None

    def with_metadata(self, metadata: str) -> GradeEntryModel:
        self.metadata = metadata
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> GradeEntryModel:
        self.rank_cap_value = rank_cap_value
        return self

    def with_property_id_regex(self, property_id_regex: str) -> GradeEntryModel:
        self.property_id_regex = property_id_regex
        return self

    def with_grade_up_property_id_regex(self, grade_up_property_id_regex: str) -> GradeEntryModel:
        self.grade_up_property_id_regex = grade_up_property_id_regex
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
    ) -> Optional[GradeEntryModel]:
        if data is None:
            return None
        return GradeEntryModel()\
            .with_metadata(data.get('metadata'))\
            .with_rank_cap_value(data.get('rankCapValue'))\
            .with_property_id_regex(data.get('propertyIdRegex'))\
            .with_grade_up_property_id_regex(data.get('gradeUpPropertyIdRegex'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata,
            "rankCapValue": self.rank_cap_value,
            "propertyIdRegex": self.property_id_regex,
            "gradeUpPropertyIdRegex": self.grade_up_property_id_regex,
        }


class DefaultGradeModel(core.Gs2Model):
    property_id_regex: str = None
    default_grade_value: int = None

    def with_property_id_regex(self, property_id_regex: str) -> DefaultGradeModel:
        self.property_id_regex = property_id_regex
        return self

    def with_default_grade_value(self, default_grade_value: int) -> DefaultGradeModel:
        self.default_grade_value = default_grade_value
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
    ) -> Optional[DefaultGradeModel]:
        if data is None:
            return None
        return DefaultGradeModel()\
            .with_property_id_regex(data.get('propertyIdRegex'))\
            .with_default_grade_value(data.get('defaultGradeValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "propertyIdRegex": self.property_id_regex,
            "defaultGradeValue": self.default_grade_value,
        }


class Status(core.Gs2Model):
    status_id: str = None
    grade_name: str = None
    user_id: str = None
    property_id: str = None
    grade_value: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_status_id(self, status_id: str) -> Status:
        self.status_id = status_id
        return self

    def with_grade_name(self, grade_name: str) -> Status:
        self.grade_name = grade_name
        return self

    def with_user_id(self, user_id: str) -> Status:
        self.user_id = user_id
        return self

    def with_property_id(self, property_id: str) -> Status:
        self.property_id = property_id
        return self

    def with_grade_value(self, grade_value: int) -> Status:
        self.grade_value = grade_value
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
        grade_name,
        property_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:grade:{namespaceName}:user:{userId}:gradeModel:{gradeName}:property:{propertyId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            gradeName=grade_name,
            propertyId=property_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):user:(?P<userId>.+):gradeModel:(?P<gradeName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):user:(?P<userId>.+):gradeModel:(?P<gradeName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):user:(?P<userId>.+):gradeModel:(?P<gradeName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):user:(?P<userId>.+):gradeModel:(?P<gradeName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_grade_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):user:(?P<userId>.+):gradeModel:(?P<gradeName>.+):property:(?P<propertyId>.+)', grn)
        if match is None:
            return None
        return match.group('grade_name')

    @classmethod
    def get_property_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):user:(?P<userId>.+):gradeModel:(?P<gradeName>.+):property:(?P<propertyId>.+)', grn)
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
            .with_grade_name(data.get('gradeName'))\
            .with_user_id(data.get('userId'))\
            .with_property_id(data.get('propertyId'))\
            .with_grade_value(data.get('gradeValue'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statusId": self.status_id,
            "gradeName": self.grade_name,
            "userId": self.user_id,
            "propertyId": self.property_id,
            "gradeValue": self.grade_value,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class GradeModel(core.Gs2Model):
    grade_model_id: str = None
    name: str = None
    metadata: str = None
    default_grades: List[DefaultGradeModel] = None
    experience_model_id: str = None
    grade_entries: List[GradeEntryModel] = None
    acquire_action_rates: List[AcquireActionRate] = None

    def with_grade_model_id(self, grade_model_id: str) -> GradeModel:
        self.grade_model_id = grade_model_id
        return self

    def with_name(self, name: str) -> GradeModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> GradeModel:
        self.metadata = metadata
        return self

    def with_default_grades(self, default_grades: List[DefaultGradeModel]) -> GradeModel:
        self.default_grades = default_grades
        return self

    def with_experience_model_id(self, experience_model_id: str) -> GradeModel:
        self.experience_model_id = experience_model_id
        return self

    def with_grade_entries(self, grade_entries: List[GradeEntryModel]) -> GradeModel:
        self.grade_entries = grade_entries
        return self

    def with_acquire_action_rates(self, acquire_action_rates: List[AcquireActionRate]) -> GradeModel:
        self.acquire_action_rates = acquire_action_rates
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        grade_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:grade:{namespaceName}:model:{gradeName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            gradeName=grade_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):model:(?P<gradeName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):model:(?P<gradeName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):model:(?P<gradeName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_grade_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):model:(?P<gradeName>.+)', grn)
        if match is None:
            return None
        return match.group('grade_name')

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
    ) -> Optional[GradeModel]:
        if data is None:
            return None
        return GradeModel()\
            .with_grade_model_id(data.get('gradeModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_default_grades(None if data.get('defaultGrades') is None else [
                DefaultGradeModel.from_dict(data.get('defaultGrades')[i])
                for i in range(len(data.get('defaultGrades')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_grade_entries(None if data.get('gradeEntries') is None else [
                GradeEntryModel.from_dict(data.get('gradeEntries')[i])
                for i in range(len(data.get('gradeEntries')))
            ])\
            .with_acquire_action_rates(None if data.get('acquireActionRates') is None else [
                AcquireActionRate.from_dict(data.get('acquireActionRates')[i])
                for i in range(len(data.get('acquireActionRates')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gradeModelId": self.grade_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "defaultGrades": None if self.default_grades is None else [
                self.default_grades[i].to_dict() if self.default_grades[i] else None
                for i in range(len(self.default_grades))
            ],
            "experienceModelId": self.experience_model_id,
            "gradeEntries": None if self.grade_entries is None else [
                self.grade_entries[i].to_dict() if self.grade_entries[i] else None
                for i in range(len(self.grade_entries))
            ],
            "acquireActionRates": None if self.acquire_action_rates is None else [
                self.acquire_action_rates[i].to_dict() if self.acquire_action_rates[i] else None
                for i in range(len(self.acquire_action_rates))
            ],
        }


class GradeModelMaster(core.Gs2Model):
    grade_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    default_grades: List[DefaultGradeModel] = None
    experience_model_id: str = None
    grade_entries: List[GradeEntryModel] = None
    acquire_action_rates: List[AcquireActionRate] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_grade_model_id(self, grade_model_id: str) -> GradeModelMaster:
        self.grade_model_id = grade_model_id
        return self

    def with_name(self, name: str) -> GradeModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> GradeModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> GradeModelMaster:
        self.metadata = metadata
        return self

    def with_default_grades(self, default_grades: List[DefaultGradeModel]) -> GradeModelMaster:
        self.default_grades = default_grades
        return self

    def with_experience_model_id(self, experience_model_id: str) -> GradeModelMaster:
        self.experience_model_id = experience_model_id
        return self

    def with_grade_entries(self, grade_entries: List[GradeEntryModel]) -> GradeModelMaster:
        self.grade_entries = grade_entries
        return self

    def with_acquire_action_rates(self, acquire_action_rates: List[AcquireActionRate]) -> GradeModelMaster:
        self.acquire_action_rates = acquire_action_rates
        return self

    def with_created_at(self, created_at: int) -> GradeModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> GradeModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> GradeModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        grade_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:grade:{namespaceName}:model:{gradeName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            gradeName=grade_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):model:(?P<gradeName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):model:(?P<gradeName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):model:(?P<gradeName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_grade_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+):model:(?P<gradeName>.+)', grn)
        if match is None:
            return None
        return match.group('grade_name')

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
    ) -> Optional[GradeModelMaster]:
        if data is None:
            return None
        return GradeModelMaster()\
            .with_grade_model_id(data.get('gradeModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_grades(None if data.get('defaultGrades') is None else [
                DefaultGradeModel.from_dict(data.get('defaultGrades')[i])
                for i in range(len(data.get('defaultGrades')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_grade_entries(None if data.get('gradeEntries') is None else [
                GradeEntryModel.from_dict(data.get('gradeEntries')[i])
                for i in range(len(data.get('gradeEntries')))
            ])\
            .with_acquire_action_rates(None if data.get('acquireActionRates') is None else [
                AcquireActionRate.from_dict(data.get('acquireActionRates')[i])
                for i in range(len(data.get('acquireActionRates')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gradeModelId": self.grade_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultGrades": None if self.default_grades is None else [
                self.default_grades[i].to_dict() if self.default_grades[i] else None
                for i in range(len(self.default_grades))
            ],
            "experienceModelId": self.experience_model_id,
            "gradeEntries": None if self.grade_entries is None else [
                self.grade_entries[i].to_dict() if self.grade_entries[i] else None
                for i in range(len(self.grade_entries))
            ],
            "acquireActionRates": None if self.acquire_action_rates is None else [
                self.acquire_action_rates[i].to_dict() if self.acquire_action_rates[i] else None
                for i in range(len(self.acquire_action_rates))
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
    change_grade_script: ScriptSetting = None
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

    def with_change_grade_script(self, change_grade_script: ScriptSetting) -> Namespace:
        self.change_grade_script = change_grade_script
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
        return 'grn:gs2:{region}:{ownerId}:grade:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):grade:(?P<namespaceName>.+)', grn)
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
            .with_change_grade_script(ScriptSetting.from_dict(data.get('changeGradeScript')))\
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
            "changeGradeScript": self.change_grade_script.to_dict() if self.change_grade_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }