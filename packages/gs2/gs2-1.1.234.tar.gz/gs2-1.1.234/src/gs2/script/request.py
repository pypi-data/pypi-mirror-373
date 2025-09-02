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


class DescribeScriptsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeScriptsRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeScriptsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeScriptsRequest:
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
    ) -> Optional[DescribeScriptsRequest]:
        if data is None:
            return None
        return DescribeScriptsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateScriptRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    script: str = None
    disable_string_number_to_number: bool = None

    def with_namespace_name(self, namespace_name: str) -> CreateScriptRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateScriptRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateScriptRequest:
        self.description = description
        return self

    def with_script(self, script: str) -> CreateScriptRequest:
        self.script = script
        return self

    def with_disable_string_number_to_number(self, disable_string_number_to_number: bool) -> CreateScriptRequest:
        self.disable_string_number_to_number = disable_string_number_to_number
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateScriptRequest]:
        if data is None:
            return None
        return CreateScriptRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_script(data.get('script'))\
            .with_disable_string_number_to_number(data.get('disableStringNumberToNumber'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "script": self.script,
            "disableStringNumberToNumber": self.disable_string_number_to_number,
        }


class CreateScriptFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    checkout_setting: GitHubCheckoutSetting = None
    disable_string_number_to_number: bool = None

    def with_namespace_name(self, namespace_name: str) -> CreateScriptFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateScriptFromGitHubRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateScriptFromGitHubRequest:
        self.description = description
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> CreateScriptFromGitHubRequest:
        self.checkout_setting = checkout_setting
        return self

    def with_disable_string_number_to_number(self, disable_string_number_to_number: bool) -> CreateScriptFromGitHubRequest:
        self.disable_string_number_to_number = disable_string_number_to_number
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateScriptFromGitHubRequest]:
        if data is None:
            return None
        return CreateScriptFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))\
            .with_disable_string_number_to_number(data.get('disableStringNumberToNumber'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
            "disableStringNumberToNumber": self.disable_string_number_to_number,
        }


class GetScriptRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    script_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetScriptRequest:
        self.namespace_name = namespace_name
        return self

    def with_script_name(self, script_name: str) -> GetScriptRequest:
        self.script_name = script_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetScriptRequest]:
        if data is None:
            return None
        return GetScriptRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_script_name(data.get('scriptName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "scriptName": self.script_name,
        }


class UpdateScriptRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    script_name: str = None
    description: str = None
    script: str = None
    disable_string_number_to_number: bool = None

    def with_namespace_name(self, namespace_name: str) -> UpdateScriptRequest:
        self.namespace_name = namespace_name
        return self

    def with_script_name(self, script_name: str) -> UpdateScriptRequest:
        self.script_name = script_name
        return self

    def with_description(self, description: str) -> UpdateScriptRequest:
        self.description = description
        return self

    def with_script(self, script: str) -> UpdateScriptRequest:
        self.script = script
        return self

    def with_disable_string_number_to_number(self, disable_string_number_to_number: bool) -> UpdateScriptRequest:
        self.disable_string_number_to_number = disable_string_number_to_number
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateScriptRequest]:
        if data is None:
            return None
        return UpdateScriptRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_script_name(data.get('scriptName'))\
            .with_description(data.get('description'))\
            .with_script(data.get('script'))\
            .with_disable_string_number_to_number(data.get('disableStringNumberToNumber'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "scriptName": self.script_name,
            "description": self.description,
            "script": self.script,
            "disableStringNumberToNumber": self.disable_string_number_to_number,
        }


class UpdateScriptFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    script_name: str = None
    description: str = None
    checkout_setting: GitHubCheckoutSetting = None
    disable_string_number_to_number: bool = None

    def with_namespace_name(self, namespace_name: str) -> UpdateScriptFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_script_name(self, script_name: str) -> UpdateScriptFromGitHubRequest:
        self.script_name = script_name
        return self

    def with_description(self, description: str) -> UpdateScriptFromGitHubRequest:
        self.description = description
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateScriptFromGitHubRequest:
        self.checkout_setting = checkout_setting
        return self

    def with_disable_string_number_to_number(self, disable_string_number_to_number: bool) -> UpdateScriptFromGitHubRequest:
        self.disable_string_number_to_number = disable_string_number_to_number
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateScriptFromGitHubRequest]:
        if data is None:
            return None
        return UpdateScriptFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_script_name(data.get('scriptName'))\
            .with_description(data.get('description'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))\
            .with_disable_string_number_to_number(data.get('disableStringNumberToNumber'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "scriptName": self.script_name,
            "description": self.description,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
            "disableStringNumberToNumber": self.disable_string_number_to_number,
        }


class DeleteScriptRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    script_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteScriptRequest:
        self.namespace_name = namespace_name
        return self

    def with_script_name(self, script_name: str) -> DeleteScriptRequest:
        self.script_name = script_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteScriptRequest]:
        if data is None:
            return None
        return DeleteScriptRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_script_name(data.get('scriptName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "scriptName": self.script_name,
        }


class InvokeScriptRequest(core.Gs2Request):

    context_stack: str = None
    script_id: str = None
    user_id: str = None
    args: str = None
    random_status: RandomStatus = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_script_id(self, script_id: str) -> InvokeScriptRequest:
        self.script_id = script_id
        return self

    def with_user_id(self, user_id: str) -> InvokeScriptRequest:
        self.user_id = user_id
        return self

    def with_args(self, args: str) -> InvokeScriptRequest:
        self.args = args
        return self

    def with_random_status(self, random_status: RandomStatus) -> InvokeScriptRequest:
        self.random_status = random_status
        return self

    def with_time_offset_token(self, time_offset_token: str) -> InvokeScriptRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> InvokeScriptRequest:
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
    ) -> Optional[InvokeScriptRequest]:
        if data is None:
            return None
        return InvokeScriptRequest()\
            .with_script_id(data.get('scriptId'))\
            .with_user_id(data.get('userId'))\
            .with_args(data.get('args'))\
            .with_random_status(RandomStatus.from_dict(data.get('randomStatus')))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scriptId": self.script_id,
            "userId": self.user_id,
            "args": self.args,
            "randomStatus": self.random_status.to_dict() if self.random_status else None,
            "timeOffsetToken": self.time_offset_token,
        }


class DebugInvokeRequest(core.Gs2Request):

    context_stack: str = None
    script: str = None
    args: str = None
    user_id: str = None
    random_status: RandomStatus = None
    disable_string_number_to_number: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_script(self, script: str) -> DebugInvokeRequest:
        self.script = script
        return self

    def with_args(self, args: str) -> DebugInvokeRequest:
        self.args = args
        return self

    def with_user_id(self, user_id: str) -> DebugInvokeRequest:
        self.user_id = user_id
        return self

    def with_random_status(self, random_status: RandomStatus) -> DebugInvokeRequest:
        self.random_status = random_status
        return self

    def with_disable_string_number_to_number(self, disable_string_number_to_number: bool) -> DebugInvokeRequest:
        self.disable_string_number_to_number = disable_string_number_to_number
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DebugInvokeRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DebugInvokeRequest:
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
    ) -> Optional[DebugInvokeRequest]:
        if data is None:
            return None
        return DebugInvokeRequest()\
            .with_script(data.get('script'))\
            .with_args(data.get('args'))\
            .with_user_id(data.get('userId'))\
            .with_random_status(RandomStatus.from_dict(data.get('randomStatus')))\
            .with_disable_string_number_to_number(data.get('disableStringNumberToNumber'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "script": self.script,
            "args": self.args,
            "userId": self.user_id,
            "randomStatus": self.random_status.to_dict() if self.random_status else None,
            "disableStringNumberToNumber": self.disable_string_number_to_number,
            "timeOffsetToken": self.time_offset_token,
        }


class InvokeByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> InvokeByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> InvokeByStampSheetRequest:
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
    ) -> Optional[InvokeByStampSheetRequest]:
        if data is None:
            return None
        return InvokeByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }