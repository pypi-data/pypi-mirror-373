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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "receiveScript": self.receive_script.to_dict() if self.receive_script else None,
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "receiveScript": self.receive_script.to_dict() if self.receive_script else None,
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


class DescribeBonusModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBonusModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeBonusModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBonusModelMastersRequest:
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
    ) -> Optional[DescribeBonusModelMastersRequest]:
        if data is None:
            return None
        return DescribeBonusModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateBonusModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    mode: str = None
    period_event_id: str = None
    reset_hour: int = None
    repeat: str = None
    rewards: List[Reward] = None
    missed_receive_relief: str = None
    missed_receive_relief_verify_actions: List[VerifyAction] = None
    missed_receive_relief_consume_actions: List[ConsumeAction] = None

    def with_namespace_name(self, namespace_name: str) -> CreateBonusModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateBonusModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateBonusModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateBonusModelMasterRequest:
        self.metadata = metadata
        return self

    def with_mode(self, mode: str) -> CreateBonusModelMasterRequest:
        self.mode = mode
        return self

    def with_period_event_id(self, period_event_id: str) -> CreateBonusModelMasterRequest:
        self.period_event_id = period_event_id
        return self

    def with_reset_hour(self, reset_hour: int) -> CreateBonusModelMasterRequest:
        self.reset_hour = reset_hour
        return self

    def with_repeat(self, repeat: str) -> CreateBonusModelMasterRequest:
        self.repeat = repeat
        return self

    def with_rewards(self, rewards: List[Reward]) -> CreateBonusModelMasterRequest:
        self.rewards = rewards
        return self

    def with_missed_receive_relief(self, missed_receive_relief: str) -> CreateBonusModelMasterRequest:
        self.missed_receive_relief = missed_receive_relief
        return self

    def with_missed_receive_relief_verify_actions(self, missed_receive_relief_verify_actions: List[VerifyAction]) -> CreateBonusModelMasterRequest:
        self.missed_receive_relief_verify_actions = missed_receive_relief_verify_actions
        return self

    def with_missed_receive_relief_consume_actions(self, missed_receive_relief_consume_actions: List[ConsumeAction]) -> CreateBonusModelMasterRequest:
        self.missed_receive_relief_consume_actions = missed_receive_relief_consume_actions
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateBonusModelMasterRequest]:
        if data is None:
            return None
        return CreateBonusModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_mode(data.get('mode'))\
            .with_period_event_id(data.get('periodEventId'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_repeat(data.get('repeat'))\
            .with_rewards(None if data.get('rewards') is None else [
                Reward.from_dict(data.get('rewards')[i])
                for i in range(len(data.get('rewards')))
            ])\
            .with_missed_receive_relief(data.get('missedReceiveRelief'))\
            .with_missed_receive_relief_verify_actions(None if data.get('missedReceiveReliefVerifyActions') is None else [
                VerifyAction.from_dict(data.get('missedReceiveReliefVerifyActions')[i])
                for i in range(len(data.get('missedReceiveReliefVerifyActions')))
            ])\
            .with_missed_receive_relief_consume_actions(None if data.get('missedReceiveReliefConsumeActions') is None else [
                ConsumeAction.from_dict(data.get('missedReceiveReliefConsumeActions')[i])
                for i in range(len(data.get('missedReceiveReliefConsumeActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "mode": self.mode,
            "periodEventId": self.period_event_id,
            "resetHour": self.reset_hour,
            "repeat": self.repeat,
            "rewards": None if self.rewards is None else [
                self.rewards[i].to_dict() if self.rewards[i] else None
                for i in range(len(self.rewards))
            ],
            "missedReceiveRelief": self.missed_receive_relief,
            "missedReceiveReliefVerifyActions": None if self.missed_receive_relief_verify_actions is None else [
                self.missed_receive_relief_verify_actions[i].to_dict() if self.missed_receive_relief_verify_actions[i] else None
                for i in range(len(self.missed_receive_relief_verify_actions))
            ],
            "missedReceiveReliefConsumeActions": None if self.missed_receive_relief_consume_actions is None else [
                self.missed_receive_relief_consume_actions[i].to_dict() if self.missed_receive_relief_consume_actions[i] else None
                for i in range(len(self.missed_receive_relief_consume_actions))
            ],
        }


class GetBonusModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBonusModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> GetBonusModelMasterRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetBonusModelMasterRequest]:
        if data is None:
            return None
        return GetBonusModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
        }


class UpdateBonusModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    description: str = None
    metadata: str = None
    mode: str = None
    period_event_id: str = None
    reset_hour: int = None
    repeat: str = None
    rewards: List[Reward] = None
    missed_receive_relief: str = None
    missed_receive_relief_verify_actions: List[VerifyAction] = None
    missed_receive_relief_consume_actions: List[ConsumeAction] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateBonusModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> UpdateBonusModelMasterRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_description(self, description: str) -> UpdateBonusModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateBonusModelMasterRequest:
        self.metadata = metadata
        return self

    def with_mode(self, mode: str) -> UpdateBonusModelMasterRequest:
        self.mode = mode
        return self

    def with_period_event_id(self, period_event_id: str) -> UpdateBonusModelMasterRequest:
        self.period_event_id = period_event_id
        return self

    def with_reset_hour(self, reset_hour: int) -> UpdateBonusModelMasterRequest:
        self.reset_hour = reset_hour
        return self

    def with_repeat(self, repeat: str) -> UpdateBonusModelMasterRequest:
        self.repeat = repeat
        return self

    def with_rewards(self, rewards: List[Reward]) -> UpdateBonusModelMasterRequest:
        self.rewards = rewards
        return self

    def with_missed_receive_relief(self, missed_receive_relief: str) -> UpdateBonusModelMasterRequest:
        self.missed_receive_relief = missed_receive_relief
        return self

    def with_missed_receive_relief_verify_actions(self, missed_receive_relief_verify_actions: List[VerifyAction]) -> UpdateBonusModelMasterRequest:
        self.missed_receive_relief_verify_actions = missed_receive_relief_verify_actions
        return self

    def with_missed_receive_relief_consume_actions(self, missed_receive_relief_consume_actions: List[ConsumeAction]) -> UpdateBonusModelMasterRequest:
        self.missed_receive_relief_consume_actions = missed_receive_relief_consume_actions
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateBonusModelMasterRequest]:
        if data is None:
            return None
        return UpdateBonusModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_mode(data.get('mode'))\
            .with_period_event_id(data.get('periodEventId'))\
            .with_reset_hour(data.get('resetHour'))\
            .with_repeat(data.get('repeat'))\
            .with_rewards(None if data.get('rewards') is None else [
                Reward.from_dict(data.get('rewards')[i])
                for i in range(len(data.get('rewards')))
            ])\
            .with_missed_receive_relief(data.get('missedReceiveRelief'))\
            .with_missed_receive_relief_verify_actions(None if data.get('missedReceiveReliefVerifyActions') is None else [
                VerifyAction.from_dict(data.get('missedReceiveReliefVerifyActions')[i])
                for i in range(len(data.get('missedReceiveReliefVerifyActions')))
            ])\
            .with_missed_receive_relief_consume_actions(None if data.get('missedReceiveReliefConsumeActions') is None else [
                ConsumeAction.from_dict(data.get('missedReceiveReliefConsumeActions')[i])
                for i in range(len(data.get('missedReceiveReliefConsumeActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "description": self.description,
            "metadata": self.metadata,
            "mode": self.mode,
            "periodEventId": self.period_event_id,
            "resetHour": self.reset_hour,
            "repeat": self.repeat,
            "rewards": None if self.rewards is None else [
                self.rewards[i].to_dict() if self.rewards[i] else None
                for i in range(len(self.rewards))
            ],
            "missedReceiveRelief": self.missed_receive_relief,
            "missedReceiveReliefVerifyActions": None if self.missed_receive_relief_verify_actions is None else [
                self.missed_receive_relief_verify_actions[i].to_dict() if self.missed_receive_relief_verify_actions[i] else None
                for i in range(len(self.missed_receive_relief_verify_actions))
            ],
            "missedReceiveReliefConsumeActions": None if self.missed_receive_relief_consume_actions is None else [
                self.missed_receive_relief_consume_actions[i].to_dict() if self.missed_receive_relief_consume_actions[i] else None
                for i in range(len(self.missed_receive_relief_consume_actions))
            ],
        }


class DeleteBonusModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteBonusModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> DeleteBonusModelMasterRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteBonusModelMasterRequest]:
        if data is None:
            return None
        return DeleteBonusModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
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


class GetCurrentBonusMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentBonusMasterRequest:
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
    ) -> Optional[GetCurrentBonusMasterRequest]:
        if data is None:
            return None
        return GetCurrentBonusMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentBonusMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentBonusMasterRequest:
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
    ) -> Optional[PreUpdateCurrentBonusMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentBonusMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentBonusMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentBonusMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentBonusMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentBonusMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentBonusMasterRequest:
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
    ) -> Optional[UpdateCurrentBonusMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentBonusMasterRequest()\
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


class UpdateCurrentBonusMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentBonusMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentBonusMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentBonusMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentBonusMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeBonusModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBonusModelsRequest:
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
    ) -> Optional[DescribeBonusModelsRequest]:
        if data is None:
            return None
        return DescribeBonusModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetBonusModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBonusModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> GetBonusModelRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetBonusModelRequest]:
        if data is None:
            return None
        return GetBonusModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
        }


class ReceiveRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    access_token: str = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> ReceiveRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_access_token(self, access_token: str) -> ReceiveRequest:
        self.access_token = access_token
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
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "accessToken": self.access_token,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class ReceiveByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    user_id: str = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> ReceiveByUserIdRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_user_id(self, user_id: str) -> ReceiveByUserIdRequest:
        self.user_id = user_id
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
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_user_id(data.get('userId'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "userId": self.user_id,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class MissedReceiveRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    access_token: str = None
    step_number: int = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> MissedReceiveRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> MissedReceiveRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_access_token(self, access_token: str) -> MissedReceiveRequest:
        self.access_token = access_token
        return self

    def with_step_number(self, step_number: int) -> MissedReceiveRequest:
        self.step_number = step_number
        return self

    def with_config(self, config: List[Config]) -> MissedReceiveRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> MissedReceiveRequest:
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
    ) -> Optional[MissedReceiveRequest]:
        if data is None:
            return None
        return MissedReceiveRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_step_number(data.get('stepNumber'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "accessToken": self.access_token,
            "stepNumber": self.step_number,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class MissedReceiveByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    user_id: str = None
    step_number: int = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> MissedReceiveByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> MissedReceiveByUserIdRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_user_id(self, user_id: str) -> MissedReceiveByUserIdRequest:
        self.user_id = user_id
        return self

    def with_step_number(self, step_number: int) -> MissedReceiveByUserIdRequest:
        self.step_number = step_number
        return self

    def with_config(self, config: List[Config]) -> MissedReceiveByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> MissedReceiveByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> MissedReceiveByUserIdRequest:
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
    ) -> Optional[MissedReceiveByUserIdRequest]:
        if data is None:
            return None
        return MissedReceiveByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_user_id(data.get('userId'))\
            .with_step_number(data.get('stepNumber'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "userId": self.user_id,
            "stepNumber": self.step_number,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeReceiveStatusesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReceiveStatusesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeReceiveStatusesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeReceiveStatusesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeReceiveStatusesRequest:
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
    ) -> Optional[DescribeReceiveStatusesRequest]:
        if data is None:
            return None
        return DescribeReceiveStatusesRequest()\
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


class DescribeReceiveStatusesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReceiveStatusesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeReceiveStatusesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeReceiveStatusesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeReceiveStatusesByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeReceiveStatusesByUserIdRequest:
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
    ) -> Optional[DescribeReceiveStatusesByUserIdRequest]:
        if data is None:
            return None
        return DescribeReceiveStatusesByUserIdRequest()\
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


class GetReceiveStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReceiveStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> GetReceiveStatusRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_access_token(self, access_token: str) -> GetReceiveStatusRequest:
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
    ) -> Optional[GetReceiveStatusRequest]:
        if data is None:
            return None
        return GetReceiveStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "accessToken": self.access_token,
        }


class GetReceiveStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReceiveStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> GetReceiveStatusByUserIdRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_user_id(self, user_id: str) -> GetReceiveStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetReceiveStatusByUserIdRequest:
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
    ) -> Optional[GetReceiveStatusByUserIdRequest]:
        if data is None:
            return None
        return GetReceiveStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteReceiveStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteReceiveStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> DeleteReceiveStatusByUserIdRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_user_id(self, user_id: str) -> DeleteReceiveStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteReceiveStatusByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteReceiveStatusByUserIdRequest:
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
    ) -> Optional[DeleteReceiveStatusByUserIdRequest]:
        if data is None:
            return None
        return DeleteReceiveStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteReceiveStatusByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> DeleteReceiveStatusByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> DeleteReceiveStatusByStampSheetRequest:
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
    ) -> Optional[DeleteReceiveStatusByStampSheetRequest]:
        if data is None:
            return None
        return DeleteReceiveStatusByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class MarkReceivedRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    access_token: str = None
    step_number: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> MarkReceivedRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> MarkReceivedRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_access_token(self, access_token: str) -> MarkReceivedRequest:
        self.access_token = access_token
        return self

    def with_step_number(self, step_number: int) -> MarkReceivedRequest:
        self.step_number = step_number
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> MarkReceivedRequest:
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
    ) -> Optional[MarkReceivedRequest]:
        if data is None:
            return None
        return MarkReceivedRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_step_number(data.get('stepNumber'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "accessToken": self.access_token,
            "stepNumber": self.step_number,
        }


class MarkReceivedByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    user_id: str = None
    step_number: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> MarkReceivedByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> MarkReceivedByUserIdRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_user_id(self, user_id: str) -> MarkReceivedByUserIdRequest:
        self.user_id = user_id
        return self

    def with_step_number(self, step_number: int) -> MarkReceivedByUserIdRequest:
        self.step_number = step_number
        return self

    def with_time_offset_token(self, time_offset_token: str) -> MarkReceivedByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> MarkReceivedByUserIdRequest:
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
    ) -> Optional[MarkReceivedByUserIdRequest]:
        if data is None:
            return None
        return MarkReceivedByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_user_id(data.get('userId'))\
            .with_step_number(data.get('stepNumber'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "userId": self.user_id,
            "stepNumber": self.step_number,
            "timeOffsetToken": self.time_offset_token,
        }


class UnmarkReceivedByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    bonus_model_name: str = None
    user_id: str = None
    step_number: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnmarkReceivedByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_bonus_model_name(self, bonus_model_name: str) -> UnmarkReceivedByUserIdRequest:
        self.bonus_model_name = bonus_model_name
        return self

    def with_user_id(self, user_id: str) -> UnmarkReceivedByUserIdRequest:
        self.user_id = user_id
        return self

    def with_step_number(self, step_number: int) -> UnmarkReceivedByUserIdRequest:
        self.step_number = step_number
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UnmarkReceivedByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnmarkReceivedByUserIdRequest:
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
    ) -> Optional[UnmarkReceivedByUserIdRequest]:
        if data is None:
            return None
        return UnmarkReceivedByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_bonus_model_name(data.get('bonusModelName'))\
            .with_user_id(data.get('userId'))\
            .with_step_number(data.get('stepNumber'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "bonusModelName": self.bonus_model_name,
            "userId": self.user_id,
            "stepNumber": self.step_number,
            "timeOffsetToken": self.time_offset_token,
        }


class MarkReceivedByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> MarkReceivedByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> MarkReceivedByStampTaskRequest:
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
    ) -> Optional[MarkReceivedByStampTaskRequest]:
        if data is None:
            return None
        return MarkReceivedByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class UnmarkReceivedByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> UnmarkReceivedByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> UnmarkReceivedByStampSheetRequest:
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
    ) -> Optional[UnmarkReceivedByStampSheetRequest]:
        if data is None:
            return None
        return UnmarkReceivedByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }