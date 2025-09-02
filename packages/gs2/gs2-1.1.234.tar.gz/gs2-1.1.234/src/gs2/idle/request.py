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
    transaction_setting: TransactionSetting = None
    receive_script: ScriptSetting = None
    override_acquire_actions_script_id: str = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> CreateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_receive_script(self, receive_script: ScriptSetting) -> CreateNamespaceRequest:
        self.receive_script = receive_script
        return self

    def with_override_acquire_actions_script_id(self, override_acquire_actions_script_id: str) -> CreateNamespaceRequest:
        self.override_acquire_actions_script_id = override_acquire_actions_script_id
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
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_receive_script(ScriptSetting.from_dict(data.get('receiveScript')))\
            .with_override_acquire_actions_script_id(data.get('overrideAcquireActionsScriptId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "receiveScript": self.receive_script.to_dict() if self.receive_script else None,
            "overrideAcquireActionsScriptId": self.override_acquire_actions_script_id,
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
    transaction_setting: TransactionSetting = None
    receive_script: ScriptSetting = None
    override_acquire_actions_script_id: str = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> UpdateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_receive_script(self, receive_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.receive_script = receive_script
        return self

    def with_override_acquire_actions_script_id(self, override_acquire_actions_script_id: str) -> UpdateNamespaceRequest:
        self.override_acquire_actions_script_id = override_acquire_actions_script_id
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
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_receive_script(ScriptSetting.from_dict(data.get('receiveScript')))\
            .with_override_acquire_actions_script_id(data.get('overrideAcquireActionsScriptId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "receiveScript": self.receive_script.to_dict() if self.receive_script else None,
            "overrideAcquireActionsScriptId": self.override_acquire_actions_script_id,
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


class DescribeCategoryModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCategoryModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeCategoryModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCategoryModelMastersRequest:
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
    ) -> Optional[DescribeCategoryModelMastersRequest]:
        if data is None:
            return None
        return DescribeCategoryModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateCategoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    reward_interval_minutes: int = None
    default_maximum_idle_minutes: int = None
    reward_reset_mode: str = None
    acquire_actions: List[AcquireActionList] = None
    idle_period_schedule_id: str = None
    receive_period_schedule_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateCategoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateCategoryModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateCategoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateCategoryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_reward_interval_minutes(self, reward_interval_minutes: int) -> CreateCategoryModelMasterRequest:
        self.reward_interval_minutes = reward_interval_minutes
        return self

    def with_default_maximum_idle_minutes(self, default_maximum_idle_minutes: int) -> CreateCategoryModelMasterRequest:
        self.default_maximum_idle_minutes = default_maximum_idle_minutes
        return self

    def with_reward_reset_mode(self, reward_reset_mode: str) -> CreateCategoryModelMasterRequest:
        self.reward_reset_mode = reward_reset_mode
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireActionList]) -> CreateCategoryModelMasterRequest:
        self.acquire_actions = acquire_actions
        return self

    def with_idle_period_schedule_id(self, idle_period_schedule_id: str) -> CreateCategoryModelMasterRequest:
        self.idle_period_schedule_id = idle_period_schedule_id
        return self

    def with_receive_period_schedule_id(self, receive_period_schedule_id: str) -> CreateCategoryModelMasterRequest:
        self.receive_period_schedule_id = receive_period_schedule_id
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
    ) -> Optional[CreateCategoryModelMasterRequest]:
        if data is None:
            return None
        return CreateCategoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_reward_interval_minutes(data.get('rewardIntervalMinutes'))\
            .with_default_maximum_idle_minutes(data.get('defaultMaximumIdleMinutes'))\
            .with_reward_reset_mode(data.get('rewardResetMode'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireActionList.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_idle_period_schedule_id(data.get('idlePeriodScheduleId'))\
            .with_receive_period_schedule_id(data.get('receivePeriodScheduleId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "rewardIntervalMinutes": self.reward_interval_minutes,
            "defaultMaximumIdleMinutes": self.default_maximum_idle_minutes,
            "rewardResetMode": self.reward_reset_mode,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "idlePeriodScheduleId": self.idle_period_schedule_id,
            "receivePeriodScheduleId": self.receive_period_schedule_id,
        }


class GetCategoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCategoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetCategoryModelMasterRequest:
        self.category_name = category_name
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
    ) -> Optional[GetCategoryModelMasterRequest]:
        if data is None:
            return None
        return GetCategoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
        }


class UpdateCategoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None
    description: str = None
    metadata: str = None
    reward_interval_minutes: int = None
    default_maximum_idle_minutes: int = None
    reward_reset_mode: str = None
    acquire_actions: List[AcquireActionList] = None
    idle_period_schedule_id: str = None
    receive_period_schedule_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCategoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> UpdateCategoryModelMasterRequest:
        self.category_name = category_name
        return self

    def with_description(self, description: str) -> UpdateCategoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateCategoryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_reward_interval_minutes(self, reward_interval_minutes: int) -> UpdateCategoryModelMasterRequest:
        self.reward_interval_minutes = reward_interval_minutes
        return self

    def with_default_maximum_idle_minutes(self, default_maximum_idle_minutes: int) -> UpdateCategoryModelMasterRequest:
        self.default_maximum_idle_minutes = default_maximum_idle_minutes
        return self

    def with_reward_reset_mode(self, reward_reset_mode: str) -> UpdateCategoryModelMasterRequest:
        self.reward_reset_mode = reward_reset_mode
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireActionList]) -> UpdateCategoryModelMasterRequest:
        self.acquire_actions = acquire_actions
        return self

    def with_idle_period_schedule_id(self, idle_period_schedule_id: str) -> UpdateCategoryModelMasterRequest:
        self.idle_period_schedule_id = idle_period_schedule_id
        return self

    def with_receive_period_schedule_id(self, receive_period_schedule_id: str) -> UpdateCategoryModelMasterRequest:
        self.receive_period_schedule_id = receive_period_schedule_id
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
    ) -> Optional[UpdateCategoryModelMasterRequest]:
        if data is None:
            return None
        return UpdateCategoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_reward_interval_minutes(data.get('rewardIntervalMinutes'))\
            .with_default_maximum_idle_minutes(data.get('defaultMaximumIdleMinutes'))\
            .with_reward_reset_mode(data.get('rewardResetMode'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireActionList.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_idle_period_schedule_id(data.get('idlePeriodScheduleId'))\
            .with_receive_period_schedule_id(data.get('receivePeriodScheduleId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
            "description": self.description,
            "metadata": self.metadata,
            "rewardIntervalMinutes": self.reward_interval_minutes,
            "defaultMaximumIdleMinutes": self.default_maximum_idle_minutes,
            "rewardResetMode": self.reward_reset_mode,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "idlePeriodScheduleId": self.idle_period_schedule_id,
            "receivePeriodScheduleId": self.receive_period_schedule_id,
        }


class DeleteCategoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteCategoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> DeleteCategoryModelMasterRequest:
        self.category_name = category_name
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
    ) -> Optional[DeleteCategoryModelMasterRequest]:
        if data is None:
            return None
        return DeleteCategoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
        }


class DescribeCategoryModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCategoryModelsRequest:
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
    ) -> Optional[DescribeCategoryModelsRequest]:
        if data is None:
            return None
        return DescribeCategoryModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCategoryModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCategoryModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_category_name(self, category_name: str) -> GetCategoryModelRequest:
        self.category_name = category_name
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
    ) -> Optional[GetCategoryModelRequest]:
        if data is None:
            return None
        return GetCategoryModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "categoryName": self.category_name,
        }


class DescribeStatusesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStatusesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeStatusesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeStatusesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStatusesRequest:
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
    ) -> Optional[DescribeStatusesRequest]:
        if data is None:
            return None
        return DescribeStatusesRequest()\
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


class DescribeStatusesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStatusesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeStatusesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeStatusesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStatusesByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeStatusesByUserIdRequest:
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
    ) -> Optional[DescribeStatusesByUserIdRequest]:
        if data is None:
            return None
        return DescribeStatusesByUserIdRequest()\
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


class GetStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetStatusRequest:
        self.access_token = access_token
        return self

    def with_category_name(self, category_name: str) -> GetStatusRequest:
        self.category_name = category_name
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
    ) -> Optional[GetStatusRequest]:
        if data is None:
            return None
        return GetStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "categoryName": self.category_name,
        }


class GetStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    category_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_category_name(self, category_name: str) -> GetStatusByUserIdRequest:
        self.category_name = category_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetStatusByUserIdRequest:
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
    ) -> Optional[GetStatusByUserIdRequest]:
        if data is None:
            return None
        return GetStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_category_name(data.get('categoryName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "categoryName": self.category_name,
            "timeOffsetToken": self.time_offset_token,
        }


class PredictionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    category_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PredictionRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> PredictionRequest:
        self.access_token = access_token
        return self

    def with_category_name(self, category_name: str) -> PredictionRequest:
        self.category_name = category_name
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
    ) -> Optional[PredictionRequest]:
        if data is None:
            return None
        return PredictionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_category_name(data.get('categoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "categoryName": self.category_name,
        }


class PredictionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    category_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> PredictionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> PredictionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_category_name(self, category_name: str) -> PredictionByUserIdRequest:
        self.category_name = category_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PredictionByUserIdRequest:
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
    ) -> Optional[PredictionByUserIdRequest]:
        if data is None:
            return None
        return PredictionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_category_name(data.get('categoryName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "categoryName": self.category_name,
            "timeOffsetToken": self.time_offset_token,
        }


class ReceiveRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    category_name: str = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> ReceiveRequest:
        self.access_token = access_token
        return self

    def with_category_name(self, category_name: str) -> ReceiveRequest:
        self.category_name = category_name
        return self

    def with_config(self, config: List[Config]) -> ReceiveRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ReceiveRequest:
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
    ) -> Optional[ReceiveRequest]:
        if data is None:
            return None
        return ReceiveRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_category_name(data.get('categoryName'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "categoryName": self.category_name,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class ReceiveByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    category_name: str = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> ReceiveByUserIdRequest:
        self.user_id = user_id
        return self

    def with_category_name(self, category_name: str) -> ReceiveByUserIdRequest:
        self.category_name = category_name
        return self

    def with_config(self, config: List[Config]) -> ReceiveByUserIdRequest:
        self.config = config
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
            .with_user_id(data.get('userId'))\
            .with_category_name(data.get('categoryName'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "categoryName": self.category_name,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class IncreaseMaximumIdleMinutesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    category_name: str = None
    increase_minutes: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> IncreaseMaximumIdleMinutesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> IncreaseMaximumIdleMinutesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_category_name(self, category_name: str) -> IncreaseMaximumIdleMinutesByUserIdRequest:
        self.category_name = category_name
        return self

    def with_increase_minutes(self, increase_minutes: int) -> IncreaseMaximumIdleMinutesByUserIdRequest:
        self.increase_minutes = increase_minutes
        return self

    def with_time_offset_token(self, time_offset_token: str) -> IncreaseMaximumIdleMinutesByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> IncreaseMaximumIdleMinutesByUserIdRequest:
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
    ) -> Optional[IncreaseMaximumIdleMinutesByUserIdRequest]:
        if data is None:
            return None
        return IncreaseMaximumIdleMinutesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_category_name(data.get('categoryName'))\
            .with_increase_minutes(data.get('increaseMinutes'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "categoryName": self.category_name,
            "increaseMinutes": self.increase_minutes,
            "timeOffsetToken": self.time_offset_token,
        }


class DecreaseMaximumIdleMinutesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    category_name: str = None
    decrease_minutes: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DecreaseMaximumIdleMinutesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DecreaseMaximumIdleMinutesRequest:
        self.access_token = access_token
        return self

    def with_category_name(self, category_name: str) -> DecreaseMaximumIdleMinutesRequest:
        self.category_name = category_name
        return self

    def with_decrease_minutes(self, decrease_minutes: int) -> DecreaseMaximumIdleMinutesRequest:
        self.decrease_minutes = decrease_minutes
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DecreaseMaximumIdleMinutesRequest:
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
    ) -> Optional[DecreaseMaximumIdleMinutesRequest]:
        if data is None:
            return None
        return DecreaseMaximumIdleMinutesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_category_name(data.get('categoryName'))\
            .with_decrease_minutes(data.get('decreaseMinutes'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "categoryName": self.category_name,
            "decreaseMinutes": self.decrease_minutes,
        }


class DecreaseMaximumIdleMinutesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    category_name: str = None
    decrease_minutes: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DecreaseMaximumIdleMinutesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DecreaseMaximumIdleMinutesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_category_name(self, category_name: str) -> DecreaseMaximumIdleMinutesByUserIdRequest:
        self.category_name = category_name
        return self

    def with_decrease_minutes(self, decrease_minutes: int) -> DecreaseMaximumIdleMinutesByUserIdRequest:
        self.decrease_minutes = decrease_minutes
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DecreaseMaximumIdleMinutesByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DecreaseMaximumIdleMinutesByUserIdRequest:
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
    ) -> Optional[DecreaseMaximumIdleMinutesByUserIdRequest]:
        if data is None:
            return None
        return DecreaseMaximumIdleMinutesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_category_name(data.get('categoryName'))\
            .with_decrease_minutes(data.get('decreaseMinutes'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "categoryName": self.category_name,
            "decreaseMinutes": self.decrease_minutes,
            "timeOffsetToken": self.time_offset_token,
        }


class SetMaximumIdleMinutesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    category_name: str = None
    maximum_idle_minutes: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetMaximumIdleMinutesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SetMaximumIdleMinutesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_category_name(self, category_name: str) -> SetMaximumIdleMinutesByUserIdRequest:
        self.category_name = category_name
        return self

    def with_maximum_idle_minutes(self, maximum_idle_minutes: int) -> SetMaximumIdleMinutesByUserIdRequest:
        self.maximum_idle_minutes = maximum_idle_minutes
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetMaximumIdleMinutesByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetMaximumIdleMinutesByUserIdRequest:
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
    ) -> Optional[SetMaximumIdleMinutesByUserIdRequest]:
        if data is None:
            return None
        return SetMaximumIdleMinutesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_category_name(data.get('categoryName'))\
            .with_maximum_idle_minutes(data.get('maximumIdleMinutes'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "categoryName": self.category_name,
            "maximumIdleMinutes": self.maximum_idle_minutes,
            "timeOffsetToken": self.time_offset_token,
        }


class IncreaseMaximumIdleMinutesByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> IncreaseMaximumIdleMinutesByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> IncreaseMaximumIdleMinutesByStampSheetRequest:
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
    ) -> Optional[IncreaseMaximumIdleMinutesByStampSheetRequest]:
        if data is None:
            return None
        return IncreaseMaximumIdleMinutesByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DecreaseMaximumIdleMinutesByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> DecreaseMaximumIdleMinutesByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> DecreaseMaximumIdleMinutesByStampTaskRequest:
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
    ) -> Optional[DecreaseMaximumIdleMinutesByStampTaskRequest]:
        if data is None:
            return None
        return DecreaseMaximumIdleMinutesByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class SetMaximumIdleMinutesByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetMaximumIdleMinutesByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetMaximumIdleMinutesByStampSheetRequest:
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
    ) -> Optional[SetMaximumIdleMinutesByStampSheetRequest]:
        if data is None:
            return None
        return SetMaximumIdleMinutesByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class ReceiveByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> ReceiveByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> ReceiveByStampSheetRequest:
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
    ) -> Optional[ReceiveByStampSheetRequest]:
        if data is None:
            return None
        return ReceiveByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
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


class GetCurrentCategoryMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentCategoryMasterRequest:
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
    ) -> Optional[GetCurrentCategoryMasterRequest]:
        if data is None:
            return None
        return GetCurrentCategoryMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentCategoryMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentCategoryMasterRequest:
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
    ) -> Optional[PreUpdateCurrentCategoryMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentCategoryMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentCategoryMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentCategoryMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentCategoryMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentCategoryMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentCategoryMasterRequest:
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
    ) -> Optional[UpdateCurrentCategoryMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentCategoryMasterRequest()\
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


class UpdateCurrentCategoryMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentCategoryMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentCategoryMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentCategoryMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentCategoryMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }