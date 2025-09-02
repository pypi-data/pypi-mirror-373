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
    transaction_setting: TransactionSetting = None
    enhance_script: ScriptSetting = None
    log_setting: LogSetting = None
    enable_direct_enhance: bool = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> CreateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_enhance_script(self, enhance_script: ScriptSetting) -> CreateNamespaceRequest:
        self.enhance_script = enhance_script
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_enable_direct_enhance(self, enable_direct_enhance: bool) -> CreateNamespaceRequest:
        self.enable_direct_enhance = enable_direct_enhance
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> CreateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> CreateNamespaceRequest:
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
    ) -> Optional[CreateNamespaceRequest]:
        if data is None:
            return None
        return CreateNamespaceRequest()\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_enhance_script(ScriptSetting.from_dict(data.get('enhanceScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_enable_direct_enhance(data.get('enableDirectEnhance'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "enhanceScript": self.enhance_script.to_dict() if self.enhance_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "enableDirectEnhance": self.enable_direct_enhance,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
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
    transaction_setting: TransactionSetting = None
    enhance_script: ScriptSetting = None
    log_setting: LogSetting = None
    enable_direct_enhance: bool = None
    queue_namespace_id: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> UpdateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_enhance_script(self, enhance_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.enhance_script = enhance_script
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
        return self

    def with_enable_direct_enhance(self, enable_direct_enhance: bool) -> UpdateNamespaceRequest:
        self.enable_direct_enhance = enable_direct_enhance
        return self

    def with_queue_namespace_id(self, queue_namespace_id: str) -> UpdateNamespaceRequest:
        self.queue_namespace_id = queue_namespace_id
        return self

    def with_key_id(self, key_id: str) -> UpdateNamespaceRequest:
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
    ) -> Optional[UpdateNamespaceRequest]:
        if data is None:
            return None
        return UpdateNamespaceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_description(data.get('description'))\
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_enhance_script(ScriptSetting.from_dict(data.get('enhanceScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_enable_direct_enhance(data.get('enableDirectEnhance'))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "enhanceScript": self.enhance_script.to_dict() if self.enhance_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "enableDirectEnhance": self.enable_direct_enhance,
            "queueNamespaceId": self.queue_namespace_id,
            "keyId": self.key_id,
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


class DescribeRateModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRateModelsRequest:
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
    ) -> Optional[DescribeRateModelsRequest]:
        if data is None:
            return None
        return DescribeRateModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetRateModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRateModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> GetRateModelRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRateModelRequest]:
        if data is None:
            return None
        return GetRateModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class DescribeRateModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeRateModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeRateModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeRateModelMastersRequest:
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
    ) -> Optional[DescribeRateModelMastersRequest]:
        if data is None:
            return None
        return DescribeRateModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    target_inventory_model_id: str = None
    acquire_experience_suffix: str = None
    material_inventory_model_id: str = None
    acquire_experience_hierarchy: List[str] = None
    experience_model_id: str = None
    bonus_rates: List[BonusRate] = None

    def with_namespace_name(self, namespace_name: str) -> CreateRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateRateModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateRateModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateRateModelMasterRequest:
        self.metadata = metadata
        return self

    def with_target_inventory_model_id(self, target_inventory_model_id: str) -> CreateRateModelMasterRequest:
        self.target_inventory_model_id = target_inventory_model_id
        return self

    def with_acquire_experience_suffix(self, acquire_experience_suffix: str) -> CreateRateModelMasterRequest:
        self.acquire_experience_suffix = acquire_experience_suffix
        return self

    def with_material_inventory_model_id(self, material_inventory_model_id: str) -> CreateRateModelMasterRequest:
        self.material_inventory_model_id = material_inventory_model_id
        return self

    def with_acquire_experience_hierarchy(self, acquire_experience_hierarchy: List[str]) -> CreateRateModelMasterRequest:
        self.acquire_experience_hierarchy = acquire_experience_hierarchy
        return self

    def with_experience_model_id(self, experience_model_id: str) -> CreateRateModelMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_bonus_rates(self, bonus_rates: List[BonusRate]) -> CreateRateModelMasterRequest:
        self.bonus_rates = bonus_rates
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateRateModelMasterRequest]:
        if data is None:
            return None
        return CreateRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_target_inventory_model_id(data.get('targetInventoryModelId'))\
            .with_acquire_experience_suffix(data.get('acquireExperienceSuffix'))\
            .with_material_inventory_model_id(data.get('materialInventoryModelId'))\
            .with_acquire_experience_hierarchy(None if data.get('acquireExperienceHierarchy') is None else [
                data.get('acquireExperienceHierarchy')[i]
                for i in range(len(data.get('acquireExperienceHierarchy')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_bonus_rates(None if data.get('bonusRates') is None else [
                BonusRate.from_dict(data.get('bonusRates')[i])
                for i in range(len(data.get('bonusRates')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "targetInventoryModelId": self.target_inventory_model_id,
            "acquireExperienceSuffix": self.acquire_experience_suffix,
            "materialInventoryModelId": self.material_inventory_model_id,
            "acquireExperienceHierarchy": None if self.acquire_experience_hierarchy is None else [
                self.acquire_experience_hierarchy[i]
                for i in range(len(self.acquire_experience_hierarchy))
            ],
            "experienceModelId": self.experience_model_id,
            "bonusRates": None if self.bonus_rates is None else [
                self.bonus_rates[i].to_dict() if self.bonus_rates[i] else None
                for i in range(len(self.bonus_rates))
            ],
        }


class GetRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> GetRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetRateModelMasterRequest]:
        if data is None:
            return None
        return GetRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class UpdateRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    description: str = None
    metadata: str = None
    target_inventory_model_id: str = None
    acquire_experience_suffix: str = None
    material_inventory_model_id: str = None
    acquire_experience_hierarchy: List[str] = None
    experience_model_id: str = None
    bonus_rates: List[BonusRate] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> UpdateRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def with_description(self, description: str) -> UpdateRateModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateRateModelMasterRequest:
        self.metadata = metadata
        return self

    def with_target_inventory_model_id(self, target_inventory_model_id: str) -> UpdateRateModelMasterRequest:
        self.target_inventory_model_id = target_inventory_model_id
        return self

    def with_acquire_experience_suffix(self, acquire_experience_suffix: str) -> UpdateRateModelMasterRequest:
        self.acquire_experience_suffix = acquire_experience_suffix
        return self

    def with_material_inventory_model_id(self, material_inventory_model_id: str) -> UpdateRateModelMasterRequest:
        self.material_inventory_model_id = material_inventory_model_id
        return self

    def with_acquire_experience_hierarchy(self, acquire_experience_hierarchy: List[str]) -> UpdateRateModelMasterRequest:
        self.acquire_experience_hierarchy = acquire_experience_hierarchy
        return self

    def with_experience_model_id(self, experience_model_id: str) -> UpdateRateModelMasterRequest:
        self.experience_model_id = experience_model_id
        return self

    def with_bonus_rates(self, bonus_rates: List[BonusRate]) -> UpdateRateModelMasterRequest:
        self.bonus_rates = bonus_rates
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateRateModelMasterRequest]:
        if data is None:
            return None
        return UpdateRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_target_inventory_model_id(data.get('targetInventoryModelId'))\
            .with_acquire_experience_suffix(data.get('acquireExperienceSuffix'))\
            .with_material_inventory_model_id(data.get('materialInventoryModelId'))\
            .with_acquire_experience_hierarchy(None if data.get('acquireExperienceHierarchy') is None else [
                data.get('acquireExperienceHierarchy')[i]
                for i in range(len(data.get('acquireExperienceHierarchy')))
            ])\
            .with_experience_model_id(data.get('experienceModelId'))\
            .with_bonus_rates(None if data.get('bonusRates') is None else [
                BonusRate.from_dict(data.get('bonusRates')[i])
                for i in range(len(data.get('bonusRates')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "description": self.description,
            "metadata": self.metadata,
            "targetInventoryModelId": self.target_inventory_model_id,
            "acquireExperienceSuffix": self.acquire_experience_suffix,
            "materialInventoryModelId": self.material_inventory_model_id,
            "acquireExperienceHierarchy": None if self.acquire_experience_hierarchy is None else [
                self.acquire_experience_hierarchy[i]
                for i in range(len(self.acquire_experience_hierarchy))
            ],
            "experienceModelId": self.experience_model_id,
            "bonusRates": None if self.bonus_rates is None else [
                self.bonus_rates[i].to_dict() if self.bonus_rates[i] else None
                for i in range(len(self.bonus_rates))
            ],
        }


class DeleteRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> DeleteRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteRateModelMasterRequest]:
        if data is None:
            return None
        return DeleteRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class DescribeUnleashRateModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeUnleashRateModelsRequest:
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
    ) -> Optional[DescribeUnleashRateModelsRequest]:
        if data is None:
            return None
        return DescribeUnleashRateModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetUnleashRateModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetUnleashRateModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> GetUnleashRateModelRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetUnleashRateModelRequest]:
        if data is None:
            return None
        return GetUnleashRateModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class DescribeUnleashRateModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeUnleashRateModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeUnleashRateModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeUnleashRateModelMastersRequest:
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
    ) -> Optional[DescribeUnleashRateModelMastersRequest]:
        if data is None:
            return None
        return DescribeUnleashRateModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateUnleashRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    target_inventory_model_id: str = None
    grade_model_id: str = None
    grade_entries: List[UnleashRateEntryModel] = None

    def with_namespace_name(self, namespace_name: str) -> CreateUnleashRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateUnleashRateModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateUnleashRateModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateUnleashRateModelMasterRequest:
        self.metadata = metadata
        return self

    def with_target_inventory_model_id(self, target_inventory_model_id: str) -> CreateUnleashRateModelMasterRequest:
        self.target_inventory_model_id = target_inventory_model_id
        return self

    def with_grade_model_id(self, grade_model_id: str) -> CreateUnleashRateModelMasterRequest:
        self.grade_model_id = grade_model_id
        return self

    def with_grade_entries(self, grade_entries: List[UnleashRateEntryModel]) -> CreateUnleashRateModelMasterRequest:
        self.grade_entries = grade_entries
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateUnleashRateModelMasterRequest]:
        if data is None:
            return None
        return CreateUnleashRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_target_inventory_model_id(data.get('targetInventoryModelId'))\
            .with_grade_model_id(data.get('gradeModelId'))\
            .with_grade_entries(None if data.get('gradeEntries') is None else [
                UnleashRateEntryModel.from_dict(data.get('gradeEntries')[i])
                for i in range(len(data.get('gradeEntries')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "targetInventoryModelId": self.target_inventory_model_id,
            "gradeModelId": self.grade_model_id,
            "gradeEntries": None if self.grade_entries is None else [
                self.grade_entries[i].to_dict() if self.grade_entries[i] else None
                for i in range(len(self.grade_entries))
            ],
        }


class GetUnleashRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetUnleashRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> GetUnleashRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetUnleashRateModelMasterRequest]:
        if data is None:
            return None
        return GetUnleashRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class UpdateUnleashRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    description: str = None
    metadata: str = None
    target_inventory_model_id: str = None
    grade_model_id: str = None
    grade_entries: List[UnleashRateEntryModel] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateUnleashRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> UpdateUnleashRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def with_description(self, description: str) -> UpdateUnleashRateModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateUnleashRateModelMasterRequest:
        self.metadata = metadata
        return self

    def with_target_inventory_model_id(self, target_inventory_model_id: str) -> UpdateUnleashRateModelMasterRequest:
        self.target_inventory_model_id = target_inventory_model_id
        return self

    def with_grade_model_id(self, grade_model_id: str) -> UpdateUnleashRateModelMasterRequest:
        self.grade_model_id = grade_model_id
        return self

    def with_grade_entries(self, grade_entries: List[UnleashRateEntryModel]) -> UpdateUnleashRateModelMasterRequest:
        self.grade_entries = grade_entries
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateUnleashRateModelMasterRequest]:
        if data is None:
            return None
        return UpdateUnleashRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_target_inventory_model_id(data.get('targetInventoryModelId'))\
            .with_grade_model_id(data.get('gradeModelId'))\
            .with_grade_entries(None if data.get('gradeEntries') is None else [
                UnleashRateEntryModel.from_dict(data.get('gradeEntries')[i])
                for i in range(len(data.get('gradeEntries')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "description": self.description,
            "metadata": self.metadata,
            "targetInventoryModelId": self.target_inventory_model_id,
            "gradeModelId": self.grade_model_id,
            "gradeEntries": None if self.grade_entries is None else [
                self.grade_entries[i].to_dict() if self.grade_entries[i] else None
                for i in range(len(self.grade_entries))
            ],
        }


class DeleteUnleashRateModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteUnleashRateModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> DeleteUnleashRateModelMasterRequest:
        self.rate_name = rate_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteUnleashRateModelMasterRequest]:
        if data is None:
            return None
        return DeleteUnleashRateModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
        }


class DirectEnhanceRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    access_token: str = None
    target_item_set_id: str = None
    materials: List[Material] = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DirectEnhanceRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> DirectEnhanceRequest:
        self.rate_name = rate_name
        return self

    def with_access_token(self, access_token: str) -> DirectEnhanceRequest:
        self.access_token = access_token
        return self

    def with_target_item_set_id(self, target_item_set_id: str) -> DirectEnhanceRequest:
        self.target_item_set_id = target_item_set_id
        return self

    def with_materials(self, materials: List[Material]) -> DirectEnhanceRequest:
        self.materials = materials
        return self

    def with_config(self, config: List[Config]) -> DirectEnhanceRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DirectEnhanceRequest:
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
    ) -> Optional[DirectEnhanceRequest]:
        if data is None:
            return None
        return DirectEnhanceRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_item_set_id(data.get('targetItemSetId'))\
            .with_materials(None if data.get('materials') is None else [
                Material.from_dict(data.get('materials')[i])
                for i in range(len(data.get('materials')))
            ])\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "accessToken": self.access_token,
            "targetItemSetId": self.target_item_set_id,
            "materials": None if self.materials is None else [
                self.materials[i].to_dict() if self.materials[i] else None
                for i in range(len(self.materials))
            ],
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class DirectEnhanceByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    user_id: str = None
    target_item_set_id: str = None
    materials: List[Material] = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DirectEnhanceByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> DirectEnhanceByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_user_id(self, user_id: str) -> DirectEnhanceByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_item_set_id(self, target_item_set_id: str) -> DirectEnhanceByUserIdRequest:
        self.target_item_set_id = target_item_set_id
        return self

    def with_materials(self, materials: List[Material]) -> DirectEnhanceByUserIdRequest:
        self.materials = materials
        return self

    def with_config(self, config: List[Config]) -> DirectEnhanceByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DirectEnhanceByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DirectEnhanceByUserIdRequest:
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
    ) -> Optional[DirectEnhanceByUserIdRequest]:
        if data is None:
            return None
        return DirectEnhanceByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_user_id(data.get('userId'))\
            .with_target_item_set_id(data.get('targetItemSetId'))\
            .with_materials(None if data.get('materials') is None else [
                Material.from_dict(data.get('materials')[i])
                for i in range(len(data.get('materials')))
            ])\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "userId": self.user_id,
            "targetItemSetId": self.target_item_set_id,
            "materials": None if self.materials is None else [
                self.materials[i].to_dict() if self.materials[i] else None
                for i in range(len(self.materials))
            ],
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DirectEnhanceByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> DirectEnhanceByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> DirectEnhanceByStampSheetRequest:
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
    ) -> Optional[DirectEnhanceByStampSheetRequest]:
        if data is None:
            return None
        return DirectEnhanceByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class UnleashRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    access_token: str = None
    target_item_set_id: str = None
    materials: List[str] = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnleashRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> UnleashRequest:
        self.rate_name = rate_name
        return self

    def with_access_token(self, access_token: str) -> UnleashRequest:
        self.access_token = access_token
        return self

    def with_target_item_set_id(self, target_item_set_id: str) -> UnleashRequest:
        self.target_item_set_id = target_item_set_id
        return self

    def with_materials(self, materials: List[str]) -> UnleashRequest:
        self.materials = materials
        return self

    def with_config(self, config: List[Config]) -> UnleashRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnleashRequest:
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
    ) -> Optional[UnleashRequest]:
        if data is None:
            return None
        return UnleashRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_access_token(data.get('accessToken'))\
            .with_target_item_set_id(data.get('targetItemSetId'))\
            .with_materials(None if data.get('materials') is None else [
                data.get('materials')[i]
                for i in range(len(data.get('materials')))
            ])\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "accessToken": self.access_token,
            "targetItemSetId": self.target_item_set_id,
            "materials": None if self.materials is None else [
                self.materials[i]
                for i in range(len(self.materials))
            ],
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class UnleashByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    user_id: str = None
    target_item_set_id: str = None
    materials: List[str] = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> UnleashByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> UnleashByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_user_id(self, user_id: str) -> UnleashByUserIdRequest:
        self.user_id = user_id
        return self

    def with_target_item_set_id(self, target_item_set_id: str) -> UnleashByUserIdRequest:
        self.target_item_set_id = target_item_set_id
        return self

    def with_materials(self, materials: List[str]) -> UnleashByUserIdRequest:
        self.materials = materials
        return self

    def with_config(self, config: List[Config]) -> UnleashByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> UnleashByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> UnleashByUserIdRequest:
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
    ) -> Optional[UnleashByUserIdRequest]:
        if data is None:
            return None
        return UnleashByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_user_id(data.get('userId'))\
            .with_target_item_set_id(data.get('targetItemSetId'))\
            .with_materials(None if data.get('materials') is None else [
                data.get('materials')[i]
                for i in range(len(data.get('materials')))
            ])\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "userId": self.user_id,
            "targetItemSetId": self.target_item_set_id,
            "materials": None if self.materials is None else [
                self.materials[i]
                for i in range(len(self.materials))
            ],
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class UnleashByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> UnleashByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> UnleashByStampSheetRequest:
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
    ) -> Optional[UnleashByStampSheetRequest]:
        if data is None:
            return None
        return UnleashByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class CreateProgressByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    rate_name: str = None
    target_item_set_id: str = None
    materials: List[Material] = None
    force: bool = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateProgressByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateProgressByUserIdRequest:
        self.user_id = user_id
        return self

    def with_rate_name(self, rate_name: str) -> CreateProgressByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_target_item_set_id(self, target_item_set_id: str) -> CreateProgressByUserIdRequest:
        self.target_item_set_id = target_item_set_id
        return self

    def with_materials(self, materials: List[Material]) -> CreateProgressByUserIdRequest:
        self.materials = materials
        return self

    def with_force(self, force: bool) -> CreateProgressByUserIdRequest:
        self.force = force
        return self

    def with_time_offset_token(self, time_offset_token: str) -> CreateProgressByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> CreateProgressByUserIdRequest:
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
    ) -> Optional[CreateProgressByUserIdRequest]:
        if data is None:
            return None
        return CreateProgressByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_rate_name(data.get('rateName'))\
            .with_target_item_set_id(data.get('targetItemSetId'))\
            .with_materials(None if data.get('materials') is None else [
                Material.from_dict(data.get('materials')[i])
                for i in range(len(data.get('materials')))
            ])\
            .with_force(data.get('force'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rateName": self.rate_name,
            "targetItemSetId": self.target_item_set_id,
            "materials": None if self.materials is None else [
                self.materials[i].to_dict() if self.materials[i] else None
                for i in range(len(self.materials))
            ],
            "force": self.force,
            "timeOffsetToken": self.time_offset_token,
        }


class GetProgressRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetProgressRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetProgressRequest:
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
    ) -> Optional[GetProgressRequest]:
        if data is None:
            return None
        return GetProgressRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
        }


class GetProgressByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetProgressByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetProgressByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetProgressByUserIdRequest:
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
    ) -> Optional[GetProgressByUserIdRequest]:
        if data is None:
            return None
        return GetProgressByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class StartRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    target_item_set_id: str = None
    materials: List[Material] = None
    access_token: str = None
    force: bool = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> StartRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> StartRequest:
        self.rate_name = rate_name
        return self

    def with_target_item_set_id(self, target_item_set_id: str) -> StartRequest:
        self.target_item_set_id = target_item_set_id
        return self

    def with_materials(self, materials: List[Material]) -> StartRequest:
        self.materials = materials
        return self

    def with_access_token(self, access_token: str) -> StartRequest:
        self.access_token = access_token
        return self

    def with_force(self, force: bool) -> StartRequest:
        self.force = force
        return self

    def with_config(self, config: List[Config]) -> StartRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> StartRequest:
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
    ) -> Optional[StartRequest]:
        if data is None:
            return None
        return StartRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_target_item_set_id(data.get('targetItemSetId'))\
            .with_materials(None if data.get('materials') is None else [
                Material.from_dict(data.get('materials')[i])
                for i in range(len(data.get('materials')))
            ])\
            .with_access_token(data.get('accessToken'))\
            .with_force(data.get('force'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "targetItemSetId": self.target_item_set_id,
            "materials": None if self.materials is None else [
                self.materials[i].to_dict() if self.materials[i] else None
                for i in range(len(self.materials))
            ],
            "accessToken": self.access_token,
            "force": self.force,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class StartByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    rate_name: str = None
    target_item_set_id: str = None
    materials: List[Material] = None
    user_id: str = None
    force: bool = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> StartByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_rate_name(self, rate_name: str) -> StartByUserIdRequest:
        self.rate_name = rate_name
        return self

    def with_target_item_set_id(self, target_item_set_id: str) -> StartByUserIdRequest:
        self.target_item_set_id = target_item_set_id
        return self

    def with_materials(self, materials: List[Material]) -> StartByUserIdRequest:
        self.materials = materials
        return self

    def with_user_id(self, user_id: str) -> StartByUserIdRequest:
        self.user_id = user_id
        return self

    def with_force(self, force: bool) -> StartByUserIdRequest:
        self.force = force
        return self

    def with_config(self, config: List[Config]) -> StartByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> StartByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> StartByUserIdRequest:
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
    ) -> Optional[StartByUserIdRequest]:
        if data is None:
            return None
        return StartByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_rate_name(data.get('rateName'))\
            .with_target_item_set_id(data.get('targetItemSetId'))\
            .with_materials(None if data.get('materials') is None else [
                Material.from_dict(data.get('materials')[i])
                for i in range(len(data.get('materials')))
            ])\
            .with_user_id(data.get('userId'))\
            .with_force(data.get('force'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "rateName": self.rate_name,
            "targetItemSetId": self.target_item_set_id,
            "materials": None if self.materials is None else [
                self.materials[i].to_dict() if self.materials[i] else None
                for i in range(len(self.materials))
            ],
            "userId": self.user_id,
            "force": self.force,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class EndRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> EndRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> EndRequest:
        self.access_token = access_token
        return self

    def with_config(self, config: List[Config]) -> EndRequest:
        self.config = config
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> EndRequest:
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
    ) -> Optional[EndRequest]:
        if data is None:
            return None
        return EndRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class EndByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> EndByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> EndByUserIdRequest:
        self.user_id = user_id
        return self

    def with_config(self, config: List[Config]) -> EndByUserIdRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> EndByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> EndByUserIdRequest:
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
    ) -> Optional[EndByUserIdRequest]:
        if data is None:
            return None
        return EndByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteProgressRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteProgressRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteProgressRequest:
        self.access_token = access_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteProgressRequest:
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
    ) -> Optional[DeleteProgressRequest]:
        if data is None:
            return None
        return DeleteProgressRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
        }


class DeleteProgressByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteProgressByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteProgressByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteProgressByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteProgressByUserIdRequest:
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
    ) -> Optional[DeleteProgressByUserIdRequest]:
        if data is None:
            return None
        return DeleteProgressByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class CreateProgressByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> CreateProgressByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> CreateProgressByStampSheetRequest:
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
    ) -> Optional[CreateProgressByStampSheetRequest]:
        if data is None:
            return None
        return CreateProgressByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DeleteProgressByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> DeleteProgressByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> DeleteProgressByStampTaskRequest:
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
    ) -> Optional[DeleteProgressByStampTaskRequest]:
        if data is None:
            return None
        return DeleteProgressByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
            "keyId": self.key_id,
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


class GetCurrentRateMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentRateMasterRequest:
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
    ) -> Optional[GetCurrentRateMasterRequest]:
        if data is None:
            return None
        return GetCurrentRateMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentRateMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentRateMasterRequest:
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
    ) -> Optional[PreUpdateCurrentRateMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentRateMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentRateMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRateMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentRateMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentRateMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentRateMasterRequest:
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
    ) -> Optional[UpdateCurrentRateMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentRateMasterRequest()\
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


class UpdateCurrentRateMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentRateMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentRateMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentRateMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentRateMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }