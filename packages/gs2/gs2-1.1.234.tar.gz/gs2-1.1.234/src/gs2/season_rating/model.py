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


class Vote(core.Gs2Model):
    vote_id: str = None
    season_name: str = None
    session_name: str = None
    written_ballots: List[WrittenBallot] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_vote_id(self, vote_id: str) -> Vote:
        self.vote_id = vote_id
        return self

    def with_season_name(self, season_name: str) -> Vote:
        self.season_name = season_name
        return self

    def with_session_name(self, session_name: str) -> Vote:
        self.session_name = session_name
        return self

    def with_written_ballots(self, written_ballots: List[WrittenBallot]) -> Vote:
        self.written_ballots = written_ballots
        return self

    def with_created_at(self, created_at: int) -> Vote:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Vote:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Vote:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        season_name,
        session_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:seasonRating:{namespaceName}:vote:{seasonName}:{sessionName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            seasonName=season_name,
            sessionName=session_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):vote:(?P<seasonName>.+):(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):vote:(?P<seasonName>.+):(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):vote:(?P<seasonName>.+):(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_season_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):vote:(?P<seasonName>.+):(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('season_name')

    @classmethod
    def get_session_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):vote:(?P<seasonName>.+):(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('session_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Vote]:
        if data is None:
            return None
        return Vote()\
            .with_vote_id(data.get('voteId'))\
            .with_season_name(data.get('seasonName'))\
            .with_session_name(data.get('sessionName'))\
            .with_written_ballots(None if data.get('writtenBallots') is None else [
                WrittenBallot.from_dict(data.get('writtenBallots')[i])
                for i in range(len(data.get('writtenBallots')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "voteId": self.vote_id,
            "seasonName": self.season_name,
            "sessionName": self.session_name,
            "writtenBallots": None if self.written_ballots is None else [
                self.written_ballots[i].to_dict() if self.written_ballots[i] else None
                for i in range(len(self.written_ballots))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class WrittenBallot(core.Gs2Model):
    ballot: Ballot = None
    game_results: List[GameResult] = None

    def with_ballot(self, ballot: Ballot) -> WrittenBallot:
        self.ballot = ballot
        return self

    def with_game_results(self, game_results: List[GameResult]) -> WrittenBallot:
        self.game_results = game_results
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[WrittenBallot]:
        if data is None:
            return None
        return WrittenBallot()\
            .with_ballot(Ballot.from_dict(data.get('ballot')))\
            .with_game_results(None if data.get('gameResults') is None else [
                GameResult.from_dict(data.get('gameResults')[i])
                for i in range(len(data.get('gameResults')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ballot": self.ballot.to_dict() if self.ballot else None,
            "gameResults": None if self.game_results is None else [
                self.game_results[i].to_dict() if self.game_results[i] else None
                for i in range(len(self.game_results))
            ],
        }


class SignedBallot(core.Gs2Model):
    body: str = None
    signature: str = None

    def with_body(self, body: str) -> SignedBallot:
        self.body = body
        return self

    def with_signature(self, signature: str) -> SignedBallot:
        self.signature = signature
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SignedBallot]:
        if data is None:
            return None
        return SignedBallot()\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body": self.body,
            "signature": self.signature,
        }


class Ballot(core.Gs2Model):
    user_id: str = None
    season_name: str = None
    session_name: str = None
    number_of_player: int = None

    def with_user_id(self, user_id: str) -> Ballot:
        self.user_id = user_id
        return self

    def with_season_name(self, season_name: str) -> Ballot:
        self.season_name = season_name
        return self

    def with_session_name(self, session_name: str) -> Ballot:
        self.session_name = session_name
        return self

    def with_number_of_player(self, number_of_player: int) -> Ballot:
        self.number_of_player = number_of_player
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Ballot]:
        if data is None:
            return None
        return Ballot()\
            .with_user_id(data.get('userId'))\
            .with_season_name(data.get('seasonName'))\
            .with_session_name(data.get('sessionName'))\
            .with_number_of_player(data.get('numberOfPlayer'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "seasonName": self.season_name,
            "sessionName": self.session_name,
            "numberOfPlayer": self.number_of_player,
        }


class GameResult(core.Gs2Model):
    rank: int = None
    user_id: str = None

    def with_rank(self, rank: int) -> GameResult:
        self.rank = rank
        return self

    def with_user_id(self, user_id: str) -> GameResult:
        self.user_id = user_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GameResult]:
        if data is None:
            return None
        return GameResult()\
            .with_rank(data.get('rank'))\
            .with_user_id(data.get('userId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rank": self.rank,
            "userId": self.user_id,
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
    enable_atomic_commit: bool = None
    transaction_use_distributor: bool = None
    acquire_action_use_job_queue: bool = None
    distributor_namespace_id: str = None
    queue_namespace_id: str = None

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
            .with_enable_atomic_commit(data.get('enableAtomicCommit'))\
            .with_transaction_use_distributor(data.get('transactionUseDistributor'))\
            .with_acquire_action_use_job_queue(data.get('acquireActionUseJobQueue'))\
            .with_distributor_namespace_id(data.get('distributorNamespaceId'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "enableAtomicCommit": self.enable_atomic_commit,
            "transactionUseDistributor": self.transaction_use_distributor,
            "acquireActionUseJobQueue": self.acquire_action_use_job_queue,
            "distributorNamespaceId": self.distributor_namespace_id,
            "queueNamespaceId": self.queue_namespace_id,
        }


class CurrentSeasonModelMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentSeasonModelMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentSeasonModelMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:seasonRating:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentSeasonModelMaster]:
        if data is None:
            return None
        return CurrentSeasonModelMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class TierModel(core.Gs2Model):
    metadata: str = None
    raise_rank_bonus: int = None
    entry_fee: int = None
    minimum_change_point: int = None
    maximum_change_point: int = None

    def with_metadata(self, metadata: str) -> TierModel:
        self.metadata = metadata
        return self

    def with_raise_rank_bonus(self, raise_rank_bonus: int) -> TierModel:
        self.raise_rank_bonus = raise_rank_bonus
        return self

    def with_entry_fee(self, entry_fee: int) -> TierModel:
        self.entry_fee = entry_fee
        return self

    def with_minimum_change_point(self, minimum_change_point: int) -> TierModel:
        self.minimum_change_point = minimum_change_point
        return self

    def with_maximum_change_point(self, maximum_change_point: int) -> TierModel:
        self.maximum_change_point = maximum_change_point
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TierModel]:
        if data is None:
            return None
        return TierModel()\
            .with_metadata(data.get('metadata'))\
            .with_raise_rank_bonus(data.get('raiseRankBonus'))\
            .with_entry_fee(data.get('entryFee'))\
            .with_minimum_change_point(data.get('minimumChangePoint'))\
            .with_maximum_change_point(data.get('maximumChangePoint'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metadata": self.metadata,
            "raiseRankBonus": self.raise_rank_bonus,
            "entryFee": self.entry_fee,
            "minimumChangePoint": self.minimum_change_point,
            "maximumChangePoint": self.maximum_change_point,
        }


class SeasonModel(core.Gs2Model):
    season_model_id: str = None
    name: str = None
    metadata: str = None
    tiers: List[TierModel] = None
    experience_model_id: str = None
    challenge_period_event_id: str = None

    def with_season_model_id(self, season_model_id: str) -> SeasonModel:
        self.season_model_id = season_model_id
        return self

    def with_name(self, name: str) -> SeasonModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SeasonModel:
        self.metadata = metadata
        return self

    def with_tiers(self, tiers: List[TierModel]) -> SeasonModel:
        self.tiers = tiers
        return self

    def with_experience_model_id(self, experience_model_id: str) -> SeasonModel:
        self.experience_model_id = experience_model_id
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> SeasonModel:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        season_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:seasonRating:{namespaceName}:model:{seasonName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            seasonName=season_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):model:(?P<seasonName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):model:(?P<seasonName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):model:(?P<seasonName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_season_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):model:(?P<seasonName>.+)', grn)
        if match is None:
            return None
        return match.group('season_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SeasonModel]:
        if data is None:
            return None
        return SeasonModel()\
            .with_season_model_id(data.get('seasonModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_tiers(None if data.get('tiers') is None else [
                TierModel.from_dict(data.get('tiers')[i])
                for i in range(len(data.get('tiers')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seasonModelId": self.season_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "tiers": None if self.tiers is None else [
                self.tiers[i].to_dict() if self.tiers[i] else None
                for i in range(len(self.tiers))
            ],
            "experienceModelId": self.experience_model_id,
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class SeasonModelMaster(core.Gs2Model):
    season_model_id: str = None
    name: str = None
    metadata: str = None
    description: str = None
    tiers: List[TierModel] = None
    experience_model_id: str = None
    challenge_period_event_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_season_model_id(self, season_model_id: str) -> SeasonModelMaster:
        self.season_model_id = season_model_id
        return self

    def with_name(self, name: str) -> SeasonModelMaster:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> SeasonModelMaster:
        self.metadata = metadata
        return self

    def with_description(self, description: str) -> SeasonModelMaster:
        self.description = description
        return self

    def with_tiers(self, tiers: List[TierModel]) -> SeasonModelMaster:
        self.tiers = tiers
        return self

    def with_experience_model_id(self, experience_model_id: str) -> SeasonModelMaster:
        self.experience_model_id = experience_model_id
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> SeasonModelMaster:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_created_at(self, created_at: int) -> SeasonModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SeasonModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> SeasonModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        season_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:seasonRating:{namespaceName}:model:{seasonName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            seasonName=season_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):model:(?P<seasonName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):model:(?P<seasonName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):model:(?P<seasonName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_season_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):model:(?P<seasonName>.+)', grn)
        if match is None:
            return None
        return match.group('season_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[SeasonModelMaster]:
        if data is None:
            return None
        return SeasonModelMaster()\
            .with_season_model_id(data.get('seasonModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_description(data.get('description'))\
            .with_tiers(None if data.get('tiers') is None else [
                TierModel.from_dict(data.get('tiers')[i])
                for i in range(len(data.get('tiers')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seasonModelId": self.season_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "description": self.description,
            "tiers": None if self.tiers is None else [
                self.tiers[i].to_dict() if self.tiers[i] else None
                for i in range(len(self.tiers))
            ],
            "experienceModelId": self.experience_model_id,
            "challengePeriodEventId": self.challenge_period_event_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class MatchSession(core.Gs2Model):
    session_id: str = None
    name: str = None
    created_at: int = None
    revision: int = None

    def with_session_id(self, session_id: str) -> MatchSession:
        self.session_id = session_id
        return self

    def with_name(self, name: str) -> MatchSession:
        self.name = name
        return self

    def with_created_at(self, created_at: int) -> MatchSession:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> MatchSession:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        session_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:seasonRating:{namespaceName}:session:{sessionName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            sessionName=session_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):session:(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):session:(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):session:(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_session_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+):session:(?P<sessionName>.+)', grn)
        if match is None:
            return None
        return match.group('session_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[MatchSession]:
        if data is None:
            return None
        return MatchSession()\
            .with_session_id(data.get('sessionId'))\
            .with_name(data.get('name'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sessionId": self.session_id,
            "name": self.name,
            "createdAt": self.created_at,
            "revision": self.revision,
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
        return 'grn:gs2:{region}:{ownerId}:seasonRating:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):seasonRating:(?P<namespaceName>.+)', grn)
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