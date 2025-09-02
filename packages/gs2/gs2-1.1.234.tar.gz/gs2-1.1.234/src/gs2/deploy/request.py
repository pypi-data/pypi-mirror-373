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


class DescribeStacksRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeStacksRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStacksRequest:
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
    ) -> Optional[DescribeStacksRequest]:
        if data is None:
            return None
        return DescribeStacksRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class PreCreateStackRequest(core.Gs2Request):

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
    ) -> Optional[PreCreateStackRequest]:
        if data is None:
            return None
        return PreCreateStackRequest()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class CreateStackRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    mode: str = None
    template: str = None
    upload_token: str = None

    def with_name(self, name: str) -> CreateStackRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateStackRequest:
        self.description = description
        return self

    def with_mode(self, mode: str) -> CreateStackRequest:
        self.mode = mode
        return self

    def with_template(self, template: str) -> CreateStackRequest:
        self.template = template
        return self

    def with_upload_token(self, upload_token: str) -> CreateStackRequest:
        self.upload_token = upload_token
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
    ) -> Optional[CreateStackRequest]:
        if data is None:
            return None
        return CreateStackRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_mode(data.get('mode'))\
            .with_template(data.get('template'))\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "mode": self.mode,
            "template": self.template,
            "uploadToken": self.upload_token,
        }


class CreateStackFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_name(self, name: str) -> CreateStackFromGitHubRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateStackFromGitHubRequest:
        self.description = description
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> CreateStackFromGitHubRequest:
        self.checkout_setting = checkout_setting
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
    ) -> Optional[CreateStackFromGitHubRequest]:
        if data is None:
            return None
        return CreateStackFromGitHubRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class PreValidateRequest(core.Gs2Request):

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
    ) -> Optional[PreValidateRequest]:
        if data is None:
            return None
        return PreValidateRequest()\

    def to_dict(self) -> Dict[str, Any]:
        return {
        }


class ValidateRequest(core.Gs2Request):

    context_stack: str = None
    mode: str = None
    template: str = None
    upload_token: str = None

    def with_mode(self, mode: str) -> ValidateRequest:
        self.mode = mode
        return self

    def with_template(self, template: str) -> ValidateRequest:
        self.template = template
        return self

    def with_upload_token(self, upload_token: str) -> ValidateRequest:
        self.upload_token = upload_token
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
    ) -> Optional[ValidateRequest]:
        if data is None:
            return None
        return ValidateRequest()\
            .with_mode(data.get('mode'))\
            .with_template(data.get('template'))\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode,
            "template": self.template,
            "uploadToken": self.upload_token,
        }


class GetStackStatusRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None

    def with_stack_name(self, stack_name: str) -> GetStackStatusRequest:
        self.stack_name = stack_name
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
    ) -> Optional[GetStackStatusRequest]:
        if data is None:
            return None
        return GetStackStatusRequest()\
            .with_stack_name(data.get('stackName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
        }


class GetStackRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None

    def with_stack_name(self, stack_name: str) -> GetStackRequest:
        self.stack_name = stack_name
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
    ) -> Optional[GetStackRequest]:
        if data is None:
            return None
        return GetStackRequest()\
            .with_stack_name(data.get('stackName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
        }


class PreUpdateStackRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None

    def with_stack_name(self, stack_name: str) -> PreUpdateStackRequest:
        self.stack_name = stack_name
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
    ) -> Optional[PreUpdateStackRequest]:
        if data is None:
            return None
        return PreUpdateStackRequest()\
            .with_stack_name(data.get('stackName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
        }


class UpdateStackRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    description: str = None
    mode: str = None
    template: str = None
    upload_token: str = None

    def with_stack_name(self, stack_name: str) -> UpdateStackRequest:
        self.stack_name = stack_name
        return self

    def with_description(self, description: str) -> UpdateStackRequest:
        self.description = description
        return self

    def with_mode(self, mode: str) -> UpdateStackRequest:
        self.mode = mode
        return self

    def with_template(self, template: str) -> UpdateStackRequest:
        self.template = template
        return self

    def with_upload_token(self, upload_token: str) -> UpdateStackRequest:
        self.upload_token = upload_token
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
    ) -> Optional[UpdateStackRequest]:
        if data is None:
            return None
        return UpdateStackRequest()\
            .with_stack_name(data.get('stackName'))\
            .with_description(data.get('description'))\
            .with_mode(data.get('mode'))\
            .with_template(data.get('template'))\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "description": self.description,
            "mode": self.mode,
            "template": self.template,
            "uploadToken": self.upload_token,
        }


class PreChangeSetRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None

    def with_stack_name(self, stack_name: str) -> PreChangeSetRequest:
        self.stack_name = stack_name
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
    ) -> Optional[PreChangeSetRequest]:
        if data is None:
            return None
        return PreChangeSetRequest()\
            .with_stack_name(data.get('stackName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
        }


class ChangeSetRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    mode: str = None
    template: str = None
    upload_token: str = None

    def with_stack_name(self, stack_name: str) -> ChangeSetRequest:
        self.stack_name = stack_name
        return self

    def with_mode(self, mode: str) -> ChangeSetRequest:
        self.mode = mode
        return self

    def with_template(self, template: str) -> ChangeSetRequest:
        self.template = template
        return self

    def with_upload_token(self, upload_token: str) -> ChangeSetRequest:
        self.upload_token = upload_token
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
    ) -> Optional[ChangeSetRequest]:
        if data is None:
            return None
        return ChangeSetRequest()\
            .with_stack_name(data.get('stackName'))\
            .with_mode(data.get('mode'))\
            .with_template(data.get('template'))\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "mode": self.mode,
            "template": self.template,
            "uploadToken": self.upload_token,
        }


class UpdateStackFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    description: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_stack_name(self, stack_name: str) -> UpdateStackFromGitHubRequest:
        self.stack_name = stack_name
        return self

    def with_description(self, description: str) -> UpdateStackFromGitHubRequest:
        self.description = description
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateStackFromGitHubRequest:
        self.checkout_setting = checkout_setting
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
    ) -> Optional[UpdateStackFromGitHubRequest]:
        if data is None:
            return None
        return UpdateStackFromGitHubRequest()\
            .with_stack_name(data.get('stackName'))\
            .with_description(data.get('description'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "description": self.description,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DeleteStackRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None

    def with_stack_name(self, stack_name: str) -> DeleteStackRequest:
        self.stack_name = stack_name
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
    ) -> Optional[DeleteStackRequest]:
        if data is None:
            return None
        return DeleteStackRequest()\
            .with_stack_name(data.get('stackName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
        }


class ForceDeleteStackRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None

    def with_stack_name(self, stack_name: str) -> ForceDeleteStackRequest:
        self.stack_name = stack_name
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
    ) -> Optional[ForceDeleteStackRequest]:
        if data is None:
            return None
        return ForceDeleteStackRequest()\
            .with_stack_name(data.get('stackName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
        }


class DeleteStackResourcesRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None

    def with_stack_name(self, stack_name: str) -> DeleteStackResourcesRequest:
        self.stack_name = stack_name
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
    ) -> Optional[DeleteStackResourcesRequest]:
        if data is None:
            return None
        return DeleteStackResourcesRequest()\
            .with_stack_name(data.get('stackName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
        }


class DeleteStackEntityRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None

    def with_stack_name(self, stack_name: str) -> DeleteStackEntityRequest:
        self.stack_name = stack_name
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
    ) -> Optional[DeleteStackEntityRequest]:
        if data is None:
            return None
        return DeleteStackEntityRequest()\
            .with_stack_name(data.get('stackName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
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


class DescribeResourcesRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    page_token: str = None
    limit: int = None

    def with_stack_name(self, stack_name: str) -> DescribeResourcesRequest:
        self.stack_name = stack_name
        return self

    def with_page_token(self, page_token: str) -> DescribeResourcesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeResourcesRequest:
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
    ) -> Optional[DescribeResourcesRequest]:
        if data is None:
            return None
        return DescribeResourcesRequest()\
            .with_stack_name(data.get('stackName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetResourceRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    resource_name: str = None

    def with_stack_name(self, stack_name: str) -> GetResourceRequest:
        self.stack_name = stack_name
        return self

    def with_resource_name(self, resource_name: str) -> GetResourceRequest:
        self.resource_name = resource_name
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
    ) -> Optional[GetResourceRequest]:
        if data is None:
            return None
        return GetResourceRequest()\
            .with_stack_name(data.get('stackName'))\
            .with_resource_name(data.get('resourceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "resourceName": self.resource_name,
        }


class DescribeEventsRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    page_token: str = None
    limit: int = None

    def with_stack_name(self, stack_name: str) -> DescribeEventsRequest:
        self.stack_name = stack_name
        return self

    def with_page_token(self, page_token: str) -> DescribeEventsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeEventsRequest:
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
    ) -> Optional[DescribeEventsRequest]:
        if data is None:
            return None
        return DescribeEventsRequest()\
            .with_stack_name(data.get('stackName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetEventRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    event_name: str = None

    def with_stack_name(self, stack_name: str) -> GetEventRequest:
        self.stack_name = stack_name
        return self

    def with_event_name(self, event_name: str) -> GetEventRequest:
        self.event_name = event_name
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
    ) -> Optional[GetEventRequest]:
        if data is None:
            return None
        return GetEventRequest()\
            .with_stack_name(data.get('stackName'))\
            .with_event_name(data.get('eventName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "eventName": self.event_name,
        }


class DescribeOutputsRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    page_token: str = None
    limit: int = None

    def with_stack_name(self, stack_name: str) -> DescribeOutputsRequest:
        self.stack_name = stack_name
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
            .with_stack_name(data.get('stackName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class GetOutputRequest(core.Gs2Request):

    context_stack: str = None
    stack_name: str = None
    output_name: str = None

    def with_stack_name(self, stack_name: str) -> GetOutputRequest:
        self.stack_name = stack_name
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
            .with_stack_name(data.get('stackName'))\
            .with_output_name(data.get('outputName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stackName": self.stack_name,
            "outputName": self.output_name,
        }