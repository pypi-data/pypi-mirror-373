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

from .model import *


class DescribeUsersRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeUsersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeUsersRequest:
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
    ) -> Optional[DescribeUsersRequest]:
        if data is None:
            return None
        return DescribeUsersRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateUserRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None

    def with_name(self, name: str) -> CreateUserRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateUserRequest:
        self.description = description
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
    ) -> Optional[CreateUserRequest]:
        if data is None:
            return None
        return CreateUserRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
        }


class UpdateUserRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    description: str = None

    def with_user_name(self, user_name: str) -> UpdateUserRequest:
        self.user_name = user_name
        return self

    def with_description(self, description: str) -> UpdateUserRequest:
        self.description = description
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
    ) -> Optional[UpdateUserRequest]:
        if data is None:
            return None
        return UpdateUserRequest()\
            .with_user_name(data.get('userName'))\
            .with_description(data.get('description'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "description": self.description,
        }


class GetUserRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None

    def with_user_name(self, user_name: str) -> GetUserRequest:
        self.user_name = user_name
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
    ) -> Optional[GetUserRequest]:
        if data is None:
            return None
        return GetUserRequest()\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
        }


class DeleteUserRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None

    def with_user_name(self, user_name: str) -> DeleteUserRequest:
        self.user_name = user_name
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
    ) -> Optional[DeleteUserRequest]:
        if data is None:
            return None
        return DeleteUserRequest()\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
        }


class DescribeSecurityPoliciesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeSecurityPoliciesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSecurityPoliciesRequest:
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
    ) -> Optional[DescribeSecurityPoliciesRequest]:
        if data is None:
            return None
        return DescribeSecurityPoliciesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeCommonSecurityPoliciesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeCommonSecurityPoliciesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCommonSecurityPoliciesRequest:
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
    ) -> Optional[DescribeCommonSecurityPoliciesRequest]:
        if data is None:
            return None
        return DescribeCommonSecurityPoliciesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateSecurityPolicyRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    policy: str = None

    def with_name(self, name: str) -> CreateSecurityPolicyRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateSecurityPolicyRequest:
        self.description = description
        return self

    def with_policy(self, policy: str) -> CreateSecurityPolicyRequest:
        self.policy = policy
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
    ) -> Optional[CreateSecurityPolicyRequest]:
        if data is None:
            return None
        return CreateSecurityPolicyRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_policy(data.get('policy'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "policy": self.policy,
        }


class UpdateSecurityPolicyRequest(core.Gs2Request):

    context_stack: str = None
    security_policy_name: str = None
    description: str = None
    policy: str = None

    def with_security_policy_name(self, security_policy_name: str) -> UpdateSecurityPolicyRequest:
        self.security_policy_name = security_policy_name
        return self

    def with_description(self, description: str) -> UpdateSecurityPolicyRequest:
        self.description = description
        return self

    def with_policy(self, policy: str) -> UpdateSecurityPolicyRequest:
        self.policy = policy
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
    ) -> Optional[UpdateSecurityPolicyRequest]:
        if data is None:
            return None
        return UpdateSecurityPolicyRequest()\
            .with_security_policy_name(data.get('securityPolicyName'))\
            .with_description(data.get('description'))\
            .with_policy(data.get('policy'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "securityPolicyName": self.security_policy_name,
            "description": self.description,
            "policy": self.policy,
        }


class GetSecurityPolicyRequest(core.Gs2Request):

    context_stack: str = None
    security_policy_name: str = None

    def with_security_policy_name(self, security_policy_name: str) -> GetSecurityPolicyRequest:
        self.security_policy_name = security_policy_name
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
    ) -> Optional[GetSecurityPolicyRequest]:
        if data is None:
            return None
        return GetSecurityPolicyRequest()\
            .with_security_policy_name(data.get('securityPolicyName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "securityPolicyName": self.security_policy_name,
        }


class DeleteSecurityPolicyRequest(core.Gs2Request):

    context_stack: str = None
    security_policy_name: str = None

    def with_security_policy_name(self, security_policy_name: str) -> DeleteSecurityPolicyRequest:
        self.security_policy_name = security_policy_name
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
    ) -> Optional[DeleteSecurityPolicyRequest]:
        if data is None:
            return None
        return DeleteSecurityPolicyRequest()\
            .with_security_policy_name(data.get('securityPolicyName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "securityPolicyName": self.security_policy_name,
        }


class DescribeIdentifiersRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    page_token: str = None
    limit: int = None

    def with_user_name(self, user_name: str) -> DescribeIdentifiersRequest:
        self.user_name = user_name
        return self

    def with_page_token(self, page_token: str) -> DescribeIdentifiersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeIdentifiersRequest:
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
    ) -> Optional[DescribeIdentifiersRequest]:
        if data is None:
            return None
        return DescribeIdentifiersRequest()\
            .with_user_name(data.get('userName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateIdentifierRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None

    def with_user_name(self, user_name: str) -> CreateIdentifierRequest:
        self.user_name = user_name
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
    ) -> Optional[CreateIdentifierRequest]:
        if data is None:
            return None
        return CreateIdentifierRequest()\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
        }


class GetIdentifierRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    client_id: str = None

    def with_user_name(self, user_name: str) -> GetIdentifierRequest:
        self.user_name = user_name
        return self

    def with_client_id(self, client_id: str) -> GetIdentifierRequest:
        self.client_id = client_id
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
    ) -> Optional[GetIdentifierRequest]:
        if data is None:
            return None
        return GetIdentifierRequest()\
            .with_user_name(data.get('userName'))\
            .with_client_id(data.get('clientId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "clientId": self.client_id,
        }


class DeleteIdentifierRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    client_id: str = None

    def with_user_name(self, user_name: str) -> DeleteIdentifierRequest:
        self.user_name = user_name
        return self

    def with_client_id(self, client_id: str) -> DeleteIdentifierRequest:
        self.client_id = client_id
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
    ) -> Optional[DeleteIdentifierRequest]:
        if data is None:
            return None
        return DeleteIdentifierRequest()\
            .with_user_name(data.get('userName'))\
            .with_client_id(data.get('clientId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "clientId": self.client_id,
        }


class DescribeAttachedGuardsRequest(core.Gs2Request):

    context_stack: str = None
    client_id: str = None
    user_name: str = None

    def with_client_id(self, client_id: str) -> DescribeAttachedGuardsRequest:
        self.client_id = client_id
        return self

    def with_user_name(self, user_name: str) -> DescribeAttachedGuardsRequest:
        self.user_name = user_name
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
    ) -> Optional[DescribeAttachedGuardsRequest]:
        if data is None:
            return None
        return DescribeAttachedGuardsRequest()\
            .with_client_id(data.get('clientId'))\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clientId": self.client_id,
            "userName": self.user_name,
        }


class AttachGuardRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    client_id: str = None
    guard_namespace_id: str = None

    def with_user_name(self, user_name: str) -> AttachGuardRequest:
        self.user_name = user_name
        return self

    def with_client_id(self, client_id: str) -> AttachGuardRequest:
        self.client_id = client_id
        return self

    def with_guard_namespace_id(self, guard_namespace_id: str) -> AttachGuardRequest:
        self.guard_namespace_id = guard_namespace_id
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
    ) -> Optional[AttachGuardRequest]:
        if data is None:
            return None
        return AttachGuardRequest()\
            .with_user_name(data.get('userName'))\
            .with_client_id(data.get('clientId'))\
            .with_guard_namespace_id(data.get('guardNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "clientId": self.client_id,
            "guardNamespaceId": self.guard_namespace_id,
        }


class DetachGuardRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    client_id: str = None
    guard_namespace_id: str = None

    def with_user_name(self, user_name: str) -> DetachGuardRequest:
        self.user_name = user_name
        return self

    def with_client_id(self, client_id: str) -> DetachGuardRequest:
        self.client_id = client_id
        return self

    def with_guard_namespace_id(self, guard_namespace_id: str) -> DetachGuardRequest:
        self.guard_namespace_id = guard_namespace_id
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
    ) -> Optional[DetachGuardRequest]:
        if data is None:
            return None
        return DetachGuardRequest()\
            .with_user_name(data.get('userName'))\
            .with_client_id(data.get('clientId'))\
            .with_guard_namespace_id(data.get('guardNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "clientId": self.client_id,
            "guardNamespaceId": self.guard_namespace_id,
        }


class GetServiceVersionRequest(core.Gs2Request):

    context_stack: str = None

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
    ) -> Optional[GetServiceVersionRequest]:
        if data is None:
            return None
        return GetServiceVersionRequest()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class CreatePasswordRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    password: str = None

    def with_user_name(self, user_name: str) -> CreatePasswordRequest:
        self.user_name = user_name
        return self

    def with_password(self, password: str) -> CreatePasswordRequest:
        self.password = password
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
    ) -> Optional[CreatePasswordRequest]:
        if data is None:
            return None
        return CreatePasswordRequest()\
            .with_user_name(data.get('userName'))\
            .with_password(data.get('password'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "password": self.password,
        }


class GetPasswordRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None

    def with_user_name(self, user_name: str) -> GetPasswordRequest:
        self.user_name = user_name
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
    ) -> Optional[GetPasswordRequest]:
        if data is None:
            return None
        return GetPasswordRequest()\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
        }


class EnableMfaRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None

    def with_user_name(self, user_name: str) -> EnableMfaRequest:
        self.user_name = user_name
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
    ) -> Optional[EnableMfaRequest]:
        if data is None:
            return None
        return EnableMfaRequest()\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
        }


class ChallengeMfaRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    passcode: str = None

    def with_user_name(self, user_name: str) -> ChallengeMfaRequest:
        self.user_name = user_name
        return self

    def with_passcode(self, passcode: str) -> ChallengeMfaRequest:
        self.passcode = passcode
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
    ) -> Optional[ChallengeMfaRequest]:
        if data is None:
            return None
        return ChallengeMfaRequest()\
            .with_user_name(data.get('userName'))\
            .with_passcode(data.get('passcode'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "passcode": self.passcode,
        }


class DisableMfaRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None

    def with_user_name(self, user_name: str) -> DisableMfaRequest:
        self.user_name = user_name
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
    ) -> Optional[DisableMfaRequest]:
        if data is None:
            return None
        return DisableMfaRequest()\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
        }


class DeletePasswordRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None

    def with_user_name(self, user_name: str) -> DeletePasswordRequest:
        self.user_name = user_name
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
    ) -> Optional[DeletePasswordRequest]:
        if data is None:
            return None
        return DeletePasswordRequest()\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
        }


class GetHasSecurityPolicyRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None

    def with_user_name(self, user_name: str) -> GetHasSecurityPolicyRequest:
        self.user_name = user_name
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
    ) -> Optional[GetHasSecurityPolicyRequest]:
        if data is None:
            return None
        return GetHasSecurityPolicyRequest()\
            .with_user_name(data.get('userName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
        }


class AttachSecurityPolicyRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    security_policy_id: str = None

    def with_user_name(self, user_name: str) -> AttachSecurityPolicyRequest:
        self.user_name = user_name
        return self

    def with_security_policy_id(self, security_policy_id: str) -> AttachSecurityPolicyRequest:
        self.security_policy_id = security_policy_id
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
    ) -> Optional[AttachSecurityPolicyRequest]:
        if data is None:
            return None
        return AttachSecurityPolicyRequest()\
            .with_user_name(data.get('userName'))\
            .with_security_policy_id(data.get('securityPolicyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "securityPolicyId": self.security_policy_id,
        }


class DetachSecurityPolicyRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    security_policy_id: str = None

    def with_user_name(self, user_name: str) -> DetachSecurityPolicyRequest:
        self.user_name = user_name
        return self

    def with_security_policy_id(self, security_policy_id: str) -> DetachSecurityPolicyRequest:
        self.security_policy_id = security_policy_id
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
    ) -> Optional[DetachSecurityPolicyRequest]:
        if data is None:
            return None
        return DetachSecurityPolicyRequest()\
            .with_user_name(data.get('userName'))\
            .with_security_policy_id(data.get('securityPolicyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "securityPolicyId": self.security_policy_id,
        }


class LoginRequest(core.Gs2Request):

    context_stack: str = None
    client_id: str = None
    client_secret: str = None

    def with_client_id(self, client_id: str) -> LoginRequest:
        self.client_id = client_id
        return self

    def with_client_secret(self, client_secret: str) -> LoginRequest:
        self.client_secret = client_secret
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
    ) -> Optional[LoginRequest]:
        if data is None:
            return None
        return LoginRequest()\
            .with_client_id(data.get('client_id'))\
            .with_client_secret(data.get('client_secret'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
        }


class LoginByUserRequest(core.Gs2Request):

    context_stack: str = None
    user_name: str = None
    password: str = None
    otp: str = None

    def with_user_name(self, user_name: str) -> LoginByUserRequest:
        self.user_name = user_name
        return self

    def with_password(self, password: str) -> LoginByUserRequest:
        self.password = password
        return self

    def with_otp(self, otp: str) -> LoginByUserRequest:
        self.otp = otp
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
    ) -> Optional[LoginByUserRequest]:
        if data is None:
            return None
        return LoginByUserRequest()\
            .with_user_name(data.get('userName'))\
            .with_password(data.get('password'))\
            .with_otp(data.get('otp'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userName": self.user_name,
            "password": self.password,
            "otp": self.otp,
        }