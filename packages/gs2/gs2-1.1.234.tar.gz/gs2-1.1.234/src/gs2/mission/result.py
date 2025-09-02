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


class DescribeCompletesResult(core.Gs2Result):
    items: List[Complete] = None
    next_page_token: str = None

    def with_items(self, items: List[Complete]) -> DescribeCompletesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeCompletesResult:
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
    ) -> Optional[DescribeCompletesResult]:
        if data is None:
            return None
        return DescribeCompletesResult()\
            .with_items(None if data.get('items') is None else [
                Complete.from_dict(data.get('items')[i])
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


class DescribeCompletesByUserIdResult(core.Gs2Result):
    items: List[Complete] = None
    next_page_token: str = None

    def with_items(self, items: List[Complete]) -> DescribeCompletesByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeCompletesByUserIdResult:
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
    ) -> Optional[DescribeCompletesByUserIdResult]:
        if data is None:
            return None
        return DescribeCompletesByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Complete.from_dict(data.get('items')[i])
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


class CompleteResult(core.Gs2Result):
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_transaction_id(self, transaction_id: str) -> CompleteResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> CompleteResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> CompleteResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> CompleteResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> CompleteResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> CompleteResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> CompleteResult:
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
    ) -> Optional[CompleteResult]:
        if data is None:
            return None
        return CompleteResult()\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class CompleteByUserIdResult(core.Gs2Result):
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_transaction_id(self, transaction_id: str) -> CompleteByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> CompleteByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> CompleteByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> CompleteByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> CompleteByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> CompleteByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> CompleteByUserIdResult:
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
    ) -> Optional[CompleteByUserIdResult]:
        if data is None:
            return None
        return CompleteByUserIdResult()\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class BatchCompleteResult(core.Gs2Result):
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_transaction_id(self, transaction_id: str) -> BatchCompleteResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> BatchCompleteResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> BatchCompleteResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> BatchCompleteResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> BatchCompleteResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> BatchCompleteResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> BatchCompleteResult:
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
    ) -> Optional[BatchCompleteResult]:
        if data is None:
            return None
        return BatchCompleteResult()\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class BatchCompleteByUserIdResult(core.Gs2Result):
    transaction_id: str = None
    stamp_sheet: str = None
    stamp_sheet_encryption_key_id: str = None
    auto_run_stamp_sheet: bool = None
    atomic_commit: bool = None
    transaction: str = None
    transaction_result: TransactionResult = None

    def with_transaction_id(self, transaction_id: str) -> BatchCompleteByUserIdResult:
        self.transaction_id = transaction_id
        return self

    def with_stamp_sheet(self, stamp_sheet: str) -> BatchCompleteByUserIdResult:
        self.stamp_sheet = stamp_sheet
        return self

    def with_stamp_sheet_encryption_key_id(self, stamp_sheet_encryption_key_id: str) -> BatchCompleteByUserIdResult:
        self.stamp_sheet_encryption_key_id = stamp_sheet_encryption_key_id
        return self

    def with_auto_run_stamp_sheet(self, auto_run_stamp_sheet: bool) -> BatchCompleteByUserIdResult:
        self.auto_run_stamp_sheet = auto_run_stamp_sheet
        return self

    def with_atomic_commit(self, atomic_commit: bool) -> BatchCompleteByUserIdResult:
        self.atomic_commit = atomic_commit
        return self

    def with_transaction(self, transaction: str) -> BatchCompleteByUserIdResult:
        self.transaction = transaction
        return self

    def with_transaction_result(self, transaction_result: TransactionResult) -> BatchCompleteByUserIdResult:
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
    ) -> Optional[BatchCompleteByUserIdResult]:
        if data is None:
            return None
        return BatchCompleteByUserIdResult()\
            .with_transaction_id(data.get('transactionId'))\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_stamp_sheet_encryption_key_id(data.get('stampSheetEncryptionKeyId'))\
            .with_auto_run_stamp_sheet(data.get('autoRunStampSheet'))\
            .with_atomic_commit(data.get('atomicCommit'))\
            .with_transaction(data.get('transaction'))\
            .with_transaction_result(TransactionResult.from_dict(data.get('transactionResult')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "stampSheet": self.stamp_sheet,
            "stampSheetEncryptionKeyId": self.stamp_sheet_encryption_key_id,
            "autoRunStampSheet": self.auto_run_stamp_sheet,
            "atomicCommit": self.atomic_commit,
            "transaction": self.transaction,
            "transactionResult": self.transaction_result.to_dict() if self.transaction_result else None,
        }


class ReceiveByUserIdResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> ReceiveByUserIdResult:
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
    ) -> Optional[ReceiveByUserIdResult]:
        if data is None:
            return None
        return ReceiveByUserIdResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class BatchReceiveByUserIdResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> BatchReceiveByUserIdResult:
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
    ) -> Optional[BatchReceiveByUserIdResult]:
        if data is None:
            return None
        return BatchReceiveByUserIdResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class RevertReceiveByUserIdResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> RevertReceiveByUserIdResult:
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
    ) -> Optional[RevertReceiveByUserIdResult]:
        if data is None:
            return None
        return RevertReceiveByUserIdResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCompleteResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> GetCompleteResult:
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
    ) -> Optional[GetCompleteResult]:
        if data is None:
            return None
        return GetCompleteResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCompleteByUserIdResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> GetCompleteByUserIdResult:
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
    ) -> Optional[GetCompleteByUserIdResult]:
        if data is None:
            return None
        return GetCompleteByUserIdResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class EvaluateCompleteResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> EvaluateCompleteResult:
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
    ) -> Optional[EvaluateCompleteResult]:
        if data is None:
            return None
        return EvaluateCompleteResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class EvaluateCompleteByUserIdResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> EvaluateCompleteByUserIdResult:
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
    ) -> Optional[EvaluateCompleteByUserIdResult]:
        if data is None:
            return None
        return EvaluateCompleteByUserIdResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteCompleteByUserIdResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> DeleteCompleteByUserIdResult:
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
    ) -> Optional[DeleteCompleteByUserIdResult]:
        if data is None:
            return None
        return DeleteCompleteByUserIdResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyCompleteResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> VerifyCompleteResult:
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
    ) -> Optional[VerifyCompleteResult]:
        if data is None:
            return None
        return VerifyCompleteResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyCompleteByUserIdResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> VerifyCompleteByUserIdResult:
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
    ) -> Optional[VerifyCompleteByUserIdResult]:
        if data is None:
            return None
        return VerifyCompleteByUserIdResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ReceiveByStampTaskResult(core.Gs2Result):
    item: Complete = None
    new_context_stack: str = None

    def with_item(self, item: Complete) -> ReceiveByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> ReceiveByStampTaskResult:
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
    ) -> Optional[ReceiveByStampTaskResult]:
        if data is None:
            return None
        return ReceiveByStampTaskResult()\
            .with_item(Complete.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class BatchReceiveByStampTaskResult(core.Gs2Result):
    item: Complete = None
    new_context_stack: str = None

    def with_item(self, item: Complete) -> BatchReceiveByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> BatchReceiveByStampTaskResult:
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
    ) -> Optional[BatchReceiveByStampTaskResult]:
        if data is None:
            return None
        return BatchReceiveByStampTaskResult()\
            .with_item(Complete.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class RevertReceiveByStampSheetResult(core.Gs2Result):
    item: Complete = None

    def with_item(self, item: Complete) -> RevertReceiveByStampSheetResult:
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
    ) -> Optional[RevertReceiveByStampSheetResult]:
        if data is None:
            return None
        return RevertReceiveByStampSheetResult()\
            .with_item(Complete.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyCompleteByStampTaskResult(core.Gs2Result):
    item: Complete = None
    new_context_stack: str = None

    def with_item(self, item: Complete) -> VerifyCompleteByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyCompleteByStampTaskResult:
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
    ) -> Optional[VerifyCompleteByStampTaskResult]:
        if data is None:
            return None
        return VerifyCompleteByStampTaskResult()\
            .with_item(Complete.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class DescribeCounterModelMastersResult(core.Gs2Result):
    items: List[CounterModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[CounterModelMaster]) -> DescribeCounterModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeCounterModelMastersResult:
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
    ) -> Optional[DescribeCounterModelMastersResult]:
        if data is None:
            return None
        return DescribeCounterModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                CounterModelMaster.from_dict(data.get('items')[i])
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


class CreateCounterModelMasterResult(core.Gs2Result):
    item: CounterModelMaster = None

    def with_item(self, item: CounterModelMaster) -> CreateCounterModelMasterResult:
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
    ) -> Optional[CreateCounterModelMasterResult]:
        if data is None:
            return None
        return CreateCounterModelMasterResult()\
            .with_item(CounterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCounterModelMasterResult(core.Gs2Result):
    item: CounterModelMaster = None

    def with_item(self, item: CounterModelMaster) -> GetCounterModelMasterResult:
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
    ) -> Optional[GetCounterModelMasterResult]:
        if data is None:
            return None
        return GetCounterModelMasterResult()\
            .with_item(CounterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCounterModelMasterResult(core.Gs2Result):
    item: CounterModelMaster = None

    def with_item(self, item: CounterModelMaster) -> UpdateCounterModelMasterResult:
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
    ) -> Optional[UpdateCounterModelMasterResult]:
        if data is None:
            return None
        return UpdateCounterModelMasterResult()\
            .with_item(CounterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteCounterModelMasterResult(core.Gs2Result):
    item: CounterModelMaster = None

    def with_item(self, item: CounterModelMaster) -> DeleteCounterModelMasterResult:
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
    ) -> Optional[DeleteCounterModelMasterResult]:
        if data is None:
            return None
        return DeleteCounterModelMasterResult()\
            .with_item(CounterModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeMissionGroupModelMastersResult(core.Gs2Result):
    items: List[MissionGroupModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[MissionGroupModelMaster]) -> DescribeMissionGroupModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeMissionGroupModelMastersResult:
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
    ) -> Optional[DescribeMissionGroupModelMastersResult]:
        if data is None:
            return None
        return DescribeMissionGroupModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                MissionGroupModelMaster.from_dict(data.get('items')[i])
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


class CreateMissionGroupModelMasterResult(core.Gs2Result):
    item: MissionGroupModelMaster = None

    def with_item(self, item: MissionGroupModelMaster) -> CreateMissionGroupModelMasterResult:
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
    ) -> Optional[CreateMissionGroupModelMasterResult]:
        if data is None:
            return None
        return CreateMissionGroupModelMasterResult()\
            .with_item(MissionGroupModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetMissionGroupModelMasterResult(core.Gs2Result):
    item: MissionGroupModelMaster = None

    def with_item(self, item: MissionGroupModelMaster) -> GetMissionGroupModelMasterResult:
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
    ) -> Optional[GetMissionGroupModelMasterResult]:
        if data is None:
            return None
        return GetMissionGroupModelMasterResult()\
            .with_item(MissionGroupModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateMissionGroupModelMasterResult(core.Gs2Result):
    item: MissionGroupModelMaster = None

    def with_item(self, item: MissionGroupModelMaster) -> UpdateMissionGroupModelMasterResult:
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
    ) -> Optional[UpdateMissionGroupModelMasterResult]:
        if data is None:
            return None
        return UpdateMissionGroupModelMasterResult()\
            .with_item(MissionGroupModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteMissionGroupModelMasterResult(core.Gs2Result):
    item: MissionGroupModelMaster = None

    def with_item(self, item: MissionGroupModelMaster) -> DeleteMissionGroupModelMasterResult:
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
    ) -> Optional[DeleteMissionGroupModelMasterResult]:
        if data is None:
            return None
        return DeleteMissionGroupModelMasterResult()\
            .with_item(MissionGroupModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


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


class DescribeCountersResult(core.Gs2Result):
    items: List[Counter] = None
    next_page_token: str = None

    def with_items(self, items: List[Counter]) -> DescribeCountersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeCountersResult:
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
    ) -> Optional[DescribeCountersResult]:
        if data is None:
            return None
        return DescribeCountersResult()\
            .with_items(None if data.get('items') is None else [
                Counter.from_dict(data.get('items')[i])
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


class DescribeCountersByUserIdResult(core.Gs2Result):
    items: List[Counter] = None
    next_page_token: str = None

    def with_items(self, items: List[Counter]) -> DescribeCountersByUserIdResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeCountersByUserIdResult:
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
    ) -> Optional[DescribeCountersByUserIdResult]:
        if data is None:
            return None
        return DescribeCountersByUserIdResult()\
            .with_items(None if data.get('items') is None else [
                Counter.from_dict(data.get('items')[i])
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


class IncreaseCounterByUserIdResult(core.Gs2Result):
    item: Counter = None
    changed_completes: List[Complete] = None

    def with_item(self, item: Counter) -> IncreaseCounterByUserIdResult:
        self.item = item
        return self

    def with_changed_completes(self, changed_completes: List[Complete]) -> IncreaseCounterByUserIdResult:
        self.changed_completes = changed_completes
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[IncreaseCounterByUserIdResult]:
        if data is None:
            return None
        return IncreaseCounterByUserIdResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_changed_completes(None if data.get('changedCompletes') is None else [
                Complete.from_dict(data.get('changedCompletes')[i])
                for i in range(len(data.get('changedCompletes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "changedCompletes": None if self.changed_completes is None else [
                self.changed_completes[i].to_dict() if self.changed_completes[i] else None
                for i in range(len(self.changed_completes))
            ],
        }


class SetCounterByUserIdResult(core.Gs2Result):
    item: Counter = None
    old: Counter = None
    changed_completes: List[Complete] = None

    def with_item(self, item: Counter) -> SetCounterByUserIdResult:
        self.item = item
        return self

    def with_old(self, old: Counter) -> SetCounterByUserIdResult:
        self.old = old
        return self

    def with_changed_completes(self, changed_completes: List[Complete]) -> SetCounterByUserIdResult:
        self.changed_completes = changed_completes
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetCounterByUserIdResult]:
        if data is None:
            return None
        return SetCounterByUserIdResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_old(Counter.from_dict(data.get('old')))\
            .with_changed_completes(None if data.get('changedCompletes') is None else [
                Complete.from_dict(data.get('changedCompletes')[i])
                for i in range(len(data.get('changedCompletes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "changedCompletes": None if self.changed_completes is None else [
                self.changed_completes[i].to_dict() if self.changed_completes[i] else None
                for i in range(len(self.changed_completes))
            ],
        }


class DecreaseCounterResult(core.Gs2Result):
    item: Counter = None
    changed_completes: List[Complete] = None

    def with_item(self, item: Counter) -> DecreaseCounterResult:
        self.item = item
        return self

    def with_changed_completes(self, changed_completes: List[Complete]) -> DecreaseCounterResult:
        self.changed_completes = changed_completes
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecreaseCounterResult]:
        if data is None:
            return None
        return DecreaseCounterResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_changed_completes(None if data.get('changedCompletes') is None else [
                Complete.from_dict(data.get('changedCompletes')[i])
                for i in range(len(data.get('changedCompletes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "changedCompletes": None if self.changed_completes is None else [
                self.changed_completes[i].to_dict() if self.changed_completes[i] else None
                for i in range(len(self.changed_completes))
            ],
        }


class DecreaseCounterByUserIdResult(core.Gs2Result):
    item: Counter = None
    changed_completes: List[Complete] = None

    def with_item(self, item: Counter) -> DecreaseCounterByUserIdResult:
        self.item = item
        return self

    def with_changed_completes(self, changed_completes: List[Complete]) -> DecreaseCounterByUserIdResult:
        self.changed_completes = changed_completes
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DecreaseCounterByUserIdResult]:
        if data is None:
            return None
        return DecreaseCounterByUserIdResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_changed_completes(None if data.get('changedCompletes') is None else [
                Complete.from_dict(data.get('changedCompletes')[i])
                for i in range(len(data.get('changedCompletes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "changedCompletes": None if self.changed_completes is None else [
                self.changed_completes[i].to_dict() if self.changed_completes[i] else None
                for i in range(len(self.changed_completes))
            ],
        }


class GetCounterResult(core.Gs2Result):
    item: Counter = None

    def with_item(self, item: Counter) -> GetCounterResult:
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
    ) -> Optional[GetCounterResult]:
        if data is None:
            return None
        return GetCounterResult()\
            .with_item(Counter.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCounterByUserIdResult(core.Gs2Result):
    item: Counter = None

    def with_item(self, item: Counter) -> GetCounterByUserIdResult:
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
    ) -> Optional[GetCounterByUserIdResult]:
        if data is None:
            return None
        return GetCounterByUserIdResult()\
            .with_item(Counter.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyCounterValueResult(core.Gs2Result):
    item: Counter = None

    def with_item(self, item: Counter) -> VerifyCounterValueResult:
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
    ) -> Optional[VerifyCounterValueResult]:
        if data is None:
            return None
        return VerifyCounterValueResult()\
            .with_item(Counter.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class VerifyCounterValueByUserIdResult(core.Gs2Result):
    item: Counter = None

    def with_item(self, item: Counter) -> VerifyCounterValueByUserIdResult:
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
    ) -> Optional[VerifyCounterValueByUserIdResult]:
        if data is None:
            return None
        return VerifyCounterValueByUserIdResult()\
            .with_item(Counter.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ResetCounterResult(core.Gs2Result):
    item: Counter = None

    def with_item(self, item: Counter) -> ResetCounterResult:
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
    ) -> Optional[ResetCounterResult]:
        if data is None:
            return None
        return ResetCounterResult()\
            .with_item(Counter.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ResetCounterByUserIdResult(core.Gs2Result):
    item: Counter = None

    def with_item(self, item: Counter) -> ResetCounterByUserIdResult:
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
    ) -> Optional[ResetCounterByUserIdResult]:
        if data is None:
            return None
        return ResetCounterByUserIdResult()\
            .with_item(Counter.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteCounterResult(core.Gs2Result):
    item: Counter = None

    def with_item(self, item: Counter) -> DeleteCounterResult:
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
    ) -> Optional[DeleteCounterResult]:
        if data is None:
            return None
        return DeleteCounterResult()\
            .with_item(Counter.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteCounterByUserIdResult(core.Gs2Result):
    item: Counter = None

    def with_item(self, item: Counter) -> DeleteCounterByUserIdResult:
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
    ) -> Optional[DeleteCounterByUserIdResult]:
        if data is None:
            return None
        return DeleteCounterByUserIdResult()\
            .with_item(Counter.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class IncreaseByStampSheetResult(core.Gs2Result):
    item: Counter = None
    changed_completes: List[Complete] = None

    def with_item(self, item: Counter) -> IncreaseByStampSheetResult:
        self.item = item
        return self

    def with_changed_completes(self, changed_completes: List[Complete]) -> IncreaseByStampSheetResult:
        self.changed_completes = changed_completes
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[IncreaseByStampSheetResult]:
        if data is None:
            return None
        return IncreaseByStampSheetResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_changed_completes(None if data.get('changedCompletes') is None else [
                Complete.from_dict(data.get('changedCompletes')[i])
                for i in range(len(data.get('changedCompletes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "changedCompletes": None if self.changed_completes is None else [
                self.changed_completes[i].to_dict() if self.changed_completes[i] else None
                for i in range(len(self.changed_completes))
            ],
        }


class SetByStampSheetResult(core.Gs2Result):
    item: Counter = None
    old: Counter = None
    changed_completes: List[Complete] = None

    def with_item(self, item: Counter) -> SetByStampSheetResult:
        self.item = item
        return self

    def with_old(self, old: Counter) -> SetByStampSheetResult:
        self.old = old
        return self

    def with_changed_completes(self, changed_completes: List[Complete]) -> SetByStampSheetResult:
        self.changed_completes = changed_completes
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SetByStampSheetResult]:
        if data is None:
            return None
        return SetByStampSheetResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_old(Counter.from_dict(data.get('old')))\
            .with_changed_completes(None if data.get('changedCompletes') is None else [
                Complete.from_dict(data.get('changedCompletes')[i])
                for i in range(len(data.get('changedCompletes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "old": self.old.to_dict() if self.old else None,
            "changedCompletes": None if self.changed_completes is None else [
                self.changed_completes[i].to_dict() if self.changed_completes[i] else None
                for i in range(len(self.changed_completes))
            ],
        }


class DecreaseByStampTaskResult(core.Gs2Result):
    item: Counter = None
    changed_completes: List[Complete] = None
    new_context_stack: str = None

    def with_item(self, item: Counter) -> DecreaseByStampTaskResult:
        self.item = item
        return self

    def with_changed_completes(self, changed_completes: List[Complete]) -> DecreaseByStampTaskResult:
        self.changed_completes = changed_completes
        return self

    def with_new_context_stack(self, new_context_stack: str) -> DecreaseByStampTaskResult:
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
    ) -> Optional[DecreaseByStampTaskResult]:
        if data is None:
            return None
        return DecreaseByStampTaskResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_changed_completes(None if data.get('changedCompletes') is None else [
                Complete.from_dict(data.get('changedCompletes')[i])
                for i in range(len(data.get('changedCompletes')))
            ])\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "changedCompletes": None if self.changed_completes is None else [
                self.changed_completes[i].to_dict() if self.changed_completes[i] else None
                for i in range(len(self.changed_completes))
            ],
            "newContextStack": self.new_context_stack,
        }


class ResetByStampTaskResult(core.Gs2Result):
    item: Counter = None
    new_context_stack: str = None

    def with_item(self, item: Counter) -> ResetByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> ResetByStampTaskResult:
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
    ) -> Optional[ResetByStampTaskResult]:
        if data is None:
            return None
        return ResetByStampTaskResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class VerifyCounterValueByStampTaskResult(core.Gs2Result):
    item: Counter = None
    new_context_stack: str = None

    def with_item(self, item: Counter) -> VerifyCounterValueByStampTaskResult:
        self.item = item
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyCounterValueByStampTaskResult:
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
    ) -> Optional[VerifyCounterValueByStampTaskResult]:
        if data is None:
            return None
        return VerifyCounterValueByStampTaskResult()\
            .with_item(Counter.from_dict(data.get('item')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "newContextStack": self.new_context_stack,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentMissionMaster = None

    def with_item(self, item: CurrentMissionMaster) -> ExportMasterResult:
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
            .with_item(CurrentMissionMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentMissionMasterResult(core.Gs2Result):
    item: CurrentMissionMaster = None

    def with_item(self, item: CurrentMissionMaster) -> GetCurrentMissionMasterResult:
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
    ) -> Optional[GetCurrentMissionMasterResult]:
        if data is None:
            return None
        return GetCurrentMissionMasterResult()\
            .with_item(CurrentMissionMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentMissionMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentMissionMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentMissionMasterResult:
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
    ) -> Optional[PreUpdateCurrentMissionMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentMissionMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentMissionMasterResult(core.Gs2Result):
    item: CurrentMissionMaster = None

    def with_item(self, item: CurrentMissionMaster) -> UpdateCurrentMissionMasterResult:
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
    ) -> Optional[UpdateCurrentMissionMasterResult]:
        if data is None:
            return None
        return UpdateCurrentMissionMasterResult()\
            .with_item(CurrentMissionMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentMissionMasterFromGitHubResult(core.Gs2Result):
    item: CurrentMissionMaster = None

    def with_item(self, item: CurrentMissionMaster) -> UpdateCurrentMissionMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentMissionMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentMissionMasterFromGitHubResult()\
            .with_item(CurrentMissionMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeCounterModelsResult(core.Gs2Result):
    items: List[CounterModel] = None

    def with_items(self, items: List[CounterModel]) -> DescribeCounterModelsResult:
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
    ) -> Optional[DescribeCounterModelsResult]:
        if data is None:
            return None
        return DescribeCounterModelsResult()\
            .with_items(None if data.get('items') is None else [
                CounterModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetCounterModelResult(core.Gs2Result):
    item: CounterModel = None

    def with_item(self, item: CounterModel) -> GetCounterModelResult:
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
    ) -> Optional[GetCounterModelResult]:
        if data is None:
            return None
        return GetCounterModelResult()\
            .with_item(CounterModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeMissionGroupModelsResult(core.Gs2Result):
    items: List[MissionGroupModel] = None

    def with_items(self, items: List[MissionGroupModel]) -> DescribeMissionGroupModelsResult:
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
    ) -> Optional[DescribeMissionGroupModelsResult]:
        if data is None:
            return None
        return DescribeMissionGroupModelsResult()\
            .with_items(None if data.get('items') is None else [
                MissionGroupModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetMissionGroupModelResult(core.Gs2Result):
    item: MissionGroupModel = None

    def with_item(self, item: MissionGroupModel) -> GetMissionGroupModelResult:
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
    ) -> Optional[GetMissionGroupModelResult]:
        if data is None:
            return None
        return GetMissionGroupModelResult()\
            .with_item(MissionGroupModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeMissionTaskModelsResult(core.Gs2Result):
    items: List[MissionTaskModel] = None

    def with_items(self, items: List[MissionTaskModel]) -> DescribeMissionTaskModelsResult:
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
    ) -> Optional[DescribeMissionTaskModelsResult]:
        if data is None:
            return None
        return DescribeMissionTaskModelsResult()\
            .with_items(None if data.get('items') is None else [
                MissionTaskModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetMissionTaskModelResult(core.Gs2Result):
    item: MissionTaskModel = None

    def with_item(self, item: MissionTaskModel) -> GetMissionTaskModelResult:
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
    ) -> Optional[GetMissionTaskModelResult]:
        if data is None:
            return None
        return GetMissionTaskModelResult()\
            .with_item(MissionTaskModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeMissionTaskModelMastersResult(core.Gs2Result):
    items: List[MissionTaskModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[MissionTaskModelMaster]) -> DescribeMissionTaskModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeMissionTaskModelMastersResult:
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
    ) -> Optional[DescribeMissionTaskModelMastersResult]:
        if data is None:
            return None
        return DescribeMissionTaskModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                MissionTaskModelMaster.from_dict(data.get('items')[i])
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


class CreateMissionTaskModelMasterResult(core.Gs2Result):
    item: MissionTaskModelMaster = None

    def with_item(self, item: MissionTaskModelMaster) -> CreateMissionTaskModelMasterResult:
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
    ) -> Optional[CreateMissionTaskModelMasterResult]:
        if data is None:
            return None
        return CreateMissionTaskModelMasterResult()\
            .with_item(MissionTaskModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetMissionTaskModelMasterResult(core.Gs2Result):
    item: MissionTaskModelMaster = None

    def with_item(self, item: MissionTaskModelMaster) -> GetMissionTaskModelMasterResult:
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
    ) -> Optional[GetMissionTaskModelMasterResult]:
        if data is None:
            return None
        return GetMissionTaskModelMasterResult()\
            .with_item(MissionTaskModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateMissionTaskModelMasterResult(core.Gs2Result):
    item: MissionTaskModelMaster = None

    def with_item(self, item: MissionTaskModelMaster) -> UpdateMissionTaskModelMasterResult:
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
    ) -> Optional[UpdateMissionTaskModelMasterResult]:
        if data is None:
            return None
        return UpdateMissionTaskModelMasterResult()\
            .with_item(MissionTaskModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteMissionTaskModelMasterResult(core.Gs2Result):
    item: MissionTaskModelMaster = None

    def with_item(self, item: MissionTaskModelMaster) -> DeleteMissionTaskModelMasterResult:
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
    ) -> Optional[DeleteMissionTaskModelMasterResult]:
        if data is None:
            return None
        return DeleteMissionTaskModelMasterResult()\
            .with_item(MissionTaskModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }