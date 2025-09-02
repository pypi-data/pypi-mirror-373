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

from ..core.model import *
from .model import *


class DescribeNamespacesResult(core.Gs2Result):
    items: List[Namespace] = None
    next_page_token: str = None

    def with_items(self, items: List[Namespace]) -> DescribeNamespacesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeNamespacesResult:
        self.next_page_token = next_page_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeNamespacesResult]:
        if data is None:
            return None
        return DescribeNamespacesResult()\
            .with_items(None if data.get('items') is None else [
                Namespace.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> CreateNamespaceResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateNamespaceResult]:
        if data is None:
            return None
        return CreateNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetNamespaceStatusResult(core.Gs2Result):
    status: str = None

    def with_status(self, status: str) -> GetNamespaceStatusResult:
        self.status = status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceStatusResult]:
        if data is None:
            return None
        return GetNamespaceStatusResult()\
            .with_status(data.get('status'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
        }


class GetNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> GetNamespaceResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetNamespaceResult]:
        if data is None:
            return None
        return GetNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> UpdateNamespaceResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateNamespaceResult]:
        if data is None:
            return None
        return UpdateNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> DeleteNamespaceResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteNamespaceResult]:
        if data is None:
            return None
        return DeleteNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetServiceVersionResult(core.Gs2Result):
    item: str = None

    def with_item(self, item: str) -> GetServiceVersionResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetServiceVersionResult]:
        if data is None:
            return None
        return GetServiceVersionResult()\
            .with_item(data.get('item'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
        }


class DescribeAreaModelsResult(core.Gs2Result):
    items: List[AreaModel] = None

    def with_items(self, items: List[AreaModel]) -> DescribeAreaModelsResult:
        self.items = items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeAreaModelsResult]:
        if data is None:
            return None
        return DescribeAreaModelsResult()\
            .with_items(None if data.get('items') is None else [
                AreaModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetAreaModelResult(core.Gs2Result):
    item: AreaModel = None

    def with_item(self, item: AreaModel) -> GetAreaModelResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetAreaModelResult]:
        if data is None:
            return None
        return GetAreaModelResult()\
            .with_item(AreaModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeAreaModelMastersResult(core.Gs2Result):
    items: List[AreaModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[AreaModelMaster]) -> DescribeAreaModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeAreaModelMastersResult:
        self.next_page_token = next_page_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeAreaModelMastersResult]:
        if data is None:
            return None
        return DescribeAreaModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                AreaModelMaster.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateAreaModelMasterResult(core.Gs2Result):
    item: AreaModelMaster = None

    def with_item(self, item: AreaModelMaster) -> CreateAreaModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateAreaModelMasterResult]:
        if data is None:
            return None
        return CreateAreaModelMasterResult()\
            .with_item(AreaModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetAreaModelMasterResult(core.Gs2Result):
    item: AreaModelMaster = None

    def with_item(self, item: AreaModelMaster) -> GetAreaModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetAreaModelMasterResult]:
        if data is None:
            return None
        return GetAreaModelMasterResult()\
            .with_item(AreaModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateAreaModelMasterResult(core.Gs2Result):
    item: AreaModelMaster = None

    def with_item(self, item: AreaModelMaster) -> UpdateAreaModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateAreaModelMasterResult]:
        if data is None:
            return None
        return UpdateAreaModelMasterResult()\
            .with_item(AreaModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteAreaModelMasterResult(core.Gs2Result):
    item: AreaModelMaster = None

    def with_item(self, item: AreaModelMaster) -> DeleteAreaModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteAreaModelMasterResult]:
        if data is None:
            return None
        return DeleteAreaModelMasterResult()\
            .with_item(AreaModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeLayerModelsResult(core.Gs2Result):
    items: List[LayerModel] = None

    def with_items(self, items: List[LayerModel]) -> DescribeLayerModelsResult:
        self.items = items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeLayerModelsResult]:
        if data is None:
            return None
        return DescribeLayerModelsResult()\
            .with_items(None if data.get('items') is None else [
                LayerModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetLayerModelResult(core.Gs2Result):
    item: LayerModel = None

    def with_item(self, item: LayerModel) -> GetLayerModelResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetLayerModelResult]:
        if data is None:
            return None
        return GetLayerModelResult()\
            .with_item(LayerModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeLayerModelMastersResult(core.Gs2Result):
    items: List[LayerModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[LayerModelMaster]) -> DescribeLayerModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeLayerModelMastersResult:
        self.next_page_token = next_page_token
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeLayerModelMastersResult]:
        if data is None:
            return None
        return DescribeLayerModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                LayerModelMaster.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateLayerModelMasterResult(core.Gs2Result):
    item: LayerModelMaster = None

    def with_item(self, item: LayerModelMaster) -> CreateLayerModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateLayerModelMasterResult]:
        if data is None:
            return None
        return CreateLayerModelMasterResult()\
            .with_item(LayerModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetLayerModelMasterResult(core.Gs2Result):
    item: LayerModelMaster = None

    def with_item(self, item: LayerModelMaster) -> GetLayerModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetLayerModelMasterResult]:
        if data is None:
            return None
        return GetLayerModelMasterResult()\
            .with_item(LayerModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateLayerModelMasterResult(core.Gs2Result):
    item: LayerModelMaster = None

    def with_item(self, item: LayerModelMaster) -> UpdateLayerModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateLayerModelMasterResult]:
        if data is None:
            return None
        return UpdateLayerModelMasterResult()\
            .with_item(LayerModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteLayerModelMasterResult(core.Gs2Result):
    item: LayerModelMaster = None

    def with_item(self, item: LayerModelMaster) -> DeleteLayerModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteLayerModelMasterResult]:
        if data is None:
            return None
        return DeleteLayerModelMasterResult()\
            .with_item(LayerModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentFieldMaster = None

    def with_item(self, item: CurrentFieldMaster) -> ExportMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ExportMasterResult]:
        if data is None:
            return None
        return ExportMasterResult()\
            .with_item(CurrentFieldMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentFieldMasterResult(core.Gs2Result):
    item: CurrentFieldMaster = None

    def with_item(self, item: CurrentFieldMaster) -> GetCurrentFieldMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCurrentFieldMasterResult]:
        if data is None:
            return None
        return GetCurrentFieldMasterResult()\
            .with_item(CurrentFieldMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentFieldMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentFieldMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentFieldMasterResult:
        self.upload_url = upload_url
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PreUpdateCurrentFieldMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentFieldMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentFieldMasterResult(core.Gs2Result):
    item: CurrentFieldMaster = None

    def with_item(self, item: CurrentFieldMaster) -> UpdateCurrentFieldMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentFieldMasterResult]:
        if data is None:
            return None
        return UpdateCurrentFieldMasterResult()\
            .with_item(CurrentFieldMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentFieldMasterFromGitHubResult(core.Gs2Result):
    item: CurrentFieldMaster = None

    def with_item(self, item: CurrentFieldMaster) -> UpdateCurrentFieldMasterFromGitHubResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentFieldMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentFieldMasterFromGitHubResult()\
            .with_item(CurrentFieldMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PutPositionResult(core.Gs2Result):
    item: Spatial = None

    def with_item(self, item: Spatial) -> PutPositionResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PutPositionResult]:
        if data is None:
            return None
        return PutPositionResult()\
            .with_item(Spatial.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PutPositionByUserIdResult(core.Gs2Result):
    item: Spatial = None

    def with_item(self, item: Spatial) -> PutPositionByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PutPositionByUserIdResult]:
        if data is None:
            return None
        return PutPositionByUserIdResult()\
            .with_item(Spatial.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class FetchPositionResult(core.Gs2Result):
    items: List[Spatial] = None

    def with_items(self, items: List[Spatial]) -> FetchPositionResult:
        self.items = items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[FetchPositionResult]:
        if data is None:
            return None
        return FetchPositionResult()\
            .with_items(None if data.get('items') is None else [
                Spatial.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class FetchPositionFromSystemResult(core.Gs2Result):
    items: List[Spatial] = None

    def with_items(self, items: List[Spatial]) -> FetchPositionFromSystemResult:
        self.items = items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[FetchPositionFromSystemResult]:
        if data is None:
            return None
        return FetchPositionFromSystemResult()\
            .with_items(None if data.get('items') is None else [
                Spatial.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class NearUserIdsResult(core.Gs2Result):
    items: List[str] = None

    def with_items(self, items: List[str]) -> NearUserIdsResult:
        self.items = items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[NearUserIdsResult]:
        if data is None:
            return None
        return NearUserIdsResult()\
            .with_items(None if data.get('items') is None else [
                data.get('items')[i]
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i]
                for i in range(len(self.items))
            ],
        }


class NearUserIdsFromSystemResult(core.Gs2Result):
    items: List[str] = None

    def with_items(self, items: List[str]) -> NearUserIdsFromSystemResult:
        self.items = items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[NearUserIdsFromSystemResult]:
        if data is None:
            return None
        return NearUserIdsFromSystemResult()\
            .with_items(None if data.get('items') is None else [
                data.get('items')[i]
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i]
                for i in range(len(self.items))
            ],
        }


class ActionResult(core.Gs2Result):
    items: List[Spatial] = None

    def with_items(self, items: List[Spatial]) -> ActionResult:
        self.items = items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ActionResult]:
        if data is None:
            return None
        return ActionResult()\
            .with_items(None if data.get('items') is None else [
                Spatial.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class ActionByUserIdResult(core.Gs2Result):
    items: List[Spatial] = None

    def with_items(self, items: List[Spatial]) -> ActionByUserIdResult:
        self.items = items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ActionByUserIdResult]:
        if data is None:
            return None
        return ActionByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Spatial.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }