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
#
# deny overwrite

from __future__ import annotations

from ..core.model import *
from .model import *


class DescribeUsersResult(core.Gs2Result):
    items: List[User] = None
    next_page_token: str = None

    def with_items(self, items: List[User]) -> DescribeUsersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeUsersResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeUsersResult]:
        if data is None:
            return None
        return DescribeUsersResult()\
            .with_items(None if data.get('items') is None else [
                User.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateUserResult(core.Gs2Result):
    item: User = None

    def with_item(self, item: User) -> CreateUserResult:
        self.item = item
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
    ) -> Optional[CreateUserResult]:
        if data is None:
            return None
        return CreateUserResult()\
            .with_item(User.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateUserResult(core.Gs2Result):
    item: User = None

    def with_item(self, item: User) -> UpdateUserResult:
        self.item = item
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
    ) -> Optional[UpdateUserResult]:
        if data is None:
            return None
        return UpdateUserResult()\
            .with_item(User.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetUserResult(core.Gs2Result):
    item: User = None

    def with_item(self, item: User) -> GetUserResult:
        self.item = item
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
    ) -> Optional[GetUserResult]:
        if data is None:
            return None
        return GetUserResult()\
            .with_item(User.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteUserResult(core.Gs2Result):
    item: User = None

    def with_item(self, item: User) -> DeleteUserResult:
        self.item = item
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
    ) -> Optional[DeleteUserResult]:
        if data is None:
            return None
        return DeleteUserResult()\
            .with_item(User.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSecurityPoliciesResult(core.Gs2Result):
    items: List[SecurityPolicy] = None
    next_page_token: str = None

    def with_items(self, items: List[SecurityPolicy]) -> DescribeSecurityPoliciesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSecurityPoliciesResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeSecurityPoliciesResult]:
        if data is None:
            return None
        return DescribeSecurityPoliciesResult()\
            .with_items(None if data.get('items') is None else [
                SecurityPolicy.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
        }


class DescribeCommonSecurityPoliciesResult(core.Gs2Result):
    items: List[SecurityPolicy] = None
    next_page_token: str = None

    def with_items(self, items: List[SecurityPolicy]) -> DescribeCommonSecurityPoliciesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeCommonSecurityPoliciesResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeCommonSecurityPoliciesResult]:
        if data is None:
            return None
        return DescribeCommonSecurityPoliciesResult()\
            .with_items(None if data.get('items') is None else [
                SecurityPolicy.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateSecurityPolicyResult(core.Gs2Result):
    item: SecurityPolicy = None

    def with_item(self, item: SecurityPolicy) -> CreateSecurityPolicyResult:
        self.item = item
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
    ) -> Optional[CreateSecurityPolicyResult]:
        if data is None:
            return None
        return CreateSecurityPolicyResult()\
            .with_item(SecurityPolicy.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateSecurityPolicyResult(core.Gs2Result):
    item: SecurityPolicy = None

    def with_item(self, item: SecurityPolicy) -> UpdateSecurityPolicyResult:
        self.item = item
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
    ) -> Optional[UpdateSecurityPolicyResult]:
        if data is None:
            return None
        return UpdateSecurityPolicyResult()\
            .with_item(SecurityPolicy.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSecurityPolicyResult(core.Gs2Result):
    item: SecurityPolicy = None

    def with_item(self, item: SecurityPolicy) -> GetSecurityPolicyResult:
        self.item = item
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
    ) -> Optional[GetSecurityPolicyResult]:
        if data is None:
            return None
        return GetSecurityPolicyResult()\
            .with_item(SecurityPolicy.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteSecurityPolicyResult(core.Gs2Result):
    item: SecurityPolicy = None

    def with_item(self, item: SecurityPolicy) -> DeleteSecurityPolicyResult:
        self.item = item
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
    ) -> Optional[DeleteSecurityPolicyResult]:
        if data is None:
            return None
        return DeleteSecurityPolicyResult()\
            .with_item(SecurityPolicy.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeIdentifiersResult(core.Gs2Result):
    items: List[Identifier] = None
    next_page_token: str = None

    def with_items(self, items: List[Identifier]) -> DescribeIdentifiersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeIdentifiersResult:
        self.next_page_token = next_page_token
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
    ) -> Optional[DescribeIdentifiersResult]:
        if data is None:
            return None
        return DescribeIdentifiersResult()\
            .with_items(None if data.get('items') is None else [
                Identifier.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])\
            .with_next_page_token(data.get('nextPageToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
            "nextPageToken": self.next_page_token,
        }


class CreateIdentifierResult(core.Gs2Result):
    item: Identifier = None
    client_secret: str = None

    def with_item(self, item: Identifier) -> CreateIdentifierResult:
        self.item = item
        return self

    def with_client_secret(self, client_secret: str) -> CreateIdentifierResult:
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
    ) -> Optional[CreateIdentifierResult]:
        if data is None:
            return None
        return CreateIdentifierResult()\
            .with_item(Identifier.from_dict(data.get('item')))\
            .with_client_secret(data.get('clientSecret'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "clientSecret": self.client_secret,
        }


class GetIdentifierResult(core.Gs2Result):
    item: Identifier = None

    def with_item(self, item: Identifier) -> GetIdentifierResult:
        self.item = item
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
    ) -> Optional[GetIdentifierResult]:
        if data is None:
            return None
        return GetIdentifierResult()\
            .with_item(Identifier.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteIdentifierResult(core.Gs2Result):
    item: Identifier = None

    def with_item(self, item: Identifier) -> DeleteIdentifierResult:
        self.item = item
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
    ) -> Optional[DeleteIdentifierResult]:
        if data is None:
            return None
        return DeleteIdentifierResult()\
            .with_item(Identifier.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeAttachedGuardsResult(core.Gs2Result):
    items: List[str] = None

    def with_items(self, items: List[str]) -> DescribeAttachedGuardsResult:
        self.items = items
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
    ) -> Optional[DescribeAttachedGuardsResult]:
        if data is None:
            return None
        return DescribeAttachedGuardsResult()\
            .with_items(None if data.get('items') is None else [
                data.get('items')[i]
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i]
                for i in range(len(self.items))
            ],
        }


class AttachGuardResult(core.Gs2Result):
    items: List[str] = None

    def with_items(self, items: List[str]) -> AttachGuardResult:
        self.items = items
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
    ) -> Optional[AttachGuardResult]:
        if data is None:
            return None
        return AttachGuardResult()\
            .with_items(None if data.get('items') is None else [
                data.get('items')[i]
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i]
                for i in range(len(self.items))
            ],
        }


class DetachGuardResult(core.Gs2Result):
    items: List[str] = None

    def with_items(self, items: List[str]) -> DetachGuardResult:
        self.items = items
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
    ) -> Optional[DetachGuardResult]:
        if data is None:
            return None
        return DetachGuardResult()\
            .with_items(None if data.get('items') is None else [
                data.get('items')[i]
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i]
                for i in range(len(self.items))
            ],
        }


class GetServiceVersionResult(core.Gs2Result):
    status: str = None

    def with_status(self, status: str) -> GetServiceVersionResult:
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
    ) -> Optional[GetServiceVersionResult]:
        if data is None:
            return None
        return GetServiceVersionResult()\
            .with_status(data.get('status'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
        }


class CreatePasswordResult(core.Gs2Result):
    item: Password = None

    def with_item(self, item: Password) -> CreatePasswordResult:
        self.item = item
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
    ) -> Optional[CreatePasswordResult]:
        if data is None:
            return None
        return CreatePasswordResult()\
            .with_item(Password.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetPasswordResult(core.Gs2Result):
    item: Password = None

    def with_item(self, item: Password) -> GetPasswordResult:
        self.item = item
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
    ) -> Optional[GetPasswordResult]:
        if data is None:
            return None
        return GetPasswordResult()\
            .with_item(Password.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class EnableMfaResult(core.Gs2Result):
    item: Password = None
    challenge_token: str = None

    def with_item(self, item: Password) -> EnableMfaResult:
        self.item = item
        return self

    def with_challenge_token(self, challenge_token: str) -> EnableMfaResult:
        self.challenge_token = challenge_token
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
    ) -> Optional[EnableMfaResult]:
        if data is None:
            return None
        return EnableMfaResult()\
            .with_item(Password.from_dict(data.get('item')))\
            .with_challenge_token(data.get('challengeToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "challengeToken": self.challenge_token,
        }


class ChallengeMfaResult(core.Gs2Result):
    item: Password = None

    def with_item(self, item: Password) -> ChallengeMfaResult:
        self.item = item
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
    ) -> Optional[ChallengeMfaResult]:
        if data is None:
            return None
        return ChallengeMfaResult()\
            .with_item(Password.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DisableMfaResult(core.Gs2Result):
    item: Password = None

    def with_item(self, item: Password) -> DisableMfaResult:
        self.item = item
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
    ) -> Optional[DisableMfaResult]:
        if data is None:
            return None
        return DisableMfaResult()\
            .with_item(Password.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeletePasswordResult(core.Gs2Result):
    item: Password = None

    def with_item(self, item: Password) -> DeletePasswordResult:
        self.item = item
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
    ) -> Optional[DeletePasswordResult]:
        if data is None:
            return None
        return DeletePasswordResult()\
            .with_item(Password.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetHasSecurityPolicyResult(core.Gs2Result):
    items: List[SecurityPolicy] = None

    def with_items(self, items: List[SecurityPolicy]) -> GetHasSecurityPolicyResult:
        self.items = items
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
    ) -> Optional[GetHasSecurityPolicyResult]:
        if data is None:
            return None
        return GetHasSecurityPolicyResult()\
            .with_items(None if data.get('items') is None else [
                SecurityPolicy.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class AttachSecurityPolicyResult(core.Gs2Result):
    items: List[SecurityPolicy] = None

    def with_items(self, items: List[SecurityPolicy]) -> AttachSecurityPolicyResult:
        self.items = items
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
    ) -> Optional[AttachSecurityPolicyResult]:
        if data is None:
            return None
        return AttachSecurityPolicyResult()\
            .with_items(None if data.get('items') is None else [
                SecurityPolicy.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class DetachSecurityPolicyResult(core.Gs2Result):
    items: List[SecurityPolicy] = None

    def with_items(self, items: List[SecurityPolicy]) -> DetachSecurityPolicyResult:
        self.items = items
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
    ) -> Optional[DetachSecurityPolicyResult]:
        if data is None:
            return None
        return DetachSecurityPolicyResult()\
            .with_items(None if data.get('items') is None else [
                SecurityPolicy.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class LoginResult(core.Gs2Result):
    access_token: str = None
    token_type: str = None
    expires_in: int = None
    owner_id: str = None

    def with_access_token(self, access_token: str) -> LoginResult:
        self.access_token = access_token
        return self

    def with_token_type(self, token_type: str) -> LoginResult:
        self.token_type = token_type
        return self

    def with_expires_in(self, expires_in: int) -> LoginResult:
        self.expires_in = expires_in
        return self

    def with_owner_id(self, owner_id: str) -> LoginResult:
        self.owner_id = owner_id
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
    ) -> Optional[LoginResult]:
        if data is None:
            return None
        return LoginResult()\
            .with_access_token(data.get('access_token'))\
            .with_token_type(data.get('token_type'))\
            .with_expires_in(data.get('expires_in'))\
            .with_owner_id(data.get('owner_id'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "owner_id": self.owner_id,
        }


class LoginByUserResult(core.Gs2Result):
    item: ProjectToken = None

    def with_item(self, item: ProjectToken) -> LoginByUserResult:
        self.item = item
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
    ) -> Optional[LoginByUserResult]:
        if data is None:
            return None
        return LoginByUserResult()\
            .with_item(ProjectToken.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }