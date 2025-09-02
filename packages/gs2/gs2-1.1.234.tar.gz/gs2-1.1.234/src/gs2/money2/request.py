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
    currency_usage_priority: str = None
    description: str = None
    shared_free_currency: bool = None
    platform_setting: PlatformSetting = None
    deposit_balance_script: ScriptSetting = None
    withdraw_balance_script: ScriptSetting = None
    verify_receipt_script: ScriptSetting = None
    subscribe_script: str = None
    renew_script: str = None
    unsubscribe_script: str = None
    take_over_script: ScriptSetting = None
    change_subscription_status_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_currency_usage_priority(self, currency_usage_priority: str) -> CreateNamespaceRequest:
        self.currency_usage_priority = currency_usage_priority
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_shared_free_currency(self, shared_free_currency: bool) -> CreateNamespaceRequest:
        self.shared_free_currency = shared_free_currency
        return self

    def with_platform_setting(self, platform_setting: PlatformSetting) -> CreateNamespaceRequest:
        self.platform_setting = platform_setting
        return self

    def with_deposit_balance_script(self, deposit_balance_script: ScriptSetting) -> CreateNamespaceRequest:
        self.deposit_balance_script = deposit_balance_script
        return self

    def with_withdraw_balance_script(self, withdraw_balance_script: ScriptSetting) -> CreateNamespaceRequest:
        self.withdraw_balance_script = withdraw_balance_script
        return self

    def with_verify_receipt_script(self, verify_receipt_script: ScriptSetting) -> CreateNamespaceRequest:
        self.verify_receipt_script = verify_receipt_script
        return self

    def with_subscribe_script(self, subscribe_script: str) -> CreateNamespaceRequest:
        self.subscribe_script = subscribe_script
        return self

    def with_renew_script(self, renew_script: str) -> CreateNamespaceRequest:
        self.renew_script = renew_script
        return self

    def with_unsubscribe_script(self, unsubscribe_script: str) -> CreateNamespaceRequest:
        self.unsubscribe_script = unsubscribe_script
        return self

    def with_take_over_script(self, take_over_script: ScriptSetting) -> CreateNamespaceRequest:
        self.take_over_script = take_over_script
        return self

    def with_change_subscription_status_notification(self, change_subscription_status_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.change_subscription_status_notification = change_subscription_status_notification
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
            .with_currency_usage_priority(data.get('currencyUsagePriority'))\
            .with_description(data.get('description'))\
            .with_shared_free_currency(data.get('sharedFreeCurrency'))\
            .with_platform_setting(PlatformSetting.from_dict(data.get('platformSetting')))\
            .with_deposit_balance_script(ScriptSetting.from_dict(data.get('depositBalanceScript')))\
            .with_withdraw_balance_script(ScriptSetting.from_dict(data.get('withdrawBalanceScript')))\
            .with_verify_receipt_script(ScriptSetting.from_dict(data.get('verifyReceiptScript')))\
            .with_subscribe_script(data.get('subscribeScript'))\
            .with_renew_script(data.get('renewScript'))\
            .with_unsubscribe_script(data.get('unsubscribeScript'))\
            .with_take_over_script(ScriptSetting.from_dict(data.get('takeOverScript')))\
            .with_change_subscription_status_notification(NotificationSetting.from_dict(data.get('changeSubscriptionStatusNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "currencyUsagePriority": self.currency_usage_priority,
            "description": self.description,
            "sharedFreeCurrency": self.shared_free_currency,
            "platformSetting": self.platform_setting.to_dict() if self.platform_setting else None,
            "depositBalanceScript": self.deposit_balance_script.to_dict() if self.deposit_balance_script else None,
            "withdrawBalanceScript": self.withdraw_balance_script.to_dict() if self.withdraw_balance_script else None,
            "verifyReceiptScript": self.verify_receipt_script.to_dict() if self.verify_receipt_script else None,
            "subscribeScript": self.subscribe_script,
            "renewScript": self.renew_script,
            "unsubscribeScript": self.unsubscribe_script,
            "takeOverScript": self.take_over_script.to_dict() if self.take_over_script else None,
            "changeSubscriptionStatusNotification": self.change_subscription_status_notification.to_dict() if self.change_subscription_status_notification else None,
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
    currency_usage_priority: str = None
    description: str = None
    platform_setting: PlatformSetting = None
    deposit_balance_script: ScriptSetting = None
    withdraw_balance_script: ScriptSetting = None
    verify_receipt_script: ScriptSetting = None
    subscribe_script: str = None
    renew_script: str = None
    unsubscribe_script: str = None
    take_over_script: ScriptSetting = None
    change_subscription_status_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_currency_usage_priority(self, currency_usage_priority: str) -> UpdateNamespaceRequest:
        self.currency_usage_priority = currency_usage_priority
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_platform_setting(self, platform_setting: PlatformSetting) -> UpdateNamespaceRequest:
        self.platform_setting = platform_setting
        return self

    def with_deposit_balance_script(self, deposit_balance_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.deposit_balance_script = deposit_balance_script
        return self

    def with_withdraw_balance_script(self, withdraw_balance_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.withdraw_balance_script = withdraw_balance_script
        return self

    def with_verify_receipt_script(self, verify_receipt_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.verify_receipt_script = verify_receipt_script
        return self

    def with_subscribe_script(self, subscribe_script: str) -> UpdateNamespaceRequest:
        self.subscribe_script = subscribe_script
        return self

    def with_renew_script(self, renew_script: str) -> UpdateNamespaceRequest:
        self.renew_script = renew_script
        return self

    def with_unsubscribe_script(self, unsubscribe_script: str) -> UpdateNamespaceRequest:
        self.unsubscribe_script = unsubscribe_script
        return self

    def with_take_over_script(self, take_over_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.take_over_script = take_over_script
        return self

    def with_change_subscription_status_notification(self, change_subscription_status_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.change_subscription_status_notification = change_subscription_status_notification
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
            .with_currency_usage_priority(data.get('currencyUsagePriority'))\
            .with_description(data.get('description'))\
            .with_platform_setting(PlatformSetting.from_dict(data.get('platformSetting')))\
            .with_deposit_balance_script(ScriptSetting.from_dict(data.get('depositBalanceScript')))\
            .with_withdraw_balance_script(ScriptSetting.from_dict(data.get('withdrawBalanceScript')))\
            .with_verify_receipt_script(ScriptSetting.from_dict(data.get('verifyReceiptScript')))\
            .with_subscribe_script(data.get('subscribeScript'))\
            .with_renew_script(data.get('renewScript'))\
            .with_unsubscribe_script(data.get('unsubscribeScript'))\
            .with_take_over_script(ScriptSetting.from_dict(data.get('takeOverScript')))\
            .with_change_subscription_status_notification(NotificationSetting.from_dict(data.get('changeSubscriptionStatusNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "currencyUsagePriority": self.currency_usage_priority,
            "description": self.description,
            "platformSetting": self.platform_setting.to_dict() if self.platform_setting else None,
            "depositBalanceScript": self.deposit_balance_script.to_dict() if self.deposit_balance_script else None,
            "withdrawBalanceScript": self.withdraw_balance_script.to_dict() if self.withdraw_balance_script else None,
            "verifyReceiptScript": self.verify_receipt_script.to_dict() if self.verify_receipt_script else None,
            "subscribeScript": self.subscribe_script,
            "renewScript": self.renew_script,
            "unsubscribeScript": self.unsubscribe_script,
            "takeOverScript": self.take_over_script.to_dict() if self.take_over_script else None,
            "changeSubscriptionStatusNotification": self.change_subscription_status_notification.to_dict() if self.change_subscription_status_notification else None,
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


class DescribeWalletsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeWalletsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeWalletsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeWalletsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeWalletsRequest:
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
    ) -> Optional[DescribeWalletsRequest]:
        if data is None:
            return None
        return DescribeWalletsRequest()\
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


class DescribeWalletsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeWalletsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeWalletsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeWalletsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeWalletsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeWalletsByUserIdRequest:
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
    ) -> Optional[DescribeWalletsByUserIdRequest]:
        if data is None:
            return None
        return DescribeWalletsByUserIdRequest()\
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


class GetWalletRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    slot: int = None

    def with_namespace_name(self, namespace_name: str) -> GetWalletRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetWalletRequest:
        self.access_token = access_token
        return self

    def with_slot(self, slot: int) -> GetWalletRequest:
        self.slot = slot
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetWalletRequest]:
        if data is None:
            return None
        return GetWalletRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_slot(data.get('slot'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "slot": self.slot,
        }


class GetWalletByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    slot: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetWalletByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetWalletByUserIdRequest:
        self.user_id = user_id
        return self

    def with_slot(self, slot: int) -> GetWalletByUserIdRequest:
        self.slot = slot
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetWalletByUserIdRequest:
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
    ) -> Optional[GetWalletByUserIdRequest]:
        if data is None:
            return None
        return GetWalletByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_slot(data.get('slot'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "slot": self.slot,
            "timeOffsetToken": self.time_offset_token,
        }


class DepositByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    slot: int = None
    deposit_transactions: List[DepositTransaction] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DepositByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DepositByUserIdRequest:
        self.user_id = user_id
        return self

    def with_slot(self, slot: int) -> DepositByUserIdRequest:
        self.slot = slot
        return self

    def with_deposit_transactions(self, deposit_transactions: List[DepositTransaction]) -> DepositByUserIdRequest:
        self.deposit_transactions = deposit_transactions
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DepositByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DepositByUserIdRequest:
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
    ) -> Optional[DepositByUserIdRequest]:
        if data is None:
            return None
        return DepositByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_slot(data.get('slot'))\
            .with_deposit_transactions(None if data.get('depositTransactions') is None else [
                DepositTransaction.from_dict(data.get('depositTransactions')[i])
                for i in range(len(data.get('depositTransactions')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "slot": self.slot,
            "depositTransactions": None if self.deposit_transactions is None else [
                self.deposit_transactions[i].to_dict() if self.deposit_transactions[i] else None
                for i in range(len(self.deposit_transactions))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class WithdrawRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    slot: int = None
    withdraw_count: int = None
    paid_only: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> WithdrawRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> WithdrawRequest:
        self.access_token = access_token
        return self

    def with_slot(self, slot: int) -> WithdrawRequest:
        self.slot = slot
        return self

    def with_withdraw_count(self, withdraw_count: int) -> WithdrawRequest:
        self.withdraw_count = withdraw_count
        return self

    def with_paid_only(self, paid_only: bool) -> WithdrawRequest:
        self.paid_only = paid_only
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> WithdrawRequest:
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
    ) -> Optional[WithdrawRequest]:
        if data is None:
            return None
        return WithdrawRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_slot(data.get('slot'))\
            .with_withdraw_count(data.get('withdrawCount'))\
            .with_paid_only(data.get('paidOnly'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "slot": self.slot,
            "withdrawCount": self.withdraw_count,
            "paidOnly": self.paid_only,
        }


class WithdrawByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    slot: int = None
    withdraw_count: int = None
    paid_only: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> WithdrawByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> WithdrawByUserIdRequest:
        self.user_id = user_id
        return self

    def with_slot(self, slot: int) -> WithdrawByUserIdRequest:
        self.slot = slot
        return self

    def with_withdraw_count(self, withdraw_count: int) -> WithdrawByUserIdRequest:
        self.withdraw_count = withdraw_count
        return self

    def with_paid_only(self, paid_only: bool) -> WithdrawByUserIdRequest:
        self.paid_only = paid_only
        return self

    def with_time_offset_token(self, time_offset_token: str) -> WithdrawByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> WithdrawByUserIdRequest:
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
    ) -> Optional[WithdrawByUserIdRequest]:
        if data is None:
            return None
        return WithdrawByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_slot(data.get('slot'))\
            .with_withdraw_count(data.get('withdrawCount'))\
            .with_paid_only(data.get('paidOnly'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "slot": self.slot,
            "withdrawCount": self.withdraw_count,
            "paidOnly": self.paid_only,
            "timeOffsetToken": self.time_offset_token,
        }


class DepositByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> DepositByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> DepositByStampSheetRequest:
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
    ) -> Optional[DepositByStampSheetRequest]:
        if data is None:
            return None
        return DepositByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class WithdrawByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> WithdrawByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> WithdrawByStampTaskRequest:
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
    ) -> Optional[WithdrawByStampTaskRequest]:
        if data is None:
            return None
        return WithdrawByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeEventsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    begin: int = None
    end: int = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeEventsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeEventsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_begin(self, begin: int) -> DescribeEventsByUserIdRequest:
        self.begin = begin
        return self

    def with_end(self, end: int) -> DescribeEventsByUserIdRequest:
        self.end = end
        return self

    def with_page_token(self, page_token: str) -> DescribeEventsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeEventsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeEventsByUserIdRequest:
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
    ) -> Optional[DescribeEventsByUserIdRequest]:
        if data is None:
            return None
        return DescribeEventsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_begin(data.get('begin'))\
            .with_end(data.get('end'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "begin": self.begin,
            "end": self.end,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetEventByTransactionIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    transaction_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetEventByTransactionIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_transaction_id(self, transaction_id: str) -> GetEventByTransactionIdRequest:
        self.transaction_id = transaction_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetEventByTransactionIdRequest]:
        if data is None:
            return None
        return GetEventByTransactionIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "transactionId": self.transaction_id,
        }


class VerifyReceiptRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    content_name: str = None
    receipt: Receipt = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyReceiptRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyReceiptRequest:
        self.access_token = access_token
        return self

    def with_content_name(self, content_name: str) -> VerifyReceiptRequest:
        self.content_name = content_name
        return self

    def with_receipt(self, receipt: Receipt) -> VerifyReceiptRequest:
        self.receipt = receipt
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyReceiptRequest:
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
    ) -> Optional[VerifyReceiptRequest]:
        if data is None:
            return None
        return VerifyReceiptRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_content_name(data.get('contentName'))\
            .with_receipt(Receipt.from_dict(data.get('receipt')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "contentName": self.content_name,
            "receipt": self.receipt.to_dict() if self.receipt else None,
        }


class VerifyReceiptByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    content_name: str = None
    receipt: Receipt = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyReceiptByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyReceiptByUserIdRequest:
        self.user_id = user_id
        return self

    def with_content_name(self, content_name: str) -> VerifyReceiptByUserIdRequest:
        self.content_name = content_name
        return self

    def with_receipt(self, receipt: Receipt) -> VerifyReceiptByUserIdRequest:
        self.receipt = receipt
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyReceiptByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyReceiptByUserIdRequest:
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
    ) -> Optional[VerifyReceiptByUserIdRequest]:
        if data is None:
            return None
        return VerifyReceiptByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_content_name(data.get('contentName'))\
            .with_receipt(Receipt.from_dict(data.get('receipt')))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "contentName": self.content_name,
            "receipt": self.receipt.to_dict() if self.receipt else None,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyReceiptByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyReceiptByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyReceiptByStampTaskRequest:
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
    ) -> Optional[VerifyReceiptByStampTaskRequest]:
        if data is None:
            return None
        return VerifyReceiptByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeSubscriptionStatusesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscriptionStatusesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSubscriptionStatusesRequest:
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
    ) -> Optional[DescribeSubscriptionStatusesRequest]:
        if data is None:
            return None
        return DescribeSubscriptionStatusesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
        }


class DescribeSubscriptionStatusesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSubscriptionStatusesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSubscriptionStatusesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeSubscriptionStatusesByUserIdRequest:
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
    ) -> Optional[DescribeSubscriptionStatusesByUserIdRequest]:
        if data is None:
            return None
        return DescribeSubscriptionStatusesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetSubscriptionStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    content_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscriptionStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetSubscriptionStatusRequest:
        self.access_token = access_token
        return self

    def with_content_name(self, content_name: str) -> GetSubscriptionStatusRequest:
        self.content_name = content_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSubscriptionStatusRequest]:
        if data is None:
            return None
        return GetSubscriptionStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_content_name(data.get('contentName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "contentName": self.content_name,
        }


class GetSubscriptionStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    content_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSubscriptionStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetSubscriptionStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_content_name(self, content_name: str) -> GetSubscriptionStatusByUserIdRequest:
        self.content_name = content_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetSubscriptionStatusByUserIdRequest:
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
    ) -> Optional[GetSubscriptionStatusByUserIdRequest]:
        if data is None:
            return None
        return GetSubscriptionStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_content_name(data.get('contentName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "contentName": self.content_name,
            "timeOffsetToken": self.time_offset_token,
        }


class AllocateSubscriptionStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    receipt: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AllocateSubscriptionStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> AllocateSubscriptionStatusRequest:
        self.access_token = access_token
        return self

    def with_receipt(self, receipt: str) -> AllocateSubscriptionStatusRequest:
        self.receipt = receipt
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AllocateSubscriptionStatusRequest:
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
    ) -> Optional[AllocateSubscriptionStatusRequest]:
        if data is None:
            return None
        return AllocateSubscriptionStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_receipt(data.get('receipt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "receipt": self.receipt,
        }


class AllocateSubscriptionStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    receipt: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AllocateSubscriptionStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AllocateSubscriptionStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_receipt(self, receipt: str) -> AllocateSubscriptionStatusByUserIdRequest:
        self.receipt = receipt
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AllocateSubscriptionStatusByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AllocateSubscriptionStatusByUserIdRequest:
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
    ) -> Optional[AllocateSubscriptionStatusByUserIdRequest]:
        if data is None:
            return None
        return AllocateSubscriptionStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_receipt(data.get('receipt'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "receipt": self.receipt,
            "timeOffsetToken": self.time_offset_token,
        }


class TakeoverSubscriptionStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    receipt: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> TakeoverSubscriptionStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> TakeoverSubscriptionStatusRequest:
        self.access_token = access_token
        return self

    def with_receipt(self, receipt: str) -> TakeoverSubscriptionStatusRequest:
        self.receipt = receipt
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> TakeoverSubscriptionStatusRequest:
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
    ) -> Optional[TakeoverSubscriptionStatusRequest]:
        if data is None:
            return None
        return TakeoverSubscriptionStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_receipt(data.get('receipt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "receipt": self.receipt,
        }


class TakeoverSubscriptionStatusByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    receipt: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> TakeoverSubscriptionStatusByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> TakeoverSubscriptionStatusByUserIdRequest:
        self.user_id = user_id
        return self

    def with_receipt(self, receipt: str) -> TakeoverSubscriptionStatusByUserIdRequest:
        self.receipt = receipt
        return self

    def with_time_offset_token(self, time_offset_token: str) -> TakeoverSubscriptionStatusByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> TakeoverSubscriptionStatusByUserIdRequest:
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
    ) -> Optional[TakeoverSubscriptionStatusByUserIdRequest]:
        if data is None:
            return None
        return TakeoverSubscriptionStatusByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_receipt(data.get('receipt'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "receipt": self.receipt,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeRefundHistoriesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRefundHistoriesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeRefundHistoriesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeRefundHistoriesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRefundHistoriesByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeRefundHistoriesByUserIdRequest:
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
    ) -> Optional[DescribeRefundHistoriesByUserIdRequest]:
        if data is None:
            return None
        return DescribeRefundHistoriesByUserIdRequest()\
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


class DescribeRefundHistoriesByDateRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    year: int = None
    month: int = None
    day: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRefundHistoriesByDateRequest:
        self.namespace_name = namespace_name
        return self

    def with_year(self, year: int) -> DescribeRefundHistoriesByDateRequest:
        self.year = year
        return self

    def with_month(self, month: int) -> DescribeRefundHistoriesByDateRequest:
        self.month = month
        return self

    def with_day(self, day: int) -> DescribeRefundHistoriesByDateRequest:
        self.day = day
        return self

    def with_page_token(self, page_token: str) -> DescribeRefundHistoriesByDateRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRefundHistoriesByDateRequest:
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
    ) -> Optional[DescribeRefundHistoriesByDateRequest]:
        if data is None:
            return None
        return DescribeRefundHistoriesByDateRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_day(data.get('day'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetRefundHistoryRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    transaction_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRefundHistoryRequest:
        self.namespace_name = namespace_name
        return self

    def with_transaction_id(self, transaction_id: str) -> GetRefundHistoryRequest:
        self.transaction_id = transaction_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRefundHistoryRequest]:
        if data is None:
            return None
        return GetRefundHistoryRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "transactionId": self.transaction_id,
        }


class DescribeStoreContentModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStoreContentModelsRequest:
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
    ) -> Optional[DescribeStoreContentModelsRequest]:
        if data is None:
            return None
        return DescribeStoreContentModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetStoreContentModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    content_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStoreContentModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_content_name(self, content_name: str) -> GetStoreContentModelRequest:
        self.content_name = content_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStoreContentModelRequest]:
        if data is None:
            return None
        return GetStoreContentModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_content_name(data.get('contentName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "contentName": self.content_name,
        }


class DescribeStoreContentModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStoreContentModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeStoreContentModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStoreContentModelMastersRequest:
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
    ) -> Optional[DescribeStoreContentModelMastersRequest]:
        if data is None:
            return None
        return DescribeStoreContentModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateStoreContentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    apple_app_store: AppleAppStoreContent = None
    google_play: GooglePlayContent = None

    def with_namespace_name(self, namespace_name: str) -> CreateStoreContentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateStoreContentModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateStoreContentModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateStoreContentModelMasterRequest:
        self.metadata = metadata
        return self

    def with_apple_app_store(self, apple_app_store: AppleAppStoreContent) -> CreateStoreContentModelMasterRequest:
        self.apple_app_store = apple_app_store
        return self

    def with_google_play(self, google_play: GooglePlayContent) -> CreateStoreContentModelMasterRequest:
        self.google_play = google_play
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateStoreContentModelMasterRequest]:
        if data is None:
            return None
        return CreateStoreContentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_apple_app_store(AppleAppStoreContent.from_dict(data.get('appleAppStore')))\
            .with_google_play(GooglePlayContent.from_dict(data.get('googlePlay')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "appleAppStore": self.apple_app_store.to_dict() if self.apple_app_store else None,
            "googlePlay": self.google_play.to_dict() if self.google_play else None,
        }


class GetStoreContentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    content_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStoreContentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_content_name(self, content_name: str) -> GetStoreContentModelMasterRequest:
        self.content_name = content_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStoreContentModelMasterRequest]:
        if data is None:
            return None
        return GetStoreContentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_content_name(data.get('contentName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "contentName": self.content_name,
        }


class UpdateStoreContentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    content_name: str = None
    description: str = None
    metadata: str = None
    apple_app_store: AppleAppStoreContent = None
    google_play: GooglePlayContent = None

    def with_namespace_name(self, namespace_name: str) -> UpdateStoreContentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_content_name(self, content_name: str) -> UpdateStoreContentModelMasterRequest:
        self.content_name = content_name
        return self

    def with_description(self, description: str) -> UpdateStoreContentModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateStoreContentModelMasterRequest:
        self.metadata = metadata
        return self

    def with_apple_app_store(self, apple_app_store: AppleAppStoreContent) -> UpdateStoreContentModelMasterRequest:
        self.apple_app_store = apple_app_store
        return self

    def with_google_play(self, google_play: GooglePlayContent) -> UpdateStoreContentModelMasterRequest:
        self.google_play = google_play
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateStoreContentModelMasterRequest]:
        if data is None:
            return None
        return UpdateStoreContentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_content_name(data.get('contentName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_apple_app_store(AppleAppStoreContent.from_dict(data.get('appleAppStore')))\
            .with_google_play(GooglePlayContent.from_dict(data.get('googlePlay')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "contentName": self.content_name,
            "description": self.description,
            "metadata": self.metadata,
            "appleAppStore": self.apple_app_store.to_dict() if self.apple_app_store else None,
            "googlePlay": self.google_play.to_dict() if self.google_play else None,
        }


class DeleteStoreContentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    content_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteStoreContentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_content_name(self, content_name: str) -> DeleteStoreContentModelMasterRequest:
        self.content_name = content_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteStoreContentModelMasterRequest]:
        if data is None:
            return None
        return DeleteStoreContentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_content_name(data.get('contentName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "contentName": self.content_name,
        }


class DescribeStoreSubscriptionContentModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStoreSubscriptionContentModelsRequest:
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
    ) -> Optional[DescribeStoreSubscriptionContentModelsRequest]:
        if data is None:
            return None
        return DescribeStoreSubscriptionContentModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetStoreSubscriptionContentModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    content_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStoreSubscriptionContentModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_content_name(self, content_name: str) -> GetStoreSubscriptionContentModelRequest:
        self.content_name = content_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStoreSubscriptionContentModelRequest]:
        if data is None:
            return None
        return GetStoreSubscriptionContentModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_content_name(data.get('contentName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "contentName": self.content_name,
        }


class DescribeStoreSubscriptionContentModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStoreSubscriptionContentModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeStoreSubscriptionContentModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStoreSubscriptionContentModelMastersRequest:
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
    ) -> Optional[DescribeStoreSubscriptionContentModelMastersRequest]:
        if data is None:
            return None
        return DescribeStoreSubscriptionContentModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateStoreSubscriptionContentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    schedule_namespace_id: str = None
    trigger_name: str = None
    trigger_extend_mode: str = None
    rollup_hour: int = None
    reallocate_span_days: int = None
    apple_app_store: AppleAppStoreSubscriptionContent = None
    google_play: GooglePlaySubscriptionContent = None

    def with_namespace_name(self, namespace_name: str) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.metadata = metadata
        return self

    def with_schedule_namespace_id(self, schedule_namespace_id: str) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.schedule_namespace_id = schedule_namespace_id
        return self

    def with_trigger_name(self, trigger_name: str) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.trigger_name = trigger_name
        return self

    def with_trigger_extend_mode(self, trigger_extend_mode: str) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.trigger_extend_mode = trigger_extend_mode
        return self

    def with_rollup_hour(self, rollup_hour: int) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.rollup_hour = rollup_hour
        return self

    def with_reallocate_span_days(self, reallocate_span_days: int) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.reallocate_span_days = reallocate_span_days
        return self

    def with_apple_app_store(self, apple_app_store: AppleAppStoreSubscriptionContent) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.apple_app_store = apple_app_store
        return self

    def with_google_play(self, google_play: GooglePlaySubscriptionContent) -> CreateStoreSubscriptionContentModelMasterRequest:
        self.google_play = google_play
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateStoreSubscriptionContentModelMasterRequest]:
        if data is None:
            return None
        return CreateStoreSubscriptionContentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_schedule_namespace_id(data.get('scheduleNamespaceId'))\
            .with_trigger_name(data.get('triggerName'))\
            .with_trigger_extend_mode(data.get('triggerExtendMode'))\
            .with_rollup_hour(data.get('rollupHour'))\
            .with_reallocate_span_days(data.get('reallocateSpanDays'))\
            .with_apple_app_store(AppleAppStoreSubscriptionContent.from_dict(data.get('appleAppStore')))\
            .with_google_play(GooglePlaySubscriptionContent.from_dict(data.get('googlePlay')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "scheduleNamespaceId": self.schedule_namespace_id,
            "triggerName": self.trigger_name,
            "triggerExtendMode": self.trigger_extend_mode,
            "rollupHour": self.rollup_hour,
            "reallocateSpanDays": self.reallocate_span_days,
            "appleAppStore": self.apple_app_store.to_dict() if self.apple_app_store else None,
            "googlePlay": self.google_play.to_dict() if self.google_play else None,
        }


class GetStoreSubscriptionContentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    content_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStoreSubscriptionContentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_content_name(self, content_name: str) -> GetStoreSubscriptionContentModelMasterRequest:
        self.content_name = content_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStoreSubscriptionContentModelMasterRequest]:
        if data is None:
            return None
        return GetStoreSubscriptionContentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_content_name(data.get('contentName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "contentName": self.content_name,
        }


class UpdateStoreSubscriptionContentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    content_name: str = None
    description: str = None
    metadata: str = None
    schedule_namespace_id: str = None
    trigger_name: str = None
    trigger_extend_mode: str = None
    rollup_hour: int = None
    reallocate_span_days: int = None
    apple_app_store: AppleAppStoreSubscriptionContent = None
    google_play: GooglePlaySubscriptionContent = None

    def with_namespace_name(self, namespace_name: str) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_content_name(self, content_name: str) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.content_name = content_name
        return self

    def with_description(self, description: str) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.metadata = metadata
        return self

    def with_schedule_namespace_id(self, schedule_namespace_id: str) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.schedule_namespace_id = schedule_namespace_id
        return self

    def with_trigger_name(self, trigger_name: str) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.trigger_name = trigger_name
        return self

    def with_trigger_extend_mode(self, trigger_extend_mode: str) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.trigger_extend_mode = trigger_extend_mode
        return self

    def with_rollup_hour(self, rollup_hour: int) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.rollup_hour = rollup_hour
        return self

    def with_reallocate_span_days(self, reallocate_span_days: int) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.reallocate_span_days = reallocate_span_days
        return self

    def with_apple_app_store(self, apple_app_store: AppleAppStoreSubscriptionContent) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.apple_app_store = apple_app_store
        return self

    def with_google_play(self, google_play: GooglePlaySubscriptionContent) -> UpdateStoreSubscriptionContentModelMasterRequest:
        self.google_play = google_play
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateStoreSubscriptionContentModelMasterRequest]:
        if data is None:
            return None
        return UpdateStoreSubscriptionContentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_content_name(data.get('contentName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_schedule_namespace_id(data.get('scheduleNamespaceId'))\
            .with_trigger_name(data.get('triggerName'))\
            .with_trigger_extend_mode(data.get('triggerExtendMode'))\
            .with_rollup_hour(data.get('rollupHour'))\
            .with_reallocate_span_days(data.get('reallocateSpanDays'))\
            .with_apple_app_store(AppleAppStoreSubscriptionContent.from_dict(data.get('appleAppStore')))\
            .with_google_play(GooglePlaySubscriptionContent.from_dict(data.get('googlePlay')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "contentName": self.content_name,
            "description": self.description,
            "metadata": self.metadata,
            "scheduleNamespaceId": self.schedule_namespace_id,
            "triggerName": self.trigger_name,
            "triggerExtendMode": self.trigger_extend_mode,
            "rollupHour": self.rollup_hour,
            "reallocateSpanDays": self.reallocate_span_days,
            "appleAppStore": self.apple_app_store.to_dict() if self.apple_app_store else None,
            "googlePlay": self.google_play.to_dict() if self.google_play else None,
        }


class DeleteStoreSubscriptionContentModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    content_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteStoreSubscriptionContentModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_content_name(self, content_name: str) -> DeleteStoreSubscriptionContentModelMasterRequest:
        self.content_name = content_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteStoreSubscriptionContentModelMasterRequest]:
        if data is None:
            return None
        return DeleteStoreSubscriptionContentModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_content_name(data.get('contentName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "contentName": self.content_name,
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


class DescribeDailyTransactionHistoriesByCurrencyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    currency: str = None
    year: int = None
    month: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDailyTransactionHistoriesByCurrencyRequest:
        self.namespace_name = namespace_name
        return self

    def with_currency(self, currency: str) -> DescribeDailyTransactionHistoriesByCurrencyRequest:
        self.currency = currency
        return self

    def with_year(self, year: int) -> DescribeDailyTransactionHistoriesByCurrencyRequest:
        self.year = year
        return self

    def with_month(self, month: int) -> DescribeDailyTransactionHistoriesByCurrencyRequest:
        self.month = month
        return self

    def with_page_token(self, page_token: str) -> DescribeDailyTransactionHistoriesByCurrencyRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDailyTransactionHistoriesByCurrencyRequest:
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
    ) -> Optional[DescribeDailyTransactionHistoriesByCurrencyRequest]:
        if data is None:
            return None
        return DescribeDailyTransactionHistoriesByCurrencyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_currency(data.get('currency'))\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "currency": self.currency,
            "year": self.year,
            "month": self.month,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeDailyTransactionHistoriesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    year: int = None
    month: int = None
    day: int = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDailyTransactionHistoriesRequest:
        self.namespace_name = namespace_name
        return self

    def with_year(self, year: int) -> DescribeDailyTransactionHistoriesRequest:
        self.year = year
        return self

    def with_month(self, month: int) -> DescribeDailyTransactionHistoriesRequest:
        self.month = month
        return self

    def with_day(self, day: int) -> DescribeDailyTransactionHistoriesRequest:
        self.day = day
        return self

    def with_page_token(self, page_token: str) -> DescribeDailyTransactionHistoriesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDailyTransactionHistoriesRequest:
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
    ) -> Optional[DescribeDailyTransactionHistoriesRequest]:
        if data is None:
            return None
        return DescribeDailyTransactionHistoriesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_day(data.get('day'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetDailyTransactionHistoryRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    year: int = None
    month: int = None
    day: int = None
    currency: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDailyTransactionHistoryRequest:
        self.namespace_name = namespace_name
        return self

    def with_year(self, year: int) -> GetDailyTransactionHistoryRequest:
        self.year = year
        return self

    def with_month(self, month: int) -> GetDailyTransactionHistoryRequest:
        self.month = month
        return self

    def with_day(self, day: int) -> GetDailyTransactionHistoryRequest:
        self.day = day
        return self

    def with_currency(self, currency: str) -> GetDailyTransactionHistoryRequest:
        self.currency = currency
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetDailyTransactionHistoryRequest]:
        if data is None:
            return None
        return GetDailyTransactionHistoryRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_year(data.get('year'))\
            .with_month(data.get('month'))\
            .with_day(data.get('day'))\
            .with_currency(data.get('currency'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "currency": self.currency,
        }


class DescribeUnusedBalancesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeUnusedBalancesRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeUnusedBalancesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeUnusedBalancesRequest:
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
    ) -> Optional[DescribeUnusedBalancesRequest]:
        if data is None:
            return None
        return DescribeUnusedBalancesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetUnusedBalanceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    currency: str = None

    def with_namespace_name(self, namespace_name: str) -> GetUnusedBalanceRequest:
        self.namespace_name = namespace_name
        return self

    def with_currency(self, currency: str) -> GetUnusedBalanceRequest:
        self.currency = currency
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetUnusedBalanceRequest]:
        if data is None:
            return None
        return GetUnusedBalanceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_currency(data.get('currency'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "currency": self.currency,
        }