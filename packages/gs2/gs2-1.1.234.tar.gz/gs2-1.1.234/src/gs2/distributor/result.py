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


class DescribeNamespacesResult(core.Gs2Result):
    items: List[Namespace] = None
    next_page_token: str = None

    def with_items(self, items: List[Namespace]) -> DescribeNamespacesResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeNamespacesResult:
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
    ) -> Optional[DescribeNamespacesResult]:
        if data is None:
            return None
        return DescribeNamespacesResult()\
            .with_items(None if data.get('items') is None else [
                Namespace.from_dict(data.get('items')[i])
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


class CreateNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> CreateNamespaceResult:
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
    ) -> Optional[CreateNamespaceResult]:
        if data is None:
            return None
        return CreateNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetNamespaceStatusResult(core.Gs2Result):
    status: str = None

    def with_status(self, status: str) -> GetNamespaceStatusResult:
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
    ) -> Optional[GetNamespaceStatusResult]:
        if data is None:
            return None
        return GetNamespaceStatusResult()\
            .with_status(data.get('status'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
        }


class GetNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> GetNamespaceResult:
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
    ) -> Optional[GetNamespaceResult]:
        if data is None:
            return None
        return GetNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> UpdateNamespaceResult:
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
    ) -> Optional[UpdateNamespaceResult]:
        if data is None:
            return None
        return UpdateNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteNamespaceResult(core.Gs2Result):
    item: Namespace = None

    def with_item(self, item: Namespace) -> DeleteNamespaceResult:
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
    ) -> Optional[DeleteNamespaceResult]:
        if data is None:
            return None
        return DeleteNamespaceResult()\
            .with_item(Namespace.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
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


class DescribeDistributorModelMastersResult(core.Gs2Result):
    items: List[DistributorModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[DistributorModelMaster]) -> DescribeDistributorModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeDistributorModelMastersResult:
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
    ) -> Optional[DescribeDistributorModelMastersResult]:
        if data is None:
            return None
        return DescribeDistributorModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                DistributorModelMaster.from_dict(data.get('items')[i])
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


class CreateDistributorModelMasterResult(core.Gs2Result):
    item: DistributorModelMaster = None

    def with_item(self, item: DistributorModelMaster) -> CreateDistributorModelMasterResult:
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
    ) -> Optional[CreateDistributorModelMasterResult]:
        if data is None:
            return None
        return CreateDistributorModelMasterResult()\
            .with_item(DistributorModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetDistributorModelMasterResult(core.Gs2Result):
    item: DistributorModelMaster = None

    def with_item(self, item: DistributorModelMaster) -> GetDistributorModelMasterResult:
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
    ) -> Optional[GetDistributorModelMasterResult]:
        if data is None:
            return None
        return GetDistributorModelMasterResult()\
            .with_item(DistributorModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateDistributorModelMasterResult(core.Gs2Result):
    item: DistributorModelMaster = None

    def with_item(self, item: DistributorModelMaster) -> UpdateDistributorModelMasterResult:
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
    ) -> Optional[UpdateDistributorModelMasterResult]:
        if data is None:
            return None
        return UpdateDistributorModelMasterResult()\
            .with_item(DistributorModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteDistributorModelMasterResult(core.Gs2Result):
    item: DistributorModelMaster = None

    def with_item(self, item: DistributorModelMaster) -> DeleteDistributorModelMasterResult:
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
    ) -> Optional[DeleteDistributorModelMasterResult]:
        if data is None:
            return None
        return DeleteDistributorModelMasterResult()\
            .with_item(DistributorModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeDistributorModelsResult(core.Gs2Result):
    items: List[DistributorModel] = None

    def with_items(self, items: List[DistributorModel]) -> DescribeDistributorModelsResult:
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
    ) -> Optional[DescribeDistributorModelsResult]:
        if data is None:
            return None
        return DescribeDistributorModelsResult()\
            .with_items(None if data.get('items') is None else [
                DistributorModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetDistributorModelResult(core.Gs2Result):
    item: DistributorModel = None

    def with_item(self, item: DistributorModel) -> GetDistributorModelResult:
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
    ) -> Optional[GetDistributorModelResult]:
        if data is None:
            return None
        return GetDistributorModelResult()\
            .with_item(DistributorModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentDistributorMaster = None

    def with_item(self, item: CurrentDistributorMaster) -> ExportMasterResult:
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
    ) -> Optional[ExportMasterResult]:
        if data is None:
            return None
        return ExportMasterResult()\
            .with_item(CurrentDistributorMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentDistributorMasterResult(core.Gs2Result):
    item: CurrentDistributorMaster = None

    def with_item(self, item: CurrentDistributorMaster) -> GetCurrentDistributorMasterResult:
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
    ) -> Optional[GetCurrentDistributorMasterResult]:
        if data is None:
            return None
        return GetCurrentDistributorMasterResult()\
            .with_item(CurrentDistributorMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentDistributorMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentDistributorMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentDistributorMasterResult:
        self.upload_url = upload_url
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
    ) -> Optional[PreUpdateCurrentDistributorMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentDistributorMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentDistributorMasterResult(core.Gs2Result):
    item: CurrentDistributorMaster = None

    def with_item(self, item: CurrentDistributorMaster) -> UpdateCurrentDistributorMasterResult:
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
    ) -> Optional[UpdateCurrentDistributorMasterResult]:
        if data is None:
            return None
        return UpdateCurrentDistributorMasterResult()\
            .with_item(CurrentDistributorMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentDistributorMasterFromGitHubResult(core.Gs2Result):
    item: CurrentDistributorMaster = None

    def with_item(self, item: CurrentDistributorMaster) -> UpdateCurrentDistributorMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentDistributorMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentDistributorMasterFromGitHubResult()\
            .with_item(CurrentDistributorMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DistributeResult(core.Gs2Result):
    distribute_resource: DistributeResource = None
    inbox_namespace_id: str = None
    result: str = None

    def with_distribute_resource(self, distribute_resource: DistributeResource) -> DistributeResult:
        self.distribute_resource = distribute_resource
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> DistributeResult:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_result(self, result: str) -> DistributeResult:
        self.result = result
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
    ) -> Optional[DistributeResult]:
        if data is None:
            return None
        return DistributeResult()\
            .with_distribute_resource(DistributeResource.from_dict(data.get('distributeResource')))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distributeResource": self.distribute_resource.to_dict() if self.distribute_resource else None,
            "inboxNamespaceId": self.inbox_namespace_id,
            "result": self.result,
        }


class DistributeWithoutOverflowProcessResult(core.Gs2Result):
    distribute_resource: DistributeResource = None
    result: str = None

    def with_distribute_resource(self, distribute_resource: DistributeResource) -> DistributeWithoutOverflowProcessResult:
        self.distribute_resource = distribute_resource
        return self

    def with_result(self, result: str) -> DistributeWithoutOverflowProcessResult:
        self.result = result
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
    ) -> Optional[DistributeWithoutOverflowProcessResult]:
        if data is None:
            return None
        return DistributeWithoutOverflowProcessResult()\
            .with_distribute_resource(DistributeResource.from_dict(data.get('distributeResource')))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distributeResource": self.distribute_resource.to_dict() if self.distribute_resource else None,
            "result": self.result,
        }


class RunVerifyTaskResult(core.Gs2Result):
    context_stack: str = None
    status_code: int = None
    result: str = None

    def with_context_stack(self, context_stack: str) -> RunVerifyTaskResult:
        self.context_stack = context_stack
        return self

    def with_status_code(self, status_code: int) -> RunVerifyTaskResult:
        self.status_code = status_code
        return self

    def with_result(self, result: str) -> RunVerifyTaskResult:
        self.result = result
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
    ) -> Optional[RunVerifyTaskResult]:
        if data is None:
            return None
        return RunVerifyTaskResult()\
            .with_context_stack(data.get('contextStack'))\
            .with_status_code(data.get('statusCode'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contextStack": self.context_stack,
            "statusCode": self.status_code,
            "result": self.result,
        }


class RunStampTaskResult(core.Gs2Result):
    context_stack: str = None
    status_code: int = None
    result: str = None

    def with_context_stack(self, context_stack: str) -> RunStampTaskResult:
        self.context_stack = context_stack
        return self

    def with_status_code(self, status_code: int) -> RunStampTaskResult:
        self.status_code = status_code
        return self

    def with_result(self, result: str) -> RunStampTaskResult:
        self.result = result
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
    ) -> Optional[RunStampTaskResult]:
        if data is None:
            return None
        return RunStampTaskResult()\
            .with_context_stack(data.get('contextStack'))\
            .with_status_code(data.get('statusCode'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contextStack": self.context_stack,
            "statusCode": self.status_code,
            "result": self.result,
        }


class RunStampSheetResult(core.Gs2Result):
    status_code: int = None
    result: str = None

    def with_status_code(self, status_code: int) -> RunStampSheetResult:
        self.status_code = status_code
        return self

    def with_result(self, result: str) -> RunStampSheetResult:
        self.result = result
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
    ) -> Optional[RunStampSheetResult]:
        if data is None:
            return None
        return RunStampSheetResult()\
            .with_status_code(data.get('statusCode'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statusCode": self.status_code,
            "result": self.result,
        }


class RunStampSheetExpressResult(core.Gs2Result):
    verify_task_result_codes: List[int] = None
    verify_task_results: List[str] = None
    task_result_codes: List[int] = None
    task_results: List[str] = None
    sheet_result_code: int = None
    sheet_result: str = None

    def with_verify_task_result_codes(self, verify_task_result_codes: List[int]) -> RunStampSheetExpressResult:
        self.verify_task_result_codes = verify_task_result_codes
        return self

    def with_verify_task_results(self, verify_task_results: List[str]) -> RunStampSheetExpressResult:
        self.verify_task_results = verify_task_results
        return self

    def with_task_result_codes(self, task_result_codes: List[int]) -> RunStampSheetExpressResult:
        self.task_result_codes = task_result_codes
        return self

    def with_task_results(self, task_results: List[str]) -> RunStampSheetExpressResult:
        self.task_results = task_results
        return self

    def with_sheet_result_code(self, sheet_result_code: int) -> RunStampSheetExpressResult:
        self.sheet_result_code = sheet_result_code
        return self

    def with_sheet_result(self, sheet_result: str) -> RunStampSheetExpressResult:
        self.sheet_result = sheet_result
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
    ) -> Optional[RunStampSheetExpressResult]:
        if data is None:
            return None
        return RunStampSheetExpressResult()\
            .with_verify_task_result_codes(None if data.get('verifyTaskResultCodes') is None else [
                data.get('verifyTaskResultCodes')[i]
                for i in range(len(data.get('verifyTaskResultCodes')))
            ])\
            .with_verify_task_results(None if data.get('verifyTaskResults') is None else [
                data.get('verifyTaskResults')[i]
                for i in range(len(data.get('verifyTaskResults')))
            ])\
            .with_task_result_codes(None if data.get('taskResultCodes') is None else [
                data.get('taskResultCodes')[i]
                for i in range(len(data.get('taskResultCodes')))
            ])\
            .with_task_results(None if data.get('taskResults') is None else [
                data.get('taskResults')[i]
                for i in range(len(data.get('taskResults')))
            ])\
            .with_sheet_result_code(data.get('sheetResultCode'))\
            .with_sheet_result(data.get('sheetResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verifyTaskResultCodes": None if self.verify_task_result_codes is None else [
                self.verify_task_result_codes[i]
                for i in range(len(self.verify_task_result_codes))
            ],
            "verifyTaskResults": None if self.verify_task_results is None else [
                self.verify_task_results[i]
                for i in range(len(self.verify_task_results))
            ],
            "taskResultCodes": None if self.task_result_codes is None else [
                self.task_result_codes[i]
                for i in range(len(self.task_result_codes))
            ],
            "taskResults": None if self.task_results is None else [
                self.task_results[i]
                for i in range(len(self.task_results))
            ],
            "sheetResultCode": self.sheet_result_code,
            "sheetResult": self.sheet_result,
        }


class RunVerifyTaskWithoutNamespaceResult(core.Gs2Result):
    context_stack: str = None
    status_code: int = None
    result: str = None

    def with_context_stack(self, context_stack: str) -> RunVerifyTaskWithoutNamespaceResult:
        self.context_stack = context_stack
        return self

    def with_status_code(self, status_code: int) -> RunVerifyTaskWithoutNamespaceResult:
        self.status_code = status_code
        return self

    def with_result(self, result: str) -> RunVerifyTaskWithoutNamespaceResult:
        self.result = result
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
    ) -> Optional[RunVerifyTaskWithoutNamespaceResult]:
        if data is None:
            return None
        return RunVerifyTaskWithoutNamespaceResult()\
            .with_context_stack(data.get('contextStack'))\
            .with_status_code(data.get('statusCode'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contextStack": self.context_stack,
            "statusCode": self.status_code,
            "result": self.result,
        }


class RunStampTaskWithoutNamespaceResult(core.Gs2Result):
    context_stack: str = None
    status_code: int = None
    result: str = None

    def with_context_stack(self, context_stack: str) -> RunStampTaskWithoutNamespaceResult:
        self.context_stack = context_stack
        return self

    def with_status_code(self, status_code: int) -> RunStampTaskWithoutNamespaceResult:
        self.status_code = status_code
        return self

    def with_result(self, result: str) -> RunStampTaskWithoutNamespaceResult:
        self.result = result
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
    ) -> Optional[RunStampTaskWithoutNamespaceResult]:
        if data is None:
            return None
        return RunStampTaskWithoutNamespaceResult()\
            .with_context_stack(data.get('contextStack'))\
            .with_status_code(data.get('statusCode'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contextStack": self.context_stack,
            "statusCode": self.status_code,
            "result": self.result,
        }


class RunStampSheetWithoutNamespaceResult(core.Gs2Result):
    status_code: int = None
    result: str = None

    def with_status_code(self, status_code: int) -> RunStampSheetWithoutNamespaceResult:
        self.status_code = status_code
        return self

    def with_result(self, result: str) -> RunStampSheetWithoutNamespaceResult:
        self.result = result
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
    ) -> Optional[RunStampSheetWithoutNamespaceResult]:
        if data is None:
            return None
        return RunStampSheetWithoutNamespaceResult()\
            .with_status_code(data.get('statusCode'))\
            .with_result(data.get('result'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "statusCode": self.status_code,
            "result": self.result,
        }


class RunStampSheetExpressWithoutNamespaceResult(core.Gs2Result):
    verify_task_result_codes: List[int] = None
    verify_task_results: List[str] = None
    task_result_codes: List[int] = None
    task_results: List[str] = None
    sheet_result_code: int = None
    sheet_result: str = None

    def with_verify_task_result_codes(self, verify_task_result_codes: List[int]) -> RunStampSheetExpressWithoutNamespaceResult:
        self.verify_task_result_codes = verify_task_result_codes
        return self

    def with_verify_task_results(self, verify_task_results: List[str]) -> RunStampSheetExpressWithoutNamespaceResult:
        self.verify_task_results = verify_task_results
        return self

    def with_task_result_codes(self, task_result_codes: List[int]) -> RunStampSheetExpressWithoutNamespaceResult:
        self.task_result_codes = task_result_codes
        return self

    def with_task_results(self, task_results: List[str]) -> RunStampSheetExpressWithoutNamespaceResult:
        self.task_results = task_results
        return self

    def with_sheet_result_code(self, sheet_result_code: int) -> RunStampSheetExpressWithoutNamespaceResult:
        self.sheet_result_code = sheet_result_code
        return self

    def with_sheet_result(self, sheet_result: str) -> RunStampSheetExpressWithoutNamespaceResult:
        self.sheet_result = sheet_result
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
    ) -> Optional[RunStampSheetExpressWithoutNamespaceResult]:
        if data is None:
            return None
        return RunStampSheetExpressWithoutNamespaceResult()\
            .with_verify_task_result_codes(None if data.get('verifyTaskResultCodes') is None else [
                data.get('verifyTaskResultCodes')[i]
                for i in range(len(data.get('verifyTaskResultCodes')))
            ])\
            .with_verify_task_results(None if data.get('verifyTaskResults') is None else [
                data.get('verifyTaskResults')[i]
                for i in range(len(data.get('verifyTaskResults')))
            ])\
            .with_task_result_codes(None if data.get('taskResultCodes') is None else [
                data.get('taskResultCodes')[i]
                for i in range(len(data.get('taskResultCodes')))
            ])\
            .with_task_results(None if data.get('taskResults') is None else [
                data.get('taskResults')[i]
                for i in range(len(data.get('taskResults')))
            ])\
            .with_sheet_result_code(data.get('sheetResultCode'))\
            .with_sheet_result(data.get('sheetResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verifyTaskResultCodes": None if self.verify_task_result_codes is None else [
                self.verify_task_result_codes[i]
                for i in range(len(self.verify_task_result_codes))
            ],
            "verifyTaskResults": None if self.verify_task_results is None else [
                self.verify_task_results[i]
                for i in range(len(self.verify_task_results))
            ],
            "taskResultCodes": None if self.task_result_codes is None else [
                self.task_result_codes[i]
                for i in range(len(self.task_result_codes))
            ],
            "taskResults": None if self.task_results is None else [
                self.task_results[i]
                for i in range(len(self.task_results))
            ],
            "sheetResultCode": self.sheet_result_code,
            "sheetResult": self.sheet_result,
        }


class SetTransactionDefaultConfigResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> SetTransactionDefaultConfigResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[SetTransactionDefaultConfigResult]:
        if data is None:
            return None
        return SetTransactionDefaultConfigResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class SetTransactionDefaultConfigByUserIdResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> SetTransactionDefaultConfigByUserIdResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[SetTransactionDefaultConfigByUserIdResult]:
        if data is None:
            return None
        return SetTransactionDefaultConfigByUserIdResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class FreezeMasterDataResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> FreezeMasterDataResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[FreezeMasterDataResult]:
        if data is None:
            return None
        return FreezeMasterDataResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class FreezeMasterDataByUserIdResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> FreezeMasterDataByUserIdResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[FreezeMasterDataByUserIdResult]:
        if data is None:
            return None
        return FreezeMasterDataByUserIdResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class SignFreezeMasterDataTimestampResult(core.Gs2Result):
    body: str = None
    signature: str = None

    def with_body(self, body: str) -> SignFreezeMasterDataTimestampResult:
        self.body = body
        return self

    def with_signature(self, signature: str) -> SignFreezeMasterDataTimestampResult:
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
    ) -> Optional[SignFreezeMasterDataTimestampResult]:
        if data is None:
            return None
        return SignFreezeMasterDataTimestampResult()\
            .with_body(data.get('body'))\
            .with_signature(data.get('signature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "body": self.body,
            "signature": self.signature,
        }


class FreezeMasterDataBySignedTimestampResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> FreezeMasterDataBySignedTimestampResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[FreezeMasterDataBySignedTimestampResult]:
        if data is None:
            return None
        return FreezeMasterDataBySignedTimestampResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class FreezeMasterDataByTimestampResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> FreezeMasterDataByTimestampResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[FreezeMasterDataByTimestampResult]:
        if data is None:
            return None
        return FreezeMasterDataByTimestampResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class BatchExecuteApiResult(core.Gs2Result):
    results: List[BatchResultPayload] = None

    def with_results(self, results: List[BatchResultPayload]) -> BatchExecuteApiResult:
        self.results = results
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
    ) -> Optional[BatchExecuteApiResult]:
        if data is None:
            return None
        return BatchExecuteApiResult()\
            .with_results(None if data.get('results') is None else [
                BatchResultPayload.from_dict(data.get('results')[i])
                for i in range(len(data.get('results')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "results": None if self.results is None else [
                self.results[i].to_dict() if self.results[i] else None
                for i in range(len(self.results))
            ],
        }


class IfExpressionByUserIdResult(core.Gs2Result):

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
    ) -> Optional[IfExpressionByUserIdResult]:
        if data is None:
            return None
        return IfExpressionByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class AndExpressionByUserIdResult(core.Gs2Result):

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
    ) -> Optional[AndExpressionByUserIdResult]:
        if data is None:
            return None
        return AndExpressionByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class OrExpressionByUserIdResult(core.Gs2Result):

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
    ) -> Optional[OrExpressionByUserIdResult]:
        if data is None:
            return None
        return OrExpressionByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class IfExpressionByStampTaskResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> IfExpressionByStampTaskResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[IfExpressionByStampTaskResult]:
        if data is None:
            return None
        return IfExpressionByStampTaskResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class AndExpressionByStampTaskResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> AndExpressionByStampTaskResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[AndExpressionByStampTaskResult]:
        if data is None:
            return None
        return AndExpressionByStampTaskResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class OrExpressionByStampTaskResult(core.Gs2Result):
    new_context_stack: str = None

    def with_new_context_stack(self, new_context_stack: str) -> OrExpressionByStampTaskResult:
        self.new_context_stack = new_context_stack
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
    ) -> Optional[OrExpressionByStampTaskResult]:
        if data is None:
            return None
        return OrExpressionByStampTaskResult()\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "newContextStack": self.new_context_stack,
        }


class GetStampSheetResultResult(core.Gs2Result):
    item: StampSheetResult = None

    def with_item(self, item: StampSheetResult) -> GetStampSheetResultResult:
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
    ) -> Optional[GetStampSheetResultResult]:
        if data is None:
            return None
        return GetStampSheetResultResult()\
            .with_item(StampSheetResult.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetStampSheetResultByUserIdResult(core.Gs2Result):
    item: StampSheetResult = None

    def with_item(self, item: StampSheetResult) -> GetStampSheetResultByUserIdResult:
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
    ) -> Optional[GetStampSheetResultByUserIdResult]:
        if data is None:
            return None
        return GetStampSheetResultByUserIdResult()\
            .with_item(StampSheetResult.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class RunTransactionResult(core.Gs2Result):
    item: TransactionResult = None

    def with_item(self, item: TransactionResult) -> RunTransactionResult:
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
    ) -> Optional[RunTransactionResult]:
        if data is None:
            return None
        return RunTransactionResult()\
            .with_item(TransactionResult.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetTransactionResultResult(core.Gs2Result):
    item: TransactionResult = None

    def with_item(self, item: TransactionResult) -> GetTransactionResultResult:
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
    ) -> Optional[GetTransactionResultResult]:
        if data is None:
            return None
        return GetTransactionResultResult()\
            .with_item(TransactionResult.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetTransactionResultByUserIdResult(core.Gs2Result):
    item: TransactionResult = None

    def with_item(self, item: TransactionResult) -> GetTransactionResultByUserIdResult:
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
    ) -> Optional[GetTransactionResultByUserIdResult]:
        if data is None:
            return None
        return GetTransactionResultByUserIdResult()\
            .with_item(TransactionResult.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }