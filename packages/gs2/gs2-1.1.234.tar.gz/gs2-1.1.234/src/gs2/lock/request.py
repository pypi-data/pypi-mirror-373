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
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
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
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
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


class LockRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    property_id: str = None
    access_token: str = None
    transaction_id: str = None
    ttl: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> LockRequest:
        self.namespace_name = namespace_name
        return self

    def with_property_id(self, property_id: str) -> LockRequest:
        self.property_id = property_id
        return self

    def with_access_token(self, access_token: str) -> LockRequest:
        self.access_token = access_token
        return self

    def with_transaction_id(self, transaction_id: str) -> LockRequest:
        self.transaction_id = transaction_id
        return self

    def with_ttl(self, ttl: int) -> LockRequest:
        self.ttl = ttl
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> LockRequest:
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
    ) -> Optional[LockRequest]:
        if data is None:
            return None
        return LockRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_access_token(data.get('accessToken'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_ttl(data.get('ttl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "propertyId": self.property_id,
            "accessToken": self.access_token,
            "transactionId": self.transaction_id,
            "ttl": self.ttl,
        }


class LockByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    property_id: str = None
    user_id: str = None
    transaction_id: str = None
    ttl: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> LockByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_property_id(self, property_id: str) -> LockByUserIdRequest:
        self.property_id = property_id
        return self

    def with_user_id(self, user_id: str) -> LockByUserIdRequest:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> LockByUserIdRequest:
        self.transaction_id = transaction_id
        return self

    def with_ttl(self, ttl: int) -> LockByUserIdRequest:
        self.ttl = ttl
        return self

    def with_time_offset_token(self, time_offset_token: str) -> LockByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> LockByUserIdRequest:
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
    ) -> Optional[LockByUserIdRequest]:
        if data is None:
            return None
        return LockByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_ttl(data.get('ttl'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "propertyId": self.property_id,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
            "ttl": self.ttl,
            "timeOffsetToken": self.time_offset_token,
        }


class UnlockRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    property_id: str = None
    access_token: str = None
    transaction_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnlockRequest:
        self.namespace_name = namespace_name
        return self

    def with_property_id(self, property_id: str) -> UnlockRequest:
        self.property_id = property_id
        return self

    def with_access_token(self, access_token: str) -> UnlockRequest:
        self.access_token = access_token
        return self

    def with_transaction_id(self, transaction_id: str) -> UnlockRequest:
        self.transaction_id = transaction_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnlockRequest:
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
    ) -> Optional[UnlockRequest]:
        if data is None:
            return None
        return UnlockRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_access_token(data.get('accessToken'))\
            .with_transaction_id(data.get('transactionId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "propertyId": self.property_id,
            "accessToken": self.access_token,
            "transactionId": self.transaction_id,
        }


class UnlockByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    property_id: str = None
    user_id: str = None
    transaction_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnlockByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_property_id(self, property_id: str) -> UnlockByUserIdRequest:
        self.property_id = property_id
        return self

    def with_user_id(self, user_id: str) -> UnlockByUserIdRequest:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> UnlockByUserIdRequest:
        self.transaction_id = transaction_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UnlockByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnlockByUserIdRequest:
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
    ) -> Optional[UnlockByUserIdRequest]:
        if data is None:
            return None
        return UnlockByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_property_id(data.get('propertyId'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "propertyId": self.property_id,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetMutexRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    property_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMutexRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetMutexRequest:
        self.access_token = access_token
        return self

    def with_property_id(self, property_id: str) -> GetMutexRequest:
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
    ) -> Optional[GetMutexRequest]:
        if data is None:
            return None
        return GetMutexRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_property_id(data.get('propertyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "propertyId": self.property_id,
        }


class GetMutexByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    property_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMutexByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetMutexByUserIdRequest:
        self.user_id = user_id
        return self

    def with_property_id(self, property_id: str) -> GetMutexByUserIdRequest:
        self.property_id = property_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetMutexByUserIdRequest:
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
    ) -> Optional[GetMutexByUserIdRequest]:
        if data is None:
            return None
        return GetMutexByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_id(data.get('propertyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "propertyId": self.property_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteMutexByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    property_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMutexByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteMutexByUserIdRequest:
        self.user_id = user_id
        return self

    def with_property_id(self, property_id: str) -> DeleteMutexByUserIdRequest:
        self.property_id = property_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteMutexByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteMutexByUserIdRequest:
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
    ) -> Optional[DeleteMutexByUserIdRequest]:
        if data is None:
            return None
        return DeleteMutexByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_id(data.get('propertyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "propertyId": self.property_id,
            "timeOffsetToken": self.time_offset_token,
        }