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


class PublicProfile(core.Gs2Model):
    user_id: str = None
    public_profile: str = None

    def with_user_id(self, user_id: str) -> PublicProfile:
        self.user_id = user_id
        return self

    def with_public_profile(self, public_profile: str) -> PublicProfile:
        self.public_profile = public_profile
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
    ) -> Optional[PublicProfile]:
        if data is None:
            return None
        return PublicProfile()\
            .with_user_id(data.get('userId'))\
            .with_public_profile(data.get('publicProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "publicProfile": self.public_profile,
        }


class ReceiveFriendRequest(core.Gs2Model):
    user_id: str = None
    target_user_id: str = None
    public_profile: str = None

    def with_user_id(self, user_id: str) -> ReceiveFriendRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> ReceiveFriendRequest:
        self.target_user_id = target_user_id
        return self

    def with_public_profile(self, public_profile: str) -> ReceiveFriendRequest:
        self.public_profile = public_profile
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
    ) -> Optional[ReceiveFriendRequest]:
        if data is None:
            return None
        return ReceiveFriendRequest()\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_public_profile(data.get('publicProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "publicProfile": self.public_profile,
        }


class SendFriendRequest(core.Gs2Model):
    user_id: str = None
    target_user_id: str = None
    public_profile: str = None

    def with_user_id(self, user_id: str) -> SendFriendRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> SendFriendRequest:
        self.target_user_id = target_user_id
        return self

    def with_public_profile(self, public_profile: str) -> SendFriendRequest:
        self.public_profile = public_profile
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
    ) -> Optional[SendFriendRequest]:
        if data is None:
            return None
        return SendFriendRequest()\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_public_profile(data.get('publicProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "publicProfile": self.public_profile,
        }


class FriendRequest(core.Gs2Model):
    user_id: str = None
    target_user_id: str = None
    public_profile: str = None

    def with_user_id(self, user_id: str) -> FriendRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> FriendRequest:
        self.target_user_id = target_user_id
        return self

    def with_public_profile(self, public_profile: str) -> FriendRequest:
        self.public_profile = public_profile
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
    ) -> Optional[FriendRequest]:
        if data is None:
            return None
        return FriendRequest()\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_public_profile(data.get('publicProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "publicProfile": self.public_profile,
        }


class FriendUser(core.Gs2Model):
    user_id: str = None
    public_profile: str = None
    friend_profile: str = None

    def with_user_id(self, user_id: str) -> FriendUser:
        self.user_id = user_id
        return self

    def with_public_profile(self, public_profile: str) -> FriendUser:
        self.public_profile = public_profile
        return self

    def with_friend_profile(self, friend_profile: str) -> FriendUser:
        self.friend_profile = friend_profile
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
    ) -> Optional[FriendUser]:
        if data is None:
            return None
        return FriendUser()\
            .with_user_id(data.get('userId'))\
            .with_public_profile(data.get('publicProfile'))\
            .with_friend_profile(data.get('friendProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "publicProfile": self.public_profile,
            "friendProfile": self.friend_profile,
        }


class FollowUser(core.Gs2Model):
    user_id: str = None
    public_profile: str = None
    follower_profile: str = None

    def with_user_id(self, user_id: str) -> FollowUser:
        self.user_id = user_id
        return self

    def with_public_profile(self, public_profile: str) -> FollowUser:
        self.public_profile = public_profile
        return self

    def with_follower_profile(self, follower_profile: str) -> FollowUser:
        self.follower_profile = follower_profile
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
    ) -> Optional[FollowUser]:
        if data is None:
            return None
        return FollowUser()\
            .with_user_id(data.get('userId'))\
            .with_public_profile(data.get('publicProfile'))\
            .with_follower_profile(data.get('followerProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "publicProfile": self.public_profile,
            "followerProfile": self.follower_profile,
        }


class BlackList(core.Gs2Model):
    black_list_id: str = None
    user_id: str = None
    target_user_ids: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_black_list_id(self, black_list_id: str) -> BlackList:
        self.black_list_id = black_list_id
        return self

    def with_user_id(self, user_id: str) -> BlackList:
        self.user_id = user_id
        return self

    def with_target_user_ids(self, target_user_ids: List[str]) -> BlackList:
        self.target_user_ids = target_user_ids
        return self

    def with_created_at(self, created_at: int) -> BlackList:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BlackList:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> BlackList:
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
        return 'grn:gs2:{region}:{ownerId}:friend:{namespaceName}:user:{userId}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
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
    ) -> Optional[BlackList]:
        if data is None:
            return None
        return BlackList()\
            .with_black_list_id(data.get('blackListId'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_ids(None if data.get('targetUserIds') is None else [
                data.get('targetUserIds')[i]
                for i in range(len(data.get('targetUserIds')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blackListId": self.black_list_id,
            "userId": self.user_id,
            "targetUserIds": None if self.target_user_ids is None else [
                self.target_user_ids[i]
                for i in range(len(self.target_user_ids))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Inbox(core.Gs2Model):
    inbox_id: str = None
    user_id: str = None
    from_user_ids: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_inbox_id(self, inbox_id: str) -> Inbox:
        self.inbox_id = inbox_id
        return self

    def with_user_id(self, user_id: str) -> Inbox:
        self.user_id = user_id
        return self

    def with_from_user_ids(self, from_user_ids: List[str]) -> Inbox:
        self.from_user_ids = from_user_ids
        return self

    def with_created_at(self, created_at: int) -> Inbox:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Inbox:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Inbox:
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
        return 'grn:gs2:{region}:{ownerId}:friend:{namespaceName}:user:{userId}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
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
    ) -> Optional[Inbox]:
        if data is None:
            return None
        return Inbox()\
            .with_inbox_id(data.get('inboxId'))\
            .with_user_id(data.get('userId'))\
            .with_from_user_ids(None if data.get('fromUserIds') is None else [
                data.get('fromUserIds')[i]
                for i in range(len(data.get('fromUserIds')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inboxId": self.inbox_id,
            "userId": self.user_id,
            "fromUserIds": None if self.from_user_ids is None else [
                self.from_user_ids[i]
                for i in range(len(self.from_user_ids))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class SendBox(core.Gs2Model):
    send_box_id: str = None
    user_id: str = None
    target_user_ids: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_send_box_id(self, send_box_id: str) -> SendBox:
        self.send_box_id = send_box_id
        return self

    def with_user_id(self, user_id: str) -> SendBox:
        self.user_id = user_id
        return self

    def with_target_user_ids(self, target_user_ids: List[str]) -> SendBox:
        self.target_user_ids = target_user_ids
        return self

    def with_created_at(self, created_at: int) -> SendBox:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SendBox:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SendBox:
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
        return 'grn:gs2:{region}:{ownerId}:friend:{namespaceName}:user:{userId}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
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
    ) -> Optional[SendBox]:
        if data is None:
            return None
        return SendBox()\
            .with_send_box_id(data.get('sendBoxId'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_ids(None if data.get('targetUserIds') is None else [
                data.get('targetUserIds')[i]
                for i in range(len(data.get('targetUserIds')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sendBoxId": self.send_box_id,
            "userId": self.user_id,
            "targetUserIds": None if self.target_user_ids is None else [
                self.target_user_ids[i]
                for i in range(len(self.target_user_ids))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Friend(core.Gs2Model):
    friend_id: str = None
    user_id: str = None
    target_user_ids: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_friend_id(self, friend_id: str) -> Friend:
        self.friend_id = friend_id
        return self

    def with_user_id(self, user_id: str) -> Friend:
        self.user_id = user_id
        return self

    def with_target_user_ids(self, target_user_ids: List[str]) -> Friend:
        self.target_user_ids = target_user_ids
        return self

    def with_created_at(self, created_at: int) -> Friend:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Friend:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Friend:
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
        return 'grn:gs2:{region}:{ownerId}:friend:{namespaceName}:user:{userId}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
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
    ) -> Optional[Friend]:
        if data is None:
            return None
        return Friend()\
            .with_friend_id(data.get('friendId'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_ids(None if data.get('targetUserIds') is None else [
                data.get('targetUserIds')[i]
                for i in range(len(data.get('targetUserIds')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "friendId": self.friend_id,
            "userId": self.user_id,
            "targetUserIds": None if self.target_user_ids is None else [
                self.target_user_ids[i]
                for i in range(len(self.target_user_ids))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Follow(core.Gs2Model):
    follow_id: str = None
    user_id: str = None
    target_user_ids: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_follow_id(self, follow_id: str) -> Follow:
        self.follow_id = follow_id
        return self

    def with_user_id(self, user_id: str) -> Follow:
        self.user_id = user_id
        return self

    def with_target_user_ids(self, target_user_ids: List[str]) -> Follow:
        self.target_user_ids = target_user_ids
        return self

    def with_created_at(self, created_at: int) -> Follow:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Follow:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Follow:
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
        return 'grn:gs2:{region}:{ownerId}:friend:{namespaceName}:user:{userId}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
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
    ) -> Optional[Follow]:
        if data is None:
            return None
        return Follow()\
            .with_follow_id(data.get('followId'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_ids(None if data.get('targetUserIds') is None else [
                data.get('targetUserIds')[i]
                for i in range(len(data.get('targetUserIds')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "followId": self.follow_id,
            "userId": self.user_id,
            "targetUserIds": None if self.target_user_ids is None else [
                self.target_user_ids[i]
                for i in range(len(self.target_user_ids))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Profile(core.Gs2Model):
    profile_id: str = None
    user_id: str = None
    public_profile: str = None
    follower_profile: str = None
    friend_profile: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_profile_id(self, profile_id: str) -> Profile:
        self.profile_id = profile_id
        return self

    def with_user_id(self, user_id: str) -> Profile:
        self.user_id = user_id
        return self

    def with_public_profile(self, public_profile: str) -> Profile:
        self.public_profile = public_profile
        return self

    def with_follower_profile(self, follower_profile: str) -> Profile:
        self.follower_profile = follower_profile
        return self

    def with_friend_profile(self, friend_profile: str) -> Profile:
        self.friend_profile = friend_profile
        return self

    def with_created_at(self, created_at: int) -> Profile:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Profile:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Profile:
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
        return 'grn:gs2:{region}:{ownerId}:friend:{namespaceName}:user:{userId}'.format(
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
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+):user:(?P<userId>.+)', grn)
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
    ) -> Optional[Profile]:
        if data is None:
            return None
        return Profile()\
            .with_profile_id(data.get('profileId'))\
            .with_user_id(data.get('userId'))\
            .with_public_profile(data.get('publicProfile'))\
            .with_follower_profile(data.get('followerProfile'))\
            .with_friend_profile(data.get('friendProfile'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "profileId": self.profile_id,
            "userId": self.user_id,
            "publicProfile": self.public_profile,
            "followerProfile": self.follower_profile,
            "friendProfile": self.friend_profile,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    follow_script: ScriptSetting = None
    unfollow_script: ScriptSetting = None
    send_request_script: ScriptSetting = None
    cancel_request_script: ScriptSetting = None
    accept_request_script: ScriptSetting = None
    reject_request_script: ScriptSetting = None
    delete_friend_script: ScriptSetting = None
    update_profile_script: ScriptSetting = None
    follow_notification: NotificationSetting = None
    receive_request_notification: NotificationSetting = None
    cancel_request_notification: NotificationSetting = None
    accept_request_notification: NotificationSetting = None
    reject_request_notification: NotificationSetting = None
    delete_friend_notification: NotificationSetting = None
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

    def with_follow_script(self, follow_script: ScriptSetting) -> Namespace:
        self.follow_script = follow_script
        return self

    def with_unfollow_script(self, unfollow_script: ScriptSetting) -> Namespace:
        self.unfollow_script = unfollow_script
        return self

    def with_send_request_script(self, send_request_script: ScriptSetting) -> Namespace:
        self.send_request_script = send_request_script
        return self

    def with_cancel_request_script(self, cancel_request_script: ScriptSetting) -> Namespace:
        self.cancel_request_script = cancel_request_script
        return self

    def with_accept_request_script(self, accept_request_script: ScriptSetting) -> Namespace:
        self.accept_request_script = accept_request_script
        return self

    def with_reject_request_script(self, reject_request_script: ScriptSetting) -> Namespace:
        self.reject_request_script = reject_request_script
        return self

    def with_delete_friend_script(self, delete_friend_script: ScriptSetting) -> Namespace:
        self.delete_friend_script = delete_friend_script
        return self

    def with_update_profile_script(self, update_profile_script: ScriptSetting) -> Namespace:
        self.update_profile_script = update_profile_script
        return self

    def with_follow_notification(self, follow_notification: NotificationSetting) -> Namespace:
        self.follow_notification = follow_notification
        return self

    def with_receive_request_notification(self, receive_request_notification: NotificationSetting) -> Namespace:
        self.receive_request_notification = receive_request_notification
        return self

    def with_cancel_request_notification(self, cancel_request_notification: NotificationSetting) -> Namespace:
        self.cancel_request_notification = cancel_request_notification
        return self

    def with_accept_request_notification(self, accept_request_notification: NotificationSetting) -> Namespace:
        self.accept_request_notification = accept_request_notification
        return self

    def with_reject_request_notification(self, reject_request_notification: NotificationSetting) -> Namespace:
        self.reject_request_notification = reject_request_notification
        return self

    def with_delete_friend_notification(self, delete_friend_notification: NotificationSetting) -> Namespace:
        self.delete_friend_notification = delete_friend_notification
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
        return 'grn:gs2:{region}:{ownerId}:friend:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):friend:(?P<namespaceName>.+)', grn)
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
            .with_follow_script(ScriptSetting.from_dict(data.get('followScript')))\
            .with_unfollow_script(ScriptSetting.from_dict(data.get('unfollowScript')))\
            .with_send_request_script(ScriptSetting.from_dict(data.get('sendRequestScript')))\
            .with_cancel_request_script(ScriptSetting.from_dict(data.get('cancelRequestScript')))\
            .with_accept_request_script(ScriptSetting.from_dict(data.get('acceptRequestScript')))\
            .with_reject_request_script(ScriptSetting.from_dict(data.get('rejectRequestScript')))\
            .with_delete_friend_script(ScriptSetting.from_dict(data.get('deleteFriendScript')))\
            .with_update_profile_script(ScriptSetting.from_dict(data.get('updateProfileScript')))\
            .with_follow_notification(NotificationSetting.from_dict(data.get('followNotification')))\
            .with_receive_request_notification(NotificationSetting.from_dict(data.get('receiveRequestNotification')))\
            .with_cancel_request_notification(NotificationSetting.from_dict(data.get('cancelRequestNotification')))\
            .with_accept_request_notification(NotificationSetting.from_dict(data.get('acceptRequestNotification')))\
            .with_reject_request_notification(NotificationSetting.from_dict(data.get('rejectRequestNotification')))\
            .with_delete_friend_notification(NotificationSetting.from_dict(data.get('deleteFriendNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "followScript": self.follow_script.to_dict() if self.follow_script else None,
            "unfollowScript": self.unfollow_script.to_dict() if self.unfollow_script else None,
            "sendRequestScript": self.send_request_script.to_dict() if self.send_request_script else None,
            "cancelRequestScript": self.cancel_request_script.to_dict() if self.cancel_request_script else None,
            "acceptRequestScript": self.accept_request_script.to_dict() if self.accept_request_script else None,
            "rejectRequestScript": self.reject_request_script.to_dict() if self.reject_request_script else None,
            "deleteFriendScript": self.delete_friend_script.to_dict() if self.delete_friend_script else None,
            "updateProfileScript": self.update_profile_script.to_dict() if self.update_profile_script else None,
            "followNotification": self.follow_notification.to_dict() if self.follow_notification else None,
            "receiveRequestNotification": self.receive_request_notification.to_dict() if self.receive_request_notification else None,
            "cancelRequestNotification": self.cancel_request_notification.to_dict() if self.cancel_request_notification else None,
            "acceptRequestNotification": self.accept_request_notification.to_dict() if self.accept_request_notification else None,
            "rejectRequestNotification": self.reject_request_notification.to_dict() if self.reject_request_notification else None,
            "deleteFriendNotification": self.delete_friend_notification.to_dict() if self.delete_friend_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }