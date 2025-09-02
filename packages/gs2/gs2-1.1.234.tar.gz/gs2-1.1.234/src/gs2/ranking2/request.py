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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
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


class DescribeGlobalRankingModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalRankingModelsRequest:
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
    ) -> Optional[DescribeGlobalRankingModelsRequest]:
        if data is None:
            return None
        return DescribeGlobalRankingModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetGlobalRankingModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalRankingModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetGlobalRankingModelRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGlobalRankingModelRequest]:
        if data is None:
            return None
        return GetGlobalRankingModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class DescribeGlobalRankingModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalRankingModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeGlobalRankingModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGlobalRankingModelMastersRequest:
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
    ) -> Optional[DescribeGlobalRankingModelMastersRequest]:
        if data is None:
            return None
        return DescribeGlobalRankingModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateGlobalRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    ranking_rewards: List[RankingReward] = None
    reward_calculation_index: str = None
    entry_period_event_id: str = None
    access_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGlobalRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateGlobalRankingModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateGlobalRankingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateGlobalRankingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> CreateGlobalRankingModelMasterRequest:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> CreateGlobalRankingModelMasterRequest:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> CreateGlobalRankingModelMasterRequest:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> CreateGlobalRankingModelMasterRequest:
        self.order_direction = order_direction
        return self

    def with_ranking_rewards(self, ranking_rewards: List[RankingReward]) -> CreateGlobalRankingModelMasterRequest:
        self.ranking_rewards = ranking_rewards
        return self

    def with_reward_calculation_index(self, reward_calculation_index: str) -> CreateGlobalRankingModelMasterRequest:
        self.reward_calculation_index = reward_calculation_index
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> CreateGlobalRankingModelMasterRequest:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> CreateGlobalRankingModelMasterRequest:
        self.access_period_event_id = access_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGlobalRankingModelMasterRequest]:
        if data is None:
            return None
        return CreateGlobalRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_ranking_rewards(None if data.get('rankingRewards') is None else [
                RankingReward.from_dict(data.get('rankingRewards')[i])
                for i in range(len(data.get('rankingRewards')))
            ])\
            .with_reward_calculation_index(data.get('rewardCalculationIndex'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "rankingRewards": None if self.ranking_rewards is None else [
                self.ranking_rewards[i].to_dict() if self.ranking_rewards[i] else None
                for i in range(len(self.ranking_rewards))
            ],
            "rewardCalculationIndex": self.reward_calculation_index,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
        }


class GetGlobalRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetGlobalRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGlobalRankingModelMasterRequest]:
        if data is None:
            return None
        return GetGlobalRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class UpdateGlobalRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    description: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    ranking_rewards: List[RankingReward] = None
    reward_calculation_index: str = None
    entry_period_event_id: str = None
    access_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGlobalRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> UpdateGlobalRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def with_description(self, description: str) -> UpdateGlobalRankingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateGlobalRankingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> UpdateGlobalRankingModelMasterRequest:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> UpdateGlobalRankingModelMasterRequest:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> UpdateGlobalRankingModelMasterRequest:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> UpdateGlobalRankingModelMasterRequest:
        self.order_direction = order_direction
        return self

    def with_ranking_rewards(self, ranking_rewards: List[RankingReward]) -> UpdateGlobalRankingModelMasterRequest:
        self.ranking_rewards = ranking_rewards
        return self

    def with_reward_calculation_index(self, reward_calculation_index: str) -> UpdateGlobalRankingModelMasterRequest:
        self.reward_calculation_index = reward_calculation_index
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> UpdateGlobalRankingModelMasterRequest:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> UpdateGlobalRankingModelMasterRequest:
        self.access_period_event_id = access_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGlobalRankingModelMasterRequest]:
        if data is None:
            return None
        return UpdateGlobalRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_ranking_rewards(None if data.get('rankingRewards') is None else [
                RankingReward.from_dict(data.get('rankingRewards')[i])
                for i in range(len(data.get('rankingRewards')))
            ])\
            .with_reward_calculation_index(data.get('rewardCalculationIndex'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "description": self.description,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "rankingRewards": None if self.ranking_rewards is None else [
                self.ranking_rewards[i].to_dict() if self.ranking_rewards[i] else None
                for i in range(len(self.ranking_rewards))
            ],
            "rewardCalculationIndex": self.reward_calculation_index,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
        }


class DeleteGlobalRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGlobalRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteGlobalRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGlobalRankingModelMasterRequest]:
        if data is None:
            return None
        return DeleteGlobalRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class DescribeGlobalRankingScoresRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalRankingScoresRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeGlobalRankingScoresRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeGlobalRankingScoresRequest:
        self.ranking_name = ranking_name
        return self

    def with_page_token(self, page_token: str) -> DescribeGlobalRankingScoresRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGlobalRankingScoresRequest:
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
    ) -> Optional[DescribeGlobalRankingScoresRequest]:
        if data is None:
            return None
        return DescribeGlobalRankingScoresRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeGlobalRankingScoresByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalRankingScoresByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeGlobalRankingScoresByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeGlobalRankingScoresByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_page_token(self, page_token: str) -> DescribeGlobalRankingScoresByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGlobalRankingScoresByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeGlobalRankingScoresByUserIdRequest:
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
    ) -> Optional[DescribeGlobalRankingScoresByUserIdRequest]:
        if data is None:
            return None
        return DescribeGlobalRankingScoresByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class PutGlobalRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    score: int = None
    metadata: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutGlobalRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> PutGlobalRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> PutGlobalRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_score(self, score: int) -> PutGlobalRankingScoreRequest:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> PutGlobalRankingScoreRequest:
        self.metadata = metadata
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutGlobalRankingScoreRequest:
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
    ) -> Optional[PutGlobalRankingScoreRequest]:
        if data is None:
            return None
        return PutGlobalRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "score": self.score,
            "metadata": self.metadata,
        }


class PutGlobalRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    score: int = None
    metadata: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutGlobalRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> PutGlobalRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> PutGlobalRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_score(self, score: int) -> PutGlobalRankingScoreByUserIdRequest:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> PutGlobalRankingScoreByUserIdRequest:
        self.metadata = metadata
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PutGlobalRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutGlobalRankingScoreByUserIdRequest:
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
    ) -> Optional[PutGlobalRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return PutGlobalRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "score": self.score,
            "metadata": self.metadata,
            "timeOffsetToken": self.time_offset_token,
        }


class GetGlobalRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    season: int = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetGlobalRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> GetGlobalRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> GetGlobalRankingScoreRequest:
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
    ) -> Optional[GetGlobalRankingScoreRequest]:
        if data is None:
            return None
        return GetGlobalRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class GetGlobalRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetGlobalRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> GetGlobalRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GetGlobalRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetGlobalRankingScoreByUserIdRequest:
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
    ) -> Optional[GetGlobalRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return GetGlobalRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteGlobalRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGlobalRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteGlobalRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> DeleteGlobalRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> DeleteGlobalRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteGlobalRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteGlobalRankingScoreByUserIdRequest:
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
    ) -> Optional[DeleteGlobalRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return DeleteGlobalRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyGlobalRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    verify_type: str = None
    season: int = None
    score: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyGlobalRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyGlobalRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> VerifyGlobalRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyGlobalRankingScoreRequest:
        self.verify_type = verify_type
        return self

    def with_season(self, season: int) -> VerifyGlobalRankingScoreRequest:
        self.season = season
        return self

    def with_score(self, score: int) -> VerifyGlobalRankingScoreRequest:
        self.score = score
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyGlobalRankingScoreRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyGlobalRankingScoreRequest:
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
    ) -> Optional[VerifyGlobalRankingScoreRequest]:
        if data is None:
            return None
        return VerifyGlobalRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_season(data.get('season'))\
            .with_score(data.get('score'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "verifyType": self.verify_type,
            "season": self.season,
            "score": self.score,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyGlobalRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    verify_type: str = None
    season: int = None
    score: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyGlobalRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyGlobalRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> VerifyGlobalRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyGlobalRankingScoreByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_season(self, season: int) -> VerifyGlobalRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_score(self, score: int) -> VerifyGlobalRankingScoreByUserIdRequest:
        self.score = score
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyGlobalRankingScoreByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyGlobalRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyGlobalRankingScoreByUserIdRequest:
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
    ) -> Optional[VerifyGlobalRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return VerifyGlobalRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_season(data.get('season'))\
            .with_score(data.get('score'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "verifyType": self.verify_type,
            "season": self.season,
            "score": self.score,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyGlobalRankingScoreByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyGlobalRankingScoreByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyGlobalRankingScoreByStampTaskRequest:
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
    ) -> Optional[VerifyGlobalRankingScoreByStampTaskRequest]:
        if data is None:
            return None
        return VerifyGlobalRankingScoreByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeGlobalRankingReceivedRewardsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalRankingReceivedRewardsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeGlobalRankingReceivedRewardsRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeGlobalRankingReceivedRewardsRequest:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> DescribeGlobalRankingReceivedRewardsRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeGlobalRankingReceivedRewardsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGlobalRankingReceivedRewardsRequest:
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
    ) -> Optional[DescribeGlobalRankingReceivedRewardsRequest]:
        if data is None:
            return None
        return DescribeGlobalRankingReceivedRewardsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeGlobalRankingReceivedRewardsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalRankingReceivedRewardsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeGlobalRankingReceivedRewardsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeGlobalRankingReceivedRewardsByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> DescribeGlobalRankingReceivedRewardsByUserIdRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeGlobalRankingReceivedRewardsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGlobalRankingReceivedRewardsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeGlobalRankingReceivedRewardsByUserIdRequest:
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
    ) -> Optional[DescribeGlobalRankingReceivedRewardsByUserIdRequest]:
        if data is None:
            return None
        return DescribeGlobalRankingReceivedRewardsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class CreateGlobalRankingReceivedRewardRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    season: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGlobalRankingReceivedRewardRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> CreateGlobalRankingReceivedRewardRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> CreateGlobalRankingReceivedRewardRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> CreateGlobalRankingReceivedRewardRequest:
        self.season = season
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateGlobalRankingReceivedRewardRequest:
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
    ) -> Optional[CreateGlobalRankingReceivedRewardRequest]:
        if data is None:
            return None
        return CreateGlobalRankingReceivedRewardRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class CreateGlobalRankingReceivedRewardByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGlobalRankingReceivedRewardByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> CreateGlobalRankingReceivedRewardByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> CreateGlobalRankingReceivedRewardByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> CreateGlobalRankingReceivedRewardByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreateGlobalRankingReceivedRewardByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateGlobalRankingReceivedRewardByUserIdRequest:
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
    ) -> Optional[CreateGlobalRankingReceivedRewardByUserIdRequest]:
        if data is None:
            return None
        return CreateGlobalRankingReceivedRewardByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class ReceiveGlobalRankingReceivedRewardRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    season: int = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveGlobalRankingReceivedRewardRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> ReceiveGlobalRankingReceivedRewardRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> ReceiveGlobalRankingReceivedRewardRequest:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> ReceiveGlobalRankingReceivedRewardRequest:
        self.season = season
        return self

    def with_config(self, config: List[Config]) -> ReceiveGlobalRankingReceivedRewardRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ReceiveGlobalRankingReceivedRewardRequest:
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
    ) -> Optional[ReceiveGlobalRankingReceivedRewardRequest]:
        if data is None:
            return None
        return ReceiveGlobalRankingReceivedRewardRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "season": self.season,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class ReceiveGlobalRankingReceivedRewardByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    season: int = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveGlobalRankingReceivedRewardByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> ReceiveGlobalRankingReceivedRewardByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> ReceiveGlobalRankingReceivedRewardByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> ReceiveGlobalRankingReceivedRewardByUserIdRequest:
        self.season = season
        return self

    def with_config(self, config: List[Config]) -> ReceiveGlobalRankingReceivedRewardByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ReceiveGlobalRankingReceivedRewardByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ReceiveGlobalRankingReceivedRewardByUserIdRequest:
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
    ) -> Optional[ReceiveGlobalRankingReceivedRewardByUserIdRequest]:
        if data is None:
            return None
        return ReceiveGlobalRankingReceivedRewardByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "season": self.season,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class GetGlobalRankingReceivedRewardRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    season: int = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalRankingReceivedRewardRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetGlobalRankingReceivedRewardRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> GetGlobalRankingReceivedRewardRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> GetGlobalRankingReceivedRewardRequest:
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
    ) -> Optional[GetGlobalRankingReceivedRewardRequest]:
        if data is None:
            return None
        return GetGlobalRankingReceivedRewardRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class GetGlobalRankingReceivedRewardByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalRankingReceivedRewardByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetGlobalRankingReceivedRewardByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> GetGlobalRankingReceivedRewardByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GetGlobalRankingReceivedRewardByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetGlobalRankingReceivedRewardByUserIdRequest:
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
    ) -> Optional[GetGlobalRankingReceivedRewardByUserIdRequest]:
        if data is None:
            return None
        return GetGlobalRankingReceivedRewardByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteGlobalRankingReceivedRewardByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGlobalRankingReceivedRewardByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteGlobalRankingReceivedRewardByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> DeleteGlobalRankingReceivedRewardByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> DeleteGlobalRankingReceivedRewardByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteGlobalRankingReceivedRewardByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteGlobalRankingReceivedRewardByUserIdRequest:
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
    ) -> Optional[DeleteGlobalRankingReceivedRewardByUserIdRequest]:
        if data is None:
            return None
        return DeleteGlobalRankingReceivedRewardByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class CreateGlobalRankingReceivedRewardByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> CreateGlobalRankingReceivedRewardByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> CreateGlobalRankingReceivedRewardByStampTaskRequest:
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
    ) -> Optional[CreateGlobalRankingReceivedRewardByStampTaskRequest]:
        if data is None:
            return None
        return CreateGlobalRankingReceivedRewardByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeGlobalRankingsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalRankingsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeGlobalRankingsRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeGlobalRankingsRequest:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> DescribeGlobalRankingsRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeGlobalRankingsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGlobalRankingsRequest:
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
    ) -> Optional[DescribeGlobalRankingsRequest]:
        if data is None:
            return None
        return DescribeGlobalRankingsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeGlobalRankingsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGlobalRankingsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeGlobalRankingsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeGlobalRankingsByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> DescribeGlobalRankingsByUserIdRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeGlobalRankingsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGlobalRankingsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeGlobalRankingsByUserIdRequest:
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
    ) -> Optional[DescribeGlobalRankingsByUserIdRequest]:
        if data is None:
            return None
        return DescribeGlobalRankingsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetGlobalRankingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    season: int = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalRankingRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetGlobalRankingRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> GetGlobalRankingRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> GetGlobalRankingRequest:
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
    ) -> Optional[GetGlobalRankingRequest]:
        if data is None:
            return None
        return GetGlobalRankingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class GetGlobalRankingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGlobalRankingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetGlobalRankingByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> GetGlobalRankingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GetGlobalRankingByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetGlobalRankingByUserIdRequest:
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
    ) -> Optional[GetGlobalRankingByUserIdRequest]:
        if data is None:
            return None
        return GetGlobalRankingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeClusterRankingModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeClusterRankingModelsRequest:
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
    ) -> Optional[DescribeClusterRankingModelsRequest]:
        if data is None:
            return None
        return DescribeClusterRankingModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetClusterRankingModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetClusterRankingModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetClusterRankingModelRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetClusterRankingModelRequest]:
        if data is None:
            return None
        return GetClusterRankingModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class DescribeClusterRankingModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeClusterRankingModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeClusterRankingModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeClusterRankingModelMastersRequest:
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
    ) -> Optional[DescribeClusterRankingModelMastersRequest]:
        if data is None:
            return None
        return DescribeClusterRankingModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateClusterRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    cluster_type: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    ranking_rewards: List[RankingReward] = None
    reward_calculation_index: str = None
    entry_period_event_id: str = None
    access_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateClusterRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateClusterRankingModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateClusterRankingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateClusterRankingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_cluster_type(self, cluster_type: str) -> CreateClusterRankingModelMasterRequest:
        self.cluster_type = cluster_type
        return self

    def with_minimum_value(self, minimum_value: int) -> CreateClusterRankingModelMasterRequest:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> CreateClusterRankingModelMasterRequest:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> CreateClusterRankingModelMasterRequest:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> CreateClusterRankingModelMasterRequest:
        self.order_direction = order_direction
        return self

    def with_ranking_rewards(self, ranking_rewards: List[RankingReward]) -> CreateClusterRankingModelMasterRequest:
        self.ranking_rewards = ranking_rewards
        return self

    def with_reward_calculation_index(self, reward_calculation_index: str) -> CreateClusterRankingModelMasterRequest:
        self.reward_calculation_index = reward_calculation_index
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> CreateClusterRankingModelMasterRequest:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> CreateClusterRankingModelMasterRequest:
        self.access_period_event_id = access_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateClusterRankingModelMasterRequest]:
        if data is None:
            return None
        return CreateClusterRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_cluster_type(data.get('clusterType'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_ranking_rewards(None if data.get('rankingRewards') is None else [
                RankingReward.from_dict(data.get('rankingRewards')[i])
                for i in range(len(data.get('rankingRewards')))
            ])\
            .with_reward_calculation_index(data.get('rewardCalculationIndex'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "clusterType": self.cluster_type,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "rankingRewards": None if self.ranking_rewards is None else [
                self.ranking_rewards[i].to_dict() if self.ranking_rewards[i] else None
                for i in range(len(self.ranking_rewards))
            ],
            "rewardCalculationIndex": self.reward_calculation_index,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
        }


class GetClusterRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetClusterRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetClusterRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetClusterRankingModelMasterRequest]:
        if data is None:
            return None
        return GetClusterRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class UpdateClusterRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    description: str = None
    metadata: str = None
    cluster_type: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    ranking_rewards: List[RankingReward] = None
    reward_calculation_index: str = None
    entry_period_event_id: str = None
    access_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateClusterRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> UpdateClusterRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def with_description(self, description: str) -> UpdateClusterRankingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateClusterRankingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_cluster_type(self, cluster_type: str) -> UpdateClusterRankingModelMasterRequest:
        self.cluster_type = cluster_type
        return self

    def with_minimum_value(self, minimum_value: int) -> UpdateClusterRankingModelMasterRequest:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> UpdateClusterRankingModelMasterRequest:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> UpdateClusterRankingModelMasterRequest:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> UpdateClusterRankingModelMasterRequest:
        self.order_direction = order_direction
        return self

    def with_ranking_rewards(self, ranking_rewards: List[RankingReward]) -> UpdateClusterRankingModelMasterRequest:
        self.ranking_rewards = ranking_rewards
        return self

    def with_reward_calculation_index(self, reward_calculation_index: str) -> UpdateClusterRankingModelMasterRequest:
        self.reward_calculation_index = reward_calculation_index
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> UpdateClusterRankingModelMasterRequest:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> UpdateClusterRankingModelMasterRequest:
        self.access_period_event_id = access_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateClusterRankingModelMasterRequest]:
        if data is None:
            return None
        return UpdateClusterRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_cluster_type(data.get('clusterType'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_ranking_rewards(None if data.get('rankingRewards') is None else [
                RankingReward.from_dict(data.get('rankingRewards')[i])
                for i in range(len(data.get('rankingRewards')))
            ])\
            .with_reward_calculation_index(data.get('rewardCalculationIndex'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "description": self.description,
            "metadata": self.metadata,
            "clusterType": self.cluster_type,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "rankingRewards": None if self.ranking_rewards is None else [
                self.ranking_rewards[i].to_dict() if self.ranking_rewards[i] else None
                for i in range(len(self.ranking_rewards))
            ],
            "rewardCalculationIndex": self.reward_calculation_index,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
        }


class DeleteClusterRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteClusterRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteClusterRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteClusterRankingModelMasterRequest]:
        if data is None:
            return None
        return DeleteClusterRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class DescribeClusterRankingScoresRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeClusterRankingScoresRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeClusterRankingScoresRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeClusterRankingScoresRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> DescribeClusterRankingScoresRequest:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> DescribeClusterRankingScoresRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeClusterRankingScoresRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeClusterRankingScoresRequest:
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
    ) -> Optional[DescribeClusterRankingScoresRequest]:
        if data is None:
            return None
        return DescribeClusterRankingScoresRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeClusterRankingScoresByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeClusterRankingScoresByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeClusterRankingScoresByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeClusterRankingScoresByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> DescribeClusterRankingScoresByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> DescribeClusterRankingScoresByUserIdRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeClusterRankingScoresByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeClusterRankingScoresByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeClusterRankingScoresByUserIdRequest:
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
    ) -> Optional[DescribeClusterRankingScoresByUserIdRequest]:
        if data is None:
            return None
        return DescribeClusterRankingScoresByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class PutClusterRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    access_token: str = None
    score: int = None
    metadata: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutClusterRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> PutClusterRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> PutClusterRankingScoreRequest:
        self.cluster_name = cluster_name
        return self

    def with_access_token(self, access_token: str) -> PutClusterRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_score(self, score: int) -> PutClusterRankingScoreRequest:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> PutClusterRankingScoreRequest:
        self.metadata = metadata
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutClusterRankingScoreRequest:
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
    ) -> Optional[PutClusterRankingScoreRequest]:
        if data is None:
            return None
        return PutClusterRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_access_token(data.get('accessToken'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "accessToken": self.access_token,
            "score": self.score,
            "metadata": self.metadata,
        }


class PutClusterRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    user_id: str = None
    score: int = None
    metadata: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutClusterRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> PutClusterRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> PutClusterRankingScoreByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_user_id(self, user_id: str) -> PutClusterRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_score(self, score: int) -> PutClusterRankingScoreByUserIdRequest:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> PutClusterRankingScoreByUserIdRequest:
        self.metadata = metadata
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PutClusterRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutClusterRankingScoreByUserIdRequest:
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
    ) -> Optional[PutClusterRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return PutClusterRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_user_id(data.get('userId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "userId": self.user_id,
            "score": self.score,
            "metadata": self.metadata,
            "timeOffsetToken": self.time_offset_token,
        }


class GetClusterRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    access_token: str = None
    season: int = None

    def with_namespace_name(self, namespace_name: str) -> GetClusterRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetClusterRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> GetClusterRankingScoreRequest:
        self.cluster_name = cluster_name
        return self

    def with_access_token(self, access_token: str) -> GetClusterRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> GetClusterRankingScoreRequest:
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
    ) -> Optional[GetClusterRankingScoreRequest]:
        if data is None:
            return None
        return GetClusterRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class GetClusterRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetClusterRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetClusterRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> GetClusterRankingScoreByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_user_id(self, user_id: str) -> GetClusterRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GetClusterRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetClusterRankingScoreByUserIdRequest:
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
    ) -> Optional[GetClusterRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return GetClusterRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteClusterRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteClusterRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteClusterRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> DeleteClusterRankingScoreByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_user_id(self, user_id: str) -> DeleteClusterRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> DeleteClusterRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteClusterRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteClusterRankingScoreByUserIdRequest:
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
    ) -> Optional[DeleteClusterRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return DeleteClusterRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyClusterRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    cluster_name: str = None
    verify_type: str = None
    season: int = None
    score: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyClusterRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyClusterRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> VerifyClusterRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> VerifyClusterRankingScoreRequest:
        self.cluster_name = cluster_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyClusterRankingScoreRequest:
        self.verify_type = verify_type
        return self

    def with_season(self, season: int) -> VerifyClusterRankingScoreRequest:
        self.season = season
        return self

    def with_score(self, score: int) -> VerifyClusterRankingScoreRequest:
        self.score = score
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyClusterRankingScoreRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyClusterRankingScoreRequest:
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
    ) -> Optional[VerifyClusterRankingScoreRequest]:
        if data is None:
            return None
        return VerifyClusterRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_season(data.get('season'))\
            .with_score(data.get('score'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "verifyType": self.verify_type,
            "season": self.season,
            "score": self.score,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyClusterRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    cluster_name: str = None
    verify_type: str = None
    season: int = None
    score: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyClusterRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyClusterRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> VerifyClusterRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> VerifyClusterRankingScoreByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyClusterRankingScoreByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_season(self, season: int) -> VerifyClusterRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_score(self, score: int) -> VerifyClusterRankingScoreByUserIdRequest:
        self.score = score
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyClusterRankingScoreByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyClusterRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyClusterRankingScoreByUserIdRequest:
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
    ) -> Optional[VerifyClusterRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return VerifyClusterRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_season(data.get('season'))\
            .with_score(data.get('score'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "verifyType": self.verify_type,
            "season": self.season,
            "score": self.score,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyClusterRankingScoreByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyClusterRankingScoreByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyClusterRankingScoreByStampTaskRequest:
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
    ) -> Optional[VerifyClusterRankingScoreByStampTaskRequest]:
        if data is None:
            return None
        return VerifyClusterRankingScoreByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeClusterRankingReceivedRewardsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeClusterRankingReceivedRewardsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeClusterRankingReceivedRewardsRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeClusterRankingReceivedRewardsRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> DescribeClusterRankingReceivedRewardsRequest:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> DescribeClusterRankingReceivedRewardsRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeClusterRankingReceivedRewardsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeClusterRankingReceivedRewardsRequest:
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
    ) -> Optional[DescribeClusterRankingReceivedRewardsRequest]:
        if data is None:
            return None
        return DescribeClusterRankingReceivedRewardsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeClusterRankingReceivedRewardsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeClusterRankingReceivedRewardsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeClusterRankingReceivedRewardsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeClusterRankingReceivedRewardsByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> DescribeClusterRankingReceivedRewardsByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> DescribeClusterRankingReceivedRewardsByUserIdRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeClusterRankingReceivedRewardsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeClusterRankingReceivedRewardsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeClusterRankingReceivedRewardsByUserIdRequest:
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
    ) -> Optional[DescribeClusterRankingReceivedRewardsByUserIdRequest]:
        if data is None:
            return None
        return DescribeClusterRankingReceivedRewardsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class CreateClusterRankingReceivedRewardRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    access_token: str = None
    season: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateClusterRankingReceivedRewardRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> CreateClusterRankingReceivedRewardRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> CreateClusterRankingReceivedRewardRequest:
        self.cluster_name = cluster_name
        return self

    def with_access_token(self, access_token: str) -> CreateClusterRankingReceivedRewardRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> CreateClusterRankingReceivedRewardRequest:
        self.season = season
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateClusterRankingReceivedRewardRequest:
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
    ) -> Optional[CreateClusterRankingReceivedRewardRequest]:
        if data is None:
            return None
        return CreateClusterRankingReceivedRewardRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class CreateClusterRankingReceivedRewardByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateClusterRankingReceivedRewardByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> CreateClusterRankingReceivedRewardByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> CreateClusterRankingReceivedRewardByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_user_id(self, user_id: str) -> CreateClusterRankingReceivedRewardByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> CreateClusterRankingReceivedRewardByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreateClusterRankingReceivedRewardByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateClusterRankingReceivedRewardByUserIdRequest:
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
    ) -> Optional[CreateClusterRankingReceivedRewardByUserIdRequest]:
        if data is None:
            return None
        return CreateClusterRankingReceivedRewardByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class ReceiveClusterRankingReceivedRewardRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveClusterRankingReceivedRewardRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> ReceiveClusterRankingReceivedRewardRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> ReceiveClusterRankingReceivedRewardRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> ReceiveClusterRankingReceivedRewardRequest:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> ReceiveClusterRankingReceivedRewardRequest:
        self.season = season
        return self

    def with_config(self, config: List[Config]) -> ReceiveClusterRankingReceivedRewardRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ReceiveClusterRankingReceivedRewardRequest:
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
    ) -> Optional[ReceiveClusterRankingReceivedRewardRequest]:
        if data is None:
            return None
        return ReceiveClusterRankingReceivedRewardRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class ReceiveClusterRankingReceivedRewardByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ReceiveClusterRankingReceivedRewardByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> ReceiveClusterRankingReceivedRewardByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> ReceiveClusterRankingReceivedRewardByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> ReceiveClusterRankingReceivedRewardByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> ReceiveClusterRankingReceivedRewardByUserIdRequest:
        self.season = season
        return self

    def with_config(self, config: List[Config]) -> ReceiveClusterRankingReceivedRewardByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ReceiveClusterRankingReceivedRewardByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ReceiveClusterRankingReceivedRewardByUserIdRequest:
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
    ) -> Optional[ReceiveClusterRankingReceivedRewardByUserIdRequest]:
        if data is None:
            return None
        return ReceiveClusterRankingReceivedRewardByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class GetClusterRankingReceivedRewardRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    access_token: str = None
    season: int = None

    def with_namespace_name(self, namespace_name: str) -> GetClusterRankingReceivedRewardRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetClusterRankingReceivedRewardRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> GetClusterRankingReceivedRewardRequest:
        self.cluster_name = cluster_name
        return self

    def with_access_token(self, access_token: str) -> GetClusterRankingReceivedRewardRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> GetClusterRankingReceivedRewardRequest:
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
    ) -> Optional[GetClusterRankingReceivedRewardRequest]:
        if data is None:
            return None
        return GetClusterRankingReceivedRewardRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class GetClusterRankingReceivedRewardByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetClusterRankingReceivedRewardByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetClusterRankingReceivedRewardByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> GetClusterRankingReceivedRewardByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_user_id(self, user_id: str) -> GetClusterRankingReceivedRewardByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GetClusterRankingReceivedRewardByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetClusterRankingReceivedRewardByUserIdRequest:
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
    ) -> Optional[GetClusterRankingReceivedRewardByUserIdRequest]:
        if data is None:
            return None
        return GetClusterRankingReceivedRewardByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteClusterRankingReceivedRewardByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteClusterRankingReceivedRewardByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteClusterRankingReceivedRewardByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> DeleteClusterRankingReceivedRewardByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_user_id(self, user_id: str) -> DeleteClusterRankingReceivedRewardByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> DeleteClusterRankingReceivedRewardByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteClusterRankingReceivedRewardByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteClusterRankingReceivedRewardByUserIdRequest:
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
    ) -> Optional[DeleteClusterRankingReceivedRewardByUserIdRequest]:
        if data is None:
            return None
        return DeleteClusterRankingReceivedRewardByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class CreateClusterRankingReceivedRewardByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> CreateClusterRankingReceivedRewardByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> CreateClusterRankingReceivedRewardByStampTaskRequest:
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
    ) -> Optional[CreateClusterRankingReceivedRewardByStampTaskRequest]:
        if data is None:
            return None
        return CreateClusterRankingReceivedRewardByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeClusterRankingsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeClusterRankingsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeClusterRankingsRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeClusterRankingsRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> DescribeClusterRankingsRequest:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> DescribeClusterRankingsRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeClusterRankingsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeClusterRankingsRequest:
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
    ) -> Optional[DescribeClusterRankingsRequest]:
        if data is None:
            return None
        return DescribeClusterRankingsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeClusterRankingsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeClusterRankingsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeClusterRankingsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeClusterRankingsByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> DescribeClusterRankingsByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> DescribeClusterRankingsByUserIdRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeClusterRankingsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeClusterRankingsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeClusterRankingsByUserIdRequest:
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
    ) -> Optional[DescribeClusterRankingsByUserIdRequest]:
        if data is None:
            return None
        return DescribeClusterRankingsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetClusterRankingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    access_token: str = None
    season: int = None

    def with_namespace_name(self, namespace_name: str) -> GetClusterRankingRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetClusterRankingRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> GetClusterRankingRequest:
        self.cluster_name = cluster_name
        return self

    def with_access_token(self, access_token: str) -> GetClusterRankingRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> GetClusterRankingRequest:
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
    ) -> Optional[GetClusterRankingRequest]:
        if data is None:
            return None
        return GetClusterRankingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class GetClusterRankingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    cluster_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetClusterRankingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetClusterRankingByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> GetClusterRankingByUserIdRequest:
        self.cluster_name = cluster_name
        return self

    def with_user_id(self, user_id: str) -> GetClusterRankingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GetClusterRankingByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetClusterRankingByUserIdRequest:
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
    ) -> Optional[GetClusterRankingByUserIdRequest]:
        if data is None:
            return None
        return GetClusterRankingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeSubscribeRankingModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribeRankingModelsRequest:
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
    ) -> Optional[DescribeSubscribeRankingModelsRequest]:
        if data is None:
            return None
        return DescribeSubscribeRankingModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetSubscribeRankingModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRankingModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetSubscribeRankingModelRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSubscribeRankingModelRequest]:
        if data is None:
            return None
        return GetSubscribeRankingModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class DescribeSubscribeRankingModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribeRankingModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribeRankingModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribeRankingModelMastersRequest:
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
    ) -> Optional[DescribeSubscribeRankingModelMastersRequest]:
        if data is None:
            return None
        return DescribeSubscribeRankingModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateSubscribeRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    entry_period_event_id: str = None
    access_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateSubscribeRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateSubscribeRankingModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateSubscribeRankingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateSubscribeRankingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> CreateSubscribeRankingModelMasterRequest:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> CreateSubscribeRankingModelMasterRequest:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> CreateSubscribeRankingModelMasterRequest:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> CreateSubscribeRankingModelMasterRequest:
        self.order_direction = order_direction
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> CreateSubscribeRankingModelMasterRequest:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> CreateSubscribeRankingModelMasterRequest:
        self.access_period_event_id = access_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateSubscribeRankingModelMasterRequest]:
        if data is None:
            return None
        return CreateSubscribeRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
        }


class GetSubscribeRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetSubscribeRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSubscribeRankingModelMasterRequest]:
        if data is None:
            return None
        return GetSubscribeRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class UpdateSubscribeRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    description: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    entry_period_event_id: str = None
    access_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateSubscribeRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> UpdateSubscribeRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def with_description(self, description: str) -> UpdateSubscribeRankingModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateSubscribeRankingModelMasterRequest:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> UpdateSubscribeRankingModelMasterRequest:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> UpdateSubscribeRankingModelMasterRequest:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> UpdateSubscribeRankingModelMasterRequest:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> UpdateSubscribeRankingModelMasterRequest:
        self.order_direction = order_direction
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> UpdateSubscribeRankingModelMasterRequest:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> UpdateSubscribeRankingModelMasterRequest:
        self.access_period_event_id = access_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateSubscribeRankingModelMasterRequest]:
        if data is None:
            return None
        return UpdateSubscribeRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "description": self.description,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
        }


class DeleteSubscribeRankingModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSubscribeRankingModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteSubscribeRankingModelMasterRequest:
        self.ranking_name = ranking_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteSubscribeRankingModelMasterRequest]:
        if data is None:
            return None
        return DeleteSubscribeRankingModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
        }


class DescribeSubscribesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSubscribesRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeSubscribesRequest:
        self.ranking_name = ranking_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribesRequest:
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
    ) -> Optional[DescribeSubscribesRequest]:
        if data is None:
            return None
        return DescribeSubscribesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeSubscribesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSubscribesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeSubscribesByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribesByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeSubscribesByUserIdRequest:
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
    ) -> Optional[DescribeSubscribesByUserIdRequest]:
        if data is None:
            return None
        return DescribeSubscribesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class AddSubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddSubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> AddSubscribeRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> AddSubscribeRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> AddSubscribeRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddSubscribeRequest:
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
    ) -> Optional[AddSubscribeRequest]:
        if data is None:
            return None
        return AddSubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class AddSubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddSubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> AddSubscribeByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> AddSubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> AddSubscribeByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AddSubscribeByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddSubscribeByUserIdRequest:
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
    ) -> Optional[AddSubscribeByUserIdRequest]:
        if data is None:
            return None
        return AddSubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeSubscribeRankingScoresRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribeRankingScoresRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSubscribeRankingScoresRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeSubscribeRankingScoresRequest:
        self.ranking_name = ranking_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribeRankingScoresRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribeRankingScoresRequest:
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
    ) -> Optional[DescribeSubscribeRankingScoresRequest]:
        if data is None:
            return None
        return DescribeSubscribeRankingScoresRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeSubscribeRankingScoresByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribeRankingScoresByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSubscribeRankingScoresByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeSubscribeRankingScoresByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribeRankingScoresByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribeRankingScoresByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeSubscribeRankingScoresByUserIdRequest:
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
    ) -> Optional[DescribeSubscribeRankingScoresByUserIdRequest]:
        if data is None:
            return None
        return DescribeSubscribeRankingScoresByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class PutSubscribeRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    score: int = None
    metadata: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutSubscribeRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> PutSubscribeRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> PutSubscribeRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_score(self, score: int) -> PutSubscribeRankingScoreRequest:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> PutSubscribeRankingScoreRequest:
        self.metadata = metadata
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutSubscribeRankingScoreRequest:
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
    ) -> Optional[PutSubscribeRankingScoreRequest]:
        if data is None:
            return None
        return PutSubscribeRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "score": self.score,
            "metadata": self.metadata,
        }


class PutSubscribeRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    score: int = None
    metadata: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutSubscribeRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> PutSubscribeRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> PutSubscribeRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_score(self, score: int) -> PutSubscribeRankingScoreByUserIdRequest:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> PutSubscribeRankingScoreByUserIdRequest:
        self.metadata = metadata
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PutSubscribeRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutSubscribeRankingScoreByUserIdRequest:
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
    ) -> Optional[PutSubscribeRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return PutSubscribeRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "score": self.score,
            "metadata": self.metadata,
            "timeOffsetToken": self.time_offset_token,
        }


class GetSubscribeRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    season: int = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetSubscribeRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> GetSubscribeRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> GetSubscribeRankingScoreRequest:
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
    ) -> Optional[GetSubscribeRankingScoreRequest]:
        if data is None:
            return None
        return GetSubscribeRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "season": self.season,
        }


class GetSubscribeRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetSubscribeRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> GetSubscribeRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GetSubscribeRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetSubscribeRankingScoreByUserIdRequest:
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
    ) -> Optional[GetSubscribeRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return GetSubscribeRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteSubscribeRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSubscribeRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteSubscribeRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> DeleteSubscribeRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> DeleteSubscribeRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteSubscribeRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteSubscribeRankingScoreByUserIdRequest:
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
    ) -> Optional[DeleteSubscribeRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return DeleteSubscribeRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifySubscribeRankingScoreRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    verify_type: str = None
    season: int = None
    score: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifySubscribeRankingScoreRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifySubscribeRankingScoreRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> VerifySubscribeRankingScoreRequest:
        self.ranking_name = ranking_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifySubscribeRankingScoreRequest:
        self.verify_type = verify_type
        return self

    def with_season(self, season: int) -> VerifySubscribeRankingScoreRequest:
        self.season = season
        return self

    def with_score(self, score: int) -> VerifySubscribeRankingScoreRequest:
        self.score = score
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifySubscribeRankingScoreRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifySubscribeRankingScoreRequest:
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
    ) -> Optional[VerifySubscribeRankingScoreRequest]:
        if data is None:
            return None
        return VerifySubscribeRankingScoreRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_season(data.get('season'))\
            .with_score(data.get('score'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "verifyType": self.verify_type,
            "season": self.season,
            "score": self.score,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifySubscribeRankingScoreByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    verify_type: str = None
    season: int = None
    score: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifySubscribeRankingScoreByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifySubscribeRankingScoreByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> VerifySubscribeRankingScoreByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifySubscribeRankingScoreByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_season(self, season: int) -> VerifySubscribeRankingScoreByUserIdRequest:
        self.season = season
        return self

    def with_score(self, score: int) -> VerifySubscribeRankingScoreByUserIdRequest:
        self.score = score
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifySubscribeRankingScoreByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifySubscribeRankingScoreByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifySubscribeRankingScoreByUserIdRequest:
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
    ) -> Optional[VerifySubscribeRankingScoreByUserIdRequest]:
        if data is None:
            return None
        return VerifySubscribeRankingScoreByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_season(data.get('season'))\
            .with_score(data.get('score'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "verifyType": self.verify_type,
            "season": self.season,
            "score": self.score,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifySubscribeRankingScoreByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifySubscribeRankingScoreByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifySubscribeRankingScoreByStampTaskRequest:
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
    ) -> Optional[VerifySubscribeRankingScoreByStampTaskRequest]:
        if data is None:
            return None
        return VerifySubscribeRankingScoreByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeSubscribeRankingsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    ranking_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribeRankingsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSubscribeRankingsRequest:
        self.access_token = access_token
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeSubscribeRankingsRequest:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> DescribeSubscribeRankingsRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribeRankingsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribeRankingsRequest:
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
    ) -> Optional[DescribeSubscribeRankingsRequest]:
        if data is None:
            return None
        return DescribeSubscribeRankingsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rankingName": self.ranking_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeSubscribeRankingsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ranking_name: str = None
    season: int = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscribeRankingsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSubscribeRankingsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_ranking_name(self, ranking_name: str) -> DescribeSubscribeRankingsByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> DescribeSubscribeRankingsByUserIdRequest:
        self.season = season
        return self

    def with_page_token(self, page_token: str) -> DescribeSubscribeRankingsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSubscribeRankingsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeSubscribeRankingsByUserIdRequest:
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
    ) -> Optional[DescribeSubscribeRankingsByUserIdRequest]:
        if data is None:
            return None
        return DescribeSubscribeRankingsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rankingName": self.ranking_name,
            "season": self.season,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetSubscribeRankingRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    season: int = None
    scorer_user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRankingRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetSubscribeRankingRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> GetSubscribeRankingRequest:
        self.access_token = access_token
        return self

    def with_season(self, season: int) -> GetSubscribeRankingRequest:
        self.season = season
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> GetSubscribeRankingRequest:
        self.scorer_user_id = scorer_user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSubscribeRankingRequest]:
        if data is None:
            return None
        return GetSubscribeRankingRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_season(data.get('season'))\
            .with_scorer_user_id(data.get('scorerUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "season": self.season,
            "scorerUserId": self.scorer_user_id,
        }


class GetSubscribeRankingByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    scorer_user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRankingByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetSubscribeRankingByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> GetSubscribeRankingByUserIdRequest:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GetSubscribeRankingByUserIdRequest:
        self.season = season
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> GetSubscribeRankingByUserIdRequest:
        self.scorer_user_id = scorer_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetSubscribeRankingByUserIdRequest:
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
    ) -> Optional[GetSubscribeRankingByUserIdRequest]:
        if data is None:
            return None
        return GetSubscribeRankingByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "scorerUserId": self.scorer_user_id,
            "timeOffsetToken": self.time_offset_token,
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


class GetCurrentRankingMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentRankingMasterRequest:
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
    ) -> Optional[GetCurrentRankingMasterRequest]:
        if data is None:
            return None
        return GetCurrentRankingMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentRankingMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentRankingMasterRequest:
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
    ) -> Optional[PreUpdateCurrentRankingMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentRankingMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentRankingMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRankingMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentRankingMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentRankingMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentRankingMasterRequest:
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
    ) -> Optional[UpdateCurrentRankingMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentRankingMasterRequest()\
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


class UpdateCurrentRankingMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRankingMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentRankingMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentRankingMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentRankingMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class GetSubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    target_user_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetSubscribeRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> GetSubscribeRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> GetSubscribeRequest:
        self.target_user_id = target_user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSubscribeRequest]:
        if data is None:
            return None
        return GetSubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class GetSubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> GetSubscribeByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> GetSubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> GetSubscribeByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetSubscribeByUserIdRequest:
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
    ) -> Optional[GetSubscribeByUserIdRequest]:
        if data is None:
            return None
        return GetSubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteSubscribeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    access_token: str = None
    target_user_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSubscribeRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteSubscribeRequest:
        self.ranking_name = ranking_name
        return self

    def with_access_token(self, access_token: str) -> DeleteSubscribeRequest:
        self.access_token = access_token
        return self

    def with_target_user_id(self, target_user_id: str) -> DeleteSubscribeRequest:
        self.target_user_id = target_user_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteSubscribeRequest:
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
    ) -> Optional[DeleteSubscribeRequest]:
        if data is None:
            return None
        return DeleteSubscribeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "accessToken": self.access_token,
            "targetUserId": self.target_user_id,
        }


class DeleteSubscribeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    ranking_name: str = None
    user_id: str = None
    target_user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSubscribeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_ranking_name(self, ranking_name: str) -> DeleteSubscribeByUserIdRequest:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> DeleteSubscribeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> DeleteSubscribeByUserIdRequest:
        self.target_user_id = target_user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteSubscribeByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteSubscribeByUserIdRequest:
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
    ) -> Optional[DeleteSubscribeByUserIdRequest]:
        if data is None:
            return None
        return DeleteSubscribeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
            "timeOffsetToken": self.time_offset_token,
        }