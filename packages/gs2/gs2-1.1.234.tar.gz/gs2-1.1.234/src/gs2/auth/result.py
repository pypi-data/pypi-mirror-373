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

from ..core.model import *
from .model import *


class LoginResult(core.Gs2Result):
    token: str = None
    user_id: str = None
    expire: int = None

    def with_token(self, token: str) -> LoginResult:
        self.token = token
        return self

    def with_user_id(self, user_id: str) -> LoginResult:
        self.user_id = user_id
        return self

    def with_expire(self, expire: int) -> LoginResult:
        self.expire = expire
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
            .with_token(data.get('token'))\
            .with_user_id(data.get('userId'))\
            .with_expire(data.get('expire'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "userId": self.user_id,
            "expire": self.expire,
        }


class LoginBySignatureResult(core.Gs2Result):
    token: str = None
    user_id: str = None
    expire: int = None

    def with_token(self, token: str) -> LoginBySignatureResult:
        self.token = token
        return self

    def with_user_id(self, user_id: str) -> LoginBySignatureResult:
        self.user_id = user_id
        return self

    def with_expire(self, expire: int) -> LoginBySignatureResult:
        self.expire = expire
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
    ) -> Optional[LoginBySignatureResult]:
        if data is None:
            return None
        return LoginBySignatureResult()\
            .with_token(data.get('token'))\
            .with_user_id(data.get('userId'))\
            .with_expire(data.get('expire'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "userId": self.user_id,
            "expire": self.expire,
        }


class FederationResult(core.Gs2Result):
    token: str = None
    user_id: str = None
    expire: int = None

    def with_token(self, token: str) -> FederationResult:
        self.token = token
        return self

    def with_user_id(self, user_id: str) -> FederationResult:
        self.user_id = user_id
        return self

    def with_expire(self, expire: int) -> FederationResult:
        self.expire = expire
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
    ) -> Optional[FederationResult]:
        if data is None:
            return None
        return FederationResult()\
            .with_token(data.get('token'))\
            .with_user_id(data.get('userId'))\
            .with_expire(data.get('expire'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "userId": self.user_id,
            "expire": self.expire,
        }


class IssueTimeOffsetTokenByUserIdResult(core.Gs2Result):
    token: str = None
    user_id: str = None
    expire: int = None

    def with_token(self, token: str) -> IssueTimeOffsetTokenByUserIdResult:
        self.token = token
        return self

    def with_user_id(self, user_id: str) -> IssueTimeOffsetTokenByUserIdResult:
        self.user_id = user_id
        return self

    def with_expire(self, expire: int) -> IssueTimeOffsetTokenByUserIdResult:
        self.expire = expire
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
    ) -> Optional[IssueTimeOffsetTokenByUserIdResult]:
        if data is None:
            return None
        return IssueTimeOffsetTokenByUserIdResult()\
            .with_token(data.get('token'))\
            .with_user_id(data.get('userId'))\
            .with_expire(data.get('expire'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "userId": self.user_id,
            "expire": self.expire,
        }


class GetServiceVersionResult(core.Gs2Result):
    item: str = None

    def with_item(self, item: str) -> GetServiceVersionResult:
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
    ) -> Optional[GetServiceVersionResult]:
        if data is None:
            return None
        return GetServiceVersionResult()\
            .with_item(data.get('item'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
        }