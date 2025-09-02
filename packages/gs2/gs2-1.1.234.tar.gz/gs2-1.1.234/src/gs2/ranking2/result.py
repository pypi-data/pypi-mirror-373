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


class DescribeGlobalRankingModelsResult(core.Gs2Result):
    items: List[GlobalRankingModel] = None

    def with_items(self, items: List[GlobalRankingModel]) -> DescribeGlobalRankingModelsResult:
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
    ) -> Optional[DescribeGlobalRankingModelsResult]:
        if data is None:
            return None
        return DescribeGlobalRankingModelsResult()\
            .with_items(None if data.get('items') is None else [
                GlobalRankingModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetGlobalRankingModelResult(core.Gs2Result):
    item: GlobalRankingModel = None

    def with_item(self, item: GlobalRankingModel) -> GetGlobalRankingModelResult:
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
    ) -> Optional[GetGlobalRankingModelResult]:
        if data is None:
            return None
        return GetGlobalRankingModelResult()\
            .with_item(GlobalRankingModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeGlobalRankingModelMastersResult(core.Gs2Result):
    items: List[GlobalRankingModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[GlobalRankingModelMaster]) -> DescribeGlobalRankingModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGlobalRankingModelMastersResult:
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
    ) -> Optional[DescribeGlobalRankingModelMastersResult]:
        if data is None:
            return None
        return DescribeGlobalRankingModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                GlobalRankingModelMaster.from_dict(data.get('items')[i])
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


class CreateGlobalRankingModelMasterResult(core.Gs2Result):
    item: GlobalRankingModelMaster = None

    def with_item(self, item: GlobalRankingModelMaster) -> CreateGlobalRankingModelMasterResult:
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
    ) -> Optional[CreateGlobalRankingModelMasterResult]:
        if data is None:
            return None
        return CreateGlobalRankingModelMasterResult()\
            .with_item(GlobalRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGlobalRankingModelMasterResult(core.Gs2Result):
    item: GlobalRankingModelMaster = None

    def with_item(self, item: GlobalRankingModelMaster) -> GetGlobalRankingModelMasterResult:
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
    ) -> Optional[GetGlobalRankingModelMasterResult]:
        if data is None:
            return None
        return GetGlobalRankingModelMasterResult()\
            .with_item(GlobalRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateGlobalRankingModelMasterResult(core.Gs2Result):
    item: GlobalRankingModelMaster = None

    def with_item(self, item: GlobalRankingModelMaster) -> UpdateGlobalRankingModelMasterResult:
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
    ) -> Optional[UpdateGlobalRankingModelMasterResult]:
        if data is None:
            return None
        return UpdateGlobalRankingModelMasterResult()\
            .with_item(GlobalRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteGlobalRankingModelMasterResult(core.Gs2Result):
    item: GlobalRankingModelMaster = None

    def with_item(self, item: GlobalRankingModelMaster) -> DeleteGlobalRankingModelMasterResult:
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
    ) -> Optional[DeleteGlobalRankingModelMasterResult]:
        if data is None:
            return None
        return DeleteGlobalRankingModelMasterResult()\
            .with_item(GlobalRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeGlobalRankingScoresResult(core.Gs2Result):
    items: List[GlobalRankingScore] = None
    next_page_token: str = None

    def with_items(self, items: List[GlobalRankingScore]) -> DescribeGlobalRankingScoresResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGlobalRankingScoresResult:
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
    ) -> Optional[DescribeGlobalRankingScoresResult]:
        if data is None:
            return None
        return DescribeGlobalRankingScoresResult()\
            .with_items(None if data.get('items') is None else [
                GlobalRankingScore.from_dict(data.get('items')[i])
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


class DescribeGlobalRankingScoresByUserIdResult(core.Gs2Result):
    items: List[GlobalRankingScore] = None
    next_page_token: str = None

    def with_items(self, items: List[GlobalRankingScore]) -> DescribeGlobalRankingScoresByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGlobalRankingScoresByUserIdResult:
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
    ) -> Optional[DescribeGlobalRankingScoresByUserIdResult]:
        if data is None:
            return None
        return DescribeGlobalRankingScoresByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                GlobalRankingScore.from_dict(data.get('items')[i])
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


class PutGlobalRankingScoreResult(core.Gs2Result):
    item: GlobalRankingScore = None

    def with_item(self, item: GlobalRankingScore) -> PutGlobalRankingScoreResult:
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
    ) -> Optional[PutGlobalRankingScoreResult]:
        if data is None:
            return None
        return PutGlobalRankingScoreResult()\
            .with_item(GlobalRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PutGlobalRankingScoreByUserIdResult(core.Gs2Result):
    item: GlobalRankingScore = None

    def with_item(self, item: GlobalRankingScore) -> PutGlobalRankingScoreByUserIdResult:
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
    ) -> Optional[PutGlobalRankingScoreByUserIdResult]:
        if data is None:
            return None
        return PutGlobalRankingScoreByUserIdResult()\
            .with_item(GlobalRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGlobalRankingScoreResult(core.Gs2Result):
    item: GlobalRankingScore = None

    def with_item(self, item: GlobalRankingScore) -> GetGlobalRankingScoreResult:
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
    ) -> Optional[GetGlobalRankingScoreResult]:
        if data is None:
            return None
        return GetGlobalRankingScoreResult()\
            .with_item(GlobalRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGlobalRankingScoreByUserIdResult(core.Gs2Result):
    item: GlobalRankingScore = None

    def with_item(self, item: GlobalRankingScore) -> GetGlobalRankingScoreByUserIdResult:
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
    ) -> Optional[GetGlobalRankingScoreByUserIdResult]:
        if data is None:
            return None
        return GetGlobalRankingScoreByUserIdResult()\
            .with_item(GlobalRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteGlobalRankingScoreByUserIdResult(core.Gs2Result):
    item: GlobalRankingScore = None

    def with_item(self, item: GlobalRankingScore) -> DeleteGlobalRankingScoreByUserIdResult:
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
    ) -> Optional[DeleteGlobalRankingScoreByUserIdResult]:
        if data is None:
            return None
        return DeleteGlobalRankingScoreByUserIdResult()\
            .with_item(GlobalRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyGlobalRankingScoreResult(core.Gs2Result):
    item: GlobalRankingScore = None

    def with_item(self, item: GlobalRankingScore) -> VerifyGlobalRankingScoreResult:
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
    ) -> Optional[VerifyGlobalRankingScoreResult]:
        if data is None:
            return None
        return VerifyGlobalRankingScoreResult()\
            .with_item(GlobalRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyGlobalRankingScoreByUserIdResult(core.Gs2Result):
    item: GlobalRankingScore = None

    def with_item(self, item: GlobalRankingScore) -> VerifyGlobalRankingScoreByUserIdResult:
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
    ) -> Optional[VerifyGlobalRankingScoreByUserIdResult]:
        if data is None:
            return None
        return VerifyGlobalRankingScoreByUserIdResult()\
            .with_item(GlobalRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyGlobalRankingScoreByStampTaskResult(core.Gs2Result):
    item: GlobalRankingScore = None
    new_context_stack: str = None

    def with_item(self, item: GlobalRankingScore) -> VerifyGlobalRankingScoreByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyGlobalRankingScoreByStampTaskResult:
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
    ) -> Optional[VerifyGlobalRankingScoreByStampTaskResult]:
        if data is None:
            return None
        return VerifyGlobalRankingScoreByStampTaskResult()\
            .with_item(GlobalRankingScore.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeGlobalRankingReceivedRewardsResult(core.Gs2Result):
    items: List[GlobalRankingReceivedReward] = None
    next_page_token: str = None

    def with_items(self, items: List[GlobalRankingReceivedReward]) -> DescribeGlobalRankingReceivedRewardsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGlobalRankingReceivedRewardsResult:
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
    ) -> Optional[DescribeGlobalRankingReceivedRewardsResult]:
        if data is None:
            return None
        return DescribeGlobalRankingReceivedRewardsResult()\
            .with_items(None if data.get('items') is None else [
                GlobalRankingReceivedReward.from_dict(data.get('items')[i])
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


class DescribeGlobalRankingReceivedRewardsByUserIdResult(core.Gs2Result):
    items: List[GlobalRankingReceivedReward] = None
    next_page_token: str = None

    def with_items(self, items: List[GlobalRankingReceivedReward]) -> DescribeGlobalRankingReceivedRewardsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGlobalRankingReceivedRewardsByUserIdResult:
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
    ) -> Optional[DescribeGlobalRankingReceivedRewardsByUserIdResult]:
        if data is None:
            return None
        return DescribeGlobalRankingReceivedRewardsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                GlobalRankingReceivedReward.from_dict(data.get('items')[i])
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


class CreateGlobalRankingReceivedRewardResult(core.Gs2Result):
    item: GlobalRankingReceivedReward = None

    def with_item(self, item: GlobalRankingReceivedReward) -> CreateGlobalRankingReceivedRewardResult:
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
    ) -> Optional[CreateGlobalRankingReceivedRewardResult]:
        if data is None:
            return None
        return CreateGlobalRankingReceivedRewardResult()\
            .with_item(GlobalRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CreateGlobalRankingReceivedRewardByUserIdResult(core.Gs2Result):
    item: GlobalRankingReceivedReward = None

    def with_item(self, item: GlobalRankingReceivedReward) -> CreateGlobalRankingReceivedRewardByUserIdResult:
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
    ) -> Optional[CreateGlobalRankingReceivedRewardByUserIdResult]:
        if data is None:
            return None
        return CreateGlobalRankingReceivedRewardByUserIdResult()\
            .with_item(GlobalRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ReceiveGlobalRankingReceivedRewardResult(core.Gs2Result):
    item: GlobalRankingModel = None
    acquire_actions: List[AcquireAction] = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: GlobalRankingModel) -> ReceiveGlobalRankingReceivedRewardResult:
        self.item = item
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> ReceiveGlobalRankingReceivedRewardResult:
        self.acquire_actions = acquire_actions
        return self

    def with_transaction_id(self, transaction_id: str) -> ReceiveGlobalRankingReceivedRewardResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> ReceiveGlobalRankingReceivedRewardResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> ReceiveGlobalRankingReceivedRewardResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> ReceiveGlobalRankingReceivedRewardResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> ReceiveGlobalRankingReceivedRewardResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> ReceiveGlobalRankingReceivedRewardResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> ReceiveGlobalRankingReceivedRewardResult:
        self.transaction_result = transaction_result
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ReceiveGlobalRankingReceivedRewardResult]:
        if data is None:
            return None
        return ReceiveGlobalRankingReceivedRewardResult()\
            .with_item(GlobalRankingModel.from_dict(data.get('item')))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class ReceiveGlobalRankingReceivedRewardByUserIdResult(core.Gs2Result):
    item: GlobalRankingModel = None
    acquire_actions: List[AcquireAction] = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: GlobalRankingModel) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.item = item
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.acquire_actions = acquire_actions
        return self

    def with_transaction_id(self, transaction_id: str) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        self.transaction_result = transaction_result
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ReceiveGlobalRankingReceivedRewardByUserIdResult]:
        if data is None:
            return None
        return ReceiveGlobalRankingReceivedRewardByUserIdResult()\
            .with_item(GlobalRankingModel.from_dict(data.get('item')))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class GetGlobalRankingReceivedRewardResult(core.Gs2Result):
    item: GlobalRankingReceivedReward = None

    def with_item(self, item: GlobalRankingReceivedReward) -> GetGlobalRankingReceivedRewardResult:
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
    ) -> Optional[GetGlobalRankingReceivedRewardResult]:
        if data is None:
            return None
        return GetGlobalRankingReceivedRewardResult()\
            .with_item(GlobalRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGlobalRankingReceivedRewardByUserIdResult(core.Gs2Result):
    item: GlobalRankingReceivedReward = None

    def with_item(self, item: GlobalRankingReceivedReward) -> GetGlobalRankingReceivedRewardByUserIdResult:
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
    ) -> Optional[GetGlobalRankingReceivedRewardByUserIdResult]:
        if data is None:
            return None
        return GetGlobalRankingReceivedRewardByUserIdResult()\
            .with_item(GlobalRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteGlobalRankingReceivedRewardByUserIdResult(core.Gs2Result):
    item: GlobalRankingReceivedReward = None

    def with_item(self, item: GlobalRankingReceivedReward) -> DeleteGlobalRankingReceivedRewardByUserIdResult:
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
    ) -> Optional[DeleteGlobalRankingReceivedRewardByUserIdResult]:
        if data is None:
            return None
        return DeleteGlobalRankingReceivedRewardByUserIdResult()\
            .with_item(GlobalRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CreateGlobalRankingReceivedRewardByStampTaskResult(core.Gs2Result):
    item: GlobalRankingReceivedReward = None
    new_context_stack: str = None

    def with_item(self, item: GlobalRankingReceivedReward) -> CreateGlobalRankingReceivedRewardByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> CreateGlobalRankingReceivedRewardByStampTaskResult:
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
    ) -> Optional[CreateGlobalRankingReceivedRewardByStampTaskResult]:
        if data is None:
            return None
        return CreateGlobalRankingReceivedRewardByStampTaskResult()\
            .with_item(GlobalRankingReceivedReward.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeGlobalRankingsResult(core.Gs2Result):
    items: List[GlobalRankingData] = None
    next_page_token: str = None

    def with_items(self, items: List[GlobalRankingData]) -> DescribeGlobalRankingsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGlobalRankingsResult:
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
    ) -> Optional[DescribeGlobalRankingsResult]:
        if data is None:
            return None
        return DescribeGlobalRankingsResult()\
            .with_items(None if data.get('items') is None else [
                GlobalRankingData.from_dict(data.get('items')[i])
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


class DescribeGlobalRankingsByUserIdResult(core.Gs2Result):
    items: List[GlobalRankingData] = None
    next_page_token: str = None

    def with_items(self, items: List[GlobalRankingData]) -> DescribeGlobalRankingsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGlobalRankingsByUserIdResult:
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
    ) -> Optional[DescribeGlobalRankingsByUserIdResult]:
        if data is None:
            return None
        return DescribeGlobalRankingsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                GlobalRankingData.from_dict(data.get('items')[i])
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


class GetGlobalRankingResult(core.Gs2Result):
    item: GlobalRankingData = None

    def with_item(self, item: GlobalRankingData) -> GetGlobalRankingResult:
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
    ) -> Optional[GetGlobalRankingResult]:
        if data is None:
            return None
        return GetGlobalRankingResult()\
            .with_item(GlobalRankingData.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGlobalRankingByUserIdResult(core.Gs2Result):
    item: GlobalRankingData = None

    def with_item(self, item: GlobalRankingData) -> GetGlobalRankingByUserIdResult:
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
    ) -> Optional[GetGlobalRankingByUserIdResult]:
        if data is None:
            return None
        return GetGlobalRankingByUserIdResult()\
            .with_item(GlobalRankingData.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeClusterRankingModelsResult(core.Gs2Result):
    items: List[ClusterRankingModel] = None

    def with_items(self, items: List[ClusterRankingModel]) -> DescribeClusterRankingModelsResult:
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
    ) -> Optional[DescribeClusterRankingModelsResult]:
        if data is None:
            return None
        return DescribeClusterRankingModelsResult()\
            .with_items(None if data.get('items') is None else [
                ClusterRankingModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetClusterRankingModelResult(core.Gs2Result):
    item: ClusterRankingModel = None

    def with_item(self, item: ClusterRankingModel) -> GetClusterRankingModelResult:
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
    ) -> Optional[GetClusterRankingModelResult]:
        if data is None:
            return None
        return GetClusterRankingModelResult()\
            .with_item(ClusterRankingModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeClusterRankingModelMastersResult(core.Gs2Result):
    items: List[ClusterRankingModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[ClusterRankingModelMaster]) -> DescribeClusterRankingModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeClusterRankingModelMastersResult:
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
    ) -> Optional[DescribeClusterRankingModelMastersResult]:
        if data is None:
            return None
        return DescribeClusterRankingModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                ClusterRankingModelMaster.from_dict(data.get('items')[i])
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


class CreateClusterRankingModelMasterResult(core.Gs2Result):
    item: ClusterRankingModelMaster = None

    def with_item(self, item: ClusterRankingModelMaster) -> CreateClusterRankingModelMasterResult:
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
    ) -> Optional[CreateClusterRankingModelMasterResult]:
        if data is None:
            return None
        return CreateClusterRankingModelMasterResult()\
            .with_item(ClusterRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetClusterRankingModelMasterResult(core.Gs2Result):
    item: ClusterRankingModelMaster = None

    def with_item(self, item: ClusterRankingModelMaster) -> GetClusterRankingModelMasterResult:
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
    ) -> Optional[GetClusterRankingModelMasterResult]:
        if data is None:
            return None
        return GetClusterRankingModelMasterResult()\
            .with_item(ClusterRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateClusterRankingModelMasterResult(core.Gs2Result):
    item: ClusterRankingModelMaster = None

    def with_item(self, item: ClusterRankingModelMaster) -> UpdateClusterRankingModelMasterResult:
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
    ) -> Optional[UpdateClusterRankingModelMasterResult]:
        if data is None:
            return None
        return UpdateClusterRankingModelMasterResult()\
            .with_item(ClusterRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteClusterRankingModelMasterResult(core.Gs2Result):
    item: ClusterRankingModelMaster = None

    def with_item(self, item: ClusterRankingModelMaster) -> DeleteClusterRankingModelMasterResult:
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
    ) -> Optional[DeleteClusterRankingModelMasterResult]:
        if data is None:
            return None
        return DeleteClusterRankingModelMasterResult()\
            .with_item(ClusterRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeClusterRankingScoresResult(core.Gs2Result):
    items: List[ClusterRankingScore] = None
    next_page_token: str = None

    def with_items(self, items: List[ClusterRankingScore]) -> DescribeClusterRankingScoresResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeClusterRankingScoresResult:
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
    ) -> Optional[DescribeClusterRankingScoresResult]:
        if data is None:
            return None
        return DescribeClusterRankingScoresResult()\
            .with_items(None if data.get('items') is None else [
                ClusterRankingScore.from_dict(data.get('items')[i])
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


class DescribeClusterRankingScoresByUserIdResult(core.Gs2Result):
    items: List[ClusterRankingScore] = None
    next_page_token: str = None

    def with_items(self, items: List[ClusterRankingScore]) -> DescribeClusterRankingScoresByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeClusterRankingScoresByUserIdResult:
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
    ) -> Optional[DescribeClusterRankingScoresByUserIdResult]:
        if data is None:
            return None
        return DescribeClusterRankingScoresByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ClusterRankingScore.from_dict(data.get('items')[i])
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


class PutClusterRankingScoreResult(core.Gs2Result):
    item: ClusterRankingScore = None

    def with_item(self, item: ClusterRankingScore) -> PutClusterRankingScoreResult:
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
    ) -> Optional[PutClusterRankingScoreResult]:
        if data is None:
            return None
        return PutClusterRankingScoreResult()\
            .with_item(ClusterRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PutClusterRankingScoreByUserIdResult(core.Gs2Result):
    item: ClusterRankingScore = None

    def with_item(self, item: ClusterRankingScore) -> PutClusterRankingScoreByUserIdResult:
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
    ) -> Optional[PutClusterRankingScoreByUserIdResult]:
        if data is None:
            return None
        return PutClusterRankingScoreByUserIdResult()\
            .with_item(ClusterRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetClusterRankingScoreResult(core.Gs2Result):
    item: ClusterRankingScore = None

    def with_item(self, item: ClusterRankingScore) -> GetClusterRankingScoreResult:
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
    ) -> Optional[GetClusterRankingScoreResult]:
        if data is None:
            return None
        return GetClusterRankingScoreResult()\
            .with_item(ClusterRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetClusterRankingScoreByUserIdResult(core.Gs2Result):
    item: ClusterRankingScore = None

    def with_item(self, item: ClusterRankingScore) -> GetClusterRankingScoreByUserIdResult:
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
    ) -> Optional[GetClusterRankingScoreByUserIdResult]:
        if data is None:
            return None
        return GetClusterRankingScoreByUserIdResult()\
            .with_item(ClusterRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteClusterRankingScoreByUserIdResult(core.Gs2Result):
    item: ClusterRankingScore = None

    def with_item(self, item: ClusterRankingScore) -> DeleteClusterRankingScoreByUserIdResult:
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
    ) -> Optional[DeleteClusterRankingScoreByUserIdResult]:
        if data is None:
            return None
        return DeleteClusterRankingScoreByUserIdResult()\
            .with_item(ClusterRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyClusterRankingScoreResult(core.Gs2Result):
    item: ClusterRankingScore = None

    def with_item(self, item: ClusterRankingScore) -> VerifyClusterRankingScoreResult:
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
    ) -> Optional[VerifyClusterRankingScoreResult]:
        if data is None:
            return None
        return VerifyClusterRankingScoreResult()\
            .with_item(ClusterRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyClusterRankingScoreByUserIdResult(core.Gs2Result):
    item: ClusterRankingScore = None

    def with_item(self, item: ClusterRankingScore) -> VerifyClusterRankingScoreByUserIdResult:
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
    ) -> Optional[VerifyClusterRankingScoreByUserIdResult]:
        if data is None:
            return None
        return VerifyClusterRankingScoreByUserIdResult()\
            .with_item(ClusterRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyClusterRankingScoreByStampTaskResult(core.Gs2Result):
    item: ClusterRankingScore = None
    new_context_stack: str = None

    def with_item(self, item: ClusterRankingScore) -> VerifyClusterRankingScoreByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyClusterRankingScoreByStampTaskResult:
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
    ) -> Optional[VerifyClusterRankingScoreByStampTaskResult]:
        if data is None:
            return None
        return VerifyClusterRankingScoreByStampTaskResult()\
            .with_item(ClusterRankingScore.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeClusterRankingReceivedRewardsResult(core.Gs2Result):
    items: List[ClusterRankingReceivedReward] = None
    next_page_token: str = None

    def with_items(self, items: List[ClusterRankingReceivedReward]) -> DescribeClusterRankingReceivedRewardsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeClusterRankingReceivedRewardsResult:
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
    ) -> Optional[DescribeClusterRankingReceivedRewardsResult]:
        if data is None:
            return None
        return DescribeClusterRankingReceivedRewardsResult()\
            .with_items(None if data.get('items') is None else [
                ClusterRankingReceivedReward.from_dict(data.get('items')[i])
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


class DescribeClusterRankingReceivedRewardsByUserIdResult(core.Gs2Result):
    items: List[ClusterRankingReceivedReward] = None
    next_page_token: str = None

    def with_items(self, items: List[ClusterRankingReceivedReward]) -> DescribeClusterRankingReceivedRewardsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeClusterRankingReceivedRewardsByUserIdResult:
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
    ) -> Optional[DescribeClusterRankingReceivedRewardsByUserIdResult]:
        if data is None:
            return None
        return DescribeClusterRankingReceivedRewardsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ClusterRankingReceivedReward.from_dict(data.get('items')[i])
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


class CreateClusterRankingReceivedRewardResult(core.Gs2Result):
    item: ClusterRankingReceivedReward = None

    def with_item(self, item: ClusterRankingReceivedReward) -> CreateClusterRankingReceivedRewardResult:
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
    ) -> Optional[CreateClusterRankingReceivedRewardResult]:
        if data is None:
            return None
        return CreateClusterRankingReceivedRewardResult()\
            .with_item(ClusterRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CreateClusterRankingReceivedRewardByUserIdResult(core.Gs2Result):
    item: ClusterRankingReceivedReward = None

    def with_item(self, item: ClusterRankingReceivedReward) -> CreateClusterRankingReceivedRewardByUserIdResult:
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
    ) -> Optional[CreateClusterRankingReceivedRewardByUserIdResult]:
        if data is None:
            return None
        return CreateClusterRankingReceivedRewardByUserIdResult()\
            .with_item(ClusterRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ReceiveClusterRankingReceivedRewardResult(core.Gs2Result):
    item: ClusterRankingModel = None
    acquire_actions: List[AcquireAction] = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: ClusterRankingModel) -> ReceiveClusterRankingReceivedRewardResult:
        self.item = item
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> ReceiveClusterRankingReceivedRewardResult:
        self.acquire_actions = acquire_actions
        return self

    def with_transaction_id(self, transaction_id: str) -> ReceiveClusterRankingReceivedRewardResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> ReceiveClusterRankingReceivedRewardResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> ReceiveClusterRankingReceivedRewardResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> ReceiveClusterRankingReceivedRewardResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> ReceiveClusterRankingReceivedRewardResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> ReceiveClusterRankingReceivedRewardResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> ReceiveClusterRankingReceivedRewardResult:
        self.transaction_result = transaction_result
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ReceiveClusterRankingReceivedRewardResult]:
        if data is None:
            return None
        return ReceiveClusterRankingReceivedRewardResult()\
            .with_item(ClusterRankingModel.from_dict(data.get('item')))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class ReceiveClusterRankingReceivedRewardByUserIdResult(core.Gs2Result):
    item: ClusterRankingModel = None
    acquire_actions: List[AcquireAction] = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: ClusterRankingModel) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.item = item
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.acquire_actions = acquire_actions
        return self

    def with_transaction_id(self, transaction_id: str) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        self.transaction_result = transaction_result
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ReceiveClusterRankingReceivedRewardByUserIdResult]:
        if data is None:
            return None
        return ReceiveClusterRankingReceivedRewardByUserIdResult()\
            .with_item(ClusterRankingModel.from_dict(data.get('item')))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class GetClusterRankingReceivedRewardResult(core.Gs2Result):
    item: ClusterRankingReceivedReward = None

    def with_item(self, item: ClusterRankingReceivedReward) -> GetClusterRankingReceivedRewardResult:
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
    ) -> Optional[GetClusterRankingReceivedRewardResult]:
        if data is None:
            return None
        return GetClusterRankingReceivedRewardResult()\
            .with_item(ClusterRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetClusterRankingReceivedRewardByUserIdResult(core.Gs2Result):
    item: ClusterRankingReceivedReward = None

    def with_item(self, item: ClusterRankingReceivedReward) -> GetClusterRankingReceivedRewardByUserIdResult:
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
    ) -> Optional[GetClusterRankingReceivedRewardByUserIdResult]:
        if data is None:
            return None
        return GetClusterRankingReceivedRewardByUserIdResult()\
            .with_item(ClusterRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteClusterRankingReceivedRewardByUserIdResult(core.Gs2Result):
    item: ClusterRankingReceivedReward = None

    def with_item(self, item: ClusterRankingReceivedReward) -> DeleteClusterRankingReceivedRewardByUserIdResult:
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
    ) -> Optional[DeleteClusterRankingReceivedRewardByUserIdResult]:
        if data is None:
            return None
        return DeleteClusterRankingReceivedRewardByUserIdResult()\
            .with_item(ClusterRankingReceivedReward.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CreateClusterRankingReceivedRewardByStampTaskResult(core.Gs2Result):
    item: ClusterRankingReceivedReward = None
    new_context_stack: str = None

    def with_item(self, item: ClusterRankingReceivedReward) -> CreateClusterRankingReceivedRewardByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> CreateClusterRankingReceivedRewardByStampTaskResult:
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
    ) -> Optional[CreateClusterRankingReceivedRewardByStampTaskResult]:
        if data is None:
            return None
        return CreateClusterRankingReceivedRewardByStampTaskResult()\
            .with_item(ClusterRankingReceivedReward.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeClusterRankingsResult(core.Gs2Result):
    items: List[ClusterRankingData] = None
    next_page_token: str = None

    def with_items(self, items: List[ClusterRankingData]) -> DescribeClusterRankingsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeClusterRankingsResult:
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
    ) -> Optional[DescribeClusterRankingsResult]:
        if data is None:
            return None
        return DescribeClusterRankingsResult()\
            .with_items(None if data.get('items') is None else [
                ClusterRankingData.from_dict(data.get('items')[i])
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


class DescribeClusterRankingsByUserIdResult(core.Gs2Result):
    items: List[ClusterRankingData] = None
    next_page_token: str = None

    def with_items(self, items: List[ClusterRankingData]) -> DescribeClusterRankingsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeClusterRankingsByUserIdResult:
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
    ) -> Optional[DescribeClusterRankingsByUserIdResult]:
        if data is None:
            return None
        return DescribeClusterRankingsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ClusterRankingData.from_dict(data.get('items')[i])
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


class GetClusterRankingResult(core.Gs2Result):
    item: ClusterRankingData = None

    def with_item(self, item: ClusterRankingData) -> GetClusterRankingResult:
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
    ) -> Optional[GetClusterRankingResult]:
        if data is None:
            return None
        return GetClusterRankingResult()\
            .with_item(ClusterRankingData.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetClusterRankingByUserIdResult(core.Gs2Result):
    item: ClusterRankingData = None

    def with_item(self, item: ClusterRankingData) -> GetClusterRankingByUserIdResult:
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
    ) -> Optional[GetClusterRankingByUserIdResult]:
        if data is None:
            return None
        return GetClusterRankingByUserIdResult()\
            .with_item(ClusterRankingData.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSubscribeRankingModelsResult(core.Gs2Result):
    items: List[SubscribeRankingModel] = None

    def with_items(self, items: List[SubscribeRankingModel]) -> DescribeSubscribeRankingModelsResult:
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
    ) -> Optional[DescribeSubscribeRankingModelsResult]:
        if data is None:
            return None
        return DescribeSubscribeRankingModelsResult()\
            .with_items(None if data.get('items') is None else [
                SubscribeRankingModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetSubscribeRankingModelResult(core.Gs2Result):
    item: SubscribeRankingModel = None

    def with_item(self, item: SubscribeRankingModel) -> GetSubscribeRankingModelResult:
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
    ) -> Optional[GetSubscribeRankingModelResult]:
        if data is None:
            return None
        return GetSubscribeRankingModelResult()\
            .with_item(SubscribeRankingModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSubscribeRankingModelMastersResult(core.Gs2Result):
    items: List[SubscribeRankingModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[SubscribeRankingModelMaster]) -> DescribeSubscribeRankingModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSubscribeRankingModelMastersResult:
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
    ) -> Optional[DescribeSubscribeRankingModelMastersResult]:
        if data is None:
            return None
        return DescribeSubscribeRankingModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                SubscribeRankingModelMaster.from_dict(data.get('items')[i])
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


class CreateSubscribeRankingModelMasterResult(core.Gs2Result):
    item: SubscribeRankingModelMaster = None

    def with_item(self, item: SubscribeRankingModelMaster) -> CreateSubscribeRankingModelMasterResult:
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
    ) -> Optional[CreateSubscribeRankingModelMasterResult]:
        if data is None:
            return None
        return CreateSubscribeRankingModelMasterResult()\
            .with_item(SubscribeRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSubscribeRankingModelMasterResult(core.Gs2Result):
    item: SubscribeRankingModelMaster = None

    def with_item(self, item: SubscribeRankingModelMaster) -> GetSubscribeRankingModelMasterResult:
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
    ) -> Optional[GetSubscribeRankingModelMasterResult]:
        if data is None:
            return None
        return GetSubscribeRankingModelMasterResult()\
            .with_item(SubscribeRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateSubscribeRankingModelMasterResult(core.Gs2Result):
    item: SubscribeRankingModelMaster = None

    def with_item(self, item: SubscribeRankingModelMaster) -> UpdateSubscribeRankingModelMasterResult:
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
    ) -> Optional[UpdateSubscribeRankingModelMasterResult]:
        if data is None:
            return None
        return UpdateSubscribeRankingModelMasterResult()\
            .with_item(SubscribeRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteSubscribeRankingModelMasterResult(core.Gs2Result):
    item: SubscribeRankingModelMaster = None

    def with_item(self, item: SubscribeRankingModelMaster) -> DeleteSubscribeRankingModelMasterResult:
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
    ) -> Optional[DeleteSubscribeRankingModelMasterResult]:
        if data is None:
            return None
        return DeleteSubscribeRankingModelMasterResult()\
            .with_item(SubscribeRankingModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSubscribesResult(core.Gs2Result):
    items: List[SubscribeUser] = None
    next_page_token: str = None

    def with_items(self, items: List[SubscribeUser]) -> DescribeSubscribesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSubscribesResult:
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
    ) -> Optional[DescribeSubscribesResult]:
        if data is None:
            return None
        return DescribeSubscribesResult()\
            .with_items(None if data.get('items') is None else [
                SubscribeUser.from_dict(data.get('items')[i])
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


class DescribeSubscribesByUserIdResult(core.Gs2Result):
    items: List[SubscribeUser] = None
    next_page_token: str = None

    def with_items(self, items: List[SubscribeUser]) -> DescribeSubscribesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSubscribesByUserIdResult:
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
    ) -> Optional[DescribeSubscribesByUserIdResult]:
        if data is None:
            return None
        return DescribeSubscribesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SubscribeUser.from_dict(data.get('items')[i])
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


class AddSubscribeResult(core.Gs2Result):
    item: SubscribeUser = None

    def with_item(self, item: SubscribeUser) -> AddSubscribeResult:
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
    ) -> Optional[AddSubscribeResult]:
        if data is None:
            return None
        return AddSubscribeResult()\
            .with_item(SubscribeUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AddSubscribeByUserIdResult(core.Gs2Result):
    item: SubscribeUser = None

    def with_item(self, item: SubscribeUser) -> AddSubscribeByUserIdResult:
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
    ) -> Optional[AddSubscribeByUserIdResult]:
        if data is None:
            return None
        return AddSubscribeByUserIdResult()\
            .with_item(SubscribeUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSubscribeRankingScoresResult(core.Gs2Result):
    items: List[SubscribeRankingScore] = None
    next_page_token: str = None

    def with_items(self, items: List[SubscribeRankingScore]) -> DescribeSubscribeRankingScoresResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSubscribeRankingScoresResult:
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
    ) -> Optional[DescribeSubscribeRankingScoresResult]:
        if data is None:
            return None
        return DescribeSubscribeRankingScoresResult()\
            .with_items(None if data.get('items') is None else [
                SubscribeRankingScore.from_dict(data.get('items')[i])
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


class DescribeSubscribeRankingScoresByUserIdResult(core.Gs2Result):
    items: List[SubscribeRankingScore] = None
    next_page_token: str = None

    def with_items(self, items: List[SubscribeRankingScore]) -> DescribeSubscribeRankingScoresByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSubscribeRankingScoresByUserIdResult:
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
    ) -> Optional[DescribeSubscribeRankingScoresByUserIdResult]:
        if data is None:
            return None
        return DescribeSubscribeRankingScoresByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SubscribeRankingScore.from_dict(data.get('items')[i])
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


class PutSubscribeRankingScoreResult(core.Gs2Result):
    item: SubscribeRankingScore = None

    def with_item(self, item: SubscribeRankingScore) -> PutSubscribeRankingScoreResult:
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
    ) -> Optional[PutSubscribeRankingScoreResult]:
        if data is None:
            return None
        return PutSubscribeRankingScoreResult()\
            .with_item(SubscribeRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PutSubscribeRankingScoreByUserIdResult(core.Gs2Result):
    item: SubscribeRankingScore = None

    def with_item(self, item: SubscribeRankingScore) -> PutSubscribeRankingScoreByUserIdResult:
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
    ) -> Optional[PutSubscribeRankingScoreByUserIdResult]:
        if data is None:
            return None
        return PutSubscribeRankingScoreByUserIdResult()\
            .with_item(SubscribeRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSubscribeRankingScoreResult(core.Gs2Result):
    item: SubscribeRankingScore = None

    def with_item(self, item: SubscribeRankingScore) -> GetSubscribeRankingScoreResult:
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
    ) -> Optional[GetSubscribeRankingScoreResult]:
        if data is None:
            return None
        return GetSubscribeRankingScoreResult()\
            .with_item(SubscribeRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSubscribeRankingScoreByUserIdResult(core.Gs2Result):
    item: SubscribeRankingScore = None

    def with_item(self, item: SubscribeRankingScore) -> GetSubscribeRankingScoreByUserIdResult:
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
    ) -> Optional[GetSubscribeRankingScoreByUserIdResult]:
        if data is None:
            return None
        return GetSubscribeRankingScoreByUserIdResult()\
            .with_item(SubscribeRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteSubscribeRankingScoreByUserIdResult(core.Gs2Result):
    item: SubscribeRankingScore = None

    def with_item(self, item: SubscribeRankingScore) -> DeleteSubscribeRankingScoreByUserIdResult:
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
    ) -> Optional[DeleteSubscribeRankingScoreByUserIdResult]:
        if data is None:
            return None
        return DeleteSubscribeRankingScoreByUserIdResult()\
            .with_item(SubscribeRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifySubscribeRankingScoreResult(core.Gs2Result):
    item: SubscribeRankingScore = None

    def with_item(self, item: SubscribeRankingScore) -> VerifySubscribeRankingScoreResult:
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
    ) -> Optional[VerifySubscribeRankingScoreResult]:
        if data is None:
            return None
        return VerifySubscribeRankingScoreResult()\
            .with_item(SubscribeRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifySubscribeRankingScoreByUserIdResult(core.Gs2Result):
    item: SubscribeRankingScore = None

    def with_item(self, item: SubscribeRankingScore) -> VerifySubscribeRankingScoreByUserIdResult:
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
    ) -> Optional[VerifySubscribeRankingScoreByUserIdResult]:
        if data is None:
            return None
        return VerifySubscribeRankingScoreByUserIdResult()\
            .with_item(SubscribeRankingScore.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifySubscribeRankingScoreByStampTaskResult(core.Gs2Result):
    item: SubscribeRankingScore = None
    new_context_stack: str = None

    def with_item(self, item: SubscribeRankingScore) -> VerifySubscribeRankingScoreByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifySubscribeRankingScoreByStampTaskResult:
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
    ) -> Optional[VerifySubscribeRankingScoreByStampTaskResult]:
        if data is None:
            return None
        return VerifySubscribeRankingScoreByStampTaskResult()\
            .with_item(SubscribeRankingScore.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeSubscribeRankingsResult(core.Gs2Result):
    items: List[SubscribeRankingData] = None
    next_page_token: str = None

    def with_items(self, items: List[SubscribeRankingData]) -> DescribeSubscribeRankingsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSubscribeRankingsResult:
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
    ) -> Optional[DescribeSubscribeRankingsResult]:
        if data is None:
            return None
        return DescribeSubscribeRankingsResult()\
            .with_items(None if data.get('items') is None else [
                SubscribeRankingData.from_dict(data.get('items')[i])
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


class DescribeSubscribeRankingsByUserIdResult(core.Gs2Result):
    items: List[SubscribeRankingData] = None
    next_page_token: str = None

    def with_items(self, items: List[SubscribeRankingData]) -> DescribeSubscribeRankingsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSubscribeRankingsByUserIdResult:
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
    ) -> Optional[DescribeSubscribeRankingsByUserIdResult]:
        if data is None:
            return None
        return DescribeSubscribeRankingsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SubscribeRankingData.from_dict(data.get('items')[i])
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


class GetSubscribeRankingResult(core.Gs2Result):
    item: SubscribeRankingData = None

    def with_item(self, item: SubscribeRankingData) -> GetSubscribeRankingResult:
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
    ) -> Optional[GetSubscribeRankingResult]:
        if data is None:
            return None
        return GetSubscribeRankingResult()\
            .with_item(SubscribeRankingData.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSubscribeRankingByUserIdResult(core.Gs2Result):
    item: SubscribeRankingData = None

    def with_item(self, item: SubscribeRankingData) -> GetSubscribeRankingByUserIdResult:
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
    ) -> Optional[GetSubscribeRankingByUserIdResult]:
        if data is None:
            return None
        return GetSubscribeRankingByUserIdResult()\
            .with_item(SubscribeRankingData.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentRankingMaster = None

    def with_item(self, item: CurrentRankingMaster) -> ExportMasterResult:
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
            .with_item(CurrentRankingMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentRankingMasterResult(core.Gs2Result):
    item: CurrentRankingMaster = None

    def with_item(self, item: CurrentRankingMaster) -> GetCurrentRankingMasterResult:
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
    ) -> Optional[GetCurrentRankingMasterResult]:
        if data is None:
            return None
        return GetCurrentRankingMasterResult()\
            .with_item(CurrentRankingMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentRankingMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentRankingMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentRankingMasterResult:
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
    ) -> Optional[PreUpdateCurrentRankingMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentRankingMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentRankingMasterResult(core.Gs2Result):
    item: CurrentRankingMaster = None

    def with_item(self, item: CurrentRankingMaster) -> UpdateCurrentRankingMasterResult:
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
    ) -> Optional[UpdateCurrentRankingMasterResult]:
        if data is None:
            return None
        return UpdateCurrentRankingMasterResult()\
            .with_item(CurrentRankingMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentRankingMasterFromGitHubResult(core.Gs2Result):
    item: CurrentRankingMaster = None

    def with_item(self, item: CurrentRankingMaster) -> UpdateCurrentRankingMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentRankingMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentRankingMasterFromGitHubResult()\
            .with_item(CurrentRankingMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSubscribeResult(core.Gs2Result):
    item: SubscribeUser = None

    def with_item(self, item: SubscribeUser) -> GetSubscribeResult:
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
    ) -> Optional[GetSubscribeResult]:
        if data is None:
            return None
        return GetSubscribeResult()\
            .with_item(SubscribeUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSubscribeByUserIdResult(core.Gs2Result):
    item: SubscribeUser = None

    def with_item(self, item: SubscribeUser) -> GetSubscribeByUserIdResult:
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
    ) -> Optional[GetSubscribeByUserIdResult]:
        if data is None:
            return None
        return GetSubscribeByUserIdResult()\
            .with_item(SubscribeUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteSubscribeResult(core.Gs2Result):
    item: SubscribeUser = None

    def with_item(self, item: SubscribeUser) -> DeleteSubscribeResult:
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
    ) -> Optional[DeleteSubscribeResult]:
        if data is None:
            return None
        return DeleteSubscribeResult()\
            .with_item(SubscribeUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteSubscribeByUserIdResult(core.Gs2Result):
    item: SubscribeUser = None

    def with_item(self, item: SubscribeUser) -> DeleteSubscribeByUserIdResult:
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
    ) -> Optional[DeleteSubscribeByUserIdResult]:
        if data is None:
            return None
        return DeleteSubscribeByUserIdResult()\
            .with_item(SubscribeUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }