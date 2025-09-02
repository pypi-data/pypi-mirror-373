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


class DescribeDataObjectsResult(core.Gs2Result):
    items: List[DataObject] = None
    next_page_token: str = None

    def with_items(self, items: List[DataObject]) -> DescribeDataObjectsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeDataObjectsResult:
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
    ) -> Optional[DescribeDataObjectsResult]:
        if data is None:
            return None
        return DescribeDataObjectsResult()\
            .with_items(None if data.get('items') is None else [
                DataObject.from_dict(data.get('items')[i])
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


class DescribeDataObjectsByUserIdResult(core.Gs2Result):
    items: List[DataObject] = None
    next_page_token: str = None

    def with_items(self, items: List[DataObject]) -> DescribeDataObjectsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeDataObjectsByUserIdResult:
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
    ) -> Optional[DescribeDataObjectsByUserIdResult]:
        if data is None:
            return None
        return DescribeDataObjectsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                DataObject.from_dict(data.get('items')[i])
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


class PrepareUploadResult(core.Gs2Result):
    item: DataObject = None
    upload_url: str = None

    def with_item(self, item: DataObject) -> PrepareUploadResult:
        self.item = item
        return self

    def with_upload_url(self, upload_url: str) -> PrepareUploadResult:
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
    ) -> Optional[PrepareUploadResult]:
        if data is None:
            return None
        return PrepareUploadResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "uploadUrl": self.upload_url,
        }


class PrepareUploadByUserIdResult(core.Gs2Result):
    item: DataObject = None
    upload_url: str = None

    def with_item(self, item: DataObject) -> PrepareUploadByUserIdResult:
        self.item = item
        return self

    def with_upload_url(self, upload_url: str) -> PrepareUploadByUserIdResult:
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
    ) -> Optional[PrepareUploadByUserIdResult]:
        if data is None:
            return None
        return PrepareUploadByUserIdResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "uploadUrl": self.upload_url,
        }


class UpdateDataObjectResult(core.Gs2Result):
    item: DataObject = None

    def with_item(self, item: DataObject) -> UpdateDataObjectResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateDataObjectResult]:
        if data is None:
            return None
        return UpdateDataObjectResult()\
            .with_item(DataObject.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateDataObjectByUserIdResult(core.Gs2Result):
    item: DataObject = None

    def with_item(self, item: DataObject) -> UpdateDataObjectByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateDataObjectByUserIdResult]:
        if data is None:
            return None
        return UpdateDataObjectByUserIdResult()\
            .with_item(DataObject.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PrepareReUploadResult(core.Gs2Result):
    item: DataObject = None
    upload_url: str = None

    def with_item(self, item: DataObject) -> PrepareReUploadResult:
        self.item = item
        return self

    def with_upload_url(self, upload_url: str) -> PrepareReUploadResult:
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
    ) -> Optional[PrepareReUploadResult]:
        if data is None:
            return None
        return PrepareReUploadResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "uploadUrl": self.upload_url,
        }


class PrepareReUploadByUserIdResult(core.Gs2Result):
    item: DataObject = None
    upload_url: str = None

    def with_item(self, item: DataObject) -> PrepareReUploadByUserIdResult:
        self.item = item
        return self

    def with_upload_url(self, upload_url: str) -> PrepareReUploadByUserIdResult:
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
    ) -> Optional[PrepareReUploadByUserIdResult]:
        if data is None:
            return None
        return PrepareReUploadByUserIdResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "uploadUrl": self.upload_url,
        }


class DoneUploadResult(core.Gs2Result):
    item: DataObject = None

    def with_item(self, item: DataObject) -> DoneUploadResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DoneUploadResult]:
        if data is None:
            return None
        return DoneUploadResult()\
            .with_item(DataObject.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DoneUploadByUserIdResult(core.Gs2Result):
    item: DataObject = None

    def with_item(self, item: DataObject) -> DoneUploadByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DoneUploadByUserIdResult]:
        if data is None:
            return None
        return DoneUploadByUserIdResult()\
            .with_item(DataObject.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteDataObjectResult(core.Gs2Result):
    item: DataObject = None

    def with_item(self, item: DataObject) -> DeleteDataObjectResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteDataObjectResult]:
        if data is None:
            return None
        return DeleteDataObjectResult()\
            .with_item(DataObject.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteDataObjectByUserIdResult(core.Gs2Result):
    item: DataObject = None

    def with_item(self, item: DataObject) -> DeleteDataObjectByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteDataObjectByUserIdResult]:
        if data is None:
            return None
        return DeleteDataObjectByUserIdResult()\
            .with_item(DataObject.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PrepareDownloadResult(core.Gs2Result):
    item: DataObject = None
    file_url: str = None
    content_length: int = None

    def with_item(self, item: DataObject) -> PrepareDownloadResult:
        self.item = item
        return self

    def with_file_url(self, file_url: str) -> PrepareDownloadResult:
        self.file_url = file_url
        return self

    def with_content_length(self, content_length: int) -> PrepareDownloadResult:
        self.content_length = content_length
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareDownloadResult]:
        if data is None:
            return None
        return PrepareDownloadResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_file_url(data.get('fileUrl'))\
            .with_content_length(data.get('contentLength'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "fileUrl": self.file_url,
            "contentLength": self.content_length,
        }


class PrepareDownloadByUserIdResult(core.Gs2Result):
    item: DataObject = None
    file_url: str = None
    content_length: int = None

    def with_item(self, item: DataObject) -> PrepareDownloadByUserIdResult:
        self.item = item
        return self

    def with_file_url(self, file_url: str) -> PrepareDownloadByUserIdResult:
        self.file_url = file_url
        return self

    def with_content_length(self, content_length: int) -> PrepareDownloadByUserIdResult:
        self.content_length = content_length
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareDownloadByUserIdResult]:
        if data is None:
            return None
        return PrepareDownloadByUserIdResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_file_url(data.get('fileUrl'))\
            .with_content_length(data.get('contentLength'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "fileUrl": self.file_url,
            "contentLength": self.content_length,
        }


class PrepareDownloadByGenerationResult(core.Gs2Result):
    item: DataObject = None
    file_url: str = None
    content_length: int = None

    def with_item(self, item: DataObject) -> PrepareDownloadByGenerationResult:
        self.item = item
        return self

    def with_file_url(self, file_url: str) -> PrepareDownloadByGenerationResult:
        self.file_url = file_url
        return self

    def with_content_length(self, content_length: int) -> PrepareDownloadByGenerationResult:
        self.content_length = content_length
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareDownloadByGenerationResult]:
        if data is None:
            return None
        return PrepareDownloadByGenerationResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_file_url(data.get('fileUrl'))\
            .with_content_length(data.get('contentLength'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "fileUrl": self.file_url,
            "contentLength": self.content_length,
        }


class PrepareDownloadByGenerationAndUserIdResult(core.Gs2Result):
    item: DataObject = None
    file_url: str = None
    content_length: int = None

    def with_item(self, item: DataObject) -> PrepareDownloadByGenerationAndUserIdResult:
        self.item = item
        return self

    def with_file_url(self, file_url: str) -> PrepareDownloadByGenerationAndUserIdResult:
        self.file_url = file_url
        return self

    def with_content_length(self, content_length: int) -> PrepareDownloadByGenerationAndUserIdResult:
        self.content_length = content_length
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareDownloadByGenerationAndUserIdResult]:
        if data is None:
            return None
        return PrepareDownloadByGenerationAndUserIdResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_file_url(data.get('fileUrl'))\
            .with_content_length(data.get('contentLength'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "fileUrl": self.file_url,
            "contentLength": self.content_length,
        }


class PrepareDownloadOwnDataResult(core.Gs2Result):
    item: DataObject = None
    file_url: str = None
    content_length: int = None

    def with_item(self, item: DataObject) -> PrepareDownloadOwnDataResult:
        self.item = item
        return self

    def with_file_url(self, file_url: str) -> PrepareDownloadOwnDataResult:
        self.file_url = file_url
        return self

    def with_content_length(self, content_length: int) -> PrepareDownloadOwnDataResult:
        self.content_length = content_length
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareDownloadOwnDataResult]:
        if data is None:
            return None
        return PrepareDownloadOwnDataResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_file_url(data.get('fileUrl'))\
            .with_content_length(data.get('contentLength'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "fileUrl": self.file_url,
            "contentLength": self.content_length,
        }


class PrepareDownloadByUserIdAndDataObjectNameResult(core.Gs2Result):
    item: DataObject = None
    file_url: str = None
    content_length: int = None

    def with_item(self, item: DataObject) -> PrepareDownloadByUserIdAndDataObjectNameResult:
        self.item = item
        return self

    def with_file_url(self, file_url: str) -> PrepareDownloadByUserIdAndDataObjectNameResult:
        self.file_url = file_url
        return self

    def with_content_length(self, content_length: int) -> PrepareDownloadByUserIdAndDataObjectNameResult:
        self.content_length = content_length
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareDownloadByUserIdAndDataObjectNameResult]:
        if data is None:
            return None
        return PrepareDownloadByUserIdAndDataObjectNameResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_file_url(data.get('fileUrl'))\
            .with_content_length(data.get('contentLength'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "fileUrl": self.file_url,
            "contentLength": self.content_length,
        }


class PrepareDownloadOwnDataByGenerationResult(core.Gs2Result):
    item: DataObject = None
    file_url: str = None
    content_length: int = None

    def with_item(self, item: DataObject) -> PrepareDownloadOwnDataByGenerationResult:
        self.item = item
        return self

    def with_file_url(self, file_url: str) -> PrepareDownloadOwnDataByGenerationResult:
        self.file_url = file_url
        return self

    def with_content_length(self, content_length: int) -> PrepareDownloadOwnDataByGenerationResult:
        self.content_length = content_length
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareDownloadOwnDataByGenerationResult]:
        if data is None:
            return None
        return PrepareDownloadOwnDataByGenerationResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_file_url(data.get('fileUrl'))\
            .with_content_length(data.get('contentLength'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "fileUrl": self.file_url,
            "contentLength": self.content_length,
        }


class PrepareDownloadByUserIdAndDataObjectNameAndGenerationResult(core.Gs2Result):
    item: DataObject = None
    file_url: str = None
    content_length: int = None

    def with_item(self, item: DataObject) -> PrepareDownloadByUserIdAndDataObjectNameAndGenerationResult:
        self.item = item
        return self

    def with_file_url(self, file_url: str) -> PrepareDownloadByUserIdAndDataObjectNameAndGenerationResult:
        self.file_url = file_url
        return self

    def with_content_length(self, content_length: int) -> PrepareDownloadByUserIdAndDataObjectNameAndGenerationResult:
        self.content_length = content_length
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareDownloadByUserIdAndDataObjectNameAndGenerationResult]:
        if data is None:
            return None
        return PrepareDownloadByUserIdAndDataObjectNameAndGenerationResult()\
            .with_item(DataObject.from_dict(data.get('item')))\
            .with_file_url(data.get('fileUrl'))\
            .with_content_length(data.get('contentLength'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "fileUrl": self.file_url,
            "contentLength": self.content_length,
        }


class RestoreDataObjectResult(core.Gs2Result):
    item: DataObject = None

    def with_item(self, item: DataObject) -> RestoreDataObjectResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RestoreDataObjectResult]:
        if data is None:
            return None
        return RestoreDataObjectResult()\
            .with_item(DataObject.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeDataObjectHistoriesResult(core.Gs2Result):
    items: List[DataObjectHistory] = None
    next_page_token: str = None

    def with_items(self, items: List[DataObjectHistory]) -> DescribeDataObjectHistoriesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeDataObjectHistoriesResult:
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
    ) -> Optional[DescribeDataObjectHistoriesResult]:
        if data is None:
            return None
        return DescribeDataObjectHistoriesResult()\
            .with_items(None if data.get('items') is None else [
                DataObjectHistory.from_dict(data.get('items')[i])
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


class DescribeDataObjectHistoriesByUserIdResult(core.Gs2Result):
    items: List[DataObjectHistory] = None
    next_page_token: str = None

    def with_items(self, items: List[DataObjectHistory]) -> DescribeDataObjectHistoriesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeDataObjectHistoriesByUserIdResult:
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
    ) -> Optional[DescribeDataObjectHistoriesByUserIdResult]:
        if data is None:
            return None
        return DescribeDataObjectHistoriesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                DataObjectHistory.from_dict(data.get('items')[i])
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


class GetDataObjectHistoryResult(core.Gs2Result):
    item: DataObjectHistory = None

    def with_item(self, item: DataObjectHistory) -> GetDataObjectHistoryResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetDataObjectHistoryResult]:
        if data is None:
            return None
        return GetDataObjectHistoryResult()\
            .with_item(DataObjectHistory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetDataObjectHistoryByUserIdResult(core.Gs2Result):
    item: DataObjectHistory = None

    def with_item(self, item: DataObjectHistory) -> GetDataObjectHistoryByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetDataObjectHistoryByUserIdResult]:
        if data is None:
            return None
        return GetDataObjectHistoryByUserIdResult()\
            .with_item(DataObjectHistory.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }