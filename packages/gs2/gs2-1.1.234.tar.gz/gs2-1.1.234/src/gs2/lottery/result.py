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


class DescribeLotteryModelMastersResult(core.Gs2Result):
    items: List[LotteryModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[LotteryModelMaster]) -> DescribeLotteryModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeLotteryModelMastersResult:
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
    ) -> Optional[DescribeLotteryModelMastersResult]:
        if data is None:
            return None
        return DescribeLotteryModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                LotteryModelMaster.from_dict(data.get('items')[i])
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


class CreateLotteryModelMasterResult(core.Gs2Result):
    item: LotteryModelMaster = None

    def with_item(self, item: LotteryModelMaster) -> CreateLotteryModelMasterResult:
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
    ) -> Optional[CreateLotteryModelMasterResult]:
        if data is None:
            return None
        return CreateLotteryModelMasterResult()\
            .with_item(LotteryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetLotteryModelMasterResult(core.Gs2Result):
    item: LotteryModelMaster = None

    def with_item(self, item: LotteryModelMaster) -> GetLotteryModelMasterResult:
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
    ) -> Optional[GetLotteryModelMasterResult]:
        if data is None:
            return None
        return GetLotteryModelMasterResult()\
            .with_item(LotteryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateLotteryModelMasterResult(core.Gs2Result):
    item: LotteryModelMaster = None

    def with_item(self, item: LotteryModelMaster) -> UpdateLotteryModelMasterResult:
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
    ) -> Optional[UpdateLotteryModelMasterResult]:
        if data is None:
            return None
        return UpdateLotteryModelMasterResult()\
            .with_item(LotteryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteLotteryModelMasterResult(core.Gs2Result):
    item: LotteryModelMaster = None

    def with_item(self, item: LotteryModelMaster) -> DeleteLotteryModelMasterResult:
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
    ) -> Optional[DeleteLotteryModelMasterResult]:
        if data is None:
            return None
        return DeleteLotteryModelMasterResult()\
            .with_item(LotteryModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribePrizeTableMastersResult(core.Gs2Result):
    items: List[PrizeTableMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[PrizeTableMaster]) -> DescribePrizeTableMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribePrizeTableMastersResult:
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
    ) -> Optional[DescribePrizeTableMastersResult]:
        if data is None:
            return None
        return DescribePrizeTableMastersResult()\
            .with_items(None if data.get('items') is None else [
                PrizeTableMaster.from_dict(data.get('items')[i])
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


class CreatePrizeTableMasterResult(core.Gs2Result):
    item: PrizeTableMaster = None

    def with_item(self, item: PrizeTableMaster) -> CreatePrizeTableMasterResult:
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
    ) -> Optional[CreatePrizeTableMasterResult]:
        if data is None:
            return None
        return CreatePrizeTableMasterResult()\
            .with_item(PrizeTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetPrizeTableMasterResult(core.Gs2Result):
    item: PrizeTableMaster = None

    def with_item(self, item: PrizeTableMaster) -> GetPrizeTableMasterResult:
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
    ) -> Optional[GetPrizeTableMasterResult]:
        if data is None:
            return None
        return GetPrizeTableMasterResult()\
            .with_item(PrizeTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdatePrizeTableMasterResult(core.Gs2Result):
    item: PrizeTableMaster = None

    def with_item(self, item: PrizeTableMaster) -> UpdatePrizeTableMasterResult:
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
    ) -> Optional[UpdatePrizeTableMasterResult]:
        if data is None:
            return None
        return UpdatePrizeTableMasterResult()\
            .with_item(PrizeTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeletePrizeTableMasterResult(core.Gs2Result):
    item: PrizeTableMaster = None

    def with_item(self, item: PrizeTableMaster) -> DeletePrizeTableMasterResult:
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
    ) -> Optional[DeletePrizeTableMasterResult]:
        if data is None:
            return None
        return DeletePrizeTableMasterResult()\
            .with_item(PrizeTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeLotteryModelsResult(core.Gs2Result):
    items: List[LotteryModel] = None

    def with_items(self, items: List[LotteryModel]) -> DescribeLotteryModelsResult:
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
    ) -> Optional[DescribeLotteryModelsResult]:
        if data is None:
            return None
        return DescribeLotteryModelsResult()\
            .with_items(None if data.get('items') is None else [
                LotteryModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetLotteryModelResult(core.Gs2Result):
    item: LotteryModel = None

    def with_item(self, item: LotteryModel) -> GetLotteryModelResult:
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
    ) -> Optional[GetLotteryModelResult]:
        if data is None:
            return None
        return GetLotteryModelResult()\
            .with_item(LotteryModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribePrizeTablesResult(core.Gs2Result):
    items: List[PrizeTable] = None

    def with_items(self, items: List[PrizeTable]) -> DescribePrizeTablesResult:
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
    ) -> Optional[DescribePrizeTablesResult]:
        if data is None:
            return None
        return DescribePrizeTablesResult()\
            .with_items(None if data.get('items') is None else [
                PrizeTable.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetPrizeTableResult(core.Gs2Result):
    item: PrizeTable = None

    def with_item(self, item: PrizeTable) -> GetPrizeTableResult:
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
    ) -> Optional[GetPrizeTableResult]:
        if data is None:
            return None
        return GetPrizeTableResult()\
            .with_item(PrizeTable.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DrawByUserIdResult(core.Gs2Result):
    items: List[DrawnPrize] = None
    box_items: BoxItems = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_items(self, items: List[DrawnPrize]) -> DrawByUserIdResult:
        self.items = items
        return self

    def with_box_items(self, box_items: BoxItems) -> DrawByUserIdResult:
        self.box_items = box_items
        return self

    def with_transaction_id(self, transaction_id: str) -> DrawByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> DrawByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> DrawByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> DrawByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> DrawByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> DrawByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> DrawByUserIdResult:
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
    ) -> Optional[DrawByUserIdResult]:
        if data is None:
            return None
        return DrawByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                DrawnPrize.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_box_items(BoxItems.from_dict(data.get('boxItems')))\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "boxItems": self.box_items.to_dict() if self.box_items else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class PredictionResult(core.Gs2Result):
    items: List[DrawnPrize] = None

    def with_items(self, items: List[DrawnPrize]) -> PredictionResult:
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
    ) -> Optional[PredictionResult]:
        if data is None:
            return None
        return PredictionResult()\
            .with_items(None if data.get('items') is None else [
                DrawnPrize.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class PredictionByUserIdResult(core.Gs2Result):
    items: List[DrawnPrize] = None

    def with_items(self, items: List[DrawnPrize]) -> PredictionByUserIdResult:
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
    ) -> Optional[PredictionByUserIdResult]:
        if data is None:
            return None
        return PredictionByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                DrawnPrize.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class DrawWithRandomSeedByUserIdResult(core.Gs2Result):
    items: List[DrawnPrize] = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_items(self, items: List[DrawnPrize]) -> DrawWithRandomSeedByUserIdResult:
        self.items = items
        return self

    def with_transaction_id(self, transaction_id: str) -> DrawWithRandomSeedByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> DrawWithRandomSeedByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> DrawWithRandomSeedByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> DrawWithRandomSeedByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> DrawWithRandomSeedByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> DrawWithRandomSeedByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> DrawWithRandomSeedByUserIdResult:
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
    ) -> Optional[DrawWithRandomSeedByUserIdResult]:
        if data is None:
            return None
        return DrawWithRandomSeedByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                DrawnPrize.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
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
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class DrawByStampSheetResult(core.Gs2Result):
    items: List[DrawnPrize] = None
    box_items: BoxItems = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_items(self, items: List[DrawnPrize]) -> DrawByStampSheetResult:
        self.items = items
        return self

    def with_box_items(self, box_items: BoxItems) -> DrawByStampSheetResult:
        self.box_items = box_items
        return self

    def with_transaction_id(self, transaction_id: str) -> DrawByStampSheetResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> DrawByStampSheetResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> DrawByStampSheetResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> DrawByStampSheetResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> DrawByStampSheetResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> DrawByStampSheetResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> DrawByStampSheetResult:
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
    ) -> Optional[DrawByStampSheetResult]:
        if data is None:
            return None
        return DrawByStampSheetResult()\
            .with_items(None if data.get('items') is None else [
                DrawnPrize.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_box_items(BoxItems.from_dict(data.get('boxItems')))\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "boxItems": self.box_items.to_dict() if self.box_items else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class DescribeProbabilitiesResult(core.Gs2Result):
    items: List[Probability] = None

    def with_items(self, items: List[Probability]) -> DescribeProbabilitiesResult:
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
    ) -> Optional[DescribeProbabilitiesResult]:
        if data is None:
            return None
        return DescribeProbabilitiesResult()\
            .with_items(None if data.get('items') is None else [
                Probability.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class DescribeProbabilitiesByUserIdResult(core.Gs2Result):
    items: List[Probability] = None

    def with_items(self, items: List[Probability]) -> DescribeProbabilitiesByUserIdResult:
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
    ) -> Optional[DescribeProbabilitiesByUserIdResult]:
        if data is None:
            return None
        return DescribeProbabilitiesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Probability.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentLotteryMaster = None

    def with_item(self, item: CurrentLotteryMaster) -> ExportMasterResult:
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
            .with_item(CurrentLotteryMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentLotteryMasterResult(core.Gs2Result):
    item: CurrentLotteryMaster = None

    def with_item(self, item: CurrentLotteryMaster) -> GetCurrentLotteryMasterResult:
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
    ) -> Optional[GetCurrentLotteryMasterResult]:
        if data is None:
            return None
        return GetCurrentLotteryMasterResult()\
            .with_item(CurrentLotteryMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentLotteryMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentLotteryMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentLotteryMasterResult:
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
    ) -> Optional[PreUpdateCurrentLotteryMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentLotteryMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentLotteryMasterResult(core.Gs2Result):
    item: CurrentLotteryMaster = None

    def with_item(self, item: CurrentLotteryMaster) -> UpdateCurrentLotteryMasterResult:
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
    ) -> Optional[UpdateCurrentLotteryMasterResult]:
        if data is None:
            return None
        return UpdateCurrentLotteryMasterResult()\
            .with_item(CurrentLotteryMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentLotteryMasterFromGitHubResult(core.Gs2Result):
    item: CurrentLotteryMaster = None

    def with_item(self, item: CurrentLotteryMaster) -> UpdateCurrentLotteryMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentLotteryMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentLotteryMasterFromGitHubResult()\
            .with_item(CurrentLotteryMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribePrizeLimitsResult(core.Gs2Result):
    items: List[PrizeLimit] = None
    next_page_token: str = None

    def with_items(self, items: List[PrizeLimit]) -> DescribePrizeLimitsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribePrizeLimitsResult:
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
    ) -> Optional[DescribePrizeLimitsResult]:
        if data is None:
            return None
        return DescribePrizeLimitsResult()\
            .with_items(None if data.get('items') is None else [
                PrizeLimit.from_dict(data.get('items')[i])
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


class GetPrizeLimitResult(core.Gs2Result):
    item: PrizeLimit = None

    def with_item(self, item: PrizeLimit) -> GetPrizeLimitResult:
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
    ) -> Optional[GetPrizeLimitResult]:
        if data is None:
            return None
        return GetPrizeLimitResult()\
            .with_item(PrizeLimit.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ResetPrizeLimitResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ResetPrizeLimitResult]:
        if data is None:
            return None
        return ResetPrizeLimitResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class DescribeBoxesResult(core.Gs2Result):
    items: List[BoxItems] = None
    next_page_token: str = None

    def with_items(self, items: List[BoxItems]) -> DescribeBoxesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBoxesResult:
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
    ) -> Optional[DescribeBoxesResult]:
        if data is None:
            return None
        return DescribeBoxesResult()\
            .with_items(None if data.get('items') is None else [
                BoxItems.from_dict(data.get('items')[i])
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


class DescribeBoxesByUserIdResult(core.Gs2Result):
    items: List[BoxItems] = None
    next_page_token: str = None

    def with_items(self, items: List[BoxItems]) -> DescribeBoxesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBoxesByUserIdResult:
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
    ) -> Optional[DescribeBoxesByUserIdResult]:
        if data is None:
            return None
        return DescribeBoxesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                BoxItems.from_dict(data.get('items')[i])
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


class GetBoxResult(core.Gs2Result):
    item: BoxItems = None

    def with_item(self, item: BoxItems) -> GetBoxResult:
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
    ) -> Optional[GetBoxResult]:
        if data is None:
            return None
        return GetBoxResult()\
            .with_item(BoxItems.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetBoxByUserIdResult(core.Gs2Result):
    item: BoxItems = None

    def with_item(self, item: BoxItems) -> GetBoxByUserIdResult:
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
    ) -> Optional[GetBoxByUserIdResult]:
        if data is None:
            return None
        return GetBoxByUserIdResult()\
            .with_item(BoxItems.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ResetBoxResult(core.Gs2Result):
    item: BoxItems = None

    def with_item(self, item: BoxItems) -> ResetBoxResult:
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
    ) -> Optional[ResetBoxResult]:
        if data is None:
            return None
        return ResetBoxResult()\
            .with_item(BoxItems.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ResetBoxByUserIdResult(core.Gs2Result):
    item: BoxItems = None

    def with_item(self, item: BoxItems) -> ResetBoxByUserIdResult:
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
    ) -> Optional[ResetBoxByUserIdResult]:
        if data is None:
            return None
        return ResetBoxByUserIdResult()\
            .with_item(BoxItems.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ResetByStampSheetResult(core.Gs2Result):
    item: BoxItems = None

    def with_item(self, item: BoxItems) -> ResetByStampSheetResult:
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
    ) -> Optional[ResetByStampSheetResult]:
        if data is None:
            return None
        return ResetByStampSheetResult()\
            .with_item(BoxItems.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }