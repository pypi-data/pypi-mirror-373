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


class RankingReward(core.Gs2Model):
    threshold_rank: int = None
    metadata: str = None
    acquire_actions: List[AcquireAction] = None

    def with_threshold_rank(self, threshold_rank: int) -> RankingReward:
        self.threshold_rank = threshold_rank
        return self

    def with_metadata(self, metadata: str) -> RankingReward:
        self.metadata = metadata
        return self

    def with_acquire_actions(self, acquire_actions: List[AcquireAction]) -> RankingReward:
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
    ) -> Optional[RankingReward]:
        if data is None:
            return None
        return RankingReward()\
            .with_threshold_rank(data.get('thresholdRank'))\
            .with_metadata(data.get('metadata'))\
            .with_acquire_actions(None if data.get('acquireActions') is None else [
                AcquireAction.from_dict(data.get('acquireActions')[i])
                for i in range(len(data.get('acquireActions')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thresholdRank": self.threshold_rank,
            "metadata": self.metadata,
            "acquireActions": None if self.acquire_actions is None else [
                self.acquire_actions[i].to_dict() if self.acquire_actions[i] else None
                for i in range(len(self.acquire_actions))
            ],
        }


class SubscribeUser(core.Gs2Model):
    ranking_name: str = None
    user_id: str = None
    target_user_id: str = None

    def with_ranking_name(self, ranking_name: str) -> SubscribeUser:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> SubscribeUser:
        self.user_id = user_id
        return self

    def with_target_user_id(self, target_user_id: str) -> SubscribeUser:
        self.target_user_id = target_user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubscribeUser]:
        if data is None:
            return None
        return SubscribeUser()\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_id(data.get('targetUserId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "targetUserId": self.target_user_id,
        }


class CurrentRankingMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentRankingMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentRankingMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentRankingMaster]:
        if data is None:
            return None
        return CurrentRankingMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class SubscribeRankingData(core.Gs2Model):
    subscribe_ranking_data_id: str = None
    ranking_name: str = None
    season: int = None
    user_id: str = None
    index: int = None
    rank: int = None
    scorer_user_id: str = None
    score: int = None
    metadata: str = None
    invert_updated_at: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_subscribe_ranking_data_id(self, subscribe_ranking_data_id: str) -> SubscribeRankingData:
        self.subscribe_ranking_data_id = subscribe_ranking_data_id
        return self

    def with_ranking_name(self, ranking_name: str) -> SubscribeRankingData:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> SubscribeRankingData:
        self.season = season
        return self

    def with_user_id(self, user_id: str) -> SubscribeRankingData:
        self.user_id = user_id
        return self

    def with_index(self, index: int) -> SubscribeRankingData:
        self.index = index
        return self

    def with_rank(self, rank: int) -> SubscribeRankingData:
        self.rank = rank
        return self

    def with_scorer_user_id(self, scorer_user_id: str) -> SubscribeRankingData:
        self.scorer_user_id = scorer_user_id
        return self

    def with_score(self, score: int) -> SubscribeRankingData:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> SubscribeRankingData:
        self.metadata = metadata
        return self

    def with_invert_updated_at(self, invert_updated_at: int) -> SubscribeRankingData:
        self.invert_updated_at = invert_updated_at
        return self

    def with_created_at(self, created_at: int) -> SubscribeRankingData:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SubscribeRankingData:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SubscribeRankingData:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        ranking_name,
        season,
        scorer_user_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:user:{userId}:ranking:subscribe:{rankingName}:{season}:user:{scorerUserId}:score'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            rankingName=ranking_name,
            season=season,
            scorerUserId=scorer_user_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    @classmethod
    def get_season_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('season')

    @classmethod
    def get_scorer_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('scorer_user_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubscribeRankingData]:
        if data is None:
            return None
        return SubscribeRankingData()\
            .with_subscribe_ranking_data_id(data.get('subscribeRankingDataId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_user_id(data.get('userId'))\
            .with_index(data.get('index'))\
            .with_rank(data.get('rank'))\
            .with_scorer_user_id(data.get('scorerUserId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_invert_updated_at(data.get('invertUpdatedAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscribeRankingDataId": self.subscribe_ranking_data_id,
            "rankingName": self.ranking_name,
            "season": self.season,
            "userId": self.user_id,
            "index": self.index,
            "rank": self.rank,
            "scorerUserId": self.scorer_user_id,
            "score": self.score,
            "metadata": self.metadata,
            "invertUpdatedAt": self.invert_updated_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class SubscribeRankingScore(core.Gs2Model):
    subscribe_ranking_score_id: str = None
    ranking_name: str = None
    season: int = None
    user_id: str = None
    score: int = None
    metadata: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_subscribe_ranking_score_id(self, subscribe_ranking_score_id: str) -> SubscribeRankingScore:
        self.subscribe_ranking_score_id = subscribe_ranking_score_id
        return self

    def with_ranking_name(self, ranking_name: str) -> SubscribeRankingScore:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> SubscribeRankingScore:
        self.season = season
        return self

    def with_user_id(self, user_id: str) -> SubscribeRankingScore:
        self.user_id = user_id
        return self

    def with_score(self, score: int) -> SubscribeRankingScore:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> SubscribeRankingScore:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> SubscribeRankingScore:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SubscribeRankingScore:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SubscribeRankingScore:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        ranking_name,
        season,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:user:{userId}:ranking:subscribe:{rankingName}:{season}:score'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            rankingName=ranking_name,
            season=season,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    @classmethod
    def get_season_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):ranking:subscribe:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('season')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubscribeRankingScore]:
        if data is None:
            return None
        return SubscribeRankingScore()\
            .with_subscribe_ranking_score_id(data.get('subscribeRankingScoreId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_user_id(data.get('userId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscribeRankingScoreId": self.subscribe_ranking_score_id,
            "rankingName": self.ranking_name,
            "season": self.season,
            "userId": self.user_id,
            "score": self.score,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Subscribe(core.Gs2Model):
    subscribe_id: str = None
    ranking_name: str = None
    user_id: str = None
    target_user_ids: List[str] = None
    from_user_ids: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_subscribe_id(self, subscribe_id: str) -> Subscribe:
        self.subscribe_id = subscribe_id
        return self

    def with_ranking_name(self, ranking_name: str) -> Subscribe:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> Subscribe:
        self.user_id = user_id
        return self

    def with_target_user_ids(self, target_user_ids: List[str]) -> Subscribe:
        self.target_user_ids = target_user_ids
        return self

    def with_from_user_ids(self, from_user_ids: List[str]) -> Subscribe:
        self.from_user_ids = from_user_ids
        return self

    def with_created_at(self, created_at: int) -> Subscribe:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Subscribe:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Subscribe:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        ranking_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:user:{userId}:subscribe:{rankingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            rankingName=ranking_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Subscribe]:
        if data is None:
            return None
        return Subscribe()\
            .with_subscribe_id(data.get('subscribeId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_target_user_ids(None if data.get('targetUserIds') is None else [
                data.get('targetUserIds')[i]
                for i in range(len(data.get('targetUserIds')))
            ])\
            .with_from_user_ids(None if data.get('fromUserIds') is None else [
                data.get('fromUserIds')[i]
                for i in range(len(data.get('fromUserIds')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscribeId": self.subscribe_id,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "targetUserIds": None if self.target_user_ids is None else [
                self.target_user_ids[i]
                for i in range(len(self.target_user_ids))
            ],
            "fromUserIds": None if self.from_user_ids is None else [
                self.from_user_ids[i]
                for i in range(len(self.from_user_ids))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class SubscribeRankingModelMaster(core.Gs2Model):
    subscribe_ranking_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    entry_period_event_id: str = None
    access_period_event_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_subscribe_ranking_model_id(self, subscribe_ranking_model_id: str) -> SubscribeRankingModelMaster:
        self.subscribe_ranking_model_id = subscribe_ranking_model_id
        return self

    def with_name(self, name: str) -> SubscribeRankingModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> SubscribeRankingModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> SubscribeRankingModelMaster:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> SubscribeRankingModelMaster:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> SubscribeRankingModelMaster:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> SubscribeRankingModelMaster:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> SubscribeRankingModelMaster:
        self.order_direction = order_direction
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> SubscribeRankingModelMaster:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> SubscribeRankingModelMaster:
        self.access_period_event_id = access_period_event_id
        return self

    def with_created_at(self, created_at: int) -> SubscribeRankingModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SubscribeRankingModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SubscribeRankingModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        ranking_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:master:model:subscribe:{rankingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rankingName=ranking_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubscribeRankingModelMaster]:
        if data is None:
            return None
        return SubscribeRankingModelMaster()\
            .with_subscribe_ranking_model_id(data.get('subscribeRankingModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscribeRankingModelId": self.subscribe_ranking_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class SubscribeRankingModel(core.Gs2Model):
    subscribe_ranking_model_id: str = None
    name: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    entry_period_event_id: str = None
    access_period_event_id: str = None

    def with_subscribe_ranking_model_id(self, subscribe_ranking_model_id: str) -> SubscribeRankingModel:
        self.subscribe_ranking_model_id = subscribe_ranking_model_id
        return self

    def with_name(self, name: str) -> SubscribeRankingModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SubscribeRankingModel:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> SubscribeRankingModel:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> SubscribeRankingModel:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> SubscribeRankingModel:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> SubscribeRankingModel:
        self.order_direction = order_direction
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> SubscribeRankingModel:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> SubscribeRankingModel:
        self.access_period_event_id = access_period_event_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        ranking_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:subscribe:{rankingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rankingName=ranking_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):subscribe:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SubscribeRankingModel]:
        if data is None:
            return None
        return SubscribeRankingModel()\
            .with_subscribe_ranking_model_id(data.get('subscribeRankingModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_access_period_event_id(data.get('accessPeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subscribeRankingModelId": self.subscribe_ranking_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "entryPeriodEventId": self.entry_period_event_id,
            "accessPeriodEventId": self.access_period_event_id,
        }


class ClusterRankingData(core.Gs2Model):
    cluster_ranking_data_id: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    user_id: str = None
    index: int = None
    rank: int = None
    score: int = None
    metadata: str = None
    invert_updated_at: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_cluster_ranking_data_id(self, cluster_ranking_data_id: str) -> ClusterRankingData:
        self.cluster_ranking_data_id = cluster_ranking_data_id
        return self

    def with_ranking_name(self, ranking_name: str) -> ClusterRankingData:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> ClusterRankingData:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> ClusterRankingData:
        self.season = season
        return self

    def with_user_id(self, user_id: str) -> ClusterRankingData:
        self.user_id = user_id
        return self

    def with_index(self, index: int) -> ClusterRankingData:
        self.index = index
        return self

    def with_rank(self, rank: int) -> ClusterRankingData:
        self.rank = rank
        return self

    def with_score(self, score: int) -> ClusterRankingData:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> ClusterRankingData:
        self.metadata = metadata
        return self

    def with_invert_updated_at(self, invert_updated_at: int) -> ClusterRankingData:
        self.invert_updated_at = invert_updated_at
        return self

    def with_created_at(self, created_at: int) -> ClusterRankingData:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ClusterRankingData:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> ClusterRankingData:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        ranking_name,
        cluster_name,
        season,
        scorer_user_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:cluster:{rankingName}:ranking:cluster:{clusterName}:{season}:user:{scorerUserId}:score'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rankingName=ranking_name,
            clusterName=cluster_name,
            season=season,
            scorerUserId=scorer_user_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+):ranking:cluster:(?P<clusterName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+):ranking:cluster:(?P<clusterName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+):ranking:cluster:(?P<clusterName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+):ranking:cluster:(?P<clusterName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    @classmethod
    def get_cluster_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+):ranking:cluster:(?P<clusterName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('cluster_name')

    @classmethod
    def get_season_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+):ranking:cluster:(?P<clusterName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('season')

    @classmethod
    def get_scorer_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+):ranking:cluster:(?P<clusterName>.+):(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('scorer_user_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ClusterRankingData]:
        if data is None:
            return None
        return ClusterRankingData()\
            .with_cluster_ranking_data_id(data.get('clusterRankingDataId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_user_id(data.get('userId'))\
            .with_index(data.get('index'))\
            .with_rank(data.get('rank'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_invert_updated_at(data.get('invertUpdatedAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clusterRankingDataId": self.cluster_ranking_data_id,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "userId": self.user_id,
            "index": self.index,
            "rank": self.rank,
            "score": self.score,
            "metadata": self.metadata,
            "invertUpdatedAt": self.invert_updated_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class ClusterRankingReceivedReward(core.Gs2Model):
    cluster_ranking_received_reward_id: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    user_id: str = None
    received_at: int = None
    revision: int = None

    def with_cluster_ranking_received_reward_id(self, cluster_ranking_received_reward_id: str) -> ClusterRankingReceivedReward:
        self.cluster_ranking_received_reward_id = cluster_ranking_received_reward_id
        return self

    def with_ranking_name(self, ranking_name: str) -> ClusterRankingReceivedReward:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> ClusterRankingReceivedReward:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> ClusterRankingReceivedReward:
        self.season = season
        return self

    def with_user_id(self, user_id: str) -> ClusterRankingReceivedReward:
        self.user_id = user_id
        return self

    def with_received_at(self, received_at: int) -> ClusterRankingReceivedReward:
        self.received_at = received_at
        return self

    def with_revision(self, revision: int) -> ClusterRankingReceivedReward:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        ranking_name,
        cluster_name,
        season,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:user:{userId}:cluster:{rankingName}:{clusterName}:{season}:reward:received'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            rankingName=ranking_name,
            clusterName=cluster_name,
            season=season,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    @classmethod
    def get_cluster_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('cluster_name')

    @classmethod
    def get_season_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('season')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ClusterRankingReceivedReward]:
        if data is None:
            return None
        return ClusterRankingReceivedReward()\
            .with_cluster_ranking_received_reward_id(data.get('clusterRankingReceivedRewardId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_user_id(data.get('userId'))\
            .with_received_at(data.get('receivedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clusterRankingReceivedRewardId": self.cluster_ranking_received_reward_id,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "userId": self.user_id,
            "receivedAt": self.received_at,
            "revision": self.revision,
        }


class ClusterRankingScore(core.Gs2Model):
    cluster_ranking_score_id: str = None
    ranking_name: str = None
    cluster_name: str = None
    season: int = None
    user_id: str = None
    score: int = None
    metadata: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_cluster_ranking_score_id(self, cluster_ranking_score_id: str) -> ClusterRankingScore:
        self.cluster_ranking_score_id = cluster_ranking_score_id
        return self

    def with_ranking_name(self, ranking_name: str) -> ClusterRankingScore:
        self.ranking_name = ranking_name
        return self

    def with_cluster_name(self, cluster_name: str) -> ClusterRankingScore:
        self.cluster_name = cluster_name
        return self

    def with_season(self, season: int) -> ClusterRankingScore:
        self.season = season
        return self

    def with_user_id(self, user_id: str) -> ClusterRankingScore:
        self.user_id = user_id
        return self

    def with_score(self, score: int) -> ClusterRankingScore:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> ClusterRankingScore:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> ClusterRankingScore:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ClusterRankingScore:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> ClusterRankingScore:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        ranking_name,
        cluster_name,
        season,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:user:{userId}:cluster:{rankingName}:{clusterName}:{season}:score'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            rankingName=ranking_name,
            clusterName=cluster_name,
            season=season,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    @classmethod
    def get_cluster_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('cluster_name')

    @classmethod
    def get_season_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):cluster:(?P<rankingName>.+):(?P<clusterName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('season')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ClusterRankingScore]:
        if data is None:
            return None
        return ClusterRankingScore()\
            .with_cluster_ranking_score_id(data.get('clusterRankingScoreId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_cluster_name(data.get('clusterName'))\
            .with_season(data.get('season'))\
            .with_user_id(data.get('userId'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clusterRankingScoreId": self.cluster_ranking_score_id,
            "rankingName": self.ranking_name,
            "clusterName": self.cluster_name,
            "season": self.season,
            "userId": self.user_id,
            "score": self.score,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class ClusterRankingModelMaster(core.Gs2Model):
    cluster_ranking_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    cluster_type: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    entry_period_event_id: str = None
    ranking_rewards: List[RankingReward] = None
    access_period_event_id: str = None
    reward_calculation_index: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_cluster_ranking_model_id(self, cluster_ranking_model_id: str) -> ClusterRankingModelMaster:
        self.cluster_ranking_model_id = cluster_ranking_model_id
        return self

    def with_name(self, name: str) -> ClusterRankingModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> ClusterRankingModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> ClusterRankingModelMaster:
        self.metadata = metadata
        return self

    def with_cluster_type(self, cluster_type: str) -> ClusterRankingModelMaster:
        self.cluster_type = cluster_type
        return self

    def with_minimum_value(self, minimum_value: int) -> ClusterRankingModelMaster:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> ClusterRankingModelMaster:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> ClusterRankingModelMaster:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> ClusterRankingModelMaster:
        self.order_direction = order_direction
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> ClusterRankingModelMaster:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_ranking_rewards(self, ranking_rewards: List[RankingReward]) -> ClusterRankingModelMaster:
        self.ranking_rewards = ranking_rewards
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> ClusterRankingModelMaster:
        self.access_period_event_id = access_period_event_id
        return self

    def with_reward_calculation_index(self, reward_calculation_index: str) -> ClusterRankingModelMaster:
        self.reward_calculation_index = reward_calculation_index
        return self

    def with_created_at(self, created_at: int) -> ClusterRankingModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> ClusterRankingModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> ClusterRankingModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        ranking_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:master:model:cluster:{rankingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rankingName=ranking_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:cluster:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:cluster:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:cluster:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:cluster:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ClusterRankingModelMaster]:
        if data is None:
            return None
        return ClusterRankingModelMaster()\
            .with_cluster_ranking_model_id(data.get('clusterRankingModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_cluster_type(data.get('clusterType'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_ranking_rewards(None if data.get('rankingRewards') is None else [
                RankingReward.from_dict(data.get('rankingRewards')[i])
                for i in range(len(data.get('rankingRewards')))
            ])\
            .with_access_period_event_id(data.get('accessPeriodEventId'))\
            .with_reward_calculation_index(data.get('rewardCalculationIndex'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clusterRankingModelId": self.cluster_ranking_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "clusterType": self.cluster_type,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "entryPeriodEventId": self.entry_period_event_id,
            "rankingRewards": None if self.ranking_rewards is None else [
                self.ranking_rewards[i].to_dict() if self.ranking_rewards[i] else None
                for i in range(len(self.ranking_rewards))
            ],
            "accessPeriodEventId": self.access_period_event_id,
            "rewardCalculationIndex": self.reward_calculation_index,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class ClusterRankingModel(core.Gs2Model):
    cluster_ranking_model_id: str = None
    name: str = None
    metadata: str = None
    cluster_type: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    entry_period_event_id: str = None
    ranking_rewards: List[RankingReward] = None
    access_period_event_id: str = None
    reward_calculation_index: str = None

    def with_cluster_ranking_model_id(self, cluster_ranking_model_id: str) -> ClusterRankingModel:
        self.cluster_ranking_model_id = cluster_ranking_model_id
        return self

    def with_name(self, name: str) -> ClusterRankingModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> ClusterRankingModel:
        self.metadata = metadata
        return self

    def with_cluster_type(self, cluster_type: str) -> ClusterRankingModel:
        self.cluster_type = cluster_type
        return self

    def with_minimum_value(self, minimum_value: int) -> ClusterRankingModel:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> ClusterRankingModel:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> ClusterRankingModel:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> ClusterRankingModel:
        self.order_direction = order_direction
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> ClusterRankingModel:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_ranking_rewards(self, ranking_rewards: List[RankingReward]) -> ClusterRankingModel:
        self.ranking_rewards = ranking_rewards
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> ClusterRankingModel:
        self.access_period_event_id = access_period_event_id
        return self

    def with_reward_calculation_index(self, reward_calculation_index: str) -> ClusterRankingModel:
        self.reward_calculation_index = reward_calculation_index
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        ranking_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:cluster:{rankingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rankingName=ranking_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):cluster:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ClusterRankingModel]:
        if data is None:
            return None
        return ClusterRankingModel()\
            .with_cluster_ranking_model_id(data.get('clusterRankingModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_cluster_type(data.get('clusterType'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_ranking_rewards(None if data.get('rankingRewards') is None else [
                RankingReward.from_dict(data.get('rankingRewards')[i])
                for i in range(len(data.get('rankingRewards')))
            ])\
            .with_access_period_event_id(data.get('accessPeriodEventId'))\
            .with_reward_calculation_index(data.get('rewardCalculationIndex'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clusterRankingModelId": self.cluster_ranking_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "clusterType": self.cluster_type,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "entryPeriodEventId": self.entry_period_event_id,
            "rankingRewards": None if self.ranking_rewards is None else [
                self.ranking_rewards[i].to_dict() if self.ranking_rewards[i] else None
                for i in range(len(self.ranking_rewards))
            ],
            "accessPeriodEventId": self.access_period_event_id,
            "rewardCalculationIndex": self.reward_calculation_index,
        }


class GlobalRankingData(core.Gs2Model):
    global_ranking_data_id: str = None
    ranking_name: str = None
    season: int = None
    user_id: str = None
    index: int = None
    rank: int = None
    score: int = None
    metadata: str = None
    invert_updated_at: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_global_ranking_data_id(self, global_ranking_data_id: str) -> GlobalRankingData:
        self.global_ranking_data_id = global_ranking_data_id
        return self

    def with_ranking_name(self, ranking_name: str) -> GlobalRankingData:
        self.ranking_name = ranking_name
        return self

    def with_season(self, season: int) -> GlobalRankingData:
        self.season = season
        return self

    def with_user_id(self, user_id: str) -> GlobalRankingData:
        self.user_id = user_id
        return self

    def with_index(self, index: int) -> GlobalRankingData:
        self.index = index
        return self

    def with_rank(self, rank: int) -> GlobalRankingData:
        self.rank = rank
        return self

    def with_score(self, score: int) -> GlobalRankingData:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> GlobalRankingData:
        self.metadata = metadata
        return self

    def with_invert_updated_at(self, invert_updated_at: int) -> GlobalRankingData:
        self.invert_updated_at = invert_updated_at
        return self

    def with_created_at(self, created_at: int) -> GlobalRankingData:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> GlobalRankingData:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> GlobalRankingData:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        ranking_name,
        season,
        scorer_user_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:global:{rankingName}:ranking:global:{season}:user:{scorerUserId}:score'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rankingName=ranking_name,
            season=season,
            scorerUserId=scorer_user_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+):ranking:global:(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+):ranking:global:(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+):ranking:global:(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+):ranking:global:(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    @classmethod
    def get_season_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+):ranking:global:(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('season')

    @classmethod
    def get_scorer_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+):ranking:global:(?P<season>.+):user:(?P<scorerUserId>.+):score', grn)
        if match is None:
            return None
        return match.group('scorer_user_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GlobalRankingData]:
        if data is None:
            return None
        return GlobalRankingData()\
            .with_global_ranking_data_id(data.get('globalRankingDataId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_season(data.get('season'))\
            .with_user_id(data.get('userId'))\
            .with_index(data.get('index'))\
            .with_rank(data.get('rank'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_invert_updated_at(data.get('invertUpdatedAt'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "globalRankingDataId": self.global_ranking_data_id,
            "rankingName": self.ranking_name,
            "season": self.season,
            "userId": self.user_id,
            "index": self.index,
            "rank": self.rank,
            "score": self.score,
            "metadata": self.metadata,
            "invertUpdatedAt": self.invert_updated_at,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class GlobalRankingReceivedReward(core.Gs2Model):
    global_ranking_received_reward_id: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    received_at: int = None
    revision: int = None

    def with_global_ranking_received_reward_id(self, global_ranking_received_reward_id: str) -> GlobalRankingReceivedReward:
        self.global_ranking_received_reward_id = global_ranking_received_reward_id
        return self

    def with_ranking_name(self, ranking_name: str) -> GlobalRankingReceivedReward:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> GlobalRankingReceivedReward:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GlobalRankingReceivedReward:
        self.season = season
        return self

    def with_received_at(self, received_at: int) -> GlobalRankingReceivedReward:
        self.received_at = received_at
        return self

    def with_revision(self, revision: int) -> GlobalRankingReceivedReward:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        ranking_name,
        season,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:user:{userId}:global:{rankingName}:{season}:reward:received'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            rankingName=ranking_name,
            season=season,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    @classmethod
    def get_season_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):reward:received', grn)
        if match is None:
            return None
        return match.group('season')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GlobalRankingReceivedReward]:
        if data is None:
            return None
        return GlobalRankingReceivedReward()\
            .with_global_ranking_received_reward_id(data.get('globalRankingReceivedRewardId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_received_at(data.get('receivedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "globalRankingReceivedRewardId": self.global_ranking_received_reward_id,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "receivedAt": self.received_at,
            "revision": self.revision,
        }


class GlobalRankingScore(core.Gs2Model):
    global_ranking_score_id: str = None
    ranking_name: str = None
    user_id: str = None
    season: int = None
    score: int = None
    metadata: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_global_ranking_score_id(self, global_ranking_score_id: str) -> GlobalRankingScore:
        self.global_ranking_score_id = global_ranking_score_id
        return self

    def with_ranking_name(self, ranking_name: str) -> GlobalRankingScore:
        self.ranking_name = ranking_name
        return self

    def with_user_id(self, user_id: str) -> GlobalRankingScore:
        self.user_id = user_id
        return self

    def with_season(self, season: int) -> GlobalRankingScore:
        self.season = season
        return self

    def with_score(self, score: int) -> GlobalRankingScore:
        self.score = score
        return self

    def with_metadata(self, metadata: str) -> GlobalRankingScore:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> GlobalRankingScore:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> GlobalRankingScore:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> GlobalRankingScore:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        ranking_name,
        season,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:user:{userId}:global:{rankingName}:{season}:score'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            rankingName=ranking_name,
            season=season,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    @classmethod
    def get_season_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):user:(?P<userId>.+):global:(?P<rankingName>.+):(?P<season>.+):score', grn)
        if match is None:
            return None
        return match.group('season')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GlobalRankingScore]:
        if data is None:
            return None
        return GlobalRankingScore()\
            .with_global_ranking_score_id(data.get('globalRankingScoreId'))\
            .with_ranking_name(data.get('rankingName'))\
            .with_user_id(data.get('userId'))\
            .with_season(data.get('season'))\
            .with_score(data.get('score'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "globalRankingScoreId": self.global_ranking_score_id,
            "rankingName": self.ranking_name,
            "userId": self.user_id,
            "season": self.season,
            "score": self.score,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class GlobalRankingModelMaster(core.Gs2Model):
    global_ranking_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    entry_period_event_id: str = None
    ranking_rewards: List[RankingReward] = None
    access_period_event_id: str = None
    reward_calculation_index: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_global_ranking_model_id(self, global_ranking_model_id: str) -> GlobalRankingModelMaster:
        self.global_ranking_model_id = global_ranking_model_id
        return self

    def with_name(self, name: str) -> GlobalRankingModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> GlobalRankingModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> GlobalRankingModelMaster:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> GlobalRankingModelMaster:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> GlobalRankingModelMaster:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> GlobalRankingModelMaster:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> GlobalRankingModelMaster:
        self.order_direction = order_direction
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> GlobalRankingModelMaster:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_ranking_rewards(self, ranking_rewards: List[RankingReward]) -> GlobalRankingModelMaster:
        self.ranking_rewards = ranking_rewards
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> GlobalRankingModelMaster:
        self.access_period_event_id = access_period_event_id
        return self

    def with_reward_calculation_index(self, reward_calculation_index: str) -> GlobalRankingModelMaster:
        self.reward_calculation_index = reward_calculation_index
        return self

    def with_created_at(self, created_at: int) -> GlobalRankingModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> GlobalRankingModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> GlobalRankingModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        ranking_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:master:model:global:{rankingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rankingName=ranking_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:global:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:global:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:global:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):master:model:global:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GlobalRankingModelMaster]:
        if data is None:
            return None
        return GlobalRankingModelMaster()\
            .with_global_ranking_model_id(data.get('globalRankingModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_ranking_rewards(None if data.get('rankingRewards') is None else [
                RankingReward.from_dict(data.get('rankingRewards')[i])
                for i in range(len(data.get('rankingRewards')))
            ])\
            .with_access_period_event_id(data.get('accessPeriodEventId'))\
            .with_reward_calculation_index(data.get('rewardCalculationIndex'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "globalRankingModelId": self.global_ranking_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "entryPeriodEventId": self.entry_period_event_id,
            "rankingRewards": None if self.ranking_rewards is None else [
                self.ranking_rewards[i].to_dict() if self.ranking_rewards[i] else None
                for i in range(len(self.ranking_rewards))
            ],
            "accessPeriodEventId": self.access_period_event_id,
            "rewardCalculationIndex": self.reward_calculation_index,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class GlobalRankingModel(core.Gs2Model):
    global_ranking_model_id: str = None
    name: str = None
    metadata: str = None
    minimum_value: int = None
    maximum_value: int = None
    sum: bool = None
    order_direction: str = None
    entry_period_event_id: str = None
    ranking_rewards: List[RankingReward] = None
    access_period_event_id: str = None
    reward_calculation_index: str = None

    def with_global_ranking_model_id(self, global_ranking_model_id: str) -> GlobalRankingModel:
        self.global_ranking_model_id = global_ranking_model_id
        return self

    def with_name(self, name: str) -> GlobalRankingModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> GlobalRankingModel:
        self.metadata = metadata
        return self

    def with_minimum_value(self, minimum_value: int) -> GlobalRankingModel:
        self.minimum_value = minimum_value
        return self

    def with_maximum_value(self, maximum_value: int) -> GlobalRankingModel:
        self.maximum_value = maximum_value
        return self

    def with_sum(self, sum: bool) -> GlobalRankingModel:
        self.sum = sum
        return self

    def with_order_direction(self, order_direction: str) -> GlobalRankingModel:
        self.order_direction = order_direction
        return self

    def with_entry_period_event_id(self, entry_period_event_id: str) -> GlobalRankingModel:
        self.entry_period_event_id = entry_period_event_id
        return self

    def with_ranking_rewards(self, ranking_rewards: List[RankingReward]) -> GlobalRankingModel:
        self.ranking_rewards = ranking_rewards
        return self

    def with_access_period_event_id(self, access_period_event_id: str) -> GlobalRankingModel:
        self.access_period_event_id = access_period_event_id
        return self

    def with_reward_calculation_index(self, reward_calculation_index: str) -> GlobalRankingModel:
        self.reward_calculation_index = reward_calculation_index
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        ranking_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}:global:{rankingName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            rankingName=ranking_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_ranking_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+):global:(?P<rankingName>.+)', grn)
        if match is None:
            return None
        return match.group('ranking_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GlobalRankingModel]:
        if data is None:
            return None
        return GlobalRankingModel()\
            .with_global_ranking_model_id(data.get('globalRankingModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_minimum_value(data.get('minimumValue'))\
            .with_maximum_value(data.get('maximumValue'))\
            .with_sum(data.get('sum'))\
            .with_order_direction(data.get('orderDirection'))\
            .with_entry_period_event_id(data.get('entryPeriodEventId'))\
            .with_ranking_rewards(None if data.get('rankingRewards') is None else [
                RankingReward.from_dict(data.get('rankingRewards')[i])
                for i in range(len(data.get('rankingRewards')))
            ])\
            .with_access_period_event_id(data.get('accessPeriodEventId'))\
            .with_reward_calculation_index(data.get('rewardCalculationIndex'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "globalRankingModelId": self.global_ranking_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "minimumValue": self.minimum_value,
            "maximumValue": self.maximum_value,
            "sum": self.sum,
            "orderDirection": self.order_direction,
            "entryPeriodEventId": self.entry_period_event_id,
            "rankingRewards": None if self.ranking_rewards is None else [
                self.ranking_rewards[i].to_dict() if self.ranking_rewards[i] else None
                for i in range(len(self.ranking_rewards))
            ],
            "accessPeriodEventId": self.access_period_event_id,
            "rewardCalculationIndex": self.reward_calculation_index,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    transaction_setting: TransactionSetting = None
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

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
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
        return 'grn:gs2:{region}:{ownerId}:ranking2:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):ranking2:(?P<namespaceName>.+)', grn)
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }