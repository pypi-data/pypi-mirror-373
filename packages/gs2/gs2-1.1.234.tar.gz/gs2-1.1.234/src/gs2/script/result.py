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


class DescribeScriptsResult(core.Gs2Result):
    items: List[Script] = None
    next_page_token: str = None

    def with_items(self, items: List[Script]) -> DescribeScriptsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeScriptsResult:
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
    ) -> Optional[DescribeScriptsResult]:
        if data is None:
            return None
        return DescribeScriptsResult()\
            .with_items(None if data.get('items') is None else [
                Script.from_dict(data.get('items')[i])
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


class CreateScriptResult(core.Gs2Result):
    item: Script = None

    def with_item(self, item: Script) -> CreateScriptResult:
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
    ) -> Optional[CreateScriptResult]:
        if data is None:
            return None
        return CreateScriptResult()\
            .with_item(Script.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class CreateScriptFromGitHubResult(core.Gs2Result):
    item: Script = None

    def with_item(self, item: Script) -> CreateScriptFromGitHubResult:
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
    ) -> Optional[CreateScriptFromGitHubResult]:
        if data is None:
            return None
        return CreateScriptFromGitHubResult()\
            .with_item(Script.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetScriptResult(core.Gs2Result):
    item: Script = None

    def with_item(self, item: Script) -> GetScriptResult:
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
    ) -> Optional[GetScriptResult]:
        if data is None:
            return None
        return GetScriptResult()\
            .with_item(Script.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateScriptResult(core.Gs2Result):
    item: Script = None

    def with_item(self, item: Script) -> UpdateScriptResult:
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
    ) -> Optional[UpdateScriptResult]:
        if data is None:
            return None
        return UpdateScriptResult()\
            .with_item(Script.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateScriptFromGitHubResult(core.Gs2Result):
    item: Script = None

    def with_item(self, item: Script) -> UpdateScriptFromGitHubResult:
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
    ) -> Optional[UpdateScriptFromGitHubResult]:
        if data is None:
            return None
        return UpdateScriptFromGitHubResult()\
            .with_item(Script.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteScriptResult(core.Gs2Result):
    item: Script = None

    def with_item(self, item: Script) -> DeleteScriptResult:
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
    ) -> Optional[DeleteScriptResult]:
        if data is None:
            return None
        return DeleteScriptResult()\
            .with_item(Script.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class InvokeScriptResult(core.Gs2Result):
    code: int = None
    result: str = None
    transaction: Transaction = None
    random_status: RandomStatus = None
    atomic_commit: bool = None
    transaction_result: TransactionResult = None
    execute_time: int = None
    charged: int = None
    output: List[str] = None

    def with_code(self, code: int) -> InvokeScriptResult:
        self.code = code
        return self

    def with_result(self, result: str) -> InvokeScriptResult:
        self.result = result
        return self

    def with_transaction(self, transaction: Transaction) -> InvokeScriptResult:
        self.transaction = transaction
        return self

    def with_random_status(self, random_status: RandomStatus) -> InvokeScriptResult:
        self.random_status = random_status
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> InvokeScriptResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> InvokeScriptResult:
        self.transaction_result = transaction_result
        return self

    def with_execute_time(self, execute_time: int) -> InvokeScriptResult:
        self.execute_time = execute_time
        return self

    def with_charged(self, charged: int) -> InvokeScriptResult:
        self.charged = charged
        return self

    def with_output(self, output: List[str]) -> InvokeScriptResult:
        self.output = output
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[InvokeScriptResult]:
        if data is None:
            return None
        return InvokeScriptResult()\
            .with_code(data.get('code'))\
            .with_result(data.get('result'))\
            .with_transaction(Transaction.from_dict(data.get('transaction')))\
            .with_random_status(RandomStatus.from_dict(data.get('randomStatus')))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))\
            .with_execute_time(data.get('executeTime'))\
            .with_charged(data.get('charged'))\
            .with_output(None if data.get('output') is None else [
                data.get('output')[i]
                for i in range(len(data.get('output')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "result": self.result,
            "transaction": self.transaction.to_dict() if self.transaction else None,
            "randomStatus": self.random_status.to_dict() if self.random_status else None,
            "atomicCommit": self.atomic_commit,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
            "executeTime": self.execute_time,
            "charged": self.charged,
            "output": None if self.output is None else [
                self.output[i]
                for i in range(len(self.output))
            ],
        }


class DebugInvokeResult(core.Gs2Result):
    code: int = None
    result: str = None
    transaction: Transaction = None
    random_status: RandomStatus = None
    atomic_commit: bool = None
    transaction_result: TransactionResult = None
    execute_time: int = None
    charged: int = None
    output: List[str] = None

    def with_code(self, code: int) -> DebugInvokeResult:
        self.code = code
        return self

    def with_result(self, result: str) -> DebugInvokeResult:
        self.result = result
        return self

    def with_transaction(self, transaction: Transaction) -> DebugInvokeResult:
        self.transaction = transaction
        return self

    def with_random_status(self, random_status: RandomStatus) -> DebugInvokeResult:
        self.random_status = random_status
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> DebugInvokeResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> DebugInvokeResult:
        self.transaction_result = transaction_result
        return self

    def with_execute_time(self, execute_time: int) -> DebugInvokeResult:
        self.execute_time = execute_time
        return self

    def with_charged(self, charged: int) -> DebugInvokeResult:
        self.charged = charged
        return self

    def with_output(self, output: List[str]) -> DebugInvokeResult:
        self.output = output
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DebugInvokeResult]:
        if data is None:
            return None
        return DebugInvokeResult()\
            .with_code(data.get('code'))\
            .with_result(data.get('result'))\
            .with_transaction(Transaction.from_dict(data.get('transaction')))\
            .with_random_status(RandomStatus.from_dict(data.get('randomStatus')))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))\
            .with_execute_time(data.get('executeTime'))\
            .with_charged(data.get('charged'))\
            .with_output(None if data.get('output') is None else [
                data.get('output')[i]
                for i in range(len(data.get('output')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "result": self.result,
            "transaction": self.transaction.to_dict() if self.transaction else None,
            "randomStatus": self.random_status.to_dict() if self.random_status else None,
            "atomicCommit": self.atomic_commit,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
            "executeTime": self.execute_time,
            "charged": self.charged,
            "output": None if self.output is None else [
                self.output[i]
                for i in range(len(self.output))
            ],
        }


class InvokeByStampSheetResult(core.Gs2Result):
    code: int = None
    result: str = None
    transaction: Transaction = None
    random_status: RandomStatus = None
    atomic_commit: bool = None
    transaction_result: TransactionResult = None
    execute_time: int = None
    charged: int = None
    output: List[str] = None

    def with_code(self, code: int) -> InvokeByStampSheetResult:
        self.code = code
        return self

    def with_result(self, result: str) -> InvokeByStampSheetResult:
        self.result = result
        return self

    def with_transaction(self, transaction: Transaction) -> InvokeByStampSheetResult:
        self.transaction = transaction
        return self

    def with_random_status(self, random_status: RandomStatus) -> InvokeByStampSheetResult:
        self.random_status = random_status
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> InvokeByStampSheetResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> InvokeByStampSheetResult:
        self.transaction_result = transaction_result
        return self

    def with_execute_time(self, execute_time: int) -> InvokeByStampSheetResult:
        self.execute_time = execute_time
        return self

    def with_charged(self, charged: int) -> InvokeByStampSheetResult:
        self.charged = charged
        return self

    def with_output(self, output: List[str]) -> InvokeByStampSheetResult:
        self.output = output
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[InvokeByStampSheetResult]:
        if data is None:
            return None
        return InvokeByStampSheetResult()\
            .with_code(data.get('code'))\
            .with_result(data.get('result'))\
            .with_transaction(Transaction.from_dict(data.get('transaction')))\
            .with_random_status(RandomStatus.from_dict(data.get('randomStatus')))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))\
            .with_execute_time(data.get('executeTime'))\
            .with_charged(data.get('charged'))\
            .with_output(None if data.get('output') is None else [
                data.get('output')[i]
                for i in range(len(data.get('output')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "result": self.result,
            "transaction": self.transaction.to_dict() if self.transaction else None,
            "randomStatus": self.random_status.to_dict() if self.random_status else None,
            "atomicCommit": self.atomic_commit,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
            "executeTime": self.execute_time,
            "charged": self.charged,
            "output": None if self.output is None else [
                self.output[i]
                for i in range(len(self.output))
            ],
        }