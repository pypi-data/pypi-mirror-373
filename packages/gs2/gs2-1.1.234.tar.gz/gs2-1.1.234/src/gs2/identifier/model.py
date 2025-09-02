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


class TwoFactorAuthenticationSetting(core.Gs2Model):
    status: str = None

    def with_status(self, status: str) -> TwoFactorAuthenticationSetting:
        self.status = status
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
    ) -> Optional[TwoFactorAuthenticationSetting]:
        if data is None:
            return None
        return TwoFactorAuthenticationSetting()\
            .with_status(data.get('status'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
        }


class ProjectToken(core.Gs2Model):
    token: str = None

    def with_token(self, token: str) -> ProjectToken:
        self.token = token
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
    ) -> Optional[ProjectToken]:
        if data is None:
            return None
        return ProjectToken()\
            .with_token(data.get('token'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
        }


class AttachSecurityPolicy(core.Gs2Model):
    user_id: str = None
    security_policy_ids: List[str] = None
    attached_at: int = None
    revision: int = None

    def with_user_id(self, user_id: str) -> AttachSecurityPolicy:
        self.user_id = user_id
        return self

    def with_security_policy_ids(self, security_policy_ids: List[str]) -> AttachSecurityPolicy:
        self.security_policy_ids = security_policy_ids
        return self

    def with_attached_at(self, attached_at: int) -> AttachSecurityPolicy:
        self.attached_at = attached_at
        return self

    def with_revision(self, revision: int) -> AttachSecurityPolicy:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        owner_id,
        user_name,
    ):
        return 'grn:gs2::{ownerId}:identifier:user:{userName}'.format(
            ownerId=owner_id,
            userName=user_name,
        )

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2::(?P<ownerId>.+):identifier:user:(?P<userName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_user_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2::(?P<ownerId>.+):identifier:user:(?P<userName>.+)', grn)
        if match is None:
            return None
        return match.group('user_name')

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
    ) -> Optional[AttachSecurityPolicy]:
        if data is None:
            return None
        return AttachSecurityPolicy()\
            .with_user_id(data.get('userId'))\
            .with_security_policy_ids(None if data.get('securityPolicyIds') is None else [
                data.get('securityPolicyIds')[i]
                for i in range(len(data.get('securityPolicyIds')))
            ])\
            .with_attached_at(data.get('attachedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "securityPolicyIds": None if self.security_policy_ids is None else [
                self.security_policy_ids[i]
                for i in range(len(self.security_policy_ids))
            ],
            "attachedAt": self.attached_at,
            "revision": self.revision,
        }


class Password(core.Gs2Model):
    password_id: str = None
    user_id: str = None
    user_name: str = None
    enable_two_factor_authentication: str = None
    two_factor_authentication_setting: TwoFactorAuthenticationSetting = None
    created_at: int = None
    revision: int = None

    def with_password_id(self, password_id: str) -> Password:
        self.password_id = password_id
        return self

    def with_user_id(self, user_id: str) -> Password:
        self.user_id = user_id
        return self

    def with_user_name(self, user_name: str) -> Password:
        self.user_name = user_name
        return self

    def with_enable_two_factor_authentication(self, enable_two_factor_authentication: str) -> Password:
        self.enable_two_factor_authentication = enable_two_factor_authentication
        return self

    def with_two_factor_authentication_setting(self, two_factor_authentication_setting: TwoFactorAuthenticationSetting) -> Password:
        self.two_factor_authentication_setting = two_factor_authentication_setting
        return self

    def with_created_at(self, created_at: int) -> Password:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Password:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        owner_id,
        user_name,
    ):
        return 'grn:gs2::{ownerId}:identifier:user:{userName}'.format(
            ownerId=owner_id,
            userName=user_name,
        )

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2::(?P<ownerId>.+):identifier:user:(?P<userName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_user_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2::(?P<ownerId>.+):identifier:user:(?P<userName>.+)', grn)
        if match is None:
            return None
        return match.group('user_name')

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
    ) -> Optional[Password]:
        if data is None:
            return None
        return Password()\
            .with_password_id(data.get('passwordId'))\
            .with_user_id(data.get('userId'))\
            .with_user_name(data.get('userName'))\
            .with_enable_two_factor_authentication(data.get('enableTwoFactorAuthentication'))\
            .with_two_factor_authentication_setting(TwoFactorAuthenticationSetting.from_dict(data.get('twoFactorAuthenticationSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passwordId": self.password_id,
            "userId": self.user_id,
            "userName": self.user_name,
            "enableTwoFactorAuthentication": self.enable_two_factor_authentication,
            "twoFactorAuthenticationSetting": self.two_factor_authentication_setting.to_dict() if self.two_factor_authentication_setting else None,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class Identifier(core.Gs2Model):
    client_id: str = None
    user_name: str = None
    client_secret: str = None
    created_at: int = None
    revision: int = None

    def with_client_id(self, client_id: str) -> Identifier:
        self.client_id = client_id
        return self

    def with_user_name(self, user_name: str) -> Identifier:
        self.user_name = user_name
        return self

    def with_client_secret(self, client_secret: str) -> Identifier:
        self.client_secret = client_secret
        return self

    def with_created_at(self, created_at: int) -> Identifier:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> Identifier:
        self.revision = revision
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
    ) -> Optional[Identifier]:
        if data is None:
            return None
        return Identifier()\
            .with_client_id(data.get('clientId'))\
            .with_user_name(data.get('userName'))\
            .with_client_secret(data.get('clientSecret'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clientId": self.client_id,
            "userName": self.user_name,
            "clientSecret": self.client_secret,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class SecurityPolicy(core.Gs2Model):
    security_policy_id: str = None
    name: str = None
    description: str = None
    policy: str = None
    created_at: int = None
    updated_at: int = None

    def with_security_policy_id(self, security_policy_id: str) -> SecurityPolicy:
        self.security_policy_id = security_policy_id
        return self

    def with_name(self, name: str) -> SecurityPolicy:
        self.name = name
        return self

    def with_description(self, description: str) -> SecurityPolicy:
        self.description = description
        return self

    def with_policy(self, policy: str) -> SecurityPolicy:
        self.policy = policy
        return self

    def with_created_at(self, created_at: int) -> SecurityPolicy:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> SecurityPolicy:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        owner_id,
        security_policy_name,
    ):
        return 'grn:gs2::{ownerId}:identifier:securityPolicy:{securityPolicyName}'.format(
            ownerId=owner_id,
            securityPolicyName=security_policy_name,
        )

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2::(?P<ownerId>.+):identifier:securityPolicy:(?P<securityPolicyName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_security_policy_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2::(?P<ownerId>.+):identifier:securityPolicy:(?P<securityPolicyName>.+)', grn)
        if match is None:
            return None
        return match.group('security_policy_name')

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
    ) -> Optional[SecurityPolicy]:
        if data is None:
            return None
        return SecurityPolicy()\
            .with_security_policy_id(data.get('securityPolicyId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_policy(data.get('policy'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "securityPolicyId": self.security_policy_id,
            "name": self.name,
            "description": self.description,
            "policy": self.policy,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class User(core.Gs2Model):
    user_id: str = None
    name: str = None
    description: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_user_id(self, user_id: str) -> User:
        self.user_id = user_id
        return self

    def with_name(self, name: str) -> User:
        self.name = name
        return self

    def with_description(self, description: str) -> User:
        self.description = description
        return self

    def with_created_at(self, created_at: int) -> User:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> User:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> User:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        owner_id,
        user_name,
    ):
        return 'grn:gs2::{ownerId}:identifier:user:{userName}'.format(
            ownerId=owner_id,
            userName=user_name,
        )

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2::(?P<ownerId>.+):identifier:user:(?P<userName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_user_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2::(?P<ownerId>.+):identifier:user:(?P<userName>.+)', grn)
        if match is None:
            return None
        return match.group('user_name')

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
    ) -> Optional[User]:
        if data is None:
            return None
        return User()\
            .with_user_id(data.get('userId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "name": self.name,
            "description": self.description,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }