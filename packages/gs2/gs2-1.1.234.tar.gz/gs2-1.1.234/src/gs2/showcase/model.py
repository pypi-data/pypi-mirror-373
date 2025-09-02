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


class TransactionSetting(core.Gs2Model):
    enable_auto_run: bool = None
    enable_atomic_commit: bool = None
    transaction_use_distributor: bool = None
    acquire_action_use_job_queue: bool = None
    distributor_namespace_id: str = None
    key_id: str = None
    queue_namespace_id: str = None

    def with_enable_auto_run(self, enable_auto_run: bool) -> TransactionSetting:
        self.enable_auto_run = enable_auto_run
        return self

    def with_enable_atomic_commit(self, enable_atomic_commit: bool) -> TransactionSetting:
        self.enable_atomic_commit = enable_atomic_commit
        return self

    def with_transaction_use_distributor(self, transaction_use_distributor: bool) -> TransactionSetting:
        self.transaction_use_distributor = transaction_use_distributor
        return self

    def with_acquire_action_use_job_queue(self, acquire_action_use_job_queue: bool) -> TransactionSetting:
        self.acquire_action_use_job_queue = acquire_action_use_job_queue
        return self

    def with_distributor_namespace_id(self, distributor_namespace_id: str) -> TransactionSetting:
        self.distributor_namespace_id = distributor_namespace_id
        return self

    def with_key_id(self, key_id: str) -> TransactionSetting:
        self.key_id = key_id
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> TransactionSetting:
        self.queue_namespace_id = queue_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TransactionSetting]:
        if data is None:
            return None
        return TransactionSetting()\
            .with_enable_auto_run(data.get('enableAutoRun'))\
            .with_enable_atomic_commit(data.get('enableAtomicCommit'))\
            .with_transaction_use_distributor(data.get('transactionUseDistributor'))\
            .with_acquire_action_use_job_queue(data.get('acquireActionUseJobQueue'))\
            .with_distributor_namespace_id(data.get('distributorNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enableAutoRun": self.enable_auto_run,
            "enableAtomicCommit": self.enable_atomic_commit,
            "transactionUseDistributor": self.transaction_use_distributor,
            "acquireActionUseJobQueue": self.acquire_action_use_job_queue,
            "distributorNamespaceId": self.distributor_namespace_id,
            "keyId": self.key_id,
            "queueNamespaceId": self.queue_namespace_id,
        }


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


class GitHubCheckoutSetting(core.Gs2Model):
    api_key_id: str = None
    repository_name: str = None
    source_path: str = None
    reference_type: str = None
    commit_hash: str = None
    branch_name: str = None
    tag_name: str = None

    def with_api_key_id(self, api_key_id: str) -> GitHubCheckoutSetting:
        self.api_key_id = api_key_id
        return self

    def with_repository_name(self, repository_name: str) -> GitHubCheckoutSetting:
        self.repository_name = repository_name
        return self

    def with_source_path(self, source_path: str) -> GitHubCheckoutSetting:
        self.source_path = source_path
        return self

    def with_reference_type(self, reference_type: str) -> GitHubCheckoutSetting:
        self.reference_type = reference_type
        return self

    def with_commit_hash(self, commit_hash: str) -> GitHubCheckoutSetting:
        self.commit_hash = commit_hash
        return self

    def with_branch_name(self, branch_name: str) -> GitHubCheckoutSetting:
        self.branch_name = branch_name
        return self

    def with_tag_name(self, tag_name: str) -> GitHubCheckoutSetting:
        self.tag_name = tag_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GitHubCheckoutSetting]:
        if data is None:
            return None
        return GitHubCheckoutSetting()\
            .with_api_key_id(data.get('apiKeyId'))\
            .with_repository_name(data.get('repositoryName'))\
            .with_source_path(data.get('sourcePath'))\
            .with_reference_type(data.get('referenceType'))\
            .with_commit_hash(data.get('commitHash'))\
            .with_branch_name(data.get('branchName'))\
            .with_tag_name(data.get('tagName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "apiKeyId": self.api_key_id,
            "repositoryName": self.repository_name,
            "sourcePath": self.source_path,
            "referenceType": self.reference_type,
            "commitHash": self.commit_hash,
            "branchName": self.branch_name,
            "tagName": self.tag_name,
        }


class Config(core.Gs2Model):
    key: str = None
    value: str = None

    def with_key(self, key: str) -> Config:
        self.key = key
        return self

    def with_value(self, value: str) -> Config:
        self.value = value
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Config]:
        if data is None:
            return None
        return Config()\
            .with_key(data.get('key'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
        }


class AcquireAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> AcquireAction:
        self.action = action
        return self

    def with_request(self, request: str) -> AcquireAction:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcquireAction]:
        if data is None:
            return None
        return AcquireAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class VerifyAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> VerifyAction:
        self.action = action
        return self

    def with_request(self, request: str) -> VerifyAction:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyAction]:
        if data is None:
            return None
        return VerifyAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class ConsumeAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> ConsumeAction:
        self.action = action
        return self

    def with_request(self, request: str) -> ConsumeAction:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeAction]:
        if data is None:
            return None
        return ConsumeAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class RandomDisplayItemModel(core.Gs2Model):
    name: str = None
    metadata: str = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None
    stock: int = None
    weight: int = None

    def with_name(self, name: str) -> RandomDisplayItemModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RandomDisplayItemModel:
        self.metadata = metadata
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> RandomDisplayItemModel:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> RandomDisplayItemModel:
        self.consume_actions = consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> RandomDisplayItemModel:
        self.acquire_actions = acquire_actions
        return self

    def with_stock(self, stock: int) -> RandomDisplayItemModel:
        self.stock = stock
        return self

    def with_weight(self, weight: int) -> RandomDisplayItemModel:
        self.weight = weight
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RandomDisplayItemModel]:
        if data is None:
            return None
        return RandomDisplayItemModel()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_stock(data.get('stock'))\
            .with_weight(data.get('weight'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "stock": self.stock,
            "weight": self.weight,
        }


class RandomDisplayItem(core.Gs2Model):
    showcase_name: str = None
    name: str = None
    metadata: str = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None
    current_purchase_count: int = None
    maximum_purchase_count: int = None

    def with_showcase_name(self, showcase_name: str) -> RandomDisplayItem:
        self.showcase_name = showcase_name
        return self

    def with_name(self, name: str) -> RandomDisplayItem:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RandomDisplayItem:
        self.metadata = metadata
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> RandomDisplayItem:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> RandomDisplayItem:
        self.consume_actions = consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> RandomDisplayItem:
        self.acquire_actions = acquire_actions
        return self

    def with_current_purchase_count(self, current_purchase_count: int) -> RandomDisplayItem:
        self.current_purchase_count = current_purchase_count
        return self

    def with_maximum_purchase_count(self, maximum_purchase_count: int) -> RandomDisplayItem:
        self.maximum_purchase_count = maximum_purchase_count
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RandomDisplayItem]:
        if data is None:
            return None
        return RandomDisplayItem()\
            .with_showcase_name(data.get('showcaseName'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_current_purchase_count(data.get('currentPurchaseCount'))\
            .with_maximum_purchase_count(data.get('maximumPurchaseCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "showcaseName": self.showcase_name,
            "name": self.name,
            "metadata": self.metadata,
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "currentPurchaseCount": self.current_purchase_count,
            "maximumPurchaseCount": self.maximum_purchase_count,
        }


class PurchaseCount(core.Gs2Model):
    name: str = None
    count: int = None

    def with_name(self, name: str) -> PurchaseCount:
        self.name = name
        return self

    def with_count(self, count: int) -> PurchaseCount:
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
    ) -> Optional[PurchaseCount]:
        if data is None:
            return None
        return PurchaseCount()\
            .with_name(data.get('name'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "count": self.count,
        }


class RandomShowcase(core.Gs2Model):
    random_showcase_id: str = None
    name: str = None
    metadata: str = None
    maximum_number_of_choice: int = None
    display_items: List[RandomDisplayItemModel] = None
    base_timestamp: int = None
    reset_interval_hours: int = None
    sales_period_event_id: str = None

    def with_random_showcase_id(self, random_showcase_id: str) -> RandomShowcase:
        self.random_showcase_id = random_showcase_id
        return self

    def with_name(self, name: str) -> RandomShowcase:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> RandomShowcase:
        self.metadata = metadata
        return self

    def with_maximum_number_of_choice(self, maximum_number_of_choice: int) -> RandomShowcase:
        self.maximum_number_of_choice = maximum_number_of_choice
        return self

    def with_display_items(self, display_items: List[RandomDisplayItemModel]) -> RandomShowcase:
        self.display_items = display_items
        return self

    def with_base_timestamp(self, base_timestamp: int) -> RandomShowcase:
        self.base_timestamp = base_timestamp
        return self

    def with_reset_interval_hours(self, reset_interval_hours: int) -> RandomShowcase:
        self.reset_interval_hours = reset_interval_hours
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> RandomShowcase:
        self.sales_period_event_id = sales_period_event_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        showcase_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:random:showcase:{showcaseName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            showcaseName=showcase_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):random:showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):random:showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):random:showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_showcase_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):random:showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('showcase_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RandomShowcase]:
        if data is None:
            return None
        return RandomShowcase()\
            .with_random_showcase_id(data.get('randomShowcaseId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_maximum_number_of_choice(data.get('maximumNumberOfChoice'))\
            .with_display_items(None if data.get('displayItems') is None else [
                RandomDisplayItemModel.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')))
            ])\
            .with_base_timestamp(data.get('baseTimestamp'))\
            .with_reset_interval_hours(data.get('resetIntervalHours'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "randomShowcaseId": self.random_showcase_id,
            "name": self.name,
            "metadata": self.metadata,
            "maximumNumberOfChoice": self.maximum_number_of_choice,
            "displayItems": None if self.display_items is None else [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items))
            ],
            "baseTimestamp": self.base_timestamp,
            "resetIntervalHours": self.reset_interval_hours,
            "salesPeriodEventId": self.sales_period_event_id,
        }


class RandomShowcaseMaster(core.Gs2Model):
    showcase_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    maximum_number_of_choice: int = None
    display_items: List[RandomDisplayItemModel] = None
    base_timestamp: int = None
    reset_interval_hours: int = None
    sales_period_event_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_showcase_id(self, showcase_id: str) -> RandomShowcaseMaster:
        self.showcase_id = showcase_id
        return self

    def with_name(self, name: str) -> RandomShowcaseMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> RandomShowcaseMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> RandomShowcaseMaster:
        self.metadata = metadata
        return self

    def with_maximum_number_of_choice(self, maximum_number_of_choice: int) -> RandomShowcaseMaster:
        self.maximum_number_of_choice = maximum_number_of_choice
        return self

    def with_display_items(self, display_items: List[RandomDisplayItemModel]) -> RandomShowcaseMaster:
        self.display_items = display_items
        return self

    def with_base_timestamp(self, base_timestamp: int) -> RandomShowcaseMaster:
        self.base_timestamp = base_timestamp
        return self

    def with_reset_interval_hours(self, reset_interval_hours: int) -> RandomShowcaseMaster:
        self.reset_interval_hours = reset_interval_hours
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> RandomShowcaseMaster:
        self.sales_period_event_id = sales_period_event_id
        return self

    def with_created_at(self, created_at: int) -> RandomShowcaseMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> RandomShowcaseMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> RandomShowcaseMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        showcase_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:random:showcase:{showcaseName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            showcaseName=showcase_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):random:showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):random:showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):random:showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_showcase_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):random:showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('showcase_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[RandomShowcaseMaster]:
        if data is None:
            return None
        return RandomShowcaseMaster()\
            .with_showcase_id(data.get('showcaseId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_maximum_number_of_choice(data.get('maximumNumberOfChoice'))\
            .with_display_items(None if data.get('displayItems') is None else [
                RandomDisplayItemModel.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')))
            ])\
            .with_base_timestamp(data.get('baseTimestamp'))\
            .with_reset_interval_hours(data.get('resetIntervalHours'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "showcaseId": self.showcase_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "maximumNumberOfChoice": self.maximum_number_of_choice,
            "displayItems": None if self.display_items is None else [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items))
            ],
            "baseTimestamp": self.base_timestamp,
            "resetIntervalHours": self.reset_interval_hours,
            "salesPeriodEventId": self.sales_period_event_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class DisplayItemMaster(core.Gs2Model):
    display_item_id: str = None
    type: str = None
    sales_item_name: str = None
    sales_item_group_name: str = None
    sales_period_event_id: str = None
    revision: int = None

    def with_display_item_id(self, display_item_id: str) -> DisplayItemMaster:
        self.display_item_id = display_item_id
        return self

    def with_type(self, type: str) -> DisplayItemMaster:
        self.type = type
        return self

    def with_sales_item_name(self, sales_item_name: str) -> DisplayItemMaster:
        self.sales_item_name = sales_item_name
        return self

    def with_sales_item_group_name(self, sales_item_group_name: str) -> DisplayItemMaster:
        self.sales_item_group_name = sales_item_group_name
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> DisplayItemMaster:
        self.sales_period_event_id = sales_period_event_id
        return self

    def with_revision(self, revision: int) -> DisplayItemMaster:
        self.revision = revision
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DisplayItemMaster]:
        if data is None:
            return None
        return DisplayItemMaster()\
            .with_display_item_id(data.get('displayItemId'))\
            .with_type(data.get('type'))\
            .with_sales_item_name(data.get('salesItemName'))\
            .with_sales_item_group_name(data.get('salesItemGroupName'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "displayItemId": self.display_item_id,
            "type": self.type,
            "salesItemName": self.sales_item_name,
            "salesItemGroupName": self.sales_item_group_name,
            "salesPeriodEventId": self.sales_period_event_id,
            "revision": self.revision,
        }


class DisplayItem(core.Gs2Model):
    display_item_id: str = None
    type: str = None
    sales_item: SalesItem = None
    sales_item_group: SalesItemGroup = None
    sales_period_event_id: str = None

    def with_display_item_id(self, display_item_id: str) -> DisplayItem:
        self.display_item_id = display_item_id
        return self

    def with_type(self, type: str) -> DisplayItem:
        self.type = type
        return self

    def with_sales_item(self, sales_item: SalesItem) -> DisplayItem:
        self.sales_item = sales_item
        return self

    def with_sales_item_group(self, sales_item_group: SalesItemGroup) -> DisplayItem:
        self.sales_item_group = sales_item_group
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> DisplayItem:
        self.sales_period_event_id = sales_period_event_id
        return self

    @classmethod
    def create_grn(
        cls,
    ):
        return ''.format(
        )

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DisplayItem]:
        if data is None:
            return None
        return DisplayItem()\
            .with_display_item_id(data.get('displayItemId'))\
            .with_type(data.get('type'))\
            .with_sales_item(SalesItem.from_dict(data.get('salesItem')))\
            .with_sales_item_group(SalesItemGroup.from_dict(data.get('salesItemGroup')))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "displayItemId": self.display_item_id,
            "type": self.type,
            "salesItem": self.sales_item.to_dict() if self.sales_item else None,
            "salesItemGroup": self.sales_item_group.to_dict() if self.sales_item_group else None,
            "salesPeriodEventId": self.sales_period_event_id,
        }


class Showcase(core.Gs2Model):
    showcase_id: str = None
    name: str = None
    metadata: str = None
    sales_period_event_id: str = None
    display_items: List[DisplayItem] = None

    def with_showcase_id(self, showcase_id: str) -> Showcase:
        self.showcase_id = showcase_id
        return self

    def with_name(self, name: str) -> Showcase:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> Showcase:
        self.metadata = metadata
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> Showcase:
        self.sales_period_event_id = sales_period_event_id
        return self

    def with_display_items(self, display_items: List[DisplayItem]) -> Showcase:
        self.display_items = display_items
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        showcase_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:showcase:{showcaseName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            showcaseName=showcase_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_showcase_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('showcase_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Showcase]:
        if data is None:
            return None
        return Showcase()\
            .with_showcase_id(data.get('showcaseId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))\
            .with_display_items(None if data.get('displayItems') is None else [
                DisplayItem.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "showcaseId": self.showcase_id,
            "name": self.name,
            "metadata": self.metadata,
            "salesPeriodEventId": self.sales_period_event_id,
            "displayItems": None if self.display_items is None else [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items))
            ],
        }


class SalesItemGroup(core.Gs2Model):
    name: str = None
    metadata: str = None
    sales_items: List[SalesItem] = None

    def with_name(self, name: str) -> SalesItemGroup:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SalesItemGroup:
        self.metadata = metadata
        return self

    def with_sales_items(self, sales_items: List[SalesItem]) -> SalesItemGroup:
        self.sales_items = sales_items
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SalesItemGroup]:
        if data is None:
            return None
        return SalesItemGroup()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_items(None if data.get('salesItems') is None else [
                SalesItem.from_dict(data.get('salesItems')[i])
                for i in range(len(data.get('salesItems')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "salesItems": None if self.sales_items is None else [
                self.sales_items[i].to_dict() if self.sales_items[i] else None
                for i in range(len(self.sales_items))
            ],
        }


class SalesItem(core.Gs2Model):
    name: str = None
    metadata: str = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None

    def with_name(self, name: str) -> SalesItem:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SalesItem:
        self.metadata = metadata
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> SalesItem:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> SalesItem:
        self.consume_actions = consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> SalesItem:
        self.acquire_actions = acquire_actions
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SalesItem]:
        if data is None:
            return None
        return SalesItem()\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "metadata": self.metadata,
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class CurrentShowcaseMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentShowcaseMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentShowcaseMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentShowcaseMaster]:
        if data is None:
            return None
        return CurrentShowcaseMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class ShowcaseMaster(core.Gs2Model):
    showcase_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    sales_period_event_id: str = None
    display_items: List[DisplayItemMaster] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_showcase_id(self, showcase_id: str) -> ShowcaseMaster:
        self.showcase_id = showcase_id
        return self

    def with_name(self, name: str) -> ShowcaseMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> ShowcaseMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> ShowcaseMaster:
        self.metadata = metadata
        return self

    def with_sales_period_event_id(self, sales_period_event_id: str) -> ShowcaseMaster:
        self.sales_period_event_id = sales_period_event_id
        return self

    def with_display_items(self, display_items: List[DisplayItemMaster]) -> ShowcaseMaster:
        self.display_items = display_items
        return self

    def with_created_at(self, created_at: int) -> ShowcaseMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ShowcaseMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> ShowcaseMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        showcase_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:showcase:{showcaseName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            showcaseName=showcase_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_showcase_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):showcase:(?P<showcaseName>.+)', grn)
        if match is None:
            return None
        return match.group('showcase_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ShowcaseMaster]:
        if data is None:
            return None
        return ShowcaseMaster()\
            .with_showcase_id(data.get('showcaseId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_period_event_id(data.get('salesPeriodEventId'))\
            .with_display_items(None if data.get('displayItems') is None else [
                DisplayItemMaster.from_dict(data.get('displayItems')[i])
                for i in range(len(data.get('displayItems')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "showcaseId": self.showcase_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "salesPeriodEventId": self.sales_period_event_id,
            "displayItems": None if self.display_items is None else [
                self.display_items[i].to_dict() if self.display_items[i] else None
                for i in range(len(self.display_items))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class SalesItemGroupMaster(core.Gs2Model):
    sales_item_group_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    sales_item_names: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_sales_item_group_id(self, sales_item_group_id: str) -> SalesItemGroupMaster:
        self.sales_item_group_id = sales_item_group_id
        return self

    def with_name(self, name: str) -> SalesItemGroupMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> SalesItemGroupMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> SalesItemGroupMaster:
        self.metadata = metadata
        return self

    def with_sales_item_names(self, sales_item_names: List[str]) -> SalesItemGroupMaster:
        self.sales_item_names = sales_item_names
        return self

    def with_created_at(self, created_at: int) -> SalesItemGroupMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SalesItemGroupMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SalesItemGroupMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        sales_item_group_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:salesItemGroup:{salesItemGroupName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            salesItemGroupName=sales_item_group_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItemGroup:(?P<salesItemGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItemGroup:(?P<salesItemGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItemGroup:(?P<salesItemGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_sales_item_group_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItemGroup:(?P<salesItemGroupName>.+)', grn)
        if match is None:
            return None
        return match.group('sales_item_group_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SalesItemGroupMaster]:
        if data is None:
            return None
        return SalesItemGroupMaster()\
            .with_sales_item_group_id(data.get('salesItemGroupId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_sales_item_names(None if data.get('salesItemNames') is None else [
                data.get('salesItemNames')[i]
                for i in range(len(data.get('salesItemNames')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "salesItemGroupId": self.sales_item_group_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "salesItemNames": None if self.sales_item_names is None else [
                self.sales_item_names[i]
                for i in range(len(self.sales_item_names))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class SalesItemMaster(core.Gs2Model):
    sales_item_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    acquire_actions: List[AcquireAction] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_sales_item_id(self, sales_item_id: str) -> SalesItemMaster:
        self.sales_item_id = sales_item_id
        return self

    def with_name(self, name: str) -> SalesItemMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> SalesItemMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> SalesItemMaster:
        self.metadata = metadata
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> SalesItemMaster:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> SalesItemMaster:
        self.consume_actions = consume_actions
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> SalesItemMaster:
        self.acquire_actions = acquire_actions
        return self

    def with_created_at(self, created_at: int) -> SalesItemMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SalesItemMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SalesItemMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        sales_item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}:salesItem:{salesItemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            salesItemName=sales_item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItem:(?P<salesItemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItem:(?P<salesItemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItem:(?P<salesItemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_sales_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+):salesItem:(?P<salesItemName>.+)', grn)
        if match is None:
            return None
        return match.group('sales_item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SalesItemMaster]:
        if data is None:
            return None
        return SalesItemMaster()\
            .with_sales_item_id(data.get('salesItemId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "salesItemId": self.sales_item_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    buy_script: ScriptSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    queue_namespace_id: str = None
    key_id: str = None
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

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
        return self

    def with_buy_script(self, buy_script: ScriptSetting) -> Namespace:
        self.buy_script = buy_script
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

    def with_queue_namespace_id(self, queue_namespace_id: str) -> Namespace:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> Namespace:
        self.key_id = key_id
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
        return 'grn:gs2:{region}:{ownerId}:showcase:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):showcase:(?P<namespaceName>.+)', grn)
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
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_buy_script(ScriptSetting.from_dict(data.get('buyScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "buyScript": self.buy_script.to_dict() if self.buy_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
            "revision": self.revision,
        }