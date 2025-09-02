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


class AccessToken(core.Gs2Model):
    token: str = None
    user_id: str = None
    federation_from_user_id: str = None
    expire: int = None
    time_offset: int = None

    def with_token(self, token: str) -> AccessToken:
        self.token = token
        return self

    def with_user_id(self, user_id: str) -> AccessToken:
        self.user_id = user_id
        return self

    def with_federation_from_user_id(self, federation_from_user_id: str) -> AccessToken:
        self.federation_from_user_id = federation_from_user_id
        return self

    def with_expire(self, expire: int) -> AccessToken:
        self.expire = expire
        return self

    def with_time_offset(self, time_offset: int) -> AccessToken:
        self.time_offset = time_offset
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
    ) -> Optional[AccessToken]:
        if data is None:
            return None
        return AccessToken()\
            .with_token(data.get('token'))\
            .with_user_id(data.get('userId'))\
            .with_federation_from_user_id(data.get('federationFromUserId'))\
            .with_expire(data.get('expire'))\
            .with_time_offset(data.get('timeOffset'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "userId": self.user_id,
            "federationFromUserId": self.federation_from_user_id,
            "expire": self.expire,
            "timeOffset": self.time_offset,
        }