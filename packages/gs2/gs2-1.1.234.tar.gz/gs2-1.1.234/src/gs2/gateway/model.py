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


class FirebaseToken(core.Gs2Model):
    firebase_token_id: str = None
    user_id: str = None
    token: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_firebase_token_id(self, firebase_token_id: str) -> FirebaseToken:
        self.firebase_token_id = firebase_token_id
        return self

    def with_user_id(self, user_id: str) -> FirebaseToken:
        self.user_id = user_id
        return self

    def with_token(self, token: str) -> FirebaseToken:
        self.token = token
        return self

    def with_created_at(self, created_at: int) -> FirebaseToken:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> FirebaseToken:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> FirebaseToken:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:gateway:{namespaceName}:user:{userId}:firebase:token'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):firebase:token', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):firebase:token', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):firebase:token', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):firebase:token', grn)
        if match is None:
            return None
        return match.group('user_id')

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
    ) -> Optional[FirebaseToken]:
        if data is None:
            return None
        return FirebaseToken()\
            .with_firebase_token_id(data.get('firebaseTokenId'))\
            .with_user_id(data.get('userId'))\
            .with_token(data.get('token'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "firebaseTokenId": self.firebase_token_id,
            "userId": self.user_id,
            "token": self.token,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class WebSocketSession(core.Gs2Model):
    web_socket_session_id: str = None
    connection_id: str = None
    namespace_name: str = None
    user_id: str = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_web_socket_session_id(self, web_socket_session_id: str) -> WebSocketSession:
        self.web_socket_session_id = web_socket_session_id
        return self

    def with_connection_id(self, connection_id: str) -> WebSocketSession:
        self.connection_id = connection_id
        return self

    def with_namespace_name(self, namespace_name: str) -> WebSocketSession:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> WebSocketSession:
        self.user_id = user_id
        return self

    def with_created_at(self, created_at: int) -> WebSocketSession:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> WebSocketSession:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> WebSocketSession:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        connection_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:gateway:{namespaceName}:user:{userId}:session:{connectionId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            connectionId=connection_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_connection_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+):user:(?P<userId>.+):session:(?P<connectionId>.+)', grn)
        if match is None:
            return None
        return match.group('connection_id')

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
    ) -> Optional[WebSocketSession]:
        if data is None:
            return None
        return WebSocketSession()\
            .with_web_socket_session_id(data.get('webSocketSessionId'))\
            .with_connection_id(data.get('connectionId'))\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "webSocketSessionId": self.web_socket_session_id,
            "connectionId": self.connection_id,
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    firebase_secret: str = None
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

    def with_firebase_secret(self, firebase_secret: str) -> Namespace:
        self.firebase_secret = firebase_secret
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
        return 'grn:gs2:{region}:{ownerId}:gateway:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):gateway:(?P<namespaceName>.+)', grn)
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
            .with_firebase_secret(data.get('firebaseSecret'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "firebaseSecret": self.firebase_secret,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }