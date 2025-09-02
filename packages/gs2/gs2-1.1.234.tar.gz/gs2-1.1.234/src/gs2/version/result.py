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


class DescribeVersionModelMastersResult(core.Gs2Result):
    items: List[VersionModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[VersionModelMaster]) -> DescribeVersionModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeVersionModelMastersResult:
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
    ) -> Optional[DescribeVersionModelMastersResult]:
        if data is None:
            return None
        return DescribeVersionModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                VersionModelMaster.from_dict(data.get('items')[i])
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


class CreateVersionModelMasterResult(core.Gs2Result):
    item: VersionModelMaster = None

    def with_item(self, item: VersionModelMaster) -> CreateVersionModelMasterResult:
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
    ) -> Optional[CreateVersionModelMasterResult]:
        if data is None:
            return None
        return CreateVersionModelMasterResult()\
            .with_item(VersionModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetVersionModelMasterResult(core.Gs2Result):
    item: VersionModelMaster = None

    def with_item(self, item: VersionModelMaster) -> GetVersionModelMasterResult:
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
    ) -> Optional[GetVersionModelMasterResult]:
        if data is None:
            return None
        return GetVersionModelMasterResult()\
            .with_item(VersionModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateVersionModelMasterResult(core.Gs2Result):
    item: VersionModelMaster = None

    def with_item(self, item: VersionModelMaster) -> UpdateVersionModelMasterResult:
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
    ) -> Optional[UpdateVersionModelMasterResult]:
        if data is None:
            return None
        return UpdateVersionModelMasterResult()\
            .with_item(VersionModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteVersionModelMasterResult(core.Gs2Result):
    item: VersionModelMaster = None

    def with_item(self, item: VersionModelMaster) -> DeleteVersionModelMasterResult:
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
    ) -> Optional[DeleteVersionModelMasterResult]:
        if data is None:
            return None
        return DeleteVersionModelMasterResult()\
            .with_item(VersionModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeVersionModelsResult(core.Gs2Result):
    items: List[VersionModel] = None

    def with_items(self, items: List[VersionModel]) -> DescribeVersionModelsResult:
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
    ) -> Optional[DescribeVersionModelsResult]:
        if data is None:
            return None
        return DescribeVersionModelsResult()\
            .with_items(None if data.get('items') is None else [
                VersionModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetVersionModelResult(core.Gs2Result):
    item: VersionModel = None

    def with_item(self, item: VersionModel) -> GetVersionModelResult:
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
    ) -> Optional[GetVersionModelResult]:
        if data is None:
            return None
        return GetVersionModelResult()\
            .with_item(VersionModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeAcceptVersionsResult(core.Gs2Result):
    items: List[AcceptVersion] = None
    next_page_token: str = None

    def with_items(self, items: List[AcceptVersion]) -> DescribeAcceptVersionsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeAcceptVersionsResult:
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
    ) -> Optional[DescribeAcceptVersionsResult]:
        if data is None:
            return None
        return DescribeAcceptVersionsResult()\
            .with_items(None if data.get('items') is None else [
                AcceptVersion.from_dict(data.get('items')[i])
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


class DescribeAcceptVersionsByUserIdResult(core.Gs2Result):
    items: List[AcceptVersion] = None
    next_page_token: str = None

    def with_items(self, items: List[AcceptVersion]) -> DescribeAcceptVersionsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeAcceptVersionsByUserIdResult:
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
    ) -> Optional[DescribeAcceptVersionsByUserIdResult]:
        if data is None:
            return None
        return DescribeAcceptVersionsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                AcceptVersion.from_dict(data.get('items')[i])
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


class AcceptResult(core.Gs2Result):
    item: AcceptVersion = None

    def with_item(self, item: AcceptVersion) -> AcceptResult:
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
    ) -> Optional[AcceptResult]:
        if data is None:
            return None
        return AcceptResult()\
            .with_item(AcceptVersion.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AcceptByUserIdResult(core.Gs2Result):
    item: AcceptVersion = None

    def with_item(self, item: AcceptVersion) -> AcceptByUserIdResult:
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
    ) -> Optional[AcceptByUserIdResult]:
        if data is None:
            return None
        return AcceptByUserIdResult()\
            .with_item(AcceptVersion.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class RejectResult(core.Gs2Result):
    item: AcceptVersion = None

    def with_item(self, item: AcceptVersion) -> RejectResult:
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
    ) -> Optional[RejectResult]:
        if data is None:
            return None
        return RejectResult()\
            .with_item(AcceptVersion.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class RejectByUserIdResult(core.Gs2Result):
    item: AcceptVersion = None

    def with_item(self, item: AcceptVersion) -> RejectByUserIdResult:
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
    ) -> Optional[RejectByUserIdResult]:
        if data is None:
            return None
        return RejectByUserIdResult()\
            .with_item(AcceptVersion.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetAcceptVersionResult(core.Gs2Result):
    item: AcceptVersion = None

    def with_item(self, item: AcceptVersion) -> GetAcceptVersionResult:
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
    ) -> Optional[GetAcceptVersionResult]:
        if data is None:
            return None
        return GetAcceptVersionResult()\
            .with_item(AcceptVersion.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetAcceptVersionByUserIdResult(core.Gs2Result):
    item: AcceptVersion = None

    def with_item(self, item: AcceptVersion) -> GetAcceptVersionByUserIdResult:
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
    ) -> Optional[GetAcceptVersionByUserIdResult]:
        if data is None:
            return None
        return GetAcceptVersionByUserIdResult()\
            .with_item(AcceptVersion.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteAcceptVersionResult(core.Gs2Result):
    item: AcceptVersion = None

    def with_item(self, item: AcceptVersion) -> DeleteAcceptVersionResult:
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
    ) -> Optional[DeleteAcceptVersionResult]:
        if data is None:
            return None
        return DeleteAcceptVersionResult()\
            .with_item(AcceptVersion.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteAcceptVersionByUserIdResult(core.Gs2Result):
    item: AcceptVersion = None

    def with_item(self, item: AcceptVersion) -> DeleteAcceptVersionByUserIdResult:
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
    ) -> Optional[DeleteAcceptVersionByUserIdResult]:
        if data is None:
            return None
        return DeleteAcceptVersionByUserIdResult()\
            .with_item(AcceptVersion.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CheckVersionResult(core.Gs2Result):
    project_token: str = None
    warnings: List[Status] = None
    errors: List[Status] = None

    def with_project_token(self, project_token: str) -> CheckVersionResult:
        self.project_token = project_token
        return self

    def with_warnings(self, warnings: List[Status]) -> CheckVersionResult:
        self.warnings = warnings
        return self

    def with_errors(self, errors: List[Status]) -> CheckVersionResult:
        self.errors = errors
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckVersionResult]:
        if data is None:
            return None
        return CheckVersionResult()\
            .with_project_token(data.get('projectToken'))\
            .with_warnings(None if data.get('warnings') is None else [
                Status.from_dict(data.get('warnings')[i])
                for i in range(len(data.get('warnings')))
            ])\
            .with_errors(None if data.get('errors') is None else [
                Status.from_dict(data.get('errors')[i])
                for i in range(len(data.get('errors')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projectToken": self.project_token,
            "warnings": None if self.warnings is None else [
                self.warnings[i].to_dict() if self.warnings[i] else None
                for i in range(len(self.warnings))
            ],
            "errors": None if self.errors is None else [
                self.errors[i].to_dict() if self.errors[i] else None
                for i in range(len(self.errors))
            ],
        }


class CheckVersionByUserIdResult(core.Gs2Result):
    project_token: str = None
    warnings: List[Status] = None
    errors: List[Status] = None

    def with_project_token(self, project_token: str) -> CheckVersionByUserIdResult:
        self.project_token = project_token
        return self

    def with_warnings(self, warnings: List[Status]) -> CheckVersionByUserIdResult:
        self.warnings = warnings
        return self

    def with_errors(self, errors: List[Status]) -> CheckVersionByUserIdResult:
        self.errors = errors
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CheckVersionByUserIdResult]:
        if data is None:
            return None
        return CheckVersionByUserIdResult()\
            .with_project_token(data.get('projectToken'))\
            .with_warnings(None if data.get('warnings') is None else [
                Status.from_dict(data.get('warnings')[i])
                for i in range(len(data.get('warnings')))
            ])\
            .with_errors(None if data.get('errors') is None else [
                Status.from_dict(data.get('errors')[i])
                for i in range(len(data.get('errors')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "projectToken": self.project_token,
            "warnings": None if self.warnings is None else [
                self.warnings[i].to_dict() if self.warnings[i] else None
                for i in range(len(self.warnings))
            ],
            "errors": None if self.errors is None else [
                self.errors[i].to_dict() if self.errors[i] else None
                for i in range(len(self.errors))
            ],
        }


class CalculateSignatureResult(core.Gs2Result):
    body: str = None
    signature: str = None

    def with_body(self, body: str) -> CalculateSignatureResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> CalculateSignatureResult:
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
    ) -> Optional[CalculateSignatureResult]:
        if data is None:
            return None
        return CalculateSignatureResult()\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body": self.body,
            "signature": self.signature,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentVersionMaster = None

    def with_item(self, item: CurrentVersionMaster) -> ExportMasterResult:
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
            .with_item(CurrentVersionMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentVersionMasterResult(core.Gs2Result):
    item: CurrentVersionMaster = None

    def with_item(self, item: CurrentVersionMaster) -> GetCurrentVersionMasterResult:
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
    ) -> Optional[GetCurrentVersionMasterResult]:
        if data is None:
            return None
        return GetCurrentVersionMasterResult()\
            .with_item(CurrentVersionMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentVersionMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentVersionMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentVersionMasterResult:
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
    ) -> Optional[PreUpdateCurrentVersionMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentVersionMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentVersionMasterResult(core.Gs2Result):
    item: CurrentVersionMaster = None

    def with_item(self, item: CurrentVersionMaster) -> UpdateCurrentVersionMasterResult:
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
    ) -> Optional[UpdateCurrentVersionMasterResult]:
        if data is None:
            return None
        return UpdateCurrentVersionMasterResult()\
            .with_item(CurrentVersionMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentVersionMasterFromGitHubResult(core.Gs2Result):
    item: CurrentVersionMaster = None

    def with_item(self, item: CurrentVersionMaster) -> UpdateCurrentVersionMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentVersionMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentVersionMasterFromGitHubResult()\
            .with_item(CurrentVersionMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }