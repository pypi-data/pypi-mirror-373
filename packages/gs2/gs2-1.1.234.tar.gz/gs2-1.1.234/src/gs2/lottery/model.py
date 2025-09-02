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


class BoxItems(core.Gs2Model):
    box_id: str = None
    prize_table_name: str = None
    user_id: str = None
    items: List[BoxItem] = None

    def with_box_id(self, box_id: str) -> BoxItems:
        self.box_id = box_id
        return self

    def with_prize_table_name(self, prize_table_name: str) -> BoxItems:
        self.prize_table_name = prize_table_name
        return self

    def with_user_id(self, user_id: str) -> BoxItems:
        self.user_id = user_id
        return self

    def with_items(self, items: List[BoxItem]) -> BoxItems:
        self.items = items
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        prize_table_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:lottery:{namespaceName}:user:{userId}:box:items:{prizeTableName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            prizeTableName=prize_table_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):user:(?P<userId>.+):box:items:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):user:(?P<userId>.+):box:items:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):user:(?P<userId>.+):box:items:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):user:(?P<userId>.+):box:items:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_prize_table_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):user:(?P<userId>.+):box:items:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('prize_table_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BoxItems]:
        if data is None:
            return None
        return BoxItems()\
            .with_box_id(data.get('boxId'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_user_id(data.get('userId'))\
            .with_items(None if data.get('items') is None else [
                BoxItem.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "boxId": self.box_id,
            "prizeTableName": self.prize_table_name,
            "userId": self.user_id,
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class BoxItem(core.Gs2Model):
    prize_id: str = None
    acquire_actions: List[AcquireAction] = None
    remaining: int = None
    initial: int = None

    def with_prize_id(self, prize_id: str) -> BoxItem:
        self.prize_id = prize_id
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> BoxItem:
        self.acquire_actions = acquire_actions
        return self

    def with_remaining(self, remaining: int) -> BoxItem:
        self.remaining = remaining
        return self

    def with_initial(self, initial: int) -> BoxItem:
        self.initial = initial
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BoxItem]:
        if data is None:
            return None
        return BoxItem()\
            .with_prize_id(data.get('prizeId'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_remaining(data.get('remaining'))\
            .with_initial(data.get('initial'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prizeId": self.prize_id,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "remaining": self.remaining,
            "initial": self.initial,
        }


class DrawnPrize(core.Gs2Model):
    prize_id: str = None
    acquire_actions: List[AcquireAction] = None

    def with_prize_id(self, prize_id: str) -> DrawnPrize:
        self.prize_id = prize_id
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> DrawnPrize:
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
    ) -> Optional[DrawnPrize]:
        if data is None:
            return None
        return DrawnPrize()\
            .with_prize_id(data.get('prizeId'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prizeId": self.prize_id,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class PrizeLimit(core.Gs2Model):
    prize_limit_id: str = None
    prize_id: str = None
    drawn_count: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_prize_limit_id(self, prize_limit_id: str) -> PrizeLimit:
        self.prize_limit_id = prize_limit_id
        return self

    def with_prize_id(self, prize_id: str) -> PrizeLimit:
        self.prize_id = prize_id
        return self

    def with_drawn_count(self, drawn_count: int) -> PrizeLimit:
        self.drawn_count = drawn_count
        return self

    def with_created_at(self, created_at: int) -> PrizeLimit:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> PrizeLimit:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> PrizeLimit:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        prize_table_name,
        prize_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:lottery:{namespaceName}:table:{prizeTableName}:prize:{prizeId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            prizeTableName=prize_table_name,
            prizeId=prize_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+):prize:(?P<prizeId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+):prize:(?P<prizeId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+):prize:(?P<prizeId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_prize_table_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+):prize:(?P<prizeId>.+)', grn)
        if match is None:
            return None
        return match.group('prize_table_name')

    @classmethod
    def get_prize_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+):prize:(?P<prizeId>.+)', grn)
        if match is None:
            return None
        return match.group('prize_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrizeLimit]:
        if data is None:
            return None
        return PrizeLimit()\
            .with_prize_limit_id(data.get('prizeLimitId'))\
            .with_prize_id(data.get('prizeId'))\
            .with_drawn_count(data.get('drawnCount'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prizeLimitId": self.prize_limit_id,
            "prizeId": self.prize_id,
            "drawnCount": self.drawn_count,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Prize(core.Gs2Model):
    prize_id: str = None
    type: str = None
    acquire_actions: List[AcquireAction] = None
    drawn_limit: int = None
    limit_fail_over_prize_id: str = None
    prize_table_name: str = None
    weight: int = None

    def with_prize_id(self, prize_id: str) -> Prize:
        self.prize_id = prize_id
        return self

    def with_type(self, type: str) -> Prize:
        self.type = type
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> Prize:
        self.acquire_actions = acquire_actions
        return self

    def with_drawn_limit(self, drawn_limit: int) -> Prize:
        self.drawn_limit = drawn_limit
        return self

    def with_limit_fail_over_prize_id(self, limit_fail_over_prize_id: str) -> Prize:
        self.limit_fail_over_prize_id = limit_fail_over_prize_id
        return self

    def with_prize_table_name(self, prize_table_name: str) -> Prize:
        self.prize_table_name = prize_table_name
        return self

    def with_weight(self, weight: int) -> Prize:
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
    ) -> Optional[Prize]:
        if data is None:
            return None
        return Prize()\
            .with_prize_id(data.get('prizeId'))\
            .with_type(data.get('type'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])\
            .with_drawn_limit(data.get('drawnLimit'))\
            .with_limit_fail_over_prize_id(data.get('limitFailOverPrizeId'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_weight(data.get('weight'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prizeId": self.prize_id,
            "type": self.type,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
            "drawnLimit": self.drawn_limit,
            "limitFailOverPrizeId": self.limit_fail_over_prize_id,
            "prizeTableName": self.prize_table_name,
            "weight": self.weight,
        }


class CurrentLotteryMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentLotteryMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentLotteryMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:lottery:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentLotteryMaster]:
        if data is None:
            return None
        return CurrentLotteryMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class Probability(core.Gs2Model):
    prize: DrawnPrize = None
    rate: float = None

    def with_prize(self, prize: DrawnPrize) -> Probability:
        self.prize = prize
        return self

    def with_rate(self, rate: float) -> Probability:
        self.rate = rate
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Probability]:
        if data is None:
            return None
        return Probability()\
            .with_prize(DrawnPrize.from_dict(data.get('prize')))\
            .with_rate(data.get('rate'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prize": self.prize.to_dict() if self.prize else None,
            "rate": self.rate,
        }


class PrizeTable(core.Gs2Model):
    prize_table_id: str = None
    name: str = None
    metadata: str = None
    prizes: List[Prize] = None

    def with_prize_table_id(self, prize_table_id: str) -> PrizeTable:
        self.prize_table_id = prize_table_id
        return self

    def with_name(self, name: str) -> PrizeTable:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> PrizeTable:
        self.metadata = metadata
        return self

    def with_prizes(self, prizes: List[Prize]) -> PrizeTable:
        self.prizes = prizes
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        prize_table_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:lottery:{namespaceName}:table:{prizeTableName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            prizeTableName=prize_table_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_prize_table_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('prize_table_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrizeTable]:
        if data is None:
            return None
        return PrizeTable()\
            .with_prize_table_id(data.get('prizeTableId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_prizes(None if data.get('prizes') is None else [
                Prize.from_dict(data.get('prizes')[i])
                for i in range(len(data.get('prizes')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prizeTableId": self.prize_table_id,
            "name": self.name,
            "metadata": self.metadata,
            "prizes": None if self.prizes is None else [
                self.prizes[i].to_dict() if self.prizes[i] else None
                for i in range(len(self.prizes))
            ],
        }


class LotteryModel(core.Gs2Model):
    lottery_model_id: str = None
    name: str = None
    metadata: str = None
    mode: str = None
    method: str = None
    prize_table_name: str = None
    choice_prize_table_script_id: str = None

    def with_lottery_model_id(self, lottery_model_id: str) -> LotteryModel:
        self.lottery_model_id = lottery_model_id
        return self

    def with_name(self, name: str) -> LotteryModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> LotteryModel:
        self.metadata = metadata
        return self

    def with_mode(self, mode: str) -> LotteryModel:
        self.mode = mode
        return self

    def with_method(self, method: str) -> LotteryModel:
        self.method = method
        return self

    def with_prize_table_name(self, prize_table_name: str) -> LotteryModel:
        self.prize_table_name = prize_table_name
        return self

    def with_choice_prize_table_script_id(self, choice_prize_table_script_id: str) -> LotteryModel:
        self.choice_prize_table_script_id = choice_prize_table_script_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        lottery_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:lottery:{namespaceName}:lotteryModel:{lotteryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            lotteryName=lottery_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):lotteryModel:(?P<lotteryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):lotteryModel:(?P<lotteryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):lotteryModel:(?P<lotteryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_lottery_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):lotteryModel:(?P<lotteryName>.+)', grn)
        if match is None:
            return None
        return match.group('lottery_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[LotteryModel]:
        if data is None:
            return None
        return LotteryModel()\
            .with_lottery_model_id(data.get('lotteryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_mode(data.get('mode'))\
            .with_method(data.get('method'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_choice_prize_table_script_id(data.get('choicePrizeTableScriptId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lotteryModelId": self.lottery_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "mode": self.mode,
            "method": self.method,
            "prizeTableName": self.prize_table_name,
            "choicePrizeTableScriptId": self.choice_prize_table_script_id,
        }


class PrizeTableMaster(core.Gs2Model):
    prize_table_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    prizes: List[Prize] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_prize_table_id(self, prize_table_id: str) -> PrizeTableMaster:
        self.prize_table_id = prize_table_id
        return self

    def with_name(self, name: str) -> PrizeTableMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> PrizeTableMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> PrizeTableMaster:
        self.description = description
        return self

    def with_prizes(self, prizes: List[Prize]) -> PrizeTableMaster:
        self.prizes = prizes
        return self

    def with_created_at(self, created_at: int) -> PrizeTableMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> PrizeTableMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> PrizeTableMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        prize_table_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:lottery:{namespaceName}:table:{prizeTableName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            prizeTableName=prize_table_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_prize_table_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):table:(?P<prizeTableName>.+)', grn)
        if match is None:
            return None
        return match.group('prize_table_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[PrizeTableMaster]:
        if data is None:
            return None
        return PrizeTableMaster()\
            .with_prize_table_id(data.get('prizeTableId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_prizes(None if data.get('prizes') is None else [
                Prize.from_dict(data.get('prizes')[i])
                for i in range(len(data.get('prizes')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prizeTableId": self.prize_table_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "prizes": None if self.prizes is None else [
                self.prizes[i].to_dict() if self.prizes[i] else None
                for i in range(len(self.prizes))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class LotteryModelMaster(core.Gs2Model):
    lottery_model_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    mode: str = None
    method: str = None
    prize_table_name: str = None
    choice_prize_table_script_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_lottery_model_id(self, lottery_model_id: str) -> LotteryModelMaster:
        self.lottery_model_id = lottery_model_id
        return self

    def with_name(self, name: str) -> LotteryModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> LotteryModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> LotteryModelMaster:
        self.description = description
        return self

    def with_mode(self, mode: str) -> LotteryModelMaster:
        self.mode = mode
        return self

    def with_method(self, method: str) -> LotteryModelMaster:
        self.method = method
        return self

    def with_prize_table_name(self, prize_table_name: str) -> LotteryModelMaster:
        self.prize_table_name = prize_table_name
        return self

    def with_choice_prize_table_script_id(self, choice_prize_table_script_id: str) -> LotteryModelMaster:
        self.choice_prize_table_script_id = choice_prize_table_script_id
        return self

    def with_created_at(self, created_at: int) -> LotteryModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> LotteryModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> LotteryModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        lottery_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:lottery:{namespaceName}:lotteryModel:{lotteryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            lotteryName=lottery_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):lotteryModel:(?P<lotteryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):lotteryModel:(?P<lotteryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):lotteryModel:(?P<lotteryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_lottery_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+):lotteryModel:(?P<lotteryName>.+)', grn)
        if match is None:
            return None
        return match.group('lottery_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[LotteryModelMaster]:
        if data is None:
            return None
        return LotteryModelMaster()\
            .with_lottery_model_id(data.get('lotteryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_mode(data.get('mode'))\
            .with_method(data.get('method'))\
            .with_prize_table_name(data.get('prizeTableName'))\
            .with_choice_prize_table_script_id(data.get('choicePrizeTableScriptId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lotteryModelId": self.lottery_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "mode": self.mode,
            "method": self.method,
            "prizeTableName": self.prize_table_name,
            "choicePrizeTableScriptId": self.choice_prize_table_script_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
    lottery_trigger_script_id: str = None
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

    def with_lottery_trigger_script_id(self, lottery_trigger_script_id: str) -> Namespace:
        self.lottery_trigger_script_id = lottery_trigger_script_id
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
        return 'grn:gs2:{region}:{ownerId}:lottery:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):lottery:(?P<namespaceName>.+)', grn)
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
            .with_lottery_trigger_script_id(data.get('lotteryTriggerScriptId'))\
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
            "lotteryTriggerScriptId": self.lottery_trigger_script_id,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
            "revision": self.revision,
        }