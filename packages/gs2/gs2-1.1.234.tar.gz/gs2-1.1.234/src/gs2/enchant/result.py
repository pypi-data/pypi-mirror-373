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


class DescribeBalanceParameterModelsResult(core.Gs2Result):
    items: List[BalanceParameterModel] = None

    def with_items(self, items: List[BalanceParameterModel]) -> DescribeBalanceParameterModelsResult:
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
    ) -> Optional[DescribeBalanceParameterModelsResult]:
        if data is None:
            return None
        return DescribeBalanceParameterModelsResult()\
            .with_items(None if data.get('items') is None else [
                BalanceParameterModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetBalanceParameterModelResult(core.Gs2Result):
    item: BalanceParameterModel = None

    def with_item(self, item: BalanceParameterModel) -> GetBalanceParameterModelResult:
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
    ) -> Optional[GetBalanceParameterModelResult]:
        if data is None:
            return None
        return GetBalanceParameterModelResult()\
            .with_item(BalanceParameterModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeBalanceParameterModelMastersResult(core.Gs2Result):
    items: List[BalanceParameterModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[BalanceParameterModelMaster]) -> DescribeBalanceParameterModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBalanceParameterModelMastersResult:
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
    ) -> Optional[DescribeBalanceParameterModelMastersResult]:
        if data is None:
            return None
        return DescribeBalanceParameterModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                BalanceParameterModelMaster.from_dict(data.get('items')[i])
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


class CreateBalanceParameterModelMasterResult(core.Gs2Result):
    item: BalanceParameterModelMaster = None

    def with_item(self, item: BalanceParameterModelMaster) -> CreateBalanceParameterModelMasterResult:
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
    ) -> Optional[CreateBalanceParameterModelMasterResult]:
        if data is None:
            return None
        return CreateBalanceParameterModelMasterResult()\
            .with_item(BalanceParameterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetBalanceParameterModelMasterResult(core.Gs2Result):
    item: BalanceParameterModelMaster = None

    def with_item(self, item: BalanceParameterModelMaster) -> GetBalanceParameterModelMasterResult:
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
    ) -> Optional[GetBalanceParameterModelMasterResult]:
        if data is None:
            return None
        return GetBalanceParameterModelMasterResult()\
            .with_item(BalanceParameterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateBalanceParameterModelMasterResult(core.Gs2Result):
    item: BalanceParameterModelMaster = None

    def with_item(self, item: BalanceParameterModelMaster) -> UpdateBalanceParameterModelMasterResult:
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
    ) -> Optional[UpdateBalanceParameterModelMasterResult]:
        if data is None:
            return None
        return UpdateBalanceParameterModelMasterResult()\
            .with_item(BalanceParameterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteBalanceParameterModelMasterResult(core.Gs2Result):
    item: BalanceParameterModelMaster = None

    def with_item(self, item: BalanceParameterModelMaster) -> DeleteBalanceParameterModelMasterResult:
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
    ) -> Optional[DeleteBalanceParameterModelMasterResult]:
        if data is None:
            return None
        return DeleteBalanceParameterModelMasterResult()\
            .with_item(BalanceParameterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRarityParameterModelsResult(core.Gs2Result):
    items: List[RarityParameterModel] = None

    def with_items(self, items: List[RarityParameterModel]) -> DescribeRarityParameterModelsResult:
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
    ) -> Optional[DescribeRarityParameterModelsResult]:
        if data is None:
            return None
        return DescribeRarityParameterModelsResult()\
            .with_items(None if data.get('items') is None else [
                RarityParameterModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetRarityParameterModelResult(core.Gs2Result):
    item: RarityParameterModel = None

    def with_item(self, item: RarityParameterModel) -> GetRarityParameterModelResult:
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
    ) -> Optional[GetRarityParameterModelResult]:
        if data is None:
            return None
        return GetRarityParameterModelResult()\
            .with_item(RarityParameterModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRarityParameterModelMastersResult(core.Gs2Result):
    items: List[RarityParameterModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[RarityParameterModelMaster]) -> DescribeRarityParameterModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRarityParameterModelMastersResult:
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
    ) -> Optional[DescribeRarityParameterModelMastersResult]:
        if data is None:
            return None
        return DescribeRarityParameterModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                RarityParameterModelMaster.from_dict(data.get('items')[i])
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


class CreateRarityParameterModelMasterResult(core.Gs2Result):
    item: RarityParameterModelMaster = None

    def with_item(self, item: RarityParameterModelMaster) -> CreateRarityParameterModelMasterResult:
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
    ) -> Optional[CreateRarityParameterModelMasterResult]:
        if data is None:
            return None
        return CreateRarityParameterModelMasterResult()\
            .with_item(RarityParameterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetRarityParameterModelMasterResult(core.Gs2Result):
    item: RarityParameterModelMaster = None

    def with_item(self, item: RarityParameterModelMaster) -> GetRarityParameterModelMasterResult:
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
    ) -> Optional[GetRarityParameterModelMasterResult]:
        if data is None:
            return None
        return GetRarityParameterModelMasterResult()\
            .with_item(RarityParameterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateRarityParameterModelMasterResult(core.Gs2Result):
    item: RarityParameterModelMaster = None

    def with_item(self, item: RarityParameterModelMaster) -> UpdateRarityParameterModelMasterResult:
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
    ) -> Optional[UpdateRarityParameterModelMasterResult]:
        if data is None:
            return None
        return UpdateRarityParameterModelMasterResult()\
            .with_item(RarityParameterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteRarityParameterModelMasterResult(core.Gs2Result):
    item: RarityParameterModelMaster = None

    def with_item(self, item: RarityParameterModelMaster) -> DeleteRarityParameterModelMasterResult:
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
    ) -> Optional[DeleteRarityParameterModelMasterResult]:
        if data is None:
            return None
        return DeleteRarityParameterModelMasterResult()\
            .with_item(RarityParameterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentParameterMaster = None

    def with_item(self, item: CurrentParameterMaster) -> ExportMasterResult:
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
            .with_item(CurrentParameterMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentParameterMasterResult(core.Gs2Result):
    item: CurrentParameterMaster = None

    def with_item(self, item: CurrentParameterMaster) -> GetCurrentParameterMasterResult:
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
    ) -> Optional[GetCurrentParameterMasterResult]:
        if data is None:
            return None
        return GetCurrentParameterMasterResult()\
            .with_item(CurrentParameterMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentParameterMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentParameterMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentParameterMasterResult:
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
    ) -> Optional[PreUpdateCurrentParameterMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentParameterMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentParameterMasterResult(core.Gs2Result):
    item: CurrentParameterMaster = None

    def with_item(self, item: CurrentParameterMaster) -> UpdateCurrentParameterMasterResult:
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
    ) -> Optional[UpdateCurrentParameterMasterResult]:
        if data is None:
            return None
        return UpdateCurrentParameterMasterResult()\
            .with_item(CurrentParameterMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentParameterMasterFromGitHubResult(core.Gs2Result):
    item: CurrentParameterMaster = None

    def with_item(self, item: CurrentParameterMaster) -> UpdateCurrentParameterMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentParameterMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentParameterMasterFromGitHubResult()\
            .with_item(CurrentParameterMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeBalanceParameterStatusesResult(core.Gs2Result):
    items: List[BalanceParameterStatus] = None
    next_page_token: str = None

    def with_items(self, items: List[BalanceParameterStatus]) -> DescribeBalanceParameterStatusesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBalanceParameterStatusesResult:
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
    ) -> Optional[DescribeBalanceParameterStatusesResult]:
        if data is None:
            return None
        return DescribeBalanceParameterStatusesResult()\
            .with_items(None if data.get('items') is None else [
                BalanceParameterStatus.from_dict(data.get('items')[i])
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


class DescribeBalanceParameterStatusesByUserIdResult(core.Gs2Result):
    items: List[BalanceParameterStatus] = None
    next_page_token: str = None

    def with_items(self, items: List[BalanceParameterStatus]) -> DescribeBalanceParameterStatusesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBalanceParameterStatusesByUserIdResult:
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
    ) -> Optional[DescribeBalanceParameterStatusesByUserIdResult]:
        if data is None:
            return None
        return DescribeBalanceParameterStatusesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                BalanceParameterStatus.from_dict(data.get('items')[i])
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


class GetBalanceParameterStatusResult(core.Gs2Result):
    item: BalanceParameterStatus = None

    def with_item(self, item: BalanceParameterStatus) -> GetBalanceParameterStatusResult:
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
    ) -> Optional[GetBalanceParameterStatusResult]:
        if data is None:
            return None
        return GetBalanceParameterStatusResult()\
            .with_item(BalanceParameterStatus.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetBalanceParameterStatusByUserIdResult(core.Gs2Result):
    item: BalanceParameterStatus = None

    def with_item(self, item: BalanceParameterStatus) -> GetBalanceParameterStatusByUserIdResult:
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
    ) -> Optional[GetBalanceParameterStatusByUserIdResult]:
        if data is None:
            return None
        return GetBalanceParameterStatusByUserIdResult()\
            .with_item(BalanceParameterStatus.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteBalanceParameterStatusByUserIdResult(core.Gs2Result):
    item: BalanceParameterStatus = None

    def with_item(self, item: BalanceParameterStatus) -> DeleteBalanceParameterStatusByUserIdResult:
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
    ) -> Optional[DeleteBalanceParameterStatusByUserIdResult]:
        if data is None:
            return None
        return DeleteBalanceParameterStatusByUserIdResult()\
            .with_item(BalanceParameterStatus.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ReDrawBalanceParameterStatusByUserIdResult(core.Gs2Result):
    item: BalanceParameterStatus = None
    old: BalanceParameterStatus = None

    def with_item(self, item: BalanceParameterStatus) -> ReDrawBalanceParameterStatusByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: BalanceParameterStatus) -> ReDrawBalanceParameterStatusByUserIdResult:
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
    ) -> Optional[ReDrawBalanceParameterStatusByUserIdResult]:
        if data is None:
            return None
        return ReDrawBalanceParameterStatusByUserIdResult()\
            .with_item(BalanceParameterStatus.from_dict(data.get('item')))\
            .with_old(BalanceParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class ReDrawBalanceParameterStatusByStampSheetResult(core.Gs2Result):
    item: BalanceParameterStatus = None
    old: BalanceParameterStatus = None

    def with_item(self, item: BalanceParameterStatus) -> ReDrawBalanceParameterStatusByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: BalanceParameterStatus) -> ReDrawBalanceParameterStatusByStampSheetResult:
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
    ) -> Optional[ReDrawBalanceParameterStatusByStampSheetResult]:
        if data is None:
            return None
        return ReDrawBalanceParameterStatusByStampSheetResult()\
            .with_item(BalanceParameterStatus.from_dict(data.get('item')))\
            .with_old(BalanceParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class SetBalanceParameterStatusByUserIdResult(core.Gs2Result):
    item: BalanceParameterStatus = None
    old: BalanceParameterStatus = None

    def with_item(self, item: BalanceParameterStatus) -> SetBalanceParameterStatusByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: BalanceParameterStatus) -> SetBalanceParameterStatusByUserIdResult:
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
    ) -> Optional[SetBalanceParameterStatusByUserIdResult]:
        if data is None:
            return None
        return SetBalanceParameterStatusByUserIdResult()\
            .with_item(BalanceParameterStatus.from_dict(data.get('item')))\
            .with_old(BalanceParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class SetBalanceParameterStatusByStampSheetResult(core.Gs2Result):
    item: BalanceParameterStatus = None
    old: BalanceParameterStatus = None

    def with_item(self, item: BalanceParameterStatus) -> SetBalanceParameterStatusByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: BalanceParameterStatus) -> SetBalanceParameterStatusByStampSheetResult:
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
    ) -> Optional[SetBalanceParameterStatusByStampSheetResult]:
        if data is None:
            return None
        return SetBalanceParameterStatusByStampSheetResult()\
            .with_item(BalanceParameterStatus.from_dict(data.get('item')))\
            .with_old(BalanceParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class DescribeRarityParameterStatusesResult(core.Gs2Result):
    items: List[RarityParameterStatus] = None
    next_page_token: str = None

    def with_items(self, items: List[RarityParameterStatus]) -> DescribeRarityParameterStatusesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRarityParameterStatusesResult:
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
    ) -> Optional[DescribeRarityParameterStatusesResult]:
        if data is None:
            return None
        return DescribeRarityParameterStatusesResult()\
            .with_items(None if data.get('items') is None else [
                RarityParameterStatus.from_dict(data.get('items')[i])
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


class DescribeRarityParameterStatusesByUserIdResult(core.Gs2Result):
    items: List[RarityParameterStatus] = None
    next_page_token: str = None

    def with_items(self, items: List[RarityParameterStatus]) -> DescribeRarityParameterStatusesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRarityParameterStatusesByUserIdResult:
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
    ) -> Optional[DescribeRarityParameterStatusesByUserIdResult]:
        if data is None:
            return None
        return DescribeRarityParameterStatusesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                RarityParameterStatus.from_dict(data.get('items')[i])
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


class GetRarityParameterStatusResult(core.Gs2Result):
    item: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> GetRarityParameterStatusResult:
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
    ) -> Optional[GetRarityParameterStatusResult]:
        if data is None:
            return None
        return GetRarityParameterStatusResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetRarityParameterStatusByUserIdResult(core.Gs2Result):
    item: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> GetRarityParameterStatusByUserIdResult:
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
    ) -> Optional[GetRarityParameterStatusByUserIdResult]:
        if data is None:
            return None
        return GetRarityParameterStatusByUserIdResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteRarityParameterStatusByUserIdResult(core.Gs2Result):
    item: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> DeleteRarityParameterStatusByUserIdResult:
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
    ) -> Optional[DeleteRarityParameterStatusByUserIdResult]:
        if data is None:
            return None
        return DeleteRarityParameterStatusByUserIdResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ReDrawRarityParameterStatusByUserIdResult(core.Gs2Result):
    item: RarityParameterStatus = None
    old: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> ReDrawRarityParameterStatusByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: RarityParameterStatus) -> ReDrawRarityParameterStatusByUserIdResult:
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
    ) -> Optional[ReDrawRarityParameterStatusByUserIdResult]:
        if data is None:
            return None
        return ReDrawRarityParameterStatusByUserIdResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))\
            .with_old(RarityParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class ReDrawRarityParameterStatusByStampSheetResult(core.Gs2Result):
    item: RarityParameterStatus = None
    old: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> ReDrawRarityParameterStatusByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: RarityParameterStatus) -> ReDrawRarityParameterStatusByStampSheetResult:
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
    ) -> Optional[ReDrawRarityParameterStatusByStampSheetResult]:
        if data is None:
            return None
        return ReDrawRarityParameterStatusByStampSheetResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))\
            .with_old(RarityParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class AddRarityParameterStatusByUserIdResult(core.Gs2Result):
    item: RarityParameterStatus = None
    old: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> AddRarityParameterStatusByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: RarityParameterStatus) -> AddRarityParameterStatusByUserIdResult:
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
    ) -> Optional[AddRarityParameterStatusByUserIdResult]:
        if data is None:
            return None
        return AddRarityParameterStatusByUserIdResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))\
            .with_old(RarityParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class AddRarityParameterStatusByStampSheetResult(core.Gs2Result):
    item: RarityParameterStatus = None
    old: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> AddRarityParameterStatusByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: RarityParameterStatus) -> AddRarityParameterStatusByStampSheetResult:
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
    ) -> Optional[AddRarityParameterStatusByStampSheetResult]:
        if data is None:
            return None
        return AddRarityParameterStatusByStampSheetResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))\
            .with_old(RarityParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class VerifyRarityParameterStatusResult(core.Gs2Result):
    item: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> VerifyRarityParameterStatusResult:
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
    ) -> Optional[VerifyRarityParameterStatusResult]:
        if data is None:
            return None
        return VerifyRarityParameterStatusResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyRarityParameterStatusByUserIdResult(core.Gs2Result):
    item: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> VerifyRarityParameterStatusByUserIdResult:
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
    ) -> Optional[VerifyRarityParameterStatusByUserIdResult]:
        if data is None:
            return None
        return VerifyRarityParameterStatusByUserIdResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyRarityParameterStatusByStampTaskResult(core.Gs2Result):
    item: RarityParameterStatus = None
    new_context_stack: str = None

    def with_item(self, item: RarityParameterStatus) -> VerifyRarityParameterStatusByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyRarityParameterStatusByStampTaskResult:
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
    ) -> Optional[VerifyRarityParameterStatusByStampTaskResult]:
        if data is None:
            return None
        return VerifyRarityParameterStatusByStampTaskResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class SetRarityParameterStatusByUserIdResult(core.Gs2Result):
    item: RarityParameterStatus = None
    old: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> SetRarityParameterStatusByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: RarityParameterStatus) -> SetRarityParameterStatusByUserIdResult:
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
    ) -> Optional[SetRarityParameterStatusByUserIdResult]:
        if data is None:
            return None
        return SetRarityParameterStatusByUserIdResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))\
            .with_old(RarityParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class SetRarityParameterStatusByStampSheetResult(core.Gs2Result):
    item: RarityParameterStatus = None
    old: RarityParameterStatus = None

    def with_item(self, item: RarityParameterStatus) -> SetRarityParameterStatusByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: RarityParameterStatus) -> SetRarityParameterStatusByStampSheetResult:
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
    ) -> Optional[SetRarityParameterStatusByStampSheetResult]:
        if data is None:
            return None
        return SetRarityParameterStatusByStampSheetResult()\
            .with_item(RarityParameterStatus.from_dict(data.get('item')))\
            .with_old(RarityParameterStatus.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }