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

from .model import *


class DescribeNamespacesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeNamespacesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeNamespacesRequest:
        self.limit = limit
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
    ) -> Optional[DescribeNamespacesRequest]:
        if data is None:
            return None
        return DescribeNamespacesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
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

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_follow_script(self, follow_script: ScriptSetting) -> CreateNamespaceRequest:
        self.follow_script = follow_script
        return self

    def with_unfollow_script(self, unfollow_script: ScriptSetting) -> CreateNamespaceRequest:
        self.unfollow_script = unfollow_script
        return self

    def with_send_request_script(self, send_request_script: ScriptSetting) -> CreateNamespaceRequest:
        self.send_request_script = send_request_script
        return self

    def with_cancel_request_script(self, cancel_request_script: ScriptSetting) -> CreateNamespaceRequest:
        self.cancel_request_script = cancel_request_script
        return self

    def with_accept_request_script(self, accept_request_script: ScriptSetting) -> CreateNamespaceRequest:
        self.accept_request_script = accept_request_script
        return self

    def with_reject_request_script(self, reject_request_script: ScriptSetting) -> CreateNamespaceRequest:
        self.reject_request_script = reject_request_script
        return self

    def with_delete_friend_script(self, delete_friend_script: ScriptSetting) -> CreateNamespaceRequest:
        self.delete_friend_script = delete_friend_script
        return self

    def with_update_profile_script(self, update_profile_script: ScriptSetting) -> CreateNamespaceRequest:
        self.update_profile_script = update_profile_script
        return self

    def with_follow_notification(self, follow_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.follow_notification = follow_notification
        return self

    def with_receive_request_notification(self, receive_request_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.receive_request_notification = receive_request_notification
        return self

    def with_cancel_request_notification(self, cancel_request_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.cancel_request_notification = cancel_request_notification
        return self

    def with_accept_request_notification(self, accept_request_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.accept_request_notification = accept_request_notification
        return self

    def with_reject_request_notification(self, reject_request_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.reject_request_notification = reject_request_notification
        return self

    def with_delete_friend_notification(self, delete_friend_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.delete_friend_notification = delete_friend_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
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
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
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
        }


class GetNamespaceStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceStatusRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[GetNamespaceStatusRequest]:
        if data is None:
            return None
        return GetNamespaceStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[GetNamespaceRequest]:
        if data is None:
            return None
        return GetNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
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

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_follow_script(self, follow_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.follow_script = follow_script
        return self

    def with_unfollow_script(self, unfollow_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.unfollow_script = unfollow_script
        return self

    def with_send_request_script(self, send_request_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.send_request_script = send_request_script
        return self

    def with_cancel_request_script(self, cancel_request_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.cancel_request_script = cancel_request_script
        return self

    def with_accept_request_script(self, accept_request_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.accept_request_script = accept_request_script
        return self

    def with_reject_request_script(self, reject_request_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.reject_request_script = reject_request_script
        return self

    def with_delete_friend_script(self, delete_friend_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.delete_friend_script = delete_friend_script
        return self

    def with_update_profile_script(self, update_profile_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.update_profile_script = update_profile_script
        return self

    def with_follow_notification(self, follow_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.follow_notification = follow_notification
        return self

    def with_receive_request_notification(self, receive_request_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.receive_request_notification = receive_request_notification
        return self

    def with_cancel_request_notification(self, cancel_request_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.cancel_request_notification = cancel_request_notification
        return self

    def with_accept_request_notification(self, accept_request_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.accept_request_notification = accept_request_notification
        return self

    def with_reject_request_notification(self, reject_request_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.reject_request_notification = reject_request_notification
        return self

    def with_delete_friend_notification(self, delete_friend_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.delete_friend_notification = delete_friend_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
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
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
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
        }


class DeleteNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteNamespaceRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[DeleteNamespaceRequest]:
        if data is None:
            return None
        return DeleteNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetServiceVersionRequest(core.Gs2Request):

    context_stack: str = None

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
    ) -> Optional[GetServiceVersionRequest]:
        if data is None:
            return None
        return GetServiceVersionRequest()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class DumpUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> DumpUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DumpUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[DumpUserDataByUserIdRequest]:
        if data is None:
            return None
        return DumpUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckDumpUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> CheckDumpUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckDumpUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[CheckDumpUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckDumpUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CleanUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> CleanUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CleanUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[CleanUserDataByUserIdRequest]:
        if data is None:
            return None
        return CleanUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckCleanUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> CheckCleanUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckCleanUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[CheckCleanUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckCleanUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class PrepareImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> PrepareImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PrepareImportUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[PrepareImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return PrepareImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class ImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> ImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> ImportUserDataByUserIdRequest:
        self.upload_token = upload_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ImportUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[ImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return ImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> CheckImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> CheckImportUserDataByUserIdRequest:
        self.upload_token = upload_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckImportUserDataByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[CheckImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
            "timeOffsetToken": self.time_offset_token,
        }


class GetProfileRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetProfileRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetProfileRequest:
        self.access_token = access_token
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
    ) -> Optional[GetProfileRequest]:
        if data is None:
            return None
        return GetProfileRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
        }


class GetProfileByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetProfileByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetProfileByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetProfileByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[GetProfileByUserIdRequest]:
        if data is None:
            return None
        return GetProfileByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class UpdateProfileRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    public_profile: str = None
    follower_profile: str = None
    friend_profile: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateProfileRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> UpdateProfileRequest:
        self.access_token = access_token
        return self

    def with_public_profile(self, public_profile: str) -> UpdateProfileRequest:
        self.public_profile = public_profile
        return self

    def with_follower_profile(self, follower_profile: str) -> UpdateProfileRequest:
        self.follower_profile = follower_profile
        return self

    def with_friend_profile(self, friend_profile: str) -> UpdateProfileRequest:
        self.friend_profile = friend_profile
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateProfileRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[UpdateProfileRequest]:
        if data is None:
            return None
        return UpdateProfileRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_public_profile(data.get('publicProfile'))\
            .with_follower_profile(data.get('followerProfile'))\
            .with_friend_profile(data.get('friendProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "publicProfile": self.public_profile,
            "followerProfile": self.follower_profile,
            "friendProfile": self.friend_profile,
        }


class UpdateProfileByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    public_profile: str = None
    follower_profile: str = None
    friend_profile: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateProfileByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateProfileByUserIdRequest:
        self.user_id = user_id
        return self

    def with_public_profile(self, public_profile: str) -> UpdateProfileByUserIdRequest:
        self.public_profile = public_profile
        return self

    def with_follower_profile(self, follower_profile: str) -> UpdateProfileByUserIdRequest:
        self.follower_profile = follower_profile
        return self

    def with_friend_profile(self, friend_profile: str) -> UpdateProfileByUserIdRequest:
        self.friend_profile = friend_profile
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UpdateProfileByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateProfileByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[UpdateProfileByUserIdRequest]:
        if data is None:
            return None
        return UpdateProfileByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_public_profile(data.get('publicProfile'))\
            .with_follower_profile(data.get('followerProfile'))\
            .with_friend_profile(data.get('friendProfile'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "publicProfile": self.public_profile,
            "followerProfile": self.follower_profile,
            "friendProfile": self.friend_profile,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteProfileByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteProfileByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteProfileByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteProfileByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteProfileByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteProfileByUserIdRequest]:
        if data is None:
            return None
        return DeleteProfileByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class UpdateProfileByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> UpdateProfileByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> UpdateProfileByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[UpdateProfileByStampSheetRequest]:
        if data is None:
            return None
        return UpdateProfileByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DescribeFriendsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    with_profile: bool = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeFriendsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeFriendsRequest:
        self.access_token = access_token
        return self

    def with_with_profile(self, with_profile: bool) -> DescribeFriendsRequest:
        self.with_profile = with_profile
        return self

    def with_page_token(self, page_token: str) -> DescribeFriendsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeFriendsRequest:
        self.limit = limit
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
    ) -> Optional[DescribeFriendsRequest]:
        if data is None:
            return None
        return DescribeFriendsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_with_profile(data.get('withProfile'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "withProfile": self.with_profile,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeFriendsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    with_profile: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeFriendsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeFriendsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_with_profile(self, with_profile: bool) -> DescribeFriendsByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_page_token(self, page_token: str) -> DescribeFriendsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeFriendsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeFriendsByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[DescribeFriendsByUserIdRequest]:
        if data is None:
            return None
        return DescribeFriendsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "withProfile": self.with_profile,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeBlackListRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBlackListRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeBlackListRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeBlackListRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBlackListRequest:
        self.limit = limit
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
    ) -> Optional[DescribeBlackListRequest]:
        if data is None:
            return None
        return DescribeBlackListRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeBlackListByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBlackListByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeBlackListByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeBlackListByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBlackListByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeBlackListByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[DescribeBlackListByUserIdRequest]:
        if data is None:
            return None
        return DescribeBlackListByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class RegisterBlackListRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RegisterBlackListRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> RegisterBlackListRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> RegisterBlackListRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RegisterBlackListRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[RegisterBlackListRequest]:
        if data is None:
            return None
        return RegisterBlackListRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class RegisterBlackListByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RegisterBlackListByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> RegisterBlackListByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> RegisterBlackListByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> RegisterBlackListByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RegisterBlackListByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[RegisterBlackListByUserIdRequest]:
        if data is None:
            return None
        return RegisterBlackListByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class UnregisterBlackListRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnregisterBlackListRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> UnregisterBlackListRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> UnregisterBlackListRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnregisterBlackListRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[UnregisterBlackListRequest]:
        if data is None:
            return None
        return UnregisterBlackListRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class UnregisterBlackListByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnregisterBlackListByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UnregisterBlackListByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> UnregisterBlackListByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UnregisterBlackListByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnregisterBlackListByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[UnregisterBlackListByUserIdRequest]:
        if data is None:
            return None
        return UnregisterBlackListByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeFollowsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    with_profile: bool = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeFollowsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeFollowsRequest:
        self.access_token = access_token
        return self

    def with_with_profile(self, with_profile: bool) -> DescribeFollowsRequest:
        self.with_profile = with_profile
        return self

    def with_page_token(self, page_token: str) -> DescribeFollowsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeFollowsRequest:
        self.limit = limit
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
    ) -> Optional[DescribeFollowsRequest]:
        if data is None:
            return None
        return DescribeFollowsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_with_profile(data.get('withProfile'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "withProfile": self.with_profile,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeFollowsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    with_profile: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeFollowsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeFollowsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_with_profile(self, with_profile: bool) -> DescribeFollowsByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_page_token(self, page_token: str) -> DescribeFollowsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeFollowsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeFollowsByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[DescribeFollowsByUserIdRequest]:
        if data is None:
            return None
        return DescribeFollowsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "withProfile": self.with_profile,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetFollowRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    with_profile: bool = None

    def with_namespace_name(self, namespace_name: str) -> GetFollowRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetFollowRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> GetFollowRequest:
        self.target_user_id = target_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> GetFollowRequest:
        self.with_profile = with_profile
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
    ) -> Optional[GetFollowRequest]:
        if data is None:
            return None
        return GetFollowRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_with_profile(data.get('withProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
            "withProfile": self.with_profile,
        }


class GetFollowByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    with_profile: bool = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetFollowByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetFollowByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> GetFollowByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> GetFollowByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetFollowByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[GetFollowByUserIdRequest]:
        if data is None:
            return None
        return GetFollowByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "withProfile": self.with_profile,
            "timeOffsetToken": self.time_offset_token,
        }


class FollowRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> FollowRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> FollowRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> FollowRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> FollowRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[FollowRequest]:
        if data is None:
            return None
        return FollowRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class FollowByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> FollowByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> FollowByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> FollowByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> FollowByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> FollowByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[FollowByUserIdRequest]:
        if data is None:
            return None
        return FollowByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class UnfollowRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnfollowRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> UnfollowRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> UnfollowRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnfollowRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[UnfollowRequest]:
        if data is None:
            return None
        return UnfollowRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class UnfollowByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnfollowByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UnfollowByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> UnfollowByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UnfollowByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnfollowByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[UnfollowByUserIdRequest]:
        if data is None:
            return None
        return UnfollowByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetFriendRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    with_profile: bool = None

    def with_namespace_name(self, namespace_name: str) -> GetFriendRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetFriendRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> GetFriendRequest:
        self.target_user_id = target_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> GetFriendRequest:
        self.with_profile = with_profile
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
    ) -> Optional[GetFriendRequest]:
        if data is None:
            return None
        return GetFriendRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_with_profile(data.get('withProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
            "withProfile": self.with_profile,
        }


class GetFriendByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    with_profile: bool = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetFriendByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetFriendByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> GetFriendByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> GetFriendByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetFriendByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[GetFriendByUserIdRequest]:
        if data is None:
            return None
        return GetFriendByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "withProfile": self.with_profile,
            "timeOffsetToken": self.time_offset_token,
        }


class AddFriendRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddFriendRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> AddFriendRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> AddFriendRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddFriendRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AddFriendRequest]:
        if data is None:
            return None
        return AddFriendRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class AddFriendByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddFriendByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AddFriendByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> AddFriendByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AddFriendByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddFriendByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AddFriendByUserIdRequest]:
        if data is None:
            return None
        return AddFriendByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteFriendRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteFriendRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteFriendRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> DeleteFriendRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteFriendRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteFriendRequest]:
        if data is None:
            return None
        return DeleteFriendRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class DeleteFriendByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteFriendByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteFriendByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> DeleteFriendByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteFriendByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteFriendByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteFriendByUserIdRequest]:
        if data is None:
            return None
        return DeleteFriendByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeSendRequestsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    with_profile: bool = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSendRequestsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSendRequestsRequest:
        self.access_token = access_token
        return self

    def with_with_profile(self, with_profile: bool) -> DescribeSendRequestsRequest:
        self.with_profile = with_profile
        return self

    def with_page_token(self, page_token: str) -> DescribeSendRequestsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSendRequestsRequest:
        self.limit = limit
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
    ) -> Optional[DescribeSendRequestsRequest]:
        if data is None:
            return None
        return DescribeSendRequestsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_with_profile(data.get('withProfile'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "withProfile": self.with_profile,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeSendRequestsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    with_profile: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSendRequestsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSendRequestsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_with_profile(self, with_profile: bool) -> DescribeSendRequestsByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_page_token(self, page_token: str) -> DescribeSendRequestsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSendRequestsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeSendRequestsByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[DescribeSendRequestsByUserIdRequest]:
        if data is None:
            return None
        return DescribeSendRequestsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "withProfile": self.with_profile,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetSendRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    with_profile: bool = None

    def with_namespace_name(self, namespace_name: str) -> GetSendRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetSendRequestRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> GetSendRequestRequest:
        self.target_user_id = target_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> GetSendRequestRequest:
        self.with_profile = with_profile
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
    ) -> Optional[GetSendRequestRequest]:
        if data is None:
            return None
        return GetSendRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_with_profile(data.get('withProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
            "withProfile": self.with_profile,
        }


class GetSendRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    with_profile: bool = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSendRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetSendRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> GetSendRequestByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> GetSendRequestByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetSendRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[GetSendRequestByUserIdRequest]:
        if data is None:
            return None
        return GetSendRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "withProfile": self.with_profile,
            "timeOffsetToken": self.time_offset_token,
        }


class SendRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    with_profile: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SendRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SendRequestRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> SendRequestRequest:
        self.target_user_id = target_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> SendRequestRequest:
        self.with_profile = with_profile
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SendRequestRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[SendRequestRequest]:
        if data is None:
            return None
        return SendRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_with_profile(data.get('withProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
            "withProfile": self.with_profile,
        }


class SendRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    with_profile: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SendRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SendRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> SendRequestByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> SendRequestByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SendRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SendRequestByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[SendRequestByUserIdRequest]:
        if data is None:
            return None
        return SendRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "withProfile": self.with_profile,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteRequestRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> DeleteRequestRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteRequestRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteRequestRequest]:
        if data is None:
            return None
        return DeleteRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class DeleteRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> DeleteRequestByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteRequestByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteRequestByUserIdRequest]:
        if data is None:
            return None
        return DeleteRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeReceiveRequestsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    with_profile: bool = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReceiveRequestsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeReceiveRequestsRequest:
        self.access_token = access_token
        return self

    def with_with_profile(self, with_profile: bool) -> DescribeReceiveRequestsRequest:
        self.with_profile = with_profile
        return self

    def with_page_token(self, page_token: str) -> DescribeReceiveRequestsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeReceiveRequestsRequest:
        self.limit = limit
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
    ) -> Optional[DescribeReceiveRequestsRequest]:
        if data is None:
            return None
        return DescribeReceiveRequestsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_with_profile(data.get('withProfile'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "withProfile": self.with_profile,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeReceiveRequestsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    with_profile: bool = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReceiveRequestsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeReceiveRequestsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_with_profile(self, with_profile: bool) -> DescribeReceiveRequestsByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_page_token(self, page_token: str) -> DescribeReceiveRequestsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeReceiveRequestsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeReceiveRequestsByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[DescribeReceiveRequestsByUserIdRequest]:
        if data is None:
            return None
        return DescribeReceiveRequestsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "withProfile": self.with_profile,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetReceiveRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    from_user_id: str = None
    with_profile: bool = None

    def with_namespace_name(self, namespace_name: str) -> GetReceiveRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetReceiveRequestRequest:
        self.access_token = access_token
        return self

    def with_from_user_id(self, from_user_id: str) -> GetReceiveRequestRequest:
        self.from_user_id = from_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> GetReceiveRequestRequest:
        self.with_profile = with_profile
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
    ) -> Optional[GetReceiveRequestRequest]:
        if data is None:
            return None
        return GetReceiveRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_from_user_id(data.get('fromUserId'))\
            .with_with_profile(data.get('withProfile'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "fromUserId": self.from_user_id,
            "withProfile": self.with_profile,
        }


class GetReceiveRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    from_user_id: str = None
    with_profile: bool = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReceiveRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetReceiveRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_from_user_id(self, from_user_id: str) -> GetReceiveRequestByUserIdRequest:
        self.from_user_id = from_user_id
        return self

    def with_with_profile(self, with_profile: bool) -> GetReceiveRequestByUserIdRequest:
        self.with_profile = with_profile
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetReceiveRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[GetReceiveRequestByUserIdRequest]:
        if data is None:
            return None
        return GetReceiveRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_from_user_id(data.get('fromUserId'))\
            .with_with_profile(data.get('withProfile'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "fromUserId": self.from_user_id,
            "withProfile": self.with_profile,
            "timeOffsetToken": self.time_offset_token,
        }


class AcceptRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    from_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcceptRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> AcceptRequestRequest:
        self.access_token = access_token
        return self

    def with_from_user_id(self, from_user_id: str) -> AcceptRequestRequest:
        self.from_user_id = from_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcceptRequestRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AcceptRequestRequest]:
        if data is None:
            return None
        return AcceptRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_from_user_id(data.get('fromUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "fromUserId": self.from_user_id,
        }


class AcceptRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    from_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcceptRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AcceptRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_from_user_id(self, from_user_id: str) -> AcceptRequestByUserIdRequest:
        self.from_user_id = from_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcceptRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcceptRequestByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AcceptRequestByUserIdRequest]:
        if data is None:
            return None
        return AcceptRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_from_user_id(data.get('fromUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "fromUserId": self.from_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class RejectRequestRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    from_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RejectRequestRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> RejectRequestRequest:
        self.access_token = access_token
        return self

    def with_from_user_id(self, from_user_id: str) -> RejectRequestRequest:
        self.from_user_id = from_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RejectRequestRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[RejectRequestRequest]:
        if data is None:
            return None
        return RejectRequestRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_from_user_id(data.get('fromUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "fromUserId": self.from_user_id,
        }


class RejectRequestByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    from_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RejectRequestByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> RejectRequestByUserIdRequest:
        self.user_id = user_id
        return self

    def with_from_user_id(self, from_user_id: str) -> RejectRequestByUserIdRequest:
        self.from_user_id = from_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> RejectRequestByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RejectRequestByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[RejectRequestByUserIdRequest]:
        if data is None:
            return None
        return RejectRequestByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_from_user_id(data.get('fromUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "fromUserId": self.from_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetPublicProfileRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPublicProfileRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetPublicProfileRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetPublicProfileRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[GetPublicProfileRequest]:
        if data is None:
            return None
        return GetPublicProfileRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }