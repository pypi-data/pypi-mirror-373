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


class DescribeStaminaModelMastersResult(core.Gs2Result):
    items: List[StaminaModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[StaminaModelMaster]) -> DescribeStaminaModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeStaminaModelMastersResult:
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
    ) -> Optional[DescribeStaminaModelMastersResult]:
        if data is None:
            return None
        return DescribeStaminaModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                StaminaModelMaster.from_dict(data.get('items')[i])
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


class CreateStaminaModelMasterResult(core.Gs2Result):
    item: StaminaModelMaster = None

    def with_item(self, item: StaminaModelMaster) -> CreateStaminaModelMasterResult:
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
    ) -> Optional[CreateStaminaModelMasterResult]:
        if data is None:
            return None
        return CreateStaminaModelMasterResult()\
            .with_item(StaminaModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetStaminaModelMasterResult(core.Gs2Result):
    item: StaminaModelMaster = None

    def with_item(self, item: StaminaModelMaster) -> GetStaminaModelMasterResult:
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
    ) -> Optional[GetStaminaModelMasterResult]:
        if data is None:
            return None
        return GetStaminaModelMasterResult()\
            .with_item(StaminaModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateStaminaModelMasterResult(core.Gs2Result):
    item: StaminaModelMaster = None

    def with_item(self, item: StaminaModelMaster) -> UpdateStaminaModelMasterResult:
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
    ) -> Optional[UpdateStaminaModelMasterResult]:
        if data is None:
            return None
        return UpdateStaminaModelMasterResult()\
            .with_item(StaminaModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteStaminaModelMasterResult(core.Gs2Result):
    item: StaminaModelMaster = None

    def with_item(self, item: StaminaModelMaster) -> DeleteStaminaModelMasterResult:
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
    ) -> Optional[DeleteStaminaModelMasterResult]:
        if data is None:
            return None
        return DeleteStaminaModelMasterResult()\
            .with_item(StaminaModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeMaxStaminaTableMastersResult(core.Gs2Result):
    items: List[MaxStaminaTableMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[MaxStaminaTableMaster]) -> DescribeMaxStaminaTableMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeMaxStaminaTableMastersResult:
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
    ) -> Optional[DescribeMaxStaminaTableMastersResult]:
        if data is None:
            return None
        return DescribeMaxStaminaTableMastersResult()\
            .with_items(None if data.get('items') is None else [
                MaxStaminaTableMaster.from_dict(data.get('items')[i])
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


class CreateMaxStaminaTableMasterResult(core.Gs2Result):
    item: MaxStaminaTableMaster = None

    def with_item(self, item: MaxStaminaTableMaster) -> CreateMaxStaminaTableMasterResult:
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
    ) -> Optional[CreateMaxStaminaTableMasterResult]:
        if data is None:
            return None
        return CreateMaxStaminaTableMasterResult()\
            .with_item(MaxStaminaTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetMaxStaminaTableMasterResult(core.Gs2Result):
    item: MaxStaminaTableMaster = None

    def with_item(self, item: MaxStaminaTableMaster) -> GetMaxStaminaTableMasterResult:
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
    ) -> Optional[GetMaxStaminaTableMasterResult]:
        if data is None:
            return None
        return GetMaxStaminaTableMasterResult()\
            .with_item(MaxStaminaTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateMaxStaminaTableMasterResult(core.Gs2Result):
    item: MaxStaminaTableMaster = None

    def with_item(self, item: MaxStaminaTableMaster) -> UpdateMaxStaminaTableMasterResult:
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
    ) -> Optional[UpdateMaxStaminaTableMasterResult]:
        if data is None:
            return None
        return UpdateMaxStaminaTableMasterResult()\
            .with_item(MaxStaminaTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteMaxStaminaTableMasterResult(core.Gs2Result):
    item: MaxStaminaTableMaster = None

    def with_item(self, item: MaxStaminaTableMaster) -> DeleteMaxStaminaTableMasterResult:
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
    ) -> Optional[DeleteMaxStaminaTableMasterResult]:
        if data is None:
            return None
        return DeleteMaxStaminaTableMasterResult()\
            .with_item(MaxStaminaTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRecoverIntervalTableMastersResult(core.Gs2Result):
    items: List[RecoverIntervalTableMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[RecoverIntervalTableMaster]) -> DescribeRecoverIntervalTableMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRecoverIntervalTableMastersResult:
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
    ) -> Optional[DescribeRecoverIntervalTableMastersResult]:
        if data is None:
            return None
        return DescribeRecoverIntervalTableMastersResult()\
            .with_items(None if data.get('items') is None else [
                RecoverIntervalTableMaster.from_dict(data.get('items')[i])
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


class CreateRecoverIntervalTableMasterResult(core.Gs2Result):
    item: RecoverIntervalTableMaster = None

    def with_item(self, item: RecoverIntervalTableMaster) -> CreateRecoverIntervalTableMasterResult:
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
    ) -> Optional[CreateRecoverIntervalTableMasterResult]:
        if data is None:
            return None
        return CreateRecoverIntervalTableMasterResult()\
            .with_item(RecoverIntervalTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetRecoverIntervalTableMasterResult(core.Gs2Result):
    item: RecoverIntervalTableMaster = None

    def with_item(self, item: RecoverIntervalTableMaster) -> GetRecoverIntervalTableMasterResult:
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
    ) -> Optional[GetRecoverIntervalTableMasterResult]:
        if data is None:
            return None
        return GetRecoverIntervalTableMasterResult()\
            .with_item(RecoverIntervalTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateRecoverIntervalTableMasterResult(core.Gs2Result):
    item: RecoverIntervalTableMaster = None

    def with_item(self, item: RecoverIntervalTableMaster) -> UpdateRecoverIntervalTableMasterResult:
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
    ) -> Optional[UpdateRecoverIntervalTableMasterResult]:
        if data is None:
            return None
        return UpdateRecoverIntervalTableMasterResult()\
            .with_item(RecoverIntervalTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteRecoverIntervalTableMasterResult(core.Gs2Result):
    item: RecoverIntervalTableMaster = None

    def with_item(self, item: RecoverIntervalTableMaster) -> DeleteRecoverIntervalTableMasterResult:
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
    ) -> Optional[DeleteRecoverIntervalTableMasterResult]:
        if data is None:
            return None
        return DeleteRecoverIntervalTableMasterResult()\
            .with_item(RecoverIntervalTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeRecoverValueTableMastersResult(core.Gs2Result):
    items: List[RecoverValueTableMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[RecoverValueTableMaster]) -> DescribeRecoverValueTableMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeRecoverValueTableMastersResult:
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
    ) -> Optional[DescribeRecoverValueTableMastersResult]:
        if data is None:
            return None
        return DescribeRecoverValueTableMastersResult()\
            .with_items(None if data.get('items') is None else [
                RecoverValueTableMaster.from_dict(data.get('items')[i])
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


class CreateRecoverValueTableMasterResult(core.Gs2Result):
    item: RecoverValueTableMaster = None

    def with_item(self, item: RecoverValueTableMaster) -> CreateRecoverValueTableMasterResult:
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
    ) -> Optional[CreateRecoverValueTableMasterResult]:
        if data is None:
            return None
        return CreateRecoverValueTableMasterResult()\
            .with_item(RecoverValueTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetRecoverValueTableMasterResult(core.Gs2Result):
    item: RecoverValueTableMaster = None

    def with_item(self, item: RecoverValueTableMaster) -> GetRecoverValueTableMasterResult:
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
    ) -> Optional[GetRecoverValueTableMasterResult]:
        if data is None:
            return None
        return GetRecoverValueTableMasterResult()\
            .with_item(RecoverValueTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateRecoverValueTableMasterResult(core.Gs2Result):
    item: RecoverValueTableMaster = None

    def with_item(self, item: RecoverValueTableMaster) -> UpdateRecoverValueTableMasterResult:
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
    ) -> Optional[UpdateRecoverValueTableMasterResult]:
        if data is None:
            return None
        return UpdateRecoverValueTableMasterResult()\
            .with_item(RecoverValueTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteRecoverValueTableMasterResult(core.Gs2Result):
    item: RecoverValueTableMaster = None

    def with_item(self, item: RecoverValueTableMaster) -> DeleteRecoverValueTableMasterResult:
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
    ) -> Optional[DeleteRecoverValueTableMasterResult]:
        if data is None:
            return None
        return DeleteRecoverValueTableMasterResult()\
            .with_item(RecoverValueTableMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentStaminaMaster = None

    def with_item(self, item: CurrentStaminaMaster) -> ExportMasterResult:
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
            .with_item(CurrentStaminaMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentStaminaMasterResult(core.Gs2Result):
    item: CurrentStaminaMaster = None

    def with_item(self, item: CurrentStaminaMaster) -> GetCurrentStaminaMasterResult:
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
    ) -> Optional[GetCurrentStaminaMasterResult]:
        if data is None:
            return None
        return GetCurrentStaminaMasterResult()\
            .with_item(CurrentStaminaMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentStaminaMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentStaminaMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentStaminaMasterResult:
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
    ) -> Optional[PreUpdateCurrentStaminaMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentStaminaMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentStaminaMasterResult(core.Gs2Result):
    item: CurrentStaminaMaster = None

    def with_item(self, item: CurrentStaminaMaster) -> UpdateCurrentStaminaMasterResult:
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
    ) -> Optional[UpdateCurrentStaminaMasterResult]:
        if data is None:
            return None
        return UpdateCurrentStaminaMasterResult()\
            .with_item(CurrentStaminaMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentStaminaMasterFromGitHubResult(core.Gs2Result):
    item: CurrentStaminaMaster = None

    def with_item(self, item: CurrentStaminaMaster) -> UpdateCurrentStaminaMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentStaminaMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentStaminaMasterFromGitHubResult()\
            .with_item(CurrentStaminaMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeStaminaModelsResult(core.Gs2Result):
    items: List[StaminaModel] = None

    def with_items(self, items: List[StaminaModel]) -> DescribeStaminaModelsResult:
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
    ) -> Optional[DescribeStaminaModelsResult]:
        if data is None:
            return None
        return DescribeStaminaModelsResult()\
            .with_items(None if data.get('items') is None else [
                StaminaModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetStaminaModelResult(core.Gs2Result):
    item: StaminaModel = None

    def with_item(self, item: StaminaModel) -> GetStaminaModelResult:
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
    ) -> Optional[GetStaminaModelResult]:
        if data is None:
            return None
        return GetStaminaModelResult()\
            .with_item(StaminaModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeStaminasResult(core.Gs2Result):
    items: List[Stamina] = None
    next_page_token: str = None

    def with_items(self, items: List[Stamina]) -> DescribeStaminasResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeStaminasResult:
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
    ) -> Optional[DescribeStaminasResult]:
        if data is None:
            return None
        return DescribeStaminasResult()\
            .with_items(None if data.get('items') is None else [
                Stamina.from_dict(data.get('items')[i])
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


class DescribeStaminasByUserIdResult(core.Gs2Result):
    items: List[Stamina] = None
    next_page_token: str = None

    def with_items(self, items: List[Stamina]) -> DescribeStaminasByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeStaminasByUserIdResult:
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
    ) -> Optional[DescribeStaminasByUserIdResult]:
        if data is None:
            return None
        return DescribeStaminasByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Stamina.from_dict(data.get('items')[i])
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


class GetStaminaResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> GetStaminaResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> GetStaminaResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStaminaResult]:
        if data is None:
            return None
        return GetStaminaResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class GetStaminaByUserIdResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> GetStaminaByUserIdResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> GetStaminaByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStaminaByUserIdResult]:
        if data is None:
            return None
        return GetStaminaByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class UpdateStaminaByUserIdResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> UpdateStaminaByUserIdResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> UpdateStaminaByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateStaminaByUserIdResult]:
        if data is None:
            return None
        return UpdateStaminaByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class ConsumeStaminaResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> ConsumeStaminaResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> ConsumeStaminaResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeStaminaResult]:
        if data is None:
            return None
        return ConsumeStaminaResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class ConsumeStaminaByUserIdResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> ConsumeStaminaByUserIdResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> ConsumeStaminaByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeStaminaByUserIdResult]:
        if data is None:
            return None
        return ConsumeStaminaByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class ApplyStaminaResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> ApplyStaminaResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> ApplyStaminaResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ApplyStaminaResult]:
        if data is None:
            return None
        return ApplyStaminaResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class ApplyStaminaByUserIdResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> ApplyStaminaByUserIdResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> ApplyStaminaByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ApplyStaminaByUserIdResult]:
        if data is None:
            return None
        return ApplyStaminaByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class RecoverStaminaByUserIdResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None
    overflow_value: int = None

    def with_item(self, item: Stamina) -> RecoverStaminaByUserIdResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> RecoverStaminaByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def with_overflow_value(self, overflow_value: int) -> RecoverStaminaByUserIdResult:
        self.overflow_value = overflow_value
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RecoverStaminaByUserIdResult]:
        if data is None:
            return None
        return RecoverStaminaByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))\
            .with_overflow_value(data.get('overflowValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
            "overflowValue": self.overflow_value,
        }


class RaiseMaxValueByUserIdResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> RaiseMaxValueByUserIdResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> RaiseMaxValueByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RaiseMaxValueByUserIdResult]:
        if data is None:
            return None
        return RaiseMaxValueByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class DecreaseMaxValueResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> DecreaseMaxValueResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> DecreaseMaxValueResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecreaseMaxValueResult]:
        if data is None:
            return None
        return DecreaseMaxValueResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class DecreaseMaxValueByUserIdResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> DecreaseMaxValueByUserIdResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> DecreaseMaxValueByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecreaseMaxValueByUserIdResult]:
        if data is None:
            return None
        return DecreaseMaxValueByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class SetMaxValueByUserIdResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetMaxValueByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetMaxValueByUserIdResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetMaxValueByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetMaxValueByUserIdResult]:
        if data is None:
            return None
        return SetMaxValueByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class SetRecoverIntervalByUserIdResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetRecoverIntervalByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetRecoverIntervalByUserIdResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetRecoverIntervalByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetRecoverIntervalByUserIdResult]:
        if data is None:
            return None
        return SetRecoverIntervalByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class SetRecoverValueByUserIdResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetRecoverValueByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetRecoverValueByUserIdResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetRecoverValueByUserIdResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetRecoverValueByUserIdResult]:
        if data is None:
            return None
        return SetRecoverValueByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class SetMaxValueByStatusResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetMaxValueByStatusResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetMaxValueByStatusResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetMaxValueByStatusResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetMaxValueByStatusResult]:
        if data is None:
            return None
        return SetMaxValueByStatusResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class SetRecoverIntervalByStatusResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetRecoverIntervalByStatusResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetRecoverIntervalByStatusResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetRecoverIntervalByStatusResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetRecoverIntervalByStatusResult]:
        if data is None:
            return None
        return SetRecoverIntervalByStatusResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class SetRecoverValueByStatusResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetRecoverValueByStatusResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetRecoverValueByStatusResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetRecoverValueByStatusResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetRecoverValueByStatusResult]:
        if data is None:
            return None
        return SetRecoverValueByStatusResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class DeleteStaminaByUserIdResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> DeleteStaminaByUserIdResult:
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
    ) -> Optional[DeleteStaminaByUserIdResult]:
        if data is None:
            return None
        return DeleteStaminaByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaValueResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaValueResult:
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
    ) -> Optional[VerifyStaminaValueResult]:
        if data is None:
            return None
        return VerifyStaminaValueResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaValueByUserIdResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaValueByUserIdResult:
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
    ) -> Optional[VerifyStaminaValueByUserIdResult]:
        if data is None:
            return None
        return VerifyStaminaValueByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaMaxValueResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaMaxValueResult:
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
    ) -> Optional[VerifyStaminaMaxValueResult]:
        if data is None:
            return None
        return VerifyStaminaMaxValueResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaMaxValueByUserIdResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaMaxValueByUserIdResult:
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
    ) -> Optional[VerifyStaminaMaxValueByUserIdResult]:
        if data is None:
            return None
        return VerifyStaminaMaxValueByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaRecoverIntervalMinutesResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaRecoverIntervalMinutesResult:
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
    ) -> Optional[VerifyStaminaRecoverIntervalMinutesResult]:
        if data is None:
            return None
        return VerifyStaminaRecoverIntervalMinutesResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaRecoverIntervalMinutesByUserIdResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaRecoverIntervalMinutesByUserIdResult:
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
    ) -> Optional[VerifyStaminaRecoverIntervalMinutesByUserIdResult]:
        if data is None:
            return None
        return VerifyStaminaRecoverIntervalMinutesByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaRecoverValueResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaRecoverValueResult:
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
    ) -> Optional[VerifyStaminaRecoverValueResult]:
        if data is None:
            return None
        return VerifyStaminaRecoverValueResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaRecoverValueByUserIdResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaRecoverValueByUserIdResult:
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
    ) -> Optional[VerifyStaminaRecoverValueByUserIdResult]:
        if data is None:
            return None
        return VerifyStaminaRecoverValueByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaOverflowValueResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaOverflowValueResult:
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
    ) -> Optional[VerifyStaminaOverflowValueResult]:
        if data is None:
            return None
        return VerifyStaminaOverflowValueResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyStaminaOverflowValueByUserIdResult(core.Gs2Result):
    item: Stamina = None

    def with_item(self, item: Stamina) -> VerifyStaminaOverflowValueByUserIdResult:
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
    ) -> Optional[VerifyStaminaOverflowValueByUserIdResult]:
        if data is None:
            return None
        return VerifyStaminaOverflowValueByUserIdResult()\
            .with_item(Stamina.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class RecoverStaminaByStampSheetResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None
    overflow_value: int = None

    def with_item(self, item: Stamina) -> RecoverStaminaByStampSheetResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> RecoverStaminaByStampSheetResult:
        self.stamina_model = stamina_model
        return self

    def with_overflow_value(self, overflow_value: int) -> RecoverStaminaByStampSheetResult:
        self.overflow_value = overflow_value
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RecoverStaminaByStampSheetResult]:
        if data is None:
            return None
        return RecoverStaminaByStampSheetResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))\
            .with_overflow_value(data.get('overflowValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
            "overflowValue": self.overflow_value,
        }


class RaiseMaxValueByStampSheetResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> RaiseMaxValueByStampSheetResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> RaiseMaxValueByStampSheetResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RaiseMaxValueByStampSheetResult]:
        if data is None:
            return None
        return RaiseMaxValueByStampSheetResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class DecreaseMaxValueByStampTaskResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None
    new_context_stack: str = None

    def with_item(self, item: Stamina) -> DecreaseMaxValueByStampTaskResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> DecreaseMaxValueByStampTaskResult:
        self.stamina_model = stamina_model
        return self

    def with_new_context_stack(self, new_context_stack: str) -> DecreaseMaxValueByStampTaskResult:
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
    ) -> Optional[DecreaseMaxValueByStampTaskResult]:
        if data is None:
            return None
        return DecreaseMaxValueByStampTaskResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
            "newContextStack": self.new_context_stack,
        }


class SetMaxValueByStampSheetResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetMaxValueByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetMaxValueByStampSheetResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetMaxValueByStampSheetResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetMaxValueByStampSheetResult]:
        if data is None:
            return None
        return SetMaxValueByStampSheetResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class SetRecoverIntervalByStampSheetResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetRecoverIntervalByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetRecoverIntervalByStampSheetResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetRecoverIntervalByStampSheetResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetRecoverIntervalByStampSheetResult]:
        if data is None:
            return None
        return SetRecoverIntervalByStampSheetResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class SetRecoverValueByStampSheetResult(core.Gs2Result):
    item: Stamina = None
    old: Stamina = None
    stamina_model: StaminaModel = None

    def with_item(self, item: Stamina) -> SetRecoverValueByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: Stamina) -> SetRecoverValueByStampSheetResult:
        self.old = old
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> SetRecoverValueByStampSheetResult:
        self.stamina_model = stamina_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetRecoverValueByStampSheetResult]:
        if data is None:
            return None
        return SetRecoverValueByStampSheetResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_old(Stamina.from_dict(data.get('old')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
        }


class ConsumeStaminaByStampTaskResult(core.Gs2Result):
    item: Stamina = None
    stamina_model: StaminaModel = None
    new_context_stack: str = None

    def with_item(self, item: Stamina) -> ConsumeStaminaByStampTaskResult:
        self.item = item
        return self

    def with_stamina_model(self, stamina_model: StaminaModel) -> ConsumeStaminaByStampTaskResult:
        self.stamina_model = stamina_model
        return self

    def with_new_context_stack(self, new_context_stack: str) -> ConsumeStaminaByStampTaskResult:
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
    ) -> Optional[ConsumeStaminaByStampTaskResult]:
        if data is None:
            return None
        return ConsumeStaminaByStampTaskResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_stamina_model(StaminaModel.from_dict(data.get('staminaModel')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "staminaModel": self.stamina_model.to_dict() if self.stamina_model else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyStaminaValueByStampTaskResult(core.Gs2Result):
    item: Stamina = None
    new_context_stack: str = None

    def with_item(self, item: Stamina) -> VerifyStaminaValueByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyStaminaValueByStampTaskResult:
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
    ) -> Optional[VerifyStaminaValueByStampTaskResult]:
        if data is None:
            return None
        return VerifyStaminaValueByStampTaskResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyStaminaMaxValueByStampTaskResult(core.Gs2Result):
    item: Stamina = None
    new_context_stack: str = None

    def with_item(self, item: Stamina) -> VerifyStaminaMaxValueByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyStaminaMaxValueByStampTaskResult:
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
    ) -> Optional[VerifyStaminaMaxValueByStampTaskResult]:
        if data is None:
            return None
        return VerifyStaminaMaxValueByStampTaskResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyStaminaRecoverIntervalMinutesByStampTaskResult(core.Gs2Result):
    item: Stamina = None
    new_context_stack: str = None

    def with_item(self, item: Stamina) -> VerifyStaminaRecoverIntervalMinutesByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyStaminaRecoverIntervalMinutesByStampTaskResult:
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
    ) -> Optional[VerifyStaminaRecoverIntervalMinutesByStampTaskResult]:
        if data is None:
            return None
        return VerifyStaminaRecoverIntervalMinutesByStampTaskResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyStaminaRecoverValueByStampTaskResult(core.Gs2Result):
    item: Stamina = None
    new_context_stack: str = None

    def with_item(self, item: Stamina) -> VerifyStaminaRecoverValueByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyStaminaRecoverValueByStampTaskResult:
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
    ) -> Optional[VerifyStaminaRecoverValueByStampTaskResult]:
        if data is None:
            return None
        return VerifyStaminaRecoverValueByStampTaskResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyStaminaOverflowValueByStampTaskResult(core.Gs2Result):
    item: Stamina = None
    new_context_stack: str = None

    def with_item(self, item: Stamina) -> VerifyStaminaOverflowValueByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyStaminaOverflowValueByStampTaskResult:
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
    ) -> Optional[VerifyStaminaOverflowValueByStampTaskResult]:
        if data is None:
            return None
        return VerifyStaminaOverflowValueByStampTaskResult()\
            .with_item(Stamina.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }