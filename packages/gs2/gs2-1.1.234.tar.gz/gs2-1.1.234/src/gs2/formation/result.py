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


class GetFormModelResult(core.Gs2Result):
    item: FormModel = None

    def with_item(self, item: FormModel) -> GetFormModelResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormModelResult]:
        if data is None:
            return None
        return GetFormModelResult()\
            .with_item(FormModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeFormModelMastersResult(core.Gs2Result):
    items: List[FormModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[FormModelMaster]) -> DescribeFormModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeFormModelMastersResult:
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
    ) -> Optional[DescribeFormModelMastersResult]:
        if data is None:
            return None
        return DescribeFormModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                FormModelMaster.from_dict(data.get('items')[i])
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


class CreateFormModelMasterResult(core.Gs2Result):
    item: FormModelMaster = None

    def with_item(self, item: FormModelMaster) -> CreateFormModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateFormModelMasterResult]:
        if data is None:
            return None
        return CreateFormModelMasterResult()\
            .with_item(FormModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetFormModelMasterResult(core.Gs2Result):
    item: FormModelMaster = None

    def with_item(self, item: FormModelMaster) -> GetFormModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormModelMasterResult]:
        if data is None:
            return None
        return GetFormModelMasterResult()\
            .with_item(FormModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateFormModelMasterResult(core.Gs2Result):
    item: FormModelMaster = None

    def with_item(self, item: FormModelMaster) -> UpdateFormModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateFormModelMasterResult]:
        if data is None:
            return None
        return UpdateFormModelMasterResult()\
            .with_item(FormModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteFormModelMasterResult(core.Gs2Result):
    item: FormModelMaster = None

    def with_item(self, item: FormModelMaster) -> DeleteFormModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteFormModelMasterResult]:
        if data is None:
            return None
        return DeleteFormModelMasterResult()\
            .with_item(FormModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeMoldModelsResult(core.Gs2Result):
    items: List[MoldModel] = None

    def with_items(self, items: List[MoldModel]) -> DescribeMoldModelsResult:
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
    ) -> Optional[DescribeMoldModelsResult]:
        if data is None:
            return None
        return DescribeMoldModelsResult()\
            .with_items(None if data.get('items') is None else [
                MoldModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetMoldModelResult(core.Gs2Result):
    item: MoldModel = None

    def with_item(self, item: MoldModel) -> GetMoldModelResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMoldModelResult]:
        if data is None:
            return None
        return GetMoldModelResult()\
            .with_item(MoldModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeMoldModelMastersResult(core.Gs2Result):
    items: List[MoldModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[MoldModelMaster]) -> DescribeMoldModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeMoldModelMastersResult:
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
    ) -> Optional[DescribeMoldModelMastersResult]:
        if data is None:
            return None
        return DescribeMoldModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                MoldModelMaster.from_dict(data.get('items')[i])
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


class CreateMoldModelMasterResult(core.Gs2Result):
    item: MoldModelMaster = None

    def with_item(self, item: MoldModelMaster) -> CreateMoldModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateMoldModelMasterResult]:
        if data is None:
            return None
        return CreateMoldModelMasterResult()\
            .with_item(MoldModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetMoldModelMasterResult(core.Gs2Result):
    item: MoldModelMaster = None

    def with_item(self, item: MoldModelMaster) -> GetMoldModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMoldModelMasterResult]:
        if data is None:
            return None
        return GetMoldModelMasterResult()\
            .with_item(MoldModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateMoldModelMasterResult(core.Gs2Result):
    item: MoldModelMaster = None

    def with_item(self, item: MoldModelMaster) -> UpdateMoldModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMoldModelMasterResult]:
        if data is None:
            return None
        return UpdateMoldModelMasterResult()\
            .with_item(MoldModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteMoldModelMasterResult(core.Gs2Result):
    item: MoldModelMaster = None

    def with_item(self, item: MoldModelMaster) -> DeleteMoldModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMoldModelMasterResult]:
        if data is None:
            return None
        return DeleteMoldModelMasterResult()\
            .with_item(MoldModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribePropertyFormModelsResult(core.Gs2Result):
    items: List[PropertyFormModel] = None

    def with_items(self, items: List[PropertyFormModel]) -> DescribePropertyFormModelsResult:
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
    ) -> Optional[DescribePropertyFormModelsResult]:
        if data is None:
            return None
        return DescribePropertyFormModelsResult()\
            .with_items(None if data.get('items') is None else [
                PropertyFormModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetPropertyFormModelResult(core.Gs2Result):
    item: PropertyFormModel = None

    def with_item(self, item: PropertyFormModel) -> GetPropertyFormModelResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormModelResult]:
        if data is None:
            return None
        return GetPropertyFormModelResult()\
            .with_item(PropertyFormModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribePropertyFormModelMastersResult(core.Gs2Result):
    items: List[PropertyFormModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[PropertyFormModelMaster]) -> DescribePropertyFormModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribePropertyFormModelMastersResult:
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
    ) -> Optional[DescribePropertyFormModelMastersResult]:
        if data is None:
            return None
        return DescribePropertyFormModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                PropertyFormModelMaster.from_dict(data.get('items')[i])
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


class CreatePropertyFormModelMasterResult(core.Gs2Result):
    item: PropertyFormModelMaster = None

    def with_item(self, item: PropertyFormModelMaster) -> CreatePropertyFormModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreatePropertyFormModelMasterResult]:
        if data is None:
            return None
        return CreatePropertyFormModelMasterResult()\
            .with_item(PropertyFormModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetPropertyFormModelMasterResult(core.Gs2Result):
    item: PropertyFormModelMaster = None

    def with_item(self, item: PropertyFormModelMaster) -> GetPropertyFormModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormModelMasterResult]:
        if data is None:
            return None
        return GetPropertyFormModelMasterResult()\
            .with_item(PropertyFormModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdatePropertyFormModelMasterResult(core.Gs2Result):
    item: PropertyFormModelMaster = None

    def with_item(self, item: PropertyFormModelMaster) -> UpdatePropertyFormModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdatePropertyFormModelMasterResult]:
        if data is None:
            return None
        return UpdatePropertyFormModelMasterResult()\
            .with_item(PropertyFormModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeletePropertyFormModelMasterResult(core.Gs2Result):
    item: PropertyFormModelMaster = None

    def with_item(self, item: PropertyFormModelMaster) -> DeletePropertyFormModelMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeletePropertyFormModelMasterResult]:
        if data is None:
            return None
        return DeletePropertyFormModelMasterResult()\
            .with_item(PropertyFormModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentFormMaster = None

    def with_item(self, item: CurrentFormMaster) -> ExportMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
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
            .with_item(CurrentFormMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentFormMasterResult(core.Gs2Result):
    item: CurrentFormMaster = None

    def with_item(self, item: CurrentFormMaster) -> GetCurrentFormMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCurrentFormMasterResult]:
        if data is None:
            return None
        return GetCurrentFormMasterResult()\
            .with_item(CurrentFormMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentFormMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentFormMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentFormMasterResult:
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
    ) -> Optional[PreUpdateCurrentFormMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentFormMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentFormMasterResult(core.Gs2Result):
    item: CurrentFormMaster = None

    def with_item(self, item: CurrentFormMaster) -> UpdateCurrentFormMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentFormMasterResult]:
        if data is None:
            return None
        return UpdateCurrentFormMasterResult()\
            .with_item(CurrentFormMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentFormMasterFromGitHubResult(core.Gs2Result):
    item: CurrentFormMaster = None

    def with_item(self, item: CurrentFormMaster) -> UpdateCurrentFormMasterFromGitHubResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentFormMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentFormMasterFromGitHubResult()\
            .with_item(CurrentFormMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeMoldsResult(core.Gs2Result):
    items: List[Mold] = None
    next_page_token: str = None

    def with_items(self, items: List[Mold]) -> DescribeMoldsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeMoldsResult:
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
    ) -> Optional[DescribeMoldsResult]:
        if data is None:
            return None
        return DescribeMoldsResult()\
            .with_items(None if data.get('items') is None else [
                Mold.from_dict(data.get('items')[i])
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


class DescribeMoldsByUserIdResult(core.Gs2Result):
    items: List[Mold] = None
    next_page_token: str = None

    def with_items(self, items: List[Mold]) -> DescribeMoldsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeMoldsByUserIdResult:
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
    ) -> Optional[DescribeMoldsByUserIdResult]:
        if data is None:
            return None
        return DescribeMoldsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Mold.from_dict(data.get('items')[i])
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


class GetMoldResult(core.Gs2Result):
    item: Mold = None
    mold_model: MoldModel = None

    def with_item(self, item: Mold) -> GetMoldResult:
        self.item = item
        return self

    def with_mold_model(self, mold_model: MoldModel) -> GetMoldResult:
        self.mold_model = mold_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMoldResult]:
        if data is None:
            return None
        return GetMoldResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
        }


class GetMoldByUserIdResult(core.Gs2Result):
    item: Mold = None
    mold_model: MoldModel = None

    def with_item(self, item: Mold) -> GetMoldByUserIdResult:
        self.item = item
        return self

    def with_mold_model(self, mold_model: MoldModel) -> GetMoldByUserIdResult:
        self.mold_model = mold_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMoldByUserIdResult]:
        if data is None:
            return None
        return GetMoldByUserIdResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
        }


class SetMoldCapacityByUserIdResult(core.Gs2Result):
    item: Mold = None
    old: Mold = None
    mold_model: MoldModel = None

    def with_item(self, item: Mold) -> SetMoldCapacityByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: Mold) -> SetMoldCapacityByUserIdResult:
        self.old = old
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SetMoldCapacityByUserIdResult:
        self.mold_model = mold_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetMoldCapacityByUserIdResult]:
        if data is None:
            return None
        return SetMoldCapacityByUserIdResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_old(Mold.from_dict(data.get('old')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
        }


class AddMoldCapacityByUserIdResult(core.Gs2Result):
    item: Mold = None
    mold_model: MoldModel = None

    def with_item(self, item: Mold) -> AddMoldCapacityByUserIdResult:
        self.item = item
        return self

    def with_mold_model(self, mold_model: MoldModel) -> AddMoldCapacityByUserIdResult:
        self.mold_model = mold_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddMoldCapacityByUserIdResult]:
        if data is None:
            return None
        return AddMoldCapacityByUserIdResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
        }


class SubMoldCapacityResult(core.Gs2Result):
    item: Mold = None
    mold_model: MoldModel = None

    def with_item(self, item: Mold) -> SubMoldCapacityResult:
        self.item = item
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SubMoldCapacityResult:
        self.mold_model = mold_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubMoldCapacityResult]:
        if data is None:
            return None
        return SubMoldCapacityResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
        }


class SubMoldCapacityByUserIdResult(core.Gs2Result):
    item: Mold = None
    mold_model: MoldModel = None

    def with_item(self, item: Mold) -> SubMoldCapacityByUserIdResult:
        self.item = item
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SubMoldCapacityByUserIdResult:
        self.mold_model = mold_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubMoldCapacityByUserIdResult]:
        if data is None:
            return None
        return SubMoldCapacityByUserIdResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
        }


class DeleteMoldResult(core.Gs2Result):
    item: Mold = None

    def with_item(self, item: Mold) -> DeleteMoldResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMoldResult]:
        if data is None:
            return None
        return DeleteMoldResult()\
            .with_item(Mold.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteMoldByUserIdResult(core.Gs2Result):
    item: Mold = None

    def with_item(self, item: Mold) -> DeleteMoldByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMoldByUserIdResult]:
        if data is None:
            return None
        return DeleteMoldByUserIdResult()\
            .with_item(Mold.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class AddCapacityByStampSheetResult(core.Gs2Result):
    item: Mold = None
    mold_model: MoldModel = None

    def with_item(self, item: Mold) -> AddCapacityByStampSheetResult:
        self.item = item
        return self

    def with_mold_model(self, mold_model: MoldModel) -> AddCapacityByStampSheetResult:
        self.mold_model = mold_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AddCapacityByStampSheetResult]:
        if data is None:
            return None
        return AddCapacityByStampSheetResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
        }


class SubCapacityByStampTaskResult(core.Gs2Result):
    item: Mold = None
    mold_model: MoldModel = None
    new_context_stack: str = None

    def with_item(self, item: Mold) -> SubCapacityByStampTaskResult:
        self.item = item
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SubCapacityByStampTaskResult:
        self.mold_model = mold_model
        return self

    def with_new_context_stack(self, new_context_stack: str) -> SubCapacityByStampTaskResult:
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
    ) -> Optional[SubCapacityByStampTaskResult]:
        if data is None:
            return None
        return SubCapacityByStampTaskResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "newContextStack": self.new_context_stack,
        }


class SetCapacityByStampSheetResult(core.Gs2Result):
    item: Mold = None
    old: Mold = None
    mold_model: MoldModel = None

    def with_item(self, item: Mold) -> SetCapacityByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: Mold) -> SetCapacityByStampSheetResult:
        self.old = old
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SetCapacityByStampSheetResult:
        self.mold_model = mold_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetCapacityByStampSheetResult]:
        if data is None:
            return None
        return SetCapacityByStampSheetResult()\
            .with_item(Mold.from_dict(data.get('item')))\
            .with_old(Mold.from_dict(data.get('old')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
        }


class DescribeFormsResult(core.Gs2Result):
    items: List[Form] = None
    next_page_token: str = None

    def with_items(self, items: List[Form]) -> DescribeFormsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeFormsResult:
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
    ) -> Optional[DescribeFormsResult]:
        if data is None:
            return None
        return DescribeFormsResult()\
            .with_items(None if data.get('items') is None else [
                Form.from_dict(data.get('items')[i])
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


class DescribeFormsByUserIdResult(core.Gs2Result):
    items: List[Form] = None
    next_page_token: str = None

    def with_items(self, items: List[Form]) -> DescribeFormsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeFormsByUserIdResult:
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
    ) -> Optional[DescribeFormsByUserIdResult]:
        if data is None:
            return None
        return DescribeFormsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Form.from_dict(data.get('items')[i])
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


class GetFormResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> GetFormResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> GetFormResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> GetFormResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> GetFormResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormResult]:
        if data is None:
            return None
        return GetFormResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class GetFormByUserIdResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> GetFormByUserIdResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> GetFormByUserIdResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> GetFormByUserIdResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> GetFormByUserIdResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormByUserIdResult]:
        if data is None:
            return None
        return GetFormByUserIdResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class GetFormWithSignatureResult(core.Gs2Result):
    item: Form = None
    body: str = None
    signature: str = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> GetFormWithSignatureResult:
        self.item = item
        return self

    def with_body(self, body: str) -> GetFormWithSignatureResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetFormWithSignatureResult:
        self.signature = signature
        return self

    def with_mold(self, mold: Mold) -> GetFormWithSignatureResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> GetFormWithSignatureResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> GetFormWithSignatureResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormWithSignatureResult]:
        if data is None:
            return None
        return GetFormWithSignatureResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "body": self.body,
            "signature": self.signature,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class GetFormWithSignatureByUserIdResult(core.Gs2Result):
    item: Form = None
    body: str = None
    signature: str = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> GetFormWithSignatureByUserIdResult:
        self.item = item
        return self

    def with_body(self, body: str) -> GetFormWithSignatureByUserIdResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetFormWithSignatureByUserIdResult:
        self.signature = signature
        return self

    def with_mold(self, mold: Mold) -> GetFormWithSignatureByUserIdResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> GetFormWithSignatureByUserIdResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> GetFormWithSignatureByUserIdResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormWithSignatureByUserIdResult]:
        if data is None:
            return None
        return GetFormWithSignatureByUserIdResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "body": self.body,
            "signature": self.signature,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class SetFormResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> SetFormResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> SetFormResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SetFormResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> SetFormResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetFormResult]:
        if data is None:
            return None
        return SetFormResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class SetFormByUserIdResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> SetFormByUserIdResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> SetFormByUserIdResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SetFormByUserIdResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> SetFormByUserIdResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetFormByUserIdResult]:
        if data is None:
            return None
        return SetFormByUserIdResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class SetFormWithSignatureResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> SetFormWithSignatureResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> SetFormWithSignatureResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SetFormWithSignatureResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> SetFormWithSignatureResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetFormWithSignatureResult]:
        if data is None:
            return None
        return SetFormWithSignatureResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class AcquireActionsToFormPropertiesResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: Form) -> AcquireActionsToFormPropertiesResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> AcquireActionsToFormPropertiesResult:
        self.mold = mold
        return self

    def with_transaction_id(self, transaction_id: str) -> AcquireActionsToFormPropertiesResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireActionsToFormPropertiesResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> AcquireActionsToFormPropertiesResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> AcquireActionsToFormPropertiesResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> AcquireActionsToFormPropertiesResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> AcquireActionsToFormPropertiesResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> AcquireActionsToFormPropertiesResult:
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
    ) -> Optional[AcquireActionsToFormPropertiesResult]:
        if data is None:
            return None
        return AcquireActionsToFormPropertiesResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
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
            "mold": self.mold.to_dict() if self.mold else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class DeleteFormResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> DeleteFormResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> DeleteFormResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> DeleteFormResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> DeleteFormResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteFormResult]:
        if data is None:
            return None
        return DeleteFormResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class DeleteFormByUserIdResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> DeleteFormByUserIdResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> DeleteFormByUserIdResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> DeleteFormByUserIdResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> DeleteFormByUserIdResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteFormByUserIdResult]:
        if data is None:
            return None
        return DeleteFormByUserIdResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class AcquireActionToFormPropertiesByStampSheetResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: Form) -> AcquireActionToFormPropertiesByStampSheetResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> AcquireActionToFormPropertiesByStampSheetResult:
        self.mold = mold
        return self

    def with_transaction_id(self, transaction_id: str) -> AcquireActionToFormPropertiesByStampSheetResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireActionToFormPropertiesByStampSheetResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> AcquireActionToFormPropertiesByStampSheetResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> AcquireActionToFormPropertiesByStampSheetResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> AcquireActionToFormPropertiesByStampSheetResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> AcquireActionToFormPropertiesByStampSheetResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> AcquireActionToFormPropertiesByStampSheetResult:
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
    ) -> Optional[AcquireActionToFormPropertiesByStampSheetResult]:
        if data is None:
            return None
        return AcquireActionToFormPropertiesByStampSheetResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
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
            "mold": self.mold.to_dict() if self.mold else None,
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class SetFormByStampSheetResult(core.Gs2Result):
    item: Form = None
    mold: Mold = None
    mold_model: MoldModel = None
    form_model: FormModel = None

    def with_item(self, item: Form) -> SetFormByStampSheetResult:
        self.item = item
        return self

    def with_mold(self, mold: Mold) -> SetFormByStampSheetResult:
        self.mold = mold
        return self

    def with_mold_model(self, mold_model: MoldModel) -> SetFormByStampSheetResult:
        self.mold_model = mold_model
        return self

    def with_form_model(self, form_model: FormModel) -> SetFormByStampSheetResult:
        self.form_model = form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetFormByStampSheetResult]:
        if data is None:
            return None
        return SetFormByStampSheetResult()\
            .with_item(Form.from_dict(data.get('item')))\
            .with_mold(Mold.from_dict(data.get('mold')))\
            .with_mold_model(MoldModel.from_dict(data.get('moldModel')))\
            .with_form_model(FormModel.from_dict(data.get('formModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "mold": self.mold.to_dict() if self.mold else None,
            "moldModel": self.mold_model.to_dict() if self.mold_model else None,
            "formModel": self.form_model.to_dict() if self.form_model else None,
        }


class DescribePropertyFormsResult(core.Gs2Result):
    items: List[PropertyForm] = None
    next_page_token: str = None

    def with_items(self, items: List[PropertyForm]) -> DescribePropertyFormsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribePropertyFormsResult:
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
    ) -> Optional[DescribePropertyFormsResult]:
        if data is None:
            return None
        return DescribePropertyFormsResult()\
            .with_items(None if data.get('items') is None else [
                PropertyForm.from_dict(data.get('items')[i])
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


class DescribePropertyFormsByUserIdResult(core.Gs2Result):
    items: List[PropertyForm] = None
    next_page_token: str = None

    def with_items(self, items: List[PropertyForm]) -> DescribePropertyFormsByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribePropertyFormsByUserIdResult:
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
    ) -> Optional[DescribePropertyFormsByUserIdResult]:
        if data is None:
            return None
        return DescribePropertyFormsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                PropertyForm.from_dict(data.get('items')[i])
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


class GetPropertyFormResult(core.Gs2Result):
    item: PropertyForm = None
    property_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> GetPropertyFormResult:
        self.item = item
        return self

    def with_property_form_model(self, property_form_model: PropertyFormModel) -> GetPropertyFormResult:
        self.property_form_model = property_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormResult]:
        if data is None:
            return None
        return GetPropertyFormResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_property_form_model(PropertyFormModel.from_dict(data.get('propertyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "propertyFormModel": self.property_form_model.to_dict() if self.property_form_model else None,
        }


class GetPropertyFormByUserIdResult(core.Gs2Result):
    item: PropertyForm = None
    property_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> GetPropertyFormByUserIdResult:
        self.item = item
        return self

    def with_property_form_model(self, property_form_model: PropertyFormModel) -> GetPropertyFormByUserIdResult:
        self.property_form_model = property_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormByUserIdResult]:
        if data is None:
            return None
        return GetPropertyFormByUserIdResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_property_form_model(PropertyFormModel.from_dict(data.get('propertyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "propertyFormModel": self.property_form_model.to_dict() if self.property_form_model else None,
        }


class GetPropertyFormWithSignatureResult(core.Gs2Result):
    item: PropertyForm = None
    body: str = None
    signature: str = None
    property_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> GetPropertyFormWithSignatureResult:
        self.item = item
        return self

    def with_body(self, body: str) -> GetPropertyFormWithSignatureResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetPropertyFormWithSignatureResult:
        self.signature = signature
        return self

    def with_property_form_model(self, property_form_model: PropertyFormModel) -> GetPropertyFormWithSignatureResult:
        self.property_form_model = property_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormWithSignatureResult]:
        if data is None:
            return None
        return GetPropertyFormWithSignatureResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))\
            .with_property_form_model(PropertyFormModel.from_dict(data.get('propertyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "body": self.body,
            "signature": self.signature,
            "propertyFormModel": self.property_form_model.to_dict() if self.property_form_model else None,
        }


class GetPropertyFormWithSignatureByUserIdResult(core.Gs2Result):
    item: PropertyForm = None
    body: str = None
    signature: str = None
    property_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> GetPropertyFormWithSignatureByUserIdResult:
        self.item = item
        return self

    def with_body(self, body: str) -> GetPropertyFormWithSignatureByUserIdResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> GetPropertyFormWithSignatureByUserIdResult:
        self.signature = signature
        return self

    def with_property_form_model(self, property_form_model: PropertyFormModel) -> GetPropertyFormWithSignatureByUserIdResult:
        self.property_form_model = property_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormWithSignatureByUserIdResult]:
        if data is None:
            return None
        return GetPropertyFormWithSignatureByUserIdResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))\
            .with_property_form_model(PropertyFormModel.from_dict(data.get('propertyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "body": self.body,
            "signature": self.signature,
            "propertyFormModel": self.property_form_model.to_dict() if self.property_form_model else None,
        }


class SetPropertyFormResult(core.Gs2Result):
    item: PropertyForm = None
    property_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> SetPropertyFormResult:
        self.item = item
        return self

    def with_property_form_model(self, property_form_model: PropertyFormModel) -> SetPropertyFormResult:
        self.property_form_model = property_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetPropertyFormResult]:
        if data is None:
            return None
        return SetPropertyFormResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_property_form_model(PropertyFormModel.from_dict(data.get('propertyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "propertyFormModel": self.property_form_model.to_dict() if self.property_form_model else None,
        }


class SetPropertyFormByUserIdResult(core.Gs2Result):
    item: PropertyForm = None
    property_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> SetPropertyFormByUserIdResult:
        self.item = item
        return self

    def with_property_form_model(self, property_form_model: PropertyFormModel) -> SetPropertyFormByUserIdResult:
        self.property_form_model = property_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetPropertyFormByUserIdResult]:
        if data is None:
            return None
        return SetPropertyFormByUserIdResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_property_form_model(PropertyFormModel.from_dict(data.get('propertyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "propertyFormModel": self.property_form_model.to_dict() if self.property_form_model else None,
        }


class SetPropertyFormWithSignatureResult(core.Gs2Result):
    item: PropertyForm = None
    proeprty_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> SetPropertyFormWithSignatureResult:
        self.item = item
        return self

    def with_proeprty_form_model(self, proeprty_form_model: PropertyFormModel) -> SetPropertyFormWithSignatureResult:
        self.proeprty_form_model = proeprty_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetPropertyFormWithSignatureResult]:
        if data is None:
            return None
        return SetPropertyFormWithSignatureResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_proeprty_form_model(PropertyFormModel.from_dict(data.get('proeprtyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "proeprtyFormModel": self.proeprty_form_model.to_dict() if self.proeprty_form_model else None,
        }


class AcquireActionsToPropertyFormPropertiesResult(core.Gs2Result):
    item: PropertyForm = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: PropertyForm) -> AcquireActionsToPropertyFormPropertiesResult:
        self.item = item
        return self

    def with_transaction_id(self, transaction_id: str) -> AcquireActionsToPropertyFormPropertiesResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireActionsToPropertyFormPropertiesResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> AcquireActionsToPropertyFormPropertiesResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> AcquireActionsToPropertyFormPropertiesResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> AcquireActionsToPropertyFormPropertiesResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> AcquireActionsToPropertyFormPropertiesResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> AcquireActionsToPropertyFormPropertiesResult:
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
    ) -> Optional[AcquireActionsToPropertyFormPropertiesResult]:
        if data is None:
            return None
        return AcquireActionsToPropertyFormPropertiesResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
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
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class DeletePropertyFormResult(core.Gs2Result):
    item: PropertyForm = None
    property_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> DeletePropertyFormResult:
        self.item = item
        return self

    def with_property_form_model(self, property_form_model: PropertyFormModel) -> DeletePropertyFormResult:
        self.property_form_model = property_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeletePropertyFormResult]:
        if data is None:
            return None
        return DeletePropertyFormResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_property_form_model(PropertyFormModel.from_dict(data.get('propertyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "propertyFormModel": self.property_form_model.to_dict() if self.property_form_model else None,
        }


class DeletePropertyFormByUserIdResult(core.Gs2Result):
    item: PropertyForm = None
    property_form_model: PropertyFormModel = None

    def with_item(self, item: PropertyForm) -> DeletePropertyFormByUserIdResult:
        self.item = item
        return self

    def with_property_form_model(self, property_form_model: PropertyFormModel) -> DeletePropertyFormByUserIdResult:
        self.property_form_model = property_form_model
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeletePropertyFormByUserIdResult]:
        if data is None:
            return None
        return DeletePropertyFormByUserIdResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
            .with_property_form_model(PropertyFormModel.from_dict(data.get('propertyFormModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "propertyFormModel": self.property_form_model.to_dict() if self.property_form_model else None,
        }


class AcquireActionToPropertyFormPropertiesByStampSheetResult(core.Gs2Result):
    item: PropertyForm = None
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_item(self, item: PropertyForm) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        self.item = item
        return self

    def with_transaction_id(self, transaction_id: str) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
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
    ) -> Optional[AcquireActionToPropertyFormPropertiesByStampSheetResult]:
        if data is None:
            return None
        return AcquireActionToPropertyFormPropertiesByStampSheetResult()\
            .with_item(PropertyForm.from_dict(data.get('item')))\
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
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }