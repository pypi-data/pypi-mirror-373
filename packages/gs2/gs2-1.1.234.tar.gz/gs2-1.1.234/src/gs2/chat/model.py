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


class NotificationType(core.Gs2Model):
    category: int = None
    enable_transfer_mobile_push_notification: bool = None

    def with_category(self, category: int) -> NotificationType:
        self.category = category
        return self

    def with_enable_transfer_mobile_push_notification(self, enable_transfer_mobile_push_notification: bool) -> NotificationType:
        self.enable_transfer_mobile_push_notification = enable_transfer_mobile_push_notification
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
    ) -> Optional[NotificationType]:
        if data is None:
            return None
        return NotificationType()\
            .with_category(data.get('category'))\
            .with_enable_transfer_mobile_push_notification(data.get('enableTransferMobilePushNotification'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "enableTransferMobilePushNotification": self.enable_transfer_mobile_push_notification,
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
        return 'grn:gs2:{region}:{ownerId}:chat:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+)', grn)
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


class CategoryModelMaster(core.Gs2Model):
    category_model_id: str = None
    category: int = None
    description: str = None
    reject_access_token_post: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_category_model_id(self, category_model_id: str) -> CategoryModelMaster:
        self.category_model_id = category_model_id
        return self

    def with_category(self, category: int) -> CategoryModelMaster:
        self.category = category
        return self

    def with_description(self, description: str) -> CategoryModelMaster:
        self.description = description
        return self

    def with_reject_access_token_post(self, reject_access_token_post: str) -> CategoryModelMaster:
        self.reject_access_token_post = reject_access_token_post
        return self

    def with_created_at(self, created_at: int) -> CategoryModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> CategoryModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> CategoryModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        category,
    ):
        return 'grn:gs2:{region}:{ownerId}:chat:{namespaceName}:model:{category}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            category=category,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):model:(?P<category>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):model:(?P<category>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):model:(?P<category>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_category_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):model:(?P<category>.+)', grn)
        if match is None:
            return None
        return match.group('category')

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
    ) -> Optional[CategoryModelMaster]:
        if data is None:
            return None
        return CategoryModelMaster()\
            .with_category_model_id(data.get('categoryModelId'))\
            .with_category(data.get('category'))\
            .with_description(data.get('description'))\
            .with_reject_access_token_post(data.get('rejectAccessTokenPost'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoryModelId": self.category_model_id,
            "category": self.category,
            "description": self.description,
            "rejectAccessTokenPost": self.reject_access_token_post,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class CategoryModel(core.Gs2Model):
    category_model_id: str = None
    category: int = None
    reject_access_token_post: str = None

    def with_category_model_id(self, category_model_id: str) -> CategoryModel:
        self.category_model_id = category_model_id
        return self

    def with_category(self, category: int) -> CategoryModel:
        self.category = category
        return self

    def with_reject_access_token_post(self, reject_access_token_post: str) -> CategoryModel:
        self.reject_access_token_post = reject_access_token_post
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        category,
    ):
        return 'grn:gs2:{region}:{ownerId}:chat:{namespaceName}:model:{category}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            category=category,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):model:(?P<category>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):model:(?P<category>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):model:(?P<category>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_category_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):model:(?P<category>.+)', grn)
        if match is None:
            return None
        return match.group('category')

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
    ) -> Optional[CategoryModel]:
        if data is None:
            return None
        return CategoryModel()\
            .with_category_model_id(data.get('categoryModelId'))\
            .with_category(data.get('category'))\
            .with_reject_access_token_post(data.get('rejectAccessTokenPost'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "categoryModelId": self.category_model_id,
            "category": self.category,
            "rejectAccessTokenPost": self.reject_access_token_post,
        }


class Subscribe(core.Gs2Model):
    subscribe_id: str = None
    user_id: str = None
    room_name: str = None
    notification_types: List[NotificationType] = None
    created_at: int = None
    revision: int = None

    def with_subscribe_id(self, subscribe_id: str) -> Subscribe:
        self.subscribe_id = subscribe_id
        return self

    def with_user_id(self, user_id: str) -> Subscribe:
        self.user_id = user_id
        return self

    def with_room_name(self, room_name: str) -> Subscribe:
        self.room_name = room_name
        return self

    def with_notification_types(self, notification_types: List[NotificationType]) -> Subscribe:
        self.notification_types = notification_types
        return self

    def with_created_at(self, created_at: int) -> Subscribe:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Subscribe:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        room_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:chat:{namespaceName}:user:{userId}:subscribe:{roomName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            roomName=room_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_room_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('room_name')

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
    ) -> Optional[Subscribe]:
        if data is None:
            return None
        return Subscribe()\
            .with_subscribe_id(data.get('subscribeId'))\
            .with_user_id(data.get('userId'))\
            .with_room_name(data.get('roomName'))\
            .with_notification_types(None if data.get('notificationTypes') is None else [
                NotificationType.from_dict(data.get('notificationTypes')[i])
                for i in range(len(data.get('notificationTypes')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscribeId": self.subscribe_id,
            "userId": self.user_id,
            "roomName": self.room_name,
            "notificationTypes": None if self.notification_types is None else [
                self.notification_types[i].to_dict() if self.notification_types[i] else None
                for i in range(len(self.notification_types))
            ],
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Message(core.Gs2Model):
    message_id: str = None
    room_name: str = None
    name: str = None
    user_id: str = None
    category: int = None
    metadata: str = None
    created_at: int = None
    revision: int = None

    def with_message_id(self, message_id: str) -> Message:
        self.message_id = message_id
        return self

    def with_room_name(self, room_name: str) -> Message:
        self.room_name = room_name
        return self

    def with_name(self, name: str) -> Message:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> Message:
        self.user_id = user_id
        return self

    def with_category(self, category: int) -> Message:
        self.category = category
        return self

    def with_metadata(self, metadata: str) -> Message:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> Message:
        self.created_at = created_at
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
        room_name,
        message_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:chat:{namespaceName}:room:{roomName}:message:{messageName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            roomName=room_name,
            messageName=message_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_room_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+):message:(?P<messageName>.+)', grn)
        if match is None:
            return None
        return match.group('room_name')

    @classmethod
    def get_message_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+):message:(?P<messageName>.+)', grn)
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
            .with_room_name(data.get('roomName'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_category(data.get('category'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "messageId": self.message_id,
            "roomName": self.room_name,
            "name": self.name,
            "userId": self.user_id,
            "category": self.category,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Room(core.Gs2Model):
    room_id: str = None
    name: str = None
    user_id: str = None
    metadata: str = None
    password: str = None
    white_list_user_ids: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_room_id(self, room_id: str) -> Room:
        self.room_id = room_id
        return self

    def with_name(self, name: str) -> Room:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> Room:
        self.user_id = user_id
        return self

    def with_metadata(self, metadata: str) -> Room:
        self.metadata = metadata
        return self

    def with_password(self, password: str) -> Room:
        self.password = password
        return self

    def with_white_list_user_ids(self, white_list_user_ids: List[str]) -> Room:
        self.white_list_user_ids = white_list_user_ids
        return self

    def with_created_at(self, created_at: int) -> Room:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Room:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Room:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        room_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:chat:{namespaceName}:room:{roomName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            roomName=room_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_room_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+):room:(?P<roomName>.+)', grn)
        if match is None:
            return None
        return match.group('room_name')

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
    ) -> Optional[Room]:
        if data is None:
            return None
        return Room()\
            .with_room_id(data.get('roomId'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_metadata(data.get('metadata'))\
            .with_password(data.get('password'))\
            .with_white_list_user_ids(None if data.get('whiteListUserIds') is None else [
                data.get('whiteListUserIds')[i]
                for i in range(len(data.get('whiteListUserIds')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "roomId": self.room_id,
            "name": self.name,
            "userId": self.user_id,
            "metadata": self.metadata,
            "password": self.password,
            "whiteListUserIds": None if self.white_list_user_ids is None else [
                self.white_list_user_ids[i]
                for i in range(len(self.white_list_user_ids))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    allow_create_room: bool = None
    message_life_time_days: int = None
    post_message_script: ScriptSetting = None
    create_room_script: ScriptSetting = None
    delete_room_script: ScriptSetting = None
    subscribe_room_script: ScriptSetting = None
    unsubscribe_room_script: ScriptSetting = None
    post_notification: NotificationSetting = None
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

    def with_allow_create_room(self, allow_create_room: bool) -> Namespace:
        self.allow_create_room = allow_create_room
        return self

    def with_message_life_time_days(self, message_life_time_days: int) -> Namespace:
        self.message_life_time_days = message_life_time_days
        return self

    def with_post_message_script(self, post_message_script: ScriptSetting) -> Namespace:
        self.post_message_script = post_message_script
        return self

    def with_create_room_script(self, create_room_script: ScriptSetting) -> Namespace:
        self.create_room_script = create_room_script
        return self

    def with_delete_room_script(self, delete_room_script: ScriptSetting) -> Namespace:
        self.delete_room_script = delete_room_script
        return self

    def with_subscribe_room_script(self, subscribe_room_script: ScriptSetting) -> Namespace:
        self.subscribe_room_script = subscribe_room_script
        return self

    def with_unsubscribe_room_script(self, unsubscribe_room_script: ScriptSetting) -> Namespace:
        self.unsubscribe_room_script = unsubscribe_room_script
        return self

    def with_post_notification(self, post_notification: NotificationSetting) -> Namespace:
        self.post_notification = post_notification
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
        return 'grn:gs2:{region}:{ownerId}:chat:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):chat:(?P<namespaceName>.+)', grn)
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
            .with_allow_create_room(data.get('allowCreateRoom'))\
            .with_message_life_time_days(data.get('messageLifeTimeDays'))\
            .with_post_message_script(ScriptSetting.from_dict(data.get('postMessageScript')))\
            .with_create_room_script(ScriptSetting.from_dict(data.get('createRoomScript')))\
            .with_delete_room_script(ScriptSetting.from_dict(data.get('deleteRoomScript')))\
            .with_subscribe_room_script(ScriptSetting.from_dict(data.get('subscribeRoomScript')))\
            .with_unsubscribe_room_script(ScriptSetting.from_dict(data.get('unsubscribeRoomScript')))\
            .with_post_notification(NotificationSetting.from_dict(data.get('postNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "allowCreateRoom": self.allow_create_room,
            "messageLifeTimeDays": self.message_life_time_days,
            "postMessageScript": self.post_message_script.to_dict() if self.post_message_script else None,
            "createRoomScript": self.create_room_script.to_dict() if self.create_room_script else None,
            "deleteRoomScript": self.delete_room_script.to_dict() if self.delete_room_script else None,
            "subscribeRoomScript": self.subscribe_room_script.to_dict() if self.subscribe_room_script else None,
            "unsubscribeRoomScript": self.unsubscribe_room_script.to_dict() if self.unsubscribe_room_script else None,
            "postNotification": self.post_notification.to_dict() if self.post_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }