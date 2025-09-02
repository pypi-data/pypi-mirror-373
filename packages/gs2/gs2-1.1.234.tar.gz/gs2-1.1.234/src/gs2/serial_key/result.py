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


class DumpUserDataByUserIdResult(core.Gs2Result):

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
    ) -> Optional[DumpUserDataByUserIdResult]:
        if data is None:
            return None
        return DumpUserDataByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class CheckDumpUserDataByUserIdResult(core.Gs2Result):
    url: str = None

    def with_url(self, url: str) -> CheckDumpUserDataByUserIdResult:
        self.url = url
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
    ) -> Optional[CheckDumpUserDataByUserIdResult]:
        if data is None:
            return None
        return CheckDumpUserDataByUserIdResult()\
            .with_url(data.get('url'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
        }


class CleanUserDataByUserIdResult(core.Gs2Result):

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
    ) -> Optional[CleanUserDataByUserIdResult]:
        if data is None:
            return None
        return CleanUserDataByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class CheckCleanUserDataByUserIdResult(core.Gs2Result):

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
    ) -> Optional[CheckCleanUserDataByUserIdResult]:
        if data is None:
            return None
        return CheckCleanUserDataByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class PrepareImportUserDataByUserIdResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PrepareImportUserDataByUserIdResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PrepareImportUserDataByUserIdResult:
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
    ) -> Optional[PrepareImportUserDataByUserIdResult]:
        if data is None:
            return None
        return PrepareImportUserDataByUserIdResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class ImportUserDataByUserIdResult(core.Gs2Result):

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
    ) -> Optional[ImportUserDataByUserIdResult]:
        if data is None:
            return None
        return ImportUserDataByUserIdResult()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class CheckImportUserDataByUserIdResult(core.Gs2Result):
    url: str = None

    def with_url(self, url: str) -> CheckImportUserDataByUserIdResult:
        self.url = url
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
    ) -> Optional[CheckImportUserDataByUserIdResult]:
        if data is None:
            return None
        return CheckImportUserDataByUserIdResult()\
            .with_url(data.get('url'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
        }


class DescribeIssueJobsResult(core.Gs2Result):
    items: List[IssueJob] = None
    next_page_token: str = None

    def with_items(self, items: List[IssueJob]) -> DescribeIssueJobsResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeIssueJobsResult:
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
    ) -> Optional[DescribeIssueJobsResult]:
        if data is None:
            return None
        return DescribeIssueJobsResult()\
            .with_items(None if data.get('items') is None else [
                IssueJob.from_dict(data.get('items')[i])
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


class GetIssueJobResult(core.Gs2Result):
    item: IssueJob = None

    def with_item(self, item: IssueJob) -> GetIssueJobResult:
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
    ) -> Optional[GetIssueJobResult]:
        if data is None:
            return None
        return GetIssueJobResult()\
            .with_item(IssueJob.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class IssueResult(core.Gs2Result):
    item: IssueJob = None

    def with_item(self, item: IssueJob) -> IssueResult:
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
    ) -> Optional[IssueResult]:
        if data is None:
            return None
        return IssueResult()\
            .with_item(IssueJob.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeSerialKeysResult(core.Gs2Result):
    items: List[SerialKey] = None
    next_page_token: str = None

    def with_items(self, items: List[SerialKey]) -> DescribeSerialKeysResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeSerialKeysResult:
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
    ) -> Optional[DescribeSerialKeysResult]:
        if data is None:
            return None
        return DescribeSerialKeysResult()\
            .with_items(None if data.get('items') is None else [
                SerialKey.from_dict(data.get('items')[i])
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


class DownloadSerialCodesResult(core.Gs2Result):
    url: str = None

    def with_url(self, url: str) -> DownloadSerialCodesResult:
        self.url = url
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
    ) -> Optional[DownloadSerialCodesResult]:
        if data is None:
            return None
        return DownloadSerialCodesResult()\
            .with_url(data.get('url'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
        }


class IssueOnceResult(core.Gs2Result):
    item: SerialKey = None

    def with_item(self, item: SerialKey) -> IssueOnceResult:
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
    ) -> Optional[IssueOnceResult]:
        if data is None:
            return None
        return IssueOnceResult()\
            .with_item(SerialKey.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetSerialKeyResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None

    def with_item(self, item: SerialKey) -> GetSerialKeyResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> GetSerialKeyResult:
        self.campaign_model = campaign_model
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
    ) -> Optional[GetSerialKeyResult]:
        if data is None:
            return None
        return GetSerialKeyResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
        }


class VerifyCodeResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None

    def with_item(self, item: SerialKey) -> VerifyCodeResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> VerifyCodeResult:
        self.campaign_model = campaign_model
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
    ) -> Optional[VerifyCodeResult]:
        if data is None:
            return None
        return VerifyCodeResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
        }


class VerifyCodeByUserIdResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None

    def with_item(self, item: SerialKey) -> VerifyCodeByUserIdResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> VerifyCodeByUserIdResult:
        self.campaign_model = campaign_model
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
    ) -> Optional[VerifyCodeByUserIdResult]:
        if data is None:
            return None
        return VerifyCodeByUserIdResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
        }


class UseResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None

    def with_item(self, item: SerialKey) -> UseResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> UseResult:
        self.campaign_model = campaign_model
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
    ) -> Optional[UseResult]:
        if data is None:
            return None
        return UseResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
        }


class UseByUserIdResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None

    def with_item(self, item: SerialKey) -> UseByUserIdResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> UseByUserIdResult:
        self.campaign_model = campaign_model
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
    ) -> Optional[UseByUserIdResult]:
        if data is None:
            return None
        return UseByUserIdResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
        }


class RevertUseByUserIdResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None

    def with_item(self, item: SerialKey) -> RevertUseByUserIdResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> RevertUseByUserIdResult:
        self.campaign_model = campaign_model
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
    ) -> Optional[RevertUseByUserIdResult]:
        if data is None:
            return None
        return RevertUseByUserIdResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
        }


class UseByStampTaskResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None
    new_context_stack: str = None

    def with_item(self, item: SerialKey) -> UseByStampTaskResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> UseByStampTaskResult:
        self.campaign_model = campaign_model
        return self

    def with_new_context_stack(self, new_context_stack: str) -> UseByStampTaskResult:
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
    ) -> Optional[UseByStampTaskResult]:
        if data is None:
            return None
        return UseByStampTaskResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
            "newContextStack": self.new_context_stack,
        }


class RevertUseByStampSheetResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None

    def with_item(self, item: SerialKey) -> RevertUseByStampSheetResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> RevertUseByStampSheetResult:
        self.campaign_model = campaign_model
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
    ) -> Optional[RevertUseByStampSheetResult]:
        if data is None:
            return None
        return RevertUseByStampSheetResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
        }


class VerifyByStampTaskResult(core.Gs2Result):
    item: SerialKey = None
    campaign_model: CampaignModel = None
    new_context_stack: str = None

    def with_item(self, item: SerialKey) -> VerifyByStampTaskResult:
        self.item = item
        return self

    def with_campaign_model(self, campaign_model: CampaignModel) -> VerifyByStampTaskResult:
        self.campaign_model = campaign_model
        return self

    def with_new_context_stack(self, new_context_stack: str) -> VerifyByStampTaskResult:
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
    ) -> Optional[VerifyByStampTaskResult]:
        if data is None:
            return None
        return VerifyByStampTaskResult()\
            .with_item(SerialKey.from_dict(data.get('item')))\
            .with_campaign_model(CampaignModel.from_dict(data.get('campaignModel')))\
            .with_new_context_stack(data.get('newContextStack'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
            "campaignModel": self.campaign_model.to_dict() if self.campaign_model else None,
            "newContextStack": self.new_context_stack,
        }


class IssueOnceByStampSheetResult(core.Gs2Result):
    item: SerialKey = None

    def with_item(self, item: SerialKey) -> IssueOnceByStampSheetResult:
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
    ) -> Optional[IssueOnceByStampSheetResult]:
        if data is None:
            return None
        return IssueOnceByStampSheetResult()\
            .with_item(SerialKey.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeCampaignModelsResult(core.Gs2Result):
    items: List[CampaignModel] = None

    def with_items(self, items: List[CampaignModel]) -> DescribeCampaignModelsResult:
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
    ) -> Optional[DescribeCampaignModelsResult]:
        if data is None:
            return None
        return DescribeCampaignModelsResult()\
            .with_items(None if data.get('items') is None else [
                CampaignModel.from_dict(data.get('items')[i])
                for i in range(len(data.get('items')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": None if self.items is None else [
                self.items[i].to_dict() if self.items[i] else None
                for i in range(len(self.items))
            ],
        }


class GetCampaignModelResult(core.Gs2Result):
    item: CampaignModel = None

    def with_item(self, item: CampaignModel) -> GetCampaignModelResult:
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
    ) -> Optional[GetCampaignModelResult]:
        if data is None:
            return None
        return GetCampaignModelResult()\
            .with_item(CampaignModel.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DescribeCampaignModelMastersResult(core.Gs2Result):
    items: List[CampaignModelMaster] = None
    next_page_token: str = None

    def with_items(self, items: List[CampaignModelMaster]) -> DescribeCampaignModelMastersResult:
        self.items = items
        return self

    def with_next_page_token(self, next_page_token: str) -> DescribeCampaignModelMastersResult:
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
    ) -> Optional[DescribeCampaignModelMastersResult]:
        if data is None:
            return None
        return DescribeCampaignModelMastersResult()\
            .with_items(None if data.get('items') is None else [
                CampaignModelMaster.from_dict(data.get('items')[i])
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


class CreateCampaignModelMasterResult(core.Gs2Result):
    item: CampaignModelMaster = None

    def with_item(self, item: CampaignModelMaster) -> CreateCampaignModelMasterResult:
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
    ) -> Optional[CreateCampaignModelMasterResult]:
        if data is None:
            return None
        return CreateCampaignModelMasterResult()\
            .with_item(CampaignModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCampaignModelMasterResult(core.Gs2Result):
    item: CampaignModelMaster = None

    def with_item(self, item: CampaignModelMaster) -> GetCampaignModelMasterResult:
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
    ) -> Optional[GetCampaignModelMasterResult]:
        if data is None:
            return None
        return GetCampaignModelMasterResult()\
            .with_item(CampaignModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCampaignModelMasterResult(core.Gs2Result):
    item: CampaignModelMaster = None

    def with_item(self, item: CampaignModelMaster) -> UpdateCampaignModelMasterResult:
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
    ) -> Optional[UpdateCampaignModelMasterResult]:
        if data is None:
            return None
        return UpdateCampaignModelMasterResult()\
            .with_item(CampaignModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class DeleteCampaignModelMasterResult(core.Gs2Result):
    item: CampaignModelMaster = None

    def with_item(self, item: CampaignModelMaster) -> DeleteCampaignModelMasterResult:
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
    ) -> Optional[DeleteCampaignModelMasterResult]:
        if data is None:
            return None
        return DeleteCampaignModelMasterResult()\
            .with_item(CampaignModelMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class ExportMasterResult(core.Gs2Result):
    item: CurrentCampaignMaster = None

    def with_item(self, item: CurrentCampaignMaster) -> ExportMasterResult:
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
            .with_item(CurrentCampaignMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class GetCurrentCampaignMasterResult(core.Gs2Result):
    item: CurrentCampaignMaster = None

    def with_item(self, item: CurrentCampaignMaster) -> GetCurrentCampaignMasterResult:
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
    ) -> Optional[GetCurrentCampaignMasterResult]:
        if data is None:
            return None
        return GetCurrentCampaignMasterResult()\
            .with_item(CurrentCampaignMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class PreUpdateCurrentCampaignMasterResult(core.Gs2Result):
    upload_token: str = None
    upload_url: str = None

    def with_upload_token(self, upload_token: str) -> PreUpdateCurrentCampaignMasterResult:
        self.upload_token = upload_token
        return self

    def with_upload_url(self, upload_url: str) -> PreUpdateCurrentCampaignMasterResult:
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
    ) -> Optional[PreUpdateCurrentCampaignMasterResult]:
        if data is None:
            return None
        return PreUpdateCurrentCampaignMasterResult()\
            .with_upload_token(data.get('uploadToken'))\
            .with_upload_url(data.get('uploadUrl'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uploadToken": self.upload_token,
            "uploadUrl": self.upload_url,
        }


class UpdateCurrentCampaignMasterResult(core.Gs2Result):
    item: CurrentCampaignMaster = None

    def with_item(self, item: CurrentCampaignMaster) -> UpdateCurrentCampaignMasterResult:
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
    ) -> Optional[UpdateCurrentCampaignMasterResult]:
        if data is None:
            return None
        return UpdateCurrentCampaignMasterResult()\
            .with_item(CurrentCampaignMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }


class UpdateCurrentCampaignMasterFromGitHubResult(core.Gs2Result):
    item: CurrentCampaignMaster = None

    def with_item(self, item: CurrentCampaignMaster) -> UpdateCurrentCampaignMasterFromGitHubResult:
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
    ) -> Optional[UpdateCurrentCampaignMasterFromGitHubResult]:
        if data is None:
            return None
        return UpdateCurrentCampaignMasterFromGitHubResult()\
            .with_item(CurrentCampaignMaster.from_dict(data.get('item')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item.to_dict() if self.item else None,
        }