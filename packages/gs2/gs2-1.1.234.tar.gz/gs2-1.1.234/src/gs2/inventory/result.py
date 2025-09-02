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


class DumpUserDataByUserIdResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DumpUserDataByUserIdResult]:
        if data is None:
            return None
        return DumpUserDataByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class CheckDumpUserDataByUserIdResult(core.Gs2Result):
    url: str = None

    def with_url(self, url: str) -> CheckDumpUserDataByUserIdResult:
        self.url = url
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckDumpUserDataByUserIdResult]:
        if data is None:
            return None
        return CheckDumpUserDataByUserIdResult()\
            .with_url(data.get('url'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
        }


class CleanUserDataByUserIdResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CleanUserDataByUserIdResult]:
        if data is None:
            return None
        return CleanUserDataByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class CheckCleanUserDataByUserIdResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckCleanUserDataByUserIdResult]:
        if data is None:
            return None
        return CheckCleanUserDataByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class PrepareImportUserDataByUserIdResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PrepareImportUserDataByUserIdResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PrepareImportUserDataByUserIdResult:
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
    ) -> Optional[PrepareImportUserDataByUserIdResult]:
        if data is None:
            return None
        return PrepareImportUserDataByUserIdResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class ImportUserDataByUserIdResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ImportUserDataByUserIdResult]:
        if data is None:
            return None
        return ImportUserDataByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class CheckImportUserDataByUserIdResult(core.Gs2Result):
    url: str = None

    def with_url(self, url: str) -> CheckImportUserDataByUserIdResult:
        self.url = url
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckImportUserDataByUserIdResult]:
        if data is None:
            return None
        return CheckImportUserDataByUserIdResult()\
            .with_url(data.get('url'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
        }


class DescribeInventoryModelMastersResult(core.Gs2Result):
    items: List[InventoryModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[InventoryModelMaster]) -> DescribeInventoryModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeInventoryModelMastersResult:
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
    ) -> Optional[DescribeInventoryModelMastersResult]:
        if data is None:
            return None
        return DescribeInventoryModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                InventoryModelMaster.from_dict(data.get('items')[i])
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


class CreateInventoryModelMasterResult(core.Gs2Result):
    item: InventoryModelMaster = None

    def with_item(self, item: InventoryModelMaster) -> CreateInventoryModelMasterResult:
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
    ) -> Optional[CreateInventoryModelMasterResult]:
        if data is None:
            return None
        return CreateInventoryModelMasterResult()\
            .with_item(InventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetInventoryModelMasterResult(core.Gs2Result):
    item: InventoryModelMaster = None

    def with_item(self, item: InventoryModelMaster) -> GetInventoryModelMasterResult:
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
    ) -> Optional[GetInventoryModelMasterResult]:
        if data is None:
            return None
        return GetInventoryModelMasterResult()\
            .with_item(InventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateInventoryModelMasterResult(core.Gs2Result):
    item: InventoryModelMaster = None

    def with_item(self, item: InventoryModelMaster) -> UpdateInventoryModelMasterResult:
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
    ) -> Optional[UpdateInventoryModelMasterResult]:
        if data is None:
            return None
        return UpdateInventoryModelMasterResult()\
            .with_item(InventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteInventoryModelMasterResult(core.Gs2Result):
    item: InventoryModelMaster = None

    def with_item(self, item: InventoryModelMaster) -> DeleteInventoryModelMasterResult:
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
    ) -> Optional[DeleteInventoryModelMasterResult]:
        if data is None:
            return None
        return DeleteInventoryModelMasterResult()\
            .with_item(InventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeInventoryModelsResult(core.Gs2Result):
    items: List[InventoryModel] = None

    def with_items(self, items: List[InventoryModel]) -> DescribeInventoryModelsResult:
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
    ) -> Optional[DescribeInventoryModelsResult]:
        if data is None:
            return None
        return DescribeInventoryModelsResult()\
            .with_items(None if data.get('items') is None else [
                InventoryModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetInventoryModelResult(core.Gs2Result):
    item: InventoryModel = None

    def with_item(self, item: InventoryModel) -> GetInventoryModelResult:
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
    ) -> Optional[GetInventoryModelResult]:
        if data is None:
            return None
        return GetInventoryModelResult()\
            .with_item(InventoryModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeItemModelMastersResult(core.Gs2Result):
    items: List[ItemModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[ItemModelMaster]) -> DescribeItemModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeItemModelMastersResult:
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
    ) -> Optional[DescribeItemModelMastersResult]:
        if data is None:
            return None
        return DescribeItemModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                ItemModelMaster.from_dict(data.get('items')[i])
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


class CreateItemModelMasterResult(core.Gs2Result):
    item: ItemModelMaster = None

    def with_item(self, item: ItemModelMaster) -> CreateItemModelMasterResult:
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
    ) -> Optional[CreateItemModelMasterResult]:
        if data is None:
            return None
        return CreateItemModelMasterResult()\
            .with_item(ItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetItemModelMasterResult(core.Gs2Result):
    item: ItemModelMaster = None

    def with_item(self, item: ItemModelMaster) -> GetItemModelMasterResult:
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
    ) -> Optional[GetItemModelMasterResult]:
        if data is None:
            return None
        return GetItemModelMasterResult()\
            .with_item(ItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateItemModelMasterResult(core.Gs2Result):
    item: ItemModelMaster = None

    def with_item(self, item: ItemModelMaster) -> UpdateItemModelMasterResult:
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
    ) -> Optional[UpdateItemModelMasterResult]:
        if data is None:
            return None
        return UpdateItemModelMasterResult()\
            .with_item(ItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteItemModelMasterResult(core.Gs2Result):
    item: ItemModelMaster = None

    def with_item(self, item: ItemModelMaster) -> DeleteItemModelMasterResult:
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
    ) -> Optional[DeleteItemModelMasterResult]:
        if data is None:
            return None
        return DeleteItemModelMasterResult()\
            .with_item(ItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeItemModelsResult(core.Gs2Result):
    items: List[ItemModel] = None

    def with_items(self, items: List[ItemModel]) -> DescribeItemModelsResult:
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
    ) -> Optional[DescribeItemModelsResult]:
        if data is None:
            return None
        return DescribeItemModelsResult()\
            .with_items(None if data.get('items') is None else [
                ItemModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetItemModelResult(core.Gs2Result):
    item: ItemModel = None

    def with_item(self, item: ItemModel) -> GetItemModelResult:
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
    ) -> Optional[GetItemModelResult]:
        if data is None:
            return None
        return GetItemModelResult()\
            .with_item(ItemModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSimpleInventoryModelMastersResult(core.Gs2Result):
    items: List[SimpleInventoryModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[SimpleInventoryModelMaster]) -> DescribeSimpleInventoryModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSimpleInventoryModelMastersResult:
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
    ) -> Optional[DescribeSimpleInventoryModelMastersResult]:
        if data is None:
            return None
        return DescribeSimpleInventoryModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                SimpleInventoryModelMaster.from_dict(data.get('items')[i])
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


class CreateSimpleInventoryModelMasterResult(core.Gs2Result):
    item: SimpleInventoryModelMaster = None

    def with_item(self, item: SimpleInventoryModelMaster) -> CreateSimpleInventoryModelMasterResult:
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
    ) -> Optional[CreateSimpleInventoryModelMasterResult]:
        if data is None:
            return None
        return CreateSimpleInventoryModelMasterResult()\
            .with_item(SimpleInventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSimpleInventoryModelMasterResult(core.Gs2Result):
    item: SimpleInventoryModelMaster = None

    def with_item(self, item: SimpleInventoryModelMaster) -> GetSimpleInventoryModelMasterResult:
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
    ) -> Optional[GetSimpleInventoryModelMasterResult]:
        if data is None:
            return None
        return GetSimpleInventoryModelMasterResult()\
            .with_item(SimpleInventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateSimpleInventoryModelMasterResult(core.Gs2Result):
    item: SimpleInventoryModelMaster = None

    def with_item(self, item: SimpleInventoryModelMaster) -> UpdateSimpleInventoryModelMasterResult:
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
    ) -> Optional[UpdateSimpleInventoryModelMasterResult]:
        if data is None:
            return None
        return UpdateSimpleInventoryModelMasterResult()\
            .with_item(SimpleInventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteSimpleInventoryModelMasterResult(core.Gs2Result):
    item: SimpleInventoryModelMaster = None

    def with_item(self, item: SimpleInventoryModelMaster) -> DeleteSimpleInventoryModelMasterResult:
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
    ) -> Optional[DeleteSimpleInventoryModelMasterResult]:
        if data is None:
            return None
        return DeleteSimpleInventoryModelMasterResult()\
            .with_item(SimpleInventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSimpleInventoryModelsResult(core.Gs2Result):
    items: List[SimpleInventoryModel] = None

    def with_items(self, items: List[SimpleInventoryModel]) -> DescribeSimpleInventoryModelsResult:
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
    ) -> Optional[DescribeSimpleInventoryModelsResult]:
        if data is None:
            return None
        return DescribeSimpleInventoryModelsResult()\
            .with_items(None if data.get('items') is None else [
                SimpleInventoryModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetSimpleInventoryModelResult(core.Gs2Result):
    item: SimpleInventoryModel = None

    def with_item(self, item: SimpleInventoryModel) -> GetSimpleInventoryModelResult:
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
    ) -> Optional[GetSimpleInventoryModelResult]:
        if data is None:
            return None
        return GetSimpleInventoryModelResult()\
            .with_item(SimpleInventoryModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSimpleItemModelMastersResult(core.Gs2Result):
    items: List[SimpleItemModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[SimpleItemModelMaster]) -> DescribeSimpleItemModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSimpleItemModelMastersResult:
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
    ) -> Optional[DescribeSimpleItemModelMastersResult]:
        if data is None:
            return None
        return DescribeSimpleItemModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItemModelMaster.from_dict(data.get('items')[i])
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


class CreateSimpleItemModelMasterResult(core.Gs2Result):
    item: SimpleItemModelMaster = None

    def with_item(self, item: SimpleItemModelMaster) -> CreateSimpleItemModelMasterResult:
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
    ) -> Optional[CreateSimpleItemModelMasterResult]:
        if data is None:
            return None
        return CreateSimpleItemModelMasterResult()\
            .with_item(SimpleItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSimpleItemModelMasterResult(core.Gs2Result):
    item: SimpleItemModelMaster = None

    def with_item(self, item: SimpleItemModelMaster) -> GetSimpleItemModelMasterResult:
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
    ) -> Optional[GetSimpleItemModelMasterResult]:
        if data is None:
            return None
        return GetSimpleItemModelMasterResult()\
            .with_item(SimpleItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateSimpleItemModelMasterResult(core.Gs2Result):
    item: SimpleItemModelMaster = None

    def with_item(self, item: SimpleItemModelMaster) -> UpdateSimpleItemModelMasterResult:
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
    ) -> Optional[UpdateSimpleItemModelMasterResult]:
        if data is None:
            return None
        return UpdateSimpleItemModelMasterResult()\
            .with_item(SimpleItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteSimpleItemModelMasterResult(core.Gs2Result):
    item: SimpleItemModelMaster = None

    def with_item(self, item: SimpleItemModelMaster) -> DeleteSimpleItemModelMasterResult:
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
    ) -> Optional[DeleteSimpleItemModelMasterResult]:
        if data is None:
            return None
        return DeleteSimpleItemModelMasterResult()\
            .with_item(SimpleItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSimpleItemModelsResult(core.Gs2Result):
    items: List[SimpleItemModel] = None

    def with_items(self, items: List[SimpleItemModel]) -> DescribeSimpleItemModelsResult:
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
    ) -> Optional[DescribeSimpleItemModelsResult]:
        if data is None:
            return None
        return DescribeSimpleItemModelsResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItemModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetSimpleItemModelResult(core.Gs2Result):
    item: SimpleItemModel = None

    def with_item(self, item: SimpleItemModel) -> GetSimpleItemModelResult:
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
    ) -> Optional[GetSimpleItemModelResult]:
        if data is None:
            return None
        return GetSimpleItemModelResult()\
            .with_item(SimpleItemModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeBigInventoryModelMastersResult(core.Gs2Result):
    items: List[BigInventoryModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[BigInventoryModelMaster]) -> DescribeBigInventoryModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBigInventoryModelMastersResult:
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
    ) -> Optional[DescribeBigInventoryModelMastersResult]:
        if data is None:
            return None
        return DescribeBigInventoryModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                BigInventoryModelMaster.from_dict(data.get('items')[i])
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


class CreateBigInventoryModelMasterResult(core.Gs2Result):
    item: BigInventoryModelMaster = None

    def with_item(self, item: BigInventoryModelMaster) -> CreateBigInventoryModelMasterResult:
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
    ) -> Optional[CreateBigInventoryModelMasterResult]:
        if data is None:
            return None
        return CreateBigInventoryModelMasterResult()\
            .with_item(BigInventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetBigInventoryModelMasterResult(core.Gs2Result):
    item: BigInventoryModelMaster = None

    def with_item(self, item: BigInventoryModelMaster) -> GetBigInventoryModelMasterResult:
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
    ) -> Optional[GetBigInventoryModelMasterResult]:
        if data is None:
            return None
        return GetBigInventoryModelMasterResult()\
            .with_item(BigInventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateBigInventoryModelMasterResult(core.Gs2Result):
    item: BigInventoryModelMaster = None

    def with_item(self, item: BigInventoryModelMaster) -> UpdateBigInventoryModelMasterResult:
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
    ) -> Optional[UpdateBigInventoryModelMasterResult]:
        if data is None:
            return None
        return UpdateBigInventoryModelMasterResult()\
            .with_item(BigInventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteBigInventoryModelMasterResult(core.Gs2Result):
    item: BigInventoryModelMaster = None

    def with_item(self, item: BigInventoryModelMaster) -> DeleteBigInventoryModelMasterResult:
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
    ) -> Optional[DeleteBigInventoryModelMasterResult]:
        if data is None:
            return None
        return DeleteBigInventoryModelMasterResult()\
            .with_item(BigInventoryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeBigInventoryModelsResult(core.Gs2Result):
    items: List[BigInventoryModel] = None

    def with_items(self, items: List[BigInventoryModel]) -> DescribeBigInventoryModelsResult:
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
    ) -> Optional[DescribeBigInventoryModelsResult]:
        if data is None:
            return None
        return DescribeBigInventoryModelsResult()\
            .with_items(None if data.get('items') is None else [
                BigInventoryModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetBigInventoryModelResult(core.Gs2Result):
    item: BigInventoryModel = None

    def with_item(self, item: BigInventoryModel) -> GetBigInventoryModelResult:
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
    ) -> Optional[GetBigInventoryModelResult]:
        if data is None:
            return None
        return GetBigInventoryModelResult()\
            .with_item(BigInventoryModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeBigItemModelMastersResult(core.Gs2Result):
    items: List[BigItemModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[BigItemModelMaster]) -> DescribeBigItemModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBigItemModelMastersResult:
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
    ) -> Optional[DescribeBigItemModelMastersResult]:
        if data is None:
            return None
        return DescribeBigItemModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                BigItemModelMaster.from_dict(data.get('items')[i])
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


class CreateBigItemModelMasterResult(core.Gs2Result):
    item: BigItemModelMaster = None

    def with_item(self, item: BigItemModelMaster) -> CreateBigItemModelMasterResult:
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
    ) -> Optional[CreateBigItemModelMasterResult]:
        if data is None:
            return None
        return CreateBigItemModelMasterResult()\
            .with_item(BigItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetBigItemModelMasterResult(core.Gs2Result):
    item: BigItemModelMaster = None

    def with_item(self, item: BigItemModelMaster) -> GetBigItemModelMasterResult:
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
    ) -> Optional[GetBigItemModelMasterResult]:
        if data is None:
            return None
        return GetBigItemModelMasterResult()\
            .with_item(BigItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateBigItemModelMasterResult(core.Gs2Result):
    item: BigItemModelMaster = None

    def with_item(self, item: BigItemModelMaster) -> UpdateBigItemModelMasterResult:
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
    ) -> Optional[UpdateBigItemModelMasterResult]:
        if data is None:
            return None
        return UpdateBigItemModelMasterResult()\
            .with_item(BigItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteBigItemModelMasterResult(core.Gs2Result):
    item: BigItemModelMaster = None

    def with_item(self, item: BigItemModelMaster) -> DeleteBigItemModelMasterResult:
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
    ) -> Optional[DeleteBigItemModelMasterResult]:
        if data is None:
            return None
        return DeleteBigItemModelMasterResult()\
            .with_item(BigItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeBigItemModelsResult(core.Gs2Result):
    items: List[BigItemModel] = None

    def with_items(self, items: List[BigItemModel]) -> DescribeBigItemModelsResult:
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
    ) -> Optional[DescribeBigItemModelsResult]:
        if data is None:
            return None
        return DescribeBigItemModelsResult()\
            .with_items(None if data.get('items') is None else [
                BigItemModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetBigItemModelResult(core.Gs2Result):
    item: BigItemModel = None

    def with_item(self, item: BigItemModel) -> GetBigItemModelResult:
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
    ) -> Optional[GetBigItemModelResult]:
        if data is None:
            return None
        return GetBigItemModelResult()\
            .with_item(BigItemModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentItemModelMaster = None

    def with_item(self, item: CurrentItemModelMaster) -> ExportMasterResult:
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
            .with_item(CurrentItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentItemModelMasterResult(core.Gs2Result):
    item: CurrentItemModelMaster = None

    def with_item(self, item: CurrentItemModelMaster) -> GetCurrentItemModelMasterResult:
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
    ) -> Optional[GetCurrentItemModelMasterResult]:
        if data is None:
            return None
        return GetCurrentItemModelMasterResult()\
            .with_item(CurrentItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentItemModelMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentItemModelMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentItemModelMasterResult:
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
    ) -> Optional[PreUpdateCurrentItemModelMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentItemModelMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentItemModelMasterResult(core.Gs2Result):
    item: CurrentItemModelMaster = None

    def with_item(self, item: CurrentItemModelMaster) -> UpdateCurrentItemModelMasterResult:
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
    ) -> Optional[UpdateCurrentItemModelMasterResult]:
        if data is None:
            return None
        return UpdateCurrentItemModelMasterResult()\
            .with_item(CurrentItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentItemModelMasterFromGitHubResult(core.Gs2Result):
    item: CurrentItemModelMaster = None

    def with_item(self, item: CurrentItemModelMaster) -> UpdateCurrentItemModelMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentItemModelMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentItemModelMasterFromGitHubResult()\
            .with_item(CurrentItemModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeInventoriesResult(core.Gs2Result):
    items: List[Inventory] = None
    next_page_token: str = None

    def with_items(self, items: List[Inventory]) -> DescribeInventoriesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeInventoriesResult:
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
    ) -> Optional[DescribeInventoriesResult]:
        if data is None:
            return None
        return DescribeInventoriesResult()\
            .with_items(None if data.get('items') is None else [
                Inventory.from_dict(data.get('items')[i])
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


class DescribeInventoriesByUserIdResult(core.Gs2Result):
    items: List[Inventory] = None
    next_page_token: str = None

    def with_items(self, items: List[Inventory]) -> DescribeInventoriesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeInventoriesByUserIdResult:
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
    ) -> Optional[DescribeInventoriesByUserIdResult]:
        if data is None:
            return None
        return DescribeInventoriesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Inventory.from_dict(data.get('items')[i])
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


class GetInventoryResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> GetInventoryResult:
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
    ) -> Optional[GetInventoryResult]:
        if data is None:
            return None
        return GetInventoryResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetInventoryByUserIdResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> GetInventoryByUserIdResult:
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
    ) -> Optional[GetInventoryByUserIdResult]:
        if data is None:
            return None
        return GetInventoryByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AddCapacityByUserIdResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> AddCapacityByUserIdResult:
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
    ) -> Optional[AddCapacityByUserIdResult]:
        if data is None:
            return None
        return AddCapacityByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SetCapacityByUserIdResult(core.Gs2Result):
    item: Inventory = None
    old: Inventory = None

    def with_item(self, item: Inventory) -> SetCapacityByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: Inventory) -> SetCapacityByUserIdResult:
        self.old = old
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetCapacityByUserIdResult]:
        if data is None:
            return None
        return SetCapacityByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))\
            .with_old(Inventory.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class DeleteInventoryByUserIdResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> DeleteInventoryByUserIdResult:
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
    ) -> Optional[DeleteInventoryByUserIdResult]:
        if data is None:
            return None
        return DeleteInventoryByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyInventoryCurrentMaxCapacityResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> VerifyInventoryCurrentMaxCapacityResult:
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
    ) -> Optional[VerifyInventoryCurrentMaxCapacityResult]:
        if data is None:
            return None
        return VerifyInventoryCurrentMaxCapacityResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyInventoryCurrentMaxCapacityByUserIdResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> VerifyInventoryCurrentMaxCapacityByUserIdResult:
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
    ) -> Optional[VerifyInventoryCurrentMaxCapacityByUserIdResult]:
        if data is None:
            return None
        return VerifyInventoryCurrentMaxCapacityByUserIdResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyInventoryCurrentMaxCapacityByStampTaskResult(core.Gs2Result):
    item: Inventory = None
    new_context_stack: str = None

    def with_item(self, item: Inventory) -> VerifyInventoryCurrentMaxCapacityByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyInventoryCurrentMaxCapacityByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyInventoryCurrentMaxCapacityByStampTaskResult]:
        if data is None:
            return None
        return VerifyInventoryCurrentMaxCapacityByStampTaskResult()\
            .with_item(Inventory.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class AddCapacityByStampSheetResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> AddCapacityByStampSheetResult:
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
    ) -> Optional[AddCapacityByStampSheetResult]:
        if data is None:
            return None
        return AddCapacityByStampSheetResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SetCapacityByStampSheetResult(core.Gs2Result):
    item: Inventory = None

    def with_item(self, item: Inventory) -> SetCapacityByStampSheetResult:
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
    ) -> Optional[SetCapacityByStampSheetResult]:
        if data is None:
            return None
        return SetCapacityByStampSheetResult()\
            .with_item(Inventory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeItemSetsResult(core.Gs2Result):
    items: List[ItemSet] = None
    next_page_token: str = None

    def with_items(self, items: List[ItemSet]) -> DescribeItemSetsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeItemSetsResult:
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
    ) -> Optional[DescribeItemSetsResult]:
        if data is None:
            return None
        return DescribeItemSetsResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
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


class DescribeItemSetsByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    next_page_token: str = None

    def with_items(self, items: List[ItemSet]) -> DescribeItemSetsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeItemSetsByUserIdResult:
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
    ) -> Optional[DescribeItemSetsByUserIdResult]:
        if data is None:
            return None
        return DescribeItemSetsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
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


class GetItemSetResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> GetItemSetResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> GetItemSetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetItemSetResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetItemSetResult]:
        if data is None:
            return None
        return GetItemSetResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class GetItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> GetItemSetByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> GetItemSetByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetItemSetByUserIdResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetItemSetByUserIdResult]:
        if data is None:
            return None
        return GetItemSetByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class GetItemWithSignatureResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    body: str = None
    signature: str = None

    def with_items(self, items: List[ItemSet]) -> GetItemWithSignatureResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> GetItemWithSignatureResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetItemWithSignatureResult:
        self.inventory = inventory
        return self

    def with_body(self, body: str) -> GetItemWithSignatureResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetItemWithSignatureResult:
        self.signature = signature
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetItemWithSignatureResult]:
        if data is None:
            return None
        return GetItemWithSignatureResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "body": self.body,
            "signature": self.signature,
        }


class GetItemWithSignatureByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    body: str = None
    signature: str = None

    def with_items(self, items: List[ItemSet]) -> GetItemWithSignatureByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> GetItemWithSignatureByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetItemWithSignatureByUserIdResult:
        self.inventory = inventory
        return self

    def with_body(self, body: str) -> GetItemWithSignatureByUserIdResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetItemWithSignatureByUserIdResult:
        self.signature = signature
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetItemWithSignatureByUserIdResult]:
        if data is None:
            return None
        return GetItemWithSignatureByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "body": self.body,
            "signature": self.signature,
        }


class AcquireItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    overflow_count: int = None

    def with_items(self, items: List[ItemSet]) -> AcquireItemSetByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> AcquireItemSetByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AcquireItemSetByUserIdResult:
        self.inventory = inventory
        return self

    def with_overflow_count(self, overflow_count: int) -> AcquireItemSetByUserIdResult:
        self.overflow_count = overflow_count
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcquireItemSetByUserIdResult]:
        if data is None:
            return None
        return AcquireItemSetByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_overflow_count(data.get('overflowCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "overflowCount": self.overflow_count,
        }


class AcquireItemSetWithGradeByUserIdResult(core.Gs2Result):
    item: ItemSet = None
    status: Status = None
    item_model: ItemModel = None
    inventory: Inventory = None
    overflow_count: int = None

    def with_item(self, item: ItemSet) -> AcquireItemSetWithGradeByUserIdResult:
        self.item = item
        return self

    def with_status(self, status: Status) -> AcquireItemSetWithGradeByUserIdResult:
        self.status = status
        return self

    def with_item_model(self, item_model: ItemModel) -> AcquireItemSetWithGradeByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AcquireItemSetWithGradeByUserIdResult:
        self.inventory = inventory
        return self

    def with_overflow_count(self, overflow_count: int) -> AcquireItemSetWithGradeByUserIdResult:
        self.overflow_count = overflow_count
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcquireItemSetWithGradeByUserIdResult]:
        if data is None:
            return None
        return AcquireItemSetWithGradeByUserIdResult()\
            .with_item(ItemSet.from_dict(data.get('item')))\
            .with_status(Status.from_dict(data.get('status')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_overflow_count(data.get('overflowCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "status": self.status.to_dict() if self.status else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "overflowCount": self.overflow_count,
        }


class ConsumeItemSetResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> ConsumeItemSetResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> ConsumeItemSetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> ConsumeItemSetResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeItemSetResult]:
        if data is None:
            return None
        return ConsumeItemSetResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class ConsumeItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> ConsumeItemSetByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> ConsumeItemSetByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> ConsumeItemSetByUserIdResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeItemSetByUserIdResult]:
        if data is None:
            return None
        return ConsumeItemSetByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DeleteItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[ItemSet]) -> DeleteItemSetByUserIdResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> DeleteItemSetByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DeleteItemSetByUserIdResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteItemSetByUserIdResult]:
        if data is None:
            return None
        return DeleteItemSetByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class VerifyItemSetResult(core.Gs2Result):
    items: List[ItemSet] = None

    def with_items(self, items: List[ItemSet]) -> VerifyItemSetResult:
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
    ) -> Optional[VerifyItemSetResult]:
        if data is None:
            return None
        return VerifyItemSetResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class VerifyItemSetByUserIdResult(core.Gs2Result):
    items: List[ItemSet] = None

    def with_items(self, items: List[ItemSet]) -> VerifyItemSetByUserIdResult:
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
    ) -> Optional[VerifyItemSetByUserIdResult]:
        if data is None:
            return None
        return VerifyItemSetByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class AcquireItemSetByStampSheetResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    overflow_count: int = None

    def with_items(self, items: List[ItemSet]) -> AcquireItemSetByStampSheetResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> AcquireItemSetByStampSheetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AcquireItemSetByStampSheetResult:
        self.inventory = inventory
        return self

    def with_overflow_count(self, overflow_count: int) -> AcquireItemSetByStampSheetResult:
        self.overflow_count = overflow_count
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcquireItemSetByStampSheetResult]:
        if data is None:
            return None
        return AcquireItemSetByStampSheetResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_overflow_count(data.get('overflowCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "overflowCount": self.overflow_count,
        }


class AcquireItemSetWithGradeByStampSheetResult(core.Gs2Result):
    item: ItemSet = None
    status: Status = None
    item_model: ItemModel = None
    inventory: Inventory = None
    overflow_count: int = None

    def with_item(self, item: ItemSet) -> AcquireItemSetWithGradeByStampSheetResult:
        self.item = item
        return self

    def with_status(self, status: Status) -> AcquireItemSetWithGradeByStampSheetResult:
        self.status = status
        return self

    def with_item_model(self, item_model: ItemModel) -> AcquireItemSetWithGradeByStampSheetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AcquireItemSetWithGradeByStampSheetResult:
        self.inventory = inventory
        return self

    def with_overflow_count(self, overflow_count: int) -> AcquireItemSetWithGradeByStampSheetResult:
        self.overflow_count = overflow_count
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcquireItemSetWithGradeByStampSheetResult]:
        if data is None:
            return None
        return AcquireItemSetWithGradeByStampSheetResult()\
            .with_item(ItemSet.from_dict(data.get('item')))\
            .with_status(Status.from_dict(data.get('status')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_overflow_count(data.get('overflowCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "status": self.status.to_dict() if self.status else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "overflowCount": self.overflow_count,
        }


class ConsumeItemSetByStampTaskResult(core.Gs2Result):
    items: List[ItemSet] = None
    item_model: ItemModel = None
    inventory: Inventory = None
    new_context_stack: str = None

    def with_items(self, items: List[ItemSet]) -> ConsumeItemSetByStampTaskResult:
        self.items = items
        return self

    def with_item_model(self, item_model: ItemModel) -> ConsumeItemSetByStampTaskResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> ConsumeItemSetByStampTaskResult:
        self.inventory = inventory
        return self

    def with_new_context_stack(self, new_context_stack: str) -> ConsumeItemSetByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeItemSetByStampTaskResult]:
        if data is None:
            return None
        return ConsumeItemSetByStampTaskResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyItemSetByStampTaskResult(core.Gs2Result):
    items: List[ItemSet] = None
    new_context_stack: str = None

    def with_items(self, items: List[ItemSet]) -> VerifyItemSetByStampTaskResult:
        self.items = items
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyItemSetByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyItemSetByStampTaskResult]:
        if data is None:
            return None
        return VerifyItemSetByStampTaskResult()\
            .with_items(None if data.get('items') is None else [
                ItemSet.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "newContextStack": self.new_context_stack,
        }


class DescribeReferenceOfResult(core.Gs2Result):
    items: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[str]) -> DescribeReferenceOfResult:
        self.items = items
        return self

    def with_item_set(self, item_set: ItemSet) -> DescribeReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DescribeReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DescribeReferenceOfResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeReferenceOfResult]:
        if data is None:
            return None
        return DescribeReferenceOfResult()\
            .with_items(None if data.get('items') is None else [
                data.get('items')[i]
                for i in range(len(data.get('items')))
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i]
                for i in range(len(self.items))
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DescribeReferenceOfByUserIdResult(core.Gs2Result):
    items: List[str] = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_items(self, items: List[str]) -> DescribeReferenceOfByUserIdResult:
        self.items = items
        return self

    def with_item_set(self, item_set: ItemSet) -> DescribeReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DescribeReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DescribeReferenceOfByUserIdResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeReferenceOfByUserIdResult]:
        if data is None:
            return None
        return DescribeReferenceOfByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                data.get('items')[i]
                for i in range(len(data.get('items')))
            ])\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i]
                for i in range(len(self.items))
            ],
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class GetReferenceOfResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> GetReferenceOfResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> GetReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> GetReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetReferenceOfResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetReferenceOfResult]:
        if data is None:
            return None
        return GetReferenceOfResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class GetReferenceOfByUserIdResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> GetReferenceOfByUserIdResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> GetReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> GetReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> GetReferenceOfByUserIdResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetReferenceOfByUserIdResult]:
        if data is None:
            return None
        return GetReferenceOfByUserIdResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class VerifyReferenceOfResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> VerifyReferenceOfResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> VerifyReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> VerifyReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> VerifyReferenceOfResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyReferenceOfResult]:
        if data is None:
            return None
        return VerifyReferenceOfResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class VerifyReferenceOfByUserIdResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> VerifyReferenceOfByUserIdResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> VerifyReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> VerifyReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> VerifyReferenceOfByUserIdResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyReferenceOfByUserIdResult]:
        if data is None:
            return None
        return VerifyReferenceOfByUserIdResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class AddReferenceOfResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> AddReferenceOfResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> AddReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> AddReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AddReferenceOfResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddReferenceOfResult]:
        if data is None:
            return None
        return AddReferenceOfResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class AddReferenceOfByUserIdResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> AddReferenceOfByUserIdResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> AddReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> AddReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AddReferenceOfByUserIdResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddReferenceOfByUserIdResult]:
        if data is None:
            return None
        return AddReferenceOfByUserIdResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DeleteReferenceOfResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> DeleteReferenceOfResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> DeleteReferenceOfResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DeleteReferenceOfResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DeleteReferenceOfResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteReferenceOfResult]:
        if data is None:
            return None
        return DeleteReferenceOfResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DeleteReferenceOfByUserIdResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> DeleteReferenceOfByUserIdResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> DeleteReferenceOfByUserIdResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DeleteReferenceOfByUserIdResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DeleteReferenceOfByUserIdResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteReferenceOfByUserIdResult]:
        if data is None:
            return None
        return DeleteReferenceOfByUserIdResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class AddReferenceOfItemSetByStampSheetResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> AddReferenceOfItemSetByStampSheetResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> AddReferenceOfItemSetByStampSheetResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> AddReferenceOfItemSetByStampSheetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> AddReferenceOfItemSetByStampSheetResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddReferenceOfItemSetByStampSheetResult]:
        if data is None:
            return None
        return AddReferenceOfItemSetByStampSheetResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class DeleteReferenceOfItemSetByStampSheetResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None

    def with_item(self, item: str) -> DeleteReferenceOfItemSetByStampSheetResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> DeleteReferenceOfItemSetByStampSheetResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> DeleteReferenceOfItemSetByStampSheetResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> DeleteReferenceOfItemSetByStampSheetResult:
        self.inventory = inventory
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteReferenceOfItemSetByStampSheetResult]:
        if data is None:
            return None
        return DeleteReferenceOfItemSetByStampSheetResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
        }


class VerifyReferenceOfByStampTaskResult(core.Gs2Result):
    item: str = None
    item_set: ItemSet = None
    item_model: ItemModel = None
    inventory: Inventory = None
    new_context_stack: str = None

    def with_item(self, item: str) -> VerifyReferenceOfByStampTaskResult:
        self.item = item
        return self

    def with_item_set(self, item_set: ItemSet) -> VerifyReferenceOfByStampTaskResult:
        self.item_set = item_set
        return self

    def with_item_model(self, item_model: ItemModel) -> VerifyReferenceOfByStampTaskResult:
        self.item_model = item_model
        return self

    def with_inventory(self, inventory: Inventory) -> VerifyReferenceOfByStampTaskResult:
        self.inventory = inventory
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyReferenceOfByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyReferenceOfByStampTaskResult]:
        if data is None:
            return None
        return VerifyReferenceOfByStampTaskResult()\
            .with_item(data.get('item'))\
            .with_item_set(ItemSet.from_dict(data.get('itemSet')))\
            .with_item_model(ItemModel.from_dict(data.get('itemModel')))\
            .with_inventory(Inventory.from_dict(data.get('inventory')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "itemSet": self.item_set.to_dict() if self.item_set else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
            "inventory": self.inventory.to_dict() if self.inventory else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeSimpleItemsResult(core.Gs2Result):
    items: List[SimpleItem] = None
    next_page_token: str = None

    def with_items(self, items: List[SimpleItem]) -> DescribeSimpleItemsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSimpleItemsResult:
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
    ) -> Optional[DescribeSimpleItemsResult]:
        if data is None:
            return None
        return DescribeSimpleItemsResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
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


class DescribeSimpleItemsByUserIdResult(core.Gs2Result):
    items: List[SimpleItem] = None
    next_page_token: str = None

    def with_items(self, items: List[SimpleItem]) -> DescribeSimpleItemsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSimpleItemsByUserIdResult:
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
    ) -> Optional[DescribeSimpleItemsByUserIdResult]:
        if data is None:
            return None
        return DescribeSimpleItemsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
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


class GetSimpleItemResult(core.Gs2Result):
    item: SimpleItem = None
    item_model: SimpleItemModel = None

    def with_item(self, item: SimpleItem) -> GetSimpleItemResult:
        self.item = item
        return self

    def with_item_model(self, item_model: SimpleItemModel) -> GetSimpleItemResult:
        self.item_model = item_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSimpleItemResult]:
        if data is None:
            return None
        return GetSimpleItemResult()\
            .with_item(SimpleItem.from_dict(data.get('item')))\
            .with_item_model(SimpleItemModel.from_dict(data.get('itemModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
        }


class GetSimpleItemByUserIdResult(core.Gs2Result):
    item: SimpleItem = None
    item_model: SimpleItemModel = None

    def with_item(self, item: SimpleItem) -> GetSimpleItemByUserIdResult:
        self.item = item
        return self

    def with_item_model(self, item_model: SimpleItemModel) -> GetSimpleItemByUserIdResult:
        self.item_model = item_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSimpleItemByUserIdResult]:
        if data is None:
            return None
        return GetSimpleItemByUserIdResult()\
            .with_item(SimpleItem.from_dict(data.get('item')))\
            .with_item_model(SimpleItemModel.from_dict(data.get('itemModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
        }


class GetSimpleItemWithSignatureResult(core.Gs2Result):
    item: SimpleItem = None
    simple_item_model: SimpleItemModel = None
    body: str = None
    signature: str = None

    def with_item(self, item: SimpleItem) -> GetSimpleItemWithSignatureResult:
        self.item = item
        return self

    def with_simple_item_model(self, simple_item_model: SimpleItemModel) -> GetSimpleItemWithSignatureResult:
        self.simple_item_model = simple_item_model
        return self

    def with_body(self, body: str) -> GetSimpleItemWithSignatureResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetSimpleItemWithSignatureResult:
        self.signature = signature
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSimpleItemWithSignatureResult]:
        if data is None:
            return None
        return GetSimpleItemWithSignatureResult()\
            .with_item(SimpleItem.from_dict(data.get('item')))\
            .with_simple_item_model(SimpleItemModel.from_dict(data.get('simpleItemModel')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "simpleItemModel": self.simple_item_model.to_dict() if self.simple_item_model else None,
            "body": self.body,
            "signature": self.signature,
        }


class GetSimpleItemWithSignatureByUserIdResult(core.Gs2Result):
    item: SimpleItem = None
    simple_item_model: SimpleItemModel = None
    body: str = None
    signature: str = None

    def with_item(self, item: SimpleItem) -> GetSimpleItemWithSignatureByUserIdResult:
        self.item = item
        return self

    def with_simple_item_model(self, simple_item_model: SimpleItemModel) -> GetSimpleItemWithSignatureByUserIdResult:
        self.simple_item_model = simple_item_model
        return self

    def with_body(self, body: str) -> GetSimpleItemWithSignatureByUserIdResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetSimpleItemWithSignatureByUserIdResult:
        self.signature = signature
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSimpleItemWithSignatureByUserIdResult]:
        if data is None:
            return None
        return GetSimpleItemWithSignatureByUserIdResult()\
            .with_item(SimpleItem.from_dict(data.get('item')))\
            .with_simple_item_model(SimpleItemModel.from_dict(data.get('simpleItemModel')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "simpleItemModel": self.simple_item_model.to_dict() if self.simple_item_model else None,
            "body": self.body,
            "signature": self.signature,
        }


class AcquireSimpleItemsByUserIdResult(core.Gs2Result):
    items: List[SimpleItem] = None

    def with_items(self, items: List[SimpleItem]) -> AcquireSimpleItemsByUserIdResult:
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
    ) -> Optional[AcquireSimpleItemsByUserIdResult]:
        if data is None:
            return None
        return AcquireSimpleItemsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class ConsumeSimpleItemsResult(core.Gs2Result):
    items: List[SimpleItem] = None

    def with_items(self, items: List[SimpleItem]) -> ConsumeSimpleItemsResult:
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
    ) -> Optional[ConsumeSimpleItemsResult]:
        if data is None:
            return None
        return ConsumeSimpleItemsResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class ConsumeSimpleItemsByUserIdResult(core.Gs2Result):
    items: List[SimpleItem] = None

    def with_items(self, items: List[SimpleItem]) -> ConsumeSimpleItemsByUserIdResult:
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
    ) -> Optional[ConsumeSimpleItemsByUserIdResult]:
        if data is None:
            return None
        return ConsumeSimpleItemsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class SetSimpleItemsByUserIdResult(core.Gs2Result):
    items: List[SimpleItem] = None

    def with_items(self, items: List[SimpleItem]) -> SetSimpleItemsByUserIdResult:
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
    ) -> Optional[SetSimpleItemsByUserIdResult]:
        if data is None:
            return None
        return SetSimpleItemsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class DeleteSimpleItemsByUserIdResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteSimpleItemsByUserIdResult]:
        if data is None:
            return None
        return DeleteSimpleItemsByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class VerifySimpleItemResult(core.Gs2Result):
    item: SimpleItem = None

    def with_item(self, item: SimpleItem) -> VerifySimpleItemResult:
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
    ) -> Optional[VerifySimpleItemResult]:
        if data is None:
            return None
        return VerifySimpleItemResult()\
            .with_item(SimpleItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifySimpleItemByUserIdResult(core.Gs2Result):
    item: SimpleItem = None

    def with_item(self, item: SimpleItem) -> VerifySimpleItemByUserIdResult:
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
    ) -> Optional[VerifySimpleItemByUserIdResult]:
        if data is None:
            return None
        return VerifySimpleItemByUserIdResult()\
            .with_item(SimpleItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AcquireSimpleItemsByStampSheetResult(core.Gs2Result):
    items: List[SimpleItem] = None

    def with_items(self, items: List[SimpleItem]) -> AcquireSimpleItemsByStampSheetResult:
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
    ) -> Optional[AcquireSimpleItemsByStampSheetResult]:
        if data is None:
            return None
        return AcquireSimpleItemsByStampSheetResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class ConsumeSimpleItemsByStampTaskResult(core.Gs2Result):
    items: List[SimpleItem] = None
    new_context_stack: str = None

    def with_items(self, items: List[SimpleItem]) -> ConsumeSimpleItemsByStampTaskResult:
        self.items = items
        return self

    def with_new_context_stack(self, new_context_stack: str) -> ConsumeSimpleItemsByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeSimpleItemsByStampTaskResult]:
        if data is None:
            return None
        return ConsumeSimpleItemsByStampTaskResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "newContextStack": self.new_context_stack,
        }


class SetSimpleItemsByStampSheetResult(core.Gs2Result):
    items: List[SimpleItem] = None

    def with_items(self, items: List[SimpleItem]) -> SetSimpleItemsByStampSheetResult:
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
    ) -> Optional[SetSimpleItemsByStampSheetResult]:
        if data is None:
            return None
        return SetSimpleItemsByStampSheetResult()\
            .with_items(None if data.get('items') is None else [
                SimpleItem.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class VerifySimpleItemByStampTaskResult(core.Gs2Result):
    item: SimpleItem = None
    new_context_stack: str = None

    def with_item(self, item: SimpleItem) -> VerifySimpleItemByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifySimpleItemByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifySimpleItemByStampTaskResult]:
        if data is None:
            return None
        return VerifySimpleItemByStampTaskResult()\
            .with_item(SimpleItem.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeBigItemsResult(core.Gs2Result):
    items: List[BigItem] = None
    next_page_token: str = None

    def with_items(self, items: List[BigItem]) -> DescribeBigItemsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBigItemsResult:
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
    ) -> Optional[DescribeBigItemsResult]:
        if data is None:
            return None
        return DescribeBigItemsResult()\
            .with_items(None if data.get('items') is None else [
                BigItem.from_dict(data.get('items')[i])
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


class DescribeBigItemsByUserIdResult(core.Gs2Result):
    items: List[BigItem] = None
    next_page_token: str = None

    def with_items(self, items: List[BigItem]) -> DescribeBigItemsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBigItemsByUserIdResult:
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
    ) -> Optional[DescribeBigItemsByUserIdResult]:
        if data is None:
            return None
        return DescribeBigItemsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                BigItem.from_dict(data.get('items')[i])
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


class GetBigItemResult(core.Gs2Result):
    item: BigItem = None
    item_model: BigItemModel = None

    def with_item(self, item: BigItem) -> GetBigItemResult:
        self.item = item
        return self

    def with_item_model(self, item_model: BigItemModel) -> GetBigItemResult:
        self.item_model = item_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetBigItemResult]:
        if data is None:
            return None
        return GetBigItemResult()\
            .with_item(BigItem.from_dict(data.get('item')))\
            .with_item_model(BigItemModel.from_dict(data.get('itemModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
        }


class GetBigItemByUserIdResult(core.Gs2Result):
    item: BigItem = None
    item_model: BigItemModel = None

    def with_item(self, item: BigItem) -> GetBigItemByUserIdResult:
        self.item = item
        return self

    def with_item_model(self, item_model: BigItemModel) -> GetBigItemByUserIdResult:
        self.item_model = item_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetBigItemByUserIdResult]:
        if data is None:
            return None
        return GetBigItemByUserIdResult()\
            .with_item(BigItem.from_dict(data.get('item')))\
            .with_item_model(BigItemModel.from_dict(data.get('itemModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "itemModel": self.item_model.to_dict() if self.item_model else None,
        }


class AcquireBigItemByUserIdResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> AcquireBigItemByUserIdResult:
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
    ) -> Optional[AcquireBigItemByUserIdResult]:
        if data is None:
            return None
        return AcquireBigItemByUserIdResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ConsumeBigItemResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> ConsumeBigItemResult:
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
    ) -> Optional[ConsumeBigItemResult]:
        if data is None:
            return None
        return ConsumeBigItemResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ConsumeBigItemByUserIdResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> ConsumeBigItemByUserIdResult:
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
    ) -> Optional[ConsumeBigItemByUserIdResult]:
        if data is None:
            return None
        return ConsumeBigItemByUserIdResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SetBigItemByUserIdResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> SetBigItemByUserIdResult:
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
    ) -> Optional[SetBigItemByUserIdResult]:
        if data is None:
            return None
        return SetBigItemByUserIdResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteBigItemByUserIdResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> DeleteBigItemByUserIdResult:
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
    ) -> Optional[DeleteBigItemByUserIdResult]:
        if data is None:
            return None
        return DeleteBigItemByUserIdResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyBigItemResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> VerifyBigItemResult:
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
    ) -> Optional[VerifyBigItemResult]:
        if data is None:
            return None
        return VerifyBigItemResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyBigItemByUserIdResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> VerifyBigItemByUserIdResult:
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
    ) -> Optional[VerifyBigItemByUserIdResult]:
        if data is None:
            return None
        return VerifyBigItemByUserIdResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AcquireBigItemByStampSheetResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> AcquireBigItemByStampSheetResult:
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
    ) -> Optional[AcquireBigItemByStampSheetResult]:
        if data is None:
            return None
        return AcquireBigItemByStampSheetResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ConsumeBigItemByStampTaskResult(core.Gs2Result):
    item: BigItem = None
    new_context_stack: str = None

    def with_item(self, item: BigItem) -> ConsumeBigItemByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> ConsumeBigItemByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeBigItemByStampTaskResult]:
        if data is None:
            return None
        return ConsumeBigItemByStampTaskResult()\
            .with_item(BigItem.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class SetBigItemByStampSheetResult(core.Gs2Result):
    item: BigItem = None

    def with_item(self, item: BigItem) -> SetBigItemByStampSheetResult:
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
    ) -> Optional[SetBigItemByStampSheetResult]:
        if data is None:
            return None
        return SetBigItemByStampSheetResult()\
            .with_item(BigItem.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyBigItemByStampTaskResult(core.Gs2Result):
    item: BigItem = None
    new_context_stack: str = None

    def with_item(self, item: BigItem) -> VerifyBigItemByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyBigItemByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyBigItemByStampTaskResult]:
        if data is None:
            return None
        return VerifyBigItemByStampTaskResult()\
            .with_item(BigItem.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }