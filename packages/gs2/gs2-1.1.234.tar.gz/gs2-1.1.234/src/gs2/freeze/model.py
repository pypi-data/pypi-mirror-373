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


class Microservice(core.Gs2Model):
    name: str = None
    version: str = None

    def with_name(self, name: str) -> Microservice:
        self.name = name
        return self

    def with_version(self, version: str) -> Microservice:
        self.version = version
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
    ) -> Optional[Microservice]:
        if data is None:
            return None
        return Microservice()\
            .with_name(data.get('name'))\
            .with_version(data.get('version'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
        }


class Output(core.Gs2Model):
    output_id: str = None
    name: str = None
    text: str = None
    created_at: int = None
    revision: int = None

    def with_output_id(self, output_id: str) -> Output:
        self.output_id = output_id
        return self

    def with_name(self, name: str) -> Output:
        self.name = name
        return self

    def with_text(self, text: str) -> Output:
        self.text = text
        return self

    def with_created_at(self, created_at: int) -> Output:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Output:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        stage_name,
        output_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:freeze:{stageName}:output:{outputName}'.format(
            region=region,
            ownerId=owner_id,
            stageName=stage_name,
            outputName=output_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):freeze:(?P<stageName>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):freeze:(?P<stageName>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_stage_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):freeze:(?P<stageName>.+):output:(?P<outputName>.+)', grn)
        if match is None:
            return None
        return match.group('stage_name')

    @classmethod
    def get_output_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):freeze:(?P<stageName>.+):output:(?P<outputName>.+)', grn)
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
            .with_text(data.get('text'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outputId": self.output_id,
            "name": self.name,
            "text": self.text,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Stage(core.Gs2Model):
    stage_id: str = None
    name: str = None
    source_stage_name: str = None
    sort_number: int = None
    status: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_stage_id(self, stage_id: str) -> Stage:
        self.stage_id = stage_id
        return self

    def with_name(self, name: str) -> Stage:
        self.name = name
        return self

    def with_source_stage_name(self, source_stage_name: str) -> Stage:
        self.source_stage_name = source_stage_name
        return self

    def with_sort_number(self, sort_number: int) -> Stage:
        self.sort_number = sort_number
        return self

    def with_status(self, status: str) -> Stage:
        self.status = status
        return self

    def with_created_at(self, created_at: int) -> Stage:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Stage:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Stage:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        stage_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:freeze:{stageName}'.format(
            region=region,
            ownerId=owner_id,
            stageName=stage_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):freeze:(?P<stageName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):freeze:(?P<stageName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_stage_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):freeze:(?P<stageName>.+)', grn)
        if match is None:
            return None
        return match.group('stage_name')

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
    ) -> Optional[Stage]:
        if data is None:
            return None
        return Stage()\
            .with_stage_id(data.get('stageId'))\
            .with_name(data.get('name'))\
            .with_source_stage_name(data.get('sourceStageName'))\
            .with_sort_number(data.get('sortNumber'))\
            .with_status(data.get('status'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stageId": self.stage_id,
            "name": self.name,
            "sourceStageName": self.source_stage_name,
            "sortNumber": self.sort_number,
            "status": self.status,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }