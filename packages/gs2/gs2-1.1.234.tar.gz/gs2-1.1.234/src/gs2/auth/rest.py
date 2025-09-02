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

from gs2.core import *
from .request import *
from .result import *


class Gs2AuthRestClient(rest.AbstractGs2RestClient):

    def _login(
        self,
        request: LoginRequest,
        callback: Callable[[AsyncResult[LoginResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='auth',
            region=self.session.region,
        ) + "/login"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset is not None:
            body["timeOffset"] = request.time_offset

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=LoginResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def login(
        self,
        request: LoginRequest,
    ) -> LoginResult:
        async_result = []
        with timeout(30):
            self._login(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def login_async(
        self,
        request: LoginRequest,
    ) -> LoginResult:
        async_result = []
        self._login(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _login_by_signature(
        self,
        request: LoginBySignatureRequest,
        callback: Callable[[AsyncResult[LoginBySignatureResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='auth',
            region=self.session.region,
        ) + "/login/signed"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.body is not None:
            body["body"] = request.body
        if request.signature is not None:
            body["signature"] = request.signature

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=LoginBySignatureResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def login_by_signature(
        self,
        request: LoginBySignatureRequest,
    ) -> LoginBySignatureResult:
        async_result = []
        with timeout(30):
            self._login_by_signature(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def login_by_signature_async(
        self,
        request: LoginBySignatureRequest,
    ) -> LoginBySignatureResult:
        async_result = []
        self._login_by_signature(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _federation(
        self,
        request: FederationRequest,
        callback: Callable[[AsyncResult[FederationResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='auth',
            region=self.session.region,
        ) + "/federation"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.original_user_id is not None:
            body["originalUserId"] = request.original_user_id
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.policy_document is not None:
            body["policyDocument"] = request.policy_document
        if request.time_offset is not None:
            body["timeOffset"] = request.time_offset

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=FederationResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def federation(
        self,
        request: FederationRequest,
    ) -> FederationResult:
        async_result = []
        with timeout(30):
            self._federation(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def federation_async(
        self,
        request: FederationRequest,
    ) -> FederationResult:
        async_result = []
        self._federation(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _issue_time_offset_token_by_user_id(
        self,
        request: IssueTimeOffsetTokenByUserIdRequest,
        callback: Callable[[AsyncResult[IssueTimeOffsetTokenByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='auth',
            region=self.session.region,
        ) + "/timeoffset/token"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset is not None:
            body["timeOffset"] = request.time_offset

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=IssueTimeOffsetTokenByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def issue_time_offset_token_by_user_id(
        self,
        request: IssueTimeOffsetTokenByUserIdRequest,
    ) -> IssueTimeOffsetTokenByUserIdResult:
        async_result = []
        with timeout(30):
            self._issue_time_offset_token_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def issue_time_offset_token_by_user_id_async(
        self,
        request: IssueTimeOffsetTokenByUserIdRequest,
    ) -> IssueTimeOffsetTokenByUserIdResult:
        async_result = []
        self._issue_time_offset_token_by_user_id(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_service_version(
        self,
        request: GetServiceVersionRequest,
        callback: Callable[[AsyncResult[GetServiceVersionResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='auth',
            region=self.session.region,
        ) + "/system/version"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetServiceVersionResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_service_version(
        self,
        request: GetServiceVersionRequest,
    ) -> GetServiceVersionResult:
        async_result = []
        with timeout(30):
            self._get_service_version(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_service_version_async(
        self,
        request: GetServiceVersionRequest,
    ) -> GetServiceVersionResult:
        async_result = []
        self._get_service_version(
            request,
            lambda result: async_result.append(result),
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result