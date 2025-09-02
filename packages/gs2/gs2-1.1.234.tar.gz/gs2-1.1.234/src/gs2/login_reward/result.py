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


class DescribeBonusModelMastersResult(core.Gs2Result):
    items: List[BonusModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[BonusModelMaster]) -> DescribeBonusModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeBonusModelMastersResult:
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
    ) -> Optional[DescribeBonusModelMastersResult]:
        if data is None:
            return None
        return DescribeBonusModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                BonusModelMaster.from_dict(data.get('items')[i])
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


class CreateBonusModelMasterResult(core.Gs2Result):
    item: BonusModelMaster = None

    def with_item(self, item: BonusModelMaster) -> CreateBonusModelMasterResult:
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
    ) -> Optional[CreateBonusModelMasterResult]:
        if data is None:
            return None
        return CreateBonusModelMasterResult()\
            .with_item(BonusModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetBonusModelMasterResult(core.Gs2Result):
    item: BonusModelMaster = None

    def with_item(self, item: BonusModelMaster) -> GetBonusModelMasterResult:
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
    ) -> Optional[GetBonusModelMasterResult]:
        if data is None:
            return None
        return GetBonusModelMasterResult()\
            .with_item(BonusModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateBonusModelMasterResult(core.Gs2Result):
    item: BonusModelMaster = None

    def with_item(self, item: BonusModelMaster) -> UpdateBonusModelMasterResult:
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
    ) -> Optional[UpdateBonusModelMasterResult]:
        if data is None:
            return None
        return UpdateBonusModelMasterResult()\
            .with_item(BonusModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteBonusModelMasterResult(core.Gs2Result):
    item: BonusModelMaster = None

    def with_item(self, item: BonusModelMaster) -> DeleteBonusModelMasterResult:
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
    ) -> Optional[DeleteBonusModelMasterResult]:
        if data is None:
            return None
        return DeleteBonusModelMasterResult()\
            .with_item(BonusModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentBonusMaster = None

    def with_item(self, item: CurrentBonusMaster) -> ExportMasterResult:
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
            .with_item(CurrentBonusMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentBonusMasterResult(core.Gs2Result):
    item: CurrentBonusMaster = None

    def with_item(self, item: CurrentBonusMaster) -> GetCurrentBonusMasterResult:
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
    ) -> Optional[GetCurrentBonusMasterResult]:
        if data is None:
            return None
        return GetCurrentBonusMasterResult()\
            .with_item(CurrentBonusMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentBonusMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentBonusMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentBonusMasterResult:
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
    ) -> Optional[PreUpdateCurrentBonusMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentBonusMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentBonusMasterResult(core.Gs2Result):
    item: CurrentBonusMaster = None

    def with_item(self, item: CurrentBonusMaster) -> UpdateCurrentBonusMasterResult:
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
    ) -> Optional[UpdateCurrentBonusMasterResult]:
        if data is None:
            return None
        return UpdateCurrentBonusMasterResult()\
            .with_item(CurrentBonusMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentBonusMasterFromGitHubResult(core.Gs2Result):
    item: CurrentBonusMaster = None

    def with_item(self, item: CurrentBonusMaster) -> UpdateCurrentBonusMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentBonusMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentBonusMasterFromGitHubResult()\
            .with_item(CurrentBonusMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeBonusModelsResult(core.Gs2Result):
    items: List[BonusModel] = None

    def with_items(self, items: List[BonusModel]) -> DescribeBonusModelsResult:
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
    ) -> Optional[DescribeBonusModelsResult]:
        if data is None:
            return None
        return DescribeBonusModelsResult()\
            .with_items(None if data.get('items') is None else [
                BonusModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetBonusModelResult(core.Gs2Result):
    item: BonusModel = None

    def with_item(self, item: BonusModel) -> GetBonusModelResult:
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
    ) -> Optional[GetBonusModelResult]:
        if data is None:
            return None
        return GetBonusModelResult()\
            .with_item(BonusModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ReceiveResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: ReceiveStatus) -> ReceiveResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> ReceiveResult:
        self.bonus_model = bonus_model
        return self

    def with_transaction_id(self, transaction_id: str) -> ReceiveResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> ReceiveResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> ReceiveResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> ReceiveResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> ReceiveResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> ReceiveResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> ReceiveResult:
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
    ) -> Optional[ReceiveResult]:
        if data is None:
            return None
        return ReceiveResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))\
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
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class ReceiveByUserIdResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: ReceiveStatus) -> ReceiveByUserIdResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> ReceiveByUserIdResult:
        self.bonus_model = bonus_model
        return self

    def with_transaction_id(self, transaction_id: str) -> ReceiveByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> ReceiveByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> ReceiveByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> ReceiveByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> ReceiveByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> ReceiveByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> ReceiveByUserIdResult:
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
    ) -> Optional[ReceiveByUserIdResult]:
        if data is None:
            return None
        return ReceiveByUserIdResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))\
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
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class MissedReceiveResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: ReceiveStatus) -> MissedReceiveResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> MissedReceiveResult:
        self.bonus_model = bonus_model
        return self

    def with_transaction_id(self, transaction_id: str) -> MissedReceiveResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> MissedReceiveResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> MissedReceiveResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> MissedReceiveResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> MissedReceiveResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> MissedReceiveResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> MissedReceiveResult:
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
    ) -> Optional[MissedReceiveResult]:
        if data is None:
            return None
        return MissedReceiveResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))\
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
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class MissedReceiveByUserIdResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: ReceiveStatus) -> MissedReceiveByUserIdResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> MissedReceiveByUserIdResult:
        self.bonus_model = bonus_model
        return self

    def with_transaction_id(self, transaction_id: str) -> MissedReceiveByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> MissedReceiveByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> MissedReceiveByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> MissedReceiveByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> MissedReceiveByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> MissedReceiveByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> MissedReceiveByUserIdResult:
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
    ) -> Optional[MissedReceiveByUserIdResult]:
        if data is None:
            return None
        return MissedReceiveByUserIdResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))\
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
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class DescribeReceiveStatusesResult(core.Gs2Result):
    items: List[ReceiveStatus] = None
    next_page_token: str = None

    def with_items(self, items: List[ReceiveStatus]) -> DescribeReceiveStatusesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeReceiveStatusesResult:
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
    ) -> Optional[DescribeReceiveStatusesResult]:
        if data is None:
            return None
        return DescribeReceiveStatusesResult()\
            .with_items(None if data.get('items') is None else [
                ReceiveStatus.from_dict(data.get('items')[i])
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


class DescribeReceiveStatusesByUserIdResult(core.Gs2Result):
    items: List[ReceiveStatus] = None
    next_page_token: str = None

    def with_items(self, items: List[ReceiveStatus]) -> DescribeReceiveStatusesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeReceiveStatusesByUserIdResult:
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
    ) -> Optional[DescribeReceiveStatusesByUserIdResult]:
        if data is None:
            return None
        return DescribeReceiveStatusesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                ReceiveStatus.from_dict(data.get('items')[i])
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


class GetReceiveStatusResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None

    def with_item(self, item: ReceiveStatus) -> GetReceiveStatusResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> GetReceiveStatusResult:
        self.bonus_model = bonus_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetReceiveStatusResult]:
        if data is None:
            return None
        return GetReceiveStatusResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
        }


class GetReceiveStatusByUserIdResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None

    def with_item(self, item: ReceiveStatus) -> GetReceiveStatusByUserIdResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> GetReceiveStatusByUserIdResult:
        self.bonus_model = bonus_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetReceiveStatusByUserIdResult]:
        if data is None:
            return None
        return GetReceiveStatusByUserIdResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
        }


class DeleteReceiveStatusByUserIdResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None

    def with_item(self, item: ReceiveStatus) -> DeleteReceiveStatusByUserIdResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> DeleteReceiveStatusByUserIdResult:
        self.bonus_model = bonus_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteReceiveStatusByUserIdResult]:
        if data is None:
            return None
        return DeleteReceiveStatusByUserIdResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
        }


class DeleteReceiveStatusByStampSheetResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None

    def with_item(self, item: ReceiveStatus) -> DeleteReceiveStatusByStampSheetResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> DeleteReceiveStatusByStampSheetResult:
        self.bonus_model = bonus_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteReceiveStatusByStampSheetResult]:
        if data is None:
            return None
        return DeleteReceiveStatusByStampSheetResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
        }


class MarkReceivedResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None

    def with_item(self, item: ReceiveStatus) -> MarkReceivedResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> MarkReceivedResult:
        self.bonus_model = bonus_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[MarkReceivedResult]:
        if data is None:
            return None
        return MarkReceivedResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
        }


class MarkReceivedByUserIdResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None

    def with_item(self, item: ReceiveStatus) -> MarkReceivedByUserIdResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> MarkReceivedByUserIdResult:
        self.bonus_model = bonus_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[MarkReceivedByUserIdResult]:
        if data is None:
            return None
        return MarkReceivedByUserIdResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
        }


class UnmarkReceivedByUserIdResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None

    def with_item(self, item: ReceiveStatus) -> UnmarkReceivedByUserIdResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> UnmarkReceivedByUserIdResult:
        self.bonus_model = bonus_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UnmarkReceivedByUserIdResult]:
        if data is None:
            return None
        return UnmarkReceivedByUserIdResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
        }


class MarkReceivedByStampTaskResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None
    new_context_stack: str = None

    def with_item(self, item: ReceiveStatus) -> MarkReceivedByStampTaskResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> MarkReceivedByStampTaskResult:
        self.bonus_model = bonus_model
        return self

    def with_new_context_stack(self, new_context_stack: str) -> MarkReceivedByStampTaskResult:
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
    ) -> Optional[MarkReceivedByStampTaskResult]:
        if data is None:
            return None
        return MarkReceivedByStampTaskResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
            "newContextStack": self.new_context_stack,
        }


class UnmarkReceivedByStampSheetResult(core.Gs2Result):
    item: ReceiveStatus = None
    bonus_model: BonusModel = None

    def with_item(self, item: ReceiveStatus) -> UnmarkReceivedByStampSheetResult:
        self.item = item
        return self

    def with_bonus_model(self, bonus_model: BonusModel) -> UnmarkReceivedByStampSheetResult:
        self.bonus_model = bonus_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UnmarkReceivedByStampSheetResult]:
        if data is None:
            return None
        return UnmarkReceivedByStampSheetResult()\
            .with_item(ReceiveStatus.from_dict(data.get('item')))\
            .with_bonus_model(BonusModel.from_dict(data.get('bonusModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "bonusModel": self.bonus_model.to_dict() if self.bonus_model else None,
        }