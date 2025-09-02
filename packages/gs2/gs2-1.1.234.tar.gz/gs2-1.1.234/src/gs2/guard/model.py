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


class BlockingPolicyModel(core.Gs2Model):
    pass_services: List[str] = None
    default_restriction: str = None
    location_detection: str = None
    locations: List[str] = None
    location_restriction: str = None
    anonymous_ip_detection: str = None
    anonymous_ip_restriction: str = None
    hosting_provider_ip_detection: str = None
    hosting_provider_ip_restriction: str = None
    reputation_ip_detection: str = None
    reputation_ip_restriction: str = None
    ip_addresses_detection: str = None
    ip_addresses: List[str] = None
    ip_address_restriction: str = None

    def with_pass_services(self, pass_services: List[str]) -> BlockingPolicyModel:
        self.pass_services = pass_services
        return self

    def with_default_restriction(self, default_restriction: str) -> BlockingPolicyModel:
        self.default_restriction = default_restriction
        return self

    def with_location_detection(self, location_detection: str) -> BlockingPolicyModel:
        self.location_detection = location_detection
        return self

    def with_locations(self, locations: List[str]) -> BlockingPolicyModel:
        self.locations = locations
        return self

    def with_location_restriction(self, location_restriction: str) -> BlockingPolicyModel:
        self.location_restriction = location_restriction
        return self

    def with_anonymous_ip_detection(self, anonymous_ip_detection: str) -> BlockingPolicyModel:
        self.anonymous_ip_detection = anonymous_ip_detection
        return self

    def with_anonymous_ip_restriction(self, anonymous_ip_restriction: str) -> BlockingPolicyModel:
        self.anonymous_ip_restriction = anonymous_ip_restriction
        return self

    def with_hosting_provider_ip_detection(self, hosting_provider_ip_detection: str) -> BlockingPolicyModel:
        self.hosting_provider_ip_detection = hosting_provider_ip_detection
        return self

    def with_hosting_provider_ip_restriction(self, hosting_provider_ip_restriction: str) -> BlockingPolicyModel:
        self.hosting_provider_ip_restriction = hosting_provider_ip_restriction
        return self

    def with_reputation_ip_detection(self, reputation_ip_detection: str) -> BlockingPolicyModel:
        self.reputation_ip_detection = reputation_ip_detection
        return self

    def with_reputation_ip_restriction(self, reputation_ip_restriction: str) -> BlockingPolicyModel:
        self.reputation_ip_restriction = reputation_ip_restriction
        return self

    def with_ip_addresses_detection(self, ip_addresses_detection: str) -> BlockingPolicyModel:
        self.ip_addresses_detection = ip_addresses_detection
        return self

    def with_ip_addresses(self, ip_addresses: List[str]) -> BlockingPolicyModel:
        self.ip_addresses = ip_addresses
        return self

    def with_ip_address_restriction(self, ip_address_restriction: str) -> BlockingPolicyModel:
        self.ip_address_restriction = ip_address_restriction
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
    ) -> Optional[BlockingPolicyModel]:
        if data is None:
            return None
        return BlockingPolicyModel()\
            .with_pass_services(None if data.get('passServices') is None else [
                data.get('passServices')[i]
                for i in range(len(data.get('passServices')))
            ])\
            .with_default_restriction(data.get('defaultRestriction'))\
            .with_location_detection(data.get('locationDetection'))\
            .with_locations(None if data.get('locations') is None else [
                data.get('locations')[i]
                for i in range(len(data.get('locations')))
            ])\
            .with_location_restriction(data.get('locationRestriction'))\
            .with_anonymous_ip_detection(data.get('anonymousIpDetection'))\
            .with_anonymous_ip_restriction(data.get('anonymousIpRestriction'))\
            .with_hosting_provider_ip_detection(data.get('hostingProviderIpDetection'))\
            .with_hosting_provider_ip_restriction(data.get('hostingProviderIpRestriction'))\
            .with_reputation_ip_detection(data.get('reputationIpDetection'))\
            .with_reputation_ip_restriction(data.get('reputationIpRestriction'))\
            .with_ip_addresses_detection(data.get('ipAddressesDetection'))\
            .with_ip_addresses(None if data.get('ipAddresses') is None else [
                data.get('ipAddresses')[i]
                for i in range(len(data.get('ipAddresses')))
            ])\
            .with_ip_address_restriction(data.get('ipAddressRestriction'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passServices": None if self.pass_services is None else [
                self.pass_services[i]
                for i in range(len(self.pass_services))
            ],
            "defaultRestriction": self.default_restriction,
            "locationDetection": self.location_detection,
            "locations": None if self.locations is None else [
                self.locations[i]
                for i in range(len(self.locations))
            ],
            "locationRestriction": self.location_restriction,
            "anonymousIpDetection": self.anonymous_ip_detection,
            "anonymousIpRestriction": self.anonymous_ip_restriction,
            "hostingProviderIpDetection": self.hosting_provider_ip_detection,
            "hostingProviderIpRestriction": self.hosting_provider_ip_restriction,
            "reputationIpDetection": self.reputation_ip_detection,
            "reputationIpRestriction": self.reputation_ip_restriction,
            "ipAddressesDetection": self.ip_addresses_detection,
            "ipAddresses": None if self.ip_addresses is None else [
                self.ip_addresses[i]
                for i in range(len(self.ip_addresses))
            ],
            "ipAddressRestriction": self.ip_address_restriction,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    blocking_policy: BlockingPolicyModel = None
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

    def with_blocking_policy(self, blocking_policy: BlockingPolicyModel) -> Namespace:
        self.blocking_policy = blocking_policy
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
        return 'grn:gs2:{region}:{ownerId}:guard:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guard:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guard:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):guard:(?P<namespaceName>.+)', grn)
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
            .with_blocking_policy(BlockingPolicyModel.from_dict(data.get('blockingPolicy')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "blockingPolicy": self.blocking_policy.to_dict() if self.blocking_policy else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }