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


class DescribeMatchSessionsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMatchSessionsRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeMatchSessionsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMatchSessionsRequest:
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
    ) -> Optional[DescribeMatchSessionsRequest]:
        if data is None:
            return None
        return DescribeMatchSessionsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateMatchSessionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    session_name: str = None
    ttl_seconds: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateMatchSessionRequest:
        self.namespace_name = namespace_name
        return self

    def with_session_name(self, session_name: str) -> CreateMatchSessionRequest:
        self.session_name = session_name
        return self

    def with_ttl_seconds(self, ttl_seconds: int) -> CreateMatchSessionRequest:
        self.ttl_seconds = ttl_seconds
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateMatchSessionRequest]:
        if data is None:
            return None
        return CreateMatchSessionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_session_name(data.get('sessionName'))\
            .with_ttl_seconds(data.get('ttlSeconds'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "sessionName": self.session_name,
            "ttlSeconds": self.ttl_seconds,
        }


class GetMatchSessionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    session_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMatchSessionRequest:
        self.namespace_name = namespace_name
        return self

    def with_session_name(self, session_name: str) -> GetMatchSessionRequest:
        self.session_name = session_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMatchSessionRequest]:
        if data is None:
            return None
        return GetMatchSessionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_session_name(data.get('sessionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "sessionName": self.session_name,
        }


class DeleteMatchSessionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    session_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMatchSessionRequest:
        self.namespace_name = namespace_name
        return self

    def with_session_name(self, session_name: str) -> DeleteMatchSessionRequest:
        self.session_name = session_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMatchSessionRequest]:
        if data is None:
            return None
        return DeleteMatchSessionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_session_name(data.get('sessionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "sessionName": self.session_name,
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
    tiers: List[TierModel] = None
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

    def with_tiers(self, tiers: List[TierModel]) -> CreateSeasonModelMasterRequest:
        self.tiers = tiers
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
            .with_tiers(None if data.get('tiers') is None else [
                TierModel.from_dict(data.get('tiers')[i])
                for i in range(len(data.get('tiers')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "tiers": None if self.tiers is None else [
                self.tiers[i].to_dict() if self.tiers[i] else None
                for i in range(len(self.tiers))
            ],
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
    tiers: List[TierModel] = None
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

    def with_tiers(self, tiers: List[TierModel]) -> UpdateSeasonModelMasterRequest:
        self.tiers = tiers
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
            .with_tiers(None if data.get('tiers') is None else [
                TierModel.from_dict(data.get('tiers')[i])
                for i in range(len(data.get('tiers')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "description": self.description,
            "metadata": self.metadata,
            "tiers": None if self.tiers is None else [
                self.tiers[i].to_dict() if self.tiers[i] else None
                for i in range(len(self.tiers))
            ],
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


class GetCurrentSeasonModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentSeasonModelMasterRequest:
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
    ) -> Optional[GetCurrentSeasonModelMasterRequest]:
        if data is None:
            return None
        return GetCurrentSeasonModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentSeasonModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentSeasonModelMasterRequest:
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
    ) -> Optional[PreUpdateCurrentSeasonModelMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentSeasonModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentSeasonModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentSeasonModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentSeasonModelMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentSeasonModelMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentSeasonModelMasterRequest:
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
    ) -> Optional[UpdateCurrentSeasonModelMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentSeasonModelMasterRequest()\
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


class UpdateCurrentSeasonModelMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentSeasonModelMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentSeasonModelMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentSeasonModelMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentSeasonModelMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class GetBallotRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    session_name: str = None
    access_token: str = None
    number_of_player: int = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBallotRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> GetBallotRequest:
        self.season_name = season_name
        return self

    def with_session_name(self, session_name: str) -> GetBallotRequest:
        self.session_name = session_name
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
            .with_season_name(data.get('seasonName'))\
            .with_session_name(data.get('sessionName'))\
            .with_access_token(data.get('accessToken'))\
            .with_number_of_player(data.get('numberOfPlayer'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "sessionName": self.session_name,
            "accessToken": self.access_token,
            "numberOfPlayer": self.number_of_player,
            "keyId": self.key_id,
        }


class GetBallotByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    season_name: str = None
    session_name: str = None
    user_id: str = None
    number_of_player: int = None
    key_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBallotByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> GetBallotByUserIdRequest:
        self.season_name = season_name
        return self

    def with_session_name(self, session_name: str) -> GetBallotByUserIdRequest:
        self.session_name = session_name
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
            .with_season_name(data.get('seasonName'))\
            .with_session_name(data.get('sessionName'))\
            .with_user_id(data.get('userId'))\
            .with_number_of_player(data.get('numberOfPlayer'))\
            .with_key_id(data.get('keyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "sessionName": self.session_name,
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
    season_name: str = None
    session_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CommitVoteRequest:
        self.namespace_name = namespace_name
        return self

    def with_season_name(self, season_name: str) -> CommitVoteRequest:
        self.season_name = season_name
        return self

    def with_session_name(self, session_name: str) -> CommitVoteRequest:
        self.session_name = session_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
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
            .with_season_name(data.get('seasonName'))\
            .with_session_name(data.get('sessionName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "seasonName": self.season_name,
            "sessionName": self.session_name,
        }