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


class ChangeSet(core.Gs2Model):
    resource_name: str = None
    resource_type: str = None
    operation: str = None

    def with_resource_name(self, resource_name: str) -> ChangeSet:
        self.resource_name = resource_name
        return self

    def with_resource_type(self, resource_type: str) -> ChangeSet:
        self.resource_type = resource_type
        return self

    def with_operation(self, operation: str) -> ChangeSet:
        self.operation = operation
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
    ) -> Optional[ChangeSet]:
        if data is None:
            return None
        return ChangeSet()\
            .with_resource_name(data.get('resourceName'))\
            .with_resource_type(data.get('resourceType'))\
            .with_operation(data.get('operation'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resourceName": self.resource_name,
            "resourceType": self.resource_type,
            "operation": self.operation,
        }


class OutputField(core.Gs2Model):
    name: str = None
    field_name: str = None

    def with_name(self, name: str) -> OutputField:
        self.name = name
        return self

    def with_field_name(self, field_name: str) -> OutputField:
        self.field_name = field_name
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
    ) -> Optional[OutputField]:
        if data is None:
            return None
        return OutputField()\
            .with_name(data.get('name'))\
            .with_field_name(data.get('fieldName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "fieldName": self.field_name,
        }


class Output(core.Gs2Model):
    output_id: str = None
    name: str = None
    value: str = None
    created_at: int = None

    def with_output_id(self, output_id: str) -> Output:
        self.output_id = output_id
        return self

    def with_name(self, name: str) -> Output:
        self.name = name
        return self

    def with_value(self, value: str) -> Output:
        self.value = value
        return self

    def with_created_at(self, created_at: int) -> Output:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        stack_name,
        output_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:deploy:{stackName}:output:{outputName}'.format(
            region=region,
            ownerId=owner_id,
            stackName=stack_name,
            outputName=output_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_stack_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('stack_name')

    @classmethod
    def get_output_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('output_name')

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
    ) -> Optional[Output]:
        if data is None:
            return None
        return Output()\
            .with_output_id(data.get('outputId'))\
            .with_name(data.get('name'))\
            .with_value(data.get('value'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outputId": self.output_id,
            "name": self.name,
            "value": self.value,
            "createdAt": self.created_at,
        }


class Event(core.Gs2Model):
    event_id: str = None
    name: str = None
    resource_name: str = None
    type: str = None
    message: str = None
    event_at: int = None
    revision: int = None

    def with_event_id(self, event_id: str) -> Event:
        self.event_id = event_id
        return self

    def with_name(self, name: str) -> Event:
        self.name = name
        return self

    def with_resource_name(self, resource_name: str) -> Event:
        self.resource_name = resource_name
        return self

    def with_type(self, type: str) -> Event:
        self.type = type
        return self

    def with_message(self, message: str) -> Event:
        self.message = message
        return self

    def with_event_at(self, event_at: int) -> Event:
        self.event_at = event_at
        return self

    def with_revision(self, revision: int) -> Event:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        stack_name,
        event_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:deploy:{stackName}:event:{eventName}'.format(
            region=region,
            ownerId=owner_id,
            stackName=stack_name,
            eventName=event_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_stack_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('stack_name')

    @classmethod
    def get_event_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):event:(?P<eventName>.+)', grn)
        if match is None:
            return None
        return match.group('event_name')

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
            .with_event_id(data.get('eventId'))\
            .with_name(data.get('name'))\
            .with_resource_name(data.get('resourceName'))\
            .with_type(data.get('type'))\
            .with_message(data.get('message'))\
            .with_event_at(data.get('eventAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "eventId": self.event_id,
            "name": self.name,
            "resourceName": self.resource_name,
            "type": self.type,
            "message": self.message,
            "eventAt": self.event_at,
            "revision": self.revision,
        }


class Resource(core.Gs2Model):
    resource_id: str = None
    type: str = None
    name: str = None
    request: str = None
    response: str = None
    rollback_context: str = None
    rollback_request: str = None
    rollback_after: List[str] = None
    output_fields: List[OutputField] = None
    work_id: str = None
    created_at: int = None

    def with_resource_id(self, resource_id: str) -> Resource:
        self.resource_id = resource_id
        return self

    def with_type(self, type: str) -> Resource:
        self.type = type
        return self

    def with_name(self, name: str) -> Resource:
        self.name = name
        return self

    def with_request(self, request: str) -> Resource:
        self.request = request
        return self

    def with_response(self, response: str) -> Resource:
        self.response = response
        return self

    def with_rollback_context(self, rollback_context: str) -> Resource:
        self.rollback_context = rollback_context
        return self

    def with_rollback_request(self, rollback_request: str) -> Resource:
        self.rollback_request = rollback_request
        return self

    def with_rollback_after(self, rollback_after: List[str]) -> Resource:
        self.rollback_after = rollback_after
        return self

    def with_output_fields(self, output_fields: List[OutputField]) -> Resource:
        self.output_fields = output_fields
        return self

    def with_work_id(self, work_id: str) -> Resource:
        self.work_id = work_id
        return self

    def with_created_at(self, created_at: int) -> Resource:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        stack_name,
        resource_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:deploy:{stackName}:resource:{resourceName}'.format(
            region=region,
            ownerId=owner_id,
            stackName=stack_name,
            resourceName=resource_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):resource:(?P<resourceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):resource:(?P<resourceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_stack_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):resource:(?P<resourceName>.+)', grn)
        if match is None:
            return None
        return match.group('stack_name')

    @classmethod
    def get_resource_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+):resource:(?P<resourceName>.+)', grn)
        if match is None:
            return None
        return match.group('resource_name')

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
    ) -> Optional[Resource]:
        if data is None:
            return None
        return Resource()\
            .with_resource_id(data.get('resourceId'))\
            .with_type(data.get('type'))\
            .with_name(data.get('name'))\
            .with_request(data.get('request'))\
            .with_response(data.get('response'))\
            .with_rollback_context(data.get('rollbackContext'))\
            .with_rollback_request(data.get('rollbackRequest'))\
            .with_rollback_after(None if data.get('rollbackAfter') is None else [
                data.get('rollbackAfter')[i]
                for i in range(len(data.get('rollbackAfter')))
            ])\
            .with_output_fields(None if data.get('outputFields') is None else [
                OutputField.from_dict(data.get('outputFields')[i])
                for i in range(len(data.get('outputFields')))
            ])\
            .with_work_id(data.get('workId'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resourceId": self.resource_id,
            "type": self.type,
            "name": self.name,
            "request": self.request,
            "response": self.response,
            "rollbackContext": self.rollback_context,
            "rollbackRequest": self.rollback_request,
            "rollbackAfter": None if self.rollback_after is None else [
                self.rollback_after[i]
                for i in range(len(self.rollback_after))
            ],
            "outputFields": None if self.output_fields is None else [
                self.output_fields[i].to_dict() if self.output_fields[i] else None
                for i in range(len(self.output_fields))
            ],
            "workId": self.work_id,
            "createdAt": self.created_at,
        }


class Stack(core.Gs2Model):
    stack_id: str = None
    name: str = None
    description: str = None
    template: str = None
    status: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_stack_id(self, stack_id: str) -> Stack:
        self.stack_id = stack_id
        return self

    def with_name(self, name: str) -> Stack:
        self.name = name
        return self

    def with_description(self, description: str) -> Stack:
        self.description = description
        return self

    def with_template(self, template: str) -> Stack:
        self.template = template
        return self

    def with_status(self, status: str) -> Stack:
        self.status = status
        return self

    def with_created_at(self, created_at: int) -> Stack:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Stack:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Stack:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        stack_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:deploy:{stackName}'.format(
            region=region,
            ownerId=owner_id,
            stackName=stack_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_stack_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):deploy:(?P<stackName>.+)', grn)
        if match is None:
            return None
        return match.group('stack_name')

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
    ) -> Optional[Stack]:
        if data is None:
            return None
        return Stack()\
            .with_stack_id(data.get('stackId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_template(data.get('template'))\
            .with_status(data.get('status'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackId": self.stack_id,
            "name": self.name,
            "description": self.description,
            "template": self.template,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }