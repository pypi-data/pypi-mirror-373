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
    enable_await_exchange: bool = None
    enable_direct_exchange: bool = None
    transaction_setting: TransactionSetting = None
    exchange_script: ScriptSetting = None
    incremental_exchange_script: ScriptSetting = None
    acquire_await_script: ScriptSetting = None
    log_setting: LogSetting = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_enable_await_exchange(self, enable_await_exchange: bool) -> CreateNamespaceRequest:
        self.enable_await_exchange = enable_await_exchange
        return self

    def with_enable_direct_exchange(self, enable_direct_exchange: bool) -> CreateNamespaceRequest:
        self.enable_direct_exchange = enable_direct_exchange
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> CreateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_exchange_script(self, exchange_script: ScriptSetting) -> CreateNamespaceRequest:
        self.exchange_script = exchange_script
        return self

    def with_incremental_exchange_script(self, incremental_exchange_script: ScriptSetting) -> CreateNamespaceRequest:
        self.incremental_exchange_script = incremental_exchange_script
        return self

    def with_acquire_await_script(self, acquire_await_script: ScriptSetting) -> CreateNamespaceRequest:
        self.acquire_await_script = acquire_await_script
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
            .with_enable_await_exchange(data.get('enableAwaitExchange'))\
            .with_enable_direct_exchange(data.get('enableDirectExchange'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_exchange_script(ScriptSetting.from_dict(data.get('exchangeScript')))\
            .with_incremental_exchange_script(ScriptSetting.from_dict(data.get('incrementalExchangeScript')))\
            .with_acquire_await_script(ScriptSetting.from_dict(data.get('acquireAwaitScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "enableAwaitExchange": self.enable_await_exchange,
            "enableDirectExchange": self.enable_direct_exchange,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "exchangeScript": self.exchange_script.to_dict() if self.exchange_script else None,
            "incrementalExchangeScript": self.incremental_exchange_script.to_dict() if self.incremental_exchange_script else None,
            "acquireAwaitScript": self.acquire_await_script.to_dict() if self.acquire_await_script else None,
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
    enable_await_exchange: bool = None
    enable_direct_exchange: bool = None
    transaction_setting: TransactionSetting = None
    exchange_script: ScriptSetting = None
    incremental_exchange_script: ScriptSetting = None
    acquire_await_script: ScriptSetting = None
    log_setting: LogSetting = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_enable_await_exchange(self, enable_await_exchange: bool) -> UpdateNamespaceRequest:
        self.enable_await_exchange = enable_await_exchange
        return self

    def with_enable_direct_exchange(self, enable_direct_exchange: bool) -> UpdateNamespaceRequest:
        self.enable_direct_exchange = enable_direct_exchange
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> UpdateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_exchange_script(self, exchange_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.exchange_script = exchange_script
        return self

    def with_incremental_exchange_script(self, incremental_exchange_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.incremental_exchange_script = incremental_exchange_script
        return self

    def with_acquire_await_script(self, acquire_await_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.acquire_await_script = acquire_await_script
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
            .with_enable_await_exchange(data.get('enableAwaitExchange'))\
            .with_enable_direct_exchange(data.get('enableDirectExchange'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_exchange_script(ScriptSetting.from_dict(data.get('exchangeScript')))\
            .with_incremental_exchange_script(ScriptSetting.from_dict(data.get('incrementalExchangeScript')))\
            .with_acquire_await_script(ScriptSetting.from_dict(data.get('acquireAwaitScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "enableAwaitExchange": self.enable_await_exchange,
            "enableDirectExchange": self.enable_direct_exchange,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "exchangeScript": self.exchange_script.to_dict() if self.exchange_script else None,
            "incrementalExchangeScript": self.incremental_exchange_script.to_dict() if self.incremental_exchange_script else None,
            "acquireAwaitScript": self.acquire_await_script.to_dict() if self.acquire_await_script else None,
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


class DescribeRateModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRateModelsRequest:
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
    ) -> Optional[DescribeRateModelsRequest]:
        if data is None:
            return None
        return DescribeRateModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetRateModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRateModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> GetRateModelRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRateModelRequest]:
        if data is None:
            return None
        return GetRateModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class DescribeRateModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRateModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRateModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRateModelMastersRequest:
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
    ) -> Optional[DescribeRateModelMastersRequest]:
        if data is None:
            return None
        return DescribeRateModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    timing_type: str = None
    lock_time: int = None
    acquire_actions: List[AcquireAction] = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None

    def with_namespace_name(self, namespace_name: str) -> CreateRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRateModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRateModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRateModelMasterRequest:
        self.metadata = metadata
        return self

    def with_timing_type(self, timing_type: str) -> CreateRateModelMasterRequest:
        self.timing_type = timing_type
        return self

    def with_lock_time(self, lock_time: int) -> CreateRateModelMasterRequest:
        self.lock_time = lock_time
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> CreateRateModelMasterRequest:
        self.acquire_actions = acquire_actions
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> CreateRateModelMasterRequest:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> CreateRateModelMasterRequest:
        self.consume_actions = consume_actions
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateRateModelMasterRequest]:
        if data is None:
            return None
        return CreateRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_timing_type(data.get('timingType'))\
            .with_lock_time(data.get('lockTime'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "timingType": self.timing_type,
            "lockTime": self.lock_time,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
        }


class GetRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> GetRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRateModelMasterRequest]:
        if data is None:
            return None
        return GetRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class UpdateRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    description: str = None
    metadata: str = None
    timing_type: str = None
    lock_time: int = None
    acquire_actions: List[AcquireAction] = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> UpdateRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def with_description(self, description: str) -> UpdateRateModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRateModelMasterRequest:
        self.metadata = metadata
        return self

    def with_timing_type(self, timing_type: str) -> UpdateRateModelMasterRequest:
        self.timing_type = timing_type
        return self

    def with_lock_time(self, lock_time: int) -> UpdateRateModelMasterRequest:
        self.lock_time = lock_time
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> UpdateRateModelMasterRequest:
        self.acquire_actions = acquire_actions
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> UpdateRateModelMasterRequest:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> UpdateRateModelMasterRequest:
        self.consume_actions = consume_actions
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateRateModelMasterRequest]:
        if data is None:
            return None
        return UpdateRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_timing_type(data.get('timingType'))\
            .with_lock_time(data.get('lockTime'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "description": self.description,
            "metadata": self.metadata,
            "timingType": self.timing_type,
            "lockTime": self.lock_time,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
        }


class DeleteRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> DeleteRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRateModelMasterRequest]:
        if data is None:
            return None
        return DeleteRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class DescribeIncrementalRateModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeIncrementalRateModelsRequest:
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
    ) -> Optional[DescribeIncrementalRateModelsRequest]:
        if data is None:
            return None
        return DescribeIncrementalRateModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetIncrementalRateModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetIncrementalRateModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> GetIncrementalRateModelRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetIncrementalRateModelRequest]:
        if data is None:
            return None
        return GetIncrementalRateModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class DescribeIncrementalRateModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeIncrementalRateModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeIncrementalRateModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeIncrementalRateModelMastersRequest:
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
    ) -> Optional[DescribeIncrementalRateModelMastersRequest]:
        if data is None:
            return None
        return DescribeIncrementalRateModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateIncrementalRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    consume_action: ConsumeAction = None
    calculate_type: str = None
    base_value: int = None
    coefficient_value: int = None
    calculate_script_id: str = None
    exchange_count_id: str = None
    maximum_exchange_count: int = None
    acquire_actions: List[AcquireAction] = None

    def with_namespace_name(self, namespace_name: str) -> CreateIncrementalRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateIncrementalRateModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateIncrementalRateModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateIncrementalRateModelMasterRequest:
        self.metadata = metadata
        return self

    def with_consume_action(self, consume_action: ConsumeAction) -> CreateIncrementalRateModelMasterRequest:
        self.consume_action = consume_action
        return self

    def with_calculate_type(self, calculate_type: str) -> CreateIncrementalRateModelMasterRequest:
        self.calculate_type = calculate_type
        return self

    def with_base_value(self, base_value: int) -> CreateIncrementalRateModelMasterRequest:
        self.base_value = base_value
        return self

    def with_coefficient_value(self, coefficient_value: int) -> CreateIncrementalRateModelMasterRequest:
        self.coefficient_value = coefficient_value
        return self

    def with_calculate_script_id(self, calculate_script_id: str) -> CreateIncrementalRateModelMasterRequest:
        self.calculate_script_id = calculate_script_id
        return self

    def with_exchange_count_id(self, exchange_count_id: str) -> CreateIncrementalRateModelMasterRequest:
        self.exchange_count_id = exchange_count_id
        return self

    def with_maximum_exchange_count(self, maximum_exchange_count: int) -> CreateIncrementalRateModelMasterRequest:
        self.maximum_exchange_count = maximum_exchange_count
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> CreateIncrementalRateModelMasterRequest:
        self.acquire_actions = acquire_actions
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateIncrementalRateModelMasterRequest]:
        if data is None:
            return None
        return CreateIncrementalRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_consume_action(ConsumeAction.from_dict(data.get('consumeAction')))\
            .with_calculate_type(data.get('calculateType'))\
            .with_base_value(data.get('baseValue'))\
            .with_coefficient_value(data.get('coefficientValue'))\
            .with_calculate_script_id(data.get('calculateScriptId'))\
            .with_exchange_count_id(data.get('exchangeCountId'))\
            .with_maximum_exchange_count(data.get('maximumExchangeCount'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "consumeAction": self.consume_action.to_dict() if self.consume_action else None,
            "calculateType": self.calculate_type,
            "baseValue": self.base_value,
            "coefficientValue": self.coefficient_value,
            "calculateScriptId": self.calculate_script_id,
            "exchangeCountId": self.exchange_count_id,
            "maximumExchangeCount": self.maximum_exchange_count,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class GetIncrementalRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetIncrementalRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> GetIncrementalRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetIncrementalRateModelMasterRequest]:
        if data is None:
            return None
        return GetIncrementalRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class UpdateIncrementalRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    description: str = None
    metadata: str = None
    consume_action: ConsumeAction = None
    calculate_type: str = None
    base_value: int = None
    coefficient_value: int = None
    calculate_script_id: str = None
    exchange_count_id: str = None
    maximum_exchange_count: int = None
    acquire_actions: List[AcquireAction] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateIncrementalRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> UpdateIncrementalRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def with_description(self, description: str) -> UpdateIncrementalRateModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateIncrementalRateModelMasterRequest:
        self.metadata = metadata
        return self

    def with_consume_action(self, consume_action: ConsumeAction) -> UpdateIncrementalRateModelMasterRequest:
        self.consume_action = consume_action
        return self

    def with_calculate_type(self, calculate_type: str) -> UpdateIncrementalRateModelMasterRequest:
        self.calculate_type = calculate_type
        return self

    def with_base_value(self, base_value: int) -> UpdateIncrementalRateModelMasterRequest:
        self.base_value = base_value
        return self

    def with_coefficient_value(self, coefficient_value: int) -> UpdateIncrementalRateModelMasterRequest:
        self.coefficient_value = coefficient_value
        return self

    def with_calculate_script_id(self, calculate_script_id: str) -> UpdateIncrementalRateModelMasterRequest:
        self.calculate_script_id = calculate_script_id
        return self

    def with_exchange_count_id(self, exchange_count_id: str) -> UpdateIncrementalRateModelMasterRequest:
        self.exchange_count_id = exchange_count_id
        return self

    def with_maximum_exchange_count(self, maximum_exchange_count: int) -> UpdateIncrementalRateModelMasterRequest:
        self.maximum_exchange_count = maximum_exchange_count
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> UpdateIncrementalRateModelMasterRequest:
        self.acquire_actions = acquire_actions
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateIncrementalRateModelMasterRequest]:
        if data is None:
            return None
        return UpdateIncrementalRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_consume_action(ConsumeAction.from_dict(data.get('consumeAction')))\
            .with_calculate_type(data.get('calculateType'))\
            .with_base_value(data.get('baseValue'))\
            .with_coefficient_value(data.get('coefficientValue'))\
            .with_calculate_script_id(data.get('calculateScriptId'))\
            .with_exchange_count_id(data.get('exchangeCountId'))\
            .with_maximum_exchange_count(data.get('maximumExchangeCount'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "description": self.description,
            "metadata": self.metadata,
            "consumeAction": self.consume_action.to_dict() if self.consume_action else None,
            "calculateType": self.calculate_type,
            "baseValue": self.base_value,
            "coefficientValue": self.coefficient_value,
            "calculateScriptId": self.calculate_script_id,
            "exchangeCountId": self.exchange_count_id,
            "maximumExchangeCount": self.maximum_exchange_count,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class DeleteIncrementalRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteIncrementalRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> DeleteIncrementalRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteIncrementalRateModelMasterRequest]:
        if data is None:
            return None
        return DeleteIncrementalRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class ExchangeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    access_token: str = None
    count: int = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ExchangeRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> ExchangeRequest:
        self.rate_name = rate_name
        return self

    def with_access_token(self, access_token: str) -> ExchangeRequest:
        self.access_token = access_token
        return self

    def with_count(self, count: int) -> ExchangeRequest:
        self.count = count
        return self

    def with_config(self, config: List[Config]) -> ExchangeRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ExchangeRequest:
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
    ) -> Optional[ExchangeRequest]:
        if data is None:
            return None
        return ExchangeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_access_token(data.get('accessToken'))\
            .with_count(data.get('count'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "accessToken": self.access_token,
            "count": self.count,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class ExchangeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    user_id: str = None
    count: int = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ExchangeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> ExchangeByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_user_id(self, user_id: str) -> ExchangeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_count(self, count: int) -> ExchangeByUserIdRequest:
        self.count = count
        return self

    def with_config(self, config: List[Config]) -> ExchangeByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ExchangeByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ExchangeByUserIdRequest:
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
    ) -> Optional[ExchangeByUserIdRequest]:
        if data is None:
            return None
        return ExchangeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_user_id(data.get('userId'))\
            .with_count(data.get('count'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "userId": self.user_id,
            "count": self.count,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class ExchangeByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> ExchangeByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> ExchangeByStampSheetRequest:
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
    ) -> Optional[ExchangeByStampSheetRequest]:
        if data is None:
            return None
        return ExchangeByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class IncrementalExchangeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    access_token: str = None
    count: int = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> IncrementalExchangeRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> IncrementalExchangeRequest:
        self.rate_name = rate_name
        return self

    def with_access_token(self, access_token: str) -> IncrementalExchangeRequest:
        self.access_token = access_token
        return self

    def with_count(self, count: int) -> IncrementalExchangeRequest:
        self.count = count
        return self

    def with_config(self, config: List[Config]) -> IncrementalExchangeRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> IncrementalExchangeRequest:
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
    ) -> Optional[IncrementalExchangeRequest]:
        if data is None:
            return None
        return IncrementalExchangeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_access_token(data.get('accessToken'))\
            .with_count(data.get('count'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "accessToken": self.access_token,
            "count": self.count,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class IncrementalExchangeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    user_id: str = None
    count: int = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> IncrementalExchangeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> IncrementalExchangeByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_user_id(self, user_id: str) -> IncrementalExchangeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_count(self, count: int) -> IncrementalExchangeByUserIdRequest:
        self.count = count
        return self

    def with_config(self, config: List[Config]) -> IncrementalExchangeByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> IncrementalExchangeByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> IncrementalExchangeByUserIdRequest:
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
    ) -> Optional[IncrementalExchangeByUserIdRequest]:
        if data is None:
            return None
        return IncrementalExchangeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_user_id(data.get('userId'))\
            .with_count(data.get('count'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "userId": self.user_id,
            "count": self.count,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class IncrementalExchangeByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> IncrementalExchangeByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> IncrementalExchangeByStampSheetRequest:
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
    ) -> Optional[IncrementalExchangeByStampSheetRequest]:
        if data is None:
            return None
        return IncrementalExchangeByStampSheetRequest()\
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


class GetCurrentRateMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentRateMasterRequest:
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
    ) -> Optional[GetCurrentRateMasterRequest]:
        if data is None:
            return None
        return GetCurrentRateMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentRateMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentRateMasterRequest:
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
    ) -> Optional[PreUpdateCurrentRateMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentRateMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentRateMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRateMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentRateMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentRateMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentRateMasterRequest:
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
    ) -> Optional[UpdateCurrentRateMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentRateMasterRequest()\
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


class UpdateCurrentRateMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRateMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentRateMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentRateMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentRateMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class CreateAwaitByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    rate_name: str = None
    count: int = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateAwaitByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateAwaitByUserIdRequest:
        self.user_id = user_id
        return self

    def with_rate_name(self, rate_name: str) -> CreateAwaitByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_count(self, count: int) -> CreateAwaitByUserIdRequest:
        self.count = count
        return self

    def with_config(self, config: List[Config]) -> CreateAwaitByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreateAwaitByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateAwaitByUserIdRequest:
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
    ) -> Optional[CreateAwaitByUserIdRequest]:
        if data is None:
            return None
        return CreateAwaitByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_rate_name(data.get('rateName'))\
            .with_count(data.get('count'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rateName": self.rate_name,
            "count": self.count,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeAwaitsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    rate_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeAwaitsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeAwaitsRequest:
        self.access_token = access_token
        return self

    def with_rate_name(self, rate_name: str) -> DescribeAwaitsRequest:
        self.rate_name = rate_name
        return self

    def with_page_token(self, page_token: str) -> DescribeAwaitsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeAwaitsRequest:
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
    ) -> Optional[DescribeAwaitsRequest]:
        if data is None:
            return None
        return DescribeAwaitsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_rate_name(data.get('rateName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rateName": self.rate_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeAwaitsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    rate_name: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeAwaitsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeAwaitsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_rate_name(self, rate_name: str) -> DescribeAwaitsByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_page_token(self, page_token: str) -> DescribeAwaitsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeAwaitsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeAwaitsByUserIdRequest:
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
    ) -> Optional[DescribeAwaitsByUserIdRequest]:
        if data is None:
            return None
        return DescribeAwaitsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_rate_name(data.get('rateName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rateName": self.rate_name,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetAwaitRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    await_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetAwaitRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetAwaitRequest:
        self.access_token = access_token
        return self

    def with_await_name(self, await_name: str) -> GetAwaitRequest:
        self.await_name = await_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetAwaitRequest]:
        if data is None:
            return None
        return GetAwaitRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_await_name(data.get('awaitName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "awaitName": self.await_name,
        }


class GetAwaitByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    await_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetAwaitByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetAwaitByUserIdRequest:
        self.user_id = user_id
        return self

    def with_await_name(self, await_name: str) -> GetAwaitByUserIdRequest:
        self.await_name = await_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetAwaitByUserIdRequest:
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
    ) -> Optional[GetAwaitByUserIdRequest]:
        if data is None:
            return None
        return GetAwaitByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_await_name(data.get('awaitName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "awaitName": self.await_name,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    await_name: str = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> AcquireRequest:
        self.access_token = access_token
        return self

    def with_await_name(self, await_name: str) -> AcquireRequest:
        self.await_name = await_name
        return self

    def with_config(self, config: List[Config]) -> AcquireRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireRequest:
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
    ) -> Optional[AcquireRequest]:
        if data is None:
            return None
        return AcquireRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_await_name(data.get('awaitName'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "awaitName": self.await_name,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class AcquireByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    await_name: str = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AcquireByUserIdRequest:
        self.user_id = user_id
        return self

    def with_await_name(self, await_name: str) -> AcquireByUserIdRequest:
        self.await_name = await_name
        return self

    def with_config(self, config: List[Config]) -> AcquireByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcquireByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireByUserIdRequest:
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
    ) -> Optional[AcquireByUserIdRequest]:
        if data is None:
            return None
        return AcquireByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_await_name(data.get('awaitName'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "awaitName": self.await_name,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireForceByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    await_name: str = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireForceByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AcquireForceByUserIdRequest:
        self.user_id = user_id
        return self

    def with_await_name(self, await_name: str) -> AcquireForceByUserIdRequest:
        self.await_name = await_name
        return self

    def with_config(self, config: List[Config]) -> AcquireForceByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcquireForceByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireForceByUserIdRequest:
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
    ) -> Optional[AcquireForceByUserIdRequest]:
        if data is None:
            return None
        return AcquireForceByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_await_name(data.get('awaitName'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "awaitName": self.await_name,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class SkipByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    await_name: str = None
    skip_type: str = None
    minutes: int = None
    rate: float = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SkipByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SkipByUserIdRequest:
        self.user_id = user_id
        return self

    def with_await_name(self, await_name: str) -> SkipByUserIdRequest:
        self.await_name = await_name
        return self

    def with_skip_type(self, skip_type: str) -> SkipByUserIdRequest:
        self.skip_type = skip_type
        return self

    def with_minutes(self, minutes: int) -> SkipByUserIdRequest:
        self.minutes = minutes
        return self

    def with_rate(self, rate: float) -> SkipByUserIdRequest:
        self.rate = rate
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SkipByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SkipByUserIdRequest:
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
    ) -> Optional[SkipByUserIdRequest]:
        if data is None:
            return None
        return SkipByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_await_name(data.get('awaitName'))\
            .with_skip_type(data.get('skipType'))\
            .with_minutes(data.get('minutes'))\
            .with_rate(data.get('rate'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "awaitName": self.await_name,
            "skipType": self.skip_type,
            "minutes": self.minutes,
            "rate": self.rate,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteAwaitRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    await_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteAwaitRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteAwaitRequest:
        self.access_token = access_token
        return self

    def with_await_name(self, await_name: str) -> DeleteAwaitRequest:
        self.await_name = await_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteAwaitRequest:
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
    ) -> Optional[DeleteAwaitRequest]:
        if data is None:
            return None
        return DeleteAwaitRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_await_name(data.get('awaitName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "awaitName": self.await_name,
        }


class DeleteAwaitByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    await_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteAwaitByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteAwaitByUserIdRequest:
        self.user_id = user_id
        return self

    def with_await_name(self, await_name: str) -> DeleteAwaitByUserIdRequest:
        self.await_name = await_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteAwaitByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteAwaitByUserIdRequest:
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
    ) -> Optional[DeleteAwaitByUserIdRequest]:
        if data is None:
            return None
        return DeleteAwaitByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_await_name(data.get('awaitName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "awaitName": self.await_name,
            "timeOffsetToken": self.time_offset_token,
        }


class CreateAwaitByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> CreateAwaitByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> CreateAwaitByStampSheetRequest:
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
    ) -> Optional[CreateAwaitByStampSheetRequest]:
        if data is None:
            return None
        return CreateAwaitByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class AcquireForceByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireForceByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AcquireForceByStampSheetRequest:
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
    ) -> Optional[AcquireForceByStampSheetRequest]:
        if data is None:
            return None
        return AcquireForceByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SkipByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SkipByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SkipByStampSheetRequest:
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
    ) -> Optional[SkipByStampSheetRequest]:
        if data is None:
            return None
        return SkipByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DeleteAwaitByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> DeleteAwaitByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> DeleteAwaitByStampTaskRequest:
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
    ) -> Optional[DeleteAwaitByStampTaskRequest]:
        if data is None:
            return None
        return DeleteAwaitByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }