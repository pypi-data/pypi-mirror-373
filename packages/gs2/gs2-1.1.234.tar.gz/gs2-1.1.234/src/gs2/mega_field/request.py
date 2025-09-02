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


class DescribeAreaModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeAreaModelsRequest:
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
    ) -> Optional[DescribeAreaModelsRequest]:
        if data is None:
            return None
        return DescribeAreaModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetAreaModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetAreaModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> GetAreaModelRequest:
        self.area_model_name = area_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetAreaModelRequest]:
        if data is None:
            return None
        return GetAreaModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
        }


class DescribeAreaModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeAreaModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeAreaModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeAreaModelMastersRequest:
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
    ) -> Optional[DescribeAreaModelMastersRequest]:
        if data is None:
            return None
        return DescribeAreaModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateAreaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateAreaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateAreaModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateAreaModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateAreaModelMasterRequest:
        self.metadata = metadata
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateAreaModelMasterRequest]:
        if data is None:
            return None
        return CreateAreaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


class GetAreaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetAreaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> GetAreaModelMasterRequest:
        self.area_model_name = area_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetAreaModelMasterRequest]:
        if data is None:
            return None
        return GetAreaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
        }


class UpdateAreaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateAreaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> UpdateAreaModelMasterRequest:
        self.area_model_name = area_model_name
        return self

    def with_description(self, description: str) -> UpdateAreaModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateAreaModelMasterRequest:
        self.metadata = metadata
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateAreaModelMasterRequest]:
        if data is None:
            return None
        return UpdateAreaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "description": self.description,
            "metadata": self.metadata,
        }


class DeleteAreaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteAreaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> DeleteAreaModelMasterRequest:
        self.area_model_name = area_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteAreaModelMasterRequest]:
        if data is None:
            return None
        return DeleteAreaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
        }


class DescribeLayerModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeLayerModelsRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> DescribeLayerModelsRequest:
        self.area_model_name = area_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeLayerModelsRequest]:
        if data is None:
            return None
        return DescribeLayerModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
        }


class GetLayerModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    layer_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetLayerModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> GetLayerModelRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> GetLayerModelRequest:
        self.layer_model_name = layer_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetLayerModelRequest]:
        if data is None:
            return None
        return GetLayerModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
        }


class DescribeLayerModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeLayerModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> DescribeLayerModelMastersRequest:
        self.area_model_name = area_model_name
        return self

    def with_page_token(self, page_token: str) -> DescribeLayerModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeLayerModelMastersRequest:
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
    ) -> Optional[DescribeLayerModelMastersRequest]:
        if data is None:
            return None
        return DescribeLayerModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateLayerModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateLayerModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> CreateLayerModelMasterRequest:
        self.area_model_name = area_model_name
        return self

    def with_name(self, name: str) -> CreateLayerModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateLayerModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateLayerModelMasterRequest:
        self.metadata = metadata
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateLayerModelMasterRequest]:
        if data is None:
            return None
        return CreateLayerModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


class GetLayerModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    layer_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetLayerModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> GetLayerModelMasterRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> GetLayerModelMasterRequest:
        self.layer_model_name = layer_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetLayerModelMasterRequest]:
        if data is None:
            return None
        return GetLayerModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
        }


class UpdateLayerModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    layer_model_name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateLayerModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> UpdateLayerModelMasterRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> UpdateLayerModelMasterRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_description(self, description: str) -> UpdateLayerModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateLayerModelMasterRequest:
        self.metadata = metadata
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateLayerModelMasterRequest]:
        if data is None:
            return None
        return UpdateLayerModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "description": self.description,
            "metadata": self.metadata,
        }


class DeleteLayerModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    layer_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteLayerModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> DeleteLayerModelMasterRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> DeleteLayerModelMasterRequest:
        self.layer_model_name = layer_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteLayerModelMasterRequest]:
        if data is None:
            return None
        return DeleteLayerModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
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


class GetCurrentFieldMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentFieldMasterRequest:
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
    ) -> Optional[GetCurrentFieldMasterRequest]:
        if data is None:
            return None
        return GetCurrentFieldMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentFieldMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentFieldMasterRequest:
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
    ) -> Optional[PreUpdateCurrentFieldMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentFieldMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentFieldMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentFieldMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentFieldMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentFieldMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentFieldMasterRequest:
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
    ) -> Optional[UpdateCurrentFieldMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentFieldMasterRequest()\
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


class UpdateCurrentFieldMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentFieldMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentFieldMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentFieldMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentFieldMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class PutPositionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    area_model_name: str = None
    layer_model_name: str = None
    position: Position = None
    vector: Vector = None
    r: float = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutPositionRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> PutPositionRequest:
        self.access_token = access_token
        return self

    def with_area_model_name(self, area_model_name: str) -> PutPositionRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> PutPositionRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_position(self, position: Position) -> PutPositionRequest:
        self.position = position
        return self

    def with_vector(self, vector: Vector) -> PutPositionRequest:
        self.vector = vector
        return self

    def with_r(self, r: float) -> PutPositionRequest:
        self.r = r
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutPositionRequest:
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
    ) -> Optional[PutPositionRequest]:
        if data is None:
            return None
        return PutPositionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_position(Position.from_dict(data.get('position')))\
            .with_vector(Vector.from_dict(data.get('vector')))\
            .with_r(data.get('r'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "position": self.position.to_dict() if self.position else None,
            "vector": self.vector.to_dict() if self.vector else None,
            "r": self.r,
        }


class PutPositionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    area_model_name: str = None
    layer_model_name: str = None
    position: Position = None
    vector: Vector = None
    r: float = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> PutPositionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> PutPositionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_area_model_name(self, area_model_name: str) -> PutPositionByUserIdRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> PutPositionByUserIdRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_position(self, position: Position) -> PutPositionByUserIdRequest:
        self.position = position
        return self

    def with_vector(self, vector: Vector) -> PutPositionByUserIdRequest:
        self.vector = vector
        return self

    def with_r(self, r: float) -> PutPositionByUserIdRequest:
        self.r = r
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PutPositionByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> PutPositionByUserIdRequest:
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
    ) -> Optional[PutPositionByUserIdRequest]:
        if data is None:
            return None
        return PutPositionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_position(Position.from_dict(data.get('position')))\
            .with_vector(Vector.from_dict(data.get('vector')))\
            .with_r(data.get('r'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "position": self.position.to_dict() if self.position else None,
            "vector": self.vector.to_dict() if self.vector else None,
            "r": self.r,
            "timeOffsetToken": self.time_offset_token,
        }


class FetchPositionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    area_model_name: str = None
    layer_model_name: str = None
    user_ids: List[str] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> FetchPositionRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> FetchPositionRequest:
        self.access_token = access_token
        return self

    def with_area_model_name(self, area_model_name: str) -> FetchPositionRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> FetchPositionRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_user_ids(self, user_ids: List[str]) -> FetchPositionRequest:
        self.user_ids = user_ids
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> FetchPositionRequest:
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
    ) -> Optional[FetchPositionRequest]:
        if data is None:
            return None
        return FetchPositionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_user_ids(None if data.get('userIds') is None else [
                data.get('userIds')[i]
                for i in range(len(data.get('userIds')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "userIds": None if self.user_ids is None else [
                self.user_ids[i]
                for i in range(len(self.user_ids))
            ],
        }


class FetchPositionFromSystemRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    layer_model_name: str = None
    user_ids: List[str] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> FetchPositionFromSystemRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> FetchPositionFromSystemRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> FetchPositionFromSystemRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_user_ids(self, user_ids: List[str]) -> FetchPositionFromSystemRequest:
        self.user_ids = user_ids
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> FetchPositionFromSystemRequest:
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
    ) -> Optional[FetchPositionFromSystemRequest]:
        if data is None:
            return None
        return FetchPositionFromSystemRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_user_ids(None if data.get('userIds') is None else [
                data.get('userIds')[i]
                for i in range(len(data.get('userIds')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "userIds": None if self.user_ids is None else [
                self.user_ids[i]
                for i in range(len(self.user_ids))
            ],
        }


class NearUserIdsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    area_model_name: str = None
    layer_model_name: str = None
    point: Position = None
    r: float = None
    limit: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> NearUserIdsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> NearUserIdsRequest:
        self.access_token = access_token
        return self

    def with_area_model_name(self, area_model_name: str) -> NearUserIdsRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> NearUserIdsRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_point(self, point: Position) -> NearUserIdsRequest:
        self.point = point
        return self

    def with_r(self, r: float) -> NearUserIdsRequest:
        self.r = r
        return self

    def with_limit(self, limit: int) -> NearUserIdsRequest:
        self.limit = limit
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> NearUserIdsRequest:
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
    ) -> Optional[NearUserIdsRequest]:
        if data is None:
            return None
        return NearUserIdsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_point(Position.from_dict(data.get('point')))\
            .with_r(data.get('r'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "point": self.point.to_dict() if self.point else None,
            "r": self.r,
            "limit": self.limit,
        }


class NearUserIdsFromSystemRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    area_model_name: str = None
    layer_model_name: str = None
    point: Position = None
    r: float = None
    limit: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> NearUserIdsFromSystemRequest:
        self.namespace_name = namespace_name
        return self

    def with_area_model_name(self, area_model_name: str) -> NearUserIdsFromSystemRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> NearUserIdsFromSystemRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_point(self, point: Position) -> NearUserIdsFromSystemRequest:
        self.point = point
        return self

    def with_r(self, r: float) -> NearUserIdsFromSystemRequest:
        self.r = r
        return self

    def with_limit(self, limit: int) -> NearUserIdsFromSystemRequest:
        self.limit = limit
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> NearUserIdsFromSystemRequest:
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
    ) -> Optional[NearUserIdsFromSystemRequest]:
        if data is None:
            return None
        return NearUserIdsFromSystemRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_point(Position.from_dict(data.get('point')))\
            .with_r(data.get('r'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "point": self.point.to_dict() if self.point else None,
            "r": self.r,
            "limit": self.limit,
        }


class ActionRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    area_model_name: str = None
    layer_model_name: str = None
    position: MyPosition = None
    scopes: List[Scope] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ActionRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> ActionRequest:
        self.access_token = access_token
        return self

    def with_area_model_name(self, area_model_name: str) -> ActionRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> ActionRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_position(self, position: MyPosition) -> ActionRequest:
        self.position = position
        return self

    def with_scopes(self, scopes: List[Scope]) -> ActionRequest:
        self.scopes = scopes
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ActionRequest:
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
    ) -> Optional[ActionRequest]:
        if data is None:
            return None
        return ActionRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_position(MyPosition.from_dict(data.get('position')))\
            .with_scopes(None if data.get('scopes') is None else [
                Scope.from_dict(data.get('scopes')[i])
                for i in range(len(data.get('scopes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "position": self.position.to_dict() if self.position else None,
            "scopes": None if self.scopes is None else [
                self.scopes[i].to_dict() if self.scopes[i] else None
                for i in range(len(self.scopes))
            ],
        }


class ActionByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    area_model_name: str = None
    layer_model_name: str = None
    position: MyPosition = None
    scopes: List[Scope] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ActionByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> ActionByUserIdRequest:
        self.user_id = user_id
        return self

    def with_area_model_name(self, area_model_name: str) -> ActionByUserIdRequest:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> ActionByUserIdRequest:
        self.layer_model_name = layer_model_name
        return self

    def with_position(self, position: MyPosition) -> ActionByUserIdRequest:
        self.position = position
        return self

    def with_scopes(self, scopes: List[Scope]) -> ActionByUserIdRequest:
        self.scopes = scopes
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ActionByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ActionByUserIdRequest:
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
    ) -> Optional[ActionByUserIdRequest]:
        if data is None:
            return None
        return ActionByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_position(MyPosition.from_dict(data.get('position')))\
            .with_scopes(None if data.get('scopes') is None else [
                Scope.from_dict(data.get('scopes')[i])
                for i in range(len(data.get('scopes')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "position": self.position.to_dict() if self.position else None,
            "scopes": None if self.scopes is None else [
                self.scopes[i].to_dict() if self.scopes[i] else None
                for i in range(len(self.scopes))
            ],
            "timeOffsetToken": self.time_offset_token,
        }