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


class CurrentCampaignMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentCampaignMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentCampaignMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:serialKey:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentCampaignMaster]:
        if data is None:
            return None
        return CurrentCampaignMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class CampaignModelMaster(core.Gs2Model):
    campaign_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    enable_campaign_code: bool = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_campaign_id(self, campaign_id: str) -> CampaignModelMaster:
        self.campaign_id = campaign_id
        return self

    def with_name(self, name: str) -> CampaignModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> CampaignModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CampaignModelMaster:
        self.metadata = metadata
        return self

    def with_enable_campaign_code(self, enable_campaign_code: bool) -> CampaignModelMaster:
        self.enable_campaign_code = enable_campaign_code
        return self

    def with_created_at(self, created_at: int) -> CampaignModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> CampaignModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> CampaignModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        campaign_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:serialKey:{namespaceName}:master:campaign:{campaignModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            campaignModelName=campaign_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):master:campaign:(?P<campaignModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):master:campaign:(?P<campaignModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):master:campaign:(?P<campaignModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_campaign_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):master:campaign:(?P<campaignModelName>.+)', grn)
        if match is None:
            return None
        return match.group('campaign_model_name')

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
    ) -> Optional[CampaignModelMaster]:
        if data is None:
            return None
        return CampaignModelMaster()\
            .with_campaign_id(data.get('campaignId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_enable_campaign_code(data.get('enableCampaignCode'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaignId": self.campaign_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "enableCampaignCode": self.enable_campaign_code,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class CampaignModel(core.Gs2Model):
    campaign_id: str = None
    name: str = None
    metadata: str = None
    enable_campaign_code: bool = None

    def with_campaign_id(self, campaign_id: str) -> CampaignModel:
        self.campaign_id = campaign_id
        return self

    def with_name(self, name: str) -> CampaignModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CampaignModel:
        self.metadata = metadata
        return self

    def with_enable_campaign_code(self, enable_campaign_code: bool) -> CampaignModel:
        self.enable_campaign_code = enable_campaign_code
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        campaign_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:serialKey:{namespaceName}:model:campaign:{campaignModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            campaignModelName=campaign_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_campaign_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+)', grn)
        if match is None:
            return None
        return match.group('campaign_model_name')

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
    ) -> Optional[CampaignModel]:
        if data is None:
            return None
        return CampaignModel()\
            .with_campaign_id(data.get('campaignId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_enable_campaign_code(data.get('enableCampaignCode'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "campaignId": self.campaign_id,
            "name": self.name,
            "metadata": self.metadata,
            "enableCampaignCode": self.enable_campaign_code,
        }


class SerialKey(core.Gs2Model):
    serial_key_id: str = None
    campaign_model_name: str = None
    code: str = None
    metadata: str = None
    status: str = None
    used_user_id: str = None
    created_at: int = None
    used_at: int = None
    updated_at: int = None
    revision: int = None

    def with_serial_key_id(self, serial_key_id: str) -> SerialKey:
        self.serial_key_id = serial_key_id
        return self

    def with_campaign_model_name(self, campaign_model_name: str) -> SerialKey:
        self.campaign_model_name = campaign_model_name
        return self

    def with_code(self, code: str) -> SerialKey:
        self.code = code
        return self

    def with_metadata(self, metadata: str) -> SerialKey:
        self.metadata = metadata
        return self

    def with_status(self, status: str) -> SerialKey:
        self.status = status
        return self

    def with_used_user_id(self, used_user_id: str) -> SerialKey:
        self.used_user_id = used_user_id
        return self

    def with_created_at(self, created_at: int) -> SerialKey:
        self.created_at = created_at
        return self

    def with_used_at(self, used_at: int) -> SerialKey:
        self.used_at = used_at
        return self

    def with_updated_at(self, updated_at: int) -> SerialKey:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SerialKey:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        serial_key_code,
    ):
        return 'grn:gs2:{region}:{ownerId}:serialKey:{namespaceName}:serialKey:{serialKeyCode}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            serialKeyCode=serial_key_code,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):serialKey:(?P<serialKeyCode>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):serialKey:(?P<serialKeyCode>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):serialKey:(?P<serialKeyCode>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_serial_key_code_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):serialKey:(?P<serialKeyCode>.+)', grn)
        if match is None:
            return None
        return match.group('serial_key_code')

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
    ) -> Optional[SerialKey]:
        if data is None:
            return None
        return SerialKey()\
            .with_serial_key_id(data.get('serialKeyId'))\
            .with_campaign_model_name(data.get('campaignModelName'))\
            .with_code(data.get('code'))\
            .with_metadata(data.get('metadata'))\
            .with_status(data.get('status'))\
            .with_used_user_id(data.get('usedUserId'))\
            .with_created_at(data.get('createdAt'))\
            .with_used_at(data.get('usedAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "serialKeyId": self.serial_key_id,
            "campaignModelName": self.campaign_model_name,
            "code": self.code,
            "metadata": self.metadata,
            "status": self.status,
            "usedUserId": self.used_user_id,
            "createdAt": self.created_at,
            "usedAt": self.used_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class IssueJob(core.Gs2Model):
    issue_job_id: str = None
    name: str = None
    metadata: str = None
    issued_count: int = None
    issue_request_count: int = None
    status: str = None
    created_at: int = None
    revision: int = None

    def with_issue_job_id(self, issue_job_id: str) -> IssueJob:
        self.issue_job_id = issue_job_id
        return self

    def with_name(self, name: str) -> IssueJob:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> IssueJob:
        self.metadata = metadata
        return self

    def with_issued_count(self, issued_count: int) -> IssueJob:
        self.issued_count = issued_count
        return self

    def with_issue_request_count(self, issue_request_count: int) -> IssueJob:
        self.issue_request_count = issue_request_count
        return self

    def with_status(self, status: str) -> IssueJob:
        self.status = status
        return self

    def with_created_at(self, created_at: int) -> IssueJob:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> IssueJob:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        campaign_model_name,
        issue_job_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:serialKey:{namespaceName}:model:campaign:{campaignModelName}:issue:job:{issueJobName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            campaignModelName=campaign_model_name,
            issueJobName=issue_job_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+):issue:job:(?P<issueJobName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+):issue:job:(?P<issueJobName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+):issue:job:(?P<issueJobName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_campaign_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+):issue:job:(?P<issueJobName>.+)', grn)
        if match is None:
            return None
        return match.group('campaign_model_name')

    @classmethod
    def get_issue_job_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+):model:campaign:(?P<campaignModelName>.+):issue:job:(?P<issueJobName>.+)', grn)
        if match is None:
            return None
        return match.group('issue_job_name')

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
    ) -> Optional[IssueJob]:
        if data is None:
            return None
        return IssueJob()\
            .with_issue_job_id(data.get('issueJobId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_issued_count(data.get('issuedCount'))\
            .with_issue_request_count(data.get('issueRequestCount'))\
            .with_status(data.get('status'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "issueJobId": self.issue_job_id,
            "name": self.name,
            "metadata": self.metadata,
            "issuedCount": self.issued_count,
            "issueRequestCount": self.issue_request_count,
            "status": self.status,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
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
        return 'grn:gs2:{region}:{ownerId}:serialKey:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):serialKey:(?P<namespaceName>.+)', grn)
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }