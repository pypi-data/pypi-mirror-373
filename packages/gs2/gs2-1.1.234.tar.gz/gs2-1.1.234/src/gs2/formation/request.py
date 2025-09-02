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
    update_mold_script: ScriptSetting = None
    update_form_script: ScriptSetting = None
    update_property_form_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_name(self, name: str) -> CreateNamespaceRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> CreateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_update_mold_script(self, update_mold_script: ScriptSetting) -> CreateNamespaceRequest:
        self.update_mold_script = update_mold_script
        return self

    def with_update_form_script(self, update_form_script: ScriptSetting) -> CreateNamespaceRequest:
        self.update_form_script = update_form_script
        return self

    def with_update_property_form_script(self, update_property_form_script: ScriptSetting) -> CreateNamespaceRequest:
        self.update_property_form_script = update_property_form_script
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
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_update_mold_script(ScriptSetting.from_dict(data.get('updateMoldScript')))\
            .with_update_form_script(ScriptSetting.from_dict(data.get('updateFormScript')))\
            .with_update_property_form_script(ScriptSetting.from_dict(data.get('updatePropertyFormScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "updateMoldScript": self.update_mold_script.to_dict() if self.update_mold_script else None,
            "updateFormScript": self.update_form_script.to_dict() if self.update_form_script else None,
            "updatePropertyFormScript": self.update_property_form_script.to_dict() if self.update_property_form_script else None,
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
    transaction_setting: TransactionSetting = None
    update_mold_script: ScriptSetting = None
    update_form_script: ScriptSetting = None
    update_property_form_script: ScriptSetting = None
    log_setting: LogSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateNamespaceRequest:
        self.namespace_name = namespace_name
        return self

    def with_description(self, description: str) -> UpdateNamespaceRequest:
        self.description = description
        return self

    def with_transaction_setting(self, transaction_setting: TransactionSetting) -> UpdateNamespaceRequest:
        self.transaction_setting = transaction_setting
        return self

    def with_update_mold_script(self, update_mold_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.update_mold_script = update_mold_script
        return self

    def with_update_form_script(self, update_form_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.update_form_script = update_form_script
        return self

    def with_update_property_form_script(self, update_property_form_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.update_property_form_script = update_property_form_script
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
            .with_transaction_setting(TransactionSetting.from_dict(data.get('transactionSetting')))\
            .with_update_mold_script(ScriptSetting.from_dict(data.get('updateMoldScript')))\
            .with_update_form_script(ScriptSetting.from_dict(data.get('updateFormScript')))\
            .with_update_property_form_script(ScriptSetting.from_dict(data.get('updatePropertyFormScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "updateMoldScript": self.update_mold_script.to_dict() if self.update_mold_script else None,
            "updateFormScript": self.update_form_script.to_dict() if self.update_form_script else None,
            "updatePropertyFormScript": self.update_property_form_script.to_dict() if self.update_property_form_script else None,
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


class GetFormModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mold_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetFormModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetFormModelRequest:
        self.mold_model_name = mold_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormModelRequest]:
        if data is None:
            return None
        return GetFormModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mold_model_name(data.get('moldModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "moldModelName": self.mold_model_name,
        }


class DescribeFormModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeFormModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeFormModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeFormModelMastersRequest:
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
    ) -> Optional[DescribeFormModelMastersRequest]:
        if data is None:
            return None
        return DescribeFormModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateFormModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    slots: List[SlotModel] = None

    def with_namespace_name(self, namespace_name: str) -> CreateFormModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateFormModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateFormModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateFormModelMasterRequest:
        self.metadata = metadata
        return self

    def with_slots(self, slots: List[SlotModel]) -> CreateFormModelMasterRequest:
        self.slots = slots
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateFormModelMasterRequest]:
        if data is None:
            return None
        return CreateFormModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_slots(None if data.get('slots') is None else [
                SlotModel.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
        }


class GetFormModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    form_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetFormModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_form_model_name(self, form_model_name: str) -> GetFormModelMasterRequest:
        self.form_model_name = form_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormModelMasterRequest]:
        if data is None:
            return None
        return GetFormModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_form_model_name(data.get('formModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "formModelName": self.form_model_name,
        }


class UpdateFormModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    form_model_name: str = None
    description: str = None
    metadata: str = None
    slots: List[SlotModel] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateFormModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_form_model_name(self, form_model_name: str) -> UpdateFormModelMasterRequest:
        self.form_model_name = form_model_name
        return self

    def with_description(self, description: str) -> UpdateFormModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateFormModelMasterRequest:
        self.metadata = metadata
        return self

    def with_slots(self, slots: List[SlotModel]) -> UpdateFormModelMasterRequest:
        self.slots = slots
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateFormModelMasterRequest]:
        if data is None:
            return None
        return UpdateFormModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_form_model_name(data.get('formModelName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_slots(None if data.get('slots') is None else [
                SlotModel.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "formModelName": self.form_model_name,
            "description": self.description,
            "metadata": self.metadata,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
        }


class DeleteFormModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    form_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteFormModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_form_model_name(self, form_model_name: str) -> DeleteFormModelMasterRequest:
        self.form_model_name = form_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteFormModelMasterRequest]:
        if data is None:
            return None
        return DeleteFormModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_form_model_name(data.get('formModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "formModelName": self.form_model_name,
        }


class DescribeMoldModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMoldModelsRequest:
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
    ) -> Optional[DescribeMoldModelsRequest]:
        if data is None:
            return None
        return DescribeMoldModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetMoldModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mold_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMoldModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetMoldModelRequest:
        self.mold_model_name = mold_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMoldModelRequest]:
        if data is None:
            return None
        return GetMoldModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mold_model_name(data.get('moldModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "moldModelName": self.mold_model_name,
        }


class DescribeMoldModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMoldModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeMoldModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMoldModelMastersRequest:
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
    ) -> Optional[DescribeMoldModelMastersRequest]:
        if data is None:
            return None
        return DescribeMoldModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateMoldModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    form_model_name: str = None
    initial_max_capacity: int = None
    max_capacity: int = None

    def with_namespace_name(self, namespace_name: str) -> CreateMoldModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateMoldModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateMoldModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateMoldModelMasterRequest:
        self.metadata = metadata
        return self

    def with_form_model_name(self, form_model_name: str) -> CreateMoldModelMasterRequest:
        self.form_model_name = form_model_name
        return self

    def with_initial_max_capacity(self, initial_max_capacity: int) -> CreateMoldModelMasterRequest:
        self.initial_max_capacity = initial_max_capacity
        return self

    def with_max_capacity(self, max_capacity: int) -> CreateMoldModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateMoldModelMasterRequest]:
        if data is None:
            return None
        return CreateMoldModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_form_model_name(data.get('formModelName'))\
            .with_initial_max_capacity(data.get('initialMaxCapacity'))\
            .with_max_capacity(data.get('maxCapacity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "formModelName": self.form_model_name,
            "initialMaxCapacity": self.initial_max_capacity,
            "maxCapacity": self.max_capacity,
        }


class GetMoldModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mold_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMoldModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetMoldModelMasterRequest:
        self.mold_model_name = mold_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMoldModelMasterRequest]:
        if data is None:
            return None
        return GetMoldModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mold_model_name(data.get('moldModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "moldModelName": self.mold_model_name,
        }


class UpdateMoldModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mold_model_name: str = None
    description: str = None
    metadata: str = None
    form_model_name: str = None
    initial_max_capacity: int = None
    max_capacity: int = None

    def with_namespace_name(self, namespace_name: str) -> UpdateMoldModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mold_model_name(self, mold_model_name: str) -> UpdateMoldModelMasterRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_description(self, description: str) -> UpdateMoldModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateMoldModelMasterRequest:
        self.metadata = metadata
        return self

    def with_form_model_name(self, form_model_name: str) -> UpdateMoldModelMasterRequest:
        self.form_model_name = form_model_name
        return self

    def with_initial_max_capacity(self, initial_max_capacity: int) -> UpdateMoldModelMasterRequest:
        self.initial_max_capacity = initial_max_capacity
        return self

    def with_max_capacity(self, max_capacity: int) -> UpdateMoldModelMasterRequest:
        self.max_capacity = max_capacity
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateMoldModelMasterRequest]:
        if data is None:
            return None
        return UpdateMoldModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_form_model_name(data.get('formModelName'))\
            .with_initial_max_capacity(data.get('initialMaxCapacity'))\
            .with_max_capacity(data.get('maxCapacity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "moldModelName": self.mold_model_name,
            "description": self.description,
            "metadata": self.metadata,
            "formModelName": self.form_model_name,
            "initialMaxCapacity": self.initial_max_capacity,
            "maxCapacity": self.max_capacity,
        }


class DeleteMoldModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mold_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMoldModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mold_model_name(self, mold_model_name: str) -> DeleteMoldModelMasterRequest:
        self.mold_model_name = mold_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteMoldModelMasterRequest]:
        if data is None:
            return None
        return DeleteMoldModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mold_model_name(data.get('moldModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "moldModelName": self.mold_model_name,
        }


class DescribePropertyFormModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribePropertyFormModelsRequest:
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
    ) -> Optional[DescribePropertyFormModelsRequest]:
        if data is None:
            return None
        return DescribePropertyFormModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetPropertyFormModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    property_form_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPropertyFormModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> GetPropertyFormModelRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormModelRequest]:
        if data is None:
            return None
        return GetPropertyFormModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "propertyFormModelName": self.property_form_model_name,
        }


class DescribePropertyFormModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribePropertyFormModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribePropertyFormModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribePropertyFormModelMastersRequest:
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
    ) -> Optional[DescribePropertyFormModelMastersRequest]:
        if data is None:
            return None
        return DescribePropertyFormModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreatePropertyFormModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    slots: List[SlotModel] = None

    def with_namespace_name(self, namespace_name: str) -> CreatePropertyFormModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreatePropertyFormModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreatePropertyFormModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreatePropertyFormModelMasterRequest:
        self.metadata = metadata
        return self

    def with_slots(self, slots: List[SlotModel]) -> CreatePropertyFormModelMasterRequest:
        self.slots = slots
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreatePropertyFormModelMasterRequest]:
        if data is None:
            return None
        return CreatePropertyFormModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_slots(None if data.get('slots') is None else [
                SlotModel.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
        }


class GetPropertyFormModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    property_form_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPropertyFormModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> GetPropertyFormModelMasterRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormModelMasterRequest]:
        if data is None:
            return None
        return GetPropertyFormModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "propertyFormModelName": self.property_form_model_name,
        }


class UpdatePropertyFormModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    property_form_model_name: str = None
    description: str = None
    metadata: str = None
    slots: List[SlotModel] = None

    def with_namespace_name(self, namespace_name: str) -> UpdatePropertyFormModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> UpdatePropertyFormModelMasterRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_description(self, description: str) -> UpdatePropertyFormModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdatePropertyFormModelMasterRequest:
        self.metadata = metadata
        return self

    def with_slots(self, slots: List[SlotModel]) -> UpdatePropertyFormModelMasterRequest:
        self.slots = slots
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdatePropertyFormModelMasterRequest]:
        if data is None:
            return None
        return UpdatePropertyFormModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_slots(None if data.get('slots') is None else [
                SlotModel.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "propertyFormModelName": self.property_form_model_name,
            "description": self.description,
            "metadata": self.metadata,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
        }


class DeletePropertyFormModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    property_form_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeletePropertyFormModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> DeletePropertyFormModelMasterRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeletePropertyFormModelMasterRequest]:
        if data is None:
            return None
        return DeletePropertyFormModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "propertyFormModelName": self.property_form_model_name,
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


class GetCurrentFormMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentFormMasterRequest:
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
    ) -> Optional[GetCurrentFormMasterRequest]:
        if data is None:
            return None
        return GetCurrentFormMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentFormMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentFormMasterRequest:
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
    ) -> Optional[PreUpdateCurrentFormMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentFormMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentFormMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentFormMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentFormMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentFormMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentFormMasterRequest:
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
    ) -> Optional[UpdateCurrentFormMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentFormMasterRequest()\
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


class UpdateCurrentFormMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentFormMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentFormMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentFormMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentFormMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeMoldsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMoldsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeMoldsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeMoldsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMoldsRequest:
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
    ) -> Optional[DescribeMoldsRequest]:
        if data is None:
            return None
        return DescribeMoldsRequest()\
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


class DescribeMoldsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeMoldsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeMoldsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeMoldsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeMoldsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeMoldsByUserIdRequest:
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
    ) -> Optional[DescribeMoldsByUserIdRequest]:
        if data is None:
            return None
        return DescribeMoldsByUserIdRequest()\
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


class GetMoldRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mold_model_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMoldRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetMoldRequest:
        self.access_token = access_token
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetMoldRequest:
        self.mold_model_name = mold_model_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetMoldRequest]:
        if data is None:
            return None
        return GetMoldRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mold_model_name(data.get('moldModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "moldModelName": self.mold_model_name,
        }


class GetMoldByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetMoldByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetMoldByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetMoldByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetMoldByUserIdRequest:
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
    ) -> Optional[GetMoldByUserIdRequest]:
        if data is None:
            return None
        return GetMoldByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "timeOffsetToken": self.time_offset_token,
        }


class SetMoldCapacityByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    capacity: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetMoldCapacityByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SetMoldCapacityByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> SetMoldCapacityByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_capacity(self, capacity: int) -> SetMoldCapacityByUserIdRequest:
        self.capacity = capacity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetMoldCapacityByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetMoldCapacityByUserIdRequest:
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
    ) -> Optional[SetMoldCapacityByUserIdRequest]:
        if data is None:
            return None
        return SetMoldCapacityByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_capacity(data.get('capacity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "capacity": self.capacity,
            "timeOffsetToken": self.time_offset_token,
        }


class AddMoldCapacityByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    capacity: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AddMoldCapacityByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AddMoldCapacityByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> AddMoldCapacityByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_capacity(self, capacity: int) -> AddMoldCapacityByUserIdRequest:
        self.capacity = capacity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AddMoldCapacityByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AddMoldCapacityByUserIdRequest:
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
    ) -> Optional[AddMoldCapacityByUserIdRequest]:
        if data is None:
            return None
        return AddMoldCapacityByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_capacity(data.get('capacity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "capacity": self.capacity,
            "timeOffsetToken": self.time_offset_token,
        }


class SubMoldCapacityRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mold_model_name: str = None
    capacity: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SubMoldCapacityRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SubMoldCapacityRequest:
        self.access_token = access_token
        return self

    def with_mold_model_name(self, mold_model_name: str) -> SubMoldCapacityRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_capacity(self, capacity: int) -> SubMoldCapacityRequest:
        self.capacity = capacity
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SubMoldCapacityRequest:
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
    ) -> Optional[SubMoldCapacityRequest]:
        if data is None:
            return None
        return SubMoldCapacityRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_capacity(data.get('capacity'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "moldModelName": self.mold_model_name,
            "capacity": self.capacity,
        }


class SubMoldCapacityByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    capacity: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SubMoldCapacityByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SubMoldCapacityByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> SubMoldCapacityByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_capacity(self, capacity: int) -> SubMoldCapacityByUserIdRequest:
        self.capacity = capacity
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SubMoldCapacityByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SubMoldCapacityByUserIdRequest:
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
    ) -> Optional[SubMoldCapacityByUserIdRequest]:
        if data is None:
            return None
        return SubMoldCapacityByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_capacity(data.get('capacity'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "capacity": self.capacity,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteMoldRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mold_model_name: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMoldRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteMoldRequest:
        self.access_token = access_token
        return self

    def with_mold_model_name(self, mold_model_name: str) -> DeleteMoldRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteMoldRequest:
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
    ) -> Optional[DeleteMoldRequest]:
        if data is None:
            return None
        return DeleteMoldRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mold_model_name(data.get('moldModelName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "moldModelName": self.mold_model_name,
        }


class DeleteMoldByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteMoldByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteMoldByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> DeleteMoldByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteMoldByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteMoldByUserIdRequest:
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
    ) -> Optional[DeleteMoldByUserIdRequest]:
        if data is None:
            return None
        return DeleteMoldByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "timeOffsetToken": self.time_offset_token,
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


class SubCapacityByStampTaskRequest(core.Gs2Request):

    context_stack: str = None
    stamp_task: str = None
    key_id: str = None

    def with_stamp_task(self, stamp_task: str) -> SubCapacityByStampTaskRequest:
        self.stamp_task = stamp_task
        return self

    def with_key_id(self, key_id: str) -> SubCapacityByStampTaskRequest:
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
    ) -> Optional[SubCapacityByStampTaskRequest]:
        if data is None:
            return None
        return SubCapacityByStampTaskRequest()\
            .with_stamp_task(data.get('stampTask'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampTask": self.stamp_task,
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


class DescribeFormsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mold_model_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeFormsRequest:
        self.namespace_name = namespace_name
        return self

    def with_mold_model_name(self, mold_model_name: str) -> DescribeFormsRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_access_token(self, access_token: str) -> DescribeFormsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeFormsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeFormsRequest:
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
    ) -> Optional[DescribeFormsRequest]:
        if data is None:
            return None
        return DescribeFormsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_access_token(data.get('accessToken'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "moldModelName": self.mold_model_name,
            "accessToken": self.access_token,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribeFormsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mold_model_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeFormsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_mold_model_name(self, mold_model_name: str) -> DescribeFormsByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_user_id(self, user_id: str) -> DescribeFormsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeFormsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeFormsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeFormsByUserIdRequest:
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
    ) -> Optional[DescribeFormsByUserIdRequest]:
        if data is None:
            return None
        return DescribeFormsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_user_id(data.get('userId'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "moldModelName": self.mold_model_name,
            "userId": self.user_id,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetFormRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mold_model_name: str = None
    index: int = None

    def with_namespace_name(self, namespace_name: str) -> GetFormRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetFormRequest:
        self.access_token = access_token
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetFormRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> GetFormRequest:
        self.index = index
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetFormRequest]:
        if data is None:
            return None
        return GetFormRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "moldModelName": self.mold_model_name,
            "index": self.index,
        }


class GetFormByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    index: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetFormByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetFormByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetFormByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> GetFormByUserIdRequest:
        self.index = index
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetFormByUserIdRequest:
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
    ) -> Optional[GetFormByUserIdRequest]:
        if data is None:
            return None
        return GetFormByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "index": self.index,
            "timeOffsetToken": self.time_offset_token,
        }


class GetFormWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mold_model_name: str = None
    index: int = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetFormWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetFormWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetFormWithSignatureRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> GetFormWithSignatureRequest:
        self.index = index
        return self

    def with_key_id(self, key_id: str) -> GetFormWithSignatureRequest:
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
    ) -> Optional[GetFormWithSignatureRequest]:
        if data is None:
            return None
        return GetFormWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "moldModelName": self.mold_model_name,
            "index": self.index,
            "keyId": self.key_id,
        }


class GetFormWithSignatureByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    index: int = None
    key_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetFormWithSignatureByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetFormWithSignatureByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> GetFormWithSignatureByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> GetFormWithSignatureByUserIdRequest:
        self.index = index
        return self

    def with_key_id(self, key_id: str) -> GetFormWithSignatureByUserIdRequest:
        self.key_id = key_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetFormWithSignatureByUserIdRequest:
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
    ) -> Optional[GetFormWithSignatureByUserIdRequest]:
        if data is None:
            return None
        return GetFormWithSignatureByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))\
            .with_key_id(data.get('keyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "index": self.index,
            "keyId": self.key_id,
            "timeOffsetToken": self.time_offset_token,
        }


class SetFormRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mold_model_name: str = None
    index: int = None
    slots: List[Slot] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetFormRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SetFormRequest:
        self.access_token = access_token
        return self

    def with_mold_model_name(self, mold_model_name: str) -> SetFormRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> SetFormRequest:
        self.index = index
        return self

    def with_slots(self, slots: List[Slot]) -> SetFormRequest:
        self.slots = slots
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetFormRequest:
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
    ) -> Optional[SetFormRequest]:
        if data is None:
            return None
        return SetFormRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))\
            .with_slots(None if data.get('slots') is None else [
                Slot.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "moldModelName": self.mold_model_name,
            "index": self.index,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
        }


class SetFormByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    index: int = None
    slots: List[Slot] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetFormByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SetFormByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> SetFormByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> SetFormByUserIdRequest:
        self.index = index
        return self

    def with_slots(self, slots: List[Slot]) -> SetFormByUserIdRequest:
        self.slots = slots
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetFormByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetFormByUserIdRequest:
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
    ) -> Optional[SetFormByUserIdRequest]:
        if data is None:
            return None
        return SetFormByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))\
            .with_slots(None if data.get('slots') is None else [
                Slot.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "index": self.index,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class SetFormWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mold_model_name: str = None
    index: int = None
    slots: List[SlotWithSignature] = None
    key_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetFormWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SetFormWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_mold_model_name(self, mold_model_name: str) -> SetFormWithSignatureRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> SetFormWithSignatureRequest:
        self.index = index
        return self

    def with_slots(self, slots: List[SlotWithSignature]) -> SetFormWithSignatureRequest:
        self.slots = slots
        return self

    def with_key_id(self, key_id: str) -> SetFormWithSignatureRequest:
        self.key_id = key_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetFormWithSignatureRequest:
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
    ) -> Optional[SetFormWithSignatureRequest]:
        if data is None:
            return None
        return SetFormWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))\
            .with_slots(None if data.get('slots') is None else [
                SlotWithSignature.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "moldModelName": self.mold_model_name,
            "index": self.index,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
            "keyId": self.key_id,
        }


class AcquireActionsToFormPropertiesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    index: int = None
    acquire_action: AcquireAction = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireActionsToFormPropertiesRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AcquireActionsToFormPropertiesRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> AcquireActionsToFormPropertiesRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> AcquireActionsToFormPropertiesRequest:
        self.index = index
        return self

    def with_acquire_action(self, acquire_action: AcquireAction) -> AcquireActionsToFormPropertiesRequest:
        self.acquire_action = acquire_action
        return self

    def with_config(self, config: List[Config]) -> AcquireActionsToFormPropertiesRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcquireActionsToFormPropertiesRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireActionsToFormPropertiesRequest:
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
    ) -> Optional[AcquireActionsToFormPropertiesRequest]:
        if data is None:
            return None
        return AcquireActionsToFormPropertiesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))\
            .with_acquire_action(AcquireAction.from_dict(data.get('acquireAction')))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "index": self.index,
            "acquireAction": self.acquire_action.to_dict() if self.acquire_action else None,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteFormRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    mold_model_name: str = None
    index: int = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteFormRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeleteFormRequest:
        self.access_token = access_token
        return self

    def with_mold_model_name(self, mold_model_name: str) -> DeleteFormRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> DeleteFormRequest:
        self.index = index
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteFormRequest:
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
    ) -> Optional[DeleteFormRequest]:
        if data is None:
            return None
        return DeleteFormRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "moldModelName": self.mold_model_name,
            "index": self.index,
        }


class DeleteFormByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    mold_model_name: str = None
    index: int = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteFormByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeleteFormByUserIdRequest:
        self.user_id = user_id
        return self

    def with_mold_model_name(self, mold_model_name: str) -> DeleteFormByUserIdRequest:
        self.mold_model_name = mold_model_name
        return self

    def with_index(self, index: int) -> DeleteFormByUserIdRequest:
        self.index = index
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteFormByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteFormByUserIdRequest:
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
    ) -> Optional[DeleteFormByUserIdRequest]:
        if data is None:
            return None
        return DeleteFormByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_mold_model_name(data.get('moldModelName'))\
            .with_index(data.get('index'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "moldModelName": self.mold_model_name,
            "index": self.index,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireActionToFormPropertiesByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireActionToFormPropertiesByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AcquireActionToFormPropertiesByStampSheetRequest:
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
    ) -> Optional[AcquireActionToFormPropertiesByStampSheetRequest]:
        if data is None:
            return None
        return AcquireActionToFormPropertiesByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class SetFormByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> SetFormByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> SetFormByStampSheetRequest:
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
    ) -> Optional[SetFormByStampSheetRequest]:
        if data is None:
            return None
        return SetFormByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }


class DescribePropertyFormsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    property_form_model_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribePropertyFormsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribePropertyFormsRequest:
        self.access_token = access_token
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> DescribePropertyFormsRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_page_token(self, page_token: str) -> DescribePropertyFormsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribePropertyFormsRequest:
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
    ) -> Optional[DescribePropertyFormsRequest]:
        if data is None:
            return None
        return DescribePropertyFormsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "propertyFormModelName": self.property_form_model_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class DescribePropertyFormsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    property_form_model_name: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribePropertyFormsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribePropertyFormsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> DescribePropertyFormsByUserIdRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_page_token(self, page_token: str) -> DescribePropertyFormsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribePropertyFormsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribePropertyFormsByUserIdRequest:
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
    ) -> Optional[DescribePropertyFormsByUserIdRequest]:
        if data is None:
            return None
        return DescribePropertyFormsByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "propertyFormModelName": self.property_form_model_name,
            "pageToken": self.page_token,
            "limit": self.limit,
            "timeOffsetToken": self.time_offset_token,
        }


class GetPropertyFormRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    property_form_model_name: str = None
    property_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPropertyFormRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetPropertyFormRequest:
        self.access_token = access_token
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> GetPropertyFormRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> GetPropertyFormRequest:
        self.property_id = property_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetPropertyFormRequest]:
        if data is None:
            return None
        return GetPropertyFormRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
        }


class GetPropertyFormByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    property_form_model_name: str = None
    property_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPropertyFormByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetPropertyFormByUserIdRequest:
        self.user_id = user_id
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> GetPropertyFormByUserIdRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> GetPropertyFormByUserIdRequest:
        self.property_id = property_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetPropertyFormByUserIdRequest:
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
    ) -> Optional[GetPropertyFormByUserIdRequest]:
        if data is None:
            return None
        return GetPropertyFormByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
            "timeOffsetToken": self.time_offset_token,
        }


class GetPropertyFormWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    property_form_model_name: str = None
    property_id: str = None
    key_id: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPropertyFormWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> GetPropertyFormWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> GetPropertyFormWithSignatureRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> GetPropertyFormWithSignatureRequest:
        self.property_id = property_id
        return self

    def with_key_id(self, key_id: str) -> GetPropertyFormWithSignatureRequest:
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
    ) -> Optional[GetPropertyFormWithSignatureRequest]:
        if data is None:
            return None
        return GetPropertyFormWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
            "keyId": self.key_id,
        }


class GetPropertyFormWithSignatureByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    property_form_model_name: str = None
    property_id: str = None
    key_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetPropertyFormWithSignatureByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> GetPropertyFormWithSignatureByUserIdRequest:
        self.user_id = user_id
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> GetPropertyFormWithSignatureByUserIdRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> GetPropertyFormWithSignatureByUserIdRequest:
        self.property_id = property_id
        return self

    def with_key_id(self, key_id: str) -> GetPropertyFormWithSignatureByUserIdRequest:
        self.key_id = key_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetPropertyFormWithSignatureByUserIdRequest:
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
    ) -> Optional[GetPropertyFormWithSignatureByUserIdRequest]:
        if data is None:
            return None
        return GetPropertyFormWithSignatureByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))\
            .with_key_id(data.get('keyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
            "keyId": self.key_id,
            "timeOffsetToken": self.time_offset_token,
        }


class SetPropertyFormRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    property_form_model_name: str = None
    property_id: str = None
    slots: List[Slot] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetPropertyFormRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SetPropertyFormRequest:
        self.access_token = access_token
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> SetPropertyFormRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> SetPropertyFormRequest:
        self.property_id = property_id
        return self

    def with_slots(self, slots: List[Slot]) -> SetPropertyFormRequest:
        self.slots = slots
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetPropertyFormRequest:
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
    ) -> Optional[SetPropertyFormRequest]:
        if data is None:
            return None
        return SetPropertyFormRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))\
            .with_slots(None if data.get('slots') is None else [
                Slot.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
        }


class SetPropertyFormByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    property_form_model_name: str = None
    property_id: str = None
    slots: List[Slot] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetPropertyFormByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> SetPropertyFormByUserIdRequest:
        self.user_id = user_id
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> SetPropertyFormByUserIdRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> SetPropertyFormByUserIdRequest:
        self.property_id = property_id
        return self

    def with_slots(self, slots: List[Slot]) -> SetPropertyFormByUserIdRequest:
        self.slots = slots
        return self

    def with_time_offset_token(self, time_offset_token: str) -> SetPropertyFormByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetPropertyFormByUserIdRequest:
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
    ) -> Optional[SetPropertyFormByUserIdRequest]:
        if data is None:
            return None
        return SetPropertyFormByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))\
            .with_slots(None if data.get('slots') is None else [
                Slot.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class SetPropertyFormWithSignatureRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    property_form_model_name: str = None
    property_id: str = None
    slots: List[SlotWithSignature] = None
    key_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> SetPropertyFormWithSignatureRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> SetPropertyFormWithSignatureRequest:
        self.access_token = access_token
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> SetPropertyFormWithSignatureRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> SetPropertyFormWithSignatureRequest:
        self.property_id = property_id
        return self

    def with_slots(self, slots: List[SlotWithSignature]) -> SetPropertyFormWithSignatureRequest:
        self.slots = slots
        return self

    def with_key_id(self, key_id: str) -> SetPropertyFormWithSignatureRequest:
        self.key_id = key_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> SetPropertyFormWithSignatureRequest:
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
    ) -> Optional[SetPropertyFormWithSignatureRequest]:
        if data is None:
            return None
        return SetPropertyFormWithSignatureRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))\
            .with_slots(None if data.get('slots') is None else [
                SlotWithSignature.from_dict(data.get('slots')[i])
                for i in range(len(data.get('slots')))
            ])\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
            "slots": None if self.slots is None else [
                self.slots[i].to_dict() if self.slots[i] else None
                for i in range(len(self.slots))
            ],
            "keyId": self.key_id,
        }


class AcquireActionsToPropertyFormPropertiesRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    property_form_model_name: str = None
    property_id: str = None
    acquire_action: AcquireAction = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> AcquireActionsToPropertyFormPropertiesRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> AcquireActionsToPropertyFormPropertiesRequest:
        self.user_id = user_id
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> AcquireActionsToPropertyFormPropertiesRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> AcquireActionsToPropertyFormPropertiesRequest:
        self.property_id = property_id
        return self

    def with_acquire_action(self, acquire_action: AcquireAction) -> AcquireActionsToPropertyFormPropertiesRequest:
        self.acquire_action = acquire_action
        return self

    def with_config(self, config: List[Config]) -> AcquireActionsToPropertyFormPropertiesRequest:
        self.config = config
        return self

    def with_time_offset_token(self, time_offset_token: str) -> AcquireActionsToPropertyFormPropertiesRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> AcquireActionsToPropertyFormPropertiesRequest:
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
    ) -> Optional[AcquireActionsToPropertyFormPropertiesRequest]:
        if data is None:
            return None
        return AcquireActionsToPropertyFormPropertiesRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))\
            .with_acquire_action(AcquireAction.from_dict(data.get('acquireAction')))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
            "acquireAction": self.acquire_action.to_dict() if self.acquire_action else None,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
            "timeOffsetToken": self.time_offset_token,
        }


class DeletePropertyFormRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    property_form_model_name: str = None
    property_id: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeletePropertyFormRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DeletePropertyFormRequest:
        self.access_token = access_token
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> DeletePropertyFormRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> DeletePropertyFormRequest:
        self.property_id = property_id
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeletePropertyFormRequest:
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
    ) -> Optional[DeletePropertyFormRequest]:
        if data is None:
            return None
        return DeletePropertyFormRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_access_token(data.get('accessToken'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
        }


class DeletePropertyFormByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    property_form_model_name: str = None
    property_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeletePropertyFormByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DeletePropertyFormByUserIdRequest:
        self.user_id = user_id
        return self

    def with_property_form_model_name(self, property_form_model_name: str) -> DeletePropertyFormByUserIdRequest:
        self.property_form_model_name = property_form_model_name
        return self

    def with_property_id(self, property_id: str) -> DeletePropertyFormByUserIdRequest:
        self.property_id = property_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeletePropertyFormByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeletePropertyFormByUserIdRequest:
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
    ) -> Optional[DeletePropertyFormByUserIdRequest]:
        if data is None:
            return None
        return DeletePropertyFormByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_user_id(data.get('userId'))\
            .with_property_form_model_name(data.get('propertyFormModelName'))\
            .with_property_id(data.get('propertyId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "propertyFormModelName": self.property_form_model_name,
            "propertyId": self.property_id,
            "timeOffsetToken": self.time_offset_token,
        }


class AcquireActionToPropertyFormPropertiesByStampSheetRequest(core.Gs2Request):

    context_stack: str = None
    stamp_sheet: str = None
    key_id: str = None

    def with_stamp_sheet(self, stamp_sheet: str) -> AcquireActionToPropertyFormPropertiesByStampSheetRequest:
        self.stamp_sheet = stamp_sheet
        return self

    def with_key_id(self, key_id: str) -> AcquireActionToPropertyFormPropertiesByStampSheetRequest:
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
    ) -> Optional[AcquireActionToPropertyFormPropertiesByStampSheetRequest]:
        if data is None:
            return None
        return AcquireActionToPropertyFormPropertiesByStampSheetRequest()\
            .with_stamp_sheet(data.get('stampSheet'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheet": self.stamp_sheet,
            "keyId": self.key_id,
        }