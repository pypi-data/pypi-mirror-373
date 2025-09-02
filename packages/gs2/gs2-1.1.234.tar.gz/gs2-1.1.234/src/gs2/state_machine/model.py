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


class RandomUsed(core.Gs2Model):
    category: int = None
    used: int = None

    def with_category(self, category: int) -> RandomUsed:
        self.category = category
        return self

    def with_used(self, used: int) -> RandomUsed:
        self.used = used
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
    ) -> Optional[RandomUsed]:
        if data is None:
            return None
        return RandomUsed()\
            .with_category(data.get('category'))\
            .with_used(data.get('used'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "used": self.used,
        }


class RandomStatus(core.Gs2Model):
    seed: int = None
    used: List[RandomUsed] = None

    def with_seed(self, seed: int) -> RandomStatus:
        self.seed = seed
        return self

    def with_used(self, used: List[RandomUsed]) -> RandomStatus:
        self.used = used
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
    ) -> Optional[RandomStatus]:
        if data is None:
            return None
        return RandomStatus()\
            .with_seed(data.get('seed'))\
            .with_used(None if data.get('used') is None else [
                RandomUsed.from_dict(data.get('used')[i])
                for i in range(len(data.get('used')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "used": None if self.used is None else [
                self.used[i].to_dict() if self.used[i] else None
                for i in range(len(self.used))
            ],
        }


class EmitEvent(core.Gs2Model):
    event: str = None
    parameters: str = None
    timestamp: int = None

    def with_event(self, event: str) -> EmitEvent:
        self.event = event
        return self

    def with_parameters(self, parameters: str) -> EmitEvent:
        self.parameters = parameters
        return self

    def with_timestamp(self, timestamp: int) -> EmitEvent:
        self.timestamp = timestamp
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
    ) -> Optional[EmitEvent]:
        if data is None:
            return None
        return EmitEvent()\
            .with_event(data.get('event'))\
            .with_parameters(data.get('parameters'))\
            .with_timestamp(data.get('timestamp'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
        }


class ChangeStateEvent(core.Gs2Model):
    task_name: str = None
    hash: str = None
    timestamp: int = None

    def with_task_name(self, task_name: str) -> ChangeStateEvent:
        self.task_name = task_name
        return self

    def with_hash(self, hash: str) -> ChangeStateEvent:
        self.hash = hash
        return self

    def with_timestamp(self, timestamp: int) -> ChangeStateEvent:
        self.timestamp = timestamp
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
    ) -> Optional[ChangeStateEvent]:
        if data is None:
            return None
        return ChangeStateEvent()\
            .with_task_name(data.get('taskName'))\
            .with_hash(data.get('hash'))\
            .with_timestamp(data.get('timestamp'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "taskName": self.task_name,
            "hash": self.hash,
            "timestamp": self.timestamp,
        }


class Event(core.Gs2Model):
    event_type: str = None
    change_state_event: ChangeStateEvent = None
    emit_event: EmitEvent = None

    def with_event_type(self, event_type: str) -> Event:
        self.event_type = event_type
        return self

    def with_change_state_event(self, change_state_event: ChangeStateEvent) -> Event:
        self.change_state_event = change_state_event
        return self

    def with_emit_event(self, emit_event: EmitEvent) -> Event:
        self.emit_event = emit_event
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
    ) -> Optional[Event]:
        if data is None:
            return None
        return Event()\
            .with_event_type(data.get('eventType'))\
            .with_change_state_event(ChangeStateEvent.from_dict(data.get('changeStateEvent')))\
            .with_emit_event(EmitEvent.from_dict(data.get('emitEvent')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eventType": self.event_type,
            "changeStateEvent": self.change_state_event.to_dict() if self.change_state_event else None,
            "emitEvent": self.emit_event.to_dict() if self.emit_event else None,
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


class Variable(core.Gs2Model):
    state_machine_name: str = None
    value: str = None

    def with_state_machine_name(self, state_machine_name: str) -> Variable:
        self.state_machine_name = state_machine_name
        return self

    def with_value(self, value: str) -> Variable:
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
    ) -> Optional[Variable]:
        if data is None:
            return None
        return Variable()\
            .with_state_machine_name(data.get('stateMachineName'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stateMachineName": self.state_machine_name,
            "value": self.value,
        }


class StackEntry(core.Gs2Model):
    state_machine_name: str = None
    task_name: str = None

    def with_state_machine_name(self, state_machine_name: str) -> StackEntry:
        self.state_machine_name = state_machine_name
        return self

    def with_task_name(self, task_name: str) -> StackEntry:
        self.task_name = task_name
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
    ) -> Optional[StackEntry]:
        if data is None:
            return None
        return StackEntry()\
            .with_state_machine_name(data.get('stateMachineName'))\
            .with_task_name(data.get('taskName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stateMachineName": self.state_machine_name,
            "taskName": self.task_name,
        }


class Status(core.Gs2Model):
    status_id: str = None
    user_id: str = None
    name: str = None
    state_machine_version: int = None
    enable_speculative_execution: str = None
    state_machine_definition: str = None
    random_status: RandomStatus = None
    stacks: List[StackEntry] = None
    variables: List[Variable] = None
    status: str = None
    last_error: str = None
    transition_count: int = None
    created_at: int = None
    updated_at: int = None

    def with_status_id(self, status_id: str) -> Status:
        self.status_id = status_id
        return self

    def with_user_id(self, user_id: str) -> Status:
        self.user_id = user_id
        return self

    def with_name(self, name: str) -> Status:
        self.name = name
        return self

    def with_state_machine_version(self, state_machine_version: int) -> Status:
        self.state_machine_version = state_machine_version
        return self

    def with_enable_speculative_execution(self, enable_speculative_execution: str) -> Status:
        self.enable_speculative_execution = enable_speculative_execution
        return self

    def with_state_machine_definition(self, state_machine_definition: str) -> Status:
        self.state_machine_definition = state_machine_definition
        return self

    def with_random_status(self, random_status: RandomStatus) -> Status:
        self.random_status = random_status
        return self

    def with_stacks(self, stacks: List[StackEntry]) -> Status:
        self.stacks = stacks
        return self

    def with_variables(self, variables: List[Variable]) -> Status:
        self.variables = variables
        return self

    def with_status(self, status: str) -> Status:
        self.status = status
        return self

    def with_last_error(self, last_error: str) -> Status:
        self.last_error = last_error
        return self

    def with_transition_count(self, transition_count: int) -> Status:
        self.transition_count = transition_count
        return self

    def with_created_at(self, created_at: int) -> Status:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Status:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        status_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:stateMachine:{namespaceName}:user:{userId}:status:{statusName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            statusName=status_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<statusName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<statusName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<statusName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<statusName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_status_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):user:(?P<userId>.+):status:(?P<statusName>.+)', grn)
        if match is None:
            return None
        return match.group('status_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Status]:
        if data is None:
            return None
        return Status()\
            .with_status_id(data.get('statusId'))\
            .with_user_id(data.get('userId'))\
            .with_name(data.get('name'))\
            .with_state_machine_version(data.get('stateMachineVersion'))\
            .with_enable_speculative_execution(data.get('enableSpeculativeExecution'))\
            .with_state_machine_definition(data.get('stateMachineDefinition'))\
            .with_random_status(RandomStatus.from_dict(data.get('randomStatus')))\
            .with_stacks(None if data.get('stacks') is None else [
                StackEntry.from_dict(data.get('stacks')[i])
                for i in range(len(data.get('stacks')))
            ])\
            .with_variables(None if data.get('variables') is None else [
                Variable.from_dict(data.get('variables')[i])
                for i in range(len(data.get('variables')))
            ])\
            .with_status(data.get('status'))\
            .with_last_error(data.get('lastError'))\
            .with_transition_count(data.get('transitionCount'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statusId": self.status_id,
            "userId": self.user_id,
            "name": self.name,
            "stateMachineVersion": self.state_machine_version,
            "enableSpeculativeExecution": self.enable_speculative_execution,
            "stateMachineDefinition": self.state_machine_definition,
            "randomStatus": self.random_status.to_dict() if self.random_status else None,
            "stacks": None if self.stacks is None else [
                self.stacks[i].to_dict() if self.stacks[i] else None
                for i in range(len(self.stacks))
            ],
            "variables": None if self.variables is None else [
                self.variables[i].to_dict() if self.variables[i] else None
                for i in range(len(self.variables))
            ],
            "status": self.status,
            "lastError": self.last_error,
            "transitionCount": self.transition_count,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class StateMachineMaster(core.Gs2Model):
    state_machine_id: str = None
    main_state_machine_name: str = None
    payload: str = None
    version: int = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_state_machine_id(self, state_machine_id: str) -> StateMachineMaster:
        self.state_machine_id = state_machine_id
        return self

    def with_main_state_machine_name(self, main_state_machine_name: str) -> StateMachineMaster:
        self.main_state_machine_name = main_state_machine_name
        return self

    def with_payload(self, payload: str) -> StateMachineMaster:
        self.payload = payload
        return self

    def with_version(self, version: int) -> StateMachineMaster:
        self.version = version
        return self

    def with_created_at(self, created_at: int) -> StateMachineMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> StateMachineMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> StateMachineMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        version,
    ):
        return 'grn:gs2:{region}:{ownerId}:stateMachine:{namespaceName}:master:stateMachine:{version}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            version=version,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):master:stateMachine:(?P<version>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):master:stateMachine:(?P<version>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):master:stateMachine:(?P<version>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_version_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+):master:stateMachine:(?P<version>.+)', grn)
        if match is None:
            return None
        return match.group('version')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[StateMachineMaster]:
        if data is None:
            return None
        return StateMachineMaster()\
            .with_state_machine_id(data.get('stateMachineId'))\
            .with_main_state_machine_name(data.get('mainStateMachineName'))\
            .with_payload(data.get('payload'))\
            .with_version(data.get('version'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stateMachineId": self.state_machine_id,
            "mainStateMachineName": self.main_state_machine_name,
            "payload": self.payload,
            "version": self.version,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    support_speculative_execution: str = None
    transaction_setting: TransactionSetting = None
    start_script: ScriptSetting = None
    pass_script: ScriptSetting = None
    error_script: ScriptSetting = None
    lowest_state_machine_version: int = None
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

    def with_support_speculative_execution(self, support_speculative_execution: str) -> Namespace:
        self.support_speculative_execution = support_speculative_execution
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> Namespace:
        self.transaction_setting = transaction_setting
        return self

    def with_start_script(self, start_script: ScriptSetting) -> Namespace:
        self.start_script = start_script
        return self

    def with_pass_script(self, pass_script: ScriptSetting) -> Namespace:
        self.pass_script = pass_script
        return self

    def with_error_script(self, error_script: ScriptSetting) -> Namespace:
        self.error_script = error_script
        return self

    def with_lowest_state_machine_version(self, lowest_state_machine_version: int) -> Namespace:
        self.lowest_state_machine_version = lowest_state_machine_version
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
        return 'grn:gs2:{region}:{ownerId}:stateMachine:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):stateMachine:(?P<namespaceName>.+)', grn)
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
            .with_support_speculative_execution(data.get('supportSpeculativeExecution'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_start_script(ScriptSetting.from_dict(data.get('startScript')))\
            .with_pass_script(ScriptSetting.from_dict(data.get('passScript')))\
            .with_error_script(ScriptSetting.from_dict(data.get('errorScript')))\
            .with_lowest_state_machine_version(data.get('lowestStateMachineVersion'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "supportSpeculativeExecution": self.support_speculative_execution,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "startScript": self.start_script.to_dict() if self.start_script else None,
            "passScript": self.pass_script.to_dict() if self.pass_script else None,
            "errorScript": self.error_script.to_dict() if self.error_script else None,
            "lowestStateMachineVersion": self.lowest_state_machine_version,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }