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


class ScheduleVersion(core.Gs2Model):
    current_version: Version = None
    warning_version: Version = None
    error_version: Version = None
    schedule_event_id: str = None

    def with_current_version(self, current_version: Version) -> ScheduleVersion:
        self.current_version = current_version
        return self

    def with_warning_version(self, warning_version: Version) -> ScheduleVersion:
        self.warning_version = warning_version
        return self

    def with_error_version(self, error_version: Version) -> ScheduleVersion:
        self.error_version = error_version
        return self

    def with_schedule_event_id(self, schedule_event_id: str) -> ScheduleVersion:
        self.schedule_event_id = schedule_event_id
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
    ) -> Optional[ScheduleVersion]:
        if data is None:
            return None
        return ScheduleVersion()\
            .with_current_version(Version.from_dict(data.get('currentVersion')))\
            .with_warning_version(Version.from_dict(data.get('warningVersion')))\
            .with_error_version(Version.from_dict(data.get('errorVersion')))\
            .with_schedule_event_id(data.get('scheduleEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "currentVersion": self.current_version.to_dict() if self.current_version else None,
            "warningVersion": self.warning_version.to_dict() if self.warning_version else None,
            "errorVersion": self.error_version.to_dict() if self.error_version else None,
            "scheduleEventId": self.schedule_event_id,
        }


class Version(core.Gs2Model):
    major: int = None
    minor: int = None
    micro: int = None

    def with_major(self, major: int) -> Version:
        self.major = major
        return self

    def with_minor(self, minor: int) -> Version:
        self.minor = minor
        return self

    def with_micro(self, micro: int) -> Version:
        self.micro = micro
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
    ) -> Optional[Version]:
        if data is None:
            return None
        return Version()\
            .with_major(data.get('major'))\
            .with_minor(data.get('minor'))\
            .with_micro(data.get('micro'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "major": self.major,
            "minor": self.minor,
            "micro": self.micro,
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


class CurrentVersionMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentVersionMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentVersionMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:version:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentVersionMaster]:
        if data is None:
            return None
        return CurrentVersionMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class SignTargetVersion(core.Gs2Model):
    region: str = None
    namespace_name: str = None
    version_name: str = None
    version: Version = None

    def with_region(self, region: str) -> SignTargetVersion:
        self.region = region
        return self

    def with_namespace_name(self, namespace_name: str) -> SignTargetVersion:
        self.namespace_name = namespace_name
        return self

    def with_version_name(self, version_name: str) -> SignTargetVersion:
        self.version_name = version_name
        return self

    def with_version(self, version: Version) -> SignTargetVersion:
        self.version = version
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
    ) -> Optional[SignTargetVersion]:
        if data is None:
            return None
        return SignTargetVersion()\
            .with_region(data.get('region'))\
            .with_namespace_name(data.get('namespaceName'))\
            .with_version_name(data.get('versionName'))\
            .with_version(Version.from_dict(data.get('version')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region": self.region,
            "namespaceName": self.namespace_name,
            "versionName": self.version_name,
            "version": self.version.to_dict() if self.version else None,
        }


class TargetVersion(core.Gs2Model):
    version_name: str = None
    body: str = None
    signature: str = None
    version: Version = None

    def with_version_name(self, version_name: str) -> TargetVersion:
        self.version_name = version_name
        return self

    def with_body(self, body: str) -> TargetVersion:
        self.body = body
        return self

    def with_signature(self, signature: str) -> TargetVersion:
        self.signature = signature
        return self

    def with_version(self, version: Version) -> TargetVersion:
        self.version = version
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
    ) -> Optional[TargetVersion]:
        if data is None:
            return None
        return TargetVersion()\
            .with_version_name(data.get('versionName'))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))\
            .with_version(Version.from_dict(data.get('version')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "versionName": self.version_name,
            "body": self.body,
            "signature": self.signature,
            "version": self.version.to_dict() if self.version else None,
        }


class Status(core.Gs2Model):
    version_model: VersionModel = None
    current_version: Version = None

    def with_version_model(self, version_model: VersionModel) -> Status:
        self.version_model = version_model
        return self

    def with_current_version(self, current_version: Version) -> Status:
        self.current_version = current_version
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
    ) -> Optional[Status]:
        if data is None:
            return None
        return Status()\
            .with_version_model(VersionModel.from_dict(data.get('versionModel')))\
            .with_current_version(Version.from_dict(data.get('currentVersion')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "versionModel": self.version_model.to_dict() if self.version_model else None,
            "currentVersion": self.current_version.to_dict() if self.current_version else None,
        }


class AcceptVersion(core.Gs2Model):
    accept_version_id: str = None
    version_name: str = None
    user_id: str = None
    version: Version = None
    status: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_accept_version_id(self, accept_version_id: str) -> AcceptVersion:
        self.accept_version_id = accept_version_id
        return self

    def with_version_name(self, version_name: str) -> AcceptVersion:
        self.version_name = version_name
        return self

    def with_user_id(self, user_id: str) -> AcceptVersion:
        self.user_id = user_id
        return self

    def with_version(self, version: Version) -> AcceptVersion:
        self.version = version
        return self

    def with_status(self, status: str) -> AcceptVersion:
        self.status = status
        return self

    def with_created_at(self, created_at: int) -> AcceptVersion:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> AcceptVersion:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> AcceptVersion:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        version_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:version:{namespaceName}:user:{userId}:version:{versionName}:accept'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            versionName=version_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):user:(?P<userId>.+):version:(?P<versionName>.+):accept', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):user:(?P<userId>.+):version:(?P<versionName>.+):accept', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):user:(?P<userId>.+):version:(?P<versionName>.+):accept', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):user:(?P<userId>.+):version:(?P<versionName>.+):accept', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_version_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):user:(?P<userId>.+):version:(?P<versionName>.+):accept', grn)
        if match is None:
            return None
        return match.group('version_name')

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
    ) -> Optional[AcceptVersion]:
        if data is None:
            return None
        return AcceptVersion()\
            .with_accept_version_id(data.get('acceptVersionId'))\
            .with_version_name(data.get('versionName'))\
            .with_user_id(data.get('userId'))\
            .with_version(Version.from_dict(data.get('version')))\
            .with_status(data.get('status'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "acceptVersionId": self.accept_version_id,
            "versionName": self.version_name,
            "userId": self.user_id,
            "version": self.version.to_dict() if self.version else None,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class VersionModel(core.Gs2Model):
    version_model_id: str = None
    name: str = None
    metadata: str = None
    scope: str = None
    type: str = None
    current_version: Version = None
    warning_version: Version = None
    error_version: Version = None
    schedule_versions: List[ScheduleVersion] = None
    need_signature: bool = None
    signature_key_id: str = None
    approve_requirement: str = None

    def with_version_model_id(self, version_model_id: str) -> VersionModel:
        self.version_model_id = version_model_id
        return self

    def with_name(self, name: str) -> VersionModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> VersionModel:
        self.metadata = metadata
        return self

    def with_scope(self, scope: str) -> VersionModel:
        self.scope = scope
        return self

    def with_type(self, type: str) -> VersionModel:
        self.type = type
        return self

    def with_current_version(self, current_version: Version) -> VersionModel:
        self.current_version = current_version
        return self

    def with_warning_version(self, warning_version: Version) -> VersionModel:
        self.warning_version = warning_version
        return self

    def with_error_version(self, error_version: Version) -> VersionModel:
        self.error_version = error_version
        return self

    def with_schedule_versions(self, schedule_versions: List[ScheduleVersion]) -> VersionModel:
        self.schedule_versions = schedule_versions
        return self

    def with_need_signature(self, need_signature: bool) -> VersionModel:
        self.need_signature = need_signature
        return self

    def with_signature_key_id(self, signature_key_id: str) -> VersionModel:
        self.signature_key_id = signature_key_id
        return self

    def with_approve_requirement(self, approve_requirement: str) -> VersionModel:
        self.approve_requirement = approve_requirement
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        version_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:version:{namespaceName}:model:version:{versionName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            versionName=version_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):model:version:(?P<versionName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):model:version:(?P<versionName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):model:version:(?P<versionName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_version_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):model:version:(?P<versionName>.+)', grn)
        if match is None:
            return None
        return match.group('version_name')

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
    ) -> Optional[VersionModel]:
        if data is None:
            return None
        return VersionModel()\
            .with_version_model_id(data.get('versionModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_scope(data.get('scope'))\
            .with_type(data.get('type'))\
            .with_current_version(Version.from_dict(data.get('currentVersion')))\
            .with_warning_version(Version.from_dict(data.get('warningVersion')))\
            .with_error_version(Version.from_dict(data.get('errorVersion')))\
            .with_schedule_versions(None if data.get('scheduleVersions') is None else [
                ScheduleVersion.from_dict(data.get('scheduleVersions')[i])
                for i in range(len(data.get('scheduleVersions')))
            ])\
            .with_need_signature(data.get('needSignature'))\
            .with_signature_key_id(data.get('signatureKeyId'))\
            .with_approve_requirement(data.get('approveRequirement'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "versionModelId": self.version_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "scope": self.scope,
            "type": self.type,
            "currentVersion": self.current_version.to_dict() if self.current_version else None,
            "warningVersion": self.warning_version.to_dict() if self.warning_version else None,
            "errorVersion": self.error_version.to_dict() if self.error_version else None,
            "scheduleVersions": None if self.schedule_versions is None else [
                self.schedule_versions[i].to_dict() if self.schedule_versions[i] else None
                for i in range(len(self.schedule_versions))
            ],
            "needSignature": self.need_signature,
            "signatureKeyId": self.signature_key_id,
            "approveRequirement": self.approve_requirement,
        }


class VersionModelMaster(core.Gs2Model):
    version_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    scope: str = None
    type: str = None
    current_version: Version = None
    warning_version: Version = None
    error_version: Version = None
    schedule_versions: List[ScheduleVersion] = None
    need_signature: bool = None
    signature_key_id: str = None
    approve_requirement: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_version_model_id(self, version_model_id: str) -> VersionModelMaster:
        self.version_model_id = version_model_id
        return self

    def with_name(self, name: str) -> VersionModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> VersionModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> VersionModelMaster:
        self.metadata = metadata
        return self

    def with_scope(self, scope: str) -> VersionModelMaster:
        self.scope = scope
        return self

    def with_type(self, type: str) -> VersionModelMaster:
        self.type = type
        return self

    def with_current_version(self, current_version: Version) -> VersionModelMaster:
        self.current_version = current_version
        return self

    def with_warning_version(self, warning_version: Version) -> VersionModelMaster:
        self.warning_version = warning_version
        return self

    def with_error_version(self, error_version: Version) -> VersionModelMaster:
        self.error_version = error_version
        return self

    def with_schedule_versions(self, schedule_versions: List[ScheduleVersion]) -> VersionModelMaster:
        self.schedule_versions = schedule_versions
        return self

    def with_need_signature(self, need_signature: bool) -> VersionModelMaster:
        self.need_signature = need_signature
        return self

    def with_signature_key_id(self, signature_key_id: str) -> VersionModelMaster:
        self.signature_key_id = signature_key_id
        return self

    def with_approve_requirement(self, approve_requirement: str) -> VersionModelMaster:
        self.approve_requirement = approve_requirement
        return self

    def with_created_at(self, created_at: int) -> VersionModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> VersionModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> VersionModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        version_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:version:{namespaceName}:model:version:{versionName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            versionName=version_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):model:version:(?P<versionName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):model:version:(?P<versionName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):model:version:(?P<versionName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_version_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+):model:version:(?P<versionName>.+)', grn)
        if match is None:
            return None
        return match.group('version_name')

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
    ) -> Optional[VersionModelMaster]:
        if data is None:
            return None
        return VersionModelMaster()\
            .with_version_model_id(data.get('versionModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_scope(data.get('scope'))\
            .with_type(data.get('type'))\
            .with_current_version(Version.from_dict(data.get('currentVersion')))\
            .with_warning_version(Version.from_dict(data.get('warningVersion')))\
            .with_error_version(Version.from_dict(data.get('errorVersion')))\
            .with_schedule_versions(None if data.get('scheduleVersions') is None else [
                ScheduleVersion.from_dict(data.get('scheduleVersions')[i])
                for i in range(len(data.get('scheduleVersions')))
            ])\
            .with_need_signature(data.get('needSignature'))\
            .with_signature_key_id(data.get('signatureKeyId'))\
            .with_approve_requirement(data.get('approveRequirement'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "versionModelId": self.version_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "scope": self.scope,
            "type": self.type,
            "currentVersion": self.current_version.to_dict() if self.current_version else None,
            "warningVersion": self.warning_version.to_dict() if self.warning_version else None,
            "errorVersion": self.error_version.to_dict() if self.error_version else None,
            "scheduleVersions": None if self.schedule_versions is None else [
                self.schedule_versions[i].to_dict() if self.schedule_versions[i] else None
                for i in range(len(self.schedule_versions))
            ],
            "needSignature": self.need_signature,
            "signatureKeyId": self.signature_key_id,
            "approveRequirement": self.approve_requirement,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    assume_user_id: str = None
    accept_version_script: ScriptSetting = None
    check_version_trigger_script_id: str = None
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

    def with_assume_user_id(self, assume_user_id: str) -> Namespace:
        self.assume_user_id = assume_user_id
        return self

    def with_accept_version_script(self, accept_version_script: ScriptSetting) -> Namespace:
        self.accept_version_script = accept_version_script
        return self

    def with_check_version_trigger_script_id(self, check_version_trigger_script_id: str) -> Namespace:
        self.check_version_trigger_script_id = check_version_trigger_script_id
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
        return 'grn:gs2:{region}:{ownerId}:version:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):version:(?P<namespaceName>.+)', grn)
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
            .with_assume_user_id(data.get('assumeUserId'))\
            .with_accept_version_script(ScriptSetting.from_dict(data.get('acceptVersionScript')))\
            .with_check_version_trigger_script_id(data.get('checkVersionTriggerScriptId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "acceptVersionScript": self.accept_version_script.to_dict() if self.accept_version_script else None,
            "checkVersionTriggerScriptId": self.check_version_trigger_script_id,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }