# encoding: utf-8
#
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
from abc import abstractmethod
from typing import Optional, Dict, Any, Generic, TypeVar, Callable, List


class Gs2Constant(object):

    ENDPOINT_HOST = "https://{service}.{region}.gen2.gs2io.com"
    WS_ENDPOINT_HOST = "wss://gateway-ws.{region}.gen2.gs2io.com"


class IGs2Credential:

    @property
    @abstractmethod
    def client_id(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def client_secret(self) -> str:
        raise NotImplementedError()


class BasicGs2Credential(IGs2Credential):

    def __init__(
            self,
            client_id: str,
            client_secret: str,
    ):
        """
        コンストラクタ
        :param client_id: クライアントID
        :param client_secret: クライアントシークレット
        """
        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret


class ProjectTokenGs2Credential(IGs2Credential):

    def __init__(
            self,
            owner_id: str,
            project_token: str,
    ):
        """
        コンストラクタ
        :param owner_id: オーナーID
        :param project_token: プロジェクトトークン
        """
        self._client_id = owner_id
        self._project_token = project_token

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return None

    @property
    def project_token(self) -> str:
        return self._project_token


class Gs2Request:

    request_id: str = None
    context_stack: str = None

    def with_request_id(
            self,
            request_id: str,
    ) -> Gs2Request:
        self.request_id = request_id
        return self

    def with_context_stack(
            self,
            context_stack: str,
    ) -> Gs2Request:
        self.context_stack = context_stack
        return self

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError()


class Gs2Result:

    @abstractmethod
    def to_dict(self):
        raise NotImplementedError()


class Gs2Model:
    pass


class LoginResult(Gs2Result):
    """
    プロジェクトトークン を取得します のレスポンスモデル
    """
    access_token: str = None
    token_type: str = None
    expires_in: int = None

    def with_access_token(self, access_token: str):
        self.access_token = access_token
        return self

    def with_token_type(self, token_type: str):
        self.token_type = token_type
        return self

    def with_expires_in(self, expires_in: int):
        self.expires_in = expires_in
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return super.__getattribute__(key)

    @staticmethod
    def from_dict(
            data: Dict[str, Any],
    ) -> Optional[LoginResult]:
        if data is None:
            return None
        return LoginResult() \
            .with_access_token(data.get('access_token')) \
            .with_token_type(data.get('token_type')) \
            .with_expires_in(data.get('expires_in'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "access_token": self.access_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
        }


class ISession:

    @property
    @abstractmethod
    def credential(self) -> IGs2Credential:
        raise NotImplementedError()

    @property
    @abstractmethod
    def region(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def project_token(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def _connect(
            self,
            callback: Callable[[AsyncResult[LoginResult]], None],
    ):
        raise NotImplementedError()

    @abstractmethod
    def connect(self):
        raise NotImplementedError()

    @abstractmethod
    async def connect_async(self):
        raise NotImplementedError()

    @abstractmethod
    def disconnect(self):
        raise NotImplementedError()


class Region:

    AP_NORTHEAST_1 = 'ap-northeast-1'
    US_EAST_1 = 'us-east-1'
    EU_WEST_1 = 'eu-west-1'
    AP_SOUTHEAST_1 = 'ap-southeast-1'

    VALUES = [
        AP_NORTHEAST_1,
        US_EAST_1,
        EU_WEST_1,
        AP_SOUTHEAST_1,
    ]


class RequestError:

    def __init__(
            self,
            component: str,
            message: str,
            code: str = None,
    ):
        self._component = component
        self._message = message
        self._code = code

    @property
    def component(self) -> str:
        return self._component

    @property
    def message(self) -> str:
        return self._message

    @property
    def code(self) -> str:
        return self._code

    def __getitem__(self, key):
        if key == 'component':
            return self.component
        if key == 'message':
            return self.message
        if key == 'code':
            return self.code
        return super(object, self).__getitem__(key)

    def get(self, key, default=None):
        if key == 'component':
            return self.component
        if key == 'message':
            return self.message
        if key == 'code':
            return self.code
        try:
            return super(object, self).__getitem__(key)
        except ValueError:
            return default


T = TypeVar('T')


class AsyncResult(Generic[T]):

    def __init__(
        self,
        result: Optional[T] = None,
        error: Optional[Exception] = None,
    ):
        self._result = result
        self._error = error

    @property
    def result(self) -> Optional[T]:
        return self._result

    @property
    def error(self) -> Optional[Exception]:
        return self._error


class VerifyActionResult(Gs2Model):
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
        return VerifyActionResult() \
            .with_action(data.get('action')) \
            .with_verify_request(data.get('verifyRequest')) \
            .with_status_code(data.get('statusCode')) \
            .with_verify_result(data.get('verifyResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "verifyRequest": self.verify_request,
            "statusCode": self.status_code,
            "verifyResult": self.verify_result,
        }


class ConsumeActionResult(Gs2Model):
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
        return ConsumeActionResult() \
            .with_action(data.get('action')) \
            .with_consume_request(data.get('consumeRequest')) \
            .with_status_code(data.get('statusCode')) \
            .with_consume_result(data.get('consumeResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "consumeRequest": self.consume_request,
            "statusCode": self.status_code,
            "consumeResult": self.consume_result,
        }


class AcquireActionResult(Gs2Model):
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
        return AcquireActionResult() \
            .with_action(data.get('action')) \
            .with_acquire_request(data.get('acquireRequest')) \
            .with_status_code(data.get('statusCode')) \
            .with_acquire_result(data.get('acquireResult'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "acquireRequest": self.acquire_request,
            "statusCode": self.status_code,
            "acquireResult": self.acquire_result,
        }


class TransactionResult(Gs2Model):
    transaction_id: str = None
    verify_results: List[VerifyActionResult] = None
    consume_results: List[ConsumeActionResult] = None
    acquire_results: List[AcquireActionResult] = None

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

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
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
        return TransactionResult() \
            .with_transaction_id(data.get('transactionId')) \
            .with_verify_results([
            VerifyActionResult.from_dict(data.get('verifyResults')[i])
            for i in range(len(data.get('verifyResults')) if data.get('verifyResults') else 0)
        ]) \
            .with_consume_results([
            ConsumeActionResult.from_dict(data.get('consumeResults')[i])
            for i in range(len(data.get('consumeResults')) if data.get('consumeResults') else 0)
        ]) \
            .with_acquire_results([
            AcquireActionResult.from_dict(data.get('acquireResults')[i])
            for i in range(len(data.get('acquireResults')) if data.get('acquireResults') else 0)
        ])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactionId": self.transaction_id,
            "verifyResults": None if self.verify_results is None else [
                self.verify_results[i].to_dict() if self.verify_results[i] else None
                for i in range(len(self.verify_results) if self.verify_results else 0)
            ],
            "consumeResults": None if self.consume_results is None else [
                self.consume_results[i].to_dict() if self.consume_results[i] else None
                for i in range(len(self.consume_results) if self.consume_results else 0)
            ],
            "acquireResults": None if self.acquire_results is None else [
                self.acquire_results[i].to_dict() if self.acquire_results[i] else None
                for i in range(len(self.acquire_results) if self.acquire_results else 0)
            ],
        }


class ResultMetadata(Gs2Model):
    uncommitted: str = None

    def with_uncommitted(self, uncommitted: str) -> ResultMetadata:
        self.uncommitted = uncommitted
        return self

    def get(self, key, default=None):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return default

    def __getitem__(self, key):
        items = self.to_dict()
        if key in items.keys():
            return items[key]
        return None

    @staticmethod
    def from_dict(
            data: Dict[str, Any],
    ) -> Optional[ResultMetadata]:
        if data is None:
            return None
        return ResultMetadata() \
            .with_uncommitted(data.get('uncommitted'))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uncommitted": self.uncommitted,
        }

