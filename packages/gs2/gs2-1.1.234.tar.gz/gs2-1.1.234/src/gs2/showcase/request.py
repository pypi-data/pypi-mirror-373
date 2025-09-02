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
    buy_script: ScriptSetting = None
    queue_namespace_id: str = None
    key_id: str = None
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

    def with_buy_script(self, buy_script: ScriptSetting) -> CreateNamespaceRequest:
        self.buy_script = buy_script
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> CreateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> CreateNamespaceRequest:
        self.key_id = key_id
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
            .with_buy_script(ScriptSetting.from_dict(data.get('buyScript')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "buyScript": self.buy_script.to_dict() if self.buy_script else None,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
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
    buy_script: ScriptSetting = None
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

    def with_buy_script(self, buy_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.buy_script = buy_script
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
            .with_buy_script(ScriptSetting.from_dict(data.get('buyScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "buyScript": self.buy_script.to_dict() if self.buy_script else None,
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


class DescribeSalesItemMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSalesItemMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSalesItemMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSalesItemMastersRequest:
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
    ) -> Optional[DescribeSalesItemMastersRequest]:
        if data is None:
            return None
        return DescribeSalesItemMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateSalesItemMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None

    def with_namespace_name(self, namespace_name: str) -> CreateSalesItemMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateSalesItemMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateSalesItemMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateSalesItemMasterRequest:
        self.metadata = metadata
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> CreateSalesItemMasterRequest:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> CreateSalesItemMasterRequest:
        self.consume_actions = consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> CreateSalesItemMasterRequest:
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
    ) -> Optional[CreateSalesItemMasterRequest]:
        if data is None:
            return None
        return CreateSalesItemMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
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
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class GetSalesItemMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    sales_item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSalesItemMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_sales_item_name(self, sales_item_name: str) -> GetSalesItemMasterRequest:
        self.sales_item_name = sales_item_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSalesItemMasterRequest]:
        if data is None:
            return None
        return GetSalesItemMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_sales_item_name(data.get('salesItemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "salesItemName": self.sales_item_name,
        }


class UpdateSalesItemMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    sales_item_name: str = None
    description: str = None
    metadata: str = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateSalesItemMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_sales_item_name(self, sales_item_name: str) -> UpdateSalesItemMasterRequest:
        self.sales_item_name = sales_item_name
        return self

    def with_description(self, description: str) -> UpdateSalesItemMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateSalesItemMasterRequest:
        self.metadata = metadata
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> UpdateSalesItemMasterRequest:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> UpdateSalesItemMasterRequest:
        self.consume_actions = consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> UpdateSalesItemMasterRequest:
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
    ) -> Optional[UpdateSalesItemMasterRequest]:
        if data is None:
            return None
        return UpdateSalesItemMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_sales_item_name(data.get('salesItemName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "salesItemName": self.sales_item_name,
            "description": self.description,
            "metadata": self.metadata,
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class DeleteSalesItemMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    sales_item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSalesItemMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_sales_item_name(self, sales_item_name: str) -> DeleteSalesItemMasterRequest:
        self.sales_item_name = sales_item_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteSalesItemMasterRequest]:
        if data is None:
            return None
        return DeleteSalesItemMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_sales_item_name(data.get('salesItemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "salesItemName": self.sales_item_name,
        }


class DescribeSalesItemGroupMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSalesItemGroupMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSalesItemGroupMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSalesItemGroupMastersRequest:
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
    ) -> Optional[DescribeSalesItemGroupMastersRequest]:
        if data is None:
            return None
        return DescribeSalesItemGroupMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateSalesItemGroupMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    sales_item_names: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> CreateSalesItemGroupMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateSalesItemGroupMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateSalesItemGroupMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateSalesItemGroupMasterRequest:
        self.metadata = metadata
        return self

    def with_sales_item_names(self, sales_item_names: List[str]) -> CreateSalesItemGroupMasterRequest:
        self.sales_item_names = sales_item_names
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateSalesItemGroupMasterRequest]:
        if data is None:
            return None
        return CreateSalesItemGroupMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_item_names(None if data.get('salesItemNames') is None else [
                data.get('salesItemNames')[i]
                for i in range(len(data.get('salesItemNames')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "salesItemNames": None if self.sales_item_names is None else [
                self.sales_item_names[i]
                for i in range(len(self.sales_item_names))
            ],
        }


class GetSalesItemGroupMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    sales_item_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSalesItemGroupMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_sales_item_group_name(self, sales_item_group_name: str) -> GetSalesItemGroupMasterRequest:
        self.sales_item_group_name = sales_item_group_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSalesItemGroupMasterRequest]:
        if data is None:
            return None
        return GetSalesItemGroupMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_sales_item_group_name(data.get('salesItemGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "salesItemGroupName": self.sales_item_group_name,
        }


class UpdateSalesItemGroupMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    sales_item_group_name: str = None
    description: str = None
    metadata: str = None
    sales_item_names: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateSalesItemGroupMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_sales_item_group_name(self, sales_item_group_name: str) -> UpdateSalesItemGroupMasterRequest:
        self.sales_item_group_name = sales_item_group_name
        return self

    def with_description(self, description: str) -> UpdateSalesItemGroupMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateSalesItemGroupMasterRequest:
        self.metadata = metadata
        return self

    def with_sales_item_names(self, sales_item_names: List[str]) -> UpdateSalesItemGroupMasterRequest:
        self.sales_item_names = sales_item_names
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateSalesItemGroupMasterRequest]:
        if data is None:
            return None
        return UpdateSalesItemGroupMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_sales_item_group_name(data.get('salesItemGroupName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_item_names(None if data.get('salesItemNames') is None else [
                data.get('salesItemNames')[i]
                for i in range(len(data.get('salesItemNames')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "salesItemGroupName": self.sales_item_group_name,
            "description": self.description,
            "metadata": self.metadata,
            "salesItemNames": None if self.sales_item_names is None else [
                self.sales_item_names[i]
                for i in range(len(self.sales_item_names))
            ],
        }


class DeleteSalesItemGroupMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    sales_item_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSalesItemGroupMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_sales_item_group_name(self, sales_item_group_name: str) -> DeleteSalesItemGroupMasterRequest:
        self.sales_item_group_name = sales_item_group_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteSalesItemGroupMasterRequest]:
        if data is None:
            return None
        return DeleteSalesItemGroupMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_sales_item_group_name(data.get('salesItemGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "salesItemGroupName": self.sales_item_group_name,
        }


class DescribeShowcaseMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeShowcaseMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeShowcaseMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeShowcaseMastersRequest:
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
    ) -> Optional[DescribeShowcaseMastersRequest]:
        if data is None:
            return None
        return DescribeShowcaseMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    display_items: List[DisplayItemMaster] = None
    sales_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateShowcaseMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateShowcaseMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateShowcaseMasterRequest:
        self.metadata = metadata
        return self

    def with_display_items(self, display_items: List[DisplayItemMaster]) -> CreateShowcaseMasterRequest:
        self.display_items = display_items
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> CreateShowcaseMasterRequest:
        self.sales_period_event_id = sales_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateShowcaseMasterRequest]:
        if data is None:
            return None
        return CreateShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_display_items(None if data.get('displayItems') is None else [
                DisplayItemMaster.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')))
            ])\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "displayItems": None if self.display_items is None else [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items))
            ],
            "salesPeriodEventId": self.sales_period_event_id,
        }


class GetShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> GetShowcaseMasterRequest:
        self.showcase_name = showcase_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetShowcaseMasterRequest]:
        if data is None:
            return None
        return GetShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
        }


class UpdateShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    description: str = None
    metadata: str = None
    display_items: List[DisplayItemMaster] = None
    sales_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> UpdateShowcaseMasterRequest:
        self.showcase_name = showcase_name
        return self

    def with_description(self, description: str) -> UpdateShowcaseMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateShowcaseMasterRequest:
        self.metadata = metadata
        return self

    def with_display_items(self, display_items: List[DisplayItemMaster]) -> UpdateShowcaseMasterRequest:
        self.display_items = display_items
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> UpdateShowcaseMasterRequest:
        self.sales_period_event_id = sales_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateShowcaseMasterRequest]:
        if data is None:
            return None
        return UpdateShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_display_items(None if data.get('displayItems') is None else [
                DisplayItemMaster.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')))
            ])\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "description": self.description,
            "metadata": self.metadata,
            "displayItems": None if self.display_items is None else [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items))
            ],
            "salesPeriodEventId": self.sales_period_event_id,
        }


class DeleteShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> DeleteShowcaseMasterRequest:
        self.showcase_name = showcase_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteShowcaseMasterRequest]:
        if data is None:
            return None
        return DeleteShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
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


class GetCurrentShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentShowcaseMasterRequest:
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
    ) -> Optional[GetCurrentShowcaseMasterRequest]:
        if data is None:
            return None
        return GetCurrentShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentShowcaseMasterRequest:
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
    ) -> Optional[PreUpdateCurrentShowcaseMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentShowcaseMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentShowcaseMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentShowcaseMasterRequest:
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
    ) -> Optional[UpdateCurrentShowcaseMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentShowcaseMasterRequest()\
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


class UpdateCurrentShowcaseMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentShowcaseMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentShowcaseMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentShowcaseMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentShowcaseMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeShowcasesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeShowcasesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeShowcasesRequest:
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
    ) -> Optional[DescribeShowcasesRequest]:
        if data is None:
            return None
        return DescribeShowcasesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
        }


class DescribeShowcasesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeShowcasesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeShowcasesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeShowcasesByUserIdRequest:
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
    ) -> Optional[DescribeShowcasesByUserIdRequest]:
        if data is None:
            return None
        return DescribeShowcasesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetShowcaseRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetShowcaseRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> GetShowcaseRequest:
        self.showcase_name = showcase_name
        return self

    def with_access_token(self, access_token: str) -> GetShowcaseRequest:
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
    ) -> Optional[GetShowcaseRequest]:
        if data is None:
            return None
        return GetShowcaseRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "accessToken": self.access_token,
        }


class GetShowcaseByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetShowcaseByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> GetShowcaseByUserIdRequest:
        self.showcase_name = showcase_name
        return self

    def with_user_id(self, user_id: str) -> GetShowcaseByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetShowcaseByUserIdRequest:
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
    ) -> Optional[GetShowcaseByUserIdRequest]:
        if data is None:
            return None
        return GetShowcaseByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class BuyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_id: str = None
    access_token: str = None
    quantity: int = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> BuyRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> BuyRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_id(self, display_item_id: str) -> BuyRequest:
        self.display_item_id = display_item_id
        return self

    def with_access_token(self, access_token: str) -> BuyRequest:
        self.access_token = access_token
        return self

    def with_quantity(self, quantity: int) -> BuyRequest:
        self.quantity = quantity
        return self

    def with_config(self, config: List[Config]) -> BuyRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> BuyRequest:
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
    ) -> Optional[BuyRequest]:
        if data is None:
            return None
        return BuyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_id(data.get('displayItemId'))\
            .with_access_token(data.get('accessToken'))\
            .with_quantity(data.get('quantity'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemId": self.display_item_id,
            "accessToken": self.access_token,
            "quantity": self.quantity,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class BuyByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_id: str = None
    user_id: str = None
    quantity: int = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> BuyByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> BuyByUserIdRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_id(self, display_item_id: str) -> BuyByUserIdRequest:
        self.display_item_id = display_item_id
        return self

    def with_user_id(self, user_id: str) -> BuyByUserIdRequest:
        self.user_id = user_id
        return self

    def with_quantity(self, quantity: int) -> BuyByUserIdRequest:
        self.quantity = quantity
        return self

    def with_config(self, config: List[Config]) -> BuyByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> BuyByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> BuyByUserIdRequest:
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
    ) -> Optional[BuyByUserIdRequest]:
        if data is None:
            return None
        return BuyByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_id(data.get('displayItemId'))\
            .with_user_id(data.get('userId'))\
            .with_quantity(data.get('quantity'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemId": self.display_item_id,
            "userId": self.user_id,
            "quantity": self.quantity,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeRandomShowcaseMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRandomShowcaseMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRandomShowcaseMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRandomShowcaseMastersRequest:
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
    ) -> Optional[DescribeRandomShowcaseMastersRequest]:
        if data is None:
            return None
        return DescribeRandomShowcaseMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRandomShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    maximum_number_of_choice: int = None
    display_items: List[RandomDisplayItemModel] = None
    base_timestamp: int = None
    reset_interval_hours: int = None
    sales_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateRandomShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRandomShowcaseMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRandomShowcaseMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRandomShowcaseMasterRequest:
        self.metadata = metadata
        return self

    def with_maximum_number_of_choice(self, maximum_number_of_choice: int) -> CreateRandomShowcaseMasterRequest:
        self.maximum_number_of_choice = maximum_number_of_choice
        return self

    def with_display_items(self, display_items: List[RandomDisplayItemModel]) -> CreateRandomShowcaseMasterRequest:
        self.display_items = display_items
        return self

    def with_base_timestamp(self, base_timestamp: int) -> CreateRandomShowcaseMasterRequest:
        self.base_timestamp = base_timestamp
        return self

    def with_reset_interval_hours(self, reset_interval_hours: int) -> CreateRandomShowcaseMasterRequest:
        self.reset_interval_hours = reset_interval_hours
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> CreateRandomShowcaseMasterRequest:
        self.sales_period_event_id = sales_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateRandomShowcaseMasterRequest]:
        if data is None:
            return None
        return CreateRandomShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_maximum_number_of_choice(data.get('maximumNumberOfChoice'))\
            .with_display_items(None if data.get('displayItems') is None else [
                RandomDisplayItemModel.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')))
            ])\
            .with_base_timestamp(data.get('baseTimestamp'))\
            .with_reset_interval_hours(data.get('resetIntervalHours'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "maximumNumberOfChoice": self.maximum_number_of_choice,
            "displayItems": None if self.display_items is None else [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items))
            ],
            "baseTimestamp": self.base_timestamp,
            "resetIntervalHours": self.reset_interval_hours,
            "salesPeriodEventId": self.sales_period_event_id,
        }


class GetRandomShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRandomShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> GetRandomShowcaseMasterRequest:
        self.showcase_name = showcase_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRandomShowcaseMasterRequest]:
        if data is None:
            return None
        return GetRandomShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
        }


class UpdateRandomShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    description: str = None
    metadata: str = None
    maximum_number_of_choice: int = None
    display_items: List[RandomDisplayItemModel] = None
    base_timestamp: int = None
    reset_interval_hours: int = None
    sales_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRandomShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> UpdateRandomShowcaseMasterRequest:
        self.showcase_name = showcase_name
        return self

    def with_description(self, description: str) -> UpdateRandomShowcaseMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRandomShowcaseMasterRequest:
        self.metadata = metadata
        return self

    def with_maximum_number_of_choice(self, maximum_number_of_choice: int) -> UpdateRandomShowcaseMasterRequest:
        self.maximum_number_of_choice = maximum_number_of_choice
        return self

    def with_display_items(self, display_items: List[RandomDisplayItemModel]) -> UpdateRandomShowcaseMasterRequest:
        self.display_items = display_items
        return self

    def with_base_timestamp(self, base_timestamp: int) -> UpdateRandomShowcaseMasterRequest:
        self.base_timestamp = base_timestamp
        return self

    def with_reset_interval_hours(self, reset_interval_hours: int) -> UpdateRandomShowcaseMasterRequest:
        self.reset_interval_hours = reset_interval_hours
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> UpdateRandomShowcaseMasterRequest:
        self.sales_period_event_id = sales_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateRandomShowcaseMasterRequest]:
        if data is None:
            return None
        return UpdateRandomShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_maximum_number_of_choice(data.get('maximumNumberOfChoice'))\
            .with_display_items(None if data.get('displayItems') is None else [
                RandomDisplayItemModel.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')))
            ])\
            .with_base_timestamp(data.get('baseTimestamp'))\
            .with_reset_interval_hours(data.get('resetIntervalHours'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "description": self.description,
            "metadata": self.metadata,
            "maximumNumberOfChoice": self.maximum_number_of_choice,
            "displayItems": None if self.display_items is None else [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items))
            ],
            "baseTimestamp": self.base_timestamp,
            "resetIntervalHours": self.reset_interval_hours,
            "salesPeriodEventId": self.sales_period_event_id,
        }


class DeleteRandomShowcaseMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRandomShowcaseMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> DeleteRandomShowcaseMasterRequest:
        self.showcase_name = showcase_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRandomShowcaseMasterRequest]:
        if data is None:
            return None
        return DeleteRandomShowcaseMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
        }


class IncrementPurchaseCountRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_name: str = None
    access_token: str = None
    count: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> IncrementPurchaseCountRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> IncrementPurchaseCountRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_name(self, display_item_name: str) -> IncrementPurchaseCountRequest:
        self.display_item_name = display_item_name
        return self

    def with_access_token(self, access_token: str) -> IncrementPurchaseCountRequest:
        self.access_token = access_token
        return self

    def with_count(self, count: int) -> IncrementPurchaseCountRequest:
        self.count = count
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> IncrementPurchaseCountRequest:
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
    ) -> Optional[IncrementPurchaseCountRequest]:
        if data is None:
            return None
        return IncrementPurchaseCountRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_name(data.get('displayItemName'))\
            .with_access_token(data.get('accessToken'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemName": self.display_item_name,
            "accessToken": self.access_token,
            "count": self.count,
        }


class IncrementPurchaseCountByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_name: str = None
    user_id: str = None
    count: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> IncrementPurchaseCountByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> IncrementPurchaseCountByUserIdRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_name(self, display_item_name: str) -> IncrementPurchaseCountByUserIdRequest:
        self.display_item_name = display_item_name
        return self

    def with_user_id(self, user_id: str) -> IncrementPurchaseCountByUserIdRequest:
        self.user_id = user_id
        return self

    def with_count(self, count: int) -> IncrementPurchaseCountByUserIdRequest:
        self.count = count
        return self

    def with_time_offset_token(self, time_offset_token: str) -> IncrementPurchaseCountByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> IncrementPurchaseCountByUserIdRequest:
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
    ) -> Optional[IncrementPurchaseCountByUserIdRequest]:
        if data is None:
            return None
        return IncrementPurchaseCountByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_name(data.get('displayItemName'))\
            .with_user_id(data.get('userId'))\
            .with_count(data.get('count'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemName": self.display_item_name,
            "userId": self.user_id,
            "count": self.count,
            "timeOffsetToken": self.time_offset_token,
        }


class DecrementPurchaseCountByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_name: str = None
    user_id: str = None
    count: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DecrementPurchaseCountByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> DecrementPurchaseCountByUserIdRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_name(self, display_item_name: str) -> DecrementPurchaseCountByUserIdRequest:
        self.display_item_name = display_item_name
        return self

    def with_user_id(self, user_id: str) -> DecrementPurchaseCountByUserIdRequest:
        self.user_id = user_id
        return self

    def with_count(self, count: int) -> DecrementPurchaseCountByUserIdRequest:
        self.count = count
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DecrementPurchaseCountByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DecrementPurchaseCountByUserIdRequest:
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
    ) -> Optional[DecrementPurchaseCountByUserIdRequest]:
        if data is None:
            return None
        return DecrementPurchaseCountByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_name(data.get('displayItemName'))\
            .with_user_id(data.get('userId'))\
            .with_count(data.get('count'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemName": self.display_item_name,
            "userId": self.user_id,
            "count": self.count,
            "timeOffsetToken": self.time_offset_token,
        }


class IncrementPurchaseCountByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> IncrementPurchaseCountByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> IncrementPurchaseCountByStampTaskRequest:
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
    ) -> Optional[IncrementPurchaseCountByStampTaskRequest]:
        if data is None:
            return None
        return IncrementPurchaseCountByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DecrementPurchaseCountByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> DecrementPurchaseCountByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> DecrementPurchaseCountByStampSheetRequest:
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
    ) -> Optional[DecrementPurchaseCountByStampSheetRequest]:
        if data is None:
            return None
        return DecrementPurchaseCountByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class ForceReDrawByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ForceReDrawByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> ForceReDrawByUserIdRequest:
        self.showcase_name = showcase_name
        return self

    def with_user_id(self, user_id: str) -> ForceReDrawByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ForceReDrawByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ForceReDrawByUserIdRequest:
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
    ) -> Optional[ForceReDrawByUserIdRequest]:
        if data is None:
            return None
        return ForceReDrawByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class ForceReDrawByUserIdByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> ForceReDrawByUserIdByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> ForceReDrawByUserIdByStampSheetRequest:
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
    ) -> Optional[ForceReDrawByUserIdByStampSheetRequest]:
        if data is None:
            return None
        return ForceReDrawByUserIdByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DescribeRandomDisplayItemsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRandomDisplayItemsRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> DescribeRandomDisplayItemsRequest:
        self.showcase_name = showcase_name
        return self

    def with_access_token(self, access_token: str) -> DescribeRandomDisplayItemsRequest:
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
    ) -> Optional[DescribeRandomDisplayItemsRequest]:
        if data is None:
            return None
        return DescribeRandomDisplayItemsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "accessToken": self.access_token,
        }


class DescribeRandomDisplayItemsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRandomDisplayItemsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> DescribeRandomDisplayItemsByUserIdRequest:
        self.showcase_name = showcase_name
        return self

    def with_user_id(self, user_id: str) -> DescribeRandomDisplayItemsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeRandomDisplayItemsByUserIdRequest:
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
    ) -> Optional[DescribeRandomDisplayItemsByUserIdRequest]:
        if data is None:
            return None
        return DescribeRandomDisplayItemsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetRandomDisplayItemRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRandomDisplayItemRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> GetRandomDisplayItemRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_name(self, display_item_name: str) -> GetRandomDisplayItemRequest:
        self.display_item_name = display_item_name
        return self

    def with_access_token(self, access_token: str) -> GetRandomDisplayItemRequest:
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
    ) -> Optional[GetRandomDisplayItemRequest]:
        if data is None:
            return None
        return GetRandomDisplayItemRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_name(data.get('displayItemName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemName": self.display_item_name,
            "accessToken": self.access_token,
        }


class GetRandomDisplayItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRandomDisplayItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> GetRandomDisplayItemByUserIdRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_name(self, display_item_name: str) -> GetRandomDisplayItemByUserIdRequest:
        self.display_item_name = display_item_name
        return self

    def with_user_id(self, user_id: str) -> GetRandomDisplayItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetRandomDisplayItemByUserIdRequest:
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
    ) -> Optional[GetRandomDisplayItemByUserIdRequest]:
        if data is None:
            return None
        return GetRandomDisplayItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_name(data.get('displayItemName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemName": self.display_item_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class RandomShowcaseBuyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_name: str = None
    access_token: str = None
    quantity: int = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RandomShowcaseBuyRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> RandomShowcaseBuyRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_name(self, display_item_name: str) -> RandomShowcaseBuyRequest:
        self.display_item_name = display_item_name
        return self

    def with_access_token(self, access_token: str) -> RandomShowcaseBuyRequest:
        self.access_token = access_token
        return self

    def with_quantity(self, quantity: int) -> RandomShowcaseBuyRequest:
        self.quantity = quantity
        return self

    def with_config(self, config: List[Config]) -> RandomShowcaseBuyRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RandomShowcaseBuyRequest:
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
    ) -> Optional[RandomShowcaseBuyRequest]:
        if data is None:
            return None
        return RandomShowcaseBuyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_name(data.get('displayItemName'))\
            .with_access_token(data.get('accessToken'))\
            .with_quantity(data.get('quantity'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemName": self.display_item_name,
            "accessToken": self.access_token,
            "quantity": self.quantity,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class RandomShowcaseBuyByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    showcase_name: str = None
    display_item_name: str = None
    user_id: str = None
    quantity: int = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RandomShowcaseBuyByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_showcase_name(self, showcase_name: str) -> RandomShowcaseBuyByUserIdRequest:
        self.showcase_name = showcase_name
        return self

    def with_display_item_name(self, display_item_name: str) -> RandomShowcaseBuyByUserIdRequest:
        self.display_item_name = display_item_name
        return self

    def with_user_id(self, user_id: str) -> RandomShowcaseBuyByUserIdRequest:
        self.user_id = user_id
        return self

    def with_quantity(self, quantity: int) -> RandomShowcaseBuyByUserIdRequest:
        self.quantity = quantity
        return self

    def with_config(self, config: List[Config]) -> RandomShowcaseBuyByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> RandomShowcaseBuyByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RandomShowcaseBuyByUserIdRequest:
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
    ) -> Optional[RandomShowcaseBuyByUserIdRequest]:
        if data is None:
            return None
        return RandomShowcaseBuyByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_showcase_name(data.get('showcaseName'))\
            .with_display_item_name(data.get('displayItemName'))\
            .with_user_id(data.get('userId'))\
            .with_quantity(data.get('quantity'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "showcaseName": self.showcase_name,
            "displayItemName": self.display_item_name,
            "userId": self.user_id,
            "quantity": self.quantity,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }