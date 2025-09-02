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


class QueryAccessLogResult(core.Gs2Result):
    items: List[AccessLog] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[AccessLog]) -> QueryAccessLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> QueryAccessLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> QueryAccessLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> QueryAccessLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryAccessLogResult]:
        if data is None:
            return None
        return QueryAccessLogResult()\
            .with_items(None if data.get('items') is None else [
                AccessLog.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class CountAccessLogResult(core.Gs2Result):
    items: List[AccessLogCount] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[AccessLogCount]) -> CountAccessLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> CountAccessLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> CountAccessLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> CountAccessLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CountAccessLogResult]:
        if data is None:
            return None
        return CountAccessLogResult()\
            .with_items(None if data.get('items') is None else [
                AccessLogCount.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class QueryIssueStampSheetLogResult(core.Gs2Result):
    items: List[IssueStampSheetLog] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[IssueStampSheetLog]) -> QueryIssueStampSheetLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> QueryIssueStampSheetLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> QueryIssueStampSheetLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> QueryIssueStampSheetLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryIssueStampSheetLogResult]:
        if data is None:
            return None
        return QueryIssueStampSheetLogResult()\
            .with_items(None if data.get('items') is None else [
                IssueStampSheetLog.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class CountIssueStampSheetLogResult(core.Gs2Result):
    items: List[IssueStampSheetLogCount] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[IssueStampSheetLogCount]) -> CountIssueStampSheetLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> CountIssueStampSheetLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> CountIssueStampSheetLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> CountIssueStampSheetLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CountIssueStampSheetLogResult]:
        if data is None:
            return None
        return CountIssueStampSheetLogResult()\
            .with_items(None if data.get('items') is None else [
                IssueStampSheetLogCount.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class QueryExecuteStampSheetLogResult(core.Gs2Result):
    items: List[ExecuteStampSheetLog] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[ExecuteStampSheetLog]) -> QueryExecuteStampSheetLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> QueryExecuteStampSheetLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> QueryExecuteStampSheetLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> QueryExecuteStampSheetLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryExecuteStampSheetLogResult]:
        if data is None:
            return None
        return QueryExecuteStampSheetLogResult()\
            .with_items(None if data.get('items') is None else [
                ExecuteStampSheetLog.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class CountExecuteStampSheetLogResult(core.Gs2Result):
    items: List[ExecuteStampSheetLogCount] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[ExecuteStampSheetLogCount]) -> CountExecuteStampSheetLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> CountExecuteStampSheetLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> CountExecuteStampSheetLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> CountExecuteStampSheetLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CountExecuteStampSheetLogResult]:
        if data is None:
            return None
        return CountExecuteStampSheetLogResult()\
            .with_items(None if data.get('items') is None else [
                ExecuteStampSheetLogCount.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class QueryExecuteStampTaskLogResult(core.Gs2Result):
    items: List[ExecuteStampTaskLog] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[ExecuteStampTaskLog]) -> QueryExecuteStampTaskLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> QueryExecuteStampTaskLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> QueryExecuteStampTaskLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> QueryExecuteStampTaskLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryExecuteStampTaskLogResult]:
        if data is None:
            return None
        return QueryExecuteStampTaskLogResult()\
            .with_items(None if data.get('items') is None else [
                ExecuteStampTaskLog.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class CountExecuteStampTaskLogResult(core.Gs2Result):
    items: List[ExecuteStampTaskLogCount] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[ExecuteStampTaskLogCount]) -> CountExecuteStampTaskLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> CountExecuteStampTaskLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> CountExecuteStampTaskLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> CountExecuteStampTaskLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CountExecuteStampTaskLogResult]:
        if data is None:
            return None
        return CountExecuteStampTaskLogResult()\
            .with_items(None if data.get('items') is None else [
                ExecuteStampTaskLogCount.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class QueryInGameLogResult(core.Gs2Result):
    items: List[InGameLog] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[InGameLog]) -> QueryInGameLogResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> QueryInGameLogResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> QueryInGameLogResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> QueryInGameLogResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryInGameLogResult]:
        if data is None:
            return None
        return QueryInGameLogResult()\
            .with_items(None if data.get('items') is None else [
                InGameLog.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class SendInGameLogResult(core.Gs2Result):
    item: InGameLog = None

    def with_item(self, item: InGameLog) -> SendInGameLogResult:
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
    ) -> Optional[SendInGameLogResult]:
        if data is None:
            return None
        return SendInGameLogResult()\
            .with_item(InGameLog.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class SendInGameLogByUserIdResult(core.Gs2Result):
    item: InGameLog = None

    def with_item(self, item: InGameLog) -> SendInGameLogByUserIdResult:
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
    ) -> Optional[SendInGameLogByUserIdResult]:
        if data is None:
            return None
        return SendInGameLogByUserIdResult()\
            .with_item(InGameLog.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class QueryAccessLogWithTelemetryResult(core.Gs2Result):
    items: List[AccessLogWithTelemetry] = None
    next_page_token: str = None
    total_count: int = None
    scan_size: int = None

    def with_items(self, items: List[AccessLogWithTelemetry]) -> QueryAccessLogWithTelemetryResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> QueryAccessLogWithTelemetryResult:
        self.next_page_token = next_page_token
        return self

    def with_total_count(self, total_count: int) -> QueryAccessLogWithTelemetryResult:
        self.total_count = total_count
        return self

    def with_scan_size(self, scan_size: int) -> QueryAccessLogWithTelemetryResult:
        self.scan_size = scan_size
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[QueryAccessLogWithTelemetryResult]:
        if data is None:
            return None
        return QueryAccessLogWithTelemetryResult()\
            .with_items(None if data.get('items') is None else [
                AccessLogWithTelemetry.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))\
            .with_total_count(data.get('totalCount'))\
            .with_scan_size(data.get('scanSize'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
            "totalCount": self.total_count,
            "scanSize": self.scan_size,
        }


class DescribeInsightsResult(core.Gs2Result):
    items: List[Insight] = None
    next_page_token: str = None

    def with_items(self, items: List[Insight]) -> DescribeInsightsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeInsightsResult:
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
    ) -> Optional[DescribeInsightsResult]:
        if data is None:
            return None
        return DescribeInsightsResult()\
            .with_items(None if data.get('items') is None else [
                Insight.from_dict(data.get('items')[i])
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


class CreateInsightResult(core.Gs2Result):
    item: Insight = None

    def with_item(self, item: Insight) -> CreateInsightResult:
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
    ) -> Optional[CreateInsightResult]:
        if data is None:
            return None
        return CreateInsightResult()\
            .with_item(Insight.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetInsightResult(core.Gs2Result):
    item: Insight = None

    def with_item(self, item: Insight) -> GetInsightResult:
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
    ) -> Optional[GetInsightResult]:
        if data is None:
            return None
        return GetInsightResult()\
            .with_item(Insight.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteInsightResult(core.Gs2Result):
    item: Insight = None

    def with_item(self, item: Insight) -> DeleteInsightResult:
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
    ) -> Optional[DeleteInsightResult]:
        if data is None:
            return None
        return DeleteInsightResult()\
            .with_item(Insight.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }