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


class DescribeStagesRequest(core.Gs2Request):

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
    ) -> Optional[DescribeStagesRequest]:
        if data is None:
            return None
        return DescribeStagesRequest()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class GetStageRequest(core.Gs2Request):

    context_stack: str = None
    stage_name: str = None

    def with_stage_name(self, stage_name: str) -> GetStageRequest:
        self.stage_name = stage_name
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
    ) -> Optional[GetStageRequest]:
        if data is None:
            return None
        return GetStageRequest()\
            .with_stage_name(data.get('stageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stageName": self.stage_name,
        }


class PromoteStageRequest(core.Gs2Request):

    context_stack: str = None
    stage_name: str = None

    def with_stage_name(self, stage_name: str) -> PromoteStageRequest:
        self.stage_name = stage_name
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
    ) -> Optional[PromoteStageRequest]:
        if data is None:
            return None
        return PromoteStageRequest()\
            .with_stage_name(data.get('stageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stageName": self.stage_name,
        }


class RollbackStageRequest(core.Gs2Request):

    context_stack: str = None
    stage_name: str = None

    def with_stage_name(self, stage_name: str) -> RollbackStageRequest:
        self.stage_name = stage_name
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
    ) -> Optional[RollbackStageRequest]:
        if data is None:
            return None
        return RollbackStageRequest()\
            .with_stage_name(data.get('stageName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stageName": self.stage_name,
        }


class DescribeOutputsRequest(core.Gs2Request):

    context_stack: str = None
    stage_name: str = None
    page_token: str = None
    limit: int = None

    def with_stage_name(self, stage_name: str) -> DescribeOutputsRequest:
        self.stage_name = stage_name
        return self

    def with_page_token(self, page_token: str) -> DescribeOutputsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeOutputsRequest:
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
    ) -> Optional[DescribeOutputsRequest]:
        if data is None:
            return None
        return DescribeOutputsRequest()\
            .with_stage_name(data.get('stageName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stageName": self.stage_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetOutputRequest(core.Gs2Request):

    context_stack: str = None
    stage_name: str = None
    output_name: str = None

    def with_stage_name(self, stage_name: str) -> GetOutputRequest:
        self.stage_name = stage_name
        return self

    def with_output_name(self, output_name: str) -> GetOutputRequest:
        self.output_name = output_name
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
    ) -> Optional[GetOutputRequest]:
        if data is None:
            return None
        return GetOutputRequest()\
            .with_stage_name(data.get('stageName'))\
            .with_output_name(data.get('outputName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stageName": self.stage_name,
            "outputName": self.output_name,
        }