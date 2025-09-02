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


class DescribeStagesResult(core.Gs2Result):
    items: List[Stage] = None

    def with_items(self, items: List[Stage]) -> DescribeStagesResult:
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
    ) -> Optional[DescribeStagesResult]:
        if data is None:
            return None
        return DescribeStagesResult()\
            .with_items(None if data.get('items') is None else [
                Stage.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetStageResult(core.Gs2Result):
    item: Stage = None
    source: List[Microservice] = None
    current: List[Microservice] = None

    def with_item(self, item: Stage) -> GetStageResult:
        self.item = item
        return self

    def with_source(self, source: List[Microservice]) -> GetStageResult:
        self.source = source
        return self

    def with_current(self, current: List[Microservice]) -> GetStageResult:
        self.current = current
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
    ) -> Optional[GetStageResult]:
        if data is None:
            return None
        return GetStageResult()\
            .with_item(Stage.from_dict(data.get('item')))\
            .with_source(None if data.get('source') is None else [
                Microservice.from_dict(data.get('source')[i])
                for i in range(len(data.get('source')))
            ])\
            .with_current(None if data.get('current') is None else [
                Microservice.from_dict(data.get('current')[i])
                for i in range(len(data.get('current')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "source": None if self.source is None else [
                self.source[i].to_dict() if self.source[i] else None
                for i in range(len(self.source))
            ],
            "current": None if self.current is None else [
                self.current[i].to_dict() if self.current[i] else None
                for i in range(len(self.current))
            ],
        }


class PromoteStageResult(core.Gs2Result):
    item: Stage = None

    def with_item(self, item: Stage) -> PromoteStageResult:
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
    ) -> Optional[PromoteStageResult]:
        if data is None:
            return None
        return PromoteStageResult()\
            .with_item(Stage.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class RollbackStageResult(core.Gs2Result):
    item: Stage = None

    def with_item(self, item: Stage) -> RollbackStageResult:
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
    ) -> Optional[RollbackStageResult]:
        if data is None:
            return None
        return RollbackStageResult()\
            .with_item(Stage.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeOutputsResult(core.Gs2Result):
    items: List[Output] = None
    next_page_token: str = None

    def with_items(self, items: List[Output]) -> DescribeOutputsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeOutputsResult:
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
    ) -> Optional[DescribeOutputsResult]:
        if data is None:
            return None
        return DescribeOutputsResult()\
            .with_items(None if data.get('items') is None else [
                Output.from_dict(data.get('items')[i])
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


class GetOutputResult(core.Gs2Result):
    item: Output = None

    def with_item(self, item: Output) -> GetOutputResult:
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
    ) -> Optional[GetOutputResult]:
        if data is None:
            return None
        return GetOutputResult()\
            .with_item(Output.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }