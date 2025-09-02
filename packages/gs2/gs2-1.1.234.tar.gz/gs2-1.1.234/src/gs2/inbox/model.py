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


class TimeSpan(core.Gs2Model):
    days: int = None
    hours: int = None
    minutes: int = None

    def with_days(self, days: int) -> TimeSpan:
        self.days = days
        return self

    def with_hours(self, hours: int) -> TimeSpan:
        self.hours = hours
        return self

    def with_minutes(self, minutes: int) -> TimeSpan:
        self.minutes = minutes
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
    ) -> Optional[TimeSpan]:
        if data is None:
            return None
        return TimeSpan()\
            .with_days(data.get('days'))\
            .with_hours(data.get('hours'))\
            .with_minutes(data.get('minutes'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "days": self.days,
            "hours": self.hours,
            "minutes": self.minutes,
        }


class Received(core.Gs2Model):
    received_id: str = None
    user_id: str = None
    received_global_message_names: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_received_id(self, received_id: str) -> Received:
        self.received_id = received_id
        return self

    def with_user_id(self, user_id: str) -> Received:
        self.user_id = user_id
        return self

    def with_received_global_message_names(self, received_global_message_names: List[str]) -> Received:
        self.received_global_message_names = received_global_message_names
        return self

    def with_created_at(self, created_at: int) -> Received:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Received:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Received:
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
        return 'grn:gs2:{region}:{ownerId}:inbox:{namespaceName}:user:{userId}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
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
    ) -> Optional[Received]:
        if data is None:
            return None
        return Received()\
            .with_received_id(data.get('receivedId'))\
            .with_user_id(data.get('userId'))\
            .with_received_global_message_names(None if data.get('receivedGlobalMessageNames') is None else [
                data.get('receivedGlobalMessageNames')[i]
                for i in range(len(data.get('receivedGlobalMessageNames')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receivedId": self.received_id,
            "userId": self.user_id,
            "receivedGlobalMessageNames": None if self.received_global_message_names is None else [
                self.received_global_message_names[i]
                for i in range(len(self.received_global_message_names))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class GlobalMessage(core.Gs2Model):
    global_message_id: str = None
    name: str = None
    metadata: str = None
    read_acquire_actions: List[AcquireAction] = None
    expires_time_span: TimeSpan = None
    expires_at: int = None
    message_reception_period_event_id: str = None

    def with_global_message_id(self, global_message_id: str) -> GlobalMessage:
        self.global_message_id = global_message_id
        return self

    def with_name(self, name: str) -> GlobalMessage:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> GlobalMessage:
        self.metadata = metadata
        return self

    def with_read_acquire_actions(self, read_acquire_actions: List[AcquireAction]) -> GlobalMessage:
        self.read_acquire_actions = read_acquire_actions
        return self

    def with_expires_time_span(self, expires_time_span: TimeSpan) -> GlobalMessage:
        self.expires_time_span = expires_time_span
        return self

    def with_expires_at(self, expires_at: int) -> GlobalMessage:
        self.expires_at = expires_at
        return self

    def with_message_reception_period_event_id(self, message_reception_period_event_id: str) -> GlobalMessage:
        self.message_reception_period_event_id = message_reception_period_event_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        global_message_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inbox:{namespaceName}:globalMessage:{globalMessageName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            globalMessageName=global_message_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):globalMessage:(?P<globalMessageName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):globalMessage:(?P<globalMessageName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):globalMessage:(?P<globalMessageName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_global_message_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):globalMessage:(?P<globalMessageName>.+)', grn)
        if match is None:
            return None
        return match.group('global_message_name')

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
    ) -> Optional[GlobalMessage]:
        if data is None:
            return None
        return GlobalMessage()\
            .with_global_message_id(data.get('globalMessageId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_read_acquire_actions(None if data.get('readAcquireActions') is None else [
                AcquireAction.from_dict(data.get('readAcquireActions')[i])
                for i in range(len(data.get('readAcquireActions')))
            ])\
            .with_expires_time_span(TimeSpan.from_dict(data.get('expiresTimeSpan')))\
            .with_expires_at(data.get('expiresAt'))\
            .with_message_reception_period_event_id(data.get('messageReceptionPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "globalMessageId": self.global_message_id,
            "name": self.name,
            "metadata": self.metadata,
            "readAcquireActions": None if self.read_acquire_actions is None else [
                self.read_acquire_actions[i].to_dict() if self.read_acquire_actions[i] else None
                for i in range(len(self.read_acquire_actions))
            ],
            "expiresTimeSpan": self.expires_time_span.to_dict() if self.expires_time_span else None,
            "expiresAt": self.expires_at,
            "messageReceptionPeriodEventId": self.message_reception_period_event_id,
        }


class GlobalMessageMaster(core.Gs2Model):
    global_message_id: str = None
    name: str = None
    metadata: str = None
    read_acquire_actions: List[AcquireAction] = None
    expires_time_span: TimeSpan = None
    expires_at: int = None
    message_reception_period_event_id: str = None
    created_at: int = None
    revision: int = None

    def with_global_message_id(self, global_message_id: str) -> GlobalMessageMaster:
        self.global_message_id = global_message_id
        return self

    def with_name(self, name: str) -> GlobalMessageMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> GlobalMessageMaster:
        self.metadata = metadata
        return self

    def with_read_acquire_actions(self, read_acquire_actions: List[AcquireAction]) -> GlobalMessageMaster:
        self.read_acquire_actions = read_acquire_actions
        return self

    def with_expires_time_span(self, expires_time_span: TimeSpan) -> GlobalMessageMaster:
        self.expires_time_span = expires_time_span
        return self

    def with_expires_at(self, expires_at: int) -> GlobalMessageMaster:
        self.expires_at = expires_at
        return self

    def with_message_reception_period_event_id(self, message_reception_period_event_id: str) -> GlobalMessageMaster:
        self.message_reception_period_event_id = message_reception_period_event_id
        return self

    def with_created_at(self, created_at: int) -> GlobalMessageMaster:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> GlobalMessageMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        global_message_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inbox:{namespaceName}:master:globalMessage:{globalMessageName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            globalMessageName=global_message_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):master:globalMessage:(?P<globalMessageName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):master:globalMessage:(?P<globalMessageName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):master:globalMessage:(?P<globalMessageName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_global_message_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):master:globalMessage:(?P<globalMessageName>.+)', grn)
        if match is None:
            return None
        return match.group('global_message_name')

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
    ) -> Optional[GlobalMessageMaster]:
        if data is None:
            return None
        return GlobalMessageMaster()\
            .with_global_message_id(data.get('globalMessageId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_read_acquire_actions(None if data.get('readAcquireActions') is None else [
                AcquireAction.from_dict(data.get('readAcquireActions')[i])
                for i in range(len(data.get('readAcquireActions')))
            ])\
            .with_expires_time_span(TimeSpan.from_dict(data.get('expiresTimeSpan')))\
            .with_expires_at(data.get('expiresAt'))\
            .with_message_reception_period_event_id(data.get('messageReceptionPeriodEventId'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "globalMessageId": self.global_message_id,
            "name": self.name,
            "metadata": self.metadata,
            "readAcquireActions": None if self.read_acquire_actions is None else [
                self.read_acquire_actions[i].to_dict() if self.read_acquire_actions[i] else None
                for i in range(len(self.read_acquire_actions))
            ],
            "expiresTimeSpan": self.expires_time_span.to_dict() if self.expires_time_span else None,
            "expiresAt": self.expires_at,
            "messageReceptionPeriodEventId": self.message_reception_period_event_id,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class CurrentMessageMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentMessageMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentMessageMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inbox:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentMessageMaster]:
        if data is None:
            return None
        return CurrentMessageMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class Message(core.Gs2Model):
    message_id: str = None
    name: str = None
    user_id: str = None
    metadata: str = None
    is_read: bool = None
    read_acquire_actions: List[AcquireAction] = None
    received_at: int = None
    read_at: int = None
    expires_at: int = None
    revision: int = None

    def with_message_id(self, message_id: str) -> Message:
        self.message_id = message_id
        return self

    def with_name(self, name: str) -> Message:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> Message:
        self.user_id = user_id
        return self

    def with_metadata(self, metadata: str) -> Message:
        self.metadata = metadata
        return self

    def with_is_read(self, is_read: bool) -> Message:
        self.is_read = is_read
        return self

    def with_read_acquire_actions(self, read_acquire_actions: List[AcquireAction]) -> Message:
        self.read_acquire_actions = read_acquire_actions
        return self

    def with_received_at(self, received_at: int) -> Message:
        self.received_at = received_at
        return self

    def with_read_at(self, read_at: int) -> Message:
        self.read_at = read_at
        return self

    def with_expires_at(self, expires_at: int) -> Message:
        self.expires_at = expires_at
        return self

    def with_revision(self, revision: int) -> Message:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        message_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inbox:{namespaceName}:user:{userId}:message:{messageName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            messageName=message_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_message_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+):user:(?P<userId>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('message_name')

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
    ) -> Optional[Message]:
        if data is None:
            return None
        return Message()\
            .with_message_id(data.get('messageId'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_metadata(data.get('metadata'))\
            .with_is_read(data.get('isRead'))\
            .with_read_acquire_actions(None if data.get('readAcquireActions') is None else [
                AcquireAction.from_dict(data.get('readAcquireActions')[i])
                for i in range(len(data.get('readAcquireActions')))
            ])\
            .with_received_at(data.get('receivedAt'))\
            .with_read_at(data.get('readAt'))\
            .with_expires_at(data.get('expiresAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "messageId": self.message_id,
            "name": self.name,
            "userId": self.user_id,
            "metadata": self.metadata,
            "isRead": self.is_read,
            "readAcquireActions": None if self.read_acquire_actions is None else [
                self.read_acquire_actions[i].to_dict() if self.read_acquire_actions[i] else None
                for i in range(len(self.read_acquire_actions))
            ],
            "receivedAt": self.received_at,
            "readAt": self.read_at,
            "expiresAt": self.expires_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    is_automatic_deleting_enabled: bool = None
    transaction_setting: TransactionSetting = None
    receive_message_script: ScriptSetting = None
    read_message_script: ScriptSetting = None
    delete_message_script: ScriptSetting = None
    receive_notification: NotificationSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
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

    def with_is_automatic_deleting_enabled(self, is_automatic_deleting_enabled: bool) -> Namespace:
        self.is_automatic_deleting_enabled = is_automatic_deleting_enabled
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
        return self

    def with_receive_message_script(self, receive_message_script: ScriptSetting) -> Namespace:
        self.receive_message_script = receive_message_script
        return self

    def with_read_message_script(self, read_message_script: ScriptSetting) -> Namespace:
        self.read_message_script = read_message_script
        return self

    def with_delete_message_script(self, delete_message_script: ScriptSetting) -> Namespace:
        self.delete_message_script = delete_message_script
        return self

    def with_receive_notification(self, receive_notification: NotificationSetting) -> Namespace:
        self.receive_notification = receive_notification
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
        return 'grn:gs2:{region}:{ownerId}:inbox:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inbox:(?P<namespaceName>.+)', grn)
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
            .with_is_automatic_deleting_enabled(data.get('isAutomaticDeletingEnabled'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_receive_message_script(ScriptSetting.from_dict(data.get('receiveMessageScript')))\
            .with_read_message_script(ScriptSetting.from_dict(data.get('readMessageScript')))\
            .with_delete_message_script(ScriptSetting.from_dict(data.get('deleteMessageScript')))\
            .with_receive_notification(NotificationSetting.from_dict(data.get('receiveNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "isAutomaticDeletingEnabled": self.is_automatic_deleting_enabled,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "receiveMessageScript": self.receive_message_script.to_dict() if self.receive_message_script else None,
            "readMessageScript": self.read_message_script.to_dict() if self.read_message_script else None,
            "deleteMessageScript": self.delete_message_script.to_dict() if self.delete_message_script else None,
            "receiveNotification": self.receive_notification.to_dict() if self.receive_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
            "revision": self.revision,
        }