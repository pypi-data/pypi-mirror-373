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


class DescribeNamespacesRequest(core.Gs2Request):

    context_stack: str = None
    page_token: str = None
    limit: int = None

    def with_page_token(self, page_token: str) -> DescribeNamespacesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeNamespacesRequest:
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
    ) -> Optional[DescribeNamespacesRequest]:
        if data is None:
            return None
        return DescribeNamespacesRequest()\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    name: str = None
    description: str = None
    acquire_script: ScriptSetting = None
    overflow_script: ScriptSetting = None
    consume_script: ScriptSetting = None
    simple_item_acquire_script: ScriptSetting = None
    simple_item_consume_script: ScriptSetting = None
    big_item_acquire_script: ScriptSetting = None
    big_item_consume_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_acquire_script(self, acquire_script: ScriptSetting) -> CreateNamespaceRequest:
        self.acquire_script = acquire_script
        return self

    def with_overflow_script(self, overflow_script: ScriptSetting) -> CreateNamespaceRequest:
        self.overflow_script = overflow_script
        return self

    def with_consume_script(self, consume_script: ScriptSetting) -> CreateNamespaceRequest:
        self.consume_script = consume_script
        return self

    def with_simple_item_acquire_script(self, simple_item_acquire_script: ScriptSetting) -> CreateNamespaceRequest:
        self.simple_item_acquire_script = simple_item_acquire_script
        return self

    def with_simple_item_consume_script(self, simple_item_consume_script: ScriptSetting) -> CreateNamespaceRequest:
        self.simple_item_consume_script = simple_item_consume_script
        return self

    def with_big_item_acquire_script(self, big_item_acquire_script: ScriptSetting) -> CreateNamespaceRequest:
        self.big_item_acquire_script = big_item_acquire_script
        return self

    def with_big_item_consume_script(self, big_item_consume_script: ScriptSetting) -> CreateNamespaceRequest:
        self.big_item_consume_script = big_item_consume_script
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
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
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_acquire_script(ScriptSetting.from_dict(data.get('acquireScript')))\
            .with_overflow_script(ScriptSetting.from_dict(data.get('overflowScript')))\
            .with_consume_script(ScriptSetting.from_dict(data.get('consumeScript')))\
            .with_simple_item_acquire_script(ScriptSetting.from_dict(data.get('simpleItemAcquireScript')))\
            .with_simple_item_consume_script(ScriptSetting.from_dict(data.get('simpleItemConsumeScript')))\
            .with_big_item_acquire_script(ScriptSetting.from_dict(data.get('bigItemAcquireScript')))\
            .with_big_item_consume_script(ScriptSetting.from_dict(data.get('bigItemConsumeScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "acquireScript": self.acquire_script.to_dict() if self.acquire_script else None,
            "overflowScript": self.overflow_script.to_dict() if self.overflow_script else None,
            "consumeScript": self.consume_script.to_dict() if self.consume_script else None,
            "simpleItemAcquireScript": self.simple_item_acquire_script.to_dict() if self.simple_item_acquire_script else None,
            "simpleItemConsumeScript": self.simple_item_consume_script.to_dict() if self.simple_item_consume_script else None,
            "bigItemAcquireScript": self.big_item_acquire_script.to_dict() if self.big_item_acquire_script else None,
            "bigItemConsumeScript": self.big_item_consume_script.to_dict() if self.big_item_consume_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
        }


class GetNamespaceStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceStatusRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[GetNamespaceStatusRequest]:
        if data is None:
            return None
        return GetNamespaceStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetNamespaceRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[GetNamespaceRequest]:
        if data is None:
            return None
        return GetNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    description: str = None
    acquire_script: ScriptSetting = None
    overflow_script: ScriptSetting = None
    consume_script: ScriptSetting = None
    simple_item_acquire_script: ScriptSetting = None
    simple_item_consume_script: ScriptSetting = None
    big_item_acquire_script: ScriptSetting = None
    big_item_consume_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_acquire_script(self, acquire_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.acquire_script = acquire_script
        return self

    def with_overflow_script(self, overflow_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.overflow_script = overflow_script
        return self

    def with_consume_script(self, consume_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.consume_script = consume_script
        return self

    def with_simple_item_acquire_script(self, simple_item_acquire_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.simple_item_acquire_script = simple_item_acquire_script
        return self

    def with_simple_item_consume_script(self, simple_item_consume_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.simple_item_consume_script = simple_item_consume_script
        return self

    def with_big_item_acquire_script(self, big_item_acquire_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.big_item_acquire_script = big_item_acquire_script
        return self

    def with_big_item_consume_script(self, big_item_consume_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.big_item_consume_script = big_item_consume_script
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
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
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_acquire_script(ScriptSetting.from_dict(data.get('acquireScript')))\
            .with_overflow_script(ScriptSetting.from_dict(data.get('overflowScript')))\
            .with_consume_script(ScriptSetting.from_dict(data.get('consumeScript')))\
            .with_simple_item_acquire_script(ScriptSetting.from_dict(data.get('simpleItemAcquireScript')))\
            .with_simple_item_consume_script(ScriptSetting.from_dict(data.get('simpleItemConsumeScript')))\
            .with_big_item_acquire_script(ScriptSetting.from_dict(data.get('bigItemAcquireScript')))\
            .with_big_item_consume_script(ScriptSetting.from_dict(data.get('bigItemConsumeScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "acquireScript": self.acquire_script.to_dict() if self.acquire_script else None,
            "overflowScript": self.overflow_script.to_dict() if self.overflow_script else None,
            "consumeScript": self.consume_script.to_dict() if self.consume_script else None,
            "simpleItemAcquireScript": self.simple_item_acquire_script.to_dict() if self.simple_item_acquire_script else None,
            "simpleItemConsumeScript": self.simple_item_consume_script.to_dict() if self.simple_item_consume_script else None,
            "bigItemAcquireScript": self.big_item_acquire_script.to_dict() if self.big_item_acquire_script else None,
            "bigItemConsumeScript": self.big_item_consume_script.to_dict() if self.big_item_consume_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
        }


class DeleteNamespaceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteNamespaceRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[DeleteNamespaceRequest]:
        if data is None:
            return None
        return DeleteNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
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


class DumpUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> DumpUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DumpUserDataByUserIdRequest:
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
    ) -> Optional[DumpUserDataByUserIdRequest]:
        if data is None:
            return None
        return DumpUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckDumpUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> CheckDumpUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckDumpUserDataByUserIdRequest:
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
    ) -> Optional[CheckDumpUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckDumpUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CleanUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> CleanUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CleanUserDataByUserIdRequest:
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
    ) -> Optional[CleanUserDataByUserIdRequest]:
        if data is None:
            return None
        return CleanUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckCleanUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> CheckCleanUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckCleanUserDataByUserIdRequest:
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
    ) -> Optional[CheckCleanUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckCleanUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class PrepareImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> PrepareImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> PrepareImportUserDataByUserIdRequest:
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
    ) -> Optional[PrepareImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return PrepareImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class ImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> ImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> ImportUserDataByUserIdRequest:
        self.upload_token = upload_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ImportUserDataByUserIdRequest:
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
    ) -> Optional[ImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return ImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
            "timeOffsetToken": self.time_offset_token,
        }


class CheckImportUserDataByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    user_id: str = None
    upload_token: str = None
    time_offset_token: str = None

    def with_user_id(self, user_id: str) -> CheckImportUserDataByUserIdRequest:
        self.user_id = user_id
        return self

    def with_upload_token(self, upload_token: str) -> CheckImportUserDataByUserIdRequest:
        self.upload_token = upload_token
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CheckImportUserDataByUserIdRequest:
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
    ) -> Optional[CheckImportUserDataByUserIdRequest]:
        if data is None:
            return None
        return CheckImportUserDataByUserIdRequest()\
            .with_user_id(data.get('userId'))\
            .with_upload_token(data.get('uploadToken'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.user_id,
            "uploadToken": self.upload_token,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeInventoryModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInventoryModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeInventoryModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeInventoryModelMastersRequest:
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
    ) -> Optional[DescribeInventoryModelMastersRequest]:
        if data is None:
            return None
        return DescribeInventoryModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    initial_capacity: int = None
    max_capacity: int = None
    protect_referenced_item: bool = None

    def with_namespace_name(self, namespace_name: str) -> CreateInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateInventoryModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateInventoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateInventoryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_initial_capacity(self, initial_capacity: int) -> CreateInventoryModelMasterRequest:
        self.initial_capacity = initial_capacity
        return self

    def with_max_capacity(self, max_capacity: int) -> CreateInventoryModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def with_protect_referenced_item(self, protect_referenced_item: bool) -> CreateInventoryModelMasterRequest:
        self.protect_referenced_item = protect_referenced_item
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
    ) -> Optional[CreateInventoryModelMasterRequest]:
        if data is None:
            return None
        return CreateInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_protect_referenced_item(data.get('protectReferencedItem'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "initialCapacity": self.initial_capacity,
            "maxCapacity": self.max_capacity,
            "protectReferencedItem": self.protect_referenced_item,
        }


class GetInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetInventoryModelMasterRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[GetInventoryModelMasterRequest]:
        if data is None:
            return None
        return GetInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class UpdateInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    description: str = None
    metadata: str = None
    initial_capacity: int = None
    max_capacity: int = None
    protect_referenced_item: bool = None

    def with_namespace_name(self, namespace_name: str) -> UpdateInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> UpdateInventoryModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_description(self, description: str) -> UpdateInventoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateInventoryModelMasterRequest:
        self.metadata = metadata
        return self

    def with_initial_capacity(self, initial_capacity: int) -> UpdateInventoryModelMasterRequest:
        self.initial_capacity = initial_capacity
        return self

    def with_max_capacity(self, max_capacity: int) -> UpdateInventoryModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def with_protect_referenced_item(self, protect_referenced_item: bool) -> UpdateInventoryModelMasterRequest:
        self.protect_referenced_item = protect_referenced_item
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
    ) -> Optional[UpdateInventoryModelMasterRequest]:
        if data is None:
            return None
        return UpdateInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_protect_referenced_item(data.get('protectReferencedItem'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "description": self.description,
            "metadata": self.metadata,
            "initialCapacity": self.initial_capacity,
            "maxCapacity": self.max_capacity,
            "protectReferencedItem": self.protect_referenced_item,
        }


class DeleteInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteInventoryModelMasterRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[DeleteInventoryModelMasterRequest]:
        if data is None:
            return None
        return DeleteInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class DescribeInventoryModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInventoryModelsRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[DescribeInventoryModelsRequest]:
        if data is None:
            return None
        return DescribeInventoryModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetInventoryModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInventoryModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetInventoryModelRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[GetInventoryModelRequest]:
        if data is None:
            return None
        return GetInventoryModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class DescribeItemModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeItemModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeItemModelMastersRequest:
        self.inventory_name = inventory_name
        return self

    def with_page_token(self, page_token: str) -> DescribeItemModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeItemModelMastersRequest:
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
    ) -> Optional[DescribeItemModelMastersRequest]:
        if data is None:
            return None
        return DescribeItemModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    stacking_limit: int = None
    allow_multiple_stacks: bool = None
    sort_value: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> CreateItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_name(self, name: str) -> CreateItemModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateItemModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateItemModelMasterRequest:
        self.metadata = metadata
        return self

    def with_stacking_limit(self, stacking_limit: int) -> CreateItemModelMasterRequest:
        self.stacking_limit = stacking_limit
        return self

    def with_allow_multiple_stacks(self, allow_multiple_stacks: bool) -> CreateItemModelMasterRequest:
        self.allow_multiple_stacks = allow_multiple_stacks
        return self

    def with_sort_value(self, sort_value: int) -> CreateItemModelMasterRequest:
        self.sort_value = sort_value
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
    ) -> Optional[CreateItemModelMasterRequest]:
        if data is None:
            return None
        return CreateItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_stacking_limit(data.get('stackingLimit'))\
            .with_allow_multiple_stacks(data.get('allowMultipleStacks'))\
            .with_sort_value(data.get('sortValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "stackingLimit": self.stacking_limit,
            "allowMultipleStacks": self.allow_multiple_stacks,
            "sortValue": self.sort_value,
        }


class GetItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> GetItemModelMasterRequest:
        self.item_name = item_name
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
    ) -> Optional[GetItemModelMasterRequest]:
        if data is None:
            return None
        return GetItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class UpdateItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None
    description: str = None
    metadata: str = None
    stacking_limit: int = None
    allow_multiple_stacks: bool = None
    sort_value: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> UpdateItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> UpdateItemModelMasterRequest:
        self.item_name = item_name
        return self

    def with_description(self, description: str) -> UpdateItemModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateItemModelMasterRequest:
        self.metadata = metadata
        return self

    def with_stacking_limit(self, stacking_limit: int) -> UpdateItemModelMasterRequest:
        self.stacking_limit = stacking_limit
        return self

    def with_allow_multiple_stacks(self, allow_multiple_stacks: bool) -> UpdateItemModelMasterRequest:
        self.allow_multiple_stacks = allow_multiple_stacks
        return self

    def with_sort_value(self, sort_value: int) -> UpdateItemModelMasterRequest:
        self.sort_value = sort_value
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
    ) -> Optional[UpdateItemModelMasterRequest]:
        if data is None:
            return None
        return UpdateItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_stacking_limit(data.get('stackingLimit'))\
            .with_allow_multiple_stacks(data.get('allowMultipleStacks'))\
            .with_sort_value(data.get('sortValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "description": self.description,
            "metadata": self.metadata,
            "stackingLimit": self.stacking_limit,
            "allowMultipleStacks": self.allow_multiple_stacks,
            "sortValue": self.sort_value,
        }


class DeleteItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> DeleteItemModelMasterRequest:
        self.item_name = item_name
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
    ) -> Optional[DeleteItemModelMasterRequest]:
        if data is None:
            return None
        return DeleteItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class DescribeItemModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeItemModelsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeItemModelsRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[DescribeItemModelsRequest]:
        if data is None:
            return None
        return DescribeItemModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class GetItemModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemModelRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> GetItemModelRequest:
        self.item_name = item_name
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
    ) -> Optional[GetItemModelRequest]:
        if data is None:
            return None
        return GetItemModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class DescribeSimpleInventoryModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSimpleInventoryModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSimpleInventoryModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSimpleInventoryModelMastersRequest:
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
    ) -> Optional[DescribeSimpleInventoryModelMastersRequest]:
        if data is None:
            return None
        return DescribeSimpleInventoryModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateSimpleInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateSimpleInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateSimpleInventoryModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateSimpleInventoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateSimpleInventoryModelMasterRequest:
        self.metadata = metadata
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
    ) -> Optional[CreateSimpleInventoryModelMasterRequest]:
        if data is None:
            return None
        return CreateSimpleInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


class GetSimpleInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSimpleInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetSimpleInventoryModelMasterRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[GetSimpleInventoryModelMasterRequest]:
        if data is None:
            return None
        return GetSimpleInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class UpdateSimpleInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateSimpleInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> UpdateSimpleInventoryModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_description(self, description: str) -> UpdateSimpleInventoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateSimpleInventoryModelMasterRequest:
        self.metadata = metadata
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
    ) -> Optional[UpdateSimpleInventoryModelMasterRequest]:
        if data is None:
            return None
        return UpdateSimpleInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "description": self.description,
            "metadata": self.metadata,
        }


class DeleteSimpleInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSimpleInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteSimpleInventoryModelMasterRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[DeleteSimpleInventoryModelMasterRequest]:
        if data is None:
            return None
        return DeleteSimpleInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class DescribeSimpleInventoryModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSimpleInventoryModelsRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[DescribeSimpleInventoryModelsRequest]:
        if data is None:
            return None
        return DescribeSimpleInventoryModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetSimpleInventoryModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSimpleInventoryModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetSimpleInventoryModelRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[GetSimpleInventoryModelRequest]:
        if data is None:
            return None
        return GetSimpleInventoryModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class DescribeSimpleItemModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSimpleItemModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeSimpleItemModelMastersRequest:
        self.inventory_name = inventory_name
        return self

    def with_page_token(self, page_token: str) -> DescribeSimpleItemModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSimpleItemModelMastersRequest:
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
    ) -> Optional[DescribeSimpleItemModelMastersRequest]:
        if data is None:
            return None
        return DescribeSimpleItemModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateSimpleItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateSimpleItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> CreateSimpleItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_name(self, name: str) -> CreateSimpleItemModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateSimpleItemModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateSimpleItemModelMasterRequest:
        self.metadata = metadata
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
    ) -> Optional[CreateSimpleItemModelMasterRequest]:
        if data is None:
            return None
        return CreateSimpleItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


class GetSimpleItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSimpleItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetSimpleItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> GetSimpleItemModelMasterRequest:
        self.item_name = item_name
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
    ) -> Optional[GetSimpleItemModelMasterRequest]:
        if data is None:
            return None
        return GetSimpleItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class UpdateSimpleItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateSimpleItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> UpdateSimpleItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> UpdateSimpleItemModelMasterRequest:
        self.item_name = item_name
        return self

    def with_description(self, description: str) -> UpdateSimpleItemModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateSimpleItemModelMasterRequest:
        self.metadata = metadata
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
    ) -> Optional[UpdateSimpleItemModelMasterRequest]:
        if data is None:
            return None
        return UpdateSimpleItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "description": self.description,
            "metadata": self.metadata,
        }


class DeleteSimpleItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSimpleItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteSimpleItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> DeleteSimpleItemModelMasterRequest:
        self.item_name = item_name
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
    ) -> Optional[DeleteSimpleItemModelMasterRequest]:
        if data is None:
            return None
        return DeleteSimpleItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class DescribeSimpleItemModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSimpleItemModelsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeSimpleItemModelsRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[DescribeSimpleItemModelsRequest]:
        if data is None:
            return None
        return DescribeSimpleItemModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class GetSimpleItemModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSimpleItemModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetSimpleItemModelRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> GetSimpleItemModelRequest:
        self.item_name = item_name
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
    ) -> Optional[GetSimpleItemModelRequest]:
        if data is None:
            return None
        return GetSimpleItemModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class DescribeBigInventoryModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBigInventoryModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeBigInventoryModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBigInventoryModelMastersRequest:
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
    ) -> Optional[DescribeBigInventoryModelMastersRequest]:
        if data is None:
            return None
        return DescribeBigInventoryModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateBigInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateBigInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateBigInventoryModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateBigInventoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateBigInventoryModelMasterRequest:
        self.metadata = metadata
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
    ) -> Optional[CreateBigInventoryModelMasterRequest]:
        if data is None:
            return None
        return CreateBigInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


class GetBigInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBigInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetBigInventoryModelMasterRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[GetBigInventoryModelMasterRequest]:
        if data is None:
            return None
        return GetBigInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class UpdateBigInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateBigInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> UpdateBigInventoryModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_description(self, description: str) -> UpdateBigInventoryModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateBigInventoryModelMasterRequest:
        self.metadata = metadata
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
    ) -> Optional[UpdateBigInventoryModelMasterRequest]:
        if data is None:
            return None
        return UpdateBigInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "description": self.description,
            "metadata": self.metadata,
        }


class DeleteBigInventoryModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteBigInventoryModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteBigInventoryModelMasterRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[DeleteBigInventoryModelMasterRequest]:
        if data is None:
            return None
        return DeleteBigInventoryModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class DescribeBigInventoryModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBigInventoryModelsRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[DescribeBigInventoryModelsRequest]:
        if data is None:
            return None
        return DescribeBigInventoryModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetBigInventoryModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBigInventoryModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetBigInventoryModelRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[GetBigInventoryModelRequest]:
        if data is None:
            return None
        return GetBigInventoryModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class DescribeBigItemModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBigItemModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeBigItemModelMastersRequest:
        self.inventory_name = inventory_name
        return self

    def with_page_token(self, page_token: str) -> DescribeBigItemModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBigItemModelMastersRequest:
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
    ) -> Optional[DescribeBigItemModelMastersRequest]:
        if data is None:
            return None
        return DescribeBigItemModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateBigItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateBigItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> CreateBigItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_name(self, name: str) -> CreateBigItemModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateBigItemModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateBigItemModelMasterRequest:
        self.metadata = metadata
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
    ) -> Optional[CreateBigItemModelMasterRequest]:
        if data is None:
            return None
        return CreateBigItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
        }


class GetBigItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBigItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetBigItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> GetBigItemModelMasterRequest:
        self.item_name = item_name
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
    ) -> Optional[GetBigItemModelMasterRequest]:
        if data is None:
            return None
        return GetBigItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class UpdateBigItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None
    description: str = None
    metadata: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateBigItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> UpdateBigItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> UpdateBigItemModelMasterRequest:
        self.item_name = item_name
        return self

    def with_description(self, description: str) -> UpdateBigItemModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateBigItemModelMasterRequest:
        self.metadata = metadata
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
    ) -> Optional[UpdateBigItemModelMasterRequest]:
        if data is None:
            return None
        return UpdateBigItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "description": self.description,
            "metadata": self.metadata,
        }


class DeleteBigItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteBigItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteBigItemModelMasterRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> DeleteBigItemModelMasterRequest:
        self.item_name = item_name
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
    ) -> Optional[DeleteBigItemModelMasterRequest]:
        if data is None:
            return None
        return DeleteBigItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class DescribeBigItemModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBigItemModelsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeBigItemModelsRequest:
        self.inventory_name = inventory_name
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
    ) -> Optional[DescribeBigItemModelsRequest]:
        if data is None:
            return None
        return DescribeBigItemModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
        }


class GetBigItemModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBigItemModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetBigItemModelRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> GetBigItemModelRequest:
        self.item_name = item_name
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
    ) -> Optional[GetBigItemModelRequest]:
        if data is None:
            return None
        return GetBigItemModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
        }


class ExportMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> ExportMasterRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[ExportMasterRequest]:
        if data is None:
            return None
        return ExportMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetCurrentItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentItemModelMasterRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[GetCurrentItemModelMasterRequest]:
        if data is None:
            return None
        return GetCurrentItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentItemModelMasterRequest:
        self.namespace_name = namespace_name
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
    ) -> Optional[PreUpdateCurrentItemModelMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentItemModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentItemModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentItemModelMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentItemModelMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentItemModelMasterRequest:
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
    ) -> Optional[UpdateCurrentItemModelMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentItemModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mode(data.get('mode'))\
            .with_settings(data.get('settings'))\
            .with_upload_token(data.get('uploadToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "mode": self.mode,
            "settings": self.settings,
            "uploadToken": self.upload_token,
        }


class UpdateCurrentItemModelMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentItemModelMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentItemModelMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentItemModelMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentItemModelMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeInventoriesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInventoriesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeInventoriesRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeInventoriesRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeInventoriesRequest:
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
    ) -> Optional[DescribeInventoriesRequest]:
        if data is None:
            return None
        return DescribeInventoriesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeInventoriesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeInventoriesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeInventoriesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeInventoriesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeInventoriesByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeInventoriesByUserIdRequest:
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
    ) -> Optional[DescribeInventoriesByUserIdRequest]:
        if data is None:
            return None
        return DescribeInventoriesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetInventoryRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInventoryRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetInventoryRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetInventoryRequest:
        self.access_token = access_token
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
    ) -> Optional[GetInventoryRequest]:
        if data is None:
            return None
        return GetInventoryRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
        }


class GetInventoryByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetInventoryByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetInventoryByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetInventoryByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetInventoryByUserIdRequest:
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
    ) -> Optional[GetInventoryByUserIdRequest]:
        if data is None:
            return None
        return GetInventoryByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class AddCapacityByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    add_capacity_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddCapacityByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AddCapacityByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> AddCapacityByUserIdRequest:
        self.user_id = user_id
        return self

    def with_add_capacity_value(self, add_capacity_value: int) -> AddCapacityByUserIdRequest:
        self.add_capacity_value = add_capacity_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AddCapacityByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddCapacityByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AddCapacityByUserIdRequest]:
        if data is None:
            return None
        return AddCapacityByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_add_capacity_value(data.get('addCapacityValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "addCapacityValue": self.add_capacity_value,
            "timeOffsetToken": self.time_offset_token,
        }


class SetCapacityByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    new_capacity_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetCapacityByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> SetCapacityByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> SetCapacityByUserIdRequest:
        self.user_id = user_id
        return self

    def with_new_capacity_value(self, new_capacity_value: int) -> SetCapacityByUserIdRequest:
        self.new_capacity_value = new_capacity_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetCapacityByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetCapacityByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[SetCapacityByUserIdRequest]:
        if data is None:
            return None
        return SetCapacityByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_new_capacity_value(data.get('newCapacityValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "newCapacityValue": self.new_capacity_value,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteInventoryByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteInventoryByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteInventoryByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DeleteInventoryByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteInventoryByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteInventoryByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteInventoryByUserIdRequest]:
        if data is None:
            return None
        return DeleteInventoryByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyInventoryCurrentMaxCapacityRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    inventory_name: str = None
    verify_type: str = None
    current_inventory_max_capacity: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyInventoryCurrentMaxCapacityRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyInventoryCurrentMaxCapacityRequest:
        self.access_token = access_token
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyInventoryCurrentMaxCapacityRequest:
        self.inventory_name = inventory_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyInventoryCurrentMaxCapacityRequest:
        self.verify_type = verify_type
        return self

    def with_current_inventory_max_capacity(self, current_inventory_max_capacity: int) -> VerifyInventoryCurrentMaxCapacityRequest:
        self.current_inventory_max_capacity = current_inventory_max_capacity
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyInventoryCurrentMaxCapacityRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyInventoryCurrentMaxCapacityRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifyInventoryCurrentMaxCapacityRequest]:
        if data is None:
            return None
        return VerifyInventoryCurrentMaxCapacityRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_current_inventory_max_capacity(data.get('currentInventoryMaxCapacity'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "inventoryName": self.inventory_name,
            "verifyType": self.verify_type,
            "currentInventoryMaxCapacity": self.current_inventory_max_capacity,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyInventoryCurrentMaxCapacityByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    inventory_name: str = None
    verify_type: str = None
    current_inventory_max_capacity: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyInventoryCurrentMaxCapacityByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyInventoryCurrentMaxCapacityByUserIdRequest:
        self.user_id = user_id
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyInventoryCurrentMaxCapacityByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyInventoryCurrentMaxCapacityByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_current_inventory_max_capacity(self, current_inventory_max_capacity: int) -> VerifyInventoryCurrentMaxCapacityByUserIdRequest:
        self.current_inventory_max_capacity = current_inventory_max_capacity
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyInventoryCurrentMaxCapacityByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyInventoryCurrentMaxCapacityByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyInventoryCurrentMaxCapacityByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifyInventoryCurrentMaxCapacityByUserIdRequest]:
        if data is None:
            return None
        return VerifyInventoryCurrentMaxCapacityByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_current_inventory_max_capacity(data.get('currentInventoryMaxCapacity'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "inventoryName": self.inventory_name,
            "verifyType": self.verify_type,
            "currentInventoryMaxCapacity": self.current_inventory_max_capacity,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyInventoryCurrentMaxCapacityByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyInventoryCurrentMaxCapacityByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyInventoryCurrentMaxCapacityByStampTaskRequest:
        self.key_id = key_id
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
    ) -> Optional[VerifyInventoryCurrentMaxCapacityByStampTaskRequest]:
        if data is None:
            return None
        return VerifyInventoryCurrentMaxCapacityByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class AddCapacityByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AddCapacityByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AddCapacityByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[AddCapacityByStampSheetRequest]:
        if data is None:
            return None
        return AddCapacityByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetCapacityByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetCapacityByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetCapacityByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[SetCapacityByStampSheetRequest]:
        if data is None:
            return None
        return SetCapacityByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DescribeItemSetsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeItemSetsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeItemSetsRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> DescribeItemSetsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeItemSetsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeItemSetsRequest:
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
    ) -> Optional[DescribeItemSetsRequest]:
        if data is None:
            return None
        return DescribeItemSetsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeItemSetsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeItemSetsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeItemSetsByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DescribeItemSetsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeItemSetsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeItemSetsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeItemSetsByUserIdRequest:
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
    ) -> Optional[DescribeItemSetsByUserIdRequest]:
        if data is None:
            return None
        return DescribeItemSetsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetItemSetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemSetRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemSetRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetItemSetRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetItemSetRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetItemSetRequest:
        self.item_set_name = item_set_name
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
    ) -> Optional[GetItemSetRequest]:
        if data is None:
            return None
        return GetItemSetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
        }


class GetItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetItemSetByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetItemSetByUserIdRequest:
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
    ) -> Optional[GetItemSetByUserIdRequest]:
        if data is None:
            return None
        return GetItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "timeOffsetToken": self.time_offset_token,
        }


class GetItemWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemWithSignatureRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetItemWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetItemWithSignatureRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetItemWithSignatureRequest:
        self.item_set_name = item_set_name
        return self

    def with_key_id(self, key_id: str) -> GetItemWithSignatureRequest:
        self.key_id = key_id
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
    ) -> Optional[GetItemWithSignatureRequest]:
        if data is None:
            return None
        return GetItemWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "keyId": self.key_id,
        }


class GetItemWithSignatureByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    key_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetItemWithSignatureByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetItemWithSignatureByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetItemWithSignatureByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetItemWithSignatureByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetItemWithSignatureByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_key_id(self, key_id: str) -> GetItemWithSignatureByUserIdRequest:
        self.key_id = key_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetItemWithSignatureByUserIdRequest:
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
    ) -> Optional[GetItemWithSignatureByUserIdRequest]:
        if data is None:
            return None
        return GetItemWithSignatureByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_key_id(data.get('keyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "keyId": self.key_id,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None
    user_id: str = None
    acquire_count: int = None
    expires_at: int = None
    create_new_item_set: bool = None
    item_set_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AcquireItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> AcquireItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_user_id(self, user_id: str) -> AcquireItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_acquire_count(self, acquire_count: int) -> AcquireItemSetByUserIdRequest:
        self.acquire_count = acquire_count
        return self

    def with_expires_at(self, expires_at: int) -> AcquireItemSetByUserIdRequest:
        self.expires_at = expires_at
        return self

    def with_create_new_item_set(self, create_new_item_set: bool) -> AcquireItemSetByUserIdRequest:
        self.create_new_item_set = create_new_item_set
        return self

    def with_item_set_name(self, item_set_name: str) -> AcquireItemSetByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcquireItemSetByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireItemSetByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AcquireItemSetByUserIdRequest]:
        if data is None:
            return None
        return AcquireItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_user_id(data.get('userId'))\
            .with_acquire_count(data.get('acquireCount'))\
            .with_expires_at(data.get('expiresAt'))\
            .with_create_new_item_set(data.get('createNewItemSet'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "userId": self.user_id,
            "acquireCount": self.acquire_count,
            "expiresAt": self.expires_at,
            "createNewItemSet": self.create_new_item_set,
            "itemSetName": self.item_set_name,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireItemSetWithGradeByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    item_name: str = None
    user_id: str = None
    grade_model_id: str = None
    grade_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireItemSetWithGradeByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AcquireItemSetWithGradeByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> AcquireItemSetWithGradeByUserIdRequest:
        self.item_name = item_name
        return self

    def with_user_id(self, user_id: str) -> AcquireItemSetWithGradeByUserIdRequest:
        self.user_id = user_id
        return self

    def with_grade_model_id(self, grade_model_id: str) -> AcquireItemSetWithGradeByUserIdRequest:
        self.grade_model_id = grade_model_id
        return self

    def with_grade_value(self, grade_value: int) -> AcquireItemSetWithGradeByUserIdRequest:
        self.grade_value = grade_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcquireItemSetWithGradeByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireItemSetWithGradeByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AcquireItemSetWithGradeByUserIdRequest]:
        if data is None:
            return None
        return AcquireItemSetWithGradeByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_user_id(data.get('userId'))\
            .with_grade_model_id(data.get('gradeModelId'))\
            .with_grade_value(data.get('gradeValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "userId": self.user_id,
            "gradeModelId": self.grade_model_id,
            "gradeValue": self.grade_value,
            "timeOffsetToken": self.time_offset_token,
        }


class ConsumeItemSetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    consume_count: int = None
    item_set_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeItemSetRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> ConsumeItemSetRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> ConsumeItemSetRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> ConsumeItemSetRequest:
        self.item_name = item_name
        return self

    def with_consume_count(self, consume_count: int) -> ConsumeItemSetRequest:
        self.consume_count = consume_count
        return self

    def with_item_set_name(self, item_set_name: str) -> ConsumeItemSetRequest:
        self.item_set_name = item_set_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeItemSetRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[ConsumeItemSetRequest]:
        if data is None:
            return None
        return ConsumeItemSetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_consume_count(data.get('consumeCount'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "consumeCount": self.consume_count,
            "itemSetName": self.item_set_name,
        }


class ConsumeItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    consume_count: int = None
    item_set_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> ConsumeItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> ConsumeItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> ConsumeItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_consume_count(self, consume_count: int) -> ConsumeItemSetByUserIdRequest:
        self.consume_count = consume_count
        return self

    def with_item_set_name(self, item_set_name: str) -> ConsumeItemSetByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ConsumeItemSetByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeItemSetByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[ConsumeItemSetByUserIdRequest]:
        if data is None:
            return None
        return ConsumeItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_consume_count(data.get('consumeCount'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "consumeCount": self.consume_count,
            "itemSetName": self.item_set_name,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DeleteItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> DeleteItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DeleteItemSetByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteItemSetByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteItemSetByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteItemSetByUserIdRequest]:
        if data is None:
            return None
        return DeleteItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyItemSetRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    inventory_name: str = None
    item_name: str = None
    verify_type: str = None
    item_set_name: str = None
    count: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyItemSetRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyItemSetRequest:
        self.access_token = access_token
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyItemSetRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> VerifyItemSetRequest:
        self.item_name = item_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyItemSetRequest:
        self.verify_type = verify_type
        return self

    def with_item_set_name(self, item_set_name: str) -> VerifyItemSetRequest:
        self.item_set_name = item_set_name
        return self

    def with_count(self, count: int) -> VerifyItemSetRequest:
        self.count = count
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyItemSetRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyItemSetRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifyItemSetRequest]:
        if data is None:
            return None
        return VerifyItemSetRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_count(data.get('count'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "verifyType": self.verify_type,
            "itemSetName": self.item_set_name,
            "count": self.count,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyItemSetByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    inventory_name: str = None
    item_name: str = None
    verify_type: str = None
    item_set_name: str = None
    count: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyItemSetByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyItemSetByUserIdRequest:
        self.user_id = user_id
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyItemSetByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> VerifyItemSetByUserIdRequest:
        self.item_name = item_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyItemSetByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_item_set_name(self, item_set_name: str) -> VerifyItemSetByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_count(self, count: int) -> VerifyItemSetByUserIdRequest:
        self.count = count
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyItemSetByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyItemSetByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyItemSetByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifyItemSetByUserIdRequest]:
        if data is None:
            return None
        return VerifyItemSetByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_count(data.get('count'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "verifyType": self.verify_type,
            "itemSetName": self.item_set_name,
            "count": self.count,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireItemSetByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireItemSetByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AcquireItemSetByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[AcquireItemSetByStampSheetRequest]:
        if data is None:
            return None
        return AcquireItemSetByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class AcquireItemSetWithGradeByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireItemSetWithGradeByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AcquireItemSetWithGradeByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[AcquireItemSetWithGradeByStampSheetRequest]:
        if data is None:
            return None
        return AcquireItemSetWithGradeByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class ConsumeItemSetByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> ConsumeItemSetByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> ConsumeItemSetByStampTaskRequest:
        self.key_id = key_id
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
    ) -> Optional[ConsumeItemSetByStampTaskRequest]:
        if data is None:
            return None
        return ConsumeItemSetByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyItemSetByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyItemSetByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyItemSetByStampTaskRequest:
        self.key_id = key_id
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
    ) -> Optional[VerifyItemSetByStampTaskRequest]:
        if data is None:
            return None
        return VerifyItemSetByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> DescribeReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> DescribeReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DescribeReferenceOfRequest:
        self.item_set_name = item_set_name
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
    ) -> Optional[DescribeReferenceOfRequest]:
        if data is None:
            return None
        return DescribeReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
        }


class DescribeReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DescribeReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> DescribeReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DescribeReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeReferenceOfByUserIdRequest:
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
    ) -> Optional[DescribeReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return DescribeReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "timeOffsetToken": self.time_offset_token,
        }


class GetReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetReferenceOfRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> GetReferenceOfRequest:
        self.reference_of = reference_of
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
    ) -> Optional[GetReferenceOfRequest]:
        if data is None:
            return None
        return GetReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class GetReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> GetReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> GetReferenceOfByUserIdRequest:
        self.reference_of = reference_of
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetReferenceOfByUserIdRequest:
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
    ) -> Optional[GetReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return GetReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    verify_type: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> VerifyReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> VerifyReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> VerifyReferenceOfRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> VerifyReferenceOfRequest:
        self.reference_of = reference_of
        return self

    def with_verify_type(self, verify_type: str) -> VerifyReferenceOfRequest:
        self.verify_type = verify_type
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyReferenceOfRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifyReferenceOfRequest]:
        if data is None:
            return None
        return VerifyReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))\
            .with_verify_type(data.get('verifyType'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
            "verifyType": self.verify_type,
        }


class VerifyReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    verify_type: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> VerifyReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> VerifyReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> VerifyReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> VerifyReferenceOfByUserIdRequest:
        self.reference_of = reference_of
        return self

    def with_verify_type(self, verify_type: str) -> VerifyReferenceOfByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyReferenceOfByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyReferenceOfByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifyReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return VerifyReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))\
            .with_verify_type(data.get('verifyType'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
            "verifyType": self.verify_type,
            "timeOffsetToken": self.time_offset_token,
        }


class AddReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AddReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> AddReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> AddReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> AddReferenceOfRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> AddReferenceOfRequest:
        self.reference_of = reference_of
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddReferenceOfRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AddReferenceOfRequest]:
        if data is None:
            return None
        return AddReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class AddReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AddReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> AddReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> AddReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> AddReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> AddReferenceOfByUserIdRequest:
        self.reference_of = reference_of
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AddReferenceOfByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddReferenceOfByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AddReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return AddReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteReferenceOfRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteReferenceOfRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteReferenceOfRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> DeleteReferenceOfRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> DeleteReferenceOfRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DeleteReferenceOfRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> DeleteReferenceOfRequest:
        self.reference_of = reference_of
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteReferenceOfRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteReferenceOfRequest]:
        if data is None:
            return None
        return DeleteReferenceOfRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
        }


class DeleteReferenceOfByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    item_set_name: str = None
    reference_of: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteReferenceOfByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteReferenceOfByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DeleteReferenceOfByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> DeleteReferenceOfByUserIdRequest:
        self.item_name = item_name
        return self

    def with_item_set_name(self, item_set_name: str) -> DeleteReferenceOfByUserIdRequest:
        self.item_set_name = item_set_name
        return self

    def with_reference_of(self, reference_of: str) -> DeleteReferenceOfByUserIdRequest:
        self.reference_of = reference_of
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteReferenceOfByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteReferenceOfByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteReferenceOfByUserIdRequest]:
        if data is None:
            return None
        return DeleteReferenceOfByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_item_set_name(data.get('itemSetName'))\
            .with_reference_of(data.get('referenceOf'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "itemSetName": self.item_set_name,
            "referenceOf": self.reference_of,
            "timeOffsetToken": self.time_offset_token,
        }


class AddReferenceOfItemSetByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AddReferenceOfItemSetByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AddReferenceOfItemSetByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[AddReferenceOfItemSetByStampSheetRequest]:
        if data is None:
            return None
        return AddReferenceOfItemSetByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DeleteReferenceOfItemSetByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> DeleteReferenceOfItemSetByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> DeleteReferenceOfItemSetByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[DeleteReferenceOfItemSetByStampSheetRequest]:
        if data is None:
            return None
        return DeleteReferenceOfItemSetByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class VerifyReferenceOfByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyReferenceOfByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyReferenceOfByStampTaskRequest:
        self.key_id = key_id
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
    ) -> Optional[VerifyReferenceOfByStampTaskRequest]:
        if data is None:
            return None
        return VerifyReferenceOfByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeSimpleItemsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSimpleItemsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeSimpleItemsRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> DescribeSimpleItemsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeSimpleItemsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSimpleItemsRequest:
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
    ) -> Optional[DescribeSimpleItemsRequest]:
        if data is None:
            return None
        return DescribeSimpleItemsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeSimpleItemsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeSimpleItemsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeSimpleItemsByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DescribeSimpleItemsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeSimpleItemsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeSimpleItemsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeSimpleItemsByUserIdRequest:
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
    ) -> Optional[DescribeSimpleItemsByUserIdRequest]:
        if data is None:
            return None
        return DescribeSimpleItemsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetSimpleItemRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSimpleItemRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetSimpleItemRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetSimpleItemRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetSimpleItemRequest:
        self.item_name = item_name
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
    ) -> Optional[GetSimpleItemRequest]:
        if data is None:
            return None
        return GetSimpleItemRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
        }


class GetSimpleItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSimpleItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetSimpleItemByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetSimpleItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetSimpleItemByUserIdRequest:
        self.item_name = item_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetSimpleItemByUserIdRequest:
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
    ) -> Optional[GetSimpleItemByUserIdRequest]:
        if data is None:
            return None
        return GetSimpleItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "timeOffsetToken": self.time_offset_token,
        }


class GetSimpleItemWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSimpleItemWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetSimpleItemWithSignatureRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetSimpleItemWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetSimpleItemWithSignatureRequest:
        self.item_name = item_name
        return self

    def with_key_id(self, key_id: str) -> GetSimpleItemWithSignatureRequest:
        self.key_id = key_id
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
    ) -> Optional[GetSimpleItemWithSignatureRequest]:
        if data is None:
            return None
        return GetSimpleItemWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "keyId": self.key_id,
        }


class GetSimpleItemWithSignatureByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    key_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetSimpleItemWithSignatureByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetSimpleItemWithSignatureByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetSimpleItemWithSignatureByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetSimpleItemWithSignatureByUserIdRequest:
        self.item_name = item_name
        return self

    def with_key_id(self, key_id: str) -> GetSimpleItemWithSignatureByUserIdRequest:
        self.key_id = key_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetSimpleItemWithSignatureByUserIdRequest:
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
    ) -> Optional[GetSimpleItemWithSignatureByUserIdRequest]:
        if data is None:
            return None
        return GetSimpleItemWithSignatureByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_key_id(data.get('keyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "keyId": self.key_id,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireSimpleItemsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    acquire_counts: List[AcquireCount] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireSimpleItemsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AcquireSimpleItemsByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> AcquireSimpleItemsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_acquire_counts(self, acquire_counts: List[AcquireCount]) -> AcquireSimpleItemsByUserIdRequest:
        self.acquire_counts = acquire_counts
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcquireSimpleItemsByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireSimpleItemsByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AcquireSimpleItemsByUserIdRequest]:
        if data is None:
            return None
        return AcquireSimpleItemsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_acquire_counts(None if data.get('acquireCounts') is None else [
                AcquireCount.from_dict(data.get('acquireCounts')[i])
                for i in range(len(data.get('acquireCounts')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "acquireCounts": None if self.acquire_counts is None else [
                self.acquire_counts[i].to_dict() if self.acquire_counts[i] else None
                for i in range(len(self.acquire_counts))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class ConsumeSimpleItemsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    consume_counts: List[ConsumeCount] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeSimpleItemsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> ConsumeSimpleItemsRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> ConsumeSimpleItemsRequest:
        self.access_token = access_token
        return self

    def with_consume_counts(self, consume_counts: List[ConsumeCount]) -> ConsumeSimpleItemsRequest:
        self.consume_counts = consume_counts
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeSimpleItemsRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[ConsumeSimpleItemsRequest]:
        if data is None:
            return None
        return ConsumeSimpleItemsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_consume_counts(None if data.get('consumeCounts') is None else [
                ConsumeCount.from_dict(data.get('consumeCounts')[i])
                for i in range(len(data.get('consumeCounts')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "consumeCounts": None if self.consume_counts is None else [
                self.consume_counts[i].to_dict() if self.consume_counts[i] else None
                for i in range(len(self.consume_counts))
            ],
        }


class ConsumeSimpleItemsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    consume_counts: List[ConsumeCount] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeSimpleItemsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> ConsumeSimpleItemsByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> ConsumeSimpleItemsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_consume_counts(self, consume_counts: List[ConsumeCount]) -> ConsumeSimpleItemsByUserIdRequest:
        self.consume_counts = consume_counts
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ConsumeSimpleItemsByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeSimpleItemsByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[ConsumeSimpleItemsByUserIdRequest]:
        if data is None:
            return None
        return ConsumeSimpleItemsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_consume_counts(None if data.get('consumeCounts') is None else [
                ConsumeCount.from_dict(data.get('consumeCounts')[i])
                for i in range(len(data.get('consumeCounts')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "consumeCounts": None if self.consume_counts is None else [
                self.consume_counts[i].to_dict() if self.consume_counts[i] else None
                for i in range(len(self.consume_counts))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class SetSimpleItemsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    counts: List[HeldCount] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetSimpleItemsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> SetSimpleItemsByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> SetSimpleItemsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_counts(self, counts: List[HeldCount]) -> SetSimpleItemsByUserIdRequest:
        self.counts = counts
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetSimpleItemsByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetSimpleItemsByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[SetSimpleItemsByUserIdRequest]:
        if data is None:
            return None
        return SetSimpleItemsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_counts(None if data.get('counts') is None else [
                HeldCount.from_dict(data.get('counts')[i])
                for i in range(len(data.get('counts')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "counts": None if self.counts is None else [
                self.counts[i].to_dict() if self.counts[i] else None
                for i in range(len(self.counts))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteSimpleItemsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteSimpleItemsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteSimpleItemsByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DeleteSimpleItemsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteSimpleItemsByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteSimpleItemsByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteSimpleItemsByUserIdRequest]:
        if data is None:
            return None
        return DeleteSimpleItemsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifySimpleItemRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    inventory_name: str = None
    item_name: str = None
    verify_type: str = None
    count: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifySimpleItemRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifySimpleItemRequest:
        self.access_token = access_token
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifySimpleItemRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> VerifySimpleItemRequest:
        self.item_name = item_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifySimpleItemRequest:
        self.verify_type = verify_type
        return self

    def with_count(self, count: int) -> VerifySimpleItemRequest:
        self.count = count
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifySimpleItemRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifySimpleItemRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifySimpleItemRequest]:
        if data is None:
            return None
        return VerifySimpleItemRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_count(data.get('count'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "verifyType": self.verify_type,
            "count": self.count,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifySimpleItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    inventory_name: str = None
    item_name: str = None
    verify_type: str = None
    count: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifySimpleItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifySimpleItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifySimpleItemByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> VerifySimpleItemByUserIdRequest:
        self.item_name = item_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifySimpleItemByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_count(self, count: int) -> VerifySimpleItemByUserIdRequest:
        self.count = count
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifySimpleItemByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifySimpleItemByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifySimpleItemByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifySimpleItemByUserIdRequest]:
        if data is None:
            return None
        return VerifySimpleItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_count(data.get('count'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "verifyType": self.verify_type,
            "count": self.count,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireSimpleItemsByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireSimpleItemsByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AcquireSimpleItemsByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[AcquireSimpleItemsByStampSheetRequest]:
        if data is None:
            return None
        return AcquireSimpleItemsByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class ConsumeSimpleItemsByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> ConsumeSimpleItemsByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> ConsumeSimpleItemsByStampTaskRequest:
        self.key_id = key_id
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
    ) -> Optional[ConsumeSimpleItemsByStampTaskRequest]:
        if data is None:
            return None
        return ConsumeSimpleItemsByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class SetSimpleItemsByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetSimpleItemsByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetSimpleItemsByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[SetSimpleItemsByStampSheetRequest]:
        if data is None:
            return None
        return SetSimpleItemsByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class VerifySimpleItemByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifySimpleItemByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifySimpleItemByStampTaskRequest:
        self.key_id = key_id
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
    ) -> Optional[VerifySimpleItemByStampTaskRequest]:
        if data is None:
            return None
        return VerifySimpleItemByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class DescribeBigItemsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBigItemsRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeBigItemsRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> DescribeBigItemsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeBigItemsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBigItemsRequest:
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
    ) -> Optional[DescribeBigItemsRequest]:
        if data is None:
            return None
        return DescribeBigItemsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeBigItemsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeBigItemsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DescribeBigItemsByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DescribeBigItemsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeBigItemsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeBigItemsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeBigItemsByUserIdRequest:
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
    ) -> Optional[DescribeBigItemsByUserIdRequest]:
        if data is None:
            return None
        return DescribeBigItemsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetBigItemRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBigItemRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetBigItemRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> GetBigItemRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> GetBigItemRequest:
        self.item_name = item_name
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
    ) -> Optional[GetBigItemRequest]:
        if data is None:
            return None
        return GetBigItemRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
        }


class GetBigItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetBigItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> GetBigItemByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> GetBigItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> GetBigItemByUserIdRequest:
        self.item_name = item_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetBigItemByUserIdRequest:
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
    ) -> Optional[GetBigItemByUserIdRequest]:
        if data is None:
            return None
        return GetBigItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireBigItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    acquire_count: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireBigItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> AcquireBigItemByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> AcquireBigItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> AcquireBigItemByUserIdRequest:
        self.item_name = item_name
        return self

    def with_acquire_count(self, acquire_count: str) -> AcquireBigItemByUserIdRequest:
        self.acquire_count = acquire_count
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcquireBigItemByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireBigItemByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[AcquireBigItemByUserIdRequest]:
        if data is None:
            return None
        return AcquireBigItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_acquire_count(data.get('acquireCount'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "acquireCount": self.acquire_count,
            "timeOffsetToken": self.time_offset_token,
        }


class ConsumeBigItemRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    access_token: str = None
    item_name: str = None
    consume_count: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeBigItemRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> ConsumeBigItemRequest:
        self.inventory_name = inventory_name
        return self

    def with_access_token(self, access_token: str) -> ConsumeBigItemRequest:
        self.access_token = access_token
        return self

    def with_item_name(self, item_name: str) -> ConsumeBigItemRequest:
        self.item_name = item_name
        return self

    def with_consume_count(self, consume_count: str) -> ConsumeBigItemRequest:
        self.consume_count = consume_count
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeBigItemRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[ConsumeBigItemRequest]:
        if data is None:
            return None
        return ConsumeBigItemRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_access_token(data.get('accessToken'))\
            .with_item_name(data.get('itemName'))\
            .with_consume_count(data.get('consumeCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "accessToken": self.access_token,
            "itemName": self.item_name,
            "consumeCount": self.consume_count,
        }


class ConsumeBigItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    consume_count: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeBigItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> ConsumeBigItemByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> ConsumeBigItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> ConsumeBigItemByUserIdRequest:
        self.item_name = item_name
        return self

    def with_consume_count(self, consume_count: str) -> ConsumeBigItemByUserIdRequest:
        self.consume_count = consume_count
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ConsumeBigItemByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeBigItemByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[ConsumeBigItemByUserIdRequest]:
        if data is None:
            return None
        return ConsumeBigItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_consume_count(data.get('consumeCount'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "consumeCount": self.consume_count,
            "timeOffsetToken": self.time_offset_token,
        }


class SetBigItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    count: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetBigItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> SetBigItemByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> SetBigItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> SetBigItemByUserIdRequest:
        self.item_name = item_name
        return self

    def with_count(self, count: str) -> SetBigItemByUserIdRequest:
        self.count = count
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetBigItemByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetBigItemByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[SetBigItemByUserIdRequest]:
        if data is None:
            return None
        return SetBigItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_count(data.get('count'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "count": self.count,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteBigItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    inventory_name: str = None
    user_id: str = None
    item_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteBigItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_inventory_name(self, inventory_name: str) -> DeleteBigItemByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_user_id(self, user_id: str) -> DeleteBigItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_item_name(self, item_name: str) -> DeleteBigItemByUserIdRequest:
        self.item_name = item_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteBigItemByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteBigItemByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[DeleteBigItemByUserIdRequest]:
        if data is None:
            return None
        return DeleteBigItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_user_id(data.get('userId'))\
            .with_item_name(data.get('itemName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "inventoryName": self.inventory_name,
            "userId": self.user_id,
            "itemName": self.item_name,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyBigItemRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    inventory_name: str = None
    item_name: str = None
    verify_type: str = None
    count: str = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyBigItemRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyBigItemRequest:
        self.access_token = access_token
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyBigItemRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> VerifyBigItemRequest:
        self.item_name = item_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyBigItemRequest:
        self.verify_type = verify_type
        return self

    def with_count(self, count: str) -> VerifyBigItemRequest:
        self.count = count
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyBigItemRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyBigItemRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifyBigItemRequest]:
        if data is None:
            return None
        return VerifyBigItemRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_count(data.get('count'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "verifyType": self.verify_type,
            "count": self.count,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyBigItemByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    inventory_name: str = None
    item_name: str = None
    verify_type: str = None
    count: str = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyBigItemByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyBigItemByUserIdRequest:
        self.user_id = user_id
        return self

    def with_inventory_name(self, inventory_name: str) -> VerifyBigItemByUserIdRequest:
        self.inventory_name = inventory_name
        return self

    def with_item_name(self, item_name: str) -> VerifyBigItemByUserIdRequest:
        self.item_name = item_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyBigItemByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_count(self, count: str) -> VerifyBigItemByUserIdRequest:
        self.count = count
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyBigItemByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyBigItemByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyBigItemByUserIdRequest:
        self.duplication_avoider = duplication_avoider
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
    ) -> Optional[VerifyBigItemByUserIdRequest]:
        if data is None:
            return None
        return VerifyBigItemByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_inventory_name(data.get('inventoryName'))\
            .with_item_name(data.get('itemName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_count(data.get('count'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "inventoryName": self.inventory_name,
            "itemName": self.item_name,
            "verifyType": self.verify_type,
            "count": self.count,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireBigItemByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireBigItemByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AcquireBigItemByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[AcquireBigItemByStampSheetRequest]:
        if data is None:
            return None
        return AcquireBigItemByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class ConsumeBigItemByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> ConsumeBigItemByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> ConsumeBigItemByStampTaskRequest:
        self.key_id = key_id
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
    ) -> Optional[ConsumeBigItemByStampTaskRequest]:
        if data is None:
            return None
        return ConsumeBigItemByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class SetBigItemByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetBigItemByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetBigItemByStampSheetRequest:
        self.key_id = key_id
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
    ) -> Optional[SetBigItemByStampSheetRequest]:
        if data is None:
            return None
        return SetBigItemByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class VerifyBigItemByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyBigItemByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyBigItemByStampTaskRequest:
        self.key_id = key_id
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
    ) -> Optional[VerifyBigItemByStampTaskRequest]:
        if data is None:
            return None
        return VerifyBigItemByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }