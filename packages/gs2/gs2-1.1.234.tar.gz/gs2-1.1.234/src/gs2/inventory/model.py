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


class HeldCount(core.Gs2Model):
    item_name: str = None
    count: int = None

    def with_item_name(self, item_name: str) -> HeldCount:
        self.item_name = item_name
        return self

    def with_count(self, count: int) -> HeldCount:
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
    ) -> Optional[HeldCount]:
        if data is None:
            return None
        return HeldCount()\
            .with_item_name(data.get('itemName'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemName": self.item_name,
            "count": self.count,
        }


class ConsumeCount(core.Gs2Model):
    item_name: str = None
    count: int = None

    def with_item_name(self, item_name: str) -> ConsumeCount:
        self.item_name = item_name
        return self

    def with_count(self, count: int) -> ConsumeCount:
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
    ) -> Optional[ConsumeCount]:
        if data is None:
            return None
        return ConsumeCount()\
            .with_item_name(data.get('itemName'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemName": self.item_name,
            "count": self.count,
        }


class AcquireCount(core.Gs2Model):
    item_name: str = None
    count: int = None

    def with_item_name(self, item_name: str) -> AcquireCount:
        self.item_name = item_name
        return self

    def with_count(self, count: int) -> AcquireCount:
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
    ) -> Optional[AcquireCount]:
        if data is None:
            return None
        return AcquireCount()\
            .with_item_name(data.get('itemName'))\
            .with_count(data.get('count'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemName": self.item_name,
            "count": self.count,
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


class BigItem(core.Gs2Model):
    item_id: str = None
    user_id: str = None
    item_name: str = None
    count: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_item_id(self, item_id: str) -> BigItem:
        self.item_id = item_id
        return self

    def with_user_id(self, user_id: str) -> BigItem:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> BigItem:
        self.item_name = item_name
        return self

    def with_count(self, count: str) -> BigItem:
        self.count = count
        return self

    def with_created_at(self, created_at: int) -> BigItem:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BigItem:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> BigItem:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        inventory_name,
        item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:user:{userId}:big:inventory:{inventoryName}:item:{itemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            inventoryName=inventory_name,
            itemName=item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BigItem]:
        if data is None:
            return None
        return BigItem()\
            .with_item_id(data.get('itemId'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_count(data.get('count'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemId": self.item_id,
            "userId": self.user_id,
            "itemName": self.item_name,
            "count": self.count,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class BigInventory(core.Gs2Model):
    inventory_id: str = None
    inventory_name: str = None
    user_id: str = None
    big_items: List[BigItem] = None
    created_at: int = None
    updated_at: int = None

    def with_inventory_id(self, inventory_id: str) -> BigInventory:
        self.inventory_id = inventory_id
        return self

    def with_inventory_name(self, inventory_name: str) -> BigInventory:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> BigInventory:
        self.user_id = user_id
        return self

    def with_big_items(self, big_items: List[BigItem]) -> BigInventory:
        self.big_items = big_items
        return self

    def with_created_at(self, created_at: int) -> BigInventory:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BigInventory:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:user:{userId}:big:inventory:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):big:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BigInventory]:
        if data is None:
            return None
        return BigInventory()\
            .with_inventory_id(data.get('inventoryId'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_big_items(None if data.get('bigItems') is None else [
                BigItem.from_dict(data.get('bigItems')[i])
                for i in range(len(data.get('bigItems')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryId": self.inventory_id,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "bigItems": None if self.big_items is None else [
                self.big_items[i].to_dict() if self.big_items[i] else None
                for i in range(len(self.big_items))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class SimpleItem(core.Gs2Model):
    item_id: str = None
    user_id: str = None
    item_name: str = None
    count: int = None
    revision: int = None

    def with_item_id(self, item_id: str) -> SimpleItem:
        self.item_id = item_id
        return self

    def with_user_id(self, user_id: str) -> SimpleItem:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> SimpleItem:
        self.item_name = item_name
        return self

    def with_count(self, count: int) -> SimpleItem:
        self.count = count
        return self

    def with_revision(self, revision: int) -> SimpleItem:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        inventory_name,
        item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:user:{userId}:simple:inventory:{inventoryName}:item:{itemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            inventoryName=inventory_name,
            itemName=item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SimpleItem]:
        if data is None:
            return None
        return SimpleItem()\
            .with_item_id(data.get('itemId'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_count(data.get('count'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemId": self.item_id,
            "userId": self.user_id,
            "itemName": self.item_name,
            "count": self.count,
            "revision": self.revision,
        }


class SimpleInventory(core.Gs2Model):
    inventory_id: str = None
    inventory_name: str = None
    user_id: str = None
    simple_items: List[SimpleItem] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_inventory_id(self, inventory_id: str) -> SimpleInventory:
        self.inventory_id = inventory_id
        return self

    def with_inventory_name(self, inventory_name: str) -> SimpleInventory:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> SimpleInventory:
        self.user_id = user_id
        return self

    def with_simple_items(self, simple_items: List[SimpleItem]) -> SimpleInventory:
        self.simple_items = simple_items
        return self

    def with_created_at(self, created_at: int) -> SimpleInventory:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SimpleInventory:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SimpleInventory:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:user:{userId}:simple:inventory:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):simple:inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SimpleInventory]:
        if data is None:
            return None
        return SimpleInventory()\
            .with_inventory_id(data.get('inventoryId'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_simple_items(None if data.get('simpleItems') is None else [
                SimpleItem.from_dict(data.get('simpleItems')[i])
                for i in range(len(data.get('simpleItems')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryId": self.inventory_id,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "simpleItems": None if self.simple_items is None else [
                self.simple_items[i].to_dict() if self.simple_items[i] else None
                for i in range(len(self.simple_items))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class ReferenceOf(core.Gs2Model):
    reference_of_id: str = None
    name: str = None

    def with_reference_of_id(self, reference_of_id: str) -> ReferenceOf:
        self.reference_of_id = reference_of_id
        return self

    def with_name(self, name: str) -> ReferenceOf:
        self.name = name
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        inventory_name,
        item_name,
        item_set_name,
        reference_of,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:user:{userId}:inventory:{inventoryName}:item:{itemName}:itemSet:{itemSetName}:referenceOf:{referenceOf}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            inventoryName=inventory_name,
            itemName=item_name,
            itemSetName=item_set_name,
            referenceOf=reference_of,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+):referenceOf:(?P<referenceOf>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+):referenceOf:(?P<referenceOf>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+):referenceOf:(?P<referenceOf>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+):referenceOf:(?P<referenceOf>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+):referenceOf:(?P<referenceOf>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+):referenceOf:(?P<referenceOf>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    @classmethod
    def get_item_set_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+):referenceOf:(?P<referenceOf>.+)', grn)
        if match is None:
            return None
        return match.group('item_set_name')

    @classmethod
    def get_reference_of_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+):referenceOf:(?P<referenceOf>.+)', grn)
        if match is None:
            return None
        return match.group('reference_of')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ReferenceOf]:
        if data is None:
            return None
        return ReferenceOf()\
            .with_reference_of_id(data.get('referenceOfId'))\
            .with_name(data.get('name'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "referenceOfId": self.reference_of_id,
            "name": self.name,
        }


class ItemSet(core.Gs2Model):
    item_set_id: str = None
    name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    count: int = None
    reference_of: List[str] = None
    sort_value: int = None
    expires_at: int = None
    created_at: int = None
    updated_at: int = None

    def with_item_set_id(self, item_set_id: str) -> ItemSet:
        self.item_set_id = item_set_id
        return self

    def with_name(self, name: str) -> ItemSet:
        self.name = name
        return self

    def with_inventory_name(self, inventory_name: str) -> ItemSet:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> ItemSet:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> ItemSet:
        self.item_name = item_name
        return self

    def with_count(self, count: int) -> ItemSet:
        self.count = count
        return self

    def with_reference_of(self, reference_of: List[str]) -> ItemSet:
        self.reference_of = reference_of
        return self

    def with_sort_value(self, sort_value: int) -> ItemSet:
        self.sort_value = sort_value
        return self

    def with_expires_at(self, expires_at: int) -> ItemSet:
        self.expires_at = expires_at
        return self

    def with_created_at(self, created_at: int) -> ItemSet:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ItemSet:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        inventory_name,
        item_name,
        item_set_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:user:{userId}:inventory:{inventoryName}:item:{itemName}:itemSet:{itemSetName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            inventoryName=inventory_name,
            itemName=item_name,
            itemSetName=item_set_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    @classmethod
    def get_item_set_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+):item:(?P<itemName>.+):itemSet:(?P<itemSetName>.+)', grn)
        if match is None:
            return None
        return match.group('item_set_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ItemSet]:
        if data is None:
            return None
        return ItemSet()\
            .with_item_set_id(data.get('itemSetId'))\
            .with_name(data.get('name'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_count(data.get('count'))\
            .with_reference_of(None if data.get('referenceOf') is None else [
                data.get('referenceOf')[i]
                for i in range(len(data.get('referenceOf')))
            ])\
            .with_sort_value(data.get('sortValue'))\
            .with_expires_at(data.get('expiresAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemSetId": self.item_set_id,
            "name": self.name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "count": self.count,
            "referenceOf": None if self.reference_of is None else [
                self.reference_of[i]
                for i in range(len(self.reference_of))
            ],
            "sortValue": self.sort_value,
            "expiresAt": self.expires_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Inventory(core.Gs2Model):
    inventory_id: str = None
    inventory_name: str = None
    user_id: str = None
    current_inventory_capacity_usage: int = None
    current_inventory_max_capacity: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_inventory_id(self, inventory_id: str) -> Inventory:
        self.inventory_id = inventory_id
        return self

    def with_inventory_name(self, inventory_name: str) -> Inventory:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> Inventory:
        self.user_id = user_id
        return self

    def with_current_inventory_capacity_usage(self, current_inventory_capacity_usage: int) -> Inventory:
        self.current_inventory_capacity_usage = current_inventory_capacity_usage
        return self

    def with_current_inventory_max_capacity(self, current_inventory_max_capacity: int) -> Inventory:
        self.current_inventory_max_capacity = current_inventory_max_capacity
        return self

    def with_created_at(self, created_at: int) -> Inventory:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Inventory:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Inventory:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:user:{userId}:inventory:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):user:(?P<userId>.+):inventory:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Inventory]:
        if data is None:
            return None
        return Inventory()\
            .with_inventory_id(data.get('inventoryId'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_current_inventory_capacity_usage(data.get('currentInventoryCapacityUsage'))\
            .with_current_inventory_max_capacity(data.get('currentInventoryMaxCapacity'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryId": self.inventory_id,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "currentInventoryCapacityUsage": self.current_inventory_capacity_usage,
            "currentInventoryMaxCapacity": self.current_inventory_max_capacity,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class CurrentItemModelMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentItemModelMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentItemModelMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentItemModelMaster]:
        if data is None:
            return None
        return CurrentItemModelMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class BigItemModel(core.Gs2Model):
    item_model_id: str = None
    name: str = None
    metadata: str = None

    def with_item_model_id(self, item_model_id: str) -> BigItemModel:
        self.item_model_id = item_model_id
        return self

    def with_name(self, name: str) -> BigItemModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> BigItemModel:
        self.metadata = metadata
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
        item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:big:model:{inventoryName}:item:{itemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
            itemName=item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BigItemModel]:
        if data is None:
            return None
        return BigItemModel()\
            .with_item_model_id(data.get('itemModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemModelId": self.item_model_id,
            "name": self.name,
            "metadata": self.metadata,
        }


class BigItemModelMaster(core.Gs2Model):
    item_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_item_model_id(self, item_model_id: str) -> BigItemModelMaster:
        self.item_model_id = item_model_id
        return self

    def with_name(self, name: str) -> BigItemModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> BigItemModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> BigItemModelMaster:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> BigItemModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BigItemModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> BigItemModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
        item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:big:model:{inventoryName}:item:{itemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
            itemName=item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BigItemModelMaster]:
        if data is None:
            return None
        return BigItemModelMaster()\
            .with_item_model_id(data.get('itemModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemModelId": self.item_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class BigInventoryModel(core.Gs2Model):
    inventory_model_id: str = None
    name: str = None
    metadata: str = None
    big_item_models: List[BigItemModel] = None

    def with_inventory_model_id(self, inventory_model_id: str) -> BigInventoryModel:
        self.inventory_model_id = inventory_model_id
        return self

    def with_name(self, name: str) -> BigInventoryModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> BigInventoryModel:
        self.metadata = metadata
        return self

    def with_big_item_models(self, big_item_models: List[BigItemModel]) -> BigInventoryModel:
        self.big_item_models = big_item_models
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:big:model:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BigInventoryModel]:
        if data is None:
            return None
        return BigInventoryModel()\
            .with_inventory_model_id(data.get('inventoryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_big_item_models(None if data.get('bigItemModels') is None else [
                BigItemModel.from_dict(data.get('bigItemModels')[i])
                for i in range(len(data.get('bigItemModels')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryModelId": self.inventory_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "bigItemModels": None if self.big_item_models is None else [
                self.big_item_models[i].to_dict() if self.big_item_models[i] else None
                for i in range(len(self.big_item_models))
            ],
        }


class BigInventoryModelMaster(core.Gs2Model):
    inventory_model_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_inventory_model_id(self, inventory_model_id: str) -> BigInventoryModelMaster:
        self.inventory_model_id = inventory_model_id
        return self

    def with_name(self, name: str) -> BigInventoryModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> BigInventoryModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> BigInventoryModelMaster:
        self.description = description
        return self

    def with_created_at(self, created_at: int) -> BigInventoryModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> BigInventoryModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> BigInventoryModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:big:model:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):big:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BigInventoryModelMaster]:
        if data is None:
            return None
        return BigInventoryModelMaster()\
            .with_inventory_model_id(data.get('inventoryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryModelId": self.inventory_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class SimpleItemModel(core.Gs2Model):
    item_model_id: str = None
    name: str = None
    metadata: str = None

    def with_item_model_id(self, item_model_id: str) -> SimpleItemModel:
        self.item_model_id = item_model_id
        return self

    def with_name(self, name: str) -> SimpleItemModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SimpleItemModel:
        self.metadata = metadata
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
        item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:simple:model:{inventoryName}:item:{itemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
            itemName=item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SimpleItemModel]:
        if data is None:
            return None
        return SimpleItemModel()\
            .with_item_model_id(data.get('itemModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemModelId": self.item_model_id,
            "name": self.name,
            "metadata": self.metadata,
        }


class SimpleItemModelMaster(core.Gs2Model):
    item_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_item_model_id(self, item_model_id: str) -> SimpleItemModelMaster:
        self.item_model_id = item_model_id
        return self

    def with_name(self, name: str) -> SimpleItemModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> SimpleItemModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> SimpleItemModelMaster:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> SimpleItemModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SimpleItemModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SimpleItemModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
        item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:simple:model:{inventoryName}:item:{itemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
            itemName=item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SimpleItemModelMaster]:
        if data is None:
            return None
        return SimpleItemModelMaster()\
            .with_item_model_id(data.get('itemModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemModelId": self.item_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class SimpleInventoryModel(core.Gs2Model):
    inventory_model_id: str = None
    name: str = None
    metadata: str = None
    simple_item_models: List[SimpleItemModel] = None

    def with_inventory_model_id(self, inventory_model_id: str) -> SimpleInventoryModel:
        self.inventory_model_id = inventory_model_id
        return self

    def with_name(self, name: str) -> SimpleInventoryModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SimpleInventoryModel:
        self.metadata = metadata
        return self

    def with_simple_item_models(self, simple_item_models: List[SimpleItemModel]) -> SimpleInventoryModel:
        self.simple_item_models = simple_item_models
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:simple:model:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SimpleInventoryModel]:
        if data is None:
            return None
        return SimpleInventoryModel()\
            .with_inventory_model_id(data.get('inventoryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_simple_item_models(None if data.get('simpleItemModels') is None else [
                SimpleItemModel.from_dict(data.get('simpleItemModels')[i])
                for i in range(len(data.get('simpleItemModels')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryModelId": self.inventory_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "simpleItemModels": None if self.simple_item_models is None else [
                self.simple_item_models[i].to_dict() if self.simple_item_models[i] else None
                for i in range(len(self.simple_item_models))
            ],
        }


class SimpleInventoryModelMaster(core.Gs2Model):
    inventory_model_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_inventory_model_id(self, inventory_model_id: str) -> SimpleInventoryModelMaster:
        self.inventory_model_id = inventory_model_id
        return self

    def with_name(self, name: str) -> SimpleInventoryModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SimpleInventoryModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> SimpleInventoryModelMaster:
        self.description = description
        return self

    def with_created_at(self, created_at: int) -> SimpleInventoryModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SimpleInventoryModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SimpleInventoryModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:simple:model:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):simple:model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SimpleInventoryModelMaster]:
        if data is None:
            return None
        return SimpleInventoryModelMaster()\
            .with_inventory_model_id(data.get('inventoryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryModelId": self.inventory_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class ItemModel(core.Gs2Model):
    item_model_id: str = None
    name: str = None
    metadata: str = None
    stacking_limit: int = None
    allow_multiple_stacks: bool = None
    sort_value: int = None

    def with_item_model_id(self, item_model_id: str) -> ItemModel:
        self.item_model_id = item_model_id
        return self

    def with_name(self, name: str) -> ItemModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> ItemModel:
        self.metadata = metadata
        return self

    def with_stacking_limit(self, stacking_limit: int) -> ItemModel:
        self.stacking_limit = stacking_limit
        return self

    def with_allow_multiple_stacks(self, allow_multiple_stacks: bool) -> ItemModel:
        self.allow_multiple_stacks = allow_multiple_stacks
        return self

    def with_sort_value(self, sort_value: int) -> ItemModel:
        self.sort_value = sort_value
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
        item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:model:{inventoryName}:item:{itemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
            itemName=item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ItemModel]:
        if data is None:
            return None
        return ItemModel()\
            .with_item_model_id(data.get('itemModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_stacking_limit(data.get('stackingLimit'))\
            .with_allow_multiple_stacks(data.get('allowMultipleStacks'))\
            .with_sort_value(data.get('sortValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemModelId": self.item_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "stackingLimit": self.stacking_limit,
            "allowMultipleStacks": self.allow_multiple_stacks,
            "sortValue": self.sort_value,
        }


class ItemModelMaster(core.Gs2Model):
    item_model_id: str = None
    inventory_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    stacking_limit: int = None
    allow_multiple_stacks: bool = None
    sort_value: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_item_model_id(self, item_model_id: str) -> ItemModelMaster:
        self.item_model_id = item_model_id
        return self

    def with_inventory_name(self, inventory_name: str) -> ItemModelMaster:
        self.inventory_name = inventory_name
        return self

    def with_name(self, name: str) -> ItemModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> ItemModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> ItemModelMaster:
        self.metadata = metadata
        return self

    def with_stacking_limit(self, stacking_limit: int) -> ItemModelMaster:
        self.stacking_limit = stacking_limit
        return self

    def with_allow_multiple_stacks(self, allow_multiple_stacks: bool) -> ItemModelMaster:
        self.allow_multiple_stacks = allow_multiple_stacks
        return self

    def with_sort_value(self, sort_value: int) -> ItemModelMaster:
        self.sort_value = sort_value
        return self

    def with_created_at(self, created_at: int) -> ItemModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ItemModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> ItemModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
        item_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:model:{inventoryName}:item:{itemName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
            itemName=item_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    @classmethod
    def get_item_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+):item:(?P<itemName>.+)', grn)
        if match is None:
            return None
        return match.group('item_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ItemModelMaster]:
        if data is None:
            return None
        return ItemModelMaster()\
            .with_item_model_id(data.get('itemModelId'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_stacking_limit(data.get('stackingLimit'))\
            .with_allow_multiple_stacks(data.get('allowMultipleStacks'))\
            .with_sort_value(data.get('sortValue'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "itemModelId": self.item_model_id,
            "inventoryName": self.inventory_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "stackingLimit": self.stacking_limit,
            "allowMultipleStacks": self.allow_multiple_stacks,
            "sortValue": self.sort_value,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class InventoryModel(core.Gs2Model):
    inventory_model_id: str = None
    name: str = None
    metadata: str = None
    initial_capacity: int = None
    max_capacity: int = None
    protect_referenced_item: bool = None
    item_models: List[ItemModel] = None

    def with_inventory_model_id(self, inventory_model_id: str) -> InventoryModel:
        self.inventory_model_id = inventory_model_id
        return self

    def with_name(self, name: str) -> InventoryModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> InventoryModel:
        self.metadata = metadata
        return self

    def with_initial_capacity(self, initial_capacity: int) -> InventoryModel:
        self.initial_capacity = initial_capacity
        return self

    def with_max_capacity(self, max_capacity: int) -> InventoryModel:
        self.max_capacity = max_capacity
        return self

    def with_protect_referenced_item(self, protect_referenced_item: bool) -> InventoryModel:
        self.protect_referenced_item = protect_referenced_item
        return self

    def with_item_models(self, item_models: List[ItemModel]) -> InventoryModel:
        self.item_models = item_models
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:model:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[InventoryModel]:
        if data is None:
            return None
        return InventoryModel()\
            .with_inventory_model_id(data.get('inventoryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_protect_referenced_item(data.get('protectReferencedItem'))\
            .with_item_models(None if data.get('itemModels') is None else [
                ItemModel.from_dict(data.get('itemModels')[i])
                for i in range(len(data.get('itemModels')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryModelId": self.inventory_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "initialCapacity": self.initial_capacity,
            "maxCapacity": self.max_capacity,
            "protectReferencedItem": self.protect_referenced_item,
            "itemModels": None if self.item_models is None else [
                self.item_models[i].to_dict() if self.item_models[i] else None
                for i in range(len(self.item_models))
            ],
        }


class InventoryModelMaster(core.Gs2Model):
    inventory_model_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    initial_capacity: int = None
    max_capacity: int = None
    protect_referenced_item: bool = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_inventory_model_id(self, inventory_model_id: str) -> InventoryModelMaster:
        self.inventory_model_id = inventory_model_id
        return self

    def with_name(self, name: str) -> InventoryModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> InventoryModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> InventoryModelMaster:
        self.description = description
        return self

    def with_initial_capacity(self, initial_capacity: int) -> InventoryModelMaster:
        self.initial_capacity = initial_capacity
        return self

    def with_max_capacity(self, max_capacity: int) -> InventoryModelMaster:
        self.max_capacity = max_capacity
        return self

    def with_protect_referenced_item(self, protect_referenced_item: bool) -> InventoryModelMaster:
        self.protect_referenced_item = protect_referenced_item
        return self

    def with_created_at(self, created_at: int) -> InventoryModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> InventoryModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> InventoryModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        inventory_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}:model:{inventoryName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            inventoryName=inventory_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_inventory_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+):model:(?P<inventoryName>.+)', grn)
        if match is None:
            return None
        return match.group('inventory_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[InventoryModelMaster]:
        if data is None:
            return None
        return InventoryModelMaster()\
            .with_inventory_model_id(data.get('inventoryModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_protect_referenced_item(data.get('protectReferencedItem'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "inventoryModelId": self.inventory_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "initialCapacity": self.initial_capacity,
            "maxCapacity": self.max_capacity,
            "protectReferencedItem": self.protect_referenced_item,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    acquire_script: ScriptSetting = None
    overflow_script: ScriptSetting = None
    consume_script: ScriptSetting = None
    simple_item_acquire_script: ScriptSetting = None
    simple_item_consume_script: ScriptSetting = None
    big_item_acquire_script: ScriptSetting = None
    big_item_consume_script: ScriptSetting = None
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

    def with_acquire_script(self, acquire_script: ScriptSetting) -> Namespace:
        self.acquire_script = acquire_script
        return self

    def with_overflow_script(self, overflow_script: ScriptSetting) -> Namespace:
        self.overflow_script = overflow_script
        return self

    def with_consume_script(self, consume_script: ScriptSetting) -> Namespace:
        self.consume_script = consume_script
        return self

    def with_simple_item_acquire_script(self, simple_item_acquire_script: ScriptSetting) -> Namespace:
        self.simple_item_acquire_script = simple_item_acquire_script
        return self

    def with_simple_item_consume_script(self, simple_item_consume_script: ScriptSetting) -> Namespace:
        self.simple_item_consume_script = simple_item_consume_script
        return self

    def with_big_item_acquire_script(self, big_item_acquire_script: ScriptSetting) -> Namespace:
        self.big_item_acquire_script = big_item_acquire_script
        return self

    def with_big_item_consume_script(self, big_item_consume_script: ScriptSetting) -> Namespace:
        self.big_item_consume_script = big_item_consume_script
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
        return 'grn:gs2:{region}:{ownerId}:inventory:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):inventory:(?P<namespaceName>.+)', grn)
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
            .with_acquire_script(ScriptSetting.from_dict(data.get('acquireScript')))\
            .with_overflow_script(ScriptSetting.from_dict(data.get('overflowScript')))\
            .with_consume_script(ScriptSetting.from_dict(data.get('consumeScript')))\
            .with_simple_item_acquire_script(ScriptSetting.from_dict(data.get('simpleItemAcquireScript')))\
            .with_simple_item_consume_script(ScriptSetting.from_dict(data.get('simpleItemConsumeScript')))\
            .with_big_item_acquire_script(ScriptSetting.from_dict(data.get('bigItemAcquireScript')))\
            .with_big_item_consume_script(ScriptSetting.from_dict(data.get('bigItemConsumeScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "acquireScript": self.acquire_script.to_dict() if self.acquire_script else None,
            "overflowScript": self.overflow_script.to_dict() if self.overflow_script else None,
            "consumeScript": self.consume_script.to_dict() if self.consume_script else None,
            "simpleItemAcquireScript": self.simple_item_acquire_script.to_dict() if self.simple_item_acquire_script else None,
            "simpleItemConsumeScript": self.simple_item_consume_script.to_dict() if self.simple_item_consume_script else None,
            "bigItemAcquireScript": self.big_item_acquire_script.to_dict() if self.big_item_acquire_script else None,
            "bigItemConsumeScript": self.big_item_consume_script.to_dict() if self.big_item_consume_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }