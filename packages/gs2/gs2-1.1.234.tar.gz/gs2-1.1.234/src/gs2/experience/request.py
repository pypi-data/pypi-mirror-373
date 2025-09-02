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
    rank_cap_script_id: str = None
    change_experience_script: ScriptSetting = None
    change_rank_script: ScriptSetting = None
    change_rank_cap_script: ScriptSetting = None
    overflow_experience_script: str = None
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

    def with_rank_cap_script_id(self, rank_cap_script_id: str) -> CreateNamespaceRequest:
        self.rank_cap_script_id = rank_cap_script_id
        return self

    def with_change_experience_script(self, change_experience_script: ScriptSetting) -> CreateNamespaceRequest:
        self.change_experience_script = change_experience_script
        return self

    def with_change_rank_script(self, change_rank_script: ScriptSetting) -> CreateNamespaceRequest:
        self.change_rank_script = change_rank_script
        return self

    def with_change_rank_cap_script(self, change_rank_cap_script: ScriptSetting) -> CreateNamespaceRequest:
        self.change_rank_cap_script = change_rank_cap_script
        return self

    def with_overflow_experience_script(self, overflow_experience_script: str) -> CreateNamespaceRequest:
        self.overflow_experience_script = overflow_experience_script
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
            .with_rank_cap_script_id(data.get('rankCapScriptId'))\
            .with_change_experience_script(ScriptSetting.from_dict(data.get('changeExperienceScript')))\
            .with_change_rank_script(ScriptSetting.from_dict(data.get('changeRankScript')))\
            .with_change_rank_cap_script(ScriptSetting.from_dict(data.get('changeRankCapScript')))\
            .with_overflow_experience_script(data.get('overflowExperienceScript'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "rankCapScriptId": self.rank_cap_script_id,
            "changeExperienceScript": self.change_experience_script.to_dict() if self.change_experience_script else None,
            "changeRankScript": self.change_rank_script.to_dict() if self.change_rank_script else None,
            "changeRankCapScript": self.change_rank_cap_script.to_dict() if self.change_rank_cap_script else None,
            "overflowExperienceScript": self.overflow_experience_script,
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
    rank_cap_script_id: str = None
    change_experience_script: ScriptSetting = None
    change_rank_script: ScriptSetting = None
    change_rank_cap_script: ScriptSetting = None
    overflow_experience_script: str = None
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

    def with_rank_cap_script_id(self, rank_cap_script_id: str) -> UpdateNamespaceRequest:
        self.rank_cap_script_id = rank_cap_script_id
        return self

    def with_change_experience_script(self, change_experience_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.change_experience_script = change_experience_script
        return self

    def with_change_rank_script(self, change_rank_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.change_rank_script = change_rank_script
        return self

    def with_change_rank_cap_script(self, change_rank_cap_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.change_rank_cap_script = change_rank_cap_script
        return self

    def with_overflow_experience_script(self, overflow_experience_script: str) -> UpdateNamespaceRequest:
        self.overflow_experience_script = overflow_experience_script
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
            .with_rank_cap_script_id(data.get('rankCapScriptId'))\
            .with_change_experience_script(ScriptSetting.from_dict(data.get('changeExperienceScript')))\
            .with_change_rank_script(ScriptSetting.from_dict(data.get('changeRankScript')))\
            .with_change_rank_cap_script(ScriptSetting.from_dict(data.get('changeRankCapScript')))\
            .with_overflow_experience_script(data.get('overflowExperienceScript'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "rankCapScriptId": self.rank_cap_script_id,
            "changeExperienceScript": self.change_experience_script.to_dict() if self.change_experience_script else None,
            "changeRankScript": self.change_rank_script.to_dict() if self.change_rank_script else None,
            "changeRankCapScript": self.change_rank_cap_script.to_dict() if self.change_rank_cap_script else None,
            "overflowExperienceScript": self.overflow_experience_script,
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


class DescribeExperienceModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeExperienceModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeExperienceModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeExperienceModelMastersRequest:
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
    ) -> Optional[DescribeExperienceModelMastersRequest]:
        if data is None:
            return None
        return DescribeExperienceModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateExperienceModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    default_experience: int = None
    default_rank_cap: int = None
    max_rank_cap: int = None
    rank_threshold_name: str = None
    acquire_action_rates: List[AcquireActionRate] = None

    def with_namespace_name(self, namespace_name: str) -> CreateExperienceModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateExperienceModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateExperienceModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateExperienceModelMasterRequest:
        self.metadata = metadata
        return self

    def with_default_experience(self, default_experience: int) -> CreateExperienceModelMasterRequest:
        self.default_experience = default_experience
        return self

    def with_default_rank_cap(self, default_rank_cap: int) -> CreateExperienceModelMasterRequest:
        self.default_rank_cap = default_rank_cap
        return self

    def with_max_rank_cap(self, max_rank_cap: int) -> CreateExperienceModelMasterRequest:
        self.max_rank_cap = max_rank_cap
        return self

    def with_rank_threshold_name(self, rank_threshold_name: str) -> CreateExperienceModelMasterRequest:
        self.rank_threshold_name = rank_threshold_name
        return self

    def with_acquire_action_rates(self, acquire_action_rates: List[AcquireActionRate]) -> CreateExperienceModelMasterRequest:
        self.acquire_action_rates = acquire_action_rates
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateExperienceModelMasterRequest]:
        if data is None:
            return None
        return CreateExperienceModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_experience(data.get('defaultExperience'))\
            .with_default_rank_cap(data.get('defaultRankCap'))\
            .with_max_rank_cap(data.get('maxRankCap'))\
            .with_rank_threshold_name(data.get('rankThresholdName'))\
            .with_acquire_action_rates(None if data.get('acquireActionRates') is None else [
                AcquireActionRate.from_dict(data.get('acquireActionRates')[i])
                for i in range(len(data.get('acquireActionRates')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultExperience": self.default_experience,
            "defaultRankCap": self.default_rank_cap,
            "maxRankCap": self.max_rank_cap,
            "rankThresholdName": self.rank_threshold_name,
            "acquireActionRates": None if self.acquire_action_rates is None else [
                self.acquire_action_rates[i].to_dict() if self.acquire_action_rates[i] else None
                for i in range(len(self.acquire_action_rates))
            ],
        }


class GetExperienceModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetExperienceModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> GetExperienceModelMasterRequest:
        self.experience_name = experience_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetExperienceModelMasterRequest]:
        if data is None:
            return None
        return GetExperienceModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
        }


class UpdateExperienceModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None
    description: str = None
    metadata: str = None
    default_experience: int = None
    default_rank_cap: int = None
    max_rank_cap: int = None
    rank_threshold_name: str = None
    acquire_action_rates: List[AcquireActionRate] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateExperienceModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> UpdateExperienceModelMasterRequest:
        self.experience_name = experience_name
        return self

    def with_description(self, description: str) -> UpdateExperienceModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateExperienceModelMasterRequest:
        self.metadata = metadata
        return self

    def with_default_experience(self, default_experience: int) -> UpdateExperienceModelMasterRequest:
        self.default_experience = default_experience
        return self

    def with_default_rank_cap(self, default_rank_cap: int) -> UpdateExperienceModelMasterRequest:
        self.default_rank_cap = default_rank_cap
        return self

    def with_max_rank_cap(self, max_rank_cap: int) -> UpdateExperienceModelMasterRequest:
        self.max_rank_cap = max_rank_cap
        return self

    def with_rank_threshold_name(self, rank_threshold_name: str) -> UpdateExperienceModelMasterRequest:
        self.rank_threshold_name = rank_threshold_name
        return self

    def with_acquire_action_rates(self, acquire_action_rates: List[AcquireActionRate]) -> UpdateExperienceModelMasterRequest:
        self.acquire_action_rates = acquire_action_rates
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateExperienceModelMasterRequest]:
        if data is None:
            return None
        return UpdateExperienceModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_default_experience(data.get('defaultExperience'))\
            .with_default_rank_cap(data.get('defaultRankCap'))\
            .with_max_rank_cap(data.get('maxRankCap'))\
            .with_rank_threshold_name(data.get('rankThresholdName'))\
            .with_acquire_action_rates(None if data.get('acquireActionRates') is None else [
                AcquireActionRate.from_dict(data.get('acquireActionRates')[i])
                for i in range(len(data.get('acquireActionRates')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
            "description": self.description,
            "metadata": self.metadata,
            "defaultExperience": self.default_experience,
            "defaultRankCap": self.default_rank_cap,
            "maxRankCap": self.max_rank_cap,
            "rankThresholdName": self.rank_threshold_name,
            "acquireActionRates": None if self.acquire_action_rates is None else [
                self.acquire_action_rates[i].to_dict() if self.acquire_action_rates[i] else None
                for i in range(len(self.acquire_action_rates))
            ],
        }


class DeleteExperienceModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteExperienceModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> DeleteExperienceModelMasterRequest:
        self.experience_name = experience_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteExperienceModelMasterRequest]:
        if data is None:
            return None
        return DeleteExperienceModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
        }


class DescribeExperienceModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeExperienceModelsRequest:
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
    ) -> Optional[DescribeExperienceModelsRequest]:
        if data is None:
            return None
        return DescribeExperienceModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetExperienceModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetExperienceModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> GetExperienceModelRequest:
        self.experience_name = experience_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetExperienceModelRequest]:
        if data is None:
            return None
        return GetExperienceModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_experience_name(data.get('experienceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
        }


class DescribeThresholdMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeThresholdMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeThresholdMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeThresholdMastersRequest:
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
    ) -> Optional[DescribeThresholdMastersRequest]:
        if data is None:
            return None
        return DescribeThresholdMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateThresholdMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> CreateThresholdMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateThresholdMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateThresholdMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateThresholdMasterRequest:
        self.metadata = metadata
        return self

    def with_values(self, values: List[int]) -> CreateThresholdMasterRequest:
        self.values = values
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateThresholdMasterRequest]:
        if data is None:
            return None
        return CreateThresholdMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class GetThresholdMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    threshold_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetThresholdMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_threshold_name(self, threshold_name: str) -> GetThresholdMasterRequest:
        self.threshold_name = threshold_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetThresholdMasterRequest]:
        if data is None:
            return None
        return GetThresholdMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_threshold_name(data.get('thresholdName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "thresholdName": self.threshold_name,
        }


class UpdateThresholdMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    threshold_name: str = None
    description: str = None
    metadata: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateThresholdMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_threshold_name(self, threshold_name: str) -> UpdateThresholdMasterRequest:
        self.threshold_name = threshold_name
        return self

    def with_description(self, description: str) -> UpdateThresholdMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateThresholdMasterRequest:
        self.metadata = metadata
        return self

    def with_values(self, values: List[int]) -> UpdateThresholdMasterRequest:
        self.values = values
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateThresholdMasterRequest]:
        if data is None:
            return None
        return UpdateThresholdMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_threshold_name(data.get('thresholdName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "thresholdName": self.threshold_name,
            "description": self.description,
            "metadata": self.metadata,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class DeleteThresholdMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    threshold_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteThresholdMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_threshold_name(self, threshold_name: str) -> DeleteThresholdMasterRequest:
        self.threshold_name = threshold_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteThresholdMasterRequest]:
        if data is None:
            return None
        return DeleteThresholdMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_threshold_name(data.get('thresholdName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "thresholdName": self.threshold_name,
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


class GetCurrentExperienceMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentExperienceMasterRequest:
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
    ) -> Optional[GetCurrentExperienceMasterRequest]:
        if data is None:
            return None
        return GetCurrentExperienceMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentExperienceMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentExperienceMasterRequest:
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
    ) -> Optional[PreUpdateCurrentExperienceMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentExperienceMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentExperienceMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentExperienceMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentExperienceMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentExperienceMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentExperienceMasterRequest:
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
    ) -> Optional[UpdateCurrentExperienceMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentExperienceMasterRequest()\
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


class UpdateCurrentExperienceMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentExperienceMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentExperienceMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentExperienceMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentExperienceMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeStatusesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStatusesRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> DescribeStatusesRequest:
        self.experience_name = experience_name
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
            .with_experience_name(data.get('experienceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeStatusesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    experience_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStatusesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_experience_name(self, experience_name: str) -> DescribeStatusesByUserIdRequest:
        self.experience_name = experience_name
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
            .with_experience_name(data.get('experienceName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "experienceName": self.experience_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    experience_name: str = None
    property_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetStatusRequest:
        self.access_token = access_token
        return self

    def with_experience_name(self, experience_name: str) -> GetStatusRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> GetStatusRequest:
        self.property_id = property_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
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
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
        }


class GetStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> GetStatusByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> GetStatusByUserIdRequest:
        self.property_id = property_id
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
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetStatusWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    experience_name: str = None
    property_id: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetStatusWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_experience_name(self, experience_name: str) -> GetStatusWithSignatureRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> GetStatusWithSignatureRequest:
        self.property_id = property_id
        return self

    def with_key_id(self, key_id: str) -> GetStatusWithSignatureRequest:
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
    ) -> Optional[GetStatusWithSignatureRequest]:
        if data is None:
            return None
        return GetStatusWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "keyId": self.key_id,
        }


class GetStatusWithSignatureByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    key_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStatusWithSignatureByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetStatusWithSignatureByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> GetStatusWithSignatureByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> GetStatusWithSignatureByUserIdRequest:
        self.property_id = property_id
        return self

    def with_key_id(self, key_id: str) -> GetStatusWithSignatureByUserIdRequest:
        self.key_id = key_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetStatusWithSignatureByUserIdRequest:
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
    ) -> Optional[GetStatusWithSignatureByUserIdRequest]:
        if data is None:
            return None
        return GetStatusWithSignatureByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_key_id(data.get('keyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "keyId": self.key_id,
            "timeOffsetToken": self.time_offset_token,
        }


class AddExperienceByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    experience_value: int = None
    truncate_experience_when_rank_up: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddExperienceByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AddExperienceByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> AddExperienceByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> AddExperienceByUserIdRequest:
        self.property_id = property_id
        return self

    def with_experience_value(self, experience_value: int) -> AddExperienceByUserIdRequest:
        self.experience_value = experience_value
        return self

    def with_truncate_experience_when_rank_up(self, truncate_experience_when_rank_up: bool) -> AddExperienceByUserIdRequest:
        self.truncate_experience_when_rank_up = truncate_experience_when_rank_up
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AddExperienceByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddExperienceByUserIdRequest:
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
    ) -> Optional[AddExperienceByUserIdRequest]:
        if data is None:
            return None
        return AddExperienceByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_experience_value(data.get('experienceValue'))\
            .with_truncate_experience_when_rank_up(data.get('truncateExperienceWhenRankUp'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "experienceValue": self.experience_value,
            "truncateExperienceWhenRankUp": self.truncate_experience_when_rank_up,
            "timeOffsetToken": self.time_offset_token,
        }


class SubExperienceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    experience_name: str = None
    property_id: str = None
    experience_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SubExperienceRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SubExperienceRequest:
        self.access_token = access_token
        return self

    def with_experience_name(self, experience_name: str) -> SubExperienceRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> SubExperienceRequest:
        self.property_id = property_id
        return self

    def with_experience_value(self, experience_value: int) -> SubExperienceRequest:
        self.experience_value = experience_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SubExperienceRequest:
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
    ) -> Optional[SubExperienceRequest]:
        if data is None:
            return None
        return SubExperienceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_experience_value(data.get('experienceValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "experienceValue": self.experience_value,
        }


class SubExperienceByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    experience_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SubExperienceByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SubExperienceByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> SubExperienceByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> SubExperienceByUserIdRequest:
        self.property_id = property_id
        return self

    def with_experience_value(self, experience_value: int) -> SubExperienceByUserIdRequest:
        self.experience_value = experience_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SubExperienceByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SubExperienceByUserIdRequest:
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
    ) -> Optional[SubExperienceByUserIdRequest]:
        if data is None:
            return None
        return SubExperienceByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_experience_value(data.get('experienceValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "experienceValue": self.experience_value,
            "timeOffsetToken": self.time_offset_token,
        }


class SetExperienceByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    experience_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetExperienceByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SetExperienceByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> SetExperienceByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> SetExperienceByUserIdRequest:
        self.property_id = property_id
        return self

    def with_experience_value(self, experience_value: int) -> SetExperienceByUserIdRequest:
        self.experience_value = experience_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetExperienceByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetExperienceByUserIdRequest:
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
    ) -> Optional[SetExperienceByUserIdRequest]:
        if data is None:
            return None
        return SetExperienceByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_experience_value(data.get('experienceValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "experienceValue": self.experience_value,
            "timeOffsetToken": self.time_offset_token,
        }


class AddRankCapByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    rank_cap_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddRankCapByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AddRankCapByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> AddRankCapByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> AddRankCapByUserIdRequest:
        self.property_id = property_id
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> AddRankCapByUserIdRequest:
        self.rank_cap_value = rank_cap_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AddRankCapByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddRankCapByUserIdRequest:
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
    ) -> Optional[AddRankCapByUserIdRequest]:
        if data is None:
            return None
        return AddRankCapByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_cap_value(data.get('rankCapValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "rankCapValue": self.rank_cap_value,
            "timeOffsetToken": self.time_offset_token,
        }


class SubRankCapRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    experience_name: str = None
    property_id: str = None
    rank_cap_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SubRankCapRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SubRankCapRequest:
        self.access_token = access_token
        return self

    def with_experience_name(self, experience_name: str) -> SubRankCapRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> SubRankCapRequest:
        self.property_id = property_id
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> SubRankCapRequest:
        self.rank_cap_value = rank_cap_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SubRankCapRequest:
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
    ) -> Optional[SubRankCapRequest]:
        if data is None:
            return None
        return SubRankCapRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_cap_value(data.get('rankCapValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "rankCapValue": self.rank_cap_value,
        }


class SubRankCapByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    rank_cap_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SubRankCapByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SubRankCapByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> SubRankCapByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> SubRankCapByUserIdRequest:
        self.property_id = property_id
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> SubRankCapByUserIdRequest:
        self.rank_cap_value = rank_cap_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SubRankCapByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SubRankCapByUserIdRequest:
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
    ) -> Optional[SubRankCapByUserIdRequest]:
        if data is None:
            return None
        return SubRankCapByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_cap_value(data.get('rankCapValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "rankCapValue": self.rank_cap_value,
            "timeOffsetToken": self.time_offset_token,
        }


class SetRankCapByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    rank_cap_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRankCapByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SetRankCapByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> SetRankCapByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> SetRankCapByUserIdRequest:
        self.property_id = property_id
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> SetRankCapByUserIdRequest:
        self.rank_cap_value = rank_cap_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetRankCapByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetRankCapByUserIdRequest:
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
    ) -> Optional[SetRankCapByUserIdRequest]:
        if data is None:
            return None
        return SetRankCapByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_cap_value(data.get('rankCapValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "rankCapValue": self.rank_cap_value,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> DeleteStatusByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> DeleteStatusByUserIdRequest:
        self.property_id = property_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteStatusByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteStatusByUserIdRequest:
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
    ) -> Optional[DeleteStatusByUserIdRequest]:
        if data is None:
            return None
        return DeleteStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyRankRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    experience_name: str = None
    verify_type: str = None
    property_id: str = None
    rank_value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyRankRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyRankRequest:
        self.access_token = access_token
        return self

    def with_experience_name(self, experience_name: str) -> VerifyRankRequest:
        self.experience_name = experience_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyRankRequest:
        self.verify_type = verify_type
        return self

    def with_property_id(self, property_id: str) -> VerifyRankRequest:
        self.property_id = property_id
        return self

    def with_rank_value(self, rank_value: int) -> VerifyRankRequest:
        self.rank_value = rank_value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyRankRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyRankRequest:
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
    ) -> Optional[VerifyRankRequest]:
        if data is None:
            return None
        return VerifyRankRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_experience_name(data.get('experienceName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_value(data.get('rankValue'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "experienceName": self.experience_name,
            "verifyType": self.verify_type,
            "propertyId": self.property_id,
            "rankValue": self.rank_value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyRankByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    verify_type: str = None
    property_id: str = None
    rank_value: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyRankByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyRankByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> VerifyRankByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyRankByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_property_id(self, property_id: str) -> VerifyRankByUserIdRequest:
        self.property_id = property_id
        return self

    def with_rank_value(self, rank_value: int) -> VerifyRankByUserIdRequest:
        self.rank_value = rank_value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyRankByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyRankByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyRankByUserIdRequest:
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
    ) -> Optional[VerifyRankByUserIdRequest]:
        if data is None:
            return None
        return VerifyRankByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_value(data.get('rankValue'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "verifyType": self.verify_type,
            "propertyId": self.property_id,
            "rankValue": self.rank_value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyRankCapRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    experience_name: str = None
    verify_type: str = None
    property_id: str = None
    rank_cap_value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyRankCapRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyRankCapRequest:
        self.access_token = access_token
        return self

    def with_experience_name(self, experience_name: str) -> VerifyRankCapRequest:
        self.experience_name = experience_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyRankCapRequest:
        self.verify_type = verify_type
        return self

    def with_property_id(self, property_id: str) -> VerifyRankCapRequest:
        self.property_id = property_id
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> VerifyRankCapRequest:
        self.rank_cap_value = rank_cap_value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyRankCapRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyRankCapRequest:
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
    ) -> Optional[VerifyRankCapRequest]:
        if data is None:
            return None
        return VerifyRankCapRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_experience_name(data.get('experienceName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_cap_value(data.get('rankCapValue'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "experienceName": self.experience_name,
            "verifyType": self.verify_type,
            "propertyId": self.property_id,
            "rankCapValue": self.rank_cap_value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyRankCapByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    verify_type: str = None
    property_id: str = None
    rank_cap_value: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyRankCapByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyRankCapByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> VerifyRankCapByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyRankCapByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_property_id(self, property_id: str) -> VerifyRankCapByUserIdRequest:
        self.property_id = property_id
        return self

    def with_rank_cap_value(self, rank_cap_value: int) -> VerifyRankCapByUserIdRequest:
        self.rank_cap_value = rank_cap_value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyRankCapByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyRankCapByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyRankCapByUserIdRequest:
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
    ) -> Optional[VerifyRankCapByUserIdRequest]:
        if data is None:
            return None
        return VerifyRankCapByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_property_id(data.get('propertyId'))\
            .with_rank_cap_value(data.get('rankCapValue'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "verifyType": self.verify_type,
            "propertyId": self.property_id,
            "rankCapValue": self.rank_cap_value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class AddExperienceByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AddExperienceByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AddExperienceByStampSheetRequest:
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
    ) -> Optional[AddExperienceByStampSheetRequest]:
        if data is None:
            return None
        return AddExperienceByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetExperienceByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetExperienceByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetExperienceByStampSheetRequest:
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
    ) -> Optional[SetExperienceByStampSheetRequest]:
        if data is None:
            return None
        return SetExperienceByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SubExperienceByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> SubExperienceByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> SubExperienceByStampTaskRequest:
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
    ) -> Optional[SubExperienceByStampTaskRequest]:
        if data is None:
            return None
        return SubExperienceByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class AddRankCapByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AddRankCapByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AddRankCapByStampSheetRequest:
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
    ) -> Optional[AddRankCapByStampSheetRequest]:
        if data is None:
            return None
        return AddRankCapByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SubRankCapByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> SubRankCapByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> SubRankCapByStampTaskRequest:
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
    ) -> Optional[SubRankCapByStampTaskRequest]:
        if data is None:
            return None
        return SubRankCapByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class SetRankCapByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetRankCapByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetRankCapByStampSheetRequest:
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
    ) -> Optional[SetRankCapByStampSheetRequest]:
        if data is None:
            return None
        return SetRankCapByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class MultiplyAcquireActionsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    experience_name: str = None
    property_id: str = None
    rate_name: str = None
    acquire_actions: List[AcquireAction] = None
    base_rate: float = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> MultiplyAcquireActionsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> MultiplyAcquireActionsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_experience_name(self, experience_name: str) -> MultiplyAcquireActionsByUserIdRequest:
        self.experience_name = experience_name
        return self

    def with_property_id(self, property_id: str) -> MultiplyAcquireActionsByUserIdRequest:
        self.property_id = property_id
        return self

    def with_rate_name(self, rate_name: str) -> MultiplyAcquireActionsByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> MultiplyAcquireActionsByUserIdRequest:
        self.acquire_actions = acquire_actions
        return self

    def with_base_rate(self, base_rate: float) -> MultiplyAcquireActionsByUserIdRequest:
        self.base_rate = base_rate
        return self

    def with_time_offset_token(self, time_offset_token: str) -> MultiplyAcquireActionsByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> MultiplyAcquireActionsByUserIdRequest:
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
    ) -> Optional[MultiplyAcquireActionsByUserIdRequest]:
        if data is None:
            return None
        return MultiplyAcquireActionsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_experience_name(data.get('experienceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_rate_name(data.get('rateName'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_base_rate(data.get('baseRate'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "experienceName": self.experience_name,
            "propertyId": self.property_id,
            "rateName": self.rate_name,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "baseRate": self.base_rate,
            "timeOffsetToken": self.time_offset_token,
        }


class MultiplyAcquireActionsByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> MultiplyAcquireActionsByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> MultiplyAcquireActionsByStampSheetRequest:
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
    ) -> Optional[MultiplyAcquireActionsByStampSheetRequest]:
        if data is None:
            return None
        return MultiplyAcquireActionsByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class VerifyRankByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyRankByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyRankByStampTaskRequest:
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
    ) -> Optional[VerifyRankByStampTaskRequest]:
        if data is None:
            return None
        return VerifyRankByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyRankCapByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyRankCapByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyRankCapByStampTaskRequest:
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
    ) -> Optional[VerifyRankCapByStampTaskRequest]:
        if data is None:
            return None
        return VerifyRankCapByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }