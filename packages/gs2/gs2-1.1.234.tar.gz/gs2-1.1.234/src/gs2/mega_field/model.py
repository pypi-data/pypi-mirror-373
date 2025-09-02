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


class Vector(core.Gs2Model):
    x: float = None
    y: float = None
    z: float = None

    def with_x(self, x: float) -> Vector:
        self.x = x
        return self

    def with_y(self, y: float) -> Vector:
        self.y = y
        return self

    def with_z(self, z: float) -> Vector:
        self.z = z
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
    ) -> Optional[Vector]:
        if data is None:
            return None
        return Vector()\
            .with_x(data.get('x'))\
            .with_y(data.get('y'))\
            .with_z(data.get('z'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }


class Scope(core.Gs2Model):
    layer_name: str = None
    r: float = None
    limit: int = None

    def with_layer_name(self, layer_name: str) -> Scope:
        self.layer_name = layer_name
        return self

    def with_r(self, r: float) -> Scope:
        self.r = r
        return self

    def with_limit(self, limit: int) -> Scope:
        self.limit = limit
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
    ) -> Optional[Scope]:
        if data is None:
            return None
        return Scope()\
            .with_layer_name(data.get('layerName'))\
            .with_r(data.get('r'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layerName": self.layer_name,
            "r": self.r,
            "limit": self.limit,
        }


class MyPosition(core.Gs2Model):
    position: Position = None
    vector: Vector = None
    r: float = None

    def with_position(self, position: Position) -> MyPosition:
        self.position = position
        return self

    def with_vector(self, vector: Vector) -> MyPosition:
        self.vector = vector
        return self

    def with_r(self, r: float) -> MyPosition:
        self.r = r
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
    ) -> Optional[MyPosition]:
        if data is None:
            return None
        return MyPosition()\
            .with_position(Position.from_dict(data.get('position')))\
            .with_vector(Vector.from_dict(data.get('vector')))\
            .with_r(data.get('r'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position.to_dict() if self.position else None,
            "vector": self.vector.to_dict() if self.vector else None,
            "r": self.r,
        }


class Position(core.Gs2Model):
    x: float = None
    y: float = None
    z: float = None

    def with_x(self, x: float) -> Position:
        self.x = x
        return self

    def with_y(self, y: float) -> Position:
        self.y = y
        return self

    def with_z(self, z: float) -> Position:
        self.z = z
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
    ) -> Optional[Position]:
        if data is None:
            return None
        return Position()\
            .with_x(data.get('x'))\
            .with_y(data.get('y'))\
            .with_z(data.get('z'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }


class Spatial(core.Gs2Model):
    spatial_id: str = None
    user_id: str = None
    area_model_name: str = None
    layer_model_name: str = None
    position: Position = None
    vector: Vector = None
    r: float = None
    last_sync_at: int = None
    created_at: int = None

    def with_spatial_id(self, spatial_id: str) -> Spatial:
        self.spatial_id = spatial_id
        return self

    def with_user_id(self, user_id: str) -> Spatial:
        self.user_id = user_id
        return self

    def with_area_model_name(self, area_model_name: str) -> Spatial:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> Spatial:
        self.layer_model_name = layer_model_name
        return self

    def with_position(self, position: Position) -> Spatial:
        self.position = position
        return self

    def with_vector(self, vector: Vector) -> Spatial:
        self.vector = vector
        return self

    def with_r(self, r: float) -> Spatial:
        self.r = r
        return self

    def with_last_sync_at(self, last_sync_at: int) -> Spatial:
        self.last_sync_at = last_sync_at
        return self

    def with_created_at(self, created_at: int) -> Spatial:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        area_model_name,
        layer_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:megaField:{namespaceName}:user:{userId}:spatial:{areaModelName}:{layerModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            areaModelName=area_model_name,
            layerModelName=layer_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):user:(?P<userId>.+):spatial:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):user:(?P<userId>.+):spatial:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):user:(?P<userId>.+):spatial:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):user:(?P<userId>.+):spatial:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_area_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):user:(?P<userId>.+):spatial:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('area_model_name')

    @classmethod
    def get_layer_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):user:(?P<userId>.+):spatial:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('layer_model_name')

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
    ) -> Optional[Spatial]:
        if data is None:
            return None
        return Spatial()\
            .with_spatial_id(data.get('spatialId'))\
            .with_user_id(data.get('userId'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_position(Position.from_dict(data.get('position')))\
            .with_vector(Vector.from_dict(data.get('vector')))\
            .with_r(data.get('r'))\
            .with_last_sync_at(data.get('lastSyncAt'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spatialId": self.spatial_id,
            "userId": self.user_id,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "position": self.position.to_dict() if self.position else None,
            "vector": self.vector.to_dict() if self.vector else None,
            "r": self.r,
            "lastSyncAt": self.last_sync_at,
            "createdAt": self.created_at,
        }


class Layer(core.Gs2Model):
    layer_id: str = None
    area_model_name: str = None
    layer_model_name: str = None
    number_of_min_entries: int = None
    number_of_max_entries: int = None
    created_at: int = None

    def with_layer_id(self, layer_id: str) -> Layer:
        self.layer_id = layer_id
        return self

    def with_area_model_name(self, area_model_name: str) -> Layer:
        self.area_model_name = area_model_name
        return self

    def with_layer_model_name(self, layer_model_name: str) -> Layer:
        self.layer_model_name = layer_model_name
        return self

    def with_number_of_min_entries(self, number_of_min_entries: int) -> Layer:
        self.number_of_min_entries = number_of_min_entries
        return self

    def with_number_of_max_entries(self, number_of_max_entries: int) -> Layer:
        self.number_of_max_entries = number_of_max_entries
        return self

    def with_created_at(self, created_at: int) -> Layer:
        self.created_at = created_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        area_model_name,
        layer_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:megaField:{namespaceName}:layer:{areaModelName}:{layerModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            areaModelName=area_model_name,
            layerModelName=layer_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):layer:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):layer:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):layer:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_area_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):layer:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('area_model_name')

    @classmethod
    def get_layer_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):layer:(?P<areaModelName>.+):(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('layer_model_name')

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
    ) -> Optional[Layer]:
        if data is None:
            return None
        return Layer()\
            .with_layer_id(data.get('layerId'))\
            .with_area_model_name(data.get('areaModelName'))\
            .with_layer_model_name(data.get('layerModelName'))\
            .with_number_of_min_entries(data.get('numberOfMinEntries'))\
            .with_number_of_max_entries(data.get('numberOfMaxEntries'))\
            .with_created_at(data.get('createdAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layerId": self.layer_id,
            "areaModelName": self.area_model_name,
            "layerModelName": self.layer_model_name,
            "numberOfMinEntries": self.number_of_min_entries,
            "numberOfMaxEntries": self.number_of_max_entries,
            "createdAt": self.created_at,
        }


class CurrentFieldMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentFieldMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentFieldMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:megaField:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentFieldMaster]:
        if data is None:
            return None
        return CurrentFieldMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class LayerModelMaster(core.Gs2Model):
    layer_model_master_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_layer_model_master_id(self, layer_model_master_id: str) -> LayerModelMaster:
        self.layer_model_master_id = layer_model_master_id
        return self

    def with_name(self, name: str) -> LayerModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> LayerModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> LayerModelMaster:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> LayerModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> LayerModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> LayerModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        area_model_name,
        layer_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:megaField:{namespaceName}:model:area:{areaModelName}:layer:{layerModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            areaModelName=area_model_name,
            layerModelName=layer_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_area_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('area_model_name')

    @classmethod
    def get_layer_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('layer_model_name')

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
    ) -> Optional[LayerModelMaster]:
        if data is None:
            return None
        return LayerModelMaster()\
            .with_layer_model_master_id(data.get('layerModelMasterId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layerModelMasterId": self.layer_model_master_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class LayerModel(core.Gs2Model):
    layer_model_id: str = None
    name: str = None
    metadata: str = None

    def with_layer_model_id(self, layer_model_id: str) -> LayerModel:
        self.layer_model_id = layer_model_id
        return self

    def with_name(self, name: str) -> LayerModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> LayerModel:
        self.metadata = metadata
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        area_model_name,
        layer_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:megaField:{namespaceName}:model:area:{areaModelName}:layer:{layerModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            areaModelName=area_model_name,
            layerModelName=layer_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_area_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('area_model_name')

    @classmethod
    def get_layer_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+):layer:(?P<layerModelName>.+)', grn)
        if match is None:
            return None
        return match.group('layer_model_name')

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
    ) -> Optional[LayerModel]:
        if data is None:
            return None
        return LayerModel()\
            .with_layer_model_id(data.get('layerModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layerModelId": self.layer_model_id,
            "name": self.name,
            "metadata": self.metadata,
        }


class AreaModelMaster(core.Gs2Model):
    area_model_master_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_area_model_master_id(self, area_model_master_id: str) -> AreaModelMaster:
        self.area_model_master_id = area_model_master_id
        return self

    def with_name(self, name: str) -> AreaModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> AreaModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> AreaModelMaster:
        self.metadata = metadata
        return self

    def with_created_at(self, created_at: int) -> AreaModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> AreaModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> AreaModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        area_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:megaField:{namespaceName}:master:area:{areaModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            areaModelName=area_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):master:area:(?P<areaModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):master:area:(?P<areaModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):master:area:(?P<areaModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_area_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):master:area:(?P<areaModelName>.+)', grn)
        if match is None:
            return None
        return match.group('area_model_name')

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
    ) -> Optional[AreaModelMaster]:
        if data is None:
            return None
        return AreaModelMaster()\
            .with_area_model_master_id(data.get('areaModelMasterId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "areaModelMasterId": self.area_model_master_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class AreaModel(core.Gs2Model):
    area_model_id: str = None
    name: str = None
    metadata: str = None
    layer_models: List[LayerModel] = None

    def with_area_model_id(self, area_model_id: str) -> AreaModel:
        self.area_model_id = area_model_id
        return self

    def with_name(self, name: str) -> AreaModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> AreaModel:
        self.metadata = metadata
        return self

    def with_layer_models(self, layer_models: List[LayerModel]) -> AreaModel:
        self.layer_models = layer_models
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        area_model_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:megaField:{namespaceName}:model:area:{areaModelName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            areaModelName=area_model_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_area_model_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+):model:area:(?P<areaModelName>.+)', grn)
        if match is None:
            return None
        return match.group('area_model_name')

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
    ) -> Optional[AreaModel]:
        if data is None:
            return None
        return AreaModel()\
            .with_area_model_id(data.get('areaModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_layer_models(None if data.get('layerModels') is None else [
                LayerModel.from_dict(data.get('layerModels')[i])
                for i in range(len(data.get('layerModels')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "areaModelId": self.area_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "layerModels": None if self.layer_models is None else [
                self.layer_models[i].to_dict() if self.layer_models[i] else None
                for i in range(len(self.layer_models))
            ],
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
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
        return 'grn:gs2:{region}:{ownerId}:megaField:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):megaField:(?P<namespaceName>.+)', grn)
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
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }