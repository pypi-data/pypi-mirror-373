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
    change_password_if_take_over: bool = None
    different_user_id_for_login_and_data_retention: bool = None
    create_account_script: ScriptSetting = None
    authentication_script: ScriptSetting = None
    create_take_over_script: ScriptSetting = None
    do_take_over_script: ScriptSetting = None
    ban_script: ScriptSetting = None
    un_ban_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_change_password_if_take_over(self, change_password_if_take_over: bool) -> CreateNamespaceRequest:
        self.change_password_if_take_over = change_password_if_take_over
        return self

    def with_different_user_id_for_login_and_data_retention(self, different_user_id_for_login_and_data_retention: bool) -> CreateNamespaceRequest:
        self.different_user_id_for_login_and_data_retention = different_user_id_for_login_and_data_retention
        return self

    def with_create_account_script(self, create_account_script: ScriptSetting) -> CreateNamespaceRequest:
        self.create_account_script = create_account_script
        return self

    def with_authentication_script(self, authentication_script: ScriptSetting) -> CreateNamespaceRequest:
        self.authentication_script = authentication_script
        return self

    def with_create_take_over_script(self, create_take_over_script: ScriptSetting) -> CreateNamespaceRequest:
        self.create_take_over_script = create_take_over_script
        return self

    def with_do_take_over_script(self, do_take_over_script: ScriptSetting) -> CreateNamespaceRequest:
        self.do_take_over_script = do_take_over_script
        return self

    def with_ban_script(self, ban_script: ScriptSetting) -> CreateNamespaceRequest:
        self.ban_script = ban_script
        return self

    def with_un_ban_script(self, un_ban_script: ScriptSetting) -> CreateNamespaceRequest:
        self.un_ban_script = un_ban_script
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
            .with_change_password_if_take_over(data.get('changePasswordIfTakeOver'))\
            .with_different_user_id_for_login_and_data_retention(data.get('differentUserIdForLoginAndDataRetention'))\
            .with_create_account_script(ScriptSetting.from_dict(data.get('createAccountScript')))\
            .with_authentication_script(ScriptSetting.from_dict(data.get('authenticationScript')))\
            .with_create_take_over_script(ScriptSetting.from_dict(data.get('createTakeOverScript')))\
            .with_do_take_over_script(ScriptSetting.from_dict(data.get('doTakeOverScript')))\
            .with_ban_script(ScriptSetting.from_dict(data.get('banScript')))\
            .with_un_ban_script(ScriptSetting.from_dict(data.get('unBanScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "changePasswordIfTakeOver": self.change_password_if_take_over,
            "differentUserIdForLoginAndDataRetention": self.different_user_id_for_login_and_data_retention,
            "createAccountScript": self.create_account_script.to_dict() if self.create_account_script else None,
            "authenticationScript": self.authentication_script.to_dict() if self.authentication_script else None,
            "createTakeOverScript": self.create_take_over_script.to_dict() if self.create_take_over_script else None,
            "doTakeOverScript": self.do_take_over_script.to_dict() if self.do_take_over_script else None,
            "banScript": self.ban_script.to_dict() if self.ban_script else None,
            "unBanScript": self.un_ban_script.to_dict() if self.un_ban_script else None,
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
    change_password_if_take_over: bool = None
    create_account_script: ScriptSetting = None
    authentication_script: ScriptSetting = None
    create_take_over_script: ScriptSetting = None
    do_take_over_script: ScriptSetting = None
    ban_script: ScriptSetting = None
    un_ban_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_change_password_if_take_over(self, change_password_if_take_over: bool) -> UpdateNamespaceRequest:
        self.change_password_if_take_over = change_password_if_take_over
        return self

    def with_create_account_script(self, create_account_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.create_account_script = create_account_script
        return self

    def with_authentication_script(self, authentication_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.authentication_script = authentication_script
        return self

    def with_create_take_over_script(self, create_take_over_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.create_take_over_script = create_take_over_script
        return self

    def with_do_take_over_script(self, do_take_over_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.do_take_over_script = do_take_over_script
        return self

    def with_ban_script(self, ban_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.ban_script = ban_script
        return self

    def with_un_ban_script(self, un_ban_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.un_ban_script = un_ban_script
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
            .with_change_password_if_take_over(data.get('changePasswordIfTakeOver'))\
            .with_create_account_script(ScriptSetting.from_dict(data.get('createAccountScript')))\
            .with_authentication_script(ScriptSetting.from_dict(data.get('authenticationScript')))\
            .with_create_take_over_script(ScriptSetting.from_dict(data.get('createTakeOverScript')))\
            .with_do_take_over_script(ScriptSetting.from_dict(data.get('doTakeOverScript')))\
            .with_ban_script(ScriptSetting.from_dict(data.get('banScript')))\
            .with_un_ban_script(ScriptSetting.from_dict(data.get('unBanScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "changePasswordIfTakeOver": self.change_password_if_take_over,
            "createAccountScript": self.create_account_script.to_dict() if self.create_account_script else None,
            "authenticationScript": self.authentication_script.to_dict() if self.authentication_script else None,
            "createTakeOverScript": self.create_take_over_script.to_dict() if self.create_take_over_script else None,
            "doTakeOverScript": self.do_take_over_script.to_dict() if self.do_take_over_script else None,
            "banScript": self.ban_script.to_dict() if self.ban_script else None,
            "unBanScript": self.un_ban_script.to_dict() if self.un_ban_script else None,
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


class DescribeAccountsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeAccountsRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeAccountsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeAccountsRequest:
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
    ) -> Optional[DescribeAccountsRequest]:
        if data is None:
            return None
        return DescribeAccountsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateAccountRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateAccountRequest:
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
    ) -> Optional[CreateAccountRequest]:
        if data is None:
            return None
        return CreateAccountRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateTimeOffsetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateTimeOffsetRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateTimeOffsetRequest:
        self.user_id = user_id
        return self

    def with_time_offset(self, time_offset: int) -> UpdateTimeOffsetRequest:
        self.time_offset = time_offset
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UpdateTimeOffsetRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateTimeOffsetRequest:
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
    ) -> Optional[UpdateTimeOffsetRequest]:
        if data is None:
            return None
        return UpdateTimeOffsetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset(data.get('timeOffset'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffset": self.time_offset,
            "timeOffsetToken": self.time_offset_token,
        }


class UpdateBannedRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    banned: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateBannedRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateBannedRequest:
        self.user_id = user_id
        return self

    def with_banned(self, banned: bool) -> UpdateBannedRequest:
        self.banned = banned
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UpdateBannedRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateBannedRequest:
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
    ) -> Optional[UpdateBannedRequest]:
        if data is None:
            return None
        return UpdateBannedRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_banned(data.get('banned'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "banned": self.banned,
            "timeOffsetToken": self.time_offset_token,
        }


class AddBanRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ban_status: BanStatus = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddBanRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AddBanRequest:
        self.user_id = user_id
        return self

    def with_ban_status(self, ban_status: BanStatus) -> AddBanRequest:
        self.ban_status = ban_status
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AddBanRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddBanRequest:
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
    ) -> Optional[AddBanRequest]:
        if data is None:
            return None
        return AddBanRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ban_status(BanStatus.from_dict(data.get('banStatus')))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "banStatus": self.ban_status.to_dict() if self.ban_status else None,
            "timeOffsetToken": self.time_offset_token,
        }


class RemoveBanRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    ban_status_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RemoveBanRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> RemoveBanRequest:
        self.user_id = user_id
        return self

    def with_ban_status_name(self, ban_status_name: str) -> RemoveBanRequest:
        self.ban_status_name = ban_status_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> RemoveBanRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RemoveBanRequest:
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
    ) -> Optional[RemoveBanRequest]:
        if data is None:
            return None
        return RemoveBanRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_ban_status_name(data.get('banStatusName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "banStatusName": self.ban_status_name,
            "timeOffsetToken": self.time_offset_token,
        }


class GetAccountRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    include_last_authenticated_at: bool = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetAccountRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetAccountRequest:
        self.user_id = user_id
        return self

    def with_include_last_authenticated_at(self, include_last_authenticated_at: bool) -> GetAccountRequest:
        self.include_last_authenticated_at = include_last_authenticated_at
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetAccountRequest:
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
    ) -> Optional[GetAccountRequest]:
        if data is None:
            return None
        return GetAccountRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_include_last_authenticated_at(data.get('includeLastAuthenticatedAt'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "includeLastAuthenticatedAt": self.include_last_authenticated_at,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteAccountRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteAccountRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteAccountRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteAccountRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteAccountRequest:
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
    ) -> Optional[DeleteAccountRequest]:
        if data is None:
            return None
        return DeleteAccountRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class AuthenticationRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    key_id: str = None
    password: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AuthenticationRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AuthenticationRequest:
        self.user_id = user_id
        return self

    def with_key_id(self, key_id: str) -> AuthenticationRequest:
        self.key_id = key_id
        return self

    def with_password(self, password: str) -> AuthenticationRequest:
        self.password = password
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AuthenticationRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AuthenticationRequest:
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
    ) -> Optional[AuthenticationRequest]:
        if data is None:
            return None
        return AuthenticationRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_key_id(data.get('keyId'))\
            .with_password(data.get('password'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "keyId": self.key_id,
            "password": self.password,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeTakeOversRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeTakeOversRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeTakeOversRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeTakeOversRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeTakeOversRequest:
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
    ) -> Optional[DescribeTakeOversRequest]:
        if data is None:
            return None
        return DescribeTakeOversRequest()\
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


class DescribeTakeOversByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeTakeOversByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeTakeOversByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeTakeOversByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeTakeOversByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeTakeOversByUserIdRequest:
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
    ) -> Optional[DescribeTakeOversByUserIdRequest]:
        if data is None:
            return None
        return DescribeTakeOversByUserIdRequest()\
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


class CreateTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    user_identifier: str = None
    password: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CreateTakeOverRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> CreateTakeOverRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> CreateTakeOverRequest:
        self.user_identifier = user_identifier
        return self

    def with_password(self, password: str) -> CreateTakeOverRequest:
        self.password = password
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateTakeOverRequest:
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
    ) -> Optional[CreateTakeOverRequest]:
        if data is None:
            return None
        return CreateTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "password": self.password,
        }


class CreateTakeOverByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    user_identifier: str = None
    password: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateTakeOverByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateTakeOverByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> CreateTakeOverByUserIdRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> CreateTakeOverByUserIdRequest:
        self.user_identifier = user_identifier
        return self

    def with_password(self, password: str) -> CreateTakeOverByUserIdRequest:
        self.password = password
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreateTakeOverByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateTakeOverByUserIdRequest:
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
    ) -> Optional[CreateTakeOverByUserIdRequest]:
        if data is None:
            return None
        return CreateTakeOverByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_password(data.get('password'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "password": self.password,
            "timeOffsetToken": self.time_offset_token,
        }


class CreateTakeOverOpenIdConnectRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    id_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateTakeOverOpenIdConnectRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CreateTakeOverOpenIdConnectRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> CreateTakeOverOpenIdConnectRequest:
        self.type = type
        return self

    def with_id_token(self, id_token: str) -> CreateTakeOverOpenIdConnectRequest:
        self.id_token = id_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateTakeOverOpenIdConnectRequest:
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
    ) -> Optional[CreateTakeOverOpenIdConnectRequest]:
        if data is None:
            return None
        return CreateTakeOverOpenIdConnectRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_id_token(data.get('idToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "idToken": self.id_token,
        }


class CreateTakeOverOpenIdConnectAndByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    id_token: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateTakeOverOpenIdConnectAndByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateTakeOverOpenIdConnectAndByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> CreateTakeOverOpenIdConnectAndByUserIdRequest:
        self.type = type
        return self

    def with_id_token(self, id_token: str) -> CreateTakeOverOpenIdConnectAndByUserIdRequest:
        self.id_token = id_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreateTakeOverOpenIdConnectAndByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateTakeOverOpenIdConnectAndByUserIdRequest:
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
    ) -> Optional[CreateTakeOverOpenIdConnectAndByUserIdRequest]:
        if data is None:
            return None
        return CreateTakeOverOpenIdConnectAndByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_id_token(data.get('idToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "idToken": self.id_token,
            "timeOffsetToken": self.time_offset_token,
        }


class GetTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None

    def with_namespace_name(self, namespace_name: str) -> GetTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetTakeOverRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> GetTakeOverRequest:
        self.type = type
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetTakeOverRequest]:
        if data is None:
            return None
        return GetTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
        }


class GetTakeOverByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetTakeOverByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetTakeOverByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> GetTakeOverByUserIdRequest:
        self.type = type
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetTakeOverByUserIdRequest:
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
    ) -> Optional[GetTakeOverByUserIdRequest]:
        if data is None:
            return None
        return GetTakeOverByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "timeOffsetToken": self.time_offset_token,
        }


class UpdateTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    old_password: str = None
    password: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> UpdateTakeOverRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> UpdateTakeOverRequest:
        self.type = type
        return self

    def with_old_password(self, old_password: str) -> UpdateTakeOverRequest:
        self.old_password = old_password
        return self

    def with_password(self, password: str) -> UpdateTakeOverRequest:
        self.password = password
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateTakeOverRequest:
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
    ) -> Optional[UpdateTakeOverRequest]:
        if data is None:
            return None
        return UpdateTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_old_password(data.get('oldPassword'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "oldPassword": self.old_password,
            "password": self.password,
        }


class UpdateTakeOverByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    old_password: str = None
    password: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateTakeOverByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateTakeOverByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> UpdateTakeOverByUserIdRequest:
        self.type = type
        return self

    def with_old_password(self, old_password: str) -> UpdateTakeOverByUserIdRequest:
        self.old_password = old_password
        return self

    def with_password(self, password: str) -> UpdateTakeOverByUserIdRequest:
        self.password = password
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UpdateTakeOverByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateTakeOverByUserIdRequest:
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
    ) -> Optional[UpdateTakeOverByUserIdRequest]:
        if data is None:
            return None
        return UpdateTakeOverByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_old_password(data.get('oldPassword'))\
            .with_password(data.get('password'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "oldPassword": self.old_password,
            "password": self.password,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteTakeOverRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> DeleteTakeOverRequest:
        self.type = type
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteTakeOverRequest:
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
    ) -> Optional[DeleteTakeOverRequest]:
        if data is None:
            return None
        return DeleteTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
        }


class DeleteTakeOverByUserIdentifierRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None
    user_identifier: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteTakeOverByUserIdentifierRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> DeleteTakeOverByUserIdentifierRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> DeleteTakeOverByUserIdentifierRequest:
        self.user_identifier = user_identifier
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteTakeOverByUserIdentifierRequest:
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
    ) -> Optional[DeleteTakeOverByUserIdentifierRequest]:
        if data is None:
            return None
        return DeleteTakeOverByUserIdentifierRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
            "userIdentifier": self.user_identifier,
        }


class DeleteTakeOverByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteTakeOverByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteTakeOverByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> DeleteTakeOverByUserIdRequest:
        self.type = type
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteTakeOverByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteTakeOverByUserIdRequest:
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
    ) -> Optional[DeleteTakeOverByUserIdRequest]:
        if data is None:
            return None
        return DeleteTakeOverByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "timeOffsetToken": self.time_offset_token,
        }


class DoTakeOverRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None
    user_identifier: str = None
    password: str = None

    def with_namespace_name(self, namespace_name: str) -> DoTakeOverRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> DoTakeOverRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> DoTakeOverRequest:
        self.user_identifier = user_identifier
        return self

    def with_password(self, password: str) -> DoTakeOverRequest:
        self.password = password
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DoTakeOverRequest]:
        if data is None:
            return None
        return DoTakeOverRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "password": self.password,
        }


class DoTakeOverOpenIdConnectRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None
    id_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DoTakeOverOpenIdConnectRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> DoTakeOverOpenIdConnectRequest:
        self.type = type
        return self

    def with_id_token(self, id_token: str) -> DoTakeOverOpenIdConnectRequest:
        self.id_token = id_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DoTakeOverOpenIdConnectRequest]:
        if data is None:
            return None
        return DoTakeOverOpenIdConnectRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))\
            .with_id_token(data.get('idToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
            "idToken": self.id_token,
        }


class GetAuthorizationUrlRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None

    def with_namespace_name(self, namespace_name: str) -> GetAuthorizationUrlRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetAuthorizationUrlRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> GetAuthorizationUrlRequest:
        self.type = type
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetAuthorizationUrlRequest]:
        if data is None:
            return None
        return GetAuthorizationUrlRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
        }


class DescribePlatformIdsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribePlatformIdsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribePlatformIdsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribePlatformIdsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribePlatformIdsRequest:
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
    ) -> Optional[DescribePlatformIdsRequest]:
        if data is None:
            return None
        return DescribePlatformIdsRequest()\
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


class DescribePlatformIdsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribePlatformIdsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribePlatformIdsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribePlatformIdsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribePlatformIdsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribePlatformIdsByUserIdRequest:
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
    ) -> Optional[DescribePlatformIdsByUserIdRequest]:
        if data is None:
            return None
        return DescribePlatformIdsByUserIdRequest()\
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


class CreatePlatformIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    user_identifier: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreatePlatformIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> CreatePlatformIdRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> CreatePlatformIdRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> CreatePlatformIdRequest:
        self.user_identifier = user_identifier
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreatePlatformIdRequest:
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
    ) -> Optional[CreatePlatformIdRequest]:
        if data is None:
            return None
        return CreatePlatformIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "userIdentifier": self.user_identifier,
        }


class CreatePlatformIdByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    user_identifier: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreatePlatformIdByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreatePlatformIdByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> CreatePlatformIdByUserIdRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> CreatePlatformIdByUserIdRequest:
        self.user_identifier = user_identifier
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreatePlatformIdByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreatePlatformIdByUserIdRequest:
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
    ) -> Optional[CreatePlatformIdByUserIdRequest]:
        if data is None:
            return None
        return CreatePlatformIdByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "timeOffsetToken": self.time_offset_token,
        }


class GetPlatformIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None

    def with_namespace_name(self, namespace_name: str) -> GetPlatformIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetPlatformIdRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> GetPlatformIdRequest:
        self.type = type
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPlatformIdRequest]:
        if data is None:
            return None
        return GetPlatformIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
        }


class GetPlatformIdByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPlatformIdByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetPlatformIdByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> GetPlatformIdByUserIdRequest:
        self.type = type
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetPlatformIdByUserIdRequest:
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
    ) -> Optional[GetPlatformIdByUserIdRequest]:
        if data is None:
            return None
        return GetPlatformIdByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "timeOffsetToken": self.time_offset_token,
        }


class FindPlatformIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    user_identifier: str = None

    def with_namespace_name(self, namespace_name: str) -> FindPlatformIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> FindPlatformIdRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> FindPlatformIdRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> FindPlatformIdRequest:
        self.user_identifier = user_identifier
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[FindPlatformIdRequest]:
        if data is None:
            return None
        return FindPlatformIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "userIdentifier": self.user_identifier,
        }


class FindPlatformIdByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    user_identifier: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> FindPlatformIdByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> FindPlatformIdByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> FindPlatformIdByUserIdRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> FindPlatformIdByUserIdRequest:
        self.user_identifier = user_identifier
        return self

    def with_time_offset_token(self, time_offset_token: str) -> FindPlatformIdByUserIdRequest:
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
    ) -> Optional[FindPlatformIdByUserIdRequest]:
        if data is None:
            return None
        return FindPlatformIdByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "userIdentifier": self.user_identifier,
            "timeOffsetToken": self.time_offset_token,
        }


class DeletePlatformIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    type: int = None
    user_identifier: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeletePlatformIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeletePlatformIdRequest:
        self.access_token = access_token
        return self

    def with_type(self, type: int) -> DeletePlatformIdRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> DeletePlatformIdRequest:
        self.user_identifier = user_identifier
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeletePlatformIdRequest:
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
    ) -> Optional[DeletePlatformIdRequest]:
        if data is None:
            return None
        return DeletePlatformIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "type": self.type,
            "userIdentifier": self.user_identifier,
        }


class DeletePlatformIdByUserIdentifierRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None
    user_identifier: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeletePlatformIdByUserIdentifierRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> DeletePlatformIdByUserIdentifierRequest:
        self.type = type
        return self

    def with_user_identifier(self, user_identifier: str) -> DeletePlatformIdByUserIdentifierRequest:
        self.user_identifier = user_identifier
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeletePlatformIdByUserIdentifierRequest:
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
    ) -> Optional[DeletePlatformIdByUserIdentifierRequest]:
        if data is None:
            return None
        return DeletePlatformIdByUserIdentifierRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))\
            .with_user_identifier(data.get('userIdentifier'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
            "userIdentifier": self.user_identifier,
        }


class DeletePlatformIdByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    type: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeletePlatformIdByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeletePlatformIdByUserIdRequest:
        self.user_id = user_id
        return self

    def with_type(self, type: int) -> DeletePlatformIdByUserIdRequest:
        self.type = type
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeletePlatformIdByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeletePlatformIdByUserIdRequest:
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
    ) -> Optional[DeletePlatformIdByUserIdRequest]:
        if data is None:
            return None
        return DeletePlatformIdByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "type": self.type,
            "timeOffsetToken": self.time_offset_token,
        }


class GetDataOwnerByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDataOwnerByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetDataOwnerByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetDataOwnerByUserIdRequest:
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
    ) -> Optional[GetDataOwnerByUserIdRequest]:
        if data is None:
            return None
        return GetDataOwnerByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class UpdateDataOwnerByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    data_owner_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateDataOwnerByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> UpdateDataOwnerByUserIdRequest:
        self.user_id = user_id
        return self

    def with_data_owner_name(self, data_owner_name: str) -> UpdateDataOwnerByUserIdRequest:
        self.data_owner_name = data_owner_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UpdateDataOwnerByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateDataOwnerByUserIdRequest:
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
    ) -> Optional[UpdateDataOwnerByUserIdRequest]:
        if data is None:
            return None
        return UpdateDataOwnerByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_data_owner_name(data.get('dataOwnerName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "dataOwnerName": self.data_owner_name,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteDataOwnerByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteDataOwnerByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteDataOwnerByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteDataOwnerByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteDataOwnerByUserIdRequest:
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
    ) -> Optional[DeleteDataOwnerByUserIdRequest]:
        if data is None:
            return None
        return DeleteDataOwnerByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeTakeOverTypeModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeTakeOverTypeModelsRequest:
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
    ) -> Optional[DescribeTakeOverTypeModelsRequest]:
        if data is None:
            return None
        return DescribeTakeOverTypeModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetTakeOverTypeModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None

    def with_namespace_name(self, namespace_name: str) -> GetTakeOverTypeModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> GetTakeOverTypeModelRequest:
        self.type = type
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetTakeOverTypeModelRequest]:
        if data is None:
            return None
        return GetTakeOverTypeModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
        }


class DescribeTakeOverTypeModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeTakeOverTypeModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeTakeOverTypeModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeTakeOverTypeModelMastersRequest:
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
    ) -> Optional[DescribeTakeOverTypeModelMastersRequest]:
        if data is None:
            return None
        return DescribeTakeOverTypeModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateTakeOverTypeModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None
    description: str = None
    metadata: str = None
    open_id_connect_setting: OpenIdConnectSetting = None

    def with_namespace_name(self, namespace_name: str) -> CreateTakeOverTypeModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> CreateTakeOverTypeModelMasterRequest:
        self.type = type
        return self

    def with_description(self, description: str) -> CreateTakeOverTypeModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateTakeOverTypeModelMasterRequest:
        self.metadata = metadata
        return self

    def with_open_id_connect_setting(self, open_id_connect_setting: OpenIdConnectSetting) -> CreateTakeOverTypeModelMasterRequest:
        self.open_id_connect_setting = open_id_connect_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateTakeOverTypeModelMasterRequest]:
        if data is None:
            return None
        return CreateTakeOverTypeModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_open_id_connect_setting(OpenIdConnectSetting.from_dict(data.get('openIdConnectSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
            "description": self.description,
            "metadata": self.metadata,
            "openIdConnectSetting": self.open_id_connect_setting.to_dict() if self.open_id_connect_setting else None,
        }


class GetTakeOverTypeModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None

    def with_namespace_name(self, namespace_name: str) -> GetTakeOverTypeModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> GetTakeOverTypeModelMasterRequest:
        self.type = type
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetTakeOverTypeModelMasterRequest]:
        if data is None:
            return None
        return GetTakeOverTypeModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
        }


class UpdateTakeOverTypeModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None
    description: str = None
    metadata: str = None
    open_id_connect_setting: OpenIdConnectSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateTakeOverTypeModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> UpdateTakeOverTypeModelMasterRequest:
        self.type = type
        return self

    def with_description(self, description: str) -> UpdateTakeOverTypeModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateTakeOverTypeModelMasterRequest:
        self.metadata = metadata
        return self

    def with_open_id_connect_setting(self, open_id_connect_setting: OpenIdConnectSetting) -> UpdateTakeOverTypeModelMasterRequest:
        self.open_id_connect_setting = open_id_connect_setting
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateTakeOverTypeModelMasterRequest]:
        if data is None:
            return None
        return UpdateTakeOverTypeModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_open_id_connect_setting(OpenIdConnectSetting.from_dict(data.get('openIdConnectSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
            "description": self.description,
            "metadata": self.metadata,
            "openIdConnectSetting": self.open_id_connect_setting.to_dict() if self.open_id_connect_setting else None,
        }


class DeleteTakeOverTypeModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    type: int = None

    def with_namespace_name(self, namespace_name: str) -> DeleteTakeOverTypeModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_type(self, type: int) -> DeleteTakeOverTypeModelMasterRequest:
        self.type = type
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteTakeOverTypeModelMasterRequest]:
        if data is None:
            return None
        return DeleteTakeOverTypeModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_type(data.get('type'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "type": self.type,
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