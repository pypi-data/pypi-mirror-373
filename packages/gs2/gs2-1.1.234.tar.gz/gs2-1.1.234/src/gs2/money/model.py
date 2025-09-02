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

import re
from typing import *
from gs2 import core


class LogSetting(core.Gs2Model):
    logging_namespace_id: str = None

    def with_logging_namespace_id(self, logging_namespace_id: str) -> LogSetting:
        self.logging_namespace_id = logging_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[LogSetting]:
        if data is None:
            return None
        return LogSetting()\
            .with_logging_namespace_id(data.get('loggingNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loggingNamespaceId": self.logging_namespace_id,
        }


class ScriptSetting(core.Gs2Model):
    trigger_script_id: str = None
    done_trigger_target_type: str = None
    done_trigger_script_id: str = None
    done_trigger_queue_namespace_id: str = None

    def with_trigger_script_id(self, trigger_script_id: str) -> ScriptSetting:
        self.trigger_script_id = trigger_script_id
        return self

    def with_done_trigger_target_type(self, done_trigger_target_type: str) -> ScriptSetting:
        self.done_trigger_target_type = done_trigger_target_type
        return self

    def with_done_trigger_script_id(self, done_trigger_script_id: str) -> ScriptSetting:
        self.done_trigger_script_id = done_trigger_script_id
        return self

    def with_done_trigger_queue_namespace_id(self, done_trigger_queue_namespace_id: str) -> ScriptSetting:
        self.done_trigger_queue_namespace_id = done_trigger_queue_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ScriptSetting]:
        if data is None:
            return None
        return ScriptSetting()\
            .with_trigger_script_id(data.get('triggerScriptId'))\
            .with_done_trigger_target_type(data.get('doneTriggerTargetType'))\
            .with_done_trigger_script_id(data.get('doneTriggerScriptId'))\
            .with_done_trigger_queue_namespace_id(data.get('doneTriggerQueueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "triggerScriptId": self.trigger_script_id,
            "doneTriggerTargetType": self.done_trigger_target_type,
            "doneTriggerScriptId": self.done_trigger_script_id,
            "doneTriggerQueueNamespaceId": self.done_trigger_queue_namespace_id,
        }


class WalletDetail(core.Gs2Model):
    price: float = None
    count: int = None

    def with_price(self, price: float) -> WalletDetail:
        self.price = price
        return self

    def with_count(self, count: int) -> WalletDetail:
        self.count = count
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WalletDetail]:
        if data is None:
            return None
        return WalletDetail()\
            .with_price(data.get('price'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "price": self.price,
            "count": self.count,
        }


class Receipt(core.Gs2Model):
    receipt_id: str = None
    transaction_id: str = None
    purchase_token: str = None
    user_id: str = None
    type: str = None
    slot: int = None
    price: float = None
    paid: int = None
    free: int = None
    total: int = None
    contents_id: str = None
    created_at: int = None
    revision: int = None

    def with_receipt_id(self, receipt_id: str) -> Receipt:
        self.receipt_id = receipt_id
        return self

    def with_transaction_id(self, transaction_id: str) -> Receipt:
        self.transaction_id = transaction_id
        return self

    def with_purchase_token(self, purchase_token: str) -> Receipt:
        self.purchase_token = purchase_token
        return self

    def with_user_id(self, user_id: str) -> Receipt:
        self.user_id = user_id
        return self

    def with_type(self, type: str) -> Receipt:
        self.type = type
        return self

    def with_slot(self, slot: int) -> Receipt:
        self.slot = slot
        return self

    def with_price(self, price: float) -> Receipt:
        self.price = price
        return self

    def with_paid(self, paid: int) -> Receipt:
        self.paid = paid
        return self

    def with_free(self, free: int) -> Receipt:
        self.free = free
        return self

    def with_total(self, total: int) -> Receipt:
        self.total = total
        return self

    def with_contents_id(self, contents_id: str) -> Receipt:
        self.contents_id = contents_id
        return self

    def with_created_at(self, created_at: int) -> Receipt:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Receipt:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        transaction_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:money:{namespaceName}:user:{userId}:receipt:{transactionId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            transactionId=transaction_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):receipt:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):receipt:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):receipt:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):receipt:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_transaction_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):receipt:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('transaction_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Receipt]:
        if data is None:
            return None
        return Receipt()\
            .with_receipt_id(data.get('receiptId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_purchase_token(data.get('purchaseToken'))\
            .with_user_id(data.get('userId'))\
            .with_type(data.get('type'))\
            .with_slot(data.get('slot'))\
            .with_price(data.get('price'))\
            .with_paid(data.get('paid'))\
            .with_free(data.get('free'))\
            .with_total(data.get('total'))\
            .with_contents_id(data.get('contentsId'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "receiptId": self.receipt_id,
            "transactionId": self.transaction_id,
            "purchaseToken": self.purchase_token,
            "userId": self.user_id,
            "type": self.type,
            "slot": self.slot,
            "price": self.price,
            "paid": self.paid,
            "free": self.free,
            "total": self.total,
            "contentsId": self.contents_id,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Wallet(core.Gs2Model):
    wallet_id: str = None
    user_id: str = None
    slot: int = None
    paid: int = None
    free: int = None
    detail: List[WalletDetail] = None
    share_free: bool = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_wallet_id(self, wallet_id: str) -> Wallet:
        self.wallet_id = wallet_id
        return self

    def with_user_id(self, user_id: str) -> Wallet:
        self.user_id = user_id
        return self

    def with_slot(self, slot: int) -> Wallet:
        self.slot = slot
        return self

    def with_paid(self, paid: int) -> Wallet:
        self.paid = paid
        return self

    def with_free(self, free: int) -> Wallet:
        self.free = free
        return self

    def with_detail(self, detail: List[WalletDetail]) -> Wallet:
        self.detail = detail
        return self

    def with_share_free(self, share_free: bool) -> Wallet:
        self.share_free = share_free
        return self

    def with_created_at(self, created_at: int) -> Wallet:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Wallet:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Wallet:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        slot,
    ):
        return 'grn:gs2:{region}:{ownerId}:money:{namespaceName}:user:{userId}:wallet:{slot}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            slot=slot,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):wallet:(?P<slot>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):wallet:(?P<slot>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):wallet:(?P<slot>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):wallet:(?P<slot>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_slot_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+):user:(?P<userId>.+):wallet:(?P<slot>.+)', grn)
        if match is None:
            return None
        return match.group('slot')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Wallet]:
        if data is None:
            return None
        return Wallet()\
            .with_wallet_id(data.get('walletId'))\
            .with_user_id(data.get('userId'))\
            .with_slot(data.get('slot'))\
            .with_paid(data.get('paid'))\
            .with_free(data.get('free'))\
            .with_detail(None if data.get('detail') is None else [
                WalletDetail.from_dict(data.get('detail')[i])
                for i in range(len(data.get('detail')))
            ])\
            .with_share_free(data.get('shareFree'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "walletId": self.wallet_id,
            "userId": self.user_id,
            "slot": self.slot,
            "paid": self.paid,
            "free": self.free,
            "detail": None if self.detail is None else [
                self.detail[i].to_dict() if self.detail[i] else None
                for i in range(len(self.detail))
            ],
            "shareFree": self.share_free,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    priority: str = None
    share_free: bool = None
    currency: str = None
    apple_key: str = None
    google_key: str = None
    enable_fake_receipt: bool = None
    create_wallet_script: ScriptSetting = None
    deposit_script: ScriptSetting = None
    withdraw_script: ScriptSetting = None
    balance: float = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_priority(self, priority: str) -> Namespace:
        self.priority = priority
        return self

    def with_share_free(self, share_free: bool) -> Namespace:
        self.share_free = share_free
        return self

    def with_currency(self, currency: str) -> Namespace:
        self.currency = currency
        return self

    def with_apple_key(self, apple_key: str) -> Namespace:
        self.apple_key = apple_key
        return self

    def with_google_key(self, google_key: str) -> Namespace:
        self.google_key = google_key
        return self

    def with_enable_fake_receipt(self, enable_fake_receipt: bool) -> Namespace:
        self.enable_fake_receipt = enable_fake_receipt
        return self

    def with_create_wallet_script(self, create_wallet_script: ScriptSetting) -> Namespace:
        self.create_wallet_script = create_wallet_script
        return self

    def with_deposit_script(self, deposit_script: ScriptSetting) -> Namespace:
        self.deposit_script = deposit_script
        return self

    def with_withdraw_script(self, withdraw_script: ScriptSetting) -> Namespace:
        self.withdraw_script = withdraw_script
        return self

    def with_balance(self, balance: float) -> Namespace:
        self.balance = balance
        return self

    def with_log_setting(self, log_setting: LogSetting) -> Namespace:
        self.log_setting = log_setting
        return self

    def with_created_at(self, created_at: int) -> Namespace:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Namespace:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Namespace:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:money:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):money:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Namespace]:
        if data is None:
            return None
        return Namespace()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_priority(data.get('priority'))\
            .with_share_free(data.get('shareFree'))\
            .with_currency(data.get('currency'))\
            .with_apple_key(data.get('appleKey'))\
            .with_google_key(data.get('googleKey'))\
            .with_enable_fake_receipt(data.get('enableFakeReceipt'))\
            .with_create_wallet_script(ScriptSetting.from_dict(data.get('createWalletScript')))\
            .with_deposit_script(ScriptSetting.from_dict(data.get('depositScript')))\
            .with_withdraw_script(ScriptSetting.from_dict(data.get('withdrawScript')))\
            .with_balance(data.get('balance'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "shareFree": self.share_free,
            "currency": self.currency,
            "appleKey": self.apple_key,
            "googleKey": self.google_key,
            "enableFakeReceipt": self.enable_fake_receipt,
            "createWalletScript": self.create_wallet_script.to_dict() if self.create_wallet_script else None,
            "depositScript": self.deposit_script.to_dict() if self.deposit_script else None,
            "withdrawScript": self.withdraw_script.to_dict() if self.withdraw_script else None,
            "balance": self.balance,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }