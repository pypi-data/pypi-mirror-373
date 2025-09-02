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


class NotificationSetting(core.Gs2Model):
    gateway_namespace_id: str = None
    enable_transfer_mobile_notification: bool = None
    sound: str = None

    def with_gateway_namespace_id(self, gateway_namespace_id: str) -> NotificationSetting:
        self.gateway_namespace_id = gateway_namespace_id
        return self

    def with_enable_transfer_mobile_notification(self, enable_transfer_mobile_notification: bool) -> NotificationSetting:
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        return self

    def with_sound(self, sound: str) -> NotificationSetting:
        self.sound = sound
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
    ) -> Optional[NotificationSetting]:
        if data is None:
            return None
        return NotificationSetting()\
            .with_gateway_namespace_id(data.get('gatewayNamespaceId'))\
            .with_enable_transfer_mobile_notification(data.get('enableTransferMobileNotification'))\
            .with_sound(data.get('sound'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gatewayNamespaceId": self.gateway_namespace_id,
            "enableTransferMobileNotification": self.enable_transfer_mobile_notification,
            "sound": self.sound,
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


class IgnoreUser(core.Gs2Model):
    user_id: str = None
    created_at: int = None

    def with_user_id(self, user_id: str) -> IgnoreUser:
        self.user_id = user_id
        return self

    def with_created_at(self, created_at: int) -> IgnoreUser:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        guild_model_name,
        guild_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:guild:{namespaceName}:guild:{guildModelName}:{guildName}:ignore:user'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            guildModelName=guild_model_name,
            guildName=guild_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):ignore:user', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):ignore:user', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):ignore:user', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_guild_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):ignore:user', grn)
        if match is None:
            return None
        return match.group('guild_model_name')

    @classmethod
    def get_guild_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):ignore:user', grn)
        if match is None:
            return None
        return match.group('guild_name')

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
    ) -> Optional[IgnoreUser]:
        if data is None:
            return None
        return IgnoreUser()\
            .with_user_id(data.get('userId'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "createdAt": self.created_at,
        }


class SendMemberRequest(core.Gs2Model):
    user_id: str = None
    target_guild_name: str = None
    metadata: str = None
    created_at: int = None

    def with_user_id(self, user_id: str) -> SendMemberRequest:
        self.user_id = user_id
        return self

    def with_target_guild_name(self, target_guild_name: str) -> SendMemberRequest:
        self.target_guild_name = target_guild_name
        return self

    def with_metadata(self, metadata: str) -> SendMemberRequest:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> SendMemberRequest:
        self.created_at = created_at
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
    ) -> Optional[SendMemberRequest]:
        if data is None:
            return None
        return SendMemberRequest()\
            .with_user_id(data.get('userId'))\
            .with_target_guild_name(data.get('targetGuildName'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "targetGuildName": self.target_guild_name,
            "metadata": self.metadata,
            "createdAt": self.created_at,
        }


class ReceiveMemberRequest(core.Gs2Model):
    user_id: str = None
    target_guild_name: str = None
    metadata: str = None
    created_at: int = None

    def with_user_id(self, user_id: str) -> ReceiveMemberRequest:
        self.user_id = user_id
        return self

    def with_target_guild_name(self, target_guild_name: str) -> ReceiveMemberRequest:
        self.target_guild_name = target_guild_name
        return self

    def with_metadata(self, metadata: str) -> ReceiveMemberRequest:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> ReceiveMemberRequest:
        self.created_at = created_at
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
    ) -> Optional[ReceiveMemberRequest]:
        if data is None:
            return None
        return ReceiveMemberRequest()\
            .with_user_id(data.get('userId'))\
            .with_target_guild_name(data.get('targetGuildName'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "targetGuildName": self.target_guild_name,
            "metadata": self.metadata,
            "createdAt": self.created_at,
        }


class Member(core.Gs2Model):
    user_id: str = None
    role_name: str = None
    metadata: str = None
    joined_at: int = None

    def with_user_id(self, user_id: str) -> Member:
        self.user_id = user_id
        return self

    def with_role_name(self, role_name: str) -> Member:
        self.role_name = role_name
        return self

    def with_metadata(self, metadata: str) -> Member:
        self.metadata = metadata
        return self

    def with_joined_at(self, joined_at: int) -> Member:
        self.joined_at = joined_at
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
    ) -> Optional[Member]:
        if data is None:
            return None
        return Member()\
            .with_user_id(data.get('userId'))\
            .with_role_name(data.get('roleName'))\
            .with_metadata(data.get('metadata'))\
            .with_joined_at(data.get('joinedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "roleName": self.role_name,
            "metadata": self.metadata,
            "joinedAt": self.joined_at,
        }


class RoleModel(core.Gs2Model):
    name: str = None
    metadata: str = None
    policy_document: str = None

    def with_name(self, name: str) -> RoleModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RoleModel:
        self.metadata = metadata
        return self

    def with_policy_document(self, policy_document: str) -> RoleModel:
        self.policy_document = policy_document
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
    ) -> Optional[RoleModel]:
        if data is None:
            return None
        return RoleModel()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_policy_document(data.get('policyDocument'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "policyDocument": self.policy_document,
        }


class CurrentGuildMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentGuildMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentGuildMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:guild:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentGuildMaster]:
        if data is None:
            return None
        return CurrentGuildMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class LastGuildMasterActivity(core.Gs2Model):
    user_id: str = None
    updated_at: int = None

    def with_user_id(self, user_id: str) -> LastGuildMasterActivity:
        self.user_id = user_id
        return self

    def with_updated_at(self, updated_at: int) -> LastGuildMasterActivity:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        guild_model_name,
        guild_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:guild:{namespaceName}:guild:{guildModelName}:{guildName}:lastActivity:master'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            guildModelName=guild_model_name,
            guildName=guild_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):lastActivity:master', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):lastActivity:master', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):lastActivity:master', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_guild_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):lastActivity:master', grn)
        if match is None:
            return None
        return match.group('guild_model_name')

    @classmethod
    def get_guild_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+):lastActivity:master', grn)
        if match is None:
            return None
        return match.group('guild_name')

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
    ) -> Optional[LastGuildMasterActivity]:
        if data is None:
            return None
        return LastGuildMasterActivity()\
            .with_user_id(data.get('userId'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "updatedAt": self.updated_at,
        }


class JoinedGuild(core.Gs2Model):
    joined_guild_id: str = None
    guild_model_name: str = None
    guild_name: str = None
    user_id: str = None
    created_at: int = None

    def with_joined_guild_id(self, joined_guild_id: str) -> JoinedGuild:
        self.joined_guild_id = joined_guild_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> JoinedGuild:
        self.guild_model_name = guild_model_name
        return self

    def with_guild_name(self, guild_name: str) -> JoinedGuild:
        self.guild_name = guild_name
        return self

    def with_user_id(self, user_id: str) -> JoinedGuild:
        self.user_id = user_id
        return self

    def with_created_at(self, created_at: int) -> JoinedGuild:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        guild_model_name,
        guild_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:guild:{namespaceName}:user:{userId}:guild:{guildModelName}:{guildName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            guildModelName=guild_model_name,
            guildName=guild_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):user:(?P<userId>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):user:(?P<userId>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):user:(?P<userId>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):user:(?P<userId>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_guild_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):user:(?P<userId>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('guild_model_name')

    @classmethod
    def get_guild_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):user:(?P<userId>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('guild_name')

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
    ) -> Optional[JoinedGuild]:
        if data is None:
            return None
        return JoinedGuild()\
            .with_joined_guild_id(data.get('joinedGuildId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_guild_name(data.get('guildName'))\
            .with_user_id(data.get('userId'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "joinedGuildId": self.joined_guild_id,
            "guildModelName": self.guild_model_name,
            "guildName": self.guild_name,
            "userId": self.user_id,
            "createdAt": self.created_at,
        }


class Guild(core.Gs2Model):
    guild_id: str = None
    guild_model_name: str = None
    name: str = None
    display_name: str = None
    attribute1: int = None
    attribute2: int = None
    attribute3: int = None
    attribute4: int = None
    attribute5: int = None
    metadata: str = None
    join_policy: str = None
    custom_roles: List[RoleModel] = None
    guild_member_default_role: str = None
    current_maximum_member_count: int = None
    members: List[Member] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_guild_id(self, guild_id: str) -> Guild:
        self.guild_id = guild_id
        return self

    def with_guild_model_name(self, guild_model_name: str) -> Guild:
        self.guild_model_name = guild_model_name
        return self

    def with_name(self, name: str) -> Guild:
        self.name = name
        return self

    def with_display_name(self, display_name: str) -> Guild:
        self.display_name = display_name
        return self

    def with_attribute1(self, attribute1: int) -> Guild:
        self.attribute1 = attribute1
        return self

    def with_attribute2(self, attribute2: int) -> Guild:
        self.attribute2 = attribute2
        return self

    def with_attribute3(self, attribute3: int) -> Guild:
        self.attribute3 = attribute3
        return self

    def with_attribute4(self, attribute4: int) -> Guild:
        self.attribute4 = attribute4
        return self

    def with_attribute5(self, attribute5: int) -> Guild:
        self.attribute5 = attribute5
        return self

    def with_metadata(self, metadata: str) -> Guild:
        self.metadata = metadata
        return self

    def with_join_policy(self, join_policy: str) -> Guild:
        self.join_policy = join_policy
        return self

    def with_custom_roles(self, custom_roles: List[RoleModel]) -> Guild:
        self.custom_roles = custom_roles
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> Guild:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_current_maximum_member_count(self, current_maximum_member_count: int) -> Guild:
        self.current_maximum_member_count = current_maximum_member_count
        return self

    def with_members(self, members: List[Member]) -> Guild:
        self.members = members
        return self

    def with_created_at(self, created_at: int) -> Guild:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Guild:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Guild:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        guild_model_name,
        guild_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:guild:{namespaceName}:guild:{guildModelName}:{guildName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            guildModelName=guild_model_name,
            guildName=guild_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_guild_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('guild_model_name')

    @classmethod
    def get_guild_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):guild:(?P<guildModelName>.+):(?P<guildName>.+)', grn)
        if match is None:
            return None
        return match.group('guild_name')

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
    ) -> Optional[Guild]:
        if data is None:
            return None
        return Guild()\
            .with_guild_id(data.get('guildId'))\
            .with_guild_model_name(data.get('guildModelName'))\
            .with_name(data.get('name'))\
            .with_display_name(data.get('displayName'))\
            .with_attribute1(data.get('attribute1'))\
            .with_attribute2(data.get('attribute2'))\
            .with_attribute3(data.get('attribute3'))\
            .with_attribute4(data.get('attribute4'))\
            .with_attribute5(data.get('attribute5'))\
            .with_metadata(data.get('metadata'))\
            .with_join_policy(data.get('joinPolicy'))\
            .with_custom_roles(None if data.get('customRoles') is None else [
                RoleModel.from_dict(data.get('customRoles')[i])
                for i in range(len(data.get('customRoles')))
            ])\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))\
            .with_current_maximum_member_count(data.get('currentMaximumMemberCount'))\
            .with_members(None if data.get('members') is None else [
                Member.from_dict(data.get('members')[i])
                for i in range(len(data.get('members')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "guildId": self.guild_id,
            "guildModelName": self.guild_model_name,
            "name": self.name,
            "displayName": self.display_name,
            "attribute1": self.attribute1,
            "attribute2": self.attribute2,
            "attribute3": self.attribute3,
            "attribute4": self.attribute4,
            "attribute5": self.attribute5,
            "metadata": self.metadata,
            "joinPolicy": self.join_policy,
            "customRoles": None if self.custom_roles is None else [
                self.custom_roles[i].to_dict() if self.custom_roles[i] else None
                for i in range(len(self.custom_roles))
            ],
            "guildMemberDefaultRole": self.guild_member_default_role,
            "currentMaximumMemberCount": self.current_maximum_member_count,
            "members": None if self.members is None else [
                self.members[i].to_dict() if self.members[i] else None
                for i in range(len(self.members))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class GuildModel(core.Gs2Model):
    guild_model_id: str = None
    name: str = None
    metadata: str = None
    default_maximum_member_count: int = None
    maximum_member_count: int = None
    inactivity_period_days: int = None
    roles: List[RoleModel] = None
    guild_master_role: str = None
    guild_member_default_role: str = None
    rejoin_cool_time_minutes: int = None
    max_concurrent_join_guilds: int = None
    max_concurrent_guild_master_count: int = None

    def with_guild_model_id(self, guild_model_id: str) -> GuildModel:
        self.guild_model_id = guild_model_id
        return self

    def with_name(self, name: str) -> GuildModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> GuildModel:
        self.metadata = metadata
        return self

    def with_default_maximum_member_count(self, default_maximum_member_count: int) -> GuildModel:
        self.default_maximum_member_count = default_maximum_member_count
        return self

    def with_maximum_member_count(self, maximum_member_count: int) -> GuildModel:
        self.maximum_member_count = maximum_member_count
        return self

    def with_inactivity_period_days(self, inactivity_period_days: int) -> GuildModel:
        self.inactivity_period_days = inactivity_period_days
        return self

    def with_roles(self, roles: List[RoleModel]) -> GuildModel:
        self.roles = roles
        return self

    def with_guild_master_role(self, guild_master_role: str) -> GuildModel:
        self.guild_master_role = guild_master_role
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> GuildModel:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_rejoin_cool_time_minutes(self, rejoin_cool_time_minutes: int) -> GuildModel:
        self.rejoin_cool_time_minutes = rejoin_cool_time_minutes
        return self

    def with_max_concurrent_join_guilds(self, max_concurrent_join_guilds: int) -> GuildModel:
        self.max_concurrent_join_guilds = max_concurrent_join_guilds
        return self

    def with_max_concurrent_guild_master_count(self, max_concurrent_guild_master_count: int) -> GuildModel:
        self.max_concurrent_guild_master_count = max_concurrent_guild_master_count
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        guild_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:guild:{namespaceName}:model:{guildModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            guildModelName=guild_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):model:(?P<guildModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):model:(?P<guildModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):model:(?P<guildModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_guild_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):model:(?P<guildModelName>.+)', grn)
        if match is None:
            return None
        return match.group('guild_model_name')

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
    ) -> Optional[GuildModel]:
        if data is None:
            return None
        return GuildModel()\
            .with_guild_model_id(data.get('guildModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_default_maximum_member_count(data.get('defaultMaximumMemberCount'))\
            .with_maximum_member_count(data.get('maximumMemberCount'))\
            .with_inactivity_period_days(data.get('inactivityPeriodDays'))\
            .with_roles(None if data.get('roles') is None else [
                RoleModel.from_dict(data.get('roles')[i])
                for i in range(len(data.get('roles')))
            ])\
            .with_guild_master_role(data.get('guildMasterRole'))\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))\
            .with_rejoin_cool_time_minutes(data.get('rejoinCoolTimeMinutes'))\
            .with_max_concurrent_join_guilds(data.get('maxConcurrentJoinGuilds'))\
            .with_max_concurrent_guild_master_count(data.get('maxConcurrentGuildMasterCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "guildModelId": self.guild_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "defaultMaximumMemberCount": self.default_maximum_member_count,
            "maximumMemberCount": self.maximum_member_count,
            "inactivityPeriodDays": self.inactivity_period_days,
            "roles": None if self.roles is None else [
                self.roles[i].to_dict() if self.roles[i] else None
                for i in range(len(self.roles))
            ],
            "guildMasterRole": self.guild_master_role,
            "guildMemberDefaultRole": self.guild_member_default_role,
            "rejoinCoolTimeMinutes": self.rejoin_cool_time_minutes,
            "maxConcurrentJoinGuilds": self.max_concurrent_join_guilds,
            "maxConcurrentGuildMasterCount": self.max_concurrent_guild_master_count,
        }


class GuildModelMaster(core.Gs2Model):
    guild_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    default_maximum_member_count: int = None
    maximum_member_count: int = None
    inactivity_period_days: int = None
    roles: List[RoleModel] = None
    guild_master_role: str = None
    guild_member_default_role: str = None
    rejoin_cool_time_minutes: int = None
    max_concurrent_join_guilds: int = None
    max_concurrent_guild_master_count: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_guild_model_id(self, guild_model_id: str) -> GuildModelMaster:
        self.guild_model_id = guild_model_id
        return self

    def with_name(self, name: str) -> GuildModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> GuildModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> GuildModelMaster:
        self.metadata = metadata
        return self

    def with_default_maximum_member_count(self, default_maximum_member_count: int) -> GuildModelMaster:
        self.default_maximum_member_count = default_maximum_member_count
        return self

    def with_maximum_member_count(self, maximum_member_count: int) -> GuildModelMaster:
        self.maximum_member_count = maximum_member_count
        return self

    def with_inactivity_period_days(self, inactivity_period_days: int) -> GuildModelMaster:
        self.inactivity_period_days = inactivity_period_days
        return self

    def with_roles(self, roles: List[RoleModel]) -> GuildModelMaster:
        self.roles = roles
        return self

    def with_guild_master_role(self, guild_master_role: str) -> GuildModelMaster:
        self.guild_master_role = guild_master_role
        return self

    def with_guild_member_default_role(self, guild_member_default_role: str) -> GuildModelMaster:
        self.guild_member_default_role = guild_member_default_role
        return self

    def with_rejoin_cool_time_minutes(self, rejoin_cool_time_minutes: int) -> GuildModelMaster:
        self.rejoin_cool_time_minutes = rejoin_cool_time_minutes
        return self

    def with_max_concurrent_join_guilds(self, max_concurrent_join_guilds: int) -> GuildModelMaster:
        self.max_concurrent_join_guilds = max_concurrent_join_guilds
        return self

    def with_max_concurrent_guild_master_count(self, max_concurrent_guild_master_count: int) -> GuildModelMaster:
        self.max_concurrent_guild_master_count = max_concurrent_guild_master_count
        return self

    def with_created_at(self, created_at: int) -> GuildModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> GuildModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> GuildModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        guild_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:guild:{namespaceName}:model:{guildModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            guildModelName=guild_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):model:(?P<guildModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):model:(?P<guildModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):model:(?P<guildModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_guild_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+):model:(?P<guildModelName>.+)', grn)
        if match is None:
            return None
        return match.group('guild_model_name')

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
    ) -> Optional[GuildModelMaster]:
        if data is None:
            return None
        return GuildModelMaster()\
            .with_guild_model_id(data.get('guildModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_maximum_member_count(data.get('defaultMaximumMemberCount'))\
            .with_maximum_member_count(data.get('maximumMemberCount'))\
            .with_inactivity_period_days(data.get('inactivityPeriodDays'))\
            .with_roles(None if data.get('roles') is None else [
                RoleModel.from_dict(data.get('roles')[i])
                for i in range(len(data.get('roles')))
            ])\
            .with_guild_master_role(data.get('guildMasterRole'))\
            .with_guild_member_default_role(data.get('guildMemberDefaultRole'))\
            .with_rejoin_cool_time_minutes(data.get('rejoinCoolTimeMinutes'))\
            .with_max_concurrent_join_guilds(data.get('maxConcurrentJoinGuilds'))\
            .with_max_concurrent_guild_master_count(data.get('maxConcurrentGuildMasterCount'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "guildModelId": self.guild_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultMaximumMemberCount": self.default_maximum_member_count,
            "maximumMemberCount": self.maximum_member_count,
            "inactivityPeriodDays": self.inactivity_period_days,
            "roles": None if self.roles is None else [
                self.roles[i].to_dict() if self.roles[i] else None
                for i in range(len(self.roles))
            ],
            "guildMasterRole": self.guild_master_role,
            "guildMemberDefaultRole": self.guild_member_default_role,
            "rejoinCoolTimeMinutes": self.rejoin_cool_time_minutes,
            "maxConcurrentJoinGuilds": self.max_concurrent_join_guilds,
            "maxConcurrentGuildMasterCount": self.max_concurrent_guild_master_count,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    change_notification: NotificationSetting = None
    join_notification: NotificationSetting = None
    leave_notification: NotificationSetting = None
    change_member_notification: NotificationSetting = None
    receive_request_notification: NotificationSetting = None
    remove_request_notification: NotificationSetting = None
    create_guild_script: ScriptSetting = None
    update_guild_script: ScriptSetting = None
    join_guild_script: ScriptSetting = None
    receive_join_request_script: ScriptSetting = None
    leave_guild_script: ScriptSetting = None
    change_role_script: ScriptSetting = None
    delete_guild_script: ScriptSetting = None
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

    def with_change_notification(self, change_notification: NotificationSetting) -> Namespace:
        self.change_notification = change_notification
        return self

    def with_join_notification(self, join_notification: NotificationSetting) -> Namespace:
        self.join_notification = join_notification
        return self

    def with_leave_notification(self, leave_notification: NotificationSetting) -> Namespace:
        self.leave_notification = leave_notification
        return self

    def with_change_member_notification(self, change_member_notification: NotificationSetting) -> Namespace:
        self.change_member_notification = change_member_notification
        return self

    def with_receive_request_notification(self, receive_request_notification: NotificationSetting) -> Namespace:
        self.receive_request_notification = receive_request_notification
        return self

    def with_remove_request_notification(self, remove_request_notification: NotificationSetting) -> Namespace:
        self.remove_request_notification = remove_request_notification
        return self

    def with_create_guild_script(self, create_guild_script: ScriptSetting) -> Namespace:
        self.create_guild_script = create_guild_script
        return self

    def with_update_guild_script(self, update_guild_script: ScriptSetting) -> Namespace:
        self.update_guild_script = update_guild_script
        return self

    def with_join_guild_script(self, join_guild_script: ScriptSetting) -> Namespace:
        self.join_guild_script = join_guild_script
        return self

    def with_receive_join_request_script(self, receive_join_request_script: ScriptSetting) -> Namespace:
        self.receive_join_request_script = receive_join_request_script
        return self

    def with_leave_guild_script(self, leave_guild_script: ScriptSetting) -> Namespace:
        self.leave_guild_script = leave_guild_script
        return self

    def with_change_role_script(self, change_role_script: ScriptSetting) -> Namespace:
        self.change_role_script = change_role_script
        return self

    def with_delete_guild_script(self, delete_guild_script: ScriptSetting) -> Namespace:
        self.delete_guild_script = delete_guild_script
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
        return 'grn:gs2:{region}:{ownerId}:guild:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guild:(?P<namespaceName>.+)', grn)
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
            .with_change_notification(NotificationSetting.from_dict(data.get('changeNotification')))\
            .with_join_notification(NotificationSetting.from_dict(data.get('joinNotification')))\
            .with_leave_notification(NotificationSetting.from_dict(data.get('leaveNotification')))\
            .with_change_member_notification(NotificationSetting.from_dict(data.get('changeMemberNotification')))\
            .with_receive_request_notification(NotificationSetting.from_dict(data.get('receiveRequestNotification')))\
            .with_remove_request_notification(NotificationSetting.from_dict(data.get('removeRequestNotification')))\
            .with_create_guild_script(ScriptSetting.from_dict(data.get('createGuildScript')))\
            .with_update_guild_script(ScriptSetting.from_dict(data.get('updateGuildScript')))\
            .with_join_guild_script(ScriptSetting.from_dict(data.get('joinGuildScript')))\
            .with_receive_join_request_script(ScriptSetting.from_dict(data.get('receiveJoinRequestScript')))\
            .with_leave_guild_script(ScriptSetting.from_dict(data.get('leaveGuildScript')))\
            .with_change_role_script(ScriptSetting.from_dict(data.get('changeRoleScript')))\
            .with_delete_guild_script(ScriptSetting.from_dict(data.get('deleteGuildScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "changeNotification": self.change_notification.to_dict() if self.change_notification else None,
            "joinNotification": self.join_notification.to_dict() if self.join_notification else None,
            "leaveNotification": self.leave_notification.to_dict() if self.leave_notification else None,
            "changeMemberNotification": self.change_member_notification.to_dict() if self.change_member_notification else None,
            "receiveRequestNotification": self.receive_request_notification.to_dict() if self.receive_request_notification else None,
            "removeRequestNotification": self.remove_request_notification.to_dict() if self.remove_request_notification else None,
            "createGuildScript": self.create_guild_script.to_dict() if self.create_guild_script else None,
            "updateGuildScript": self.update_guild_script.to_dict() if self.update_guild_script else None,
            "joinGuildScript": self.join_guild_script.to_dict() if self.join_guild_script else None,
            "receiveJoinRequestScript": self.receive_join_request_script.to_dict() if self.receive_join_request_script else None,
            "leaveGuildScript": self.leave_guild_script.to_dict() if self.leave_guild_script else None,
            "changeRoleScript": self.change_role_script.to_dict() if self.change_role_script else None,
            "deleteGuildScript": self.delete_guild_script.to_dict() if self.delete_guild_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }