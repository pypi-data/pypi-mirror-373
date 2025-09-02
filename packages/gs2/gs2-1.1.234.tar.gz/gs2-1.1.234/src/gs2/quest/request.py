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
    start_quest_script: ScriptSetting = None
    complete_quest_script: ScriptSetting = None
    failed_quest_script: ScriptSetting = None
    log_setting: LogSetting = None
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

    def with_start_quest_script(self, start_quest_script: ScriptSetting) -> CreateNamespaceRequest:
        self.start_quest_script = start_quest_script
        return self

    def with_complete_quest_script(self, complete_quest_script: ScriptSetting) -> CreateNamespaceRequest:
        self.complete_quest_script = complete_quest_script
        return self

    def with_failed_quest_script(self, failed_quest_script: ScriptSetting) -> CreateNamespaceRequest:
        self.failed_quest_script = failed_quest_script
        return self

    def with_log_setting(self, log_setting: LogSetting) -> CreateNamespaceRequest:
        self.log_setting = log_setting
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
            .with_start_quest_script(ScriptSetting.from_dict(data.get('startQuestScript')))\
            .with_complete_quest_script(ScriptSetting.from_dict(data.get('completeQuestScript')))\
            .with_failed_quest_script(ScriptSetting.from_dict(data.get('failedQuestScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "startQuestScript": self.start_quest_script.to_dict() if self.start_quest_script else None,
            "completeQuestScript": self.complete_quest_script.to_dict() if self.complete_quest_script else None,
            "failedQuestScript": self.failed_quest_script.to_dict() if self.failed_quest_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
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
    start_quest_script: ScriptSetting = None
    complete_quest_script: ScriptSetting = None
    failed_quest_script: ScriptSetting = None
    log_setting: LogSetting = None
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

    def with_start_quest_script(self, start_quest_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.start_quest_script = start_quest_script
        return self

    def with_complete_quest_script(self, complete_quest_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.complete_quest_script = complete_quest_script
        return self

    def with_failed_quest_script(self, failed_quest_script: ScriptSetting) -> UpdateNamespaceRequest:
        self.failed_quest_script = failed_quest_script
        return self

    def with_log_setting(self, log_setting: LogSetting) -> UpdateNamespaceRequest:
        self.log_setting = log_setting
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
            .with_start_quest_script(ScriptSetting.from_dict(data.get('startQuestScript')))\
            .with_complete_quest_script(ScriptSetting.from_dict(data.get('completeQuestScript')))\
            .with_failed_quest_script(ScriptSetting.from_dict(data.get('failedQuestScript')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_queue_namespace_id(data.get('queueNamespaceId'))\
            .with_key_id(data.get('keyId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "description": self.description,
            "transactionSetting": self.transaction_setting.to_dict() if self.transaction_setting else None,
            "startQuestScript": self.start_quest_script.to_dict() if self.start_quest_script else None,
            "completeQuestScript": self.complete_quest_script.to_dict() if self.complete_quest_script else None,
            "failedQuestScript": self.failed_quest_script.to_dict() if self.failed_quest_script else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
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


class DescribeQuestGroupModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeQuestGroupModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_page_token(self, page_token: str) -> DescribeQuestGroupModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeQuestGroupModelMastersRequest:
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
    ) -> Optional[DescribeQuestGroupModelMastersRequest]:
        if data is None:
            return None
        return DescribeQuestGroupModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateQuestGroupModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    challenge_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateQuestGroupModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_name(self, name: str) -> CreateQuestGroupModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateQuestGroupModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateQuestGroupModelMasterRequest:
        self.metadata = metadata
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> CreateQuestGroupModelMasterRequest:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateQuestGroupModelMasterRequest]:
        if data is None:
            return None
        return CreateQuestGroupModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class GetQuestGroupModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetQuestGroupModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> GetQuestGroupModelMasterRequest:
        self.quest_group_name = quest_group_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetQuestGroupModelMasterRequest]:
        if data is None:
            return None
        return GetQuestGroupModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
        }


class UpdateQuestGroupModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    description: str = None
    metadata: str = None
    challenge_period_event_id: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateQuestGroupModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> UpdateQuestGroupModelMasterRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_description(self, description: str) -> UpdateQuestGroupModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateQuestGroupModelMasterRequest:
        self.metadata = metadata
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> UpdateQuestGroupModelMasterRequest:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateQuestGroupModelMasterRequest]:
        if data is None:
            return None
        return UpdateQuestGroupModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "description": self.description,
            "metadata": self.metadata,
            "challengePeriodEventId": self.challenge_period_event_id,
        }


class DeleteQuestGroupModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteQuestGroupModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> DeleteQuestGroupModelMasterRequest:
        self.quest_group_name = quest_group_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteQuestGroupModelMasterRequest]:
        if data is None:
            return None
        return DeleteQuestGroupModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
        }


class DescribeQuestModelMastersRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeQuestModelMastersRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> DescribeQuestModelMastersRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_page_token(self, page_token: str) -> DescribeQuestModelMastersRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeQuestModelMastersRequest:
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
    ) -> Optional[DescribeQuestModelMastersRequest]:
        if data is None:
            return None
        return DescribeQuestModelMastersRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_page_token(data.get('pageToken'))\
            .with_limit(data.get('limit'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "pageToken": self.page_token,
            "limit": self.limit,
        }


class CreateQuestModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    name: str = None
    description: str = None
    metadata: str = None
    contents: List[Contents] = None
    challenge_period_event_id: str = None
    first_complete_acquire_actions: List[AcquireAction] = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    failed_acquire_actions: List[AcquireAction] = None
    premise_quest_names: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> CreateQuestModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> CreateQuestModelMasterRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_name(self, name: str) -> CreateQuestModelMasterRequest:
        self.name = name
        return self

    def with_description(self, description: str) -> CreateQuestModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> CreateQuestModelMasterRequest:
        self.metadata = metadata
        return self

    def with_contents(self, contents: List[Contents]) -> CreateQuestModelMasterRequest:
        self.contents = contents
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> CreateQuestModelMasterRequest:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_first_complete_acquire_actions(self, first_complete_acquire_actions: List[AcquireAction]) -> CreateQuestModelMasterRequest:
        self.first_complete_acquire_actions = first_complete_acquire_actions
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> CreateQuestModelMasterRequest:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> CreateQuestModelMasterRequest:
        self.consume_actions = consume_actions
        return self

    def with_failed_acquire_actions(self, failed_acquire_actions: List[AcquireAction]) -> CreateQuestModelMasterRequest:
        self.failed_acquire_actions = failed_acquire_actions
        return self

    def with_premise_quest_names(self, premise_quest_names: List[str]) -> CreateQuestModelMasterRequest:
        self.premise_quest_names = premise_quest_names
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[CreateQuestModelMasterRequest]:
        if data is None:
            return None
        return CreateQuestModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_contents(None if data.get('contents') is None else [
                Contents.from_dict(data.get('contents')[i])
                for i in range(len(data.get('contents')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_first_complete_acquire_actions(None if data.get('firstCompleteAcquireActions') is None else [
                AcquireAction.from_dict(data.get('firstCompleteAcquireActions')[i])
                for i in range(len(data.get('firstCompleteAcquireActions')))
            ])\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_failed_acquire_actions(None if data.get('failedAcquireActions') is None else [
                AcquireAction.from_dict(data.get('failedAcquireActions')[i])
                for i in range(len(data.get('failedAcquireActions')))
            ])\
            .with_premise_quest_names(None if data.get('premiseQuestNames') is None else [
                data.get('premiseQuestNames')[i]
                for i in range(len(data.get('premiseQuestNames')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "contents": None if self.contents is None else [
                self.contents[i].to_dict() if self.contents[i] else None
                for i in range(len(self.contents))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "firstCompleteAcquireActions": None if self.first_complete_acquire_actions is None else [
                self.first_complete_acquire_actions[i].to_dict() if self.first_complete_acquire_actions[i] else None
                for i in range(len(self.first_complete_acquire_actions))
            ],
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "failedAcquireActions": None if self.failed_acquire_actions is None else [
                self.failed_acquire_actions[i].to_dict() if self.failed_acquire_actions[i] else None
                for i in range(len(self.failed_acquire_actions))
            ],
            "premiseQuestNames": None if self.premise_quest_names is None else [
                self.premise_quest_names[i]
                for i in range(len(self.premise_quest_names))
            ],
        }


class GetQuestModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    quest_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetQuestModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> GetQuestModelMasterRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_quest_name(self, quest_name: str) -> GetQuestModelMasterRequest:
        self.quest_name = quest_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetQuestModelMasterRequest]:
        if data is None:
            return None
        return GetQuestModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_quest_name(data.get('questName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "questName": self.quest_name,
        }


class UpdateQuestModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    quest_name: str = None
    description: str = None
    metadata: str = None
    contents: List[Contents] = None
    challenge_period_event_id: str = None
    first_complete_acquire_actions: List[AcquireAction] = None
    verify_actions: List[VerifyAction] = None
    consume_actions: List[ConsumeAction] = None
    failed_acquire_actions: List[AcquireAction] = None
    premise_quest_names: List[str] = None

    def with_namespace_name(self, namespace_name: str) -> UpdateQuestModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> UpdateQuestModelMasterRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_quest_name(self, quest_name: str) -> UpdateQuestModelMasterRequest:
        self.quest_name = quest_name
        return self

    def with_description(self, description: str) -> UpdateQuestModelMasterRequest:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> UpdateQuestModelMasterRequest:
        self.metadata = metadata
        return self

    def with_contents(self, contents: List[Contents]) -> UpdateQuestModelMasterRequest:
        self.contents = contents
        return self

    def with_challenge_period_event_id(self, challenge_period_event_id: str) -> UpdateQuestModelMasterRequest:
        self.challenge_period_event_id = challenge_period_event_id
        return self

    def with_first_complete_acquire_actions(self, first_complete_acquire_actions: List[AcquireAction]) -> UpdateQuestModelMasterRequest:
        self.first_complete_acquire_actions = first_complete_acquire_actions
        return self

    def with_verify_actions(self, verify_actions: List[VerifyAction]) -> UpdateQuestModelMasterRequest:
        self.verify_actions = verify_actions
        return self

    def with_consume_actions(self, consume_actions: List[ConsumeAction]) -> UpdateQuestModelMasterRequest:
        self.consume_actions = consume_actions
        return self

    def with_failed_acquire_actions(self, failed_acquire_actions: List[AcquireAction]) -> UpdateQuestModelMasterRequest:
        self.failed_acquire_actions = failed_acquire_actions
        return self

    def with_premise_quest_names(self, premise_quest_names: List[str]) -> UpdateQuestModelMasterRequest:
        self.premise_quest_names = premise_quest_names
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[UpdateQuestModelMasterRequest]:
        if data is None:
            return None
        return UpdateQuestModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_quest_name(data.get('questName'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_contents(None if data.get('contents') is None else [
                Contents.from_dict(data.get('contents')[i])
                for i in range(len(data.get('contents')))
            ])\
            .with_challenge_period_event_id(data.get('challengePeriodEventId'))\
            .with_first_complete_acquire_actions(None if data.get('firstCompleteAcquireActions') is None else [
                AcquireAction.from_dict(data.get('firstCompleteAcquireActions')[i])
                for i in range(len(data.get('firstCompleteAcquireActions')))
            ])\
            .with_verify_actions(None if data.get('verifyActions') is None else [
                VerifyAction.from_dict(data.get('verifyActions')[i])
                for i in range(len(data.get('verifyActions')))
            ])\
            .with_consume_actions(None if data.get('consumeActions') is None else [
                ConsumeAction.from_dict(data.get('consumeActions')[i])
                for i in range(len(data.get('consumeActions')))
            ])\
            .with_failed_acquire_actions(None if data.get('failedAcquireActions') is None else [
                AcquireAction.from_dict(data.get('failedAcquireActions')[i])
                for i in range(len(data.get('failedAcquireActions')))
            ])\
            .with_premise_quest_names(None if data.get('premiseQuestNames') is None else [
                data.get('premiseQuestNames')[i]
                for i in range(len(data.get('premiseQuestNames')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "questName": self.quest_name,
            "description": self.description,
            "metadata": self.metadata,
            "contents": None if self.contents is None else [
                self.contents[i].to_dict() if self.contents[i] else None
                for i in range(len(self.contents))
            ],
            "challengePeriodEventId": self.challenge_period_event_id,
            "firstCompleteAcquireActions": None if self.first_complete_acquire_actions is None else [
                self.first_complete_acquire_actions[i].to_dict() if self.first_complete_acquire_actions[i] else None
                for i in range(len(self.first_complete_acquire_actions))
            ],
            "verifyActions": None if self.verify_actions is None else [
                self.verify_actions[i].to_dict() if self.verify_actions[i] else None
                for i in range(len(self.verify_actions))
            ],
            "consumeActions": None if self.consume_actions is None else [
                self.consume_actions[i].to_dict() if self.consume_actions[i] else None
                for i in range(len(self.consume_actions))
            ],
            "failedAcquireActions": None if self.failed_acquire_actions is None else [
                self.failed_acquire_actions[i].to_dict() if self.failed_acquire_actions[i] else None
                for i in range(len(self.failed_acquire_actions))
            ],
            "premiseQuestNames": None if self.premise_quest_names is None else [
                self.premise_quest_names[i]
                for i in range(len(self.premise_quest_names))
            ],
        }


class DeleteQuestModelMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    quest_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteQuestModelMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> DeleteQuestModelMasterRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_quest_name(self, quest_name: str) -> DeleteQuestModelMasterRequest:
        self.quest_name = quest_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DeleteQuestModelMasterRequest]:
        if data is None:
            return None
        return DeleteQuestModelMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_quest_name(data.get('questName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "questName": self.quest_name,
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


class GetCurrentQuestMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCurrentQuestMasterRequest:
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
    ) -> Optional[GetCurrentQuestMasterRequest]:
        if data is None:
            return None
        return GetCurrentQuestMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class PreUpdateCurrentQuestMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> PreUpdateCurrentQuestMasterRequest:
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
    ) -> Optional[PreUpdateCurrentQuestMasterRequest]:
        if data is None:
            return None
        return PreUpdateCurrentQuestMasterRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class UpdateCurrentQuestMasterRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    mode: str = None
    settings: str = None
    upload_token: str = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentQuestMasterRequest:
        self.namespace_name = namespace_name
        return self

    def with_mode(self, mode: str) -> UpdateCurrentQuestMasterRequest:
        self.mode = mode
        return self

    def with_settings(self, settings: str) -> UpdateCurrentQuestMasterRequest:
        self.settings = settings
        return self

    def with_upload_token(self, upload_token: str) -> UpdateCurrentQuestMasterRequest:
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
    ) -> Optional[UpdateCurrentQuestMasterRequest]:
        if data is None:
            return None
        return UpdateCurrentQuestMasterRequest()\
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


class UpdateCurrentQuestMasterFromGitHubRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    checkout_setting: GitHubCheckoutSetting = None

    def with_namespace_name(self, namespace_name: str) -> UpdateCurrentQuestMasterFromGitHubRequest:
        self.namespace_name = namespace_name
        return self

    def with_checkout_setting(self, checkout_setting: GitHubCheckoutSetting) -> UpdateCurrentQuestMasterFromGitHubRequest:
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
    ) -> Optional[UpdateCurrentQuestMasterFromGitHubRequest]:
        if data is None:
            return None
        return UpdateCurrentQuestMasterFromGitHubRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_checkout_setting(GitHubCheckoutSetting.from_dict(data.get('checkoutSetting')))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "checkoutSetting": self.checkout_setting.to_dict() if self.checkout_setting else None,
        }


class DescribeProgressesByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeProgressesByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeProgressesByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeProgressesByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeProgressesByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeProgressesByUserIdRequest:
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
    ) -> Optional[DescribeProgressesByUserIdRequest]:
        if data is None:
            return None
        return DescribeProgressesByUserIdRequest()\
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


class CreateProgressByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    quest_model_id: str = None
    force: bool = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> CreateProgressByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> CreateProgressByUserIdRequest:
        self.user_id = user_id
        return self

    def with_quest_model_id(self, quest_model_id: str) -> CreateProgressByUserIdRequest:
        self.quest_model_id = quest_model_id
        return self

    def with_force(self, force: bool) -> CreateProgressByUserIdRequest:
        self.force = force
        return self

    def with_config(self, config: List[Config]) -> CreateProgressByUserIdRequest:
        self.config = config
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
            .with_quest_model_id(data.get('questModelId'))\
            .with_force(data.get('force'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "questModelId": self.quest_model_id,
            "force": self.force,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
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
    quest_group_name: str = None
    quest_name: str = None
    access_token: str = None
    force: bool = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> StartRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> StartRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_quest_name(self, quest_name: str) -> StartRequest:
        self.quest_name = quest_name
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
            .with_quest_group_name(data.get('questGroupName'))\
            .with_quest_name(data.get('questName'))\
            .with_access_token(data.get('accessToken'))\
            .with_force(data.get('force'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "questName": self.quest_name,
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
    quest_group_name: str = None
    quest_name: str = None
    user_id: str = None
    force: bool = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> StartByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> StartByUserIdRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_quest_name(self, quest_name: str) -> StartByUserIdRequest:
        self.quest_name = quest_name
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
            .with_quest_group_name(data.get('questGroupName'))\
            .with_quest_name(data.get('questName'))\
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
            "questGroupName": self.quest_group_name,
            "questName": self.quest_name,
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
    rewards: List[Reward] = None
    is_complete: bool = None
    config: List[Config] = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> EndRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> EndRequest:
        self.access_token = access_token
        return self

    def with_rewards(self, rewards: List[Reward]) -> EndRequest:
        self.rewards = rewards
        return self

    def with_is_complete(self, is_complete: bool) -> EndRequest:
        self.is_complete = is_complete
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
            .with_rewards(None if data.get('rewards') is None else [
                Reward.from_dict(data.get('rewards')[i])
                for i in range(len(data.get('rewards')))
            ])\
            .with_is_complete(data.get('isComplete'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "accessToken": self.access_token,
            "rewards": None if self.rewards is None else [
                self.rewards[i].to_dict() if self.rewards[i] else None
                for i in range(len(self.rewards))
            ],
            "isComplete": self.is_complete,
            "config": None if self.config is None else [
                self.config[i].to_dict() if self.config[i] else None
                for i in range(len(self.config))
            ],
        }


class EndByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    rewards: List[Reward] = None
    is_complete: bool = None
    config: List[Config] = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> EndByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> EndByUserIdRequest:
        self.user_id = user_id
        return self

    def with_rewards(self, rewards: List[Reward]) -> EndByUserIdRequest:
        self.rewards = rewards
        return self

    def with_is_complete(self, is_complete: bool) -> EndByUserIdRequest:
        self.is_complete = is_complete
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
            .with_rewards(None if data.get('rewards') is None else [
                Reward.from_dict(data.get('rewards')[i])
                for i in range(len(data.get('rewards')))
            ])\
            .with_is_complete(data.get('isComplete'))\
            .with_config(None if data.get('config') is None else [
                Config.from_dict(data.get('config')[i])
                for i in range(len(data.get('config')))
            ])\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "userId": self.user_id,
            "rewards": None if self.rewards is None else [
                self.rewards[i].to_dict() if self.rewards[i] else None
                for i in range(len(self.rewards))
            ],
            "isComplete": self.is_complete,
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


class DescribeCompletedQuestListsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    access_token: str = None
    page_token: str = None
    limit: int = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCompletedQuestListsRequest:
        self.namespace_name = namespace_name
        return self

    def with_access_token(self, access_token: str) -> DescribeCompletedQuestListsRequest:
        self.access_token = access_token
        return self

    def with_page_token(self, page_token: str) -> DescribeCompletedQuestListsRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCompletedQuestListsRequest:
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
    ) -> Optional[DescribeCompletedQuestListsRequest]:
        if data is None:
            return None
        return DescribeCompletedQuestListsRequest()\
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


class DescribeCompletedQuestListsByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    user_id: str = None
    page_token: str = None
    limit: int = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeCompletedQuestListsByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_user_id(self, user_id: str) -> DescribeCompletedQuestListsByUserIdRequest:
        self.user_id = user_id
        return self

    def with_page_token(self, page_token: str) -> DescribeCompletedQuestListsByUserIdRequest:
        self.page_token = page_token
        return self

    def with_limit(self, limit: int) -> DescribeCompletedQuestListsByUserIdRequest:
        self.limit = limit
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DescribeCompletedQuestListsByUserIdRequest:
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
    ) -> Optional[DescribeCompletedQuestListsByUserIdRequest]:
        if data is None:
            return None
        return DescribeCompletedQuestListsByUserIdRequest()\
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


class GetCompletedQuestListRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    access_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCompletedQuestListRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> GetCompletedQuestListRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_access_token(self, access_token: str) -> GetCompletedQuestListRequest:
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
    ) -> Optional[GetCompletedQuestListRequest]:
        if data is None:
            return None
        return GetCompletedQuestListRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_access_token(data.get('accessToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "accessToken": self.access_token,
        }


class GetCompletedQuestListByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    user_id: str = None
    time_offset_token: str = None

    def with_namespace_name(self, namespace_name: str) -> GetCompletedQuestListByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> GetCompletedQuestListByUserIdRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_user_id(self, user_id: str) -> GetCompletedQuestListByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> GetCompletedQuestListByUserIdRequest:
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
    ) -> Optional[GetCompletedQuestListByUserIdRequest]:
        if data is None:
            return None
        return GetCompletedQuestListByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DeleteCompletedQuestListByUserIdRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    user_id: str = None
    time_offset_token: str = None
    duplication_avoider: str = None

    def with_namespace_name(self, namespace_name: str) -> DeleteCompletedQuestListByUserIdRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> DeleteCompletedQuestListByUserIdRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_user_id(self, user_id: str) -> DeleteCompletedQuestListByUserIdRequest:
        self.user_id = user_id
        return self

    def with_time_offset_token(self, time_offset_token: str) -> DeleteCompletedQuestListByUserIdRequest:
        self.time_offset_token = time_offset_token
        return self

    def with_duplication_avoider(self, duplication_avoider: str) -> DeleteCompletedQuestListByUserIdRequest:
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
    ) -> Optional[DeleteCompletedQuestListByUserIdRequest]:
        if data is None:
            return None
        return DeleteCompletedQuestListByUserIdRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_user_id(data.get('userId'))\
            .with_time_offset_token(data.get('timeOffsetToken'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "userId": self.user_id,
            "timeOffsetToken": self.time_offset_token,
        }


class DescribeQuestGroupModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeQuestGroupModelsRequest:
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
    ) -> Optional[DescribeQuestGroupModelsRequest]:
        if data is None:
            return None
        return DescribeQuestGroupModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
        }


class GetQuestGroupModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetQuestGroupModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> GetQuestGroupModelRequest:
        self.quest_group_name = quest_group_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetQuestGroupModelRequest]:
        if data is None:
            return None
        return GetQuestGroupModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
        }


class DescribeQuestModelsRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None

    def with_namespace_name(self, namespace_name: str) -> DescribeQuestModelsRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> DescribeQuestModelsRequest:
        self.quest_group_name = quest_group_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DescribeQuestModelsRequest]:
        if data is None:
            return None
        return DescribeQuestModelsRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
        }


class GetQuestModelRequest(core.Gs2Request):

    context_stack: str = None
    namespace_name: str = None
    quest_group_name: str = None
    quest_name: str = None

    def with_namespace_name(self, namespace_name: str) -> GetQuestModelRequest:
        self.namespace_name = namespace_name
        return self

    def with_quest_group_name(self, quest_group_name: str) -> GetQuestModelRequest:
        self.quest_group_name = quest_group_name
        return self

    def with_quest_name(self, quest_name: str) -> GetQuestModelRequest:
        self.quest_name = quest_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GetQuestModelRequest]:
        if data is None:
            return None
        return GetQuestModelRequest()\
            .with_namespace_name(data.get('namespaceName'))\
            .with_quest_group_name(data.get('questGroupName'))\
            .with_quest_name(data.get('questName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceName": self.namespace_name,
            "questGroupName": self.quest_group_name,
            "questName": self.quest_name,
        }