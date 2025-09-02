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

import re
from typing import *
from gs2 import core


class JobResultBody(core.Gs2Model):
    try_number: int = None
    status_code: int = None
    result: str = None
    try_at: int = None

    def with_try_number(self, try_number: int) -> JobResultBody:
        self.try_number = try_number
        return self

    def with_status_code(self, status_code: int) -> JobResultBody:
        self.status_code = status_code
        return self

    def with_result(self, result: str) -> JobResultBody:
        self.result = result
        return self

    def with_try_at(self, try_at: int) -> JobResultBody:
        self.try_at = try_at
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[JobResultBody]:
        if data is None:
            return None
        return JobResultBody()\
            .with_try_number(data.get('tryNumber'))\
            .with_status_code(data.get('statusCode'))\
            .with_result(data.get('result'))\
            .with_try_at(data.get('tryAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tryNumber": self.try_number,
            "statusCode": self.status_code,
            "result": self.result,
            "tryAt": self.try_at,
        }


class JobEntry(core.Gs2Model):
    script_id: str = None
    args: str = None
    max_try_count: int = None

    def with_script_id(self, script_id: str) -> JobEntry:
        self.script_id = script_id
        return self

    def with_args(self, args: str) -> JobEntry:
        self.args = args
        return self

    def with_max_try_count(self, max_try_count: int) -> JobEntry:
        self.max_try_count = max_try_count
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[JobEntry]:
        if data is None:
            return None
        return JobEntry()\
            .with_script_id(data.get('scriptId'))\
            .with_args(data.get('args'))\
            .with_max_try_count(data.get('maxTryCount'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scriptId": self.script_id,
            "args": self.args,
            "maxTryCount": self.max_try_count,
        }


class LogSetting(core.Gs2Model):
    logging_namespace_id: str = None

    def with_logging_namespace_id(self, logging_namespace_id: str) -> LogSetting:
        self.logging_namespace_id = logging_namespace_id
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[LogSetting]:
        if data is None:
            return None
        return LogSetting()\
            .with_logging_namespace_id(data.get('loggingNamespaceId'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "loggingNamespaceId": self.logging_namespace_id,
        }


class NotificationSetting(core.Gs2Model):
    gateway_namespace_id: str = None
    enable_transfer_mobile_notification: bool = None
    sound: str = None

    def with_gateway_namespace_id(self, gateway_namespace_id: str) -> NotificationSetting:
        self.gateway_namespace_id = gateway_namespace_id
        return self

    def with_enable_transfer_mobile_notification(self, enable_transfer_mobile_notification: bool) -> NotificationSetting:
        self.enable_transfer_mobile_notification = enable_transfer_mobile_notification
        return self

    def with_sound(self, sound: str) -> NotificationSetting:
        self.sound = sound
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[NotificationSetting]:
        if data is None:
            return None
        return NotificationSetting()\
            .with_gateway_namespace_id(data.get('gatewayNamespaceId'))\
            .with_enable_transfer_mobile_notification(data.get('enableTransferMobileNotification'))\
            .with_sound(data.get('sound'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gatewayNamespaceId": self.gateway_namespace_id,
            "enableTransferMobileNotification": self.enable_transfer_mobile_notification,
            "sound": self.sound,
        }


class JobResult(core.Gs2Model):
    job_result_id: str = None
    job_id: str = None
    script_id: str = None
    args: str = None
    try_number: int = None
    status_code: int = None
    result: str = None
    try_at: int = None

    def with_job_result_id(self, job_result_id: str) -> JobResult:
        self.job_result_id = job_result_id
        return self

    def with_job_id(self, job_id: str) -> JobResult:
        self.job_id = job_id
        return self

    def with_script_id(self, script_id: str) -> JobResult:
        self.script_id = script_id
        return self

    def with_args(self, args: str) -> JobResult:
        self.args = args
        return self

    def with_try_number(self, try_number: int) -> JobResult:
        self.try_number = try_number
        return self

    def with_status_code(self, status_code: int) -> JobResult:
        self.status_code = status_code
        return self

    def with_result(self, result: str) -> JobResult:
        self.result = result
        return self

    def with_try_at(self, try_at: int) -> JobResult:
        self.try_at = try_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        job_name,
        try_number,
    ):
        return 'grn:gs2:{region}:{ownerId}:queue:{namespaceName}:user:{userId}:job:{jobName}:jobResult:{tryNumber}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            jobName=job_name,
            tryNumber=try_number,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+):jobResult:(?P<tryNumber>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+):jobResult:(?P<tryNumber>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+):jobResult:(?P<tryNumber>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+):jobResult:(?P<tryNumber>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_job_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+):jobResult:(?P<tryNumber>.+)', grn)
        if match is None:
            return None
        return match.group('job_name')

    @classmethod
    def get_try_number_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+):jobResult:(?P<tryNumber>.+)', grn)
        if match is None:
            return None
        return match.group('try_number')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[JobResult]:
        if data is None:
            return None
        return JobResult()\
            .with_job_result_id(data.get('jobResultId'))\
            .with_job_id(data.get('jobId'))\
            .with_script_id(data.get('scriptId'))\
            .with_args(data.get('args'))\
            .with_try_number(data.get('tryNumber'))\
            .with_status_code(data.get('statusCode'))\
            .with_result(data.get('result'))\
            .with_try_at(data.get('tryAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jobResultId": self.job_result_id,
            "jobId": self.job_id,
            "scriptId": self.script_id,
            "args": self.args,
            "tryNumber": self.try_number,
            "statusCode": self.status_code,
            "result": self.result,
            "tryAt": self.try_at,
        }


class Job(core.Gs2Model):
    job_id: str = None
    name: str = None
    user_id: str = None
    script_id: str = None
    args: str = None
    current_retry_count: int = None
    max_try_count: int = None
    created_at: int = None
    updated_at: int = None

    def with_job_id(self, job_id: str) -> Job:
        self.job_id = job_id
        return self

    def with_name(self, name: str) -> Job:
        self.name = name
        return self

    def with_user_id(self, user_id: str) -> Job:
        self.user_id = user_id
        return self

    def with_script_id(self, script_id: str) -> Job:
        self.script_id = script_id
        return self

    def with_args(self, args: str) -> Job:
        self.args = args
        return self

    def with_current_retry_count(self, current_retry_count: int) -> Job:
        self.current_retry_count = current_retry_count
        return self

    def with_max_try_count(self, max_try_count: int) -> Job:
        self.max_try_count = max_try_count
        return self

    def with_created_at(self, created_at: int) -> Job:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Job:
        self.updated_at = updated_at
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        job_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:queue:{namespaceName}:user:{userId}:job:{jobName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            jobName=job_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_job_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+):user:(?P<userId>.+):job:(?P<jobName>.+)', grn)
        if match is None:
            return None
        return match.group('job_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Job]:
        if data is None:
            return None
        return Job()\
            .with_job_id(data.get('jobId'))\
            .with_name(data.get('name'))\
            .with_user_id(data.get('userId'))\
            .with_script_id(data.get('scriptId'))\
            .with_args(data.get('args'))\
            .with_current_retry_count(data.get('currentRetryCount'))\
            .with_max_try_count(data.get('maxTryCount'))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jobId": self.job_id,
            "name": self.name,
            "userId": self.user_id,
            "scriptId": self.script_id,
            "args": self.args,
            "currentRetryCount": self.current_retry_count,
            "maxTryCount": self.max_try_count,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    enable_auto_run: bool = None
    run_notification: NotificationSetting = None
    push_notification: NotificationSetting = None
    log_setting: LogSetting = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_namespace_id(self, namespace_id: str) -> Namespace:
        self.namespace_id = namespace_id
        return self

    def with_name(self, name: str) -> Namespace:
        self.name = name
        return self

    def with_description(self, description: str) -> Namespace:
        self.description = description
        return self

    def with_enable_auto_run(self, enable_auto_run: bool) -> Namespace:
        self.enable_auto_run = enable_auto_run
        return self

    def with_run_notification(self, run_notification: NotificationSetting) -> Namespace:
        self.run_notification = run_notification
        return self

    def with_push_notification(self, push_notification: NotificationSetting) -> Namespace:
        self.push_notification = push_notification
        return self

    def with_log_setting(self, log_setting: LogSetting) -> Namespace:
        self.log_setting = log_setting
        return self

    def with_created_at(self, created_at: int) -> Namespace:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> Namespace:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> Namespace:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:queue:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):queue:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Namespace]:
        if data is None:
            return None
        return Namespace()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_enable_auto_run(data.get('enableAutoRun'))\
            .with_run_notification(NotificationSetting.from_dict(data.get('runNotification')))\
            .with_push_notification(NotificationSetting.from_dict(data.get('pushNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "enableAutoRun": self.enable_auto_run,
            "runNotification": self.run_notification.to_dict() if self.run_notification else None,
            "pushNotification": self.push_notification.to_dict() if self.push_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }