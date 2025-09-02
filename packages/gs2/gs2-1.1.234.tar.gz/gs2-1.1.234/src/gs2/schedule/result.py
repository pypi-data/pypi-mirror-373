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


class DescribeEventMastersResult(core.Gs2Result):
    items: List[EventMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[EventMaster]) -> DescribeEventMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeEventMastersResult:
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
    ) -> Optional[DescribeEventMastersResult]:
        if data is None:
            return None
        return DescribeEventMastersResult()\
            .with_items(None if data.get('items') is None else [
                EventMaster.from_dict(data.get('items')[i])
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


class CreateEventMasterResult(core.Gs2Result):
    item: EventMaster = None

    def with_item(self, item: EventMaster) -> CreateEventMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateEventMasterResult]:
        if data is None:
            return None
        return CreateEventMasterResult()\
            .with_item(EventMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetEventMasterResult(core.Gs2Result):
    item: EventMaster = None

    def with_item(self, item: EventMaster) -> GetEventMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetEventMasterResult]:
        if data is None:
            return None
        return GetEventMasterResult()\
            .with_item(EventMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateEventMasterResult(core.Gs2Result):
    item: EventMaster = None

    def with_item(self, item: EventMaster) -> UpdateEventMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateEventMasterResult]:
        if data is None:
            return None
        return UpdateEventMasterResult()\
            .with_item(EventMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteEventMasterResult(core.Gs2Result):
    item: EventMaster = None

    def with_item(self, item: EventMaster) -> DeleteEventMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteEventMasterResult]:
        if data is None:
            return None
        return DeleteEventMasterResult()\
            .with_item(EventMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeTriggersResult(core.Gs2Result):
    items: List[Trigger] = None
    next_page_token: str = None

    def with_items(self, items: List[Trigger]) -> DescribeTriggersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeTriggersResult:
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
    ) -> Optional[DescribeTriggersResult]:
        if data is None:
            return None
        return DescribeTriggersResult()\
            .with_items(None if data.get('items') is None else [
                Trigger.from_dict(data.get('items')[i])
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


class DescribeTriggersByUserIdResult(core.Gs2Result):
    items: List[Trigger] = None
    next_page_token: str = None

    def with_items(self, items: List[Trigger]) -> DescribeTriggersByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeTriggersByUserIdResult:
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
    ) -> Optional[DescribeTriggersByUserIdResult]:
        if data is None:
            return None
        return DescribeTriggersByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Trigger.from_dict(data.get('items')[i])
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


class GetTriggerResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> GetTriggerResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetTriggerResult]:
        if data is None:
            return None
        return GetTriggerResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetTriggerByUserIdResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> GetTriggerByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetTriggerByUserIdResult]:
        if data is None:
            return None
        return GetTriggerByUserIdResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class TriggerByUserIdResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> TriggerByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TriggerByUserIdResult]:
        if data is None:
            return None
        return TriggerByUserIdResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExtendTriggerByUserIdResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> ExtendTriggerByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ExtendTriggerByUserIdResult]:
        if data is None:
            return None
        return ExtendTriggerByUserIdResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class TriggerByStampSheetResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> TriggerByStampSheetResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TriggerByStampSheetResult]:
        if data is None:
            return None
        return TriggerByStampSheetResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExtendTriggerByStampSheetResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> ExtendTriggerByStampSheetResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ExtendTriggerByStampSheetResult]:
        if data is None:
            return None
        return ExtendTriggerByStampSheetResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteTriggerResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> DeleteTriggerResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteTriggerResult]:
        if data is None:
            return None
        return DeleteTriggerResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteTriggerByUserIdResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> DeleteTriggerByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteTriggerByUserIdResult]:
        if data is None:
            return None
        return DeleteTriggerByUserIdResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyTriggerResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> VerifyTriggerResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyTriggerResult]:
        if data is None:
            return None
        return VerifyTriggerResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyTriggerByUserIdResult(core.Gs2Result):
    item: Trigger = None

    def with_item(self, item: Trigger) -> VerifyTriggerByUserIdResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyTriggerByUserIdResult]:
        if data is None:
            return None
        return VerifyTriggerByUserIdResult()\
            .with_item(Trigger.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteTriggerByStampTaskResult(core.Gs2Result):
    item: Trigger = None
    new_context_stack: str = None

    def with_item(self, item: Trigger) -> DeleteTriggerByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> DeleteTriggerByStampTaskResult:
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
    ) -> Optional[DeleteTriggerByStampTaskResult]:
        if data is None:
            return None
        return DeleteTriggerByStampTaskResult()\
            .with_item(Trigger.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyTriggerByStampTaskResult(core.Gs2Result):
    item: Trigger = None
    new_context_stack: str = None

    def with_item(self, item: Trigger) -> VerifyTriggerByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyTriggerByStampTaskResult:
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
    ) -> Optional[VerifyTriggerByStampTaskResult]:
        if data is None:
            return None
        return VerifyTriggerByStampTaskResult()\
            .with_item(Trigger.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeEventsResult(core.Gs2Result):
    items: List[Event] = None

    def with_items(self, items: List[Event]) -> DescribeEventsResult:
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
    ) -> Optional[DescribeEventsResult]:
        if data is None:
            return None
        return DescribeEventsResult()\
            .with_items(None if data.get('items') is None else [
                Event.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class DescribeEventsByUserIdResult(core.Gs2Result):
    items: List[Event] = None

    def with_items(self, items: List[Event]) -> DescribeEventsByUserIdResult:
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
    ) -> Optional[DescribeEventsByUserIdResult]:
        if data is None:
            return None
        return DescribeEventsByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Event.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class DescribeRawEventsResult(core.Gs2Result):
    items: List[Event] = None

    def with_items(self, items: List[Event]) -> DescribeRawEventsResult:
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
    ) -> Optional[DescribeRawEventsResult]:
        if data is None:
            return None
        return DescribeRawEventsResult()\
            .with_items(None if data.get('items') is None else [
                Event.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetEventResult(core.Gs2Result):
    item: Event = None
    in_schedule: bool = None
    schedule_start_at: int = None
    schedule_end_at: int = None
    repeat_schedule: RepeatSchedule = None
    is_global_schedule: bool = None

    def with_item(self, item: Event) -> GetEventResult:
        self.item = item
        return self

    def with_in_schedule(self, in_schedule: bool) -> GetEventResult:
        self.in_schedule = in_schedule
        return self

    def with_schedule_start_at(self, schedule_start_at: int) -> GetEventResult:
        self.schedule_start_at = schedule_start_at
        return self

    def with_schedule_end_at(self, schedule_end_at: int) -> GetEventResult:
        self.schedule_end_at = schedule_end_at
        return self

    def with_repeat_schedule(self, repeat_schedule: RepeatSchedule) -> GetEventResult:
        self.repeat_schedule = repeat_schedule
        return self

    def with_is_global_schedule(self, is_global_schedule: bool) -> GetEventResult:
        self.is_global_schedule = is_global_schedule
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetEventResult]:
        if data is None:
            return None
        return GetEventResult()\
            .with_item(Event.from_dict(data.get('item')))\
            .with_in_schedule(data.get('inSchedule'))\
            .with_schedule_start_at(data.get('scheduleStartAt'))\
            .with_schedule_end_at(data.get('scheduleEndAt'))\
            .with_repeat_schedule(RepeatSchedule.from_dict(data.get('repeatSchedule')))\
            .with_is_global_schedule(data.get('isGlobalSchedule'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "inSchedule": self.in_schedule,
            "scheduleStartAt": self.schedule_start_at,
            "scheduleEndAt": self.schedule_end_at,
            "repeatSchedule": self.repeat_schedule.to_dict() if self.repeat_schedule else None,
            "isGlobalSchedule": self.is_global_schedule,
        }


class GetEventByUserIdResult(core.Gs2Result):
    item: Event = None
    in_schedule: bool = None
    schedule_start_at: int = None
    schedule_end_at: int = None
    repeat_schedule: RepeatSchedule = None
    is_global_schedule: bool = None

    def with_item(self, item: Event) -> GetEventByUserIdResult:
        self.item = item
        return self

    def with_in_schedule(self, in_schedule: bool) -> GetEventByUserIdResult:
        self.in_schedule = in_schedule
        return self

    def with_schedule_start_at(self, schedule_start_at: int) -> GetEventByUserIdResult:
        self.schedule_start_at = schedule_start_at
        return self

    def with_schedule_end_at(self, schedule_end_at: int) -> GetEventByUserIdResult:
        self.schedule_end_at = schedule_end_at
        return self

    def with_repeat_schedule(self, repeat_schedule: RepeatSchedule) -> GetEventByUserIdResult:
        self.repeat_schedule = repeat_schedule
        return self

    def with_is_global_schedule(self, is_global_schedule: bool) -> GetEventByUserIdResult:
        self.is_global_schedule = is_global_schedule
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetEventByUserIdResult]:
        if data is None:
            return None
        return GetEventByUserIdResult()\
            .with_item(Event.from_dict(data.get('item')))\
            .with_in_schedule(data.get('inSchedule'))\
            .with_schedule_start_at(data.get('scheduleStartAt'))\
            .with_schedule_end_at(data.get('scheduleEndAt'))\
            .with_repeat_schedule(RepeatSchedule.from_dict(data.get('repeatSchedule')))\
            .with_is_global_schedule(data.get('isGlobalSchedule'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "inSchedule": self.in_schedule,
            "scheduleStartAt": self.schedule_start_at,
            "scheduleEndAt": self.schedule_end_at,
            "repeatSchedule": self.repeat_schedule.to_dict() if self.repeat_schedule else None,
            "isGlobalSchedule": self.is_global_schedule,
        }


class GetRawEventResult(core.Gs2Result):
    item: Event = None

    def with_item(self, item: Event) -> GetRawEventResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRawEventResult]:
        if data is None:
            return None
        return GetRawEventResult()\
            .with_item(Event.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyEventResult(core.Gs2Result):
    item: Event = None
    in_schedule: bool = None
    schedule_start_at: int = None
    schedule_end_at: int = None
    repeat_schedule: RepeatSchedule = None
    is_global_schedule: bool = None

    def with_item(self, item: Event) -> VerifyEventResult:
        self.item = item
        return self

    def with_in_schedule(self, in_schedule: bool) -> VerifyEventResult:
        self.in_schedule = in_schedule
        return self

    def with_schedule_start_at(self, schedule_start_at: int) -> VerifyEventResult:
        self.schedule_start_at = schedule_start_at
        return self

    def with_schedule_end_at(self, schedule_end_at: int) -> VerifyEventResult:
        self.schedule_end_at = schedule_end_at
        return self

    def with_repeat_schedule(self, repeat_schedule: RepeatSchedule) -> VerifyEventResult:
        self.repeat_schedule = repeat_schedule
        return self

    def with_is_global_schedule(self, is_global_schedule: bool) -> VerifyEventResult:
        self.is_global_schedule = is_global_schedule
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyEventResult]:
        if data is None:
            return None
        return VerifyEventResult()\
            .with_item(Event.from_dict(data.get('item')))\
            .with_in_schedule(data.get('inSchedule'))\
            .with_schedule_start_at(data.get('scheduleStartAt'))\
            .with_schedule_end_at(data.get('scheduleEndAt'))\
            .with_repeat_schedule(RepeatSchedule.from_dict(data.get('repeatSchedule')))\
            .with_is_global_schedule(data.get('isGlobalSchedule'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "inSchedule": self.in_schedule,
            "scheduleStartAt": self.schedule_start_at,
            "scheduleEndAt": self.schedule_end_at,
            "repeatSchedule": self.repeat_schedule.to_dict() if self.repeat_schedule else None,
            "isGlobalSchedule": self.is_global_schedule,
        }


class VerifyEventByUserIdResult(core.Gs2Result):
    item: Event = None
    in_schedule: bool = None
    schedule_start_at: int = None
    schedule_end_at: int = None
    repeat_schedule: RepeatSchedule = None
    is_global_schedule: bool = None

    def with_item(self, item: Event) -> VerifyEventByUserIdResult:
        self.item = item
        return self

    def with_in_schedule(self, in_schedule: bool) -> VerifyEventByUserIdResult:
        self.in_schedule = in_schedule
        return self

    def with_schedule_start_at(self, schedule_start_at: int) -> VerifyEventByUserIdResult:
        self.schedule_start_at = schedule_start_at
        return self

    def with_schedule_end_at(self, schedule_end_at: int) -> VerifyEventByUserIdResult:
        self.schedule_end_at = schedule_end_at
        return self

    def with_repeat_schedule(self, repeat_schedule: RepeatSchedule) -> VerifyEventByUserIdResult:
        self.repeat_schedule = repeat_schedule
        return self

    def with_is_global_schedule(self, is_global_schedule: bool) -> VerifyEventByUserIdResult:
        self.is_global_schedule = is_global_schedule
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyEventByUserIdResult]:
        if data is None:
            return None
        return VerifyEventByUserIdResult()\
            .with_item(Event.from_dict(data.get('item')))\
            .with_in_schedule(data.get('inSchedule'))\
            .with_schedule_start_at(data.get('scheduleStartAt'))\
            .with_schedule_end_at(data.get('scheduleEndAt'))\
            .with_repeat_schedule(RepeatSchedule.from_dict(data.get('repeatSchedule')))\
            .with_is_global_schedule(data.get('isGlobalSchedule'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "inSchedule": self.in_schedule,
            "scheduleStartAt": self.schedule_start_at,
            "scheduleEndAt": self.schedule_end_at,
            "repeatSchedule": self.repeat_schedule.to_dict() if self.repeat_schedule else None,
            "isGlobalSchedule": self.is_global_schedule,
        }


class VerifyEventByStampTaskResult(core.Gs2Result):
    item: Event = None
    in_schedule: bool = None
    schedule_start_at: int = None
    schedule_end_at: int = None
    repeat_schedule: RepeatSchedule = None
    is_global_schedule: bool = None
    new_context_stack: str = None

    def with_item(self, item: Event) -> VerifyEventByStampTaskResult:
        self.item = item
        return self

    def with_in_schedule(self, in_schedule: bool) -> VerifyEventByStampTaskResult:
        self.in_schedule = in_schedule
        return self

    def with_schedule_start_at(self, schedule_start_at: int) -> VerifyEventByStampTaskResult:
        self.schedule_start_at = schedule_start_at
        return self

    def with_schedule_end_at(self, schedule_end_at: int) -> VerifyEventByStampTaskResult:
        self.schedule_end_at = schedule_end_at
        return self

    def with_repeat_schedule(self, repeat_schedule: RepeatSchedule) -> VerifyEventByStampTaskResult:
        self.repeat_schedule = repeat_schedule
        return self

    def with_is_global_schedule(self, is_global_schedule: bool) -> VerifyEventByStampTaskResult:
        self.is_global_schedule = is_global_schedule
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyEventByStampTaskResult:
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
    ) -> Optional[VerifyEventByStampTaskResult]:
        if data is None:
            return None
        return VerifyEventByStampTaskResult()\
            .with_item(Event.from_dict(data.get('item')))\
            .with_in_schedule(data.get('inSchedule'))\
            .with_schedule_start_at(data.get('scheduleStartAt'))\
            .with_schedule_end_at(data.get('scheduleEndAt'))\
            .with_repeat_schedule(RepeatSchedule.from_dict(data.get('repeatSchedule')))\
            .with_is_global_schedule(data.get('isGlobalSchedule'))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "inSchedule": self.in_schedule,
            "scheduleStartAt": self.schedule_start_at,
            "scheduleEndAt": self.schedule_end_at,
            "repeatSchedule": self.repeat_schedule.to_dict() if self.repeat_schedule else None,
            "isGlobalSchedule": self.is_global_schedule,
            "newContextStack": self.new_context_stack,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentEventMaster = None

    def with_item(self, item: CurrentEventMaster) -> ExportMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
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
            .with_item(CurrentEventMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentEventMasterResult(core.Gs2Result):
    item: CurrentEventMaster = None

    def with_item(self, item: CurrentEventMaster) -> GetCurrentEventMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetCurrentEventMasterResult]:
        if data is None:
            return None
        return GetCurrentEventMasterResult()\
            .with_item(CurrentEventMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentEventMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentEventMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentEventMasterResult:
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
    ) -> Optional[PreUpdateCurrentEventMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentEventMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentEventMasterResult(core.Gs2Result):
    item: CurrentEventMaster = None

    def with_item(self, item: CurrentEventMaster) -> UpdateCurrentEventMasterResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentEventMasterResult]:
        if data is None:
            return None
        return UpdateCurrentEventMasterResult()\
            .with_item(CurrentEventMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentEventMasterFromGitHubResult(core.Gs2Result):
    item: CurrentEventMaster = None

    def with_item(self, item: CurrentEventMaster) -> UpdateCurrentEventMasterFromGitHubResult:
        self.item = item
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateCurrentEventMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentEventMasterFromGitHubResult()\
            .with_item(CurrentEventMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }