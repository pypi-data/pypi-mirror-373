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


class DescribeGuildModelMastersResult(core.Gs2Result):
    items: List[GuildModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[GuildModelMaster]) -> DescribeGuildModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGuildModelMastersResult:
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
    ) -> Optional[DescribeGuildModelMastersResult]:
        if data is None:
            return None
        return DescribeGuildModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                GuildModelMaster.from_dict(data.get('items')[i])
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


class CreateGuildModelMasterResult(core.Gs2Result):
    item: GuildModelMaster = None

    def with_item(self, item: GuildModelMaster) -> CreateGuildModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGuildModelMasterResult]:
        if data is None:
            return None
        return CreateGuildModelMasterResult()\
            .with_item(GuildModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGuildModelMasterResult(core.Gs2Result):
    item: GuildModelMaster = None

    def with_item(self, item: GuildModelMaster) -> GetGuildModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGuildModelMasterResult]:
        if data is None:
            return None
        return GetGuildModelMasterResult()\
            .with_item(GuildModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateGuildModelMasterResult(core.Gs2Result):
    item: GuildModelMaster = None

    def with_item(self, item: GuildModelMaster) -> UpdateGuildModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGuildModelMasterResult]:
        if data is None:
            return None
        return UpdateGuildModelMasterResult()\
            .with_item(GuildModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteGuildModelMasterResult(core.Gs2Result):
    item: GuildModelMaster = None

    def with_item(self, item: GuildModelMaster) -> DeleteGuildModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGuildModelMasterResult]:
        if data is None:
            return None
        return DeleteGuildModelMasterResult()\
            .with_item(GuildModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeGuildModelsResult(core.Gs2Result):
    items: List[GuildModel] = None

    def with_items(self, items: List[GuildModel]) -> DescribeGuildModelsResult:
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
    ) -> Optional[DescribeGuildModelsResult]:
        if data is None:
            return None
        return DescribeGuildModelsResult()\
            .with_items(None if data.get('items') is None else [
                GuildModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetGuildModelResult(core.Gs2Result):
    item: GuildModel = None

    def with_item(self, item: GuildModel) -> GetGuildModelResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGuildModelResult]:
        if data is None:
            return None
        return GetGuildModelResult()\
            .with_item(GuildModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SearchGuildsResult(core.Gs2Result):
    items: List[Guild] = None
    next_page_token: str = None

    def with_items(self, items: List[Guild]) -> SearchGuildsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> SearchGuildsResult:
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
    ) -> Optional[SearchGuildsResult]:
        if data is None:
            return None
        return SearchGuildsResult()\
            .with_items(None if data.get('items') is None else [
                Guild.from_dict(data.get('items')[i])
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


class SearchGuildsByUserIdResult(core.Gs2Result):
    items: List[Guild] = None
    next_page_token: str = None

    def with_items(self, items: List[Guild]) -> SearchGuildsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> SearchGuildsByUserIdResult:
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
    ) -> Optional[SearchGuildsByUserIdResult]:
        if data is None:
            return None
        return SearchGuildsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Guild.from_dict(data.get('items')[i])
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


class CreateGuildResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> CreateGuildResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGuildResult]:
        if data is None:
            return None
        return CreateGuildResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CreateGuildByUserIdResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> CreateGuildByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGuildByUserIdResult]:
        if data is None:
            return None
        return CreateGuildByUserIdResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGuildResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> GetGuildResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGuildResult]:
        if data is None:
            return None
        return GetGuildResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGuildByUserIdResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> GetGuildByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGuildByUserIdResult]:
        if data is None:
            return None
        return GetGuildByUserIdResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateGuildResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> UpdateGuildResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGuildResult]:
        if data is None:
            return None
        return UpdateGuildResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateGuildByGuildNameResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> UpdateGuildByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGuildByGuildNameResult]:
        if data is None:
            return None
        return UpdateGuildByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteMemberResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> DeleteMemberResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMemberResult]:
        if data is None:
            return None
        return DeleteMemberResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteMemberByGuildNameResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> DeleteMemberByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMemberByGuildNameResult]:
        if data is None:
            return None
        return DeleteMemberByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateMemberRoleResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> UpdateMemberRoleResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMemberRoleResult]:
        if data is None:
            return None
        return UpdateMemberRoleResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateMemberRoleByGuildNameResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> UpdateMemberRoleByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMemberRoleByGuildNameResult]:
        if data is None:
            return None
        return UpdateMemberRoleByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class BatchUpdateMemberRoleResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> BatchUpdateMemberRoleResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BatchUpdateMemberRoleResult]:
        if data is None:
            return None
        return BatchUpdateMemberRoleResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class BatchUpdateMemberRoleByGuildNameResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> BatchUpdateMemberRoleByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BatchUpdateMemberRoleByGuildNameResult]:
        if data is None:
            return None
        return BatchUpdateMemberRoleByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteGuildResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> DeleteGuildResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGuildResult]:
        if data is None:
            return None
        return DeleteGuildResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteGuildByGuildNameResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> DeleteGuildByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGuildByGuildNameResult]:
        if data is None:
            return None
        return DeleteGuildByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class IncreaseMaximumCurrentMaximumMemberCountByGuildNameResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> IncreaseMaximumCurrentMaximumMemberCountByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[IncreaseMaximumCurrentMaximumMemberCountByGuildNameResult]:
        if data is None:
            return None
        return IncreaseMaximumCurrentMaximumMemberCountByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DecreaseMaximumCurrentMaximumMemberCountResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> DecreaseMaximumCurrentMaximumMemberCountResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecreaseMaximumCurrentMaximumMemberCountResult]:
        if data is None:
            return None
        return DecreaseMaximumCurrentMaximumMemberCountResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DecreaseMaximumCurrentMaximumMemberCountByGuildNameResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> DecreaseMaximumCurrentMaximumMemberCountByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecreaseMaximumCurrentMaximumMemberCountByGuildNameResult]:
        if data is None:
            return None
        return DecreaseMaximumCurrentMaximumMemberCountByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyCurrentMaximumMemberCountResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> VerifyCurrentMaximumMemberCountResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyCurrentMaximumMemberCountResult]:
        if data is None:
            return None
        return VerifyCurrentMaximumMemberCountResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyCurrentMaximumMemberCountByGuildNameResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> VerifyCurrentMaximumMemberCountByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyCurrentMaximumMemberCountByGuildNameResult]:
        if data is None:
            return None
        return VerifyCurrentMaximumMemberCountByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyIncludeMemberResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> VerifyIncludeMemberResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyIncludeMemberResult]:
        if data is None:
            return None
        return VerifyIncludeMemberResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyIncludeMemberByUserIdResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> VerifyIncludeMemberByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyIncludeMemberByUserIdResult]:
        if data is None:
            return None
        return VerifyIncludeMemberByUserIdResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SetMaximumCurrentMaximumMemberCountByGuildNameResult(core.Gs2Result):
    item: Guild = None
    old: Guild = None

    def with_item(self, item: Guild) -> SetMaximumCurrentMaximumMemberCountByGuildNameResult:
        self.item = item
        return self

    def with_old(self, old: Guild) -> SetMaximumCurrentMaximumMemberCountByGuildNameResult:
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
    ) -> Optional[SetMaximumCurrentMaximumMemberCountByGuildNameResult]:
        if data is None:
            return None
        return SetMaximumCurrentMaximumMemberCountByGuildNameResult()\
            .with_item(Guild.from_dict(data.get('item')))\
            .with_old(Guild.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class AssumeResult(core.Gs2Result):
    token: str = None
    user_id: str = None
    expire: int = None

    def with_token(self, token: str) -> AssumeResult:
        self.token = token
        return self

    def with_user_id(self, user_id: str) -> AssumeResult:
        self.user_id = user_id
        return self

    def with_expire(self, expire: int) -> AssumeResult:
        self.expire = expire
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AssumeResult]:
        if data is None:
            return None
        return AssumeResult()\
            .with_token(data.get('token'))\
            .with_user_id(data.get('userId'))\
            .with_expire(data.get('expire'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "userId": self.user_id,
            "expire": self.expire,
        }


class AssumeByUserIdResult(core.Gs2Result):
    token: str = None
    user_id: str = None
    expire: int = None

    def with_token(self, token: str) -> AssumeByUserIdResult:
        self.token = token
        return self

    def with_user_id(self, user_id: str) -> AssumeByUserIdResult:
        self.user_id = user_id
        return self

    def with_expire(self, expire: int) -> AssumeByUserIdResult:
        self.expire = expire
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AssumeByUserIdResult]:
        if data is None:
            return None
        return AssumeByUserIdResult()\
            .with_token(data.get('token'))\
            .with_user_id(data.get('userId'))\
            .with_expire(data.get('expire'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "userId": self.user_id,
            "expire": self.expire,
        }


class IncreaseMaximumCurrentMaximumMemberCountByStampSheetResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> IncreaseMaximumCurrentMaximumMemberCountByStampSheetResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[IncreaseMaximumCurrentMaximumMemberCountByStampSheetResult]:
        if data is None:
            return None
        return IncreaseMaximumCurrentMaximumMemberCountByStampSheetResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult(core.Gs2Result):
    item: Guild = None
    new_context_stack: str = None

    def with_item(self, item: Guild) -> DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult:
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
    ) -> Optional[DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult]:
        if data is None:
            return None
        return DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult()\
            .with_item(Guild.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class SetMaximumCurrentMaximumMemberCountByStampSheetResult(core.Gs2Result):
    item: Guild = None
    old: Guild = None

    def with_item(self, item: Guild) -> SetMaximumCurrentMaximumMemberCountByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: Guild) -> SetMaximumCurrentMaximumMemberCountByStampSheetResult:
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
    ) -> Optional[SetMaximumCurrentMaximumMemberCountByStampSheetResult]:
        if data is None:
            return None
        return SetMaximumCurrentMaximumMemberCountByStampSheetResult()\
            .with_item(Guild.from_dict(data.get('item')))\
            .with_old(Guild.from_dict(data.get('old')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
        }


class VerifyCurrentMaximumMemberCountByStampTaskResult(core.Gs2Result):
    item: Guild = None
    new_context_stack: str = None

    def with_item(self, item: Guild) -> VerifyCurrentMaximumMemberCountByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyCurrentMaximumMemberCountByStampTaskResult:
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
    ) -> Optional[VerifyCurrentMaximumMemberCountByStampTaskResult]:
        if data is None:
            return None
        return VerifyCurrentMaximumMemberCountByStampTaskResult()\
            .with_item(Guild.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyIncludeMemberByStampTaskResult(core.Gs2Result):
    item: Guild = None
    new_context_stack: str = None

    def with_item(self, item: Guild) -> VerifyIncludeMemberByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyIncludeMemberByStampTaskResult:
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
    ) -> Optional[VerifyIncludeMemberByStampTaskResult]:
        if data is None:
            return None
        return VerifyIncludeMemberByStampTaskResult()\
            .with_item(Guild.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeJoinedGuildsResult(core.Gs2Result):
    items: List[JoinedGuild] = None
    next_page_token: str = None

    def with_items(self, items: List[JoinedGuild]) -> DescribeJoinedGuildsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeJoinedGuildsResult:
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
    ) -> Optional[DescribeJoinedGuildsResult]:
        if data is None:
            return None
        return DescribeJoinedGuildsResult()\
            .with_items(None if data.get('items') is None else [
                JoinedGuild.from_dict(data.get('items')[i])
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


class DescribeJoinedGuildsByUserIdResult(core.Gs2Result):
    items: List[JoinedGuild] = None
    next_page_token: str = None

    def with_items(self, items: List[JoinedGuild]) -> DescribeJoinedGuildsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeJoinedGuildsByUserIdResult:
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
    ) -> Optional[DescribeJoinedGuildsByUserIdResult]:
        if data is None:
            return None
        return DescribeJoinedGuildsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                JoinedGuild.from_dict(data.get('items')[i])
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


class GetJoinedGuildResult(core.Gs2Result):
    item: JoinedGuild = None

    def with_item(self, item: JoinedGuild) -> GetJoinedGuildResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetJoinedGuildResult]:
        if data is None:
            return None
        return GetJoinedGuildResult()\
            .with_item(JoinedGuild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetJoinedGuildByUserIdResult(core.Gs2Result):
    item: JoinedGuild = None

    def with_item(self, item: JoinedGuild) -> GetJoinedGuildByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetJoinedGuildByUserIdResult]:
        if data is None:
            return None
        return GetJoinedGuildByUserIdResult()\
            .with_item(JoinedGuild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateMemberMetadataResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> UpdateMemberMetadataResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMemberMetadataResult]:
        if data is None:
            return None
        return UpdateMemberMetadataResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateMemberMetadataByUserIdResult(core.Gs2Result):
    item: Guild = None

    def with_item(self, item: Guild) -> UpdateMemberMetadataByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMemberMetadataByUserIdResult]:
        if data is None:
            return None
        return UpdateMemberMetadataByUserIdResult()\
            .with_item(Guild.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class WithdrawalResult(core.Gs2Result):
    item: JoinedGuild = None
    guild: Guild = None

    def with_item(self, item: JoinedGuild) -> WithdrawalResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> WithdrawalResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WithdrawalResult]:
        if data is None:
            return None
        return WithdrawalResult()\
            .with_item(JoinedGuild.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class WithdrawalByUserIdResult(core.Gs2Result):
    item: JoinedGuild = None
    guild: Guild = None

    def with_item(self, item: JoinedGuild) -> WithdrawalByUserIdResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> WithdrawalByUserIdResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WithdrawalByUserIdResult]:
        if data is None:
            return None
        return WithdrawalByUserIdResult()\
            .with_item(JoinedGuild.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class GetLastGuildMasterActivityResult(core.Gs2Result):
    item: LastGuildMasterActivity = None
    guild: Guild = None

    def with_item(self, item: LastGuildMasterActivity) -> GetLastGuildMasterActivityResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> GetLastGuildMasterActivityResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetLastGuildMasterActivityResult]:
        if data is None:
            return None
        return GetLastGuildMasterActivityResult()\
            .with_item(LastGuildMasterActivity.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class GetLastGuildMasterActivityByGuildNameResult(core.Gs2Result):
    item: LastGuildMasterActivity = None
    guild: Guild = None

    def with_item(self, item: LastGuildMasterActivity) -> GetLastGuildMasterActivityByGuildNameResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> GetLastGuildMasterActivityByGuildNameResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetLastGuildMasterActivityByGuildNameResult]:
        if data is None:
            return None
        return GetLastGuildMasterActivityByGuildNameResult()\
            .with_item(LastGuildMasterActivity.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class PromoteSeniorMemberResult(core.Gs2Result):
    item: LastGuildMasterActivity = None
    guild: Guild = None

    def with_item(self, item: LastGuildMasterActivity) -> PromoteSeniorMemberResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> PromoteSeniorMemberResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PromoteSeniorMemberResult]:
        if data is None:
            return None
        return PromoteSeniorMemberResult()\
            .with_item(LastGuildMasterActivity.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class PromoteSeniorMemberByGuildNameResult(core.Gs2Result):
    item: LastGuildMasterActivity = None
    guild: Guild = None

    def with_item(self, item: LastGuildMasterActivity) -> PromoteSeniorMemberByGuildNameResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> PromoteSeniorMemberByGuildNameResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PromoteSeniorMemberByGuildNameResult]:
        if data is None:
            return None
        return PromoteSeniorMemberByGuildNameResult()\
            .with_item(LastGuildMasterActivity.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentGuildMaster = None

    def with_item(self, item: CurrentGuildMaster) -> ExportMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
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
            .with_item(CurrentGuildMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentGuildMasterResult(core.Gs2Result):
    item: CurrentGuildMaster = None

    def with_item(self, item: CurrentGuildMaster) -> GetCurrentGuildMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCurrentGuildMasterResult]:
        if data is None:
            return None
        return GetCurrentGuildMasterResult()\
            .with_item(CurrentGuildMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentGuildMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentGuildMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentGuildMasterResult:
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
    ) -> Optional[PreUpdateCurrentGuildMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentGuildMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentGuildMasterResult(core.Gs2Result):
    item: CurrentGuildMaster = None

    def with_item(self, item: CurrentGuildMaster) -> UpdateCurrentGuildMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentGuildMasterResult]:
        if data is None:
            return None
        return UpdateCurrentGuildMasterResult()\
            .with_item(CurrentGuildMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentGuildMasterFromGitHubResult(core.Gs2Result):
    item: CurrentGuildMaster = None

    def with_item(self, item: CurrentGuildMaster) -> UpdateCurrentGuildMasterFromGitHubResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentGuildMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentGuildMasterFromGitHubResult()\
            .with_item(CurrentGuildMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeReceiveRequestsResult(core.Gs2Result):
    items: List[ReceiveMemberRequest] = None
    next_page_token: str = None

    def with_items(self, items: List[ReceiveMemberRequest]) -> DescribeReceiveRequestsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeReceiveRequestsResult:
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
    ) -> Optional[DescribeReceiveRequestsResult]:
        if data is None:
            return None
        return DescribeReceiveRequestsResult()\
            .with_items(None if data.get('items') is None else [
                ReceiveMemberRequest.from_dict(data.get('items')[i])
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


class DescribeReceiveRequestsByGuildNameResult(core.Gs2Result):
    items: List[ReceiveMemberRequest] = None
    next_page_token: str = None

    def with_items(self, items: List[ReceiveMemberRequest]) -> DescribeReceiveRequestsByGuildNameResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeReceiveRequestsByGuildNameResult:
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
    ) -> Optional[DescribeReceiveRequestsByGuildNameResult]:
        if data is None:
            return None
        return DescribeReceiveRequestsByGuildNameResult()\
            .with_items(None if data.get('items') is None else [
                ReceiveMemberRequest.from_dict(data.get('items')[i])
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


class GetReceiveRequestResult(core.Gs2Result):
    item: ReceiveMemberRequest = None

    def with_item(self, item: ReceiveMemberRequest) -> GetReceiveRequestResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetReceiveRequestResult]:
        if data is None:
            return None
        return GetReceiveRequestResult()\
            .with_item(ReceiveMemberRequest.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetReceiveRequestByGuildNameResult(core.Gs2Result):
    item: ReceiveMemberRequest = None

    def with_item(self, item: ReceiveMemberRequest) -> GetReceiveRequestByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetReceiveRequestByGuildNameResult]:
        if data is None:
            return None
        return GetReceiveRequestByGuildNameResult()\
            .with_item(ReceiveMemberRequest.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AcceptRequestResult(core.Gs2Result):
    item: ReceiveMemberRequest = None
    guild: Guild = None

    def with_item(self, item: ReceiveMemberRequest) -> AcceptRequestResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> AcceptRequestResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcceptRequestResult]:
        if data is None:
            return None
        return AcceptRequestResult()\
            .with_item(ReceiveMemberRequest.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class AcceptRequestByGuildNameResult(core.Gs2Result):
    item: ReceiveMemberRequest = None
    guild: Guild = None

    def with_item(self, item: ReceiveMemberRequest) -> AcceptRequestByGuildNameResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> AcceptRequestByGuildNameResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcceptRequestByGuildNameResult]:
        if data is None:
            return None
        return AcceptRequestByGuildNameResult()\
            .with_item(ReceiveMemberRequest.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class RejectRequestResult(core.Gs2Result):
    item: ReceiveMemberRequest = None

    def with_item(self, item: ReceiveMemberRequest) -> RejectRequestResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RejectRequestResult]:
        if data is None:
            return None
        return RejectRequestResult()\
            .with_item(ReceiveMemberRequest.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class RejectRequestByGuildNameResult(core.Gs2Result):
    item: ReceiveMemberRequest = None

    def with_item(self, item: ReceiveMemberRequest) -> RejectRequestByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RejectRequestByGuildNameResult]:
        if data is None:
            return None
        return RejectRequestByGuildNameResult()\
            .with_item(ReceiveMemberRequest.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSendRequestsResult(core.Gs2Result):
    items: List[SendMemberRequest] = None
    next_page_token: str = None

    def with_items(self, items: List[SendMemberRequest]) -> DescribeSendRequestsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSendRequestsResult:
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
    ) -> Optional[DescribeSendRequestsResult]:
        if data is None:
            return None
        return DescribeSendRequestsResult()\
            .with_items(None if data.get('items') is None else [
                SendMemberRequest.from_dict(data.get('items')[i])
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


class DescribeSendRequestsByUserIdResult(core.Gs2Result):
    items: List[SendMemberRequest] = None
    next_page_token: str = None

    def with_items(self, items: List[SendMemberRequest]) -> DescribeSendRequestsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSendRequestsByUserIdResult:
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
    ) -> Optional[DescribeSendRequestsByUserIdResult]:
        if data is None:
            return None
        return DescribeSendRequestsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                SendMemberRequest.from_dict(data.get('items')[i])
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


class GetSendRequestResult(core.Gs2Result):
    item: SendMemberRequest = None

    def with_item(self, item: SendMemberRequest) -> GetSendRequestResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSendRequestResult]:
        if data is None:
            return None
        return GetSendRequestResult()\
            .with_item(SendMemberRequest.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSendRequestByUserIdResult(core.Gs2Result):
    item: SendMemberRequest = None

    def with_item(self, item: SendMemberRequest) -> GetSendRequestByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetSendRequestByUserIdResult]:
        if data is None:
            return None
        return GetSendRequestByUserIdResult()\
            .with_item(SendMemberRequest.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SendRequestResult(core.Gs2Result):
    item: Guild = None
    send_member_request: SendMemberRequest = None

    def with_item(self, item: Guild) -> SendRequestResult:
        self.item = item
        return self

    def with_send_member_request(self, send_member_request: SendMemberRequest) -> SendRequestResult:
        self.send_member_request = send_member_request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SendRequestResult]:
        if data is None:
            return None
        return SendRequestResult()\
            .with_item(Guild.from_dict(data.get('item')))\
            .with_send_member_request(SendMemberRequest.from_dict(data.get('sendMemberRequest')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "sendMemberRequest": self.send_member_request.to_dict() if self.send_member_request else None,
        }


class SendRequestByUserIdResult(core.Gs2Result):
    item: Guild = None
    send_member_request: SendMemberRequest = None

    def with_item(self, item: Guild) -> SendRequestByUserIdResult:
        self.item = item
        return self

    def with_send_member_request(self, send_member_request: SendMemberRequest) -> SendRequestByUserIdResult:
        self.send_member_request = send_member_request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SendRequestByUserIdResult]:
        if data is None:
            return None
        return SendRequestByUserIdResult()\
            .with_item(Guild.from_dict(data.get('item')))\
            .with_send_member_request(SendMemberRequest.from_dict(data.get('sendMemberRequest')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "sendMemberRequest": self.send_member_request.to_dict() if self.send_member_request else None,
        }


class DeleteRequestResult(core.Gs2Result):
    item: SendMemberRequest = None

    def with_item(self, item: SendMemberRequest) -> DeleteRequestResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRequestResult]:
        if data is None:
            return None
        return DeleteRequestResult()\
            .with_item(SendMemberRequest.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteRequestByUserIdResult(core.Gs2Result):
    item: SendMemberRequest = None

    def with_item(self, item: SendMemberRequest) -> DeleteRequestByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRequestByUserIdResult]:
        if data is None:
            return None
        return DeleteRequestByUserIdResult()\
            .with_item(SendMemberRequest.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeIgnoreUsersResult(core.Gs2Result):
    items: List[IgnoreUser] = None
    next_page_token: str = None

    def with_items(self, items: List[IgnoreUser]) -> DescribeIgnoreUsersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeIgnoreUsersResult:
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
    ) -> Optional[DescribeIgnoreUsersResult]:
        if data is None:
            return None
        return DescribeIgnoreUsersResult()\
            .with_items(None if data.get('items') is None else [
                IgnoreUser.from_dict(data.get('items')[i])
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


class DescribeIgnoreUsersByGuildNameResult(core.Gs2Result):
    items: List[IgnoreUser] = None
    next_page_token: str = None

    def with_items(self, items: List[IgnoreUser]) -> DescribeIgnoreUsersByGuildNameResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeIgnoreUsersByGuildNameResult:
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
    ) -> Optional[DescribeIgnoreUsersByGuildNameResult]:
        if data is None:
            return None
        return DescribeIgnoreUsersByGuildNameResult()\
            .with_items(None if data.get('items') is None else [
                IgnoreUser.from_dict(data.get('items')[i])
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


class GetIgnoreUserResult(core.Gs2Result):
    item: IgnoreUser = None

    def with_item(self, item: IgnoreUser) -> GetIgnoreUserResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetIgnoreUserResult]:
        if data is None:
            return None
        return GetIgnoreUserResult()\
            .with_item(IgnoreUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetIgnoreUserByGuildNameResult(core.Gs2Result):
    item: IgnoreUser = None

    def with_item(self, item: IgnoreUser) -> GetIgnoreUserByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetIgnoreUserByGuildNameResult]:
        if data is None:
            return None
        return GetIgnoreUserByGuildNameResult()\
            .with_item(IgnoreUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AddIgnoreUserResult(core.Gs2Result):
    item: IgnoreUser = None
    guild: Guild = None

    def with_item(self, item: IgnoreUser) -> AddIgnoreUserResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> AddIgnoreUserResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddIgnoreUserResult]:
        if data is None:
            return None
        return AddIgnoreUserResult()\
            .with_item(IgnoreUser.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class AddIgnoreUserByGuildNameResult(core.Gs2Result):
    item: IgnoreUser = None
    guild: Guild = None

    def with_item(self, item: IgnoreUser) -> AddIgnoreUserByGuildNameResult:
        self.item = item
        return self

    def with_guild(self, guild: Guild) -> AddIgnoreUserByGuildNameResult:
        self.guild = guild
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddIgnoreUserByGuildNameResult]:
        if data is None:
            return None
        return AddIgnoreUserByGuildNameResult()\
            .with_item(IgnoreUser.from_dict(data.get('item')))\
            .with_guild(Guild.from_dict(data.get('guild')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "guild": self.guild.to_dict() if self.guild else None,
        }


class DeleteIgnoreUserResult(core.Gs2Result):
    item: IgnoreUser = None

    def with_item(self, item: IgnoreUser) -> DeleteIgnoreUserResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteIgnoreUserResult]:
        if data is None:
            return None
        return DeleteIgnoreUserResult()\
            .with_item(IgnoreUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteIgnoreUserByGuildNameResult(core.Gs2Result):
    item: IgnoreUser = None

    def with_item(self, item: IgnoreUser) -> DeleteIgnoreUserByGuildNameResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteIgnoreUserByGuildNameResult]:
        if data is None:
            return None
        return DeleteIgnoreUserByGuildNameResult()\
            .with_item(IgnoreUser.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }