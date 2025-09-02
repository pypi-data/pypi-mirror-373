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


class DescribeKeysRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeKeysRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeKeysRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeKeysRequest:
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
    ) -> Optional[DescribeKeysRequest]:
        if data is None:
            return None
        return DescribeKeysRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateKeyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateKeyRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateKeyRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateKeyRequest:
        self.description = description
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateKeyRequest]:
        if data is None:
            return None
        return CreateKeyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
        }


class UpdateKeyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    key_name: str = None
    description: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateKeyRequest:
        self.namespace_name = namespace_name
        return self

    def with_key_name(self, key_name: str) -> UpdateKeyRequest:
        self.key_name = key_name
        return self

    def with_description(self, description: str) -> UpdateKeyRequest:
        self.description = description
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateKeyRequest]:
        if data is None:
            return None
        return UpdateKeyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_key_name(data.get('keyName'))\
            .with_description(data.get('description'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "keyName": self.key_name,
            "description": self.description,
        }


class GetKeyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    key_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetKeyRequest:
        self.namespace_name = namespace_name
        return self

    def with_key_name(self, key_name: str) -> GetKeyRequest:
        self.key_name = key_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetKeyRequest]:
        if data is None:
            return None
        return GetKeyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_key_name(data.get('keyName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "keyName": self.key_name,
        }


class DeleteKeyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    key_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteKeyRequest:
        self.namespace_name = namespace_name
        return self

    def with_key_name(self, key_name: str) -> DeleteKeyRequest:
        self.key_name = key_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteKeyRequest]:
        if data is None:
            return None
        return DeleteKeyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_key_name(data.get('keyName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "keyName": self.key_name,
        }


class EncryptRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    key_name: str = None
    data: str = None

    def with_namespace_name(self, namespace_name: str) -> EncryptRequest:
        self.namespace_name = namespace_name
        return self

    def with_key_name(self, key_name: str) -> EncryptRequest:
        self.key_name = key_name
        return self

    def with_data(self, data: str) -> EncryptRequest:
        self.data = data
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[EncryptRequest]:
        if data is None:
            return None
        return EncryptRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_key_name(data.get('keyName'))\
            .with_data(data.get('data'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "keyName": self.key_name,
            "data": self.data,
        }


class DecryptRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    key_name: str = None
    data: str = None

    def with_namespace_name(self, namespace_name: str) -> DecryptRequest:
        self.namespace_name = namespace_name
        return self

    def with_key_name(self, key_name: str) -> DecryptRequest:
        self.key_name = key_name
        return self

    def with_data(self, data: str) -> DecryptRequest:
        self.data = data
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecryptRequest]:
        if data is None:
            return None
        return DecryptRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_key_name(data.get('keyName'))\
            .with_data(data.get('data'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "keyName": self.key_name,
            "data": self.data,
        }


class DescribeGitHubApiKeysRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeGitHubApiKeysRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeGitHubApiKeysRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeGitHubApiKeysRequest:
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
    ) -> Optional[DescribeGitHubApiKeysRequest]:
        if data is None:
            return None
        return DescribeGitHubApiKeysRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateGitHubApiKeyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    api_key: str = None
    encryption_key_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateGitHubApiKeyRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateGitHubApiKeyRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateGitHubApiKeyRequest:
        self.description = description
        return self

    def with_api_key(self, api_key: str) -> CreateGitHubApiKeyRequest:
        self.api_key = api_key
        return self

    def with_encryption_key_name(self, encryption_key_name: str) -> CreateGitHubApiKeyRequest:
        self.encryption_key_name = encryption_key_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGitHubApiKeyRequest]:
        if data is None:
            return None
        return CreateGitHubApiKeyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_api_key(data.get('apiKey'))\
            .with_encryption_key_name(data.get('encryptionKeyName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "apiKey": self.api_key,
            "encryptionKeyName": self.encryption_key_name,
        }


class UpdateGitHubApiKeyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    api_key_name: str = None
    description: str = None
    api_key: str = None
    encryption_key_name: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateGitHubApiKeyRequest:
        self.namespace_name = namespace_name
        return self

    def with_api_key_name(self, api_key_name: str) -> UpdateGitHubApiKeyRequest:
        self.api_key_name = api_key_name
        return self

    def with_description(self, description: str) -> UpdateGitHubApiKeyRequest:
        self.description = description
        return self

    def with_api_key(self, api_key: str) -> UpdateGitHubApiKeyRequest:
        self.api_key = api_key
        return self

    def with_encryption_key_name(self, encryption_key_name: str) -> UpdateGitHubApiKeyRequest:
        self.encryption_key_name = encryption_key_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGitHubApiKeyRequest]:
        if data is None:
            return None
        return UpdateGitHubApiKeyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_api_key_name(data.get('apiKeyName'))\
            .with_description(data.get('description'))\
            .with_api_key(data.get('apiKey'))\
            .with_encryption_key_name(data.get('encryptionKeyName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "apiKeyName": self.api_key_name,
            "description": self.description,
            "apiKey": self.api_key,
            "encryptionKeyName": self.encryption_key_name,
        }


class GetGitHubApiKeyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    api_key_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetGitHubApiKeyRequest:
        self.namespace_name = namespace_name
        return self

    def with_api_key_name(self, api_key_name: str) -> GetGitHubApiKeyRequest:
        self.api_key_name = api_key_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGitHubApiKeyRequest]:
        if data is None:
            return None
        return GetGitHubApiKeyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_api_key_name(data.get('apiKeyName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "apiKeyName": self.api_key_name,
        }


class DeleteGitHubApiKeyRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    api_key_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteGitHubApiKeyRequest:
        self.namespace_name = namespace_name
        return self

    def with_api_key_name(self, api_key_name: str) -> DeleteGitHubApiKeyRequest:
        self.api_key_name = api_key_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGitHubApiKeyRequest]:
        if data is None:
            return None
        return DeleteGitHubApiKeyRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_api_key_name(data.get('apiKeyName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "apiKeyName": self.api_key_name,
        }