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


class LoginRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset: int = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> LoginRequest:
        self.user_id = user_id
        return self

    def with_time_offset(self, time_offset: int) -> LoginRequest:
        self.time_offset = time_offset
        return self

    def with_time_offset_token(self, time_offset_token: str) -> LoginRequest:
        self.time_offset_token = time_offset_token
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
            .with_user_id(data.get('userId'))\
            .with_time_offset(data.get('timeOffset'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffset": self.time_offset,
            "timeOffsetToken": self.time_offset_token,
        }


class LoginBySignatureRequest(core.Gs2Request):

    context_stack: str = None
    key_id: str = None
    body: str = None
    signature: str = None

    def with_key_id(self, key_id: str) -> LoginBySignatureRequest:
        self.key_id = key_id
        return self

    def with_body(self, body: str) -> LoginBySignatureRequest:
        self.body = body
        return self

    def with_signature(self, signature: str) -> LoginBySignatureRequest:
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
    ) -> Optional[LoginBySignatureRequest]:
        if data is None:
            return None
        return LoginBySignatureRequest()\
            .with_key_id(data.get('keyId'))\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "keyId": self.key_id,
            "body": self.body,
            "signature": self.signature,
        }


class FederationRequest(core.Gs2Request):

    context_stack: str = None
    original_user_id: str = None
    user_id: str = None
    policy_document: str = None
    time_offset: int = None
    time_offset_token: str = None

    def with_original_user_id(self, original_user_id: str) -> FederationRequest:
        self.original_user_id = original_user_id
        return self

    def with_user_id(self, user_id: str) -> FederationRequest:
        self.user_id = user_id
        return self

    def with_policy_document(self, policy_document: str) -> FederationRequest:
        self.policy_document = policy_document
        return self

    def with_time_offset(self, time_offset: int) -> FederationRequest:
        self.time_offset = time_offset
        return self

    def with_time_offset_token(self, time_offset_token: str) -> FederationRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[FederationRequest]:
        if data is None:
            return None
        return FederationRequest()\
            .with_original_user_id(data.get('originalUserId'))\
            .with_user_id(data.get('userId'))\
            .with_policy_document(data.get('policyDocument'))\
            .with_time_offset(data.get('timeOffset'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "originalUserId": self.original_user_id,
            "userId": self.user_id,
            "policyDocument": self.policy_document,
            "timeOffset": self.time_offset,
            "timeOffsetToken": self.time_offset_token,
        }


class IssueTimeOffsetTokenByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset: int = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> IssueTimeOffsetTokenByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset(self, time_offset: int) -> IssueTimeOffsetTokenByUserIdRequest:
        self.time_offset = time_offset
        return self

    def with_time_offset_token(self, time_offset_token: str) -> IssueTimeOffsetTokenByUserIdRequest:
        self.time_offset_token = time_offset_token
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
    ) -> Optional[IssueTimeOffsetTokenByUserIdRequest]:
        if data is None:
            return None
        return IssueTimeOffsetTokenByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset(data.get('timeOffset'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffset": self.time_offset,
            "timeOffsetToken": self.time_offset_token,
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