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


class DistributeResource(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> DistributeResource:
        self.action = action
        return self

    def with_request(self, request: str) -> DistributeResource:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DistributeResource]:
        if data is None:
            return None
        return DistributeResource()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class GitHubCheckoutSetting(core.Gs2Model):
    api_key_id: str = None
    repository_name: str = None
    source_path: str = None
    reference_type: str = None
    commit_hash: str = None
    branch_name: str = None
    tag_name: str = None

    def with_api_key_id(self, api_key_id: str) -> GitHubCheckoutSetting:
        self.api_key_id = api_key_id
        return self

    def with_repository_name(self, repository_name: str) -> GitHubCheckoutSetting:
        self.repository_name = repository_name
        return self

    def with_source_path(self, source_path: str) -> GitHubCheckoutSetting:
        self.source_path = source_path
        return self

    def with_reference_type(self, reference_type: str) -> GitHubCheckoutSetting:
        self.reference_type = reference_type
        return self

    def with_commit_hash(self, commit_hash: str) -> GitHubCheckoutSetting:
        self.commit_hash = commit_hash
        return self

    def with_branch_name(self, branch_name: str) -> GitHubCheckoutSetting:
        self.branch_name = branch_name
        return self

    def with_tag_name(self, tag_name: str) -> GitHubCheckoutSetting:
        self.tag_name = tag_name
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[GitHubCheckoutSetting]:
        if data is None:
            return None
        return GitHubCheckoutSetting()\
            .with_api_key_id(data.get('apiKeyId'))\
            .with_repository_name(data.get('repositoryName'))\
            .with_source_path(data.get('sourcePath'))\
            .with_reference_type(data.get('referenceType'))\
            .with_commit_hash(data.get('commitHash'))\
            .with_branch_name(data.get('branchName'))\
            .with_tag_name(data.get('tagName'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "apiKeyId": self.api_key_id,
            "repositoryName": self.repository_name,
            "sourcePath": self.source_path,
            "referenceType": self.reference_type,
            "commitHash": self.commit_hash,
            "branchName": self.branch_name,
            "tagName": self.tag_name,
        }


class Config(core.Gs2Model):
    key: str = None
    value: str = None

    def with_key(self, key: str) -> Config:
        self.key = key
        return self

    def with_value(self, value: str) -> Config:
        self.value = value
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[Config]:
        if data is None:
            return None
        return Config()\
            .with_key(data.get('key'))\
            .with_value(data.get('value'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
        }


class VerifyActionResult(core.Gs2Model):
    action: str = None
    verify_request: str = None
    status_code: int = None
    verify_result: str = None

    def with_action(self, action: str) -> VerifyActionResult:
        self.action = action
        return self

    def with_verify_request(self, verify_request: str) -> VerifyActionResult:
        self.verify_request = verify_request
        return self

    def with_status_code(self, status_code: int) -> VerifyActionResult:
        self.status_code = status_code
        return self

    def with_verify_result(self, verify_result: str) -> VerifyActionResult:
        self.verify_result = verify_result
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyActionResult]:
        if data is None:
            return None
        return VerifyActionResult()\
            .with_action(data.get('action'))\
            .with_verify_request(data.get('verifyRequest'))\
            .with_status_code(data.get('statusCode'))\
            .with_verify_result(data.get('verifyResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "verifyRequest": self.verify_request,
            "statusCode": self.status_code,
            "verifyResult": self.verify_result,
        }


class ConsumeActionResult(core.Gs2Model):
    action: str = None
    consume_request: str = None
    status_code: int = None
    consume_result: str = None

    def with_action(self, action: str) -> ConsumeActionResult:
        self.action = action
        return self

    def with_consume_request(self, consume_request: str) -> ConsumeActionResult:
        self.consume_request = consume_request
        return self

    def with_status_code(self, status_code: int) -> ConsumeActionResult:
        self.status_code = status_code
        return self

    def with_consume_result(self, consume_result: str) -> ConsumeActionResult:
        self.consume_result = consume_result
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeActionResult]:
        if data is None:
            return None
        return ConsumeActionResult()\
            .with_action(data.get('action'))\
            .with_consume_request(data.get('consumeRequest'))\
            .with_status_code(data.get('statusCode'))\
            .with_consume_result(data.get('consumeResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "consumeRequest": self.consume_request,
            "statusCode": self.status_code,
            "consumeResult": self.consume_result,
        }


class AcquireActionResult(core.Gs2Model):
    action: str = None
    acquire_request: str = None
    status_code: int = None
    acquire_result: str = None

    def with_action(self, action: str) -> AcquireActionResult:
        self.action = action
        return self

    def with_acquire_request(self, acquire_request: str) -> AcquireActionResult:
        self.acquire_request = acquire_request
        return self

    def with_status_code(self, status_code: int) -> AcquireActionResult:
        self.status_code = status_code
        return self

    def with_acquire_result(self, acquire_result: str) -> AcquireActionResult:
        self.acquire_result = acquire_result
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcquireActionResult]:
        if data is None:
            return None
        return AcquireActionResult()\
            .with_action(data.get('action'))\
            .with_acquire_request(data.get('acquireRequest'))\
            .with_status_code(data.get('statusCode'))\
            .with_acquire_result(data.get('acquireResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "acquireRequest": self.acquire_request,
            "statusCode": self.status_code,
            "acquireResult": self.acquire_result,
        }


class TransactionResult(core.Gs2Model):
    transaction_result_id: str = None
    user_id: str = None
    transaction_id: str = None
    verify_results: List[VerifyActionResult] = None
    consume_results: List[ConsumeActionResult] = None
    acquire_results: List[AcquireActionResult] = None
    has_error: bool = None
    created_at: int = None
    revision: int = None

    def with_transaction_result_id(self, transaction_result_id: str) -> TransactionResult:
        self.transaction_result_id = transaction_result_id
        return self

    def with_user_id(self, user_id: str) -> TransactionResult:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> TransactionResult:
        self.transaction_id = transaction_id
        return self

    def with_verify_results(self, verify_results: List[VerifyActionResult]) -> TransactionResult:
        self.verify_results = verify_results
        return self

    def with_consume_results(self, consume_results: List[ConsumeActionResult]) -> TransactionResult:
        self.consume_results = consume_results
        return self

    def with_acquire_results(self, acquire_results: List[AcquireActionResult]) -> TransactionResult:
        self.acquire_results = acquire_results
        return self

    def with_has_error(self, has_error: bool) -> TransactionResult:
        self.has_error = has_error
        return self

    def with_created_at(self, created_at: int) -> TransactionResult:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> TransactionResult:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        transaction_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}:user:{userId}:transaction:result:{transactionId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            transactionId=transaction_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):transaction:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):transaction:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):transaction:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):transaction:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_transaction_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):transaction:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('transaction_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[TransactionResult]:
        if data is None:
            return None
        return TransactionResult()\
            .with_transaction_result_id(data.get('transactionResultId'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_verify_results(None if data.get('verifyResults') is None else [
                VerifyActionResult.from_dict(data.get('verifyResults')[i])
                for i in range(len(data.get('verifyResults')))
            ])\
            .with_consume_results(None if data.get('consumeResults') is None else [
                ConsumeActionResult.from_dict(data.get('consumeResults')[i])
                for i in range(len(data.get('consumeResults')))
            ])\
            .with_acquire_results(None if data.get('acquireResults') is None else [
                AcquireActionResult.from_dict(data.get('acquireResults')[i])
                for i in range(len(data.get('acquireResults')))
            ])\
            .with_has_error(data.get('hasError'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionResultId": self.transaction_result_id,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
            "verifyResults": None if self.verify_results is None else [
                self.verify_results[i].to_dict() if self.verify_results[i] else None
                for i in range(len(self.verify_results))
            ],
            "consumeResults": None if self.consume_results is None else [
                self.consume_results[i].to_dict() if self.consume_results[i] else None
                for i in range(len(self.consume_results))
            ],
            "acquireResults": None if self.acquire_results is None else [
                self.acquire_results[i].to_dict() if self.acquire_results[i] else None
                for i in range(len(self.acquire_results))
            ],
            "hasError": self.has_error,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class VerifyAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> VerifyAction:
        self.action = action
        return self

    def with_request(self, request: str) -> VerifyAction:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[VerifyAction]:
        if data is None:
            return None
        return VerifyAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class ConsumeAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> ConsumeAction:
        self.action = action
        return self

    def with_request(self, request: str) -> ConsumeAction:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[ConsumeAction]:
        if data is None:
            return None
        return ConsumeAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class AcquireAction(core.Gs2Model):
    action: str = None
    request: str = None

    def with_action(self, action: str) -> AcquireAction:
        self.action = action
        return self

    def with_request(self, request: str) -> AcquireAction:
        self.request = request
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[AcquireAction]:
        if data is None:
            return None
        return AcquireAction()\
            .with_action(data.get('action'))\
            .with_request(data.get('request'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "request": self.request,
        }


class BatchResultPayload(core.Gs2Model):
    request_id: str = None
    status_code: int = None
    result_payload: str = None

    def with_request_id(self, request_id: str) -> BatchResultPayload:
        self.request_id = request_id
        return self

    def with_status_code(self, status_code: int) -> BatchResultPayload:
        self.status_code = status_code
        return self

    def with_result_payload(self, result_payload: str) -> BatchResultPayload:
        self.result_payload = result_payload
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BatchResultPayload]:
        if data is None:
            return None
        return BatchResultPayload()\
            .with_request_id(data.get('requestId'))\
            .with_status_code(data.get('statusCode'))\
            .with_result_payload(data.get('resultPayload'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requestId": self.request_id,
            "statusCode": self.status_code,
            "resultPayload": self.result_payload,
        }


class BatchRequestPayload(core.Gs2Model):
    request_id: str = None
    service: str = None
    method_name: str = None
    parameter: str = None

    def with_request_id(self, request_id: str) -> BatchRequestPayload:
        self.request_id = request_id
        return self

    def with_service(self, service: str) -> BatchRequestPayload:
        self.service = service
        return self

    def with_method_name(self, method_name: str) -> BatchRequestPayload:
        self.method_name = method_name
        return self

    def with_parameter(self, parameter: str) -> BatchRequestPayload:
        self.parameter = parameter
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[BatchRequestPayload]:
        if data is None:
            return None
        return BatchRequestPayload()\
            .with_request_id(data.get('requestId'))\
            .with_service(data.get('service'))\
            .with_method_name(data.get('methodName'))\
            .with_parameter(data.get('parameter'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requestId": self.request_id,
            "service": self.service,
            "methodName": self.method_name,
            "parameter": self.parameter,
        }


class StampSheetResult(core.Gs2Model):
    stamp_sheet_result_id: str = None
    user_id: str = None
    transaction_id: str = None
    verify_task_requests: List[VerifyAction] = None
    task_requests: List[ConsumeAction] = None
    sheet_request: AcquireAction = None
    verify_task_result_codes: List[int] = None
    verify_task_results: List[str] = None
    task_result_codes: List[int] = None
    task_results: List[str] = None
    sheet_result_code: int = None
    sheet_result: str = None
    next_transaction_id: str = None
    created_at: int = None
    revision: int = None

    def with_stamp_sheet_result_id(self, stamp_sheet_result_id: str) -> StampSheetResult:
        self.stamp_sheet_result_id = stamp_sheet_result_id
        return self

    def with_user_id(self, user_id: str) -> StampSheetResult:
        self.user_id = user_id
        return self

    def with_transaction_id(self, transaction_id: str) -> StampSheetResult:
        self.transaction_id = transaction_id
        return self

    def with_verify_task_requests(self, verify_task_requests: List[VerifyAction]) -> StampSheetResult:
        self.verify_task_requests = verify_task_requests
        return self

    def with_task_requests(self, task_requests: List[ConsumeAction]) -> StampSheetResult:
        self.task_requests = task_requests
        return self

    def with_sheet_request(self, sheet_request: AcquireAction) -> StampSheetResult:
        self.sheet_request = sheet_request
        return self

    def with_verify_task_result_codes(self, verify_task_result_codes: List[int]) -> StampSheetResult:
        self.verify_task_result_codes = verify_task_result_codes
        return self

    def with_verify_task_results(self, verify_task_results: List[str]) -> StampSheetResult:
        self.verify_task_results = verify_task_results
        return self

    def with_task_result_codes(self, task_result_codes: List[int]) -> StampSheetResult:
        self.task_result_codes = task_result_codes
        return self

    def with_task_results(self, task_results: List[str]) -> StampSheetResult:
        self.task_results = task_results
        return self

    def with_sheet_result_code(self, sheet_result_code: int) -> StampSheetResult:
        self.sheet_result_code = sheet_result_code
        return self

    def with_sheet_result(self, sheet_result: str) -> StampSheetResult:
        self.sheet_result = sheet_result
        return self

    def with_next_transaction_id(self, next_transaction_id: str) -> StampSheetResult:
        self.next_transaction_id = next_transaction_id
        return self

    def with_created_at(self, created_at: int) -> StampSheetResult:
        self.created_at = created_at
        return self

    def with_revision(self, revision: int) -> StampSheetResult:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        user_id,
        transaction_id,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}:user:{userId}:stampSheet:result:{transactionId}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            userId=user_id,
            transactionId=transaction_id,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_user_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('user_id')

    @classmethod
    def get_transaction_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):user:(?P<userId>.+):stampSheet:result:(?P<transactionId>.+)', grn)
        if match is None:
            return None
        return match.group('transaction_id')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[StampSheetResult]:
        if data is None:
            return None
        return StampSheetResult()\
            .with_stamp_sheet_result_id(data.get('stampSheetResultId'))\
            .with_user_id(data.get('userId'))\
            .with_transaction_id(data.get('transactionId'))\
            .with_verify_task_requests(None if data.get('verifyTaskRequests') is None else [
                VerifyAction.from_dict(data.get('verifyTaskRequests')[i])
                for i in range(len(data.get('verifyTaskRequests')))
            ])\
            .with_task_requests(None if data.get('taskRequests') is None else [
                ConsumeAction.from_dict(data.get('taskRequests')[i])
                for i in range(len(data.get('taskRequests')))
            ])\
            .with_sheet_request(AcquireAction.from_dict(data.get('sheetRequest')))\
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
            .with_sheet_result(data.get('sheetResult'))\
            .with_next_transaction_id(data.get('nextTransactionId'))\
            .with_created_at(data.get('createdAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stampSheetResultId": self.stamp_sheet_result_id,
            "userId": self.user_id,
            "transactionId": self.transaction_id,
            "verifyTaskRequests": None if self.verify_task_requests is None else [
                self.verify_task_requests[i].to_dict() if self.verify_task_requests[i] else None
                for i in range(len(self.verify_task_requests))
            ],
            "taskRequests": None if self.task_requests is None else [
                self.task_requests[i].to_dict() if self.task_requests[i] else None
                for i in range(len(self.task_requests))
            ],
            "sheetRequest": self.sheet_request.to_dict() if self.sheet_request else None,
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
            "nextTransactionId": self.next_transaction_id,
            "createdAt": self.created_at,
            "revision": self.revision,
        }


class CurrentDistributorMaster(core.Gs2Model):
    namespace_id: str = None
    settings: str = None

    def with_namespace_id(self, namespace_id: str) -> CurrentDistributorMaster:
        self.namespace_id = namespace_id
        return self

    def with_settings(self, settings: str) -> CurrentDistributorMaster:
        self.settings = settings
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
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
    ) -> Optional[CurrentDistributorMaster]:
        if data is None:
            return None
        return CurrentDistributorMaster()\
            .with_namespace_id(data.get('namespaceId'))\
            .with_settings(data.get('settings'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "settings": self.settings,
        }


class DistributorModel(core.Gs2Model):
    distributor_model_id: str = None
    name: str = None
    metadata: str = None
    inbox_namespace_id: str = None
    white_list_target_ids: List[str] = None

    def with_distributor_model_id(self, distributor_model_id: str) -> DistributorModel:
        self.distributor_model_id = distributor_model_id
        return self

    def with_name(self, name: str) -> DistributorModel:
        self.name = name
        return self

    def with_metadata(self, metadata: str) -> DistributorModel:
        self.metadata = metadata
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> DistributorModel:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_white_list_target_ids(self, white_list_target_ids: List[str]) -> DistributorModel:
        self.white_list_target_ids = white_list_target_ids
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        distributor_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}:model:{distributorName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            distributorName=distributor_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_distributor_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('distributor_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DistributorModel]:
        if data is None:
            return None
        return DistributorModel()\
            .with_distributor_model_id(data.get('distributorModelId'))\
            .with_name(data.get('name'))\
            .with_metadata(data.get('metadata'))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_white_list_target_ids(None if data.get('whiteListTargetIds') is None else [
                data.get('whiteListTargetIds')[i]
                for i in range(len(data.get('whiteListTargetIds')))
            ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distributorModelId": self.distributor_model_id,
            "name": self.name,
            "metadata": self.metadata,
            "inboxNamespaceId": self.inbox_namespace_id,
            "whiteListTargetIds": None if self.white_list_target_ids is None else [
                self.white_list_target_ids[i]
                for i in range(len(self.white_list_target_ids))
            ],
        }


class DistributorModelMaster(core.Gs2Model):
    distributor_model_id: str = None
    name: str = None
    description: str = None
    metadata: str = None
    inbox_namespace_id: str = None
    white_list_target_ids: List[str] = None
    created_at: int = None
    updated_at: int = None
    revision: int = None

    def with_distributor_model_id(self, distributor_model_id: str) -> DistributorModelMaster:
        self.distributor_model_id = distributor_model_id
        return self

    def with_name(self, name: str) -> DistributorModelMaster:
        self.name = name
        return self

    def with_description(self, description: str) -> DistributorModelMaster:
        self.description = description
        return self

    def with_metadata(self, metadata: str) -> DistributorModelMaster:
        self.metadata = metadata
        return self

    def with_inbox_namespace_id(self, inbox_namespace_id: str) -> DistributorModelMaster:
        self.inbox_namespace_id = inbox_namespace_id
        return self

    def with_white_list_target_ids(self, white_list_target_ids: List[str]) -> DistributorModelMaster:
        self.white_list_target_ids = white_list_target_ids
        return self

    def with_created_at(self, created_at: int) -> DistributorModelMaster:
        self.created_at = created_at
        return self

    def with_updated_at(self, updated_at: int) -> DistributorModelMaster:
        self.updated_at = updated_at
        return self

    def with_revision(self, revision: int) -> DistributorModelMaster:
        self.revision = revision
        return self

    @classmethod
    def create_grn(
        cls,
        region,
        owner_id,
        namespace_name,
        distributor_name,
    ):
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}:model:{distributorName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
            distributorName=distributor_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('namespace_name')

    @classmethod
    def get_distributor_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+):model:(?P<distributorName>.+)', grn)
        if match is None:
            return None
        return match.group('distributor_name')

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
    ) -> Optional[DistributorModelMaster]:
        if data is None:
            return None
        return DistributorModelMaster()\
            .with_distributor_model_id(data.get('distributorModelId'))\
            .with_name(data.get('name'))\
            .with_description(data.get('description'))\
            .with_metadata(data.get('metadata'))\
            .with_inbox_namespace_id(data.get('inboxNamespaceId'))\
            .with_white_list_target_ids(None if data.get('whiteListTargetIds') is None else [
                data.get('whiteListTargetIds')[i]
                for i in range(len(data.get('whiteListTargetIds')))
            ])\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "distributorModelId": self.distributor_model_id,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata,
            "inboxNamespaceId": self.inbox_namespace_id,
            "whiteListTargetIds": None if self.white_list_target_ids is None else [
                self.white_list_target_ids[i]
                for i in range(len(self.white_list_target_ids))
            ],
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }


class Namespace(core.Gs2Model):
    namespace_id: str = None
    name: str = None
    description: str = None
    assume_user_id: str = None
    auto_run_stamp_sheet_notification: NotificationSetting = None
    auto_run_transaction_notification: NotificationSetting = None
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

    def with_assume_user_id(self, assume_user_id: str) -> Namespace:
        self.assume_user_id = assume_user_id
        return self

    def with_auto_run_stamp_sheet_notification(self, auto_run_stamp_sheet_notification: NotificationSetting) -> Namespace:
        self.auto_run_stamp_sheet_notification = auto_run_stamp_sheet_notification
        return self

    def with_auto_run_transaction_notification(self, auto_run_transaction_notification: NotificationSetting) -> Namespace:
        self.auto_run_transaction_notification = auto_run_transaction_notification
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
        return 'grn:gs2:{region}:{ownerId}:distributor:{namespaceName}'.format(
            region=region,
            ownerId=owner_id,
            namespaceName=namespace_name,
        )

    @classmethod
    def get_region_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('region')

    @classmethod
    def get_owner_id_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
        if match is None:
            return None
        return match.group('owner_id')

    @classmethod
    def get_namespace_name_from_grn(
        cls,
        grn: str,
    ) -> Optional[str]:
        match = re.search('grn:gs2:(?P<region>.+):(?P<ownerId>.+):distributor:(?P<namespaceName>.+)', grn)
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
            .with_assume_user_id(data.get('assumeUserId'))\
            .with_auto_run_stamp_sheet_notification(NotificationSetting.from_dict(data.get('autoRunStampSheetNotification')))\
            .with_auto_run_transaction_notification(NotificationSetting.from_dict(data.get('autoRunTransactionNotification')))\
            .with_log_setting(LogSetting.from_dict(data.get('logSetting')))\
            .with_created_at(data.get('createdAt'))\
            .with_updated_at(data.get('updatedAt'))\
            .with_revision(data.get('revision'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "namespaceId": self.namespace_id,
            "name": self.name,
            "description": self.description,
            "assumeUserId": self.assume_user_id,
            "autoRunStampSheetNotification": self.auto_run_stamp_sheet_notification.to_dict() if self.auto_run_stamp_sheet_notification else None,
            "autoRunTransactionNotification": self.auto_run_transaction_notification.to_dict() if self.auto_run_transaction_notification else None,
            "logSetting": self.log_setting.to_dict() if self.log_setting else None,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "revision": self.revision,
        }