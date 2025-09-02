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


class BanStatus(core.Gs2Model):
    name: str = None
    reason: str = None
    release_timestamp: int = None

    def with_name(self, name: str) -> BanStatus:
        self.name = name
        return self

    def with_reason(self, reason: str) -> BanStatus:
        self.reason = reason
        return self

    def with_release_timestamp(self, release_timestamp: int) -> BanStatus:
        self.release_timestamp = release_timestamp
        return self

    @classmethod
    def create_grn(
        cls,
    ):
        return ''.format(
        )

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
    ) -> Optional[BanStatus]:
        if data is None:
            return None
        return BanStatus()\
            .with_name(data.get('name'))\
            .with_reason(data.get('reason'))\
            .with_release_timestamp(data.get('releaseTimestamp'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "reason": self.reason,
            "releaseTimestamp": self.release_timestamp,
        }


class PlatformUser(core.Gs2Model):
    type: int = None
    user_identifier: str = None
    user_id: str = None

    def with_type(self, type: int) -> PlatformUser:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> PlatformUser:
        self.user_identifier = user_identifier
        return self

    def with_user_id(self, user_id: str) -> PlatformUser:
        self.user_id = user_id
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
    ) -> Optional[PlatformUser]:
        if data is None:
            return None
        return PlatformUser()\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "userId": self.user_id,
        }


class ScopeValue(core.Gs2Model):
    key: str = None
    value: str = None

    def with_key(self, key: str) -> ScopeValue:
        self.key = key
        return self

    def with_value(self, value: str) -> ScopeValue:
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
    ) -> Optional[ScopeValue]:
        if data is None:
            return None
        return ScopeValue()\
            .with_key(data.get('key'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
        }


class OpenIdConnectSetting(core.Gs2Model):
    configuration_path: str = None
    client_id: str = None
    client_secret: str = None
    apple_team_id: str = None
    apple_key_id: str = None
    apple_private_key_pem: str = None
    done_endpoint_url: str = None
    additional_scope_values: List[ScopeValue] = None
    additional_return_values: List[str] = None

    def with_configuration_path(self, configuration_path: str) -> OpenIdConnectSetting:
        self.configuration_path = configuration_path
        return self

    def with_client_id(self, client_id: str) -> OpenIdConnectSetting:
        self.client_id = client_id
        return self

    def with_client_secret(self, client_secret: str) -> OpenIdConnectSetting:
        self.client_secret = client_secret
        return self

    def with_apple_team_id(self, apple_team_id: str) -> OpenIdConnectSetting:
        self.apple_team_id = apple_team_id
        return self

    def with_apple_key_id(self, apple_key_id: str) -> OpenIdConnectSetting:
        self.apple_key_id = apple_key_id
        return self

    def with_apple_private_key_pem(self, apple_private_key_pem: str) -> OpenIdConnectSetting:
        self.apple_private_key_pem = apple_private_key_pem
        return self

    def with_done_endpoint_url(self, done_endpoint_url: str) -> OpenIdConnectSetting:
        self.done_endpoint_url = done_endpoint_url
        return self

    def with_additional_scope_values(self, additional_scope_values: List[ScopeValue]) -> OpenIdConnectSetting:
        self.additional_scope_values = additional_scope_values
        return self

    def with_additional_return_values(self, additional_return_values: List[str]) -> OpenIdConnectSetting:
        self.additional_return_values = additional_return_values
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
    ) -> Optional[OpenIdConnectSetting]:
        if data is None:
            return None
        return OpenIdConnectSetting()\
            .with_configuration_path(data.get('configurationPath'))\
            .with_client_id(data.get('clientId'))\
            .with_client_secret(data.get('clientSecret'))\
            .with_apple_team_id(data.get('appleTeamId'))\
            .with_apple_key_id(data.get('appleKeyId'))\
            .with_apple_private_key_pem(data.get('applePrivateKeyPem'))\
            .with_done_endpoint_url(data.get('doneEndpointUrl'))\
            .with_additional_scope_values(None if data.get('additionalScopeValues') is None else [
                ScopeValue.from_dict(data.get('additionalScopeValues')[i])
                for i in range(len(data.get('additionalScopeValues')))
            ])\
            .with_additional_return_values(None if data.get('additionalReturnValues') is None else [
                data.get('additionalReturnValues')[i]
                for i in range(len(data.get('additionalReturnValues')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "configurationPath": self.configuration_path,
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
            "appleTeamId": self.apple_team_id,
            "appleKeyId": self.apple_key_id,
            "applePrivateKeyPem": self.apple_private_key_pem,
            "doneEndpointUrl": self.done_endpoint_url,
            "additionalScopeValues": None if self.additional_scope_values is None else [
                self.additional_scope_values[i].to_dict() if self.additional_scope_values[i] else None
                for i in range(len(self.additional_scope_values))
            ],
            "additionalReturnValues": None if self.additional_return_values is None else [
                self.additional_return_values[i]
                for i in range(len(self.additional_return_values))
            ],
        }


class CurrentModelMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentModelMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentModelMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentModelMaster]:
        if data is None:
            return None
        return CurrentModelMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class TakeOverTypeModelMaster(core.Gs2Model):
    take_over_type_model_id: str = None
    type: int = None
    description: str = None
    metadata: str = None
    open_id_connect_setting: OpenIdConnectSetting = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_take_over_type_model_id(self, take_over_type_model_id: str) -> TakeOverTypeModelMaster:
        self.take_over_type_model_id = take_over_type_model_id
        return self

    def with_type(self, type: int) -> TakeOverTypeModelMaster:
        self.type = type
        return self

    def with_description(self, description: str) -> TakeOverTypeModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> TakeOverTypeModelMaster:
        self.metadata = metadata
        return self

    def with_open_id_connect_setting(self, open_id_connect_setting: OpenIdConnectSetting) -> TakeOverTypeModelMaster:
        self.open_id_connect_setting = open_id_connect_setting
        return self

    def with_created_at(self, created_at: int) -> TakeOverTypeModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> TakeOverTypeModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> TakeOverTypeModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        _type,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:model:takeOver:{type}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            Type=_type,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):model:takeOver:(?P<type>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):model:takeOver:(?P<type>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):model:takeOver:(?P<type>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get__type_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):model:takeOver:(?P<type>.+)', grn)
        if match is None:
            return None
        return match.group('_type')

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
    ) -> Optional[TakeOverTypeModelMaster]:
        if data is None:
            return None
        return TakeOverTypeModelMaster()\
            .with_take_over_type_model_id(data.get('takeOverTypeModelId'))\
            .with_type(data.get('type'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_open_id_connect_setting(OpenIdConnectSetting.from_dict(data.get('openIdConnectSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "takeOverTypeModelId": self.take_over_type_model_id,
            "type": self.type,
            "description": self.description,
            "metadata": self.metadata,
            "openIdConnectSetting": self.open_id_connect_setting.to_dict() if self.open_id_connect_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class TakeOverTypeModel(core.Gs2Model):
    take_over_type_model_id: str = None
    type: int = None
    metadata: str = None
    open_id_connect_setting: OpenIdConnectSetting = None

    def with_take_over_type_model_id(self, take_over_type_model_id: str) -> TakeOverTypeModel:
        self.take_over_type_model_id = take_over_type_model_id
        return self

    def with_type(self, type: int) -> TakeOverTypeModel:
        self.type = type
        return self

    def with_metadata(self, metadata: str) -> TakeOverTypeModel:
        self.metadata = metadata
        return self

    def with_open_id_connect_setting(self, open_id_connect_setting: OpenIdConnectSetting) -> TakeOverTypeModel:
        self.open_id_connect_setting = open_id_connect_setting
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        _type,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:model:takeOver:{type}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            Type=_type,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):model:takeOver:(?P<type>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):model:takeOver:(?P<type>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):model:takeOver:(?P<type>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get__type_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):model:takeOver:(?P<type>.+)', grn)
        if match is None:
            return None
        return match.group('_type')

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
    ) -> Optional[TakeOverTypeModel]:
        if data is None:
            return None
        return TakeOverTypeModel()\
            .with_take_over_type_model_id(data.get('takeOverTypeModelId'))\
            .with_type(data.get('type'))\
            .with_metadata(data.get('metadata'))\
            .with_open_id_connect_setting(OpenIdConnectSetting.from_dict(data.get('openIdConnectSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "takeOverTypeModelId": self.take_over_type_model_id,
            "type": self.type,
            "metadata": self.metadata,
            "openIdConnectSetting": self.open_id_connect_setting.to_dict() if self.open_id_connect_setting else None,
        }


class DataOwner(core.Gs2Model):
    data_owner_id: str = None
    user_id: str = None
    name: str = None
    created_at: int = None
    revision: int = None

    def with_data_owner_id(self, data_owner_id: str) -> DataOwner:
        self.data_owner_id = data_owner_id
        return self

    def with_user_id(self, user_id: str) -> DataOwner:
        self.user_id = user_id
        return self

    def with_name(self, name: str) -> DataOwner:
        self.name = name
        return self

    def with_created_at(self, created_at: int) -> DataOwner:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> DataOwner:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        data_owner_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:account:{userId}:dataOwner:{dataOwnerName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            dataOwnerName=data_owner_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_data_owner_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+):dataOwner:(?P<dataOwnerName>.+)', grn)
        if match is None:
            return None
        return match.group('data_owner_name')

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
    ) -> Optional[DataOwner]:
        if data is None:
            return None
        return DataOwner()\
            .with_data_owner_id(data.get('dataOwnerId'))\
            .with_user_id(data.get('userId'))\
            .with_name(data.get('name'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataOwnerId": self.data_owner_id,
            "userId": self.user_id,
            "name": self.name,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class PlatformId(core.Gs2Model):
    platform_id: str = None
    user_id: str = None
    type: int = None
    user_identifier: str = None
    created_at: int = None
    revision: int = None

    def with_platform_id(self, platform_id: str) -> PlatformId:
        self.platform_id = platform_id
        return self

    def with_user_id(self, user_id: str) -> PlatformId:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> PlatformId:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> PlatformId:
        self.user_identifier = user_identifier
        return self

    def with_created_at(self, created_at: int) -> PlatformId:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> PlatformId:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        _type,
        user_identifier,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:platformId:{type}:{userIdentifier}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            Type=_type,
            userIdentifier=user_identifier,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):platformId:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):platformId:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):platformId:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get__type_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):platformId:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('_type')

    @classmethod
    def get_user_identifier_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):platformId:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('user_identifier')

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
    ) -> Optional[PlatformId]:
        if data is None:
            return None
        return PlatformId()\
            .with_platform_id(data.get('platformId'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platformId": self.platform_id,
            "userId": self.user_id,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class TakeOver(core.Gs2Model):
    take_over_id: str = None
    user_id: str = None
    type: int = None
    user_identifier: str = None
    password: str = None
    created_at: int = None
    revision: int = None

    def with_take_over_id(self, take_over_id: str) -> TakeOver:
        self.take_over_id = take_over_id
        return self

    def with_user_id(self, user_id: str) -> TakeOver:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> TakeOver:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> TakeOver:
        self.user_identifier = user_identifier
        return self

    def with_password(self, password: str) -> TakeOver:
        self.password = password
        return self

    def with_created_at(self, created_at: int) -> TakeOver:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> TakeOver:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        _type,
        user_identifier,
    ):
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:takeOver:{type}:{userIdentifier}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            Type=_type,
            userIdentifier=user_identifier,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get__type_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('_type')

    @classmethod
    def get_user_identifier_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):takeOver:(?P<type>.+):(?P<userIdentifier>.+)', grn)
        if match is None:
            return None
        return match.group('user_identifier')

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
    ) -> Optional[TakeOver]:
        if data is None:
            return None
        return TakeOver()\
            .with_take_over_id(data.get('takeOverId'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_password(data.get('password'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "takeOverId": self.take_over_id,
            "userId": self.user_id,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "password": self.password,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Account(core.Gs2Model):
    account_id: str = None
    user_id: str = None
    password: str = None
    time_offset: int = None
    ban_statuses: List[BanStatus] = None
    banned: bool = None
    last_authenticated_at: int = None
    created_at: int = None
    revision: int = None

    def with_account_id(self, account_id: str) -> Account:
        self.account_id = account_id
        return self

    def with_user_id(self, user_id: str) -> Account:
        self.user_id = user_id
        return self

    def with_password(self, password: str) -> Account:
        self.password = password
        return self

    def with_time_offset(self, time_offset: int) -> Account:
        self.time_offset = time_offset
        return self

    def with_ban_statuses(self, ban_statuses: List[BanStatus]) -> Account:
        self.ban_statuses = ban_statuses
        return self

    def with_banned(self, banned: bool) -> Account:
        self.banned = banned
        return self

    def with_last_authenticated_at(self, last_authenticated_at: int) -> Account:
        self.last_authenticated_at = last_authenticated_at
        return self

    def with_created_at(self, created_at: int) -> Account:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Account:
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
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}:account:{userId}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+):account:(?P<userId>.+)', grn)
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
    ) -> Optional[Account]:
        if data is None:
            return None
        return Account()\
            .with_account_id(data.get('accountId'))\
            .with_user_id(data.get('userId'))\
            .with_password(data.get('password'))\
            .with_time_offset(data.get('timeOffset'))\
            .with_ban_statuses(None if data.get('banStatuses') is None else [
                BanStatus.from_dict(data.get('banStatuses')[i])
                for i in range(len(data.get('banStatuses')))
            ])\
            .with_banned(data.get('banned'))\
            .with_last_authenticated_at(data.get('lastAuthenticatedAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accountId": self.account_id,
            "userId": self.user_id,
            "password": self.password,
            "timeOffset": self.time_offset,
            "banStatuses": None if self.ban_statuses is None else [
                self.ban_statuses[i].to_dict() if self.ban_statuses[i] else None
                for i in range(len(self.ban_statuses))
            ],
            "banned": self.banned,
            "lastAuthenticatedAt": self.last_authenticated_at,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    change_password_if_take_over: bool = None
    different_user_id_for_login_and_data_retention: bool = None
    create_account_script: ScriptSetting = None
    authentication_script: ScriptSetting = None
    create_take_over_script: ScriptSetting = None
    do_take_over_script: ScriptSetting = None
    ban_script: ScriptSetting = None
    un_ban_script: ScriptSetting = None
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

    def with_change_password_if_take_over(self, change_password_if_take_over: bool) -> Namespace:
        self.change_password_if_take_over = change_password_if_take_over
        return self

    def with_different_user_id_for_login_and_data_retention(self, different_user_id_for_login_and_data_retention: bool) -> Namespace:
        self.different_user_id_for_login_and_data_retention = different_user_id_for_login_and_data_retention
        return self

    def with_create_account_script(self, create_account_script: ScriptSetting) -> Namespace:
        self.create_account_script = create_account_script
        return self

    def with_authentication_script(self, authentication_script: ScriptSetting) -> Namespace:
        self.authentication_script = authentication_script
        return self

    def with_create_take_over_script(self, create_take_over_script: ScriptSetting) -> Namespace:
        self.create_take_over_script = create_take_over_script
        return self

    def with_do_take_over_script(self, do_take_over_script: ScriptSetting) -> Namespace:
        self.do_take_over_script = do_take_over_script
        return self

    def with_ban_script(self, ban_script: ScriptSetting) -> Namespace:
        self.ban_script = ban_script
        return self

    def with_un_ban_script(self, un_ban_script: ScriptSetting) -> Namespace:
        self.un_ban_script = un_ban_script
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
        return 'grn:gs2:{region}:{ownerId}:account:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):account:(?P<namespaceName>.+)', grn)
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
            .with_change_password_if_take_over(data.get('changePasswordIfTakeOver'))\
            .with_different_user_id_for_login_and_data_retention(data.get('differentUserIdForLoginAndDataRetention'))\
            .with_create_account_script(ScriptSetting.from_dict(data.get('createAccountScript')))\
            .with_authentication_script(ScriptSetting.from_dict(data.get('authenticationScript')))\
            .with_create_take_over_script(ScriptSetting.from_dict(data.get('createTakeOverScript')))\
            .with_do_take_over_script(ScriptSetting.from_dict(data.get('doTakeOverScript')))\
            .with_ban_script(ScriptSetting.from_dict(data.get('banScript')))\
            .with_un_ban_script(ScriptSetting.from_dict(data.get('unBanScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "changePasswordIfTakeOver": self.change_password_if_take_over,
            "differentUserIdForLoginAndDataRetention": self.different_user_id_for_login_and_data_retention,
            "createAccountScript": self.create_account_script.to_dict() if self.create_account_script else None,
            "authenticationScript": self.authentication_script.to_dict() if self.authentication_script else None,
            "createTakeOverScript": self.create_take_over_script.to_dict() if self.create_take_over_script else None,
            "doTakeOverScript": self.do_take_over_script.to_dict() if self.do_take_over_script else None,
            "banScript": self.ban_script.to_dict() if self.ban_script else None,
            "unBanScript": self.un_ban_script.to_dict() if self.un_ban_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }