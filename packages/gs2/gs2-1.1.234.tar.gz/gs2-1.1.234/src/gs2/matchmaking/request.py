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
    enable_rating: bool = None
    enable_disconnect_detection: str = None
    disconnect_detection_timeout_seconds: int = None
    create_gathering_trigger_type: str = None
    create_gathering_trigger_realtime_namespace_id: str = None
    create_gathering_trigger_script_id: str = None
    complete_matchmaking_trigger_type: str = None
    complete_matchmaking_trigger_realtime_namespace_id: str = None
    complete_matchmaking_trigger_script_id: str = None
    enable_collaborate_season_rating: str = None
    collaborate_season_rating_namespace_id: str = None
    collaborate_season_rating_ttl: int = None
    change_rating_script: ScriptSetting = None
    join_notification: NotificationSetting = None
    leave_notification: NotificationSetting = None
    complete_notification: NotificationSetting = None
    change_rating_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_enable_rating(self, enable_rating: bool) -> CreateNamespaceRequest:
        self.enable_rating = enable_rating
        return self

    def with_enable_disconnect_detection(self, enable_disconnect_detection: str) -> CreateNamespaceRequest:
        self.enable_disconnect_detection = enable_disconnect_detection
        return self

    def with_disconnect_detection_timeout_seconds(self, disconnect_detection_timeout_seconds: int) -> CreateNamespaceRequest:
        self.disconnect_detection_timeout_seconds = disconnect_detection_timeout_seconds
        return self

    def with_create_gathering_trigger_type(self, create_gathering_trigger_type: str) -> CreateNamespaceRequest:
        self.create_gathering_trigger_type = create_gathering_trigger_type
        return self

    def with_create_gathering_trigger_realtime_namespace_id(self, create_gathering_trigger_realtime_namespace_id: str) -> CreateNamespaceRequest:
        self.create_gathering_trigger_realtime_namespace_id = create_gathering_trigger_realtime_namespace_id
        return self

    def with_create_gathering_trigger_script_id(self, create_gathering_trigger_script_id: str) -> CreateNamespaceRequest:
        self.create_gathering_trigger_script_id = create_gathering_trigger_script_id
        return self

    def with_complete_matchmaking_trigger_type(self, complete_matchmaking_trigger_type: str) -> CreateNamespaceRequest:
        self.complete_matchmaking_trigger_type = complete_matchmaking_trigger_type
        return self

    def with_complete_matchmaking_trigger_realtime_namespace_id(self, complete_matchmaking_trigger_realtime_namespace_id: str) -> CreateNamespaceRequest:
        self.complete_matchmaking_trigger_realtime_namespace_id = complete_matchmaking_trigger_realtime_namespace_id
        return self

    def with_complete_matchmaking_trigger_script_id(self, complete_matchmaking_trigger_script_id: str) -> CreateNamespaceRequest:
        self.complete_matchmaking_trigger_script_id = complete_matchmaking_trigger_script_id
        return self

    def with_enable_collaborate_season_rating(self, enable_collaborate_season_rating: str) -> CreateNamespaceRequest:
        self.enable_collaborate_season_rating = enable_collaborate_season_rating
        return self

    def with_collaborate_season_rating_namespace_id(self, collaborate_season_rating_namespace_id: str) -> CreateNamespaceRequest:
        self.collaborate_season_rating_namespace_id = collaborate_season_rating_namespace_id
        return self

    def with_collaborate_season_rating_ttl(self, collaborate_season_rating_ttl: int) -> CreateNamespaceRequest:
        self.collaborate_season_rating_ttl = collaborate_season_rating_ttl
        return self

    def with_change_rating_script(self, change_rating_script: ScriptSetting) -> CreateNamespaceRequest:
        self.change_rating_script = change_rating_script
        return self

    def with_join_notification(self, join_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.join_notification = join_notification
        return self

    def with_leave_notification(self, leave_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.leave_notification = leave_notification
        return self

    def with_complete_notification(self, complete_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.complete_notification = complete_notification
        return self

    def with_change_rating_notification(self, change_rating_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.change_rating_notification = change_rating_notification
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
            .with_enable_rating(data.get('enableRating'))\
            .with_enable_disconnect_detection(data.get('enableDisconnectDetection'))\
            .with_disconnect_detection_timeout_seconds(data.get('disconnectDetectionTimeoutSeconds'))\
            .with_create_gathering_trigger_type(data.get('createGatheringTriggerType'))\
            .with_create_gathering_trigger_realtime_namespace_id(data.get('createGatheringTriggerRealtimeNamespaceId'))\
            .with_create_gathering_trigger_script_id(data.get('createGatheringTriggerScriptId'))\
            .with_complete_matchmaking_trigger_type(data.get('completeMatchmakingTriggerType'))\
            .with_complete_matchmaking_trigger_realtime_namespace_id(data.get('completeMatchmakingTriggerRealtimeNamespaceId'))\
            .with_complete_matchmaking_trigger_script_id(data.get('completeMatchmakingTriggerScriptId'))\
            .with_enable_collaborate_season_rating(data.get('enableCollaborateSeasonRating'))\
            .with_collaborate_season_rating_namespace_id(data.get('collaborateSeasonRatingNamespaceId'))\
            .with_collaborate_season_rating_ttl(data.get('collaborateSeasonRatingTtl'))\
            .with_change_rating_script(ScriptSetting.from_dict(data.get('changeRatingScript')))\
            .with_join_notification(NotificationSetting.from_dict(data.get('joinNotification')))\
            .with_leave_notification(NotificationSetting.from_dict(data.get('leaveNotification')))\
            .with_complete_notification(NotificationSetting.from_dict(data.get('completeNotification')))\
            .with_change_rating_notification(NotificationSetting.from_dict(data.get('changeRatingNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "enableRating": self.enable_rating,
            "enableDisconnectDetection": self.enable_disconnect_detection,
            "disconnectDetectionTimeoutSeconds": self.disconnect_detection_timeout_seconds,
            "createGatheringTriggerType": self.create_gathering_trigger_type,
            "createGatheringTriggerRealtimeNamespaceId": self.create_gathering_trigger_realtime_namespace_id,
            "createGatheringTriggerScriptId": self.create_gathering_trigger_script_id,
            "completeMatchmakingTriggerType": self.complete_matchmaking_trigger_type,
            "completeMatchmakingTriggerRealtimeNamespaceId": self.complete_matchmaking_trigger_realtime_namespace_id,
            "completeMatchmakingTriggerScriptId": self.complete_matchmaking_trigger_script_id,
            "enableCollaborateSeasonRating": self.enable_collaborate_season_rating,
            "collaborateSeasonRatingNamespaceId": self.collaborate_season_rating_namespace_id,
            "collaborateSeasonRatingTtl": self.collaborate_season_rating_ttl,
            "changeRatingScript": self.change_rating_script.to_dict() if self.change_rating_script else None,
            "joinNotification": self.join_notification.to_dict() if self.join_notification else None,
            "leaveNotification": self.leave_notification.to_dict() if self.leave_notification else None,
            "completeNotification": self.complete_notification.to_dict() if self.complete_notification else None,
            "changeRatingNotification": self.change_rating_notification.to_dict() if self.change_rating_notification else None,
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
    enable_rating: bool = None
    enable_disconnect_detection: str = None
    disconnect_detection_timeout_seconds: int = None
    create_gathering_trigger_type: str = None
    create_gathering_trigger_realtime_namespace_id: str = None
    create_gathering_trigger_script_id: str = None
    complete_matchmaking_trigger_type: str = None
    complete_matchmaking_trigger_realtime_namespace_id: str = None
    complete_matchmaking_trigger_script_id: str = None
    enable_collaborate_season_rating: str = None
    collaborate_season_rating_namespace_id: str = None
    collaborate_season_rating_ttl: int = None
    change_rating_script: ScriptSetting = None
    join_notification: NotificationSetting = None
    leave_notification: NotificationSetting = None
    complete_notification: NotificationSetting = None
    change_rating_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_enable_rating(self, enable_rating: bool) -> UpdateNamespaceRequest:
        self.enable_rating = enable_rating
        return self

    def with_enable_disconnect_detection(self, enable_disconnect_detection: str) -> UpdateNamespaceRequest:
        self.enable_disconnect_detection = enable_disconnect_detection
        return self

    def with_disconnect_detection_timeout_seconds(self, disconnect_detection_timeout_seconds: int) -> UpdateNamespaceRequest:
        self.disconnect_detection_timeout_seconds = disconnect_detection_timeout_seconds
        return self

    def with_create_gathering_trigger_type(self, create_gathering_trigger_type: str) -> UpdateNamespaceRequest:
        self.create_gathering_trigger_type = create_gathering_trigger_type
        return self

    def with_create_gathering_trigger_realtime_namespace_id(self, create_gathering_trigger_realtime_namespace_id: str) -> UpdateNamespaceRequest:
        self.create_gathering_trigger_realtime_namespace_id = create_gathering_trigger_realtime_namespace_id
        return self

    def with_create_gathering_trigger_script_id(self, create_gathering_trigger_script_id: str) -> UpdateNamespaceRequest:
        self.create_gathering_trigger_script_id = create_gathering_trigger_script_id
        return self

    def with_complete_matchmaking_trigger_type(self, complete_matchmaking_trigger_type: str) -> UpdateNamespaceRequest:
        self.complete_matchmaking_trigger_type = complete_matchmaking_trigger_type
        return self

    def with_complete_matchmaking_trigger_realtime_namespace_id(self, complete_matchmaking_trigger_realtime_namespace_id: str) -> UpdateNamespaceRequest:
        self.complete_matchmaking_trigger_realtime_namespace_id = complete_matchmaking_trigger_realtime_namespace_id
        return self

    def with_complete_matchmaking_trigger_script_id(self, complete_matchmaking_trigger_script_id: str) -> UpdateNamespaceRequest:
        self.complete_matchmaking_trigger_script_id = complete_matchmaking_trigger_script_id
        return self

    def with_enable_collaborate_season_rating(self, enable_collaborate_season_rating: str) -> UpdateNamespaceRequest:
        self.enable_collaborate_season_rating = enable_collaborate_season_rating
        return self

    def with_collaborate_season_rating_namespace_id(self, collaborate_season_rating_namespace_id: str) -> UpdateNamespaceRequest:
        self.collaborate_season_rating_namespace_id = collaborate_season_rating_namespace_id
        return self

    def with_collaborate_season_rating_ttl(self, collaborate_season_rating_ttl: int) -> UpdateNamespaceRequest:
        self.collaborate_season_rating_ttl = collaborate_season_rating_ttl
        return self

    def with_change_rating_script(self, change_rating_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.change_rating_script = change_rating_script
        return self

    def with_join_notification(self, join_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.join_notification = join_notification
        return self

    def with_leave_notification(self, leave_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.leave_notification = leave_notification
        return self

    def with_complete_notification(self, complete_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.complete_notification = complete_notification
        return self

    def with_change_rating_notification(self, change_rating_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.change_rating_notification = change_rating_notification
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
            .with_enable_rating(data.get('enableRating'))\
            .with_enable_disconnect_detection(data.get('enableDisconnectDetection'))\
            .with_disconnect_detection_timeout_seconds(data.get('disconnectDetectionTimeoutSeconds'))\
            .with_create_gathering_trigger_type(data.get('createGatheringTriggerType'))\
            .with_create_gathering_trigger_realtime_namespace_id(data.get('createGatheringTriggerRealtimeNamespaceId'))\
            .with_create_gathering_trigger_script_id(data.get('createGatheringTriggerScriptId'))\
            .with_complete_matchmaking_trigger_type(data.get('completeMatchmakingTriggerType'))\
            .with_complete_matchmaking_trigger_realtime_namespace_id(data.get('completeMatchmakingTriggerRealtimeNamespaceId'))\
            .with_complete_matchmaking_trigger_script_id(data.get('completeMatchmakingTriggerScriptId'))\
            .with_enable_collaborate_season_rating(data.get('enableCollaborateSeasonRating'))\
            .with_collaborate_season_rating_namespace_id(data.get('collaborateSeasonRatingNamespaceId'))\
            .with_collaborate_season_rating_ttl(data.get('collaborateSeasonRatingTtl'))\
            .with_change_rating_script(ScriptSetting.from_dict(data.get('changeRatingScript')))\
            .with_join_notification(NotificationSetting.from_dict(data.get('joinNotification')))\
            .with_leave_notification(NotificationSetting.from_dict(data.get('leaveNotification')))\
            .with_complete_notification(NotificationSetting.from_dict(data.get('completeNotification')))\
            .with_change_rating_notification(NotificationSetting.from_dict(data.get('changeRatingNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "enableRating": self.enable_rating,
            "enableDisconnectDetection": self.enable_disconnect_detection,
            "disconnectDetectionTimeoutSeconds": self.disconnect_detection_timeout_seconds,
            "createGatheringTriggerType": self.create_gathering_trigger_type,
            "createGatheringTriggerRealtimeNamespaceId": self.create_gathering_trigger_realtime_namespace_id,
            "createGatheringTriggerScriptId": self.create_gathering_trigger_script_id,
            "completeMatchmakingTriggerType": self.complete_matchmaking_trigger_type,
            "completeMatchmakingTriggerRealtimeNamespaceId": self.complete_matchmaking_trigger_realtime_namespace_id,
            "completeMatchmakingTriggerScriptId": self.complete_matchmaking_trigger_script_id,
            "enableCollaborateSeasonRating": self.enable_collaborate_season_rating,
            "collaborateSeasonRatingNamespaceId": self.collaborate_season_rating_namespace_id,
            "collaborateSeasonRatingTtl": self.collaborate_season_rating_ttl,
            "changeRatingScript": self.change_rating_script.to_dict() if self.change_rating_script else None,
            "joinNotification": self.join_notification.to_dict() if self.join_notification else None,
            "leaveNotification": self.leave_notification.to_dict() if self.leave_notification else None,
            "completeNotification": self.complete_notification.to_dict() if self.complete_notification else None,
            "changeRatingNotification": self.change_rating_notification.to_dict() if self.change_rating_notification else None,
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


class DescribeGatheringsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGatheringsRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeGatheringsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGatheringsRequest:
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
    ) -> Optional[DescribeGatheringsRequest]:
        if data is None:
            return None
        return DescribeGatheringsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    player: Player = None
    attribute_ranges: List[AttributeRange] = None
    capacity_of_roles: List[CapacityOfRole] = None
    allow_user_ids: List[str] = None
    expires_at: int = None
    expires_at_time_span: TimeSpan = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CreateGatheringRequest:
        self.access_token = access_token
        return self

    def with_player(self, player: Player) -> CreateGatheringRequest:
        self.player = player
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> CreateGatheringRequest:
        self.attribute_ranges = attribute_ranges
        return self

    def with_capacity_of_roles(self, capacity_of_roles: List[CapacityOfRole]) -> CreateGatheringRequest:
        self.capacity_of_roles = capacity_of_roles
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> CreateGatheringRequest:
        self.allow_user_ids = allow_user_ids
        return self

    def with_expires_at(self, expires_at: int) -> CreateGatheringRequest:
        self.expires_at = expires_at
        return self

    def with_expires_at_time_span(self, expires_at_time_span: TimeSpan) -> CreateGatheringRequest:
        self.expires_at_time_span = expires_at_time_span
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateGatheringRequest:
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
    ) -> Optional[CreateGatheringRequest]:
        if data is None:
            return None
        return CreateGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_attribute_ranges(None if data.get('attributeRanges') is None else [
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')))
            ])\
            .with_capacity_of_roles(None if data.get('capacityOfRoles') is None else [
                CapacityOfRole.from_dict(data.get('capacityOfRoles')[i])
                for i in range(len(data.get('capacityOfRoles')))
            ])\
            .with_allow_user_ids(None if data.get('allowUserIds') is None else [
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')))
            ])\
            .with_expires_at(data.get('expiresAt'))\
            .with_expires_at_time_span(TimeSpan.from_dict(data.get('expiresAtTimeSpan')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "player": self.player.to_dict() if self.player else None,
            "attributeRanges": None if self.attribute_ranges is None else [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges))
            ],
            "capacityOfRoles": None if self.capacity_of_roles is None else [
                self.capacity_of_roles[i].to_dict() if self.capacity_of_roles[i] else None
                for i in range(len(self.capacity_of_roles))
            ],
            "allowUserIds": None if self.allow_user_ids is None else [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids))
            ],
            "expiresAt": self.expires_at,
            "expiresAtTimeSpan": self.expires_at_time_span.to_dict() if self.expires_at_time_span else None,
        }


class CreateGatheringByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    player: Player = None
    attribute_ranges: List[AttributeRange] = None
    capacity_of_roles: List[CapacityOfRole] = None
    allow_user_ids: List[str] = None
    expires_at: int = None
    expires_at_time_span: TimeSpan = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGatheringByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateGatheringByUserIdRequest:
        self.user_id = user_id
        return self

    def with_player(self, player: Player) -> CreateGatheringByUserIdRequest:
        self.player = player
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> CreateGatheringByUserIdRequest:
        self.attribute_ranges = attribute_ranges
        return self

    def with_capacity_of_roles(self, capacity_of_roles: List[CapacityOfRole]) -> CreateGatheringByUserIdRequest:
        self.capacity_of_roles = capacity_of_roles
        return self

    def with_allow_user_ids(self, allow_user_ids: List[str]) -> CreateGatheringByUserIdRequest:
        self.allow_user_ids = allow_user_ids
        return self

    def with_expires_at(self, expires_at: int) -> CreateGatheringByUserIdRequest:
        self.expires_at = expires_at
        return self

    def with_expires_at_time_span(self, expires_at_time_span: TimeSpan) -> CreateGatheringByUserIdRequest:
        self.expires_at_time_span = expires_at_time_span
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreateGatheringByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateGatheringByUserIdRequest:
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
    ) -> Optional[CreateGatheringByUserIdRequest]:
        if data is None:
            return None
        return CreateGatheringByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_attribute_ranges(None if data.get('attributeRanges') is None else [
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')))
            ])\
            .with_capacity_of_roles(None if data.get('capacityOfRoles') is None else [
                CapacityOfRole.from_dict(data.get('capacityOfRoles')[i])
                for i in range(len(data.get('capacityOfRoles')))
            ])\
            .with_allow_user_ids(None if data.get('allowUserIds') is None else [
                data.get('allowUserIds')[i]
                for i in range(len(data.get('allowUserIds')))
            ])\
            .with_expires_at(data.get('expiresAt'))\
            .with_expires_at_time_span(TimeSpan.from_dict(data.get('expiresAtTimeSpan')))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "player": self.player.to_dict() if self.player else None,
            "attributeRanges": None if self.attribute_ranges is None else [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges))
            ],
            "capacityOfRoles": None if self.capacity_of_roles is None else [
                self.capacity_of_roles[i].to_dict() if self.capacity_of_roles[i] else None
                for i in range(len(self.capacity_of_roles))
            ],
            "allowUserIds": None if self.allow_user_ids is None else [
                self.allow_user_ids[i]
                for i in range(len(self.allow_user_ids))
            ],
            "expiresAt": self.expires_at,
            "expiresAtTimeSpan": self.expires_at_time_span.to_dict() if self.expires_at_time_span else None,
            "timeOffsetToken": self.time_offset_token,
        }


class UpdateGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    access_token: str = None
    attribute_ranges: List[AttributeRange] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> UpdateGatheringRequest:
        self.gathering_name = gathering_name
        return self

    def with_access_token(self, access_token: str) -> UpdateGatheringRequest:
        self.access_token = access_token
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> UpdateGatheringRequest:
        self.attribute_ranges = attribute_ranges
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateGatheringRequest:
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
    ) -> Optional[UpdateGatheringRequest]:
        if data is None:
            return None
        return UpdateGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_access_token(data.get('accessToken'))\
            .with_attribute_ranges(None if data.get('attributeRanges') is None else [
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "accessToken": self.access_token,
            "attributeRanges": None if self.attribute_ranges is None else [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges))
            ],
        }


class UpdateGatheringByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    user_id: str = None
    attribute_ranges: List[AttributeRange] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGatheringByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> UpdateGatheringByUserIdRequest:
        self.gathering_name = gathering_name
        return self

    def with_user_id(self, user_id: str) -> UpdateGatheringByUserIdRequest:
        self.user_id = user_id
        return self

    def with_attribute_ranges(self, attribute_ranges: List[AttributeRange]) -> UpdateGatheringByUserIdRequest:
        self.attribute_ranges = attribute_ranges
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UpdateGatheringByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateGatheringByUserIdRequest:
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
    ) -> Optional[UpdateGatheringByUserIdRequest]:
        if data is None:
            return None
        return UpdateGatheringByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_user_id(data.get('userId'))\
            .with_attribute_ranges(None if data.get('attributeRanges') is None else [
                AttributeRange.from_dict(data.get('attributeRanges')[i])
                for i in range(len(data.get('attributeRanges')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "userId": self.user_id,
            "attributeRanges": None if self.attribute_ranges is None else [
                self.attribute_ranges[i].to_dict() if self.attribute_ranges[i] else None
                for i in range(len(self.attribute_ranges))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DoMatchmakingByPlayerRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    player: Player = None
    matchmaking_context_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DoMatchmakingByPlayerRequest:
        self.namespace_name = namespace_name
        return self

    def with_player(self, player: Player) -> DoMatchmakingByPlayerRequest:
        self.player = player
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingByPlayerRequest:
        self.matchmaking_context_token = matchmaking_context_token
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
    ) -> Optional[DoMatchmakingByPlayerRequest]:
        if data is None:
            return None
        return DoMatchmakingByPlayerRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "player": self.player.to_dict() if self.player else None,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class DoMatchmakingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    player: Player = None
    matchmaking_context_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DoMatchmakingRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DoMatchmakingRequest:
        self.access_token = access_token
        return self

    def with_player(self, player: Player) -> DoMatchmakingRequest:
        self.player = player
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingRequest:
        self.matchmaking_context_token = matchmaking_context_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DoMatchmakingRequest:
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
    ) -> Optional[DoMatchmakingRequest]:
        if data is None:
            return None
        return DoMatchmakingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "player": self.player.to_dict() if self.player else None,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class DoMatchmakingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    player: Player = None
    matchmaking_context_token: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DoMatchmakingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DoMatchmakingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_player(self, player: Player) -> DoMatchmakingByUserIdRequest:
        self.player = player
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoMatchmakingByUserIdRequest:
        self.matchmaking_context_token = matchmaking_context_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DoMatchmakingByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DoMatchmakingByUserIdRequest:
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
    ) -> Optional[DoMatchmakingByUserIdRequest]:
        if data is None:
            return None
        return DoMatchmakingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_player(Player.from_dict(data.get('player')))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "player": self.player.to_dict() if self.player else None,
            "matchmakingContextToken": self.matchmaking_context_token,
            "timeOffsetToken": self.time_offset_token,
        }


class PingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    access_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PingRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> PingRequest:
        self.gathering_name = gathering_name
        return self

    def with_access_token(self, access_token: str) -> PingRequest:
        self.access_token = access_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PingRequest:
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
    ) -> Optional[PingRequest]:
        if data is None:
            return None
        return PingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "accessToken": self.access_token,
        }


class PingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> PingByUserIdRequest:
        self.gathering_name = gathering_name
        return self

    def with_user_id(self, user_id: str) -> PingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PingByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PingByUserIdRequest:
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
    ) -> Optional[PingByUserIdRequest]:
        if data is None:
            return None
        return PingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> GetGatheringRequest:
        self.gathering_name = gathering_name
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
    ) -> Optional[GetGatheringRequest]:
        if data is None:
            return None
        return GetGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
        }


class CancelMatchmakingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    access_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CancelMatchmakingRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> CancelMatchmakingRequest:
        self.gathering_name = gathering_name
        return self

    def with_access_token(self, access_token: str) -> CancelMatchmakingRequest:
        self.access_token = access_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CancelMatchmakingRequest:
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
    ) -> Optional[CancelMatchmakingRequest]:
        if data is None:
            return None
        return CancelMatchmakingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "accessToken": self.access_token,
        }


class CancelMatchmakingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CancelMatchmakingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> CancelMatchmakingByUserIdRequest:
        self.gathering_name = gathering_name
        return self

    def with_user_id(self, user_id: str) -> CancelMatchmakingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CancelMatchmakingByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CancelMatchmakingByUserIdRequest:
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
    ) -> Optional[CancelMatchmakingByUserIdRequest]:
        if data is None:
            return None
        return CancelMatchmakingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class EarlyCompleteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    access_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> EarlyCompleteRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> EarlyCompleteRequest:
        self.gathering_name = gathering_name
        return self

    def with_access_token(self, access_token: str) -> EarlyCompleteRequest:
        self.access_token = access_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> EarlyCompleteRequest:
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
    ) -> Optional[EarlyCompleteRequest]:
        if data is None:
            return None
        return EarlyCompleteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "accessToken": self.access_token,
        }


class EarlyCompleteByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> EarlyCompleteByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> EarlyCompleteByUserIdRequest:
        self.gathering_name = gathering_name
        return self

    def with_user_id(self, user_id: str) -> EarlyCompleteByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> EarlyCompleteByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> EarlyCompleteByUserIdRequest:
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
    ) -> Optional[EarlyCompleteByUserIdRequest]:
        if data is None:
            return None
        return EarlyCompleteByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    gathering_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_gathering_name(self, gathering_name: str) -> DeleteGatheringRequest:
        self.gathering_name = gathering_name
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
    ) -> Optional[DeleteGatheringRequest]:
        if data is None:
            return None
        return DeleteGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_gathering_name(data.get('gatheringName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "gatheringName": self.gathering_name,
        }


class DescribeRatingModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRatingModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRatingModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRatingModelMastersRequest:
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
    ) -> Optional[DescribeRatingModelMastersRequest]:
        if data is None:
            return None
        return DescribeRatingModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    initial_value: int = None
    volatility: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRatingModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRatingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRatingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_initial_value(self, initial_value: int) -> CreateRatingModelMasterRequest:
        self.initial_value = initial_value
        return self

    def with_volatility(self, volatility: int) -> CreateRatingModelMasterRequest:
        self.volatility = volatility
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
    ) -> Optional[CreateRatingModelMasterRequest]:
        if data is None:
            return None
        return CreateRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_initial_value(data.get('initialValue'))\
            .with_volatility(data.get('volatility'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "initialValue": self.initial_value,
            "volatility": self.volatility,
        }


class GetRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> GetRatingModelMasterRequest:
        self.rating_name = rating_name
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
    ) -> Optional[GetRatingModelMasterRequest]:
        if data is None:
            return None
        return GetRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
        }


class UpdateRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    description: str = None
    metadata: str = None
    initial_value: int = None
    volatility: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> UpdateRatingModelMasterRequest:
        self.rating_name = rating_name
        return self

    def with_description(self, description: str) -> UpdateRatingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRatingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_initial_value(self, initial_value: int) -> UpdateRatingModelMasterRequest:
        self.initial_value = initial_value
        return self

    def with_volatility(self, volatility: int) -> UpdateRatingModelMasterRequest:
        self.volatility = volatility
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
    ) -> Optional[UpdateRatingModelMasterRequest]:
        if data is None:
            return None
        return UpdateRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_initial_value(data.get('initialValue'))\
            .with_volatility(data.get('volatility'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "description": self.description,
            "metadata": self.metadata,
            "initialValue": self.initial_value,
            "volatility": self.volatility,
        }


class DeleteRatingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRatingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> DeleteRatingModelMasterRequest:
        self.rating_name = rating_name
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
    ) -> Optional[DeleteRatingModelMasterRequest]:
        if data is None:
            return None
        return DeleteRatingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
        }


class DescribeRatingModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRatingModelsRequest:
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
    ) -> Optional[DescribeRatingModelsRequest]:
        if data is None:
            return None
        return DescribeRatingModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetRatingModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRatingModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> GetRatingModelRequest:
        self.rating_name = rating_name
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
    ) -> Optional[GetRatingModelRequest]:
        if data is None:
            return None
        return GetRatingModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
        }


class ExportMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> ExportMasterRequest:
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
    ) -> Optional[ExportMasterRequest]:
        if data is None:
            return None
        return ExportMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCurrentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentModelMasterRequest:
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
    ) -> Optional[GetCurrentModelMasterRequest]:
        if data is None:
            return None
        return GetCurrentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentModelMasterRequest:
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
    ) -> Optional[PreUpdateCurrentModelMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentModelMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentModelMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentModelMasterRequest:
        self.upload_token = upload_token
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
    ) -> Optional[UpdateCurrentModelMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mode(data.get('mode'))\
            .with_settings(data.get('settings'))\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "mode": self.mode,
            "settings": self.settings,
            "uploadToken": self.upload_token,
        }


class UpdateCurrentModelMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentModelMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentModelMasterFromGitHubRequest:
        self.checkout_setting = checkout_setting
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
    ) -> Optional[UpdateCurrentModelMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentModelMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeSeasonModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSeasonModelsRequest:
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
    ) -> Optional[DescribeSeasonModelsRequest]:
        if data is None:
            return None
        return DescribeSeasonModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetSeasonModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSeasonModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> GetSeasonModelRequest:
        self.season_name = season_name
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
    ) -> Optional[GetSeasonModelRequest]:
        if data is None:
            return None
        return GetSeasonModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
        }


class DescribeSeasonModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSeasonModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSeasonModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSeasonModelMastersRequest:
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
    ) -> Optional[DescribeSeasonModelMastersRequest]:
        if data is None:
            return None
        return DescribeSeasonModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateSeasonModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    maximum_participants: int = None
    experience_model_id: str = None
    challenge_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateSeasonModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateSeasonModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateSeasonModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateSeasonModelMasterRequest:
        self.metadata = metadata
        return self

    def with_maximum_participants(self, maximum_participants: int) -> CreateSeasonModelMasterRequest:
        self.maximum_participants = maximum_participants
        return self

    def with_experience_model_id(self, experience_model_id: str) -> CreateSeasonModelMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> CreateSeasonModelMasterRequest:
        self.challenge_period_event_id = challenge_period_event_id
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
    ) -> Optional[CreateSeasonModelMasterRequest]:
        if data is None:
            return None
        return CreateSeasonModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_maximum_participants(data.get('maximumParticipants'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "maximumParticipants": self.maximum_participants,
            "experienceModelId": self.experience_model_id,
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class GetSeasonModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSeasonModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> GetSeasonModelMasterRequest:
        self.season_name = season_name
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
    ) -> Optional[GetSeasonModelMasterRequest]:
        if data is None:
            return None
        return GetSeasonModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
        }


class UpdateSeasonModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    description: str = None
    metadata: str = None
    maximum_participants: int = None
    experience_model_id: str = None
    challenge_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateSeasonModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> UpdateSeasonModelMasterRequest:
        self.season_name = season_name
        return self

    def with_description(self, description: str) -> UpdateSeasonModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateSeasonModelMasterRequest:
        self.metadata = metadata
        return self

    def with_maximum_participants(self, maximum_participants: int) -> UpdateSeasonModelMasterRequest:
        self.maximum_participants = maximum_participants
        return self

    def with_experience_model_id(self, experience_model_id: str) -> UpdateSeasonModelMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> UpdateSeasonModelMasterRequest:
        self.challenge_period_event_id = challenge_period_event_id
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
    ) -> Optional[UpdateSeasonModelMasterRequest]:
        if data is None:
            return None
        return UpdateSeasonModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_maximum_participants(data.get('maximumParticipants'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "description": self.description,
            "metadata": self.metadata,
            "maximumParticipants": self.maximum_participants,
            "experienceModelId": self.experience_model_id,
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class DeleteSeasonModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSeasonModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> DeleteSeasonModelMasterRequest:
        self.season_name = season_name
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
    ) -> Optional[DeleteSeasonModelMasterRequest]:
        if data is None:
            return None
        return DeleteSeasonModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
        }


class DescribeSeasonGatheringsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    season: int = None
    tier: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSeasonGatheringsRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> DescribeSeasonGatheringsRequest:
        self.season_name = season_name
        return self

    def with_season(self, season: int) -> DescribeSeasonGatheringsRequest:
        self.season = season
        return self

    def with_tier(self, tier: int) -> DescribeSeasonGatheringsRequest:
        self.tier = tier
        return self

    def with_page_token(self, page_token: str) -> DescribeSeasonGatheringsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSeasonGatheringsRequest:
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
    ) -> Optional[DescribeSeasonGatheringsRequest]:
        if data is None:
            return None
        return DescribeSeasonGatheringsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_season(data.get('season'))\
            .with_tier(data.get('tier'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "season": self.season,
            "tier": self.tier,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeMatchmakingSeasonGatheringsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    season: int = None
    tier: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMatchmakingSeasonGatheringsRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> DescribeMatchmakingSeasonGatheringsRequest:
        self.season_name = season_name
        return self

    def with_season(self, season: int) -> DescribeMatchmakingSeasonGatheringsRequest:
        self.season = season
        return self

    def with_tier(self, tier: int) -> DescribeMatchmakingSeasonGatheringsRequest:
        self.tier = tier
        return self

    def with_page_token(self, page_token: str) -> DescribeMatchmakingSeasonGatheringsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMatchmakingSeasonGatheringsRequest:
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
    ) -> Optional[DescribeMatchmakingSeasonGatheringsRequest]:
        if data is None:
            return None
        return DescribeMatchmakingSeasonGatheringsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_season(data.get('season'))\
            .with_tier(data.get('tier'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "season": self.season,
            "tier": self.tier,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DoSeasonMatchmakingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    access_token: str = None
    matchmaking_context_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DoSeasonMatchmakingRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> DoSeasonMatchmakingRequest:
        self.season_name = season_name
        return self

    def with_access_token(self, access_token: str) -> DoSeasonMatchmakingRequest:
        self.access_token = access_token
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoSeasonMatchmakingRequest:
        self.matchmaking_context_token = matchmaking_context_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DoSeasonMatchmakingRequest:
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
    ) -> Optional[DoSeasonMatchmakingRequest]:
        if data is None:
            return None
        return DoSeasonMatchmakingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_access_token(data.get('accessToken'))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "accessToken": self.access_token,
            "matchmakingContextToken": self.matchmaking_context_token,
        }


class DoSeasonMatchmakingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    user_id: str = None
    matchmaking_context_token: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DoSeasonMatchmakingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> DoSeasonMatchmakingByUserIdRequest:
        self.season_name = season_name
        return self

    def with_user_id(self, user_id: str) -> DoSeasonMatchmakingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_matchmaking_context_token(self, matchmaking_context_token: str) -> DoSeasonMatchmakingByUserIdRequest:
        self.matchmaking_context_token = matchmaking_context_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DoSeasonMatchmakingByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DoSeasonMatchmakingByUserIdRequest:
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
    ) -> Optional[DoSeasonMatchmakingByUserIdRequest]:
        if data is None:
            return None
        return DoSeasonMatchmakingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_user_id(data.get('userId'))\
            .with_matchmaking_context_token(data.get('matchmakingContextToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "userId": self.user_id,
            "matchmakingContextToken": self.matchmaking_context_token,
            "timeOffsetToken": self.time_offset_token,
        }


class GetSeasonGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    season: int = None
    tier: int = None
    season_gathering_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSeasonGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> GetSeasonGatheringRequest:
        self.season_name = season_name
        return self

    def with_season(self, season: int) -> GetSeasonGatheringRequest:
        self.season = season
        return self

    def with_tier(self, tier: int) -> GetSeasonGatheringRequest:
        self.tier = tier
        return self

    def with_season_gathering_name(self, season_gathering_name: str) -> GetSeasonGatheringRequest:
        self.season_gathering_name = season_gathering_name
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
    ) -> Optional[GetSeasonGatheringRequest]:
        if data is None:
            return None
        return GetSeasonGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_season(data.get('season'))\
            .with_tier(data.get('tier'))\
            .with_season_gathering_name(data.get('seasonGatheringName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "season": self.season,
            "tier": self.tier,
            "seasonGatheringName": self.season_gathering_name,
        }


class VerifyIncludeParticipantRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    season: int = None
    tier: int = None
    season_gathering_name: str = None
    access_token: str = None
    verify_type: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyIncludeParticipantRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> VerifyIncludeParticipantRequest:
        self.season_name = season_name
        return self

    def with_season(self, season: int) -> VerifyIncludeParticipantRequest:
        self.season = season
        return self

    def with_tier(self, tier: int) -> VerifyIncludeParticipantRequest:
        self.tier = tier
        return self

    def with_season_gathering_name(self, season_gathering_name: str) -> VerifyIncludeParticipantRequest:
        self.season_gathering_name = season_gathering_name
        return self

    def with_access_token(self, access_token: str) -> VerifyIncludeParticipantRequest:
        self.access_token = access_token
        return self

    def with_verify_type(self, verify_type: str) -> VerifyIncludeParticipantRequest:
        self.verify_type = verify_type
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyIncludeParticipantRequest:
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
    ) -> Optional[VerifyIncludeParticipantRequest]:
        if data is None:
            return None
        return VerifyIncludeParticipantRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_season(data.get('season'))\
            .with_tier(data.get('tier'))\
            .with_season_gathering_name(data.get('seasonGatheringName'))\
            .with_access_token(data.get('accessToken'))\
            .with_verify_type(data.get('verifyType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "season": self.season,
            "tier": self.tier,
            "seasonGatheringName": self.season_gathering_name,
            "accessToken": self.access_token,
            "verifyType": self.verify_type,
        }


class VerifyIncludeParticipantByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    season: int = None
    tier: int = None
    season_gathering_name: str = None
    user_id: str = None
    verify_type: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyIncludeParticipantByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> VerifyIncludeParticipantByUserIdRequest:
        self.season_name = season_name
        return self

    def with_season(self, season: int) -> VerifyIncludeParticipantByUserIdRequest:
        self.season = season
        return self

    def with_tier(self, tier: int) -> VerifyIncludeParticipantByUserIdRequest:
        self.tier = tier
        return self

    def with_season_gathering_name(self, season_gathering_name: str) -> VerifyIncludeParticipantByUserIdRequest:
        self.season_gathering_name = season_gathering_name
        return self

    def with_user_id(self, user_id: str) -> VerifyIncludeParticipantByUserIdRequest:
        self.user_id = user_id
        return self

    def with_verify_type(self, verify_type: str) -> VerifyIncludeParticipantByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyIncludeParticipantByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyIncludeParticipantByUserIdRequest:
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
    ) -> Optional[VerifyIncludeParticipantByUserIdRequest]:
        if data is None:
            return None
        return VerifyIncludeParticipantByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_season(data.get('season'))\
            .with_tier(data.get('tier'))\
            .with_season_gathering_name(data.get('seasonGatheringName'))\
            .with_user_id(data.get('userId'))\
            .with_verify_type(data.get('verifyType'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "season": self.season,
            "tier": self.tier,
            "seasonGatheringName": self.season_gathering_name,
            "userId": self.user_id,
            "verifyType": self.verify_type,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteSeasonGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    season: int = None
    tier: int = None
    season_gathering_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSeasonGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> DeleteSeasonGatheringRequest:
        self.season_name = season_name
        return self

    def with_season(self, season: int) -> DeleteSeasonGatheringRequest:
        self.season = season
        return self

    def with_tier(self, tier: int) -> DeleteSeasonGatheringRequest:
        self.tier = tier
        return self

    def with_season_gathering_name(self, season_gathering_name: str) -> DeleteSeasonGatheringRequest:
        self.season_gathering_name = season_gathering_name
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
    ) -> Optional[DeleteSeasonGatheringRequest]:
        if data is None:
            return None
        return DeleteSeasonGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_season_name(data.get('seasonName'))\
            .with_season(data.get('season'))\
            .with_tier(data.get('tier'))\
            .with_season_gathering_name(data.get('seasonGatheringName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "season": self.season,
            "tier": self.tier,
            "seasonGatheringName": self.season_gathering_name,
        }


class VerifyIncludeParticipantByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyIncludeParticipantByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyIncludeParticipantByStampTaskRequest:
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
    ) -> Optional[VerifyIncludeParticipantByStampTaskRequest]:
        if data is None:
            return None
        return VerifyIncludeParticipantByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeJoinedSeasonGatheringsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    season_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeJoinedSeasonGatheringsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeJoinedSeasonGatheringsRequest:
        self.access_token = access_token
        return self

    def with_season_name(self, season_name: str) -> DescribeJoinedSeasonGatheringsRequest:
        self.season_name = season_name
        return self

    def with_page_token(self, page_token: str) -> DescribeJoinedSeasonGatheringsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeJoinedSeasonGatheringsRequest:
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
    ) -> Optional[DescribeJoinedSeasonGatheringsRequest]:
        if data is None:
            return None
        return DescribeJoinedSeasonGatheringsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season_name(data.get('seasonName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "seasonName": self.season_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeJoinedSeasonGatheringsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    season_name: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeJoinedSeasonGatheringsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeJoinedSeasonGatheringsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season_name(self, season_name: str) -> DescribeJoinedSeasonGatheringsByUserIdRequest:
        self.season_name = season_name
        return self

    def with_page_token(self, page_token: str) -> DescribeJoinedSeasonGatheringsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeJoinedSeasonGatheringsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeJoinedSeasonGatheringsByUserIdRequest:
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
    ) -> Optional[DescribeJoinedSeasonGatheringsByUserIdRequest]:
        if data is None:
            return None
        return DescribeJoinedSeasonGatheringsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_season_name(data.get('seasonName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "seasonName": self.season_name,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetJoinedSeasonGatheringRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    season_name: str = None
    season: int = None

    def with_namespace_name(self, namespace_name: str) -> GetJoinedSeasonGatheringRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetJoinedSeasonGatheringRequest:
        self.access_token = access_token
        return self

    def with_season_name(self, season_name: str) -> GetJoinedSeasonGatheringRequest:
        self.season_name = season_name
        return self

    def with_season(self, season: int) -> GetJoinedSeasonGatheringRequest:
        self.season = season
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
    ) -> Optional[GetJoinedSeasonGatheringRequest]:
        if data is None:
            return None
        return GetJoinedSeasonGatheringRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season_name(data.get('seasonName'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "seasonName": self.season_name,
            "season": self.season,
        }


class GetJoinedSeasonGatheringByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    season_name: str = None
    season: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetJoinedSeasonGatheringByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetJoinedSeasonGatheringByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season_name(self, season_name: str) -> GetJoinedSeasonGatheringByUserIdRequest:
        self.season_name = season_name
        return self

    def with_season(self, season: int) -> GetJoinedSeasonGatheringByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetJoinedSeasonGatheringByUserIdRequest:
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
    ) -> Optional[GetJoinedSeasonGatheringByUserIdRequest]:
        if data is None:
            return None
        return GetJoinedSeasonGatheringByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_season_name(data.get('seasonName'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "seasonName": self.season_name,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeRatingsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRatingsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeRatingsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeRatingsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRatingsRequest:
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
    ) -> Optional[DescribeRatingsRequest]:
        if data is None:
            return None
        return DescribeRatingsRequest()\
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


class DescribeRatingsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRatingsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeRatingsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeRatingsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRatingsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeRatingsByUserIdRequest:
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
    ) -> Optional[DescribeRatingsByUserIdRequest]:
        if data is None:
            return None
        return DescribeRatingsByUserIdRequest()\
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


class GetRatingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    rating_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRatingRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetRatingRequest:
        self.access_token = access_token
        return self

    def with_rating_name(self, rating_name: str) -> GetRatingRequest:
        self.rating_name = rating_name
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
    ) -> Optional[GetRatingRequest]:
        if data is None:
            return None
        return GetRatingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_rating_name(data.get('ratingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "ratingName": self.rating_name,
        }


class GetRatingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    rating_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRatingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetRatingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_rating_name(self, rating_name: str) -> GetRatingByUserIdRequest:
        self.rating_name = rating_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetRatingByUserIdRequest:
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
    ) -> Optional[GetRatingByUserIdRequest]:
        if data is None:
            return None
        return GetRatingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_rating_name(data.get('ratingName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "ratingName": self.rating_name,
            "timeOffsetToken": self.time_offset_token,
        }


class PutResultRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    game_results: List[GameResult] = None

    def with_namespace_name(self, namespace_name: str) -> PutResultRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> PutResultRequest:
        self.rating_name = rating_name
        return self

    def with_game_results(self, game_results: List[GameResult]) -> PutResultRequest:
        self.game_results = game_results
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
    ) -> Optional[PutResultRequest]:
        if data is None:
            return None
        return PutResultRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_game_results(None if data.get('gameResults') is None else [
                GameResult.from_dict(data.get('gameResults')[i])
                for i in range(len(data.get('gameResults')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "gameResults": None if self.game_results is None else [
                self.game_results[i].to_dict() if self.game_results[i] else None
                for i in range(len(self.game_results))
            ],
        }


class DeleteRatingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    rating_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRatingRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteRatingRequest:
        self.user_id = user_id
        return self

    def with_rating_name(self, rating_name: str) -> DeleteRatingRequest:
        self.rating_name = rating_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteRatingRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteRatingRequest:
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
    ) -> Optional[DeleteRatingRequest]:
        if data is None:
            return None
        return DeleteRatingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_rating_name(data.get('ratingName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "ratingName": self.rating_name,
            "timeOffsetToken": self.time_offset_token,
        }


class GetBallotRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    gathering_name: str = None
    access_token: str = None
    number_of_player: int = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBallotRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> GetBallotRequest:
        self.rating_name = rating_name
        return self

    def with_gathering_name(self, gathering_name: str) -> GetBallotRequest:
        self.gathering_name = gathering_name
        return self

    def with_access_token(self, access_token: str) -> GetBallotRequest:
        self.access_token = access_token
        return self

    def with_number_of_player(self, number_of_player: int) -> GetBallotRequest:
        self.number_of_player = number_of_player
        return self

    def with_key_id(self, key_id: str) -> GetBallotRequest:
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
    ) -> Optional[GetBallotRequest]:
        if data is None:
            return None
        return GetBallotRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_access_token(data.get('accessToken'))\
            .with_number_of_player(data.get('numberOfPlayer'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "gatheringName": self.gathering_name,
            "accessToken": self.access_token,
            "numberOfPlayer": self.number_of_player,
            "keyId": self.key_id,
        }


class GetBallotByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    gathering_name: str = None
    user_id: str = None
    number_of_player: int = None
    key_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBallotByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> GetBallotByUserIdRequest:
        self.rating_name = rating_name
        return self

    def with_gathering_name(self, gathering_name: str) -> GetBallotByUserIdRequest:
        self.gathering_name = gathering_name
        return self

    def with_user_id(self, user_id: str) -> GetBallotByUserIdRequest:
        self.user_id = user_id
        return self

    def with_number_of_player(self, number_of_player: int) -> GetBallotByUserIdRequest:
        self.number_of_player = number_of_player
        return self

    def with_key_id(self, key_id: str) -> GetBallotByUserIdRequest:
        self.key_id = key_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetBallotByUserIdRequest:
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
    ) -> Optional[GetBallotByUserIdRequest]:
        if data is None:
            return None
        return GetBallotByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_gathering_name(data.get('gatheringName'))\
            .with_user_id(data.get('userId'))\
            .with_number_of_player(data.get('numberOfPlayer'))\
            .with_key_id(data.get('keyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "gatheringName": self.gathering_name,
            "userId": self.user_id,
            "numberOfPlayer": self.number_of_player,
            "keyId": self.key_id,
            "timeOffsetToken": self.time_offset_token,
        }


class VoteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ballot_body: str = None
    ballot_signature: str = None
    game_results: List[GameResult] = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> VoteRequest:
        self.namespace_name = namespace_name
        return self

    def with_ballot_body(self, ballot_body: str) -> VoteRequest:
        self.ballot_body = ballot_body
        return self

    def with_ballot_signature(self, ballot_signature: str) -> VoteRequest:
        self.ballot_signature = ballot_signature
        return self

    def with_game_results(self, game_results: List[GameResult]) -> VoteRequest:
        self.game_results = game_results
        return self

    def with_key_id(self, key_id: str) -> VoteRequest:
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
    ) -> Optional[VoteRequest]:
        if data is None:
            return None
        return VoteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ballot_body(data.get('ballotBody'))\
            .with_ballot_signature(data.get('ballotSignature'))\
            .with_game_results(None if data.get('gameResults') is None else [
                GameResult.from_dict(data.get('gameResults')[i])
                for i in range(len(data.get('gameResults')))
            ])\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ballotBody": self.ballot_body,
            "ballotSignature": self.ballot_signature,
            "gameResults": None if self.game_results is None else [
                self.game_results[i].to_dict() if self.game_results[i] else None
                for i in range(len(self.game_results))
            ],
            "keyId": self.key_id,
        }


class VoteMultipleRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    signed_ballots: List[SignedBallot] = None
    game_results: List[GameResult] = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> VoteMultipleRequest:
        self.namespace_name = namespace_name
        return self

    def with_signed_ballots(self, signed_ballots: List[SignedBallot]) -> VoteMultipleRequest:
        self.signed_ballots = signed_ballots
        return self

    def with_game_results(self, game_results: List[GameResult]) -> VoteMultipleRequest:
        self.game_results = game_results
        return self

    def with_key_id(self, key_id: str) -> VoteMultipleRequest:
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
    ) -> Optional[VoteMultipleRequest]:
        if data is None:
            return None
        return VoteMultipleRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_signed_ballots(None if data.get('signedBallots') is None else [
                SignedBallot.from_dict(data.get('signedBallots')[i])
                for i in range(len(data.get('signedBallots')))
            ])\
            .with_game_results(None if data.get('gameResults') is None else [
                GameResult.from_dict(data.get('gameResults')[i])
                for i in range(len(data.get('gameResults')))
            ])\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "signedBallots": None if self.signed_ballots is None else [
                self.signed_ballots[i].to_dict() if self.signed_ballots[i] else None
                for i in range(len(self.signed_ballots))
            ],
            "gameResults": None if self.game_results is None else [
                self.game_results[i].to_dict() if self.game_results[i] else None
                for i in range(len(self.game_results))
            ],
            "keyId": self.key_id,
        }


class CommitVoteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rating_name: str = None
    gathering_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CommitVoteRequest:
        self.namespace_name = namespace_name
        return self

    def with_rating_name(self, rating_name: str) -> CommitVoteRequest:
        self.rating_name = rating_name
        return self

    def with_gathering_name(self, gathering_name: str) -> CommitVoteRequest:
        self.gathering_name = gathering_name
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
    ) -> Optional[CommitVoteRequest]:
        if data is None:
            return None
        return CommitVoteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rating_name(data.get('ratingName'))\
            .with_gathering_name(data.get('gatheringName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "ratingName": self.rating_name,
            "gatheringName": self.gathering_name,
        }