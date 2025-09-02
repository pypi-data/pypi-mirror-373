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
    overflow_trigger_script: str = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_overflow_trigger_script(self, overflow_trigger_script: str) -> CreateNamespaceRequest:
        self.overflow_trigger_script = overflow_trigger_script
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
            .with_overflow_trigger_script(data.get('overflowTriggerScript'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "overflowTriggerScript": self.overflow_trigger_script,
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
    overflow_trigger_script: str = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_overflow_trigger_script(self, overflow_trigger_script: str) -> UpdateNamespaceRequest:
        self.overflow_trigger_script = overflow_trigger_script
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
            .with_overflow_trigger_script(data.get('overflowTriggerScript'))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "overflowTriggerScript": self.overflow_trigger_script,
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


class DescribeStaminaModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStaminaModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeStaminaModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStaminaModelMastersRequest:
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
    ) -> Optional[DescribeStaminaModelMastersRequest]:
        if data is None:
            return None
        return DescribeStaminaModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateStaminaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    recover_interval_minutes: int = None
    recover_value: int = None
    initial_capacity: int = None
    is_overflow: bool = None
    max_capacity: int = None
    max_stamina_table_name: str = None
    recover_interval_table_name: str = None
    recover_value_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateStaminaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateStaminaModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateStaminaModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateStaminaModelMasterRequest:
        self.metadata = metadata
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> CreateStaminaModelMasterRequest:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> CreateStaminaModelMasterRequest:
        self.recover_value = recover_value
        return self

    def with_initial_capacity(self, initial_capacity: int) -> CreateStaminaModelMasterRequest:
        self.initial_capacity = initial_capacity
        return self

    def with_is_overflow(self, is_overflow: bool) -> CreateStaminaModelMasterRequest:
        self.is_overflow = is_overflow
        return self

    def with_max_capacity(self, max_capacity: int) -> CreateStaminaModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> CreateStaminaModelMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> CreateStaminaModelMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> CreateStaminaModelMasterRequest:
        self.recover_value_table_name = recover_value_table_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateStaminaModelMasterRequest]:
        if data is None:
            return None
        return CreateStaminaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_is_overflow(data.get('isOverflow'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
            "initialCapacity": self.initial_capacity,
            "isOverflow": self.is_overflow,
            "maxCapacity": self.max_capacity,
            "maxStaminaTableName": self.max_stamina_table_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
            "recoverValueTableName": self.recover_value_table_name,
        }


class GetStaminaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStaminaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> GetStaminaModelMasterRequest:
        self.stamina_name = stamina_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStaminaModelMasterRequest]:
        if data is None:
            return None
        return GetStaminaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
        }


class UpdateStaminaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    description: str = None
    metadata: str = None
    recover_interval_minutes: int = None
    recover_value: int = None
    initial_capacity: int = None
    is_overflow: bool = None
    max_capacity: int = None
    max_stamina_table_name: str = None
    recover_interval_table_name: str = None
    recover_value_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateStaminaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> UpdateStaminaModelMasterRequest:
        self.stamina_name = stamina_name
        return self

    def with_description(self, description: str) -> UpdateStaminaModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateStaminaModelMasterRequest:
        self.metadata = metadata
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> UpdateStaminaModelMasterRequest:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> UpdateStaminaModelMasterRequest:
        self.recover_value = recover_value
        return self

    def with_initial_capacity(self, initial_capacity: int) -> UpdateStaminaModelMasterRequest:
        self.initial_capacity = initial_capacity
        return self

    def with_is_overflow(self, is_overflow: bool) -> UpdateStaminaModelMasterRequest:
        self.is_overflow = is_overflow
        return self

    def with_max_capacity(self, max_capacity: int) -> UpdateStaminaModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> UpdateStaminaModelMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> UpdateStaminaModelMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> UpdateStaminaModelMasterRequest:
        self.recover_value_table_name = recover_value_table_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateStaminaModelMasterRequest]:
        if data is None:
            return None
        return UpdateStaminaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_initial_capacity(data.get('initialCapacity'))\
            .with_is_overflow(data.get('isOverflow'))\
            .with_max_capacity(data.get('maxCapacity'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "description": self.description,
            "metadata": self.metadata,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
            "initialCapacity": self.initial_capacity,
            "isOverflow": self.is_overflow,
            "maxCapacity": self.max_capacity,
            "maxStaminaTableName": self.max_stamina_table_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
            "recoverValueTableName": self.recover_value_table_name,
        }


class DeleteStaminaModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteStaminaModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> DeleteStaminaModelMasterRequest:
        self.stamina_name = stamina_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteStaminaModelMasterRequest]:
        if data is None:
            return None
        return DeleteStaminaModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
        }


class DescribeMaxStaminaTableMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMaxStaminaTableMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeMaxStaminaTableMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMaxStaminaTableMastersRequest:
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
    ) -> Optional[DescribeMaxStaminaTableMastersRequest]:
        if data is None:
            return None
        return DescribeMaxStaminaTableMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateMaxStaminaTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> CreateMaxStaminaTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateMaxStaminaTableMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateMaxStaminaTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateMaxStaminaTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> CreateMaxStaminaTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> CreateMaxStaminaTableMasterRequest:
        self.values = values
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateMaxStaminaTableMasterRequest]:
        if data is None:
            return None
        return CreateMaxStaminaTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class GetMaxStaminaTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    max_stamina_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMaxStaminaTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> GetMaxStaminaTableMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMaxStaminaTableMasterRequest]:
        if data is None:
            return None
        return GetMaxStaminaTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "maxStaminaTableName": self.max_stamina_table_name,
        }


class UpdateMaxStaminaTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    max_stamina_table_name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateMaxStaminaTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> UpdateMaxStaminaTableMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def with_description(self, description: str) -> UpdateMaxStaminaTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateMaxStaminaTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> UpdateMaxStaminaTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> UpdateMaxStaminaTableMasterRequest:
        self.values = values
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMaxStaminaTableMasterRequest]:
        if data is None:
            return None
        return UpdateMaxStaminaTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "maxStaminaTableName": self.max_stamina_table_name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class DeleteMaxStaminaTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    max_stamina_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMaxStaminaTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_max_stamina_table_name(self, max_stamina_table_name: str) -> DeleteMaxStaminaTableMasterRequest:
        self.max_stamina_table_name = max_stamina_table_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMaxStaminaTableMasterRequest]:
        if data is None:
            return None
        return DeleteMaxStaminaTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_max_stamina_table_name(data.get('maxStaminaTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "maxStaminaTableName": self.max_stamina_table_name,
        }


class DescribeRecoverIntervalTableMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRecoverIntervalTableMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRecoverIntervalTableMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRecoverIntervalTableMastersRequest:
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
    ) -> Optional[DescribeRecoverIntervalTableMastersRequest]:
        if data is None:
            return None
        return DescribeRecoverIntervalTableMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRecoverIntervalTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> CreateRecoverIntervalTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRecoverIntervalTableMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRecoverIntervalTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRecoverIntervalTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> CreateRecoverIntervalTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> CreateRecoverIntervalTableMasterRequest:
        self.values = values
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateRecoverIntervalTableMasterRequest]:
        if data is None:
            return None
        return CreateRecoverIntervalTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class GetRecoverIntervalTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_interval_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRecoverIntervalTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> GetRecoverIntervalTableMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRecoverIntervalTableMasterRequest]:
        if data is None:
            return None
        return GetRecoverIntervalTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
        }


class UpdateRecoverIntervalTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_interval_table_name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def with_description(self, description: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> UpdateRecoverIntervalTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> UpdateRecoverIntervalTableMasterRequest:
        self.values = values
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateRecoverIntervalTableMasterRequest]:
        if data is None:
            return None
        return UpdateRecoverIntervalTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class DeleteRecoverIntervalTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_interval_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRecoverIntervalTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_interval_table_name(self, recover_interval_table_name: str) -> DeleteRecoverIntervalTableMasterRequest:
        self.recover_interval_table_name = recover_interval_table_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRecoverIntervalTableMasterRequest]:
        if data is None:
            return None
        return DeleteRecoverIntervalTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_interval_table_name(data.get('recoverIntervalTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverIntervalTableName": self.recover_interval_table_name,
        }


class DescribeRecoverValueTableMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRecoverValueTableMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRecoverValueTableMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRecoverValueTableMastersRequest:
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
    ) -> Optional[DescribeRecoverValueTableMastersRequest]:
        if data is None:
            return None
        return DescribeRecoverValueTableMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRecoverValueTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> CreateRecoverValueTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRecoverValueTableMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRecoverValueTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRecoverValueTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> CreateRecoverValueTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> CreateRecoverValueTableMasterRequest:
        self.values = values
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateRecoverValueTableMasterRequest]:
        if data is None:
            return None
        return CreateRecoverValueTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class GetRecoverValueTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_value_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRecoverValueTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> GetRecoverValueTableMasterRequest:
        self.recover_value_table_name = recover_value_table_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRecoverValueTableMasterRequest]:
        if data is None:
            return None
        return GetRecoverValueTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverValueTableName": self.recover_value_table_name,
        }


class UpdateRecoverValueTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_value_table_name: str = None
    description: str = None
    metadata: str = None
    experience_model_id: str = None
    values: List[int] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRecoverValueTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> UpdateRecoverValueTableMasterRequest:
        self.recover_value_table_name = recover_value_table_name
        return self

    def with_description(self, description: str) -> UpdateRecoverValueTableMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRecoverValueTableMasterRequest:
        self.metadata = metadata
        return self

    def with_experience_model_id(self, experience_model_id: str) -> UpdateRecoverValueTableMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_values(self, values: List[int]) -> UpdateRecoverValueTableMasterRequest:
        self.values = values
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateRecoverValueTableMasterRequest]:
        if data is None:
            return None
        return UpdateRecoverValueTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_values(None if data.get('values') is None else [
                data.get('values')[i]
                for i in range(len(data.get('values')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverValueTableName": self.recover_value_table_name,
            "description": self.description,
            "metadata": self.metadata,
            "experienceModelId": self.experience_model_id,
            "values": None if self.values is None else [
                self.values[i]
                for i in range(len(self.values))
            ],
        }


class DeleteRecoverValueTableMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    recover_value_table_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRecoverValueTableMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_recover_value_table_name(self, recover_value_table_name: str) -> DeleteRecoverValueTableMasterRequest:
        self.recover_value_table_name = recover_value_table_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRecoverValueTableMasterRequest]:
        if data is None:
            return None
        return DeleteRecoverValueTableMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_recover_value_table_name(data.get('recoverValueTableName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "recoverValueTableName": self.recover_value_table_name,
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


class GetCurrentStaminaMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentStaminaMasterRequest:
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
    ) -> Optional[GetCurrentStaminaMasterRequest]:
        if data is None:
            return None
        return GetCurrentStaminaMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentStaminaMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentStaminaMasterRequest:
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
    ) -> Optional[PreUpdateCurrentStaminaMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentStaminaMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentStaminaMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentStaminaMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentStaminaMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentStaminaMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentStaminaMasterRequest:
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
    ) -> Optional[UpdateCurrentStaminaMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentStaminaMasterRequest()\
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


class UpdateCurrentStaminaMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentStaminaMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentStaminaMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentStaminaMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentStaminaMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeStaminaModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStaminaModelsRequest:
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
    ) -> Optional[DescribeStaminaModelsRequest]:
        if data is None:
            return None
        return DescribeStaminaModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetStaminaModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStaminaModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> GetStaminaModelRequest:
        self.stamina_name = stamina_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetStaminaModelRequest]:
        if data is None:
            return None
        return GetStaminaModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
        }


class DescribeStaminasRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStaminasRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeStaminasRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeStaminasRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStaminasRequest:
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
    ) -> Optional[DescribeStaminasRequest]:
        if data is None:
            return None
        return DescribeStaminasRequest()\
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


class DescribeStaminasByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeStaminasByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeStaminasByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeStaminasByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeStaminasByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeStaminasByUserIdRequest:
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
    ) -> Optional[DescribeStaminasByUserIdRequest]:
        if data is None:
            return None
        return DescribeStaminasByUserIdRequest()\
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


class GetStaminaRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStaminaRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> GetStaminaRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> GetStaminaRequest:
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
    ) -> Optional[GetStaminaRequest]:
        if data is None:
            return None
        return GetStaminaRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
        }


class GetStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> GetStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> GetStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetStaminaByUserIdRequest:
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
    ) -> Optional[GetStaminaByUserIdRequest]:
        if data is None:
            return None
        return GetStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class UpdateStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    value: int = None
    max_value: int = None
    recover_interval_minutes: int = None
    recover_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> UpdateStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> UpdateStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_value(self, value: int) -> UpdateStaminaByUserIdRequest:
        self.value = value
        return self

    def with_max_value(self, max_value: int) -> UpdateStaminaByUserIdRequest:
        self.max_value = max_value
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> UpdateStaminaByUserIdRequest:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_recover_value(self, recover_value: int) -> UpdateStaminaByUserIdRequest:
        self.recover_value = recover_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UpdateStaminaByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UpdateStaminaByUserIdRequest:
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
    ) -> Optional[UpdateStaminaByUserIdRequest]:
        if data is None:
            return None
        return UpdateStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_value(data.get('value'))\
            .with_max_value(data.get('maxValue'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "value": self.value,
            "maxValue": self.max_value,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "recoverValue": self.recover_value,
            "timeOffsetToken": self.time_offset_token,
        }


class ConsumeStaminaRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    consume_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeStaminaRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> ConsumeStaminaRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> ConsumeStaminaRequest:
        self.access_token = access_token
        return self

    def with_consume_value(self, consume_value: int) -> ConsumeStaminaRequest:
        self.consume_value = consume_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeStaminaRequest:
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
    ) -> Optional[ConsumeStaminaRequest]:
        if data is None:
            return None
        return ConsumeStaminaRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_consume_value(data.get('consumeValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "consumeValue": self.consume_value,
        }


class ConsumeStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    consume_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ConsumeStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> ConsumeStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> ConsumeStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_consume_value(self, consume_value: int) -> ConsumeStaminaByUserIdRequest:
        self.consume_value = consume_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ConsumeStaminaByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ConsumeStaminaByUserIdRequest:
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
    ) -> Optional[ConsumeStaminaByUserIdRequest]:
        if data is None:
            return None
        return ConsumeStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_consume_value(data.get('consumeValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "consumeValue": self.consume_value,
            "timeOffsetToken": self.time_offset_token,
        }


class ApplyStaminaRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ApplyStaminaRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> ApplyStaminaRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> ApplyStaminaRequest:
        self.access_token = access_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ApplyStaminaRequest:
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
    ) -> Optional[ApplyStaminaRequest]:
        if data is None:
            return None
        return ApplyStaminaRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
        }


class ApplyStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> ApplyStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> ApplyStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> ApplyStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> ApplyStaminaByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> ApplyStaminaByUserIdRequest:
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
    ) -> Optional[ApplyStaminaByUserIdRequest]:
        if data is None:
            return None
        return ApplyStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class RecoverStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    recover_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RecoverStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> RecoverStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> RecoverStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_recover_value(self, recover_value: int) -> RecoverStaminaByUserIdRequest:
        self.recover_value = recover_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> RecoverStaminaByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RecoverStaminaByUserIdRequest:
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
    ) -> Optional[RecoverStaminaByUserIdRequest]:
        if data is None:
            return None
        return RecoverStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "recoverValue": self.recover_value,
            "timeOffsetToken": self.time_offset_token,
        }


class RaiseMaxValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    raise_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> RaiseMaxValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> RaiseMaxValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> RaiseMaxValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_raise_value(self, raise_value: int) -> RaiseMaxValueByUserIdRequest:
        self.raise_value = raise_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> RaiseMaxValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> RaiseMaxValueByUserIdRequest:
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
    ) -> Optional[RaiseMaxValueByUserIdRequest]:
        if data is None:
            return None
        return RaiseMaxValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_raise_value(data.get('raiseValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "raiseValue": self.raise_value,
            "timeOffsetToken": self.time_offset_token,
        }


class DecreaseMaxValueRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    decrease_value: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DecreaseMaxValueRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> DecreaseMaxValueRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> DecreaseMaxValueRequest:
        self.access_token = access_token
        return self

    def with_decrease_value(self, decrease_value: int) -> DecreaseMaxValueRequest:
        self.decrease_value = decrease_value
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DecreaseMaxValueRequest:
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
    ) -> Optional[DecreaseMaxValueRequest]:
        if data is None:
            return None
        return DecreaseMaxValueRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_decrease_value(data.get('decreaseValue'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "decreaseValue": self.decrease_value,
        }


class DecreaseMaxValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    decrease_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DecreaseMaxValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> DecreaseMaxValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> DecreaseMaxValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_decrease_value(self, decrease_value: int) -> DecreaseMaxValueByUserIdRequest:
        self.decrease_value = decrease_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DecreaseMaxValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DecreaseMaxValueByUserIdRequest:
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
    ) -> Optional[DecreaseMaxValueByUserIdRequest]:
        if data is None:
            return None
        return DecreaseMaxValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_decrease_value(data.get('decreaseValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "decreaseValue": self.decrease_value,
            "timeOffsetToken": self.time_offset_token,
        }


class SetMaxValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    max_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetMaxValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetMaxValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> SetMaxValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_max_value(self, max_value: int) -> SetMaxValueByUserIdRequest:
        self.max_value = max_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetMaxValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetMaxValueByUserIdRequest:
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
    ) -> Optional[SetMaxValueByUserIdRequest]:
        if data is None:
            return None
        return SetMaxValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_max_value(data.get('maxValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "maxValue": self.max_value,
            "timeOffsetToken": self.time_offset_token,
        }


class SetRecoverIntervalByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    recover_interval_minutes: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRecoverIntervalByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetRecoverIntervalByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> SetRecoverIntervalByUserIdRequest:
        self.user_id = user_id
        return self

    def with_recover_interval_minutes(self, recover_interval_minutes: int) -> SetRecoverIntervalByUserIdRequest:
        self.recover_interval_minutes = recover_interval_minutes
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetRecoverIntervalByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetRecoverIntervalByUserIdRequest:
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
    ) -> Optional[SetRecoverIntervalByUserIdRequest]:
        if data is None:
            return None
        return SetRecoverIntervalByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_recover_interval_minutes(data.get('recoverIntervalMinutes'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "recoverIntervalMinutes": self.recover_interval_minutes,
            "timeOffsetToken": self.time_offset_token,
        }


class SetRecoverValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    recover_value: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRecoverValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetRecoverValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> SetRecoverValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_recover_value(self, recover_value: int) -> SetRecoverValueByUserIdRequest:
        self.recover_value = recover_value
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetRecoverValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetRecoverValueByUserIdRequest:
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
    ) -> Optional[SetRecoverValueByUserIdRequest]:
        if data is None:
            return None
        return SetRecoverValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_recover_value(data.get('recoverValue'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "recoverValue": self.recover_value,
            "timeOffsetToken": self.time_offset_token,
        }


class SetMaxValueByStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    key_id: str = None
    signed_status_body: str = None
    signed_status_signature: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetMaxValueByStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetMaxValueByStatusRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> SetMaxValueByStatusRequest:
        self.access_token = access_token
        return self

    def with_key_id(self, key_id: str) -> SetMaxValueByStatusRequest:
        self.key_id = key_id
        return self

    def with_signed_status_body(self, signed_status_body: str) -> SetMaxValueByStatusRequest:
        self.signed_status_body = signed_status_body
        return self

    def with_signed_status_signature(self, signed_status_signature: str) -> SetMaxValueByStatusRequest:
        self.signed_status_signature = signed_status_signature
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetMaxValueByStatusRequest:
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
    ) -> Optional[SetMaxValueByStatusRequest]:
        if data is None:
            return None
        return SetMaxValueByStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_key_id(data.get('keyId'))\
            .with_signed_status_body(data.get('signedStatusBody'))\
            .with_signed_status_signature(data.get('signedStatusSignature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "keyId": self.key_id,
            "signedStatusBody": self.signed_status_body,
            "signedStatusSignature": self.signed_status_signature,
        }


class SetRecoverIntervalByStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    key_id: str = None
    signed_status_body: str = None
    signed_status_signature: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRecoverIntervalByStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetRecoverIntervalByStatusRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> SetRecoverIntervalByStatusRequest:
        self.access_token = access_token
        return self

    def with_key_id(self, key_id: str) -> SetRecoverIntervalByStatusRequest:
        self.key_id = key_id
        return self

    def with_signed_status_body(self, signed_status_body: str) -> SetRecoverIntervalByStatusRequest:
        self.signed_status_body = signed_status_body
        return self

    def with_signed_status_signature(self, signed_status_signature: str) -> SetRecoverIntervalByStatusRequest:
        self.signed_status_signature = signed_status_signature
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetRecoverIntervalByStatusRequest:
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
    ) -> Optional[SetRecoverIntervalByStatusRequest]:
        if data is None:
            return None
        return SetRecoverIntervalByStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_key_id(data.get('keyId'))\
            .with_signed_status_body(data.get('signedStatusBody'))\
            .with_signed_status_signature(data.get('signedStatusSignature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "keyId": self.key_id,
            "signedStatusBody": self.signed_status_body,
            "signedStatusSignature": self.signed_status_signature,
        }


class SetRecoverValueByStatusRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    access_token: str = None
    key_id: str = None
    signed_status_body: str = None
    signed_status_signature: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetRecoverValueByStatusRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> SetRecoverValueByStatusRequest:
        self.stamina_name = stamina_name
        return self

    def with_access_token(self, access_token: str) -> SetRecoverValueByStatusRequest:
        self.access_token = access_token
        return self

    def with_key_id(self, key_id: str) -> SetRecoverValueByStatusRequest:
        self.key_id = key_id
        return self

    def with_signed_status_body(self, signed_status_body: str) -> SetRecoverValueByStatusRequest:
        self.signed_status_body = signed_status_body
        return self

    def with_signed_status_signature(self, signed_status_signature: str) -> SetRecoverValueByStatusRequest:
        self.signed_status_signature = signed_status_signature
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetRecoverValueByStatusRequest:
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
    ) -> Optional[SetRecoverValueByStatusRequest]:
        if data is None:
            return None
        return SetRecoverValueByStatusRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_access_token(data.get('accessToken'))\
            .with_key_id(data.get('keyId'))\
            .with_signed_status_body(data.get('signedStatusBody'))\
            .with_signed_status_signature(data.get('signedStatusSignature'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "accessToken": self.access_token,
            "keyId": self.key_id,
            "signedStatusBody": self.signed_status_body,
            "signedStatusSignature": self.signed_status_signature,
        }


class DeleteStaminaByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    stamina_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteStaminaByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_stamina_name(self, stamina_name: str) -> DeleteStaminaByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_user_id(self, user_id: str) -> DeleteStaminaByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteStaminaByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteStaminaByUserIdRequest:
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
    ) -> Optional[DeleteStaminaByUserIdRequest]:
        if data is None:
            return None
        return DeleteStaminaByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "staminaName": self.stamina_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyStaminaValueRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaValueRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyStaminaValueRequest:
        self.access_token = access_token
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaValueRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaValueRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaValueRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaValueRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaValueRequest:
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
    ) -> Optional[VerifyStaminaValueRequest]:
        if data is None:
            return None
        return VerifyStaminaValueRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyStaminaValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyStaminaValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaValueByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaValueByUserIdRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaValueByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyStaminaValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaValueByUserIdRequest:
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
    ) -> Optional[VerifyStaminaValueByUserIdRequest]:
        if data is None:
            return None
        return VerifyStaminaValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyStaminaMaxValueRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaMaxValueRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyStaminaMaxValueRequest:
        self.access_token = access_token
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaMaxValueRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaMaxValueRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaMaxValueRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaMaxValueRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaMaxValueRequest:
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
    ) -> Optional[VerifyStaminaMaxValueRequest]:
        if data is None:
            return None
        return VerifyStaminaMaxValueRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyStaminaMaxValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaMaxValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyStaminaMaxValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaMaxValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaMaxValueByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaMaxValueByUserIdRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaMaxValueByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyStaminaMaxValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaMaxValueByUserIdRequest:
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
    ) -> Optional[VerifyStaminaMaxValueByUserIdRequest]:
        if data is None:
            return None
        return VerifyStaminaMaxValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyStaminaRecoverIntervalMinutesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaRecoverIntervalMinutesRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyStaminaRecoverIntervalMinutesRequest:
        self.access_token = access_token
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaRecoverIntervalMinutesRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaRecoverIntervalMinutesRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaRecoverIntervalMinutesRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaRecoverIntervalMinutesRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaRecoverIntervalMinutesRequest:
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
    ) -> Optional[VerifyStaminaRecoverIntervalMinutesRequest]:
        if data is None:
            return None
        return VerifyStaminaRecoverIntervalMinutesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyStaminaRecoverIntervalMinutesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaRecoverIntervalMinutesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyStaminaRecoverIntervalMinutesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaRecoverIntervalMinutesByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaRecoverIntervalMinutesByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaRecoverIntervalMinutesByUserIdRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaRecoverIntervalMinutesByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyStaminaRecoverIntervalMinutesByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaRecoverIntervalMinutesByUserIdRequest:
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
    ) -> Optional[VerifyStaminaRecoverIntervalMinutesByUserIdRequest]:
        if data is None:
            return None
        return VerifyStaminaRecoverIntervalMinutesByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyStaminaRecoverValueRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaRecoverValueRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyStaminaRecoverValueRequest:
        self.access_token = access_token
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaRecoverValueRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaRecoverValueRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaRecoverValueRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaRecoverValueRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaRecoverValueRequest:
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
    ) -> Optional[VerifyStaminaRecoverValueRequest]:
        if data is None:
            return None
        return VerifyStaminaRecoverValueRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyStaminaRecoverValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaRecoverValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyStaminaRecoverValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaRecoverValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaRecoverValueByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaRecoverValueByUserIdRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaRecoverValueByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyStaminaRecoverValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaRecoverValueByUserIdRequest:
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
    ) -> Optional[VerifyStaminaRecoverValueByUserIdRequest]:
        if data is None:
            return None
        return VerifyStaminaRecoverValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class VerifyStaminaOverflowValueRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaOverflowValueRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> VerifyStaminaOverflowValueRequest:
        self.access_token = access_token
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaOverflowValueRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaOverflowValueRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaOverflowValueRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaOverflowValueRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaOverflowValueRequest:
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
    ) -> Optional[VerifyStaminaOverflowValueRequest]:
        if data is None:
            return None
        return VerifyStaminaOverflowValueRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
        }


class VerifyStaminaOverflowValueByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    stamina_name: str = None
    verify_type: str = None
    value: int = None
    multiply_value_specifying_quantity: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> VerifyStaminaOverflowValueByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> VerifyStaminaOverflowValueByUserIdRequest:
        self.user_id = user_id
        return self

    def with_stamina_name(self, stamina_name: str) -> VerifyStaminaOverflowValueByUserIdRequest:
        self.stamina_name = stamina_name
        return self

    def with_verify_type(self, verify_type: str) -> VerifyStaminaOverflowValueByUserIdRequest:
        self.verify_type = verify_type
        return self

    def with_value(self, value: int) -> VerifyStaminaOverflowValueByUserIdRequest:
        self.value = value
        return self

    def with_multiply_value_specifying_quantity(self, multiply_value_specifying_quantity: bool) -> VerifyStaminaOverflowValueByUserIdRequest:
        self.multiply_value_specifying_quantity = multiply_value_specifying_quantity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> VerifyStaminaOverflowValueByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> VerifyStaminaOverflowValueByUserIdRequest:
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
    ) -> Optional[VerifyStaminaOverflowValueByUserIdRequest]:
        if data is None:
            return None
        return VerifyStaminaOverflowValueByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_stamina_name(data.get('staminaName'))\
            .with_verify_type(data.get('verifyType'))\
            .with_value(data.get('value'))\
            .with_multiply_value_specifying_quantity(data.get('multiplyValueSpecifyingQuantity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "staminaName": self.stamina_name,
            "verifyType": self.verify_type,
            "value": self.value,
            "multiplyValueSpecifyingQuantity": self.multiply_value_specifying_quantity,
            "timeOffsetToken": self.time_offset_token,
        }


class RecoverStaminaByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RecoverStaminaByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RecoverStaminaByStampSheetRequest:
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
    ) -> Optional[RecoverStaminaByStampSheetRequest]:
        if data is None:
            return None
        return RecoverStaminaByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class RaiseMaxValueByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> RaiseMaxValueByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> RaiseMaxValueByStampSheetRequest:
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
    ) -> Optional[RaiseMaxValueByStampSheetRequest]:
        if data is None:
            return None
        return RaiseMaxValueByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DecreaseMaxValueByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> DecreaseMaxValueByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> DecreaseMaxValueByStampTaskRequest:
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
    ) -> Optional[DecreaseMaxValueByStampTaskRequest]:
        if data is None:
            return None
        return DecreaseMaxValueByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class SetMaxValueByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetMaxValueByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetMaxValueByStampSheetRequest:
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
    ) -> Optional[SetMaxValueByStampSheetRequest]:
        if data is None:
            return None
        return SetMaxValueByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetRecoverIntervalByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetRecoverIntervalByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetRecoverIntervalByStampSheetRequest:
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
    ) -> Optional[SetRecoverIntervalByStampSheetRequest]:
        if data is None:
            return None
        return SetRecoverIntervalByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetRecoverValueByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetRecoverValueByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetRecoverValueByStampSheetRequest:
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
    ) -> Optional[SetRecoverValueByStampSheetRequest]:
        if data is None:
            return None
        return SetRecoverValueByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class ConsumeStaminaByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> ConsumeStaminaByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> ConsumeStaminaByStampTaskRequest:
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
    ) -> Optional[ConsumeStaminaByStampTaskRequest]:
        if data is None:
            return None
        return ConsumeStaminaByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyStaminaValueByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyStaminaValueByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyStaminaValueByStampTaskRequest:
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
    ) -> Optional[VerifyStaminaValueByStampTaskRequest]:
        if data is None:
            return None
        return VerifyStaminaValueByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyStaminaMaxValueByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyStaminaMaxValueByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyStaminaMaxValueByStampTaskRequest:
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
    ) -> Optional[VerifyStaminaMaxValueByStampTaskRequest]:
        if data is None:
            return None
        return VerifyStaminaMaxValueByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyStaminaRecoverIntervalMinutesByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyStaminaRecoverIntervalMinutesByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyStaminaRecoverIntervalMinutesByStampTaskRequest:
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
    ) -> Optional[VerifyStaminaRecoverIntervalMinutesByStampTaskRequest]:
        if data is None:
            return None
        return VerifyStaminaRecoverIntervalMinutesByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyStaminaRecoverValueByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyStaminaRecoverValueByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyStaminaRecoverValueByStampTaskRequest:
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
    ) -> Optional[VerifyStaminaRecoverValueByStampTaskRequest]:
        if data is None:
            return None
        return VerifyStaminaRecoverValueByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }


class VerifyStaminaOverflowValueByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> VerifyStaminaOverflowValueByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> VerifyStaminaOverflowValueByStampTaskRequest:
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
    ) -> Optional[VerifyStaminaOverflowValueByStampTaskRequest]:
        if data is None:
            return None
        return VerifyStaminaOverflowValueByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
        }