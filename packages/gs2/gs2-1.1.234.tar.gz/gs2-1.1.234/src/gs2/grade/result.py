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


class DescribeGradeModelMastersResult(core.Gs2Result):
    items: List[GradeModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[GradeModelMaster]) -> DescribeGradeModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeGradeModelMastersResult:
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
    ) -> Optional[DescribeGradeModelMastersResult]:
        if data is None:
            return None
        return DescribeGradeModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                GradeModelMaster.from_dict(data.get('items')[i])
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


class CreateGradeModelMasterResult(core.Gs2Result):
    item: GradeModelMaster = None

    def with_item(self, item: GradeModelMaster) -> CreateGradeModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateGradeModelMasterResult]:
        if data is None:
            return None
        return CreateGradeModelMasterResult()\
            .with_item(GradeModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetGradeModelMasterResult(core.Gs2Result):
    item: GradeModelMaster = None

    def with_item(self, item: GradeModelMaster) -> GetGradeModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGradeModelMasterResult]:
        if data is None:
            return None
        return GetGradeModelMasterResult()\
            .with_item(GradeModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateGradeModelMasterResult(core.Gs2Result):
    item: GradeModelMaster = None

    def with_item(self, item: GradeModelMaster) -> UpdateGradeModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateGradeModelMasterResult]:
        if data is None:
            return None
        return UpdateGradeModelMasterResult()\
            .with_item(GradeModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteGradeModelMasterResult(core.Gs2Result):
    item: GradeModelMaster = None

    def with_item(self, item: GradeModelMaster) -> DeleteGradeModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteGradeModelMasterResult]:
        if data is None:
            return None
        return DeleteGradeModelMasterResult()\
            .with_item(GradeModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeGradeModelsResult(core.Gs2Result):
    items: List[GradeModel] = None

    def with_items(self, items: List[GradeModel]) -> DescribeGradeModelsResult:
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
    ) -> Optional[DescribeGradeModelsResult]:
        if data is None:
            return None
        return DescribeGradeModelsResult()\
            .with_items(None if data.get('items') is None else [
                GradeModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetGradeModelResult(core.Gs2Result):
    item: GradeModel = None

    def with_item(self, item: GradeModel) -> GetGradeModelResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetGradeModelResult]:
        if data is None:
            return None
        return GetGradeModelResult()\
            .with_item(GradeModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeStatusesResult(core.Gs2Result):
    items: List[Status] = None
    next_page_token: str = None

    def with_items(self, items: List[Status]) -> DescribeStatusesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeStatusesResult:
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
    ) -> Optional[DescribeStatusesResult]:
        if data is None:
            return None
        return DescribeStatusesResult()\
            .with_items(None if data.get('items') is None else [
                Status.from_dict(data.get('items')[i])
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


class DescribeStatusesByUserIdResult(core.Gs2Result):
    items: List[Status] = None
    next_page_token: str = None

    def with_items(self, items: List[Status]) -> DescribeStatusesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeStatusesByUserIdResult:
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
    ) -> Optional[DescribeStatusesByUserIdResult]:
        if data is None:
            return None
        return DescribeStatusesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Status.from_dict(data.get('items')[i])
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


class GetStatusResult(core.Gs2Result):
    item: Status = None

    def with_item(self, item: Status) -> GetStatusResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStatusResult]:
        if data is None:
            return None
        return GetStatusResult()\
            .with_item(Status.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetStatusByUserIdResult(core.Gs2Result):
    item: Status = None

    def with_item(self, item: Status) -> GetStatusByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStatusByUserIdResult]:
        if data is None:
            return None
        return GetStatusByUserIdResult()\
            .with_item(Status.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AddGradeByUserIdResult(core.Gs2Result):
    item: Status = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> AddGradeByUserIdResult:
        self.item = item
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> AddGradeByUserIdResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> AddGradeByUserIdResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddGradeByUserIdResult]:
        if data is None:
            return None
        return AddGradeByUserIdResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class SubGradeResult(core.Gs2Result):
    item: Status = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> SubGradeResult:
        self.item = item
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> SubGradeResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> SubGradeResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubGradeResult]:
        if data is None:
            return None
        return SubGradeResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class SubGradeByUserIdResult(core.Gs2Result):
    item: Status = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> SubGradeByUserIdResult:
        self.item = item
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> SubGradeByUserIdResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> SubGradeByUserIdResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubGradeByUserIdResult]:
        if data is None:
            return None
        return SubGradeByUserIdResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class SetGradeByUserIdResult(core.Gs2Result):
    item: Status = None
    old: Status = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> SetGradeByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: Status) -> SetGradeByUserIdResult:
        self.old = old
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> SetGradeByUserIdResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> SetGradeByUserIdResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetGradeByUserIdResult]:
        if data is None:
            return None
        return SetGradeByUserIdResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_old(Status.from_dict(data.get('old')))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class ApplyRankCapResult(core.Gs2Result):
    item: Status = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> ApplyRankCapResult:
        self.item = item
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> ApplyRankCapResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> ApplyRankCapResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ApplyRankCapResult]:
        if data is None:
            return None
        return ApplyRankCapResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class ApplyRankCapByUserIdResult(core.Gs2Result):
    item: Status = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> ApplyRankCapByUserIdResult:
        self.item = item
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> ApplyRankCapByUserIdResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> ApplyRankCapByUserIdResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ApplyRankCapByUserIdResult]:
        if data is None:
            return None
        return ApplyRankCapByUserIdResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class DeleteStatusByUserIdResult(core.Gs2Result):
    item: Status = None

    def with_item(self, item: Status) -> DeleteStatusByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteStatusByUserIdResult]:
        if data is None:
            return None
        return DeleteStatusByUserIdResult()\
            .with_item(Status.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyGradeResult(core.Gs2Result):
    item: Status = None

    def with_item(self, item: Status) -> VerifyGradeResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyGradeResult]:
        if data is None:
            return None
        return VerifyGradeResult()\
            .with_item(Status.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyGradeByUserIdResult(core.Gs2Result):
    item: Status = None

    def with_item(self, item: Status) -> VerifyGradeByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyGradeByUserIdResult]:
        if data is None:
            return None
        return VerifyGradeByUserIdResult()\
            .with_item(Status.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyGradeUpMaterialResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyGradeUpMaterialResult]:
        if data is None:
            return None
        return VerifyGradeUpMaterialResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class VerifyGradeUpMaterialByUserIdResult(core.Gs2Result):

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyGradeUpMaterialByUserIdResult]:
        if data is None:
            return None
        return VerifyGradeUpMaterialByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class AddGradeByStampSheetResult(core.Gs2Result):
    item: Status = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> AddGradeByStampSheetResult:
        self.item = item
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> AddGradeByStampSheetResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> AddGradeByStampSheetResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddGradeByStampSheetResult]:
        if data is None:
            return None
        return AddGradeByStampSheetResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class ApplyRankCapByStampSheetResult(core.Gs2Result):
    item: Status = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> ApplyRankCapByStampSheetResult:
        self.item = item
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> ApplyRankCapByStampSheetResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> ApplyRankCapByStampSheetResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ApplyRankCapByStampSheetResult]:
        if data is None:
            return None
        return ApplyRankCapByStampSheetResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class SubGradeByStampTaskResult(core.Gs2Result):
    item: Status = None
    new_context_stack: str = None
    experience_namespace_name: str = None
    experience_status: Status = None

    def with_item(self, item: Status) -> SubGradeByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> SubGradeByStampTaskResult:
        self.new_context_stack = new_context_stack
        return self

    def with_experience_namespace_name(self, experience_namespace_name: str) -> SubGradeByStampTaskResult:
        self.experience_namespace_name = experience_namespace_name
        return self

    def with_experience_status(self, experience_status: Status) -> SubGradeByStampTaskResult:
        self.experience_status = experience_status
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubGradeByStampTaskResult]:
        if data is None:
            return None
        return SubGradeByStampTaskResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))\
            .with_experience_namespace_name(data.get('experienceNamespaceName'))\
            .with_experience_status(Status.from_dict(data.get('experienceStatus')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
            "experienceNamespaceName": self.experience_namespace_name,
            "experienceStatus": self.experience_status.to_dict() if self.experience_status else None,
        }


class MultiplyAcquireActionsByUserIdResult(core.Gs2Result):
    items: List[AcquireAction] = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_items(self, items: List[AcquireAction]) -> MultiplyAcquireActionsByUserIdResult:
        self.items = items
        return self

    def with_transaction_id(self, transaction_id: str) -> MultiplyAcquireActionsByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> MultiplyAcquireActionsByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> MultiplyAcquireActionsByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> MultiplyAcquireActionsByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> MultiplyAcquireActionsByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> MultiplyAcquireActionsByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> MultiplyAcquireActionsByUserIdResult:
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
    ) -> Optional[MultiplyAcquireActionsByUserIdResult]:
        if data is None:
            return None
        return MultiplyAcquireActionsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                AcquireAction.from_dict(data.get('items')[i])
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


class MultiplyAcquireActionsByStampSheetResult(core.Gs2Result):
    items: List[AcquireAction] = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_items(self, items: List[AcquireAction]) -> MultiplyAcquireActionsByStampSheetResult:
        self.items = items
        return self

    def with_transaction_id(self, transaction_id: str) -> MultiplyAcquireActionsByStampSheetResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> MultiplyAcquireActionsByStampSheetResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> MultiplyAcquireActionsByStampSheetResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> MultiplyAcquireActionsByStampSheetResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> MultiplyAcquireActionsByStampSheetResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> MultiplyAcquireActionsByStampSheetResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> MultiplyAcquireActionsByStampSheetResult:
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
    ) -> Optional[MultiplyAcquireActionsByStampSheetResult]:
        if data is None:
            return None
        return MultiplyAcquireActionsByStampSheetResult()\
            .with_items(None if data.get('items') is None else [
                AcquireAction.from_dict(data.get('items')[i])
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


class VerifyGradeByStampTaskResult(core.Gs2Result):
    item: Status = None
    new_context_stack: str = None

    def with_item(self, item: Status) -> VerifyGradeByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyGradeByStampTaskResult:
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
    ) -> Optional[VerifyGradeByStampTaskResult]:
        if data is None:
            return None
        return VerifyGradeByStampTaskResult()\
            .with_item(Status.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyGradeUpMaterialByStampTaskResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> VerifyGradeUpMaterialByStampTaskResult:
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
    ) -> Optional[VerifyGradeUpMaterialByStampTaskResult]:
        if data is None:
            return None
        return VerifyGradeUpMaterialByStampTaskResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentGradeMaster = None

    def with_item(self, item: CurrentGradeMaster) -> ExportMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
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
            .with_item(CurrentGradeMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentGradeMasterResult(core.Gs2Result):
    item: CurrentGradeMaster = None

    def with_item(self, item: CurrentGradeMaster) -> GetCurrentGradeMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCurrentGradeMasterResult]:
        if data is None:
            return None
        return GetCurrentGradeMasterResult()\
            .with_item(CurrentGradeMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentGradeMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentGradeMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentGradeMasterResult:
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
    ) -> Optional[PreUpdateCurrentGradeMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentGradeMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentGradeMasterResult(core.Gs2Result):
    item: CurrentGradeMaster = None

    def with_item(self, item: CurrentGradeMaster) -> UpdateCurrentGradeMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentGradeMasterResult]:
        if data is None:
            return None
        return UpdateCurrentGradeMasterResult()\
            .with_item(CurrentGradeMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentGradeMasterFromGitHubResult(core.Gs2Result):
    item: CurrentGradeMaster = None

    def with_item(self, item: CurrentGradeMaster) -> UpdateCurrentGradeMasterFromGitHubResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentGradeMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentGradeMasterFromGitHubResult()\
            .with_item(CurrentGradeMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }