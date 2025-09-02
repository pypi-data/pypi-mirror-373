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
import time
from collections import deque
from typing import Dict, Any, Callable, TypeVar, Type, Deque, Generic
from netrc import netrc, NetrcParseError  # メインスレッド以外でimportするとデッドロックするらしい https://github.com/kennethreitz/requests/issues/2925

import requests

from ..core.exception import *
from ..core.model import *
from ..core.util import timeout

T = TypeVar('T')


def _parse_response(response: requests.Response) -> Dict[str, Any]:
    if response.status_code == 200:
        try:
            import json
            return json.loads(response.text)
        except ValueError:
            from ..core.exception import UnknownException
            raise UnknownException(response.text)
    elif response.status_code == 400:
        from ..core.exception import BadRequestException
        raise BadRequestException(response.text)
    elif response.status_code == 401:
        from ..core.exception import UnauthorizedException
        raise UnauthorizedException(response.text)
    elif response.status_code == 402:
        from ..core.exception import QuotaExceedException
        raise QuotaExceedException(response.text)
    elif response.status_code == 404:
        from ..core.exception import NotFoundException
        raise NotFoundException(response.text)
    elif response.status_code == 409:
        from ..core.exception import ConflictException
        raise ConflictException(response.text)
    elif response.status_code == 500:
        from ..core.exception import InternalServerErrorException
        raise InternalServerErrorException(response.text)
    elif response.status_code == 502:
        from ..core.exception import BadGatewayException
        raise BadGatewayException(response.text)
    elif response.status_code == 503:
        from ..core.exception import ServiceUnavailableException
        raise ServiceUnavailableException('')
    elif response.status_code == 504:
        from ..core.exception import RequestTimeoutException
        raise RequestTimeoutException(response.text)
    else:
        from ..core.exception import UnknownException
        raise UnknownException(response.text)


class NetworkJob:

    def __init__(
            self,
            url: str,
            method: str,
            result_type: Type[T],
            callback: Callable[[AsyncResult[T]], None],
            headers: Dict[str, Any] = None,
            query_strings: Dict[str, Any] = None,
            body: Dict[str, Any] = None,
    ):
        if headers is None:
            headers = {}
        if query_strings is None:
            query_strings = {}
        if body is None:
            body = {}

        self._url = url
        self._method = method
        self._result_type = result_type
        self._callback = callback
        self._headers = headers
        self._query_strings = query_strings
        self._body = body

    @property
    def url(self) -> str:
        return self._url

    @property
    def method(self) -> str:
        return self._method

    @property
    def result_type(self) -> Type[T]:
        return self._result_type

    @property
    def callback(self) -> Callable[[T], None]:
        return self._callback

    @property
    def headers(self) -> Dict[str, Any]:
        return self._headers

    @property
    def query_strings(self) -> Dict[str, Any]:
        return self._query_strings

    @property
    def body(self) -> Dict[str, Any]:
        return self._body


class Gs2RestSession(ISession):

    def __init__(
            self,
            credential: IGs2Credential,
            region: str,
    ):
        """
        コンストラクタ
        :param credential: クレデンシャル
        :param region: クレデンシャル
        """
        super().__init__()
        self._credential = credential
        self._project_token = None
        self._region = region
        self._connection = None
        self._connection_thread = None
        self._job_queue = deque()

    @property
    def credential(self) -> IGs2Credential:
        return self._credential

    @property
    def project_token(self) -> str:
        return self._project_token

    @property
    def region(self) -> str:
        return self._region

    @property
    def connection(self) -> requests.Session:
        return self._connection

    def _send(self, job: NetworkJob):
        if not self._connection:
            raise BrokenPipeError()

        if job.method == 'GET':
            response = self.connection.get(
                url=job.url,
                headers=job.headers,
                params=job.query_strings,
            )
        elif job.method == 'POST':
            response = self.connection.post(
                url=job.url,
                headers=job.headers,
                json=job.body,
            )
        elif job.method == 'PUT':
            response = self.connection.put(
                url=job.url,
                headers=job.headers,
                json=job.body,
            )
        elif job.method == 'DELETE':
            response = self.connection.delete(
                url=job.url,
                headers=job.headers,
                params=job.query_strings,
            )
        else:
            raise AttributeError()

        try:
            job.callback(
                AsyncResult(
                    result=job.result_type.from_dict(_parse_response(response)),
                )
            )
        except Gs2Exception as e:
            job.callback(
                AsyncResult(
                    error=e,
                )
            )

    def send(
            self,
            job: NetworkJob,
            is_blocking: bool = False
    ):
        if not self._connection:
            raise BrokenPipeError()
        if is_blocking:
            self._send(job)
            pass
        else:
            self._job_queue.append(job)

    def _connect(
            self,
            callback: Callable[[AsyncResult[LoginResult]], None],
            is_blocking: bool = False,
    ):
        try:
            if not self._connection:
                import threading
                self._connection = requests.Session()
                self._connection_thread = threading.Thread(target=receive_handler, args=(self, self._job_queue))
                self._connection_thread.start()

                if isinstance(self.credential, ProjectTokenGs2Credential):
                    self._project_token = self.credential.project_token
                    callback(
                        AsyncResult(
                        )
                    )
                else:
                    url = Gs2Constant.ENDPOINT_HOST.format(
                        service='identifier',
                        region=self.region,
                    ) + "/projectToken/login"
                    body = {
                        "client_id": self.credential.client_id,
                        "client_secret": self.credential.client_secret,
                    }

                    _job = NetworkJob(
                        url=url,
                        method='POST',
                        result_type=LoginResult,
                        callback=callback,
                        body=body,
                    )

                    self.send(
                        job=_job,
                        is_blocking=is_blocking,
                    )
            else:
                callback(
                    AsyncResult(
                        error=BrokenPipeError()
                    )
                )
        except Exception as e:
            callback(
                AsyncResult(
                    error=e
                )
            )

    def connect(self):
        if self._connection:
            return

        async_result = []
        with timeout(30):
            self._connect(
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            self.disconnect()
            raise async_result[0].error

        if self._project_token is None:
            self._project_token = async_result[0].result.access_token

    async def connect_async(self):
        if self._connection:
            return

        async_result = []
        self._connect(
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error

        if self._project_token is None:
            self._project_token = async_result[0].result.access_token

    def disconnect(self):
        if self._connection:
            self._connection.close()
            self._connection = None
        for job in self._job_queue:
            job.callback(
                AsyncResult(
                    error=BrokenPipeError(),
                )
            )
        self._job_queue.clear()
        self._project_token = None


class AbstractGs2RestClient(object):

    def __init__(self, session):
        """
        コンストラクタ
        :param session: 認証情報
        :type session: gs2_core_client.model.RestSession.RestSession
        """
        self._session = session

    @property
    def session(self) -> Gs2RestSession:
        return self._session

    def _create_authorized_headers(self) -> Dict[str, Any]:
        return {
            'X-GS2-CLIENT-ID': self._session.credential.client_id,
            'Authorization': 'Bearer {}'.format(self._session.project_token),
        }


def receive_handler(
        session: Gs2RestSession,
        job_queue: Deque[NetworkJob],
):
    while session.connection:
        try:
            job = job_queue.popleft()
            session._send(job)
        except IndexError:
            time.sleep(0.01)

