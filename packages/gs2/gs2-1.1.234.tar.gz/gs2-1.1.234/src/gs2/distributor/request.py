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
    assume_user_id: str = None
    auto_run_stamp_sheet_notification: NotificationSetting = None
    auto_run_transaction_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_assume_user_id(self, assume_user_id: str) -> CreateNamespaceRequest:
        self.assume_user_id = assume_user_id
        return self

    def with_auto_run_stamp_sheet_notification(self, auto_run_stamp_sheet_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.auto_run_stamp_sheet_notification = auto_run_stamp_sheet_notification
        return self

    def with_auto_run_transaction_notification(self, auto_run_transaction_notification: NotificationSetting) -> CreateNamespaceRequest:
        self.auto_run_transaction_notification = auto_run_transaction_notification
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
            .with_assume_user_id(data.get('assumeUserId'))\
            .with_auto_run_stamp_sheet_notification(NotificationSetting.from_dict(data.get('autoRunStampSheetNotification')))\
            .with_auto_run_transaction_notification(NotificationSetting.from_dict(data.get('autoRunTransactionNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "autoRunStampSheetNotification": self.auto_run_stamp_sheet_notification.to_dict() if self.auto_run_stamp_sheet_notification else None,
            "autoRunTransactionNotification": self.auto_run_transaction_notification.to_dict() if self.auto_run_transaction_notification else None,
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
    assume_user_id: str = None
    auto_run_stamp_sheet_notification: NotificationSetting = None
    auto_run_transaction_notification: NotificationSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_assume_user_id(self, assume_user_id: str) -> UpdateNamespaceRequest:
        self.assume_user_id = assume_user_id
        return self

    def with_auto_run_stamp_sheet_notification(self, auto_run_stamp_sheet_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.auto_run_stamp_sheet_notification = auto_run_stamp_sheet_notification
        return self

    def with_auto_run_transaction_notification(self, auto_run_transaction_notification: NotificationSetting) -> UpdateNamespaceRequest:
        self.auto_run_transaction_notification = auto_run_transaction_notification
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
            .with_assume_user_id(data.get('assumeUserId'))\
            .with_auto_run_stamp_sheet_notification(NotificationSetting.from_dict(data.get('autoRunStampSheetNotification')))\
            .with_auto_run_transaction_notification(NotificationSetting.from_dict(data.get('autoRunTransactionNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "autoRunStampSheetNotification": self.auto_run_stamp_sheet_notification.to_dict() if self.auto_run_stamp_sheet_notification else None,
            "autoRunTransactionNotification": self.auto_run_transaction_notification.to_dict() if self.auto_run_transaction_notification else None,
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


class DescribeDistributorModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDistributorModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeDistributorModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeDistributorModelMastersRequest:
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
    ) -> Optional[DescribeDistributorModelMastersRequest]:
        if data is None:
            return None
        return DescribeDistributorModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateDistributorModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    inbox_namespace_id: str = None
    white_list_target_ids: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> CreateDistributorModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateDistributorModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateDistributorModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateDistributorModelMasterRequest:
        self.metadata = metadata
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> CreateDistributorModelMasterRequest:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_white_list_target_ids(self, white_list_target_ids: List[str]) -> CreateDistributorModelMasterRequest:
        self.white_list_target_ids = white_list_target_ids
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateDistributorModelMasterRequest]:
        if data is None:
            return None
        return CreateDistributorModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_white_list_target_ids(None if data.get('whiteListTargetIds') is None else [
                data.get('whiteListTargetIds')[i]
                for i in range(len(data.get('whiteListTargetIds')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "inboxNamespaceId": self.inbox_namespace_id,
            "whiteListTargetIds": None if self.white_list_target_ids is None else [
                self.white_list_target_ids[i]
                for i in range(len(self.white_list_target_ids))
            ],
        }


class GetDistributorModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDistributorModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> GetDistributorModelMasterRequest:
        self.distributor_name = distributor_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetDistributorModelMasterRequest]:
        if data is None:
            return None
        return GetDistributorModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
        }


class UpdateDistributorModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None
    description: str = None
    metadata: str = None
    inbox_namespace_id: str = None
    white_list_target_ids: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateDistributorModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> UpdateDistributorModelMasterRequest:
        self.distributor_name = distributor_name
        return self

    def with_description(self, description: str) -> UpdateDistributorModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateDistributorModelMasterRequest:
        self.metadata = metadata
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> UpdateDistributorModelMasterRequest:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_white_list_target_ids(self, white_list_target_ids: List[str]) -> UpdateDistributorModelMasterRequest:
        self.white_list_target_ids = white_list_target_ids
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateDistributorModelMasterRequest]:
        if data is None:
            return None
        return UpdateDistributorModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_white_list_target_ids(None if data.get('whiteListTargetIds') is None else [
                data.get('whiteListTargetIds')[i]
                for i in range(len(data.get('whiteListTargetIds')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
            "description": self.description,
            "metadata": self.metadata,
            "inboxNamespaceId": self.inbox_namespace_id,
            "whiteListTargetIds": None if self.white_list_target_ids is None else [
                self.white_list_target_ids[i]
                for i in range(len(self.white_list_target_ids))
            ],
        }


class DeleteDistributorModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteDistributorModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> DeleteDistributorModelMasterRequest:
        self.distributor_name = distributor_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteDistributorModelMasterRequest]:
        if data is None:
            return None
        return DeleteDistributorModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
        }


class DescribeDistributorModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeDistributorModelsRequest:
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
    ) -> Optional[DescribeDistributorModelsRequest]:
        if data is None:
            return None
        return DescribeDistributorModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetDistributorModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetDistributorModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> GetDistributorModelRequest:
        self.distributor_name = distributor_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetDistributorModelRequest]:
        if data is None:
            return None
        return GetDistributorModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
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


class GetCurrentDistributorMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentDistributorMasterRequest:
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
    ) -> Optional[GetCurrentDistributorMasterRequest]:
        if data is None:
            return None
        return GetCurrentDistributorMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentDistributorMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentDistributorMasterRequest:
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
    ) -> Optional[PreUpdateCurrentDistributorMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentDistributorMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentDistributorMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentDistributorMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentDistributorMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentDistributorMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentDistributorMasterRequest:
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
    ) -> Optional[UpdateCurrentDistributorMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentDistributorMasterRequest()\
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


class UpdateCurrentDistributorMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentDistributorMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentDistributorMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentDistributorMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentDistributorMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DistributeRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    distributor_name: str = None
    user_id: str = None
    distribute_resource: DistributeResource = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DistributeRequest:
        self.namespace_name = namespace_name
        return self

    def with_distributor_name(self, distributor_name: str) -> DistributeRequest:
        self.distributor_name = distributor_name
        return self

    def with_user_id(self, user_id: str) -> DistributeRequest:
        self.user_id = user_id
        return self

    def with_distribute_resource(self, distribute_resource: DistributeResource) -> DistributeRequest:
        self.distribute_resource = distribute_resource
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DistributeRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DistributeRequest:
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
    ) -> Optional[DistributeRequest]:
        if data is None:
            return None
        return DistributeRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_distributor_name(data.get('distributorName'))\
            .with_user_id(data.get('userId'))\
            .with_distribute_resource(DistributeResource.from_dict(data.get('distributeResource')))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "distributorName": self.distributor_name,
            "userId": self.user_id,
            "distributeResource": self.distribute_resource.to_dict() if self.distribute_resource else None,
            "timeOffsetToken": self.time_offset_token,
        }


class DistributeWithoutOverflowProcessRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    distribute_resource: DistributeResource = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> DistributeWithoutOverflowProcessRequest:
        self.user_id = user_id
        return self

    def with_distribute_resource(self, distribute_resource: DistributeResource) -> DistributeWithoutOverflowProcessRequest:
        self.distribute_resource = distribute_resource
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DistributeWithoutOverflowProcessRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DistributeWithoutOverflowProcessRequest:
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
    ) -> Optional[DistributeWithoutOverflowProcessRequest]:
        if data is None:
            return None
        return DistributeWithoutOverflowProcessRequest()\
            .with_user_id(data.get('userId'))\
            .with_distribute_resource(DistributeResource.from_dict(data.get('distributeResource')))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "distributeResource": self.distribute_resource.to_dict() if self.distribute_resource else None,
            "timeOffsetToken": self.time_offset_token,
        }


class RunVerifyTaskRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    verify_task: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> RunVerifyTaskRequest:
        self.namespace_name = namespace_name
        return self

    def with_verify_task(self, verify_task: str) -> RunVerifyTaskRequest:
        self.verify_task = verify_task
        return self

    def with_key_id(self, key_id: str) -> RunVerifyTaskRequest:
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
    ) -> Optional[RunVerifyTaskRequest]:
        if data is None:
            return None
        return RunVerifyTaskRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_verify_task(data.get('verifyTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "verifyTask": self.verify_task,
            "keyId": self.key_id,
        }


class RunStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamp_task: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> RunStampTaskRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamp_task(self, stamp_task: str) -> RunStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> RunStampTaskRequest:
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
    ) -> Optional[RunStampTaskRequest]:
        if data is None:
            return None
        return RunStampTaskRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class RunStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> RunStampSheetRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> RunStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RunStampSheetRequest:
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
    ) -> Optional[RunStampSheetRequest]:
        if data is None:
            return None
        return RunStampSheetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class RunStampSheetExpressRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> RunStampSheetExpressRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> RunStampSheetExpressRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RunStampSheetExpressRequest:
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
    ) -> Optional[RunStampSheetExpressRequest]:
        if data is None:
            return None
        return RunStampSheetExpressRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class RunVerifyTaskWithoutNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    verify_task: str = None
    key_id: str = None

    def with_verify_task(self, verify_task: str) -> RunVerifyTaskWithoutNamespaceRequest:
        self.verify_task = verify_task
        return self

    def with_key_id(self, key_id: str) -> RunVerifyTaskWithoutNamespaceRequest:
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
    ) -> Optional[RunVerifyTaskWithoutNamespaceRequest]:
        if data is None:
            return None
        return RunVerifyTaskWithoutNamespaceRequest()\
            .with_verify_task(data.get('verifyTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verifyTask": self.verify_task,
            "keyId": self.key_id,
        }


class RunStampTaskWithoutNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> RunStampTaskWithoutNamespaceRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> RunStampTaskWithoutNamespaceRequest:
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
    ) -> Optional[RunStampTaskWithoutNamespaceRequest]:
        if data is None:
            return None
        return RunStampTaskWithoutNamespaceRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class RunStampSheetWithoutNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RunStampSheetWithoutNamespaceRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RunStampSheetWithoutNamespaceRequest:
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
    ) -> Optional[RunStampSheetWithoutNamespaceRequest]:
        if data is None:
            return None
        return RunStampSheetWithoutNamespaceRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class RunStampSheetExpressWithoutNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RunStampSheetExpressWithoutNamespaceRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RunStampSheetExpressWithoutNamespaceRequest:
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
    ) -> Optional[RunStampSheetExpressWithoutNamespaceRequest]:
        if data is None:
            return None
        return RunStampSheetExpressWithoutNamespaceRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetTransactionDefaultConfigRequest(core.Gs2Request):

    context_stack: str = None
    access_token: str = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_access_token(self, access_token: str) -> SetTransactionDefaultConfigRequest:
        self.access_token = access_token
        return self

    def with_config(self, config: List[Config]) -> SetTransactionDefaultConfigRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetTransactionDefaultConfigRequest:
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
    ) -> Optional[SetTransactionDefaultConfigRequest]:
        if data is None:
            return None
        return SetTransactionDefaultConfigRequest()\
            .with_access_token(data.get('accessToken'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accessToken": self.access_token,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class SetTransactionDefaultConfigByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_user_id(self, user_id: str) -> SetTransactionDefaultConfigByUserIdRequest:
        self.user_id = user_id
        return self

    def with_config(self, config: List[Config]) -> SetTransactionDefaultConfigByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetTransactionDefaultConfigByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetTransactionDefaultConfigByUserIdRequest:
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
    ) -> Optional[SetTransactionDefaultConfigByUserIdRequest]:
        if data is None:
            return None
        return SetTransactionDefaultConfigByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class FreezeMasterDataRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> FreezeMasterDataRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> FreezeMasterDataRequest:
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
    ) -> Optional[FreezeMasterDataRequest]:
        if data is None:
            return None
        return FreezeMasterDataRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
        }


class FreezeMasterDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> FreezeMasterDataByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> FreezeMasterDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> FreezeMasterDataByUserIdRequest:
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
    ) -> Optional[FreezeMasterDataByUserIdRequest]:
        if data is None:
            return None
        return FreezeMasterDataByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class SignFreezeMasterDataTimestampRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    timestamp: int = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> SignFreezeMasterDataTimestampRequest:
        self.namespace_name = namespace_name
        return self

    def with_timestamp(self, timestamp: int) -> SignFreezeMasterDataTimestampRequest:
        self.timestamp = timestamp
        return self

    def with_key_id(self, key_id: str) -> SignFreezeMasterDataTimestampRequest:
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
    ) -> Optional[SignFreezeMasterDataTimestampRequest]:
        if data is None:
            return None
        return SignFreezeMasterDataTimestampRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_timestamp(data.get('timestamp'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "timestamp": self.timestamp,
            "keyId": self.key_id,
        }


class FreezeMasterDataBySignedTimestampRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    body: str = None
    signature: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> FreezeMasterDataBySignedTimestampRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> FreezeMasterDataBySignedTimestampRequest:
        self.access_token = access_token
        return self

    def with_body(self, body: str) -> FreezeMasterDataBySignedTimestampRequest:
        self.body = body
        return self

    def with_signature(self, signature: str) -> FreezeMasterDataBySignedTimestampRequest:
        self.signature = signature
        return self

    def with_key_id(self, key_id: str) -> FreezeMasterDataBySignedTimestampRequest:
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
    ) -> Optional[FreezeMasterDataBySignedTimestampRequest]:
        if data is None:
            return None
        return FreezeMasterDataBySignedTimestampRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "body": self.body,
            "signature": self.signature,
            "keyId": self.key_id,
        }


class FreezeMasterDataByTimestampRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    timestamp: int = None

    def with_namespace_name(self, namespace_name: str) -> FreezeMasterDataByTimestampRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> FreezeMasterDataByTimestampRequest:
        self.access_token = access_token
        return self

    def with_timestamp(self, timestamp: int) -> FreezeMasterDataByTimestampRequest:
        self.timestamp = timestamp
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[FreezeMasterDataByTimestampRequest]:
        if data is None:
            return None
        return FreezeMasterDataByTimestampRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_timestamp(data.get('timestamp'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "timestamp": self.timestamp,
        }


class BatchExecuteApiRequest(core.Gs2Request):

    context_stack: str = None
    request_payloads: List[BatchRequestPayload] = None

    def with_request_payloads(self, request_payloads: List[BatchRequestPayload]) -> BatchExecuteApiRequest:
        self.request_payloads = request_payloads
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BatchExecuteApiRequest]:
        if data is None:
            return None
        return BatchExecuteApiRequest()\
            .with_request_payloads(None if data.get('requestPayloads') is None else [
                BatchRequestPayload.from_dict(data.get('requestPayloads')[i])
                for i in range(len(data.get('requestPayloads')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requestPayloads": None if self.request_payloads is None else [
                self.request_payloads[i].to_dict() if self.request_payloads[i] else None
                for i in range(len(self.request_payloads))
            ],
        }


class IfExpressionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    condition: VerifyAction = None
    true_actions: List[ConsumeAction] = None
    false_actions: List[ConsumeAction] = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> IfExpressionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> IfExpressionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_condition(self, condition: VerifyAction) -> IfExpressionByUserIdRequest:
        self.condition = condition
        return self

    def with_true_actions(self, true_actions: List[ConsumeAction]) -> IfExpressionByUserIdRequest:
        self.true_actions = true_actions
        return self

    def with_false_actions(self, false_actions: List[ConsumeAction]) -> IfExpressionByUserIdRequest:
        self.false_actions = false_actions
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> IfExpressionByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> IfExpressionByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> IfExpressionByUserIdRequest:
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
    ) -> Optional[IfExpressionByUserIdRequest]:
        if data is None:
            return None
        return IfExpressionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_condition(VerifyAction.from_dict(data.get('condition')))\
            .with_true_actions(None if data.get('trueActions') is None else [
                ConsumeAction.from_dict(data.get('trueActions')[i])
                for i in range(len(data.get('trueActions')))
            ])\
            .with_false_actions(None if data.get('falseActions') is None else [
                ConsumeAction.from_dict(data.get('falseActions')[i])
                for i in range(len(data.get('falseActions')))
            ])\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "condition": self.condition.to_dict() if self.condition else None,
            "trueActions": None if self.true_actions is None else [
                self.true_actions[i].to_dict() if self.true_actions[i] else None
                for i in range(len(self.true_actions))
            ],
            "falseActions": None if self.false_actions is None else [
                self.false_actions[i].to_dict() if self.false_actions[i] else None
                for i in range(len(self.false_actions))
            ],
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class AndExpressionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    actions: List[VerifyAction] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AndExpressionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AndExpressionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_actions(self, actions: List[VerifyAction]) -> AndExpressionByUserIdRequest:
        self.actions = actions
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AndExpressionByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AndExpressionByUserIdRequest:
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
    ) -> Optional[AndExpressionByUserIdRequest]:
        if data is None:
            return None
        return AndExpressionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_actions(None if data.get('actions') is None else [
                VerifyAction.from_dict(data.get('actions')[i])
                for i in range(len(data.get('actions')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "actions": None if self.actions is None else [
                self.actions[i].to_dict() if self.actions[i] else None
                for i in range(len(self.actions))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class OrExpressionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    actions: List[VerifyAction] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> OrExpressionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> OrExpressionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_actions(self, actions: List[VerifyAction]) -> OrExpressionByUserIdRequest:
        self.actions = actions
        return self

    def with_time_offset_token(self, time_offset_token: str) -> OrExpressionByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> OrExpressionByUserIdRequest:
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
    ) -> Optional[OrExpressionByUserIdRequest]:
        if data is None:
            return None
        return OrExpressionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_actions(None if data.get('actions') is None else [
                VerifyAction.from_dict(data.get('actions')[i])
                for i in range(len(data.get('actions')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "actions": None if self.actions is None else [
                self.actions[i].to_dict() if self.actions[i] else None
                for i in range(len(self.actions))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class IfExpressionByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> IfExpressionByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> IfExpressionByStampTaskRequest:
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
    ) -> Optional[IfExpressionByStampTaskRequest]:
        if data is None:
            return None
        return IfExpressionByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class AndExpressionByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> AndExpressionByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> AndExpressionByStampTaskRequest:
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
    ) -> Optional[AndExpressionByStampTaskRequest]:
        if data is None:
            return None
        return AndExpressionByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class OrExpressionByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> OrExpressionByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> OrExpressionByStampTaskRequest:
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
    ) -> Optional[OrExpressionByStampTaskRequest]:
        if data is None:
            return None
        return OrExpressionByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class GetStampSheetResultRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    transaction_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStampSheetResultRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetStampSheetResultRequest:
        self.access_token = access_token
        return self

    def with_transaction_id(self, transaction_id: str) -> GetStampSheetResultRequest:
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
    ) -> Optional[GetStampSheetResultRequest]:
        if data is None:
            return None
        return GetStampSheetResultRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "transactionId": self.transaction_id,
        }


class GetStampSheetResultByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    transaction_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStampSheetResultByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetStampSheetResultByUserIdRequest:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> GetStampSheetResultByUserIdRequest:
        self.transaction_id = transaction_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetStampSheetResultByUserIdRequest:
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
    ) -> Optional[GetStampSheetResultByUserIdRequest]:
        if data is None:
            return None
        return GetStampSheetResultByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
            "timeOffsetToken": self.time_offset_token,
        }


class RunTransactionRequest(core.Gs2Request):

    context_stack: str = None
    owner_id: str = None
    namespace_name: str = None
    user_id: str = None
    transaction: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_owner_id(self, owner_id: str) -> RunTransactionRequest:
        self.owner_id = owner_id
        return self

    def with_namespace_name(self, namespace_name: str) -> RunTransactionRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> RunTransactionRequest:
        self.user_id = user_id
        return self

    def with_transaction(self, transaction: str) -> RunTransactionRequest:
        self.transaction = transaction
        return self

    def with_time_offset_token(self, time_offset_token: str) -> RunTransactionRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RunTransactionRequest:
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
    ) -> Optional[RunTransactionRequest]:
        if data is None:
            return None
        return RunTransactionRequest()\
            .with_owner_id(data.get('ownerId'))\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_transaction(data.get('transaction'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ownerId": self.owner_id,
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "transaction": self.transaction,
            "timeOffsetToken": self.time_offset_token,
        }


class GetTransactionResultRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    transaction_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetTransactionResultRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetTransactionResultRequest:
        self.access_token = access_token
        return self

    def with_transaction_id(self, transaction_id: str) -> GetTransactionResultRequest:
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
    ) -> Optional[GetTransactionResultRequest]:
        if data is None:
            return None
        return GetTransactionResultRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "transactionId": self.transaction_id,
        }


class GetTransactionResultByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    transaction_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetTransactionResultByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetTransactionResultByUserIdRequest:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> GetTransactionResultByUserIdRequest:
        self.transaction_id = transaction_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetTransactionResultByUserIdRequest:
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
    ) -> Optional[GetTransactionResultByUserIdRequest]:
        if data is None:
            return None
        return GetTransactionResultByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
            "timeOffsetToken": self.time_offset_token,
        }