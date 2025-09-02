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


class DescribeProgressesResult(core.Gs2Result):
    items: List[Progress] = None
    next_page_token: str = None

    def with_items(self, items: List[Progress]) -> DescribeProgressesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeProgressesResult:
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
    ) -> Optional[DescribeProgressesResult]:
        if data is None:
            return None
        return DescribeProgressesResult()\
            .with_items(None if data.get('items') is None else [
                Progress.from_dict(data.get('items')[i])
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


class GetProgressResult(core.Gs2Result):
    item: Progress = None

    def with_item(self, item: Progress) -> GetProgressResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetProgressResult]:
        if data is None:
            return None
        return GetProgressResult()\
            .with_item(Progress.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeOutputsResult(core.Gs2Result):
    items: List[Output] = None
    next_page_token: str = None

    def with_items(self, items: List[Output]) -> DescribeOutputsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeOutputsResult:
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
    ) -> Optional[DescribeOutputsResult]:
        if data is None:
            return None
        return DescribeOutputsResult()\
            .with_items(None if data.get('items') is None else [
                Output.from_dict(data.get('items')[i])
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


class GetOutputResult(core.Gs2Result):
    item: Output = None

    def with_item(self, item: Output) -> GetOutputResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetOutputResult]:
        if data is None:
            return None
        return GetOutputResult()\
            .with_item(Output.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PrepareUpdateCurrentNewsMasterResult(core.Gs2Result):
    upload_token: str = None
    template_upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PrepareUpdateCurrentNewsMasterResult:
        self.upload_token = upload_token
        return self

    def with_template_upload_url(self, template_upload_url: str) -> PrepareUpdateCurrentNewsMasterResult:
        self.template_upload_url = template_upload_url
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrepareUpdateCurrentNewsMasterResult]:
        if data is None:
            return None
        return PrepareUpdateCurrentNewsMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_template_upload_url(data.get('templateUploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "templateUploadUrl": self.template_upload_url,
        }


class UpdateCurrentNewsMasterResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentNewsMasterResult]:
        if data is None:
            return None
        return UpdateCurrentNewsMasterResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class PrepareUpdateCurrentNewsMasterFromGitHubResult(core.Gs2Result):
    upload_token: str = None

    def with_upload_token(self, upload_token: str) -> PrepareUpdateCurrentNewsMasterFromGitHubResult:
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
    ) -> Optional[PrepareUpdateCurrentNewsMasterFromGitHubResult]:
        if data is None:
            return None
        return PrepareUpdateCurrentNewsMasterFromGitHubResult()\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
        }


class DescribeNewsResult(core.Gs2Result):
    items: List[News] = None
    content_hash: str = None
    template_hash: str = None

    def with_items(self, items: List[News]) -> DescribeNewsResult:
        self.items = items
        return self

    def with_content_hash(self, content_hash: str) -> DescribeNewsResult:
        self.content_hash = content_hash
        return self

    def with_template_hash(self, template_hash: str) -> DescribeNewsResult:
        self.template_hash = template_hash
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeNewsResult]:
        if data is None:
            return None
        return DescribeNewsResult()\
            .with_items(None if data.get('items') is None else [
                News.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_content_hash(data.get('contentHash'))\
            .with_template_hash(data.get('templateHash'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "contentHash": self.content_hash,
            "templateHash": self.template_hash,
        }


class DescribeNewsByUserIdResult(core.Gs2Result):
    items: List[News] = None
    content_hash: str = None
    template_hash: str = None

    def with_items(self, items: List[News]) -> DescribeNewsByUserIdResult:
        self.items = items
        return self

    def with_content_hash(self, content_hash: str) -> DescribeNewsByUserIdResult:
        self.content_hash = content_hash
        return self

    def with_template_hash(self, template_hash: str) -> DescribeNewsByUserIdResult:
        self.template_hash = template_hash
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeNewsByUserIdResult]:
        if data is None:
            return None
        return DescribeNewsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                News.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_content_hash(data.get('contentHash'))\
            .with_template_hash(data.get('templateHash'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "contentHash": self.content_hash,
            "templateHash": self.template_hash,
        }


class WantGrantResult(core.Gs2Result):
    items: List[SetCookieRequestEntry] = None
    browser_url: str = None
    zip_url: str = None

    def with_items(self, items: List[SetCookieRequestEntry]) -> WantGrantResult:
        self.items = items
        return self

    def with_browser_url(self, browser_url: str) -> WantGrantResult:
        self.browser_url = browser_url
        return self

    def with_zip_url(self, zip_url: str) -> WantGrantResult:
        self.zip_url = zip_url
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WantGrantResult]:
        if data is None:
            return None
        return WantGrantResult()\
            .with_items(None if data.get('items') is None else [
                SetCookieRequestEntry.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_browser_url(data.get('browserUrl'))\
            .with_zip_url(data.get('zipUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "browserUrl": self.browser_url,
            "zipUrl": self.zip_url,
        }


class WantGrantByUserIdResult(core.Gs2Result):
    items: List[SetCookieRequestEntry] = None
    browser_url: str = None
    zip_url: str = None

    def with_items(self, items: List[SetCookieRequestEntry]) -> WantGrantByUserIdResult:
        self.items = items
        return self

    def with_browser_url(self, browser_url: str) -> WantGrantByUserIdResult:
        self.browser_url = browser_url
        return self

    def with_zip_url(self, zip_url: str) -> WantGrantByUserIdResult:
        self.zip_url = zip_url
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WantGrantByUserIdResult]:
        if data is None:
            return None
        return WantGrantByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SetCookieRequestEntry.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_browser_url(data.get('browserUrl'))\
            .with_zip_url(data.get('zipUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "browserUrl": self.browser_url,
            "zipUrl": self.zip_url,
        }