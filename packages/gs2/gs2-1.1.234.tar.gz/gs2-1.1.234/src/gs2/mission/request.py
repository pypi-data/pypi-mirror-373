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


class DescribeCompletesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCompletesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeCompletesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeCompletesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCompletesRequest:
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
    ) -> Optional[DescribeCompletesRequest]:
        if data is None:
            return None
        return DescribeCompletesRequest()\
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


class DescribeCompletesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCompletesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeCompletesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeCompletesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCompletesByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeCompletesByUserIdRequest:
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
    ) -> Optional[DescribeCompletesByUserIdRequest]:
        if data is None:
            return None
        return DescribeCompletesByUserIdRequest()\
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


class CompleteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    mission_task_name: str = None
    access_token: str = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CompleteRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> CompleteRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_mission_task_name(self, mission_task_name: str) -> CompleteRequest:
        self.mission_task_name = mission_task_name
        return self

    def with_access_token(self, access_token: str) -> CompleteRequest:
        self.access_token = access_token
        return self

    def with_config(self, config: List[Config]) -> CompleteRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CompleteRequest:
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
    ) -> Optional[CompleteRequest]:
        if data is None:
            return None
        return CompleteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_mission_task_name(data.get('missionTaskName'))\
            .with_access_token(data.get('accessToken'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "missionTaskName": self.mission_task_name,
            "accessToken": self.access_token,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class CompleteByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    mission_task_name: str = None
    user_id: str = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CompleteByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> CompleteByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_mission_task_name(self, mission_task_name: str) -> CompleteByUserIdRequest:
        self.mission_task_name = mission_task_name
        return self

    def with_user_id(self, user_id: str) -> CompleteByUserIdRequest:
        self.user_id = user_id
        return self

    def with_config(self, config: List[Config]) -> CompleteByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CompleteByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CompleteByUserIdRequest:
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
    ) -> Optional[CompleteByUserIdRequest]:
        if data is None:
            return None
        return CompleteByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_mission_task_name(data.get('missionTaskName'))\
            .with_user_id(data.get('userId'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "missionTaskName": self.mission_task_name,
            "userId": self.user_id,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class BatchCompleteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    access_token: str = None
    mission_task_names: List[str] = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> BatchCompleteRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> BatchCompleteRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_access_token(self, access_token: str) -> BatchCompleteRequest:
        self.access_token = access_token
        return self

    def with_mission_task_names(self, mission_task_names: List[str]) -> BatchCompleteRequest:
        self.mission_task_names = mission_task_names
        return self

    def with_config(self, config: List[Config]) -> BatchCompleteRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> BatchCompleteRequest:
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
    ) -> Optional[BatchCompleteRequest]:
        if data is None:
            return None
        return BatchCompleteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mission_task_names(None if data.get('missionTaskNames') is None else [
                data.get('missionTaskNames')[i]
                for i in range(len(data.get('missionTaskNames')))
            ])\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "accessToken": self.access_token,
            "missionTaskNames": None if self.mission_task_names is None else [
                self.mission_task_names[i]
                for i in range(len(self.mission_task_names))
            ],
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class BatchCompleteByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    user_id: str = None
    mission_task_names: List[str] = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> BatchCompleteByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> BatchCompleteByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_user_id(self, user_id: str) -> BatchCompleteByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mission_task_names(self, mission_task_names: List[str]) -> BatchCompleteByUserIdRequest:
        self.mission_task_names = mission_task_names
        return self

    def with_config(self, config: List[Config]) -> BatchCompleteByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> BatchCompleteByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> BatchCompleteByUserIdRequest:
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
    ) -> Optional[BatchCompleteByUserIdRequest]:
        if data is None:
            return None
        return BatchCompleteByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_user_id(data.get('userId'))\
            .with_mission_task_names(None if data.get('missionTaskNames') is None else [
                data.get('missionTaskNames')[i]
                for i in range(len(data.get('missionTaskNames')))
            ])\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "userId": self.user_id,
            "missionTaskNames": None if self.mission_task_names is None else [
                self.mission_task_names[i]
                for i in range(len(self.mission_task_names))
            ],
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class ReceiveByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    mission_task_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> ReceiveByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_mission_task_name(self, mission_task_name: str) -> ReceiveByUserIdRequest:
        self.mission_task_name = mission_task_name
        return self

    def with_user_id(self, user_id: str) -> ReceiveByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ReceiveByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ReceiveByUserIdRequest:
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
    ) -> Optional[ReceiveByUserIdRequest]:
        if data is None:
            return None
        return ReceiveByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_mission_task_name(data.get('missionTaskName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "missionTaskName": self.mission_task_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class BatchReceiveByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    user_id: str = None
    mission_task_names: List[str] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> BatchReceiveByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> BatchReceiveByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_user_id(self, user_id: str) -> BatchReceiveByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mission_task_names(self, mission_task_names: List[str]) -> BatchReceiveByUserIdRequest:
        self.mission_task_names = mission_task_names
        return self

    def with_time_offset_token(self, time_offset_token: str) -> BatchReceiveByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> BatchReceiveByUserIdRequest:
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
    ) -> Optional[BatchReceiveByUserIdRequest]:
        if data is None:
            return None
        return BatchReceiveByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_user_id(data.get('userId'))\
            .with_mission_task_names(None if data.get('missionTaskNames') is None else [
                data.get('missionTaskNames')[i]
                for i in range(len(data.get('missionTaskNames')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "userId": self.user_id,
            "missionTaskNames": None if self.mission_task_names is None else [
                self.mission_task_names[i]
                for i in range(len(self.mission_task_names))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class RevertReceiveByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    mission_task_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RevertReceiveByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> RevertReceiveByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_mission_task_name(self, mission_task_name: str) -> RevertReceiveByUserIdRequest:
        self.mission_task_name = mission_task_name
        return self

    def with_user_id(self, user_id: str) -> RevertReceiveByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> RevertReceiveByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RevertReceiveByUserIdRequest:
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
    ) -> Optional[RevertReceiveByUserIdRequest]:
        if data is None:
            return None
        return RevertReceiveByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_mission_task_name(data.get('missionTaskName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "missionTaskName": self.mission_task_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetCompleteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCompleteRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> GetCompleteRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_access_token(self, access_token: str) -> GetCompleteRequest:
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
    ) -> Optional[GetCompleteRequest]:
        if data is None:
            return None
        return GetCompleteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "accessToken": self.access_token,
        }


class GetCompleteByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCompleteByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> GetCompleteByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_user_id(self, user_id: str) -> GetCompleteByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetCompleteByUserIdRequest:
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
    ) -> Optional[GetCompleteByUserIdRequest]:
        if data is None:
            return None
        return GetCompleteByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class EvaluateCompleteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mission_group_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> EvaluateCompleteRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> EvaluateCompleteRequest:
        self.access_token = access_token
        return self

    def with_mission_group_name(self, mission_group_name: str) -> EvaluateCompleteRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> EvaluateCompleteRequest:
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
    ) -> Optional[EvaluateCompleteRequest]:
        if data is None:
            return None
        return EvaluateCompleteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mission_group_name(data.get('missionGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "missionGroupName": self.mission_group_name,
        }


class EvaluateCompleteByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mission_group_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> EvaluateCompleteByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> EvaluateCompleteByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mission_group_name(self, mission_group_name: str) -> EvaluateCompleteByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> EvaluateCompleteByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> EvaluateCompleteByUserIdRequest:
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
    ) -> Optional[EvaluateCompleteByUserIdRequest]:
        if data is None:
            return None
        return EvaluateCompleteByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "missionGroupName": self.mission_group_name,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteCompleteByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mission_group_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteCompleteByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteCompleteByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mission_group_name(self, mission_group_name: str) -> DeleteCompleteByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteCompleteByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteCompleteByUserIdRequest:
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
    ) -> Optional[DeleteCompleteByUserIdRequest]:
        if data is None:
            return None
        return DeleteCompleteByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "missionGroupName": self.mission_group_name,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyCompleteRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    access_token: str = None
    verify_type: str = None
    mission_task_name: str = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyCompleteRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> VerifyCompleteRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_access_token(self, access_token: str) -> VerifyCompleteRequest:
        self.access_token = access_token
        return self

    def with_verify_type(self, verify_type: str) -> VerifyCompleteRequest:
        self.verify_type = verify_type
        return self

    def with_mission_task_name(self, mission_task_name: str) -> VerifyCompleteRequest:
        self.mission_task_name = mission_task_name
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyCompleteRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyCompleteRequest:
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
    ) -> Optional[VerifyCompleteRequest]:
        if data is None:
            return None
        return VerifyCompleteRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_access_token(data.get('accessToken'))\
            .with_verify_type(data.get('verifyType'))\
            .with_mission_task_name(data.get('missionTaskName'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "accessToken": self.access_token,
            "verifyType": self.verify_type,
            "missionTaskName": self.mission_task_name,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyCompleteByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    user_id: str = None
    verify_type: str = None
    mission_task_name: str = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyCompleteByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> VerifyCompleteByUserIdRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_user_id(self, user_id: str) -> VerifyCompleteByUserIdRequest:
        self.user_id = user_id
        return self

    def with_verify_type(self, verify_type: str) -> VerifyCompleteByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_mission_task_name(self, mission_task_name: str) -> VerifyCompleteByUserIdRequest:
        self.mission_task_name = mission_task_name
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyCompleteByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyCompleteByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyCompleteByUserIdRequest:
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
    ) -> Optional[VerifyCompleteByUserIdRequest]:
        if data is None:
            return None
        return VerifyCompleteByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_user_id(data.get('userId'))\
            .with_verify_type(data.get('verifyType'))\
            .with_mission_task_name(data.get('missionTaskName'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "userId": self.user_id,
            "verifyType": self.verify_type,
            "missionTaskName": self.mission_task_name,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class ReceiveByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> ReceiveByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> ReceiveByStampTaskRequest:
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
    ) -> Optional[ReceiveByStampTaskRequest]:
        if data is None:
            return None
        return ReceiveByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class BatchReceiveByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> BatchReceiveByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> BatchReceiveByStampTaskRequest:
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
    ) -> Optional[BatchReceiveByStampTaskRequest]:
        if data is None:
            return None
        return BatchReceiveByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class RevertReceiveByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RevertReceiveByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RevertReceiveByStampSheetRequest:
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
    ) -> Optional[RevertReceiveByStampSheetRequest]:
        if data is None:
            return None
        return RevertReceiveByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class VerifyCompleteByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyCompleteByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyCompleteByStampTaskRequest:
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
    ) -> Optional[VerifyCompleteByStampTaskRequest]:
        if data is None:
            return None
        return VerifyCompleteByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeCounterModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCounterModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeCounterModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCounterModelMastersRequest:
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
    ) -> Optional[DescribeCounterModelMastersRequest]:
        if data is None:
            return None
        return DescribeCounterModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateCounterModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    metadata: str = None
    description: str = None
    scopes: List[CounterScopeModel] = None
    challenge_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateCounterModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateCounterModelMasterRequest:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CreateCounterModelMasterRequest:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> CreateCounterModelMasterRequest:
        self.description = description
        return self

    def with_scopes(self, scopes: List[CounterScopeModel]) -> CreateCounterModelMasterRequest:
        self.scopes = scopes
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> CreateCounterModelMasterRequest:
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
    ) -> Optional[CreateCounterModelMasterRequest]:
        if data is None:
            return None
        return CreateCounterModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_scopes(None if data.get('scopes') is None else [
                CounterScopeModel.from_dict(data.get('scopes')[i])
                for i in range(len(data.get('scopes')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "scopes": None if self.scopes is None else [
                self.scopes[i].to_dict() if self.scopes[i] else None
                for i in range(len(self.scopes))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class GetCounterModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCounterModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> GetCounterModelMasterRequest:
        self.counter_name = counter_name
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
    ) -> Optional[GetCounterModelMasterRequest]:
        if data is None:
            return None
        return GetCounterModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
        }


class UpdateCounterModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None
    metadata: str = None
    description: str = None
    scopes: List[CounterScopeModel] = None
    challenge_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCounterModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> UpdateCounterModelMasterRequest:
        self.counter_name = counter_name
        return self

    def with_metadata(self, metadata: str) -> UpdateCounterModelMasterRequest:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> UpdateCounterModelMasterRequest:
        self.description = description
        return self

    def with_scopes(self, scopes: List[CounterScopeModel]) -> UpdateCounterModelMasterRequest:
        self.scopes = scopes
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> UpdateCounterModelMasterRequest:
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
    ) -> Optional[UpdateCounterModelMasterRequest]:
        if data is None:
            return None
        return UpdateCounterModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_scopes(None if data.get('scopes') is None else [
                CounterScopeModel.from_dict(data.get('scopes')[i])
                for i in range(len(data.get('scopes')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
            "metadata": self.metadata,
            "description": self.description,
            "scopes": None if self.scopes is None else [
                self.scopes[i].to_dict() if self.scopes[i] else None
                for i in range(len(self.scopes))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class DeleteCounterModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteCounterModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> DeleteCounterModelMasterRequest:
        self.counter_name = counter_name
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
    ) -> Optional[DeleteCounterModelMasterRequest]:
        if data is None:
            return None
        return DeleteCounterModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
        }


class DescribeMissionGroupModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMissionGroupModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeMissionGroupModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMissionGroupModelMastersRequest:
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
    ) -> Optional[DescribeMissionGroupModelMastersRequest]:
        if data is None:
            return None
        return DescribeMissionGroupModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateMissionGroupModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    metadata: str = None
    description: str = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None
    anchor_timestamp: int = None
    days: int = None
    complete_notification_namespace_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateMissionGroupModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateMissionGroupModelMasterRequest:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CreateMissionGroupModelMasterRequest:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> CreateMissionGroupModelMasterRequest:
        self.description = description
        return self

    def with_reset_type(self, reset_type: str) -> CreateMissionGroupModelMasterRequest:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> CreateMissionGroupModelMasterRequest:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> CreateMissionGroupModelMasterRequest:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> CreateMissionGroupModelMasterRequest:
        self.reset_hour = reset_hour
        return self

    def with_anchor_timestamp(self, anchor_timestamp: int) -> CreateMissionGroupModelMasterRequest:
        self.anchor_timestamp = anchor_timestamp
        return self

    def with_days(self, days: int) -> CreateMissionGroupModelMasterRequest:
        self.days = days
        return self

    def with_complete_notification_namespace_id(self, complete_notification_namespace_id: str) -> CreateMissionGroupModelMasterRequest:
        self.complete_notification_namespace_id = complete_notification_namespace_id
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
    ) -> Optional[CreateMissionGroupModelMasterRequest]:
        if data is None:
            return None
        return CreateMissionGroupModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_anchor_timestamp(data.get('anchorTimestamp'))\
            .with_days(data.get('days'))\
            .with_complete_notification_namespace_id(data.get('completeNotificationNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
            "anchorTimestamp": self.anchor_timestamp,
            "days": self.days,
            "completeNotificationNamespaceId": self.complete_notification_namespace_id,
        }


class GetMissionGroupModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMissionGroupModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> GetMissionGroupModelMasterRequest:
        self.mission_group_name = mission_group_name
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
    ) -> Optional[GetMissionGroupModelMasterRequest]:
        if data is None:
            return None
        return GetMissionGroupModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
        }


class UpdateMissionGroupModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    metadata: str = None
    description: str = None
    reset_type: str = None
    reset_day_of_month: int = None
    reset_day_of_week: str = None
    reset_hour: int = None
    anchor_timestamp: int = None
    days: int = None
    complete_notification_namespace_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateMissionGroupModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> UpdateMissionGroupModelMasterRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_metadata(self, metadata: str) -> UpdateMissionGroupModelMasterRequest:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> UpdateMissionGroupModelMasterRequest:
        self.description = description
        return self

    def with_reset_type(self, reset_type: str) -> UpdateMissionGroupModelMasterRequest:
        self.reset_type = reset_type
        return self

    def with_reset_day_of_month(self, reset_day_of_month: int) -> UpdateMissionGroupModelMasterRequest:
        self.reset_day_of_month = reset_day_of_month
        return self

    def with_reset_day_of_week(self, reset_day_of_week: str) -> UpdateMissionGroupModelMasterRequest:
        self.reset_day_of_week = reset_day_of_week
        return self

    def with_reset_hour(self, reset_hour: int) -> UpdateMissionGroupModelMasterRequest:
        self.reset_hour = reset_hour
        return self

    def with_anchor_timestamp(self, anchor_timestamp: int) -> UpdateMissionGroupModelMasterRequest:
        self.anchor_timestamp = anchor_timestamp
        return self

    def with_days(self, days: int) -> UpdateMissionGroupModelMasterRequest:
        self.days = days
        return self

    def with_complete_notification_namespace_id(self, complete_notification_namespace_id: str) -> UpdateMissionGroupModelMasterRequest:
        self.complete_notification_namespace_id = complete_notification_namespace_id
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
    ) -> Optional[UpdateMissionGroupModelMasterRequest]:
        if data is None:
            return None
        return UpdateMissionGroupModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_reset_type(data.get('resetType'))\
            .with_reset_day_of_month(data.get('resetDayOfMonth'))\
            .with_reset_day_of_week(data.get('resetDayOfWeek'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_anchor_timestamp(data.get('anchorTimestamp'))\
            .with_days(data.get('days'))\
            .with_complete_notification_namespace_id(data.get('completeNotificationNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "metadata": self.metadata,
            "description": self.description,
            "resetType": self.reset_type,
            "resetDayOfMonth": self.reset_day_of_month,
            "resetDayOfWeek": self.reset_day_of_week,
            "resetHour": self.reset_hour,
            "anchorTimestamp": self.anchor_timestamp,
            "days": self.days,
            "completeNotificationNamespaceId": self.complete_notification_namespace_id,
        }


class DeleteMissionGroupModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMissionGroupModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> DeleteMissionGroupModelMasterRequest:
        self.mission_group_name = mission_group_name
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
    ) -> Optional[DeleteMissionGroupModelMasterRequest]:
        if data is None:
            return None
        return DeleteMissionGroupModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
        }


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
    transaction_setting: TransactionSetting = None
    mission_complete_script: ScriptSetting = None
    counter_increment_script: ScriptSetting = None
    receive_rewards_script: ScriptSetting = None
    complete_notification: NotificationSetting = None
    log_setting: LogSetting = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> CreateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_mission_complete_script(self, mission_complete_script: ScriptSetting) -> CreateNamespaceRequest:
        self.mission_complete_script = mission_complete_script
        return self

    def with_counter_increment_script(self, counter_increment_script: ScriptSetting) -> CreateNamespaceRequest:
        self.counter_increment_script = counter_increment_script
        return self

    def with_receive_rewards_script(self, receive_rewards_script: ScriptSetting) -> CreateNamespaceRequest:
        self.receive_rewards_script = receive_rewards_script
        return self

    def with_complete_notification(self, complete_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.complete_notification = complete_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> CreateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> CreateNamespaceRequest:
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
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_mission_complete_script(ScriptSetting.from_dict(data.get('missionCompleteScript')))\
            .with_counter_increment_script(ScriptSetting.from_dict(data.get('counterIncrementScript')))\
            .with_receive_rewards_script(ScriptSetting.from_dict(data.get('receiveRewardsScript')))\
            .with_complete_notification(NotificationSetting.from_dict(data.get('completeNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "missionCompleteScript": self.mission_complete_script.to_dict() if self.mission_complete_script else None,
            "counterIncrementScript": self.counter_increment_script.to_dict() if self.counter_increment_script else None,
            "receiveRewardsScript": self.receive_rewards_script.to_dict() if self.receive_rewards_script else None,
            "completeNotification": self.complete_notification.to_dict() if self.complete_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
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
    transaction_setting: TransactionSetting = None
    mission_complete_script: ScriptSetting = None
    counter_increment_script: ScriptSetting = None
    receive_rewards_script: ScriptSetting = None
    complete_notification: NotificationSetting = None
    log_setting: LogSetting = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> UpdateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_mission_complete_script(self, mission_complete_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.mission_complete_script = mission_complete_script
        return self

    def with_counter_increment_script(self, counter_increment_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.counter_increment_script = counter_increment_script
        return self

    def with_receive_rewards_script(self, receive_rewards_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.receive_rewards_script = receive_rewards_script
        return self

    def with_complete_notification(self, complete_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.complete_notification = complete_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> UpdateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> UpdateNamespaceRequest:
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
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_mission_complete_script(ScriptSetting.from_dict(data.get('missionCompleteScript')))\
            .with_counter_increment_script(ScriptSetting.from_dict(data.get('counterIncrementScript')))\
            .with_receive_rewards_script(ScriptSetting.from_dict(data.get('receiveRewardsScript')))\
            .with_complete_notification(NotificationSetting.from_dict(data.get('completeNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "missionCompleteScript": self.mission_complete_script.to_dict() if self.mission_complete_script else None,
            "counterIncrementScript": self.counter_increment_script.to_dict() if self.counter_increment_script else None,
            "receiveRewardsScript": self.receive_rewards_script.to_dict() if self.receive_rewards_script else None,
            "completeNotification": self.complete_notification.to_dict() if self.complete_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
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


class DescribeCountersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCountersRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeCountersRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeCountersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCountersRequest:
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
    ) -> Optional[DescribeCountersRequest]:
        if data is None:
            return None
        return DescribeCountersRequest()\
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


class DescribeCountersByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCountersByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeCountersByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeCountersByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCountersByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeCountersByUserIdRequest:
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
    ) -> Optional[DescribeCountersByUserIdRequest]:
        if data is None:
            return None
        return DescribeCountersByUserIdRequest()\
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


class IncreaseCounterByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None
    user_id: str = None
    value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> IncreaseCounterByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> IncreaseCounterByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_user_id(self, user_id: str) -> IncreaseCounterByUserIdRequest:
        self.user_id = user_id
        return self

    def with_value(self, value: int) -> IncreaseCounterByUserIdRequest:
        self.value = value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> IncreaseCounterByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> IncreaseCounterByUserIdRequest:
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
    ) -> Optional[IncreaseCounterByUserIdRequest]:
        if data is None:
            return None
        return IncreaseCounterByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))\
            .with_user_id(data.get('userId'))\
            .with_value(data.get('value'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
            "userId": self.user_id,
            "value": self.value,
            "timeOffsetToken": self.time_offset_token,
        }


class SetCounterByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None
    user_id: str = None
    values: List[ScopedValue] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetCounterByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> SetCounterByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_user_id(self, user_id: str) -> SetCounterByUserIdRequest:
        self.user_id = user_id
        return self

    def with_values(self, values: List[ScopedValue]) -> SetCounterByUserIdRequest:
        self.values = values
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetCounterByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetCounterByUserIdRequest:
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
    ) -> Optional[SetCounterByUserIdRequest]:
        if data is None:
            return None
        return SetCounterByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))\
            .with_user_id(data.get('userId'))\
            .with_values(None if data.get('values') is None else [
                ScopedValue.from_dict(data.get('values')[i])
                for i in range(len(data.get('values')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
            "userId": self.user_id,
            "values": None if self.values is None else [
                self.values[i].to_dict() if self.values[i] else None
                for i in range(len(self.values))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DecreaseCounterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None
    access_token: str = None
    value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DecreaseCounterRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> DecreaseCounterRequest:
        self.counter_name = counter_name
        return self

    def with_access_token(self, access_token: str) -> DecreaseCounterRequest:
        self.access_token = access_token
        return self

    def with_value(self, value: int) -> DecreaseCounterRequest:
        self.value = value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DecreaseCounterRequest:
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
    ) -> Optional[DecreaseCounterRequest]:
        if data is None:
            return None
        return DecreaseCounterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))\
            .with_access_token(data.get('accessToken'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
            "accessToken": self.access_token,
            "value": self.value,
        }


class DecreaseCounterByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None
    user_id: str = None
    value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DecreaseCounterByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> DecreaseCounterByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_user_id(self, user_id: str) -> DecreaseCounterByUserIdRequest:
        self.user_id = user_id
        return self

    def with_value(self, value: int) -> DecreaseCounterByUserIdRequest:
        self.value = value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DecreaseCounterByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DecreaseCounterByUserIdRequest:
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
    ) -> Optional[DecreaseCounterByUserIdRequest]:
        if data is None:
            return None
        return DecreaseCounterByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))\
            .with_user_id(data.get('userId'))\
            .with_value(data.get('value'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
            "userId": self.user_id,
            "value": self.value,
            "timeOffsetToken": self.time_offset_token,
        }


class GetCounterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCounterRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> GetCounterRequest:
        self.counter_name = counter_name
        return self

    def with_access_token(self, access_token: str) -> GetCounterRequest:
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
    ) -> Optional[GetCounterRequest]:
        if data is None:
            return None
        return GetCounterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
            "accessToken": self.access_token,
        }


class GetCounterByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCounterByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> GetCounterByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_user_id(self, user_id: str) -> GetCounterByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetCounterByUserIdRequest:
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
    ) -> Optional[GetCounterByUserIdRequest]:
        if data is None:
            return None
        return GetCounterByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyCounterValueRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    counter_name: str = None
    verify_type: str = None
    scope_type: str = None
    reset_type: str = None
    condition_name: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyCounterValueRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyCounterValueRequest:
        self.access_token = access_token
        return self

    def with_counter_name(self, counter_name: str) -> VerifyCounterValueRequest:
        self.counter_name = counter_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyCounterValueRequest:
        self.verify_type = verify_type
        return self

    def with_scope_type(self, scope_type: str) -> VerifyCounterValueRequest:
        self.scope_type = scope_type
        return self

    def with_reset_type(self, reset_type: str) -> VerifyCounterValueRequest:
        self.reset_type = reset_type
        return self

    def with_condition_name(self, condition_name: str) -> VerifyCounterValueRequest:
        self.condition_name = condition_name
        return self

    def with_value(self, value: int) -> VerifyCounterValueRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyCounterValueRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyCounterValueRequest:
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
    ) -> Optional[VerifyCounterValueRequest]:
        if data is None:
            return None
        return VerifyCounterValueRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_counter_name(data.get('counterName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_scope_type(data.get('scopeType'))\
            .with_reset_type(data.get('resetType'))\
            .with_condition_name(data.get('conditionName'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "counterName": self.counter_name,
            "verifyType": self.verify_type,
            "scopeType": self.scope_type,
            "resetType": self.reset_type,
            "conditionName": self.condition_name,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyCounterValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    counter_name: str = None
    verify_type: str = None
    scope_type: str = None
    reset_type: str = None
    condition_name: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyCounterValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyCounterValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_counter_name(self, counter_name: str) -> VerifyCounterValueByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyCounterValueByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_scope_type(self, scope_type: str) -> VerifyCounterValueByUserIdRequest:
        self.scope_type = scope_type
        return self

    def with_reset_type(self, reset_type: str) -> VerifyCounterValueByUserIdRequest:
        self.reset_type = reset_type
        return self

    def with_condition_name(self, condition_name: str) -> VerifyCounterValueByUserIdRequest:
        self.condition_name = condition_name
        return self

    def with_value(self, value: int) -> VerifyCounterValueByUserIdRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyCounterValueByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyCounterValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyCounterValueByUserIdRequest:
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
    ) -> Optional[VerifyCounterValueByUserIdRequest]:
        if data is None:
            return None
        return VerifyCounterValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_counter_name(data.get('counterName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_scope_type(data.get('scopeType'))\
            .with_reset_type(data.get('resetType'))\
            .with_condition_name(data.get('conditionName'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "counterName": self.counter_name,
            "verifyType": self.verify_type,
            "scopeType": self.scope_type,
            "resetType": self.reset_type,
            "conditionName": self.condition_name,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class ResetCounterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    counter_name: str = None
    scopes: List[ScopedValue] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ResetCounterRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> ResetCounterRequest:
        self.access_token = access_token
        return self

    def with_counter_name(self, counter_name: str) -> ResetCounterRequest:
        self.counter_name = counter_name
        return self

    def with_scopes(self, scopes: List[ScopedValue]) -> ResetCounterRequest:
        self.scopes = scopes
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ResetCounterRequest:
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
    ) -> Optional[ResetCounterRequest]:
        if data is None:
            return None
        return ResetCounterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_counter_name(data.get('counterName'))\
            .with_scopes(None if data.get('scopes') is None else [
                ScopedValue.from_dict(data.get('scopes')[i])
                for i in range(len(data.get('scopes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "counterName": self.counter_name,
            "scopes": None if self.scopes is None else [
                self.scopes[i].to_dict() if self.scopes[i] else None
                for i in range(len(self.scopes))
            ],
        }


class ResetCounterByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    counter_name: str = None
    scopes: List[ScopedValue] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ResetCounterByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> ResetCounterByUserIdRequest:
        self.user_id = user_id
        return self

    def with_counter_name(self, counter_name: str) -> ResetCounterByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_scopes(self, scopes: List[ScopedValue]) -> ResetCounterByUserIdRequest:
        self.scopes = scopes
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ResetCounterByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ResetCounterByUserIdRequest:
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
    ) -> Optional[ResetCounterByUserIdRequest]:
        if data is None:
            return None
        return ResetCounterByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_counter_name(data.get('counterName'))\
            .with_scopes(None if data.get('scopes') is None else [
                ScopedValue.from_dict(data.get('scopes')[i])
                for i in range(len(data.get('scopes')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "counterName": self.counter_name,
            "scopes": None if self.scopes is None else [
                self.scopes[i].to_dict() if self.scopes[i] else None
                for i in range(len(self.scopes))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteCounterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    counter_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteCounterRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteCounterRequest:
        self.access_token = access_token
        return self

    def with_counter_name(self, counter_name: str) -> DeleteCounterRequest:
        self.counter_name = counter_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteCounterRequest:
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
    ) -> Optional[DeleteCounterRequest]:
        if data is None:
            return None
        return DeleteCounterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_counter_name(data.get('counterName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "counterName": self.counter_name,
        }


class DeleteCounterByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    counter_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteCounterByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteCounterByUserIdRequest:
        self.user_id = user_id
        return self

    def with_counter_name(self, counter_name: str) -> DeleteCounterByUserIdRequest:
        self.counter_name = counter_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteCounterByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteCounterByUserIdRequest:
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
    ) -> Optional[DeleteCounterByUserIdRequest]:
        if data is None:
            return None
        return DeleteCounterByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_counter_name(data.get('counterName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "counterName": self.counter_name,
            "timeOffsetToken": self.time_offset_token,
        }


class IncreaseByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> IncreaseByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> IncreaseByStampSheetRequest:
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
    ) -> Optional[IncreaseByStampSheetRequest]:
        if data is None:
            return None
        return IncreaseByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetByStampSheetRequest:
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
    ) -> Optional[SetByStampSheetRequest]:
        if data is None:
            return None
        return SetByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DecreaseByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> DecreaseByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> DecreaseByStampTaskRequest:
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
    ) -> Optional[DecreaseByStampTaskRequest]:
        if data is None:
            return None
        return DecreaseByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class ResetByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> ResetByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> ResetByStampTaskRequest:
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
    ) -> Optional[ResetByStampTaskRequest]:
        if data is None:
            return None
        return ResetByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyCounterValueByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyCounterValueByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyCounterValueByStampTaskRequest:
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
    ) -> Optional[VerifyCounterValueByStampTaskRequest]:
        if data is None:
            return None
        return VerifyCounterValueByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
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


class GetCurrentMissionMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentMissionMasterRequest:
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
    ) -> Optional[GetCurrentMissionMasterRequest]:
        if data is None:
            return None
        return GetCurrentMissionMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentMissionMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentMissionMasterRequest:
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
    ) -> Optional[PreUpdateCurrentMissionMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentMissionMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentMissionMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentMissionMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentMissionMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentMissionMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentMissionMasterRequest:
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
    ) -> Optional[UpdateCurrentMissionMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentMissionMasterRequest()\
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


class UpdateCurrentMissionMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentMissionMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentMissionMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentMissionMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentMissionMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeCounterModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCounterModelsRequest:
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
    ) -> Optional[DescribeCounterModelsRequest]:
        if data is None:
            return None
        return DescribeCounterModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCounterModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    counter_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCounterModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_counter_name(self, counter_name: str) -> GetCounterModelRequest:
        self.counter_name = counter_name
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
    ) -> Optional[GetCounterModelRequest]:
        if data is None:
            return None
        return GetCounterModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_counter_name(data.get('counterName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "counterName": self.counter_name,
        }


class DescribeMissionGroupModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMissionGroupModelsRequest:
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
    ) -> Optional[DescribeMissionGroupModelsRequest]:
        if data is None:
            return None
        return DescribeMissionGroupModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetMissionGroupModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMissionGroupModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> GetMissionGroupModelRequest:
        self.mission_group_name = mission_group_name
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
    ) -> Optional[GetMissionGroupModelRequest]:
        if data is None:
            return None
        return GetMissionGroupModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
        }


class DescribeMissionTaskModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMissionTaskModelsRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> DescribeMissionTaskModelsRequest:
        self.mission_group_name = mission_group_name
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
    ) -> Optional[DescribeMissionTaskModelsRequest]:
        if data is None:
            return None
        return DescribeMissionTaskModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
        }


class GetMissionTaskModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    mission_task_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMissionTaskModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> GetMissionTaskModelRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_mission_task_name(self, mission_task_name: str) -> GetMissionTaskModelRequest:
        self.mission_task_name = mission_task_name
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
    ) -> Optional[GetMissionTaskModelRequest]:
        if data is None:
            return None
        return GetMissionTaskModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_mission_task_name(data.get('missionTaskName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "missionTaskName": self.mission_task_name,
        }


class DescribeMissionTaskModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMissionTaskModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> DescribeMissionTaskModelMastersRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_page_token(self, page_token: str) -> DescribeMissionTaskModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMissionTaskModelMastersRequest:
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
    ) -> Optional[DescribeMissionTaskModelMastersRequest]:
        if data is None:
            return None
        return DescribeMissionTaskModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateMissionTaskModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    name: str = None
    metadata: str = None
    description: str = None
    verify_complete_type: str = None
    target_counter: TargetCounterModel = None
    verify_complete_consume_actions: List[VerifyAction] = None
    complete_acquire_actions: List[AcquireAction] = None
    challenge_period_event_id: str = None
    premise_mission_task_name: str = None
    counter_name: str = None
    target_reset_type: str = None
    target_value: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateMissionTaskModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> CreateMissionTaskModelMasterRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_name(self, name: str) -> CreateMissionTaskModelMasterRequest:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> CreateMissionTaskModelMasterRequest:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> CreateMissionTaskModelMasterRequest:
        self.description = description
        return self

    def with_verify_complete_type(self, verify_complete_type: str) -> CreateMissionTaskModelMasterRequest:
        self.verify_complete_type = verify_complete_type
        return self

    def with_target_counter(self, target_counter: TargetCounterModel) -> CreateMissionTaskModelMasterRequest:
        self.target_counter = target_counter
        return self

    def with_verify_complete_consume_actions(self, verify_complete_consume_actions: List[VerifyAction]) -> CreateMissionTaskModelMasterRequest:
        self.verify_complete_consume_actions = verify_complete_consume_actions
        return self

    def with_complete_acquire_actions(self, complete_acquire_actions: List[AcquireAction]) -> CreateMissionTaskModelMasterRequest:
        self.complete_acquire_actions = complete_acquire_actions
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> CreateMissionTaskModelMasterRequest:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_premise_mission_task_name(self, premise_mission_task_name: str) -> CreateMissionTaskModelMasterRequest:
        self.premise_mission_task_name = premise_mission_task_name
        return self

    def with_counter_name(self, counter_name: str) -> CreateMissionTaskModelMasterRequest:
        self.counter_name = counter_name
        return self

    def with_target_reset_type(self, target_reset_type: str) -> CreateMissionTaskModelMasterRequest:
        self.target_reset_type = target_reset_type
        return self

    def with_target_value(self, target_value: int) -> CreateMissionTaskModelMasterRequest:
        self.target_value = target_value
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
    ) -> Optional[CreateMissionTaskModelMasterRequest]:
        if data is None:
            return None
        return CreateMissionTaskModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_verify_complete_type(data.get('verifyCompleteType'))\
            .with_target_counter(TargetCounterModel.from_dict(data.get('targetCounter')))\
            .with_verify_complete_consume_actions(None if data.get('verifyCompleteConsumeActions') is None else [
                VerifyAction.from_dict(data.get('verifyCompleteConsumeActions')[i])
                for i in range(len(data.get('verifyCompleteConsumeActions')))
            ])\
            .with_complete_acquire_actions(None if data.get('completeAcquireActions') is None else [
                AcquireAction.from_dict(data.get('completeAcquireActions')[i])
                for i in range(len(data.get('completeAcquireActions')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_premise_mission_task_name(data.get('premiseMissionTaskName'))\
            .with_counter_name(data.get('counterName'))\
            .with_target_reset_type(data.get('targetResetType'))\
            .with_target_value(data.get('targetValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "verifyCompleteType": self.verify_complete_type,
            "targetCounter": self.target_counter.to_dict() if self.target_counter else None,
            "verifyCompleteConsumeActions": None if self.verify_complete_consume_actions is None else [
                self.verify_complete_consume_actions[i].to_dict() if self.verify_complete_consume_actions[i] else None
                for i in range(len(self.verify_complete_consume_actions))
            ],
            "completeAcquireActions": None if self.complete_acquire_actions is None else [
                self.complete_acquire_actions[i].to_dict() if self.complete_acquire_actions[i] else None
                for i in range(len(self.complete_acquire_actions))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "premiseMissionTaskName": self.premise_mission_task_name,
            "counterName": self.counter_name,
            "targetResetType": self.target_reset_type,
            "targetValue": self.target_value,
        }


class GetMissionTaskModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    mission_task_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMissionTaskModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> GetMissionTaskModelMasterRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_mission_task_name(self, mission_task_name: str) -> GetMissionTaskModelMasterRequest:
        self.mission_task_name = mission_task_name
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
    ) -> Optional[GetMissionTaskModelMasterRequest]:
        if data is None:
            return None
        return GetMissionTaskModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_mission_task_name(data.get('missionTaskName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "missionTaskName": self.mission_task_name,
        }


class UpdateMissionTaskModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    mission_task_name: str = None
    metadata: str = None
    description: str = None
    verify_complete_type: str = None
    target_counter: TargetCounterModel = None
    verify_complete_consume_actions: List[VerifyAction] = None
    complete_acquire_actions: List[AcquireAction] = None
    challenge_period_event_id: str = None
    premise_mission_task_name: str = None
    counter_name: str = None
    target_reset_type: str = None
    target_value: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateMissionTaskModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> UpdateMissionTaskModelMasterRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_mission_task_name(self, mission_task_name: str) -> UpdateMissionTaskModelMasterRequest:
        self.mission_task_name = mission_task_name
        return self

    def with_metadata(self, metadata: str) -> UpdateMissionTaskModelMasterRequest:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> UpdateMissionTaskModelMasterRequest:
        self.description = description
        return self

    def with_verify_complete_type(self, verify_complete_type: str) -> UpdateMissionTaskModelMasterRequest:
        self.verify_complete_type = verify_complete_type
        return self

    def with_target_counter(self, target_counter: TargetCounterModel) -> UpdateMissionTaskModelMasterRequest:
        self.target_counter = target_counter
        return self

    def with_verify_complete_consume_actions(self, verify_complete_consume_actions: List[VerifyAction]) -> UpdateMissionTaskModelMasterRequest:
        self.verify_complete_consume_actions = verify_complete_consume_actions
        return self

    def with_complete_acquire_actions(self, complete_acquire_actions: List[AcquireAction]) -> UpdateMissionTaskModelMasterRequest:
        self.complete_acquire_actions = complete_acquire_actions
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> UpdateMissionTaskModelMasterRequest:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_premise_mission_task_name(self, premise_mission_task_name: str) -> UpdateMissionTaskModelMasterRequest:
        self.premise_mission_task_name = premise_mission_task_name
        return self

    def with_counter_name(self, counter_name: str) -> UpdateMissionTaskModelMasterRequest:
        self.counter_name = counter_name
        return self

    def with_target_reset_type(self, target_reset_type: str) -> UpdateMissionTaskModelMasterRequest:
        self.target_reset_type = target_reset_type
        return self

    def with_target_value(self, target_value: int) -> UpdateMissionTaskModelMasterRequest:
        self.target_value = target_value
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
    ) -> Optional[UpdateMissionTaskModelMasterRequest]:
        if data is None:
            return None
        return UpdateMissionTaskModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_mission_task_name(data.get('missionTaskName'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_verify_complete_type(data.get('verifyCompleteType'))\
            .with_target_counter(TargetCounterModel.from_dict(data.get('targetCounter')))\
            .with_verify_complete_consume_actions(None if data.get('verifyCompleteConsumeActions') is None else [
                VerifyAction.from_dict(data.get('verifyCompleteConsumeActions')[i])
                for i in range(len(data.get('verifyCompleteConsumeActions')))
            ])\
            .with_complete_acquire_actions(None if data.get('completeAcquireActions') is None else [
                AcquireAction.from_dict(data.get('completeAcquireActions')[i])
                for i in range(len(data.get('completeAcquireActions')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_premise_mission_task_name(data.get('premiseMissionTaskName'))\
            .with_counter_name(data.get('counterName'))\
            .with_target_reset_type(data.get('targetResetType'))\
            .with_target_value(data.get('targetValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "missionTaskName": self.mission_task_name,
            "metadata": self.metadata,
            "description": self.description,
            "verifyCompleteType": self.verify_complete_type,
            "targetCounter": self.target_counter.to_dict() if self.target_counter else None,
            "verifyCompleteConsumeActions": None if self.verify_complete_consume_actions is None else [
                self.verify_complete_consume_actions[i].to_dict() if self.verify_complete_consume_actions[i] else None
                for i in range(len(self.verify_complete_consume_actions))
            ],
            "completeAcquireActions": None if self.complete_acquire_actions is None else [
                self.complete_acquire_actions[i].to_dict() if self.complete_acquire_actions[i] else None
                for i in range(len(self.complete_acquire_actions))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "premiseMissionTaskName": self.premise_mission_task_name,
            "counterName": self.counter_name,
            "targetResetType": self.target_reset_type,
            "targetValue": self.target_value,
        }


class DeleteMissionTaskModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mission_group_name: str = None
    mission_task_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMissionTaskModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mission_group_name(self, mission_group_name: str) -> DeleteMissionTaskModelMasterRequest:
        self.mission_group_name = mission_group_name
        return self

    def with_mission_task_name(self, mission_task_name: str) -> DeleteMissionTaskModelMasterRequest:
        self.mission_task_name = mission_task_name
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
    ) -> Optional[DeleteMissionTaskModelMasterRequest]:
        if data is None:
            return None
        return DeleteMissionTaskModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mission_group_name(data.get('missionGroupName'))\
            .with_mission_task_name(data.get('missionTaskName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "missionGroupName": self.mission_group_name,
            "missionTaskName": self.mission_task_name,
        }