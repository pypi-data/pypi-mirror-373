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
#
# deny overwrite

from gs2.core import *
from .request import *
from .result import *


class Gs2IdentifierRestClient(rest.AbstractGs2RestClient):

    def _describe_users(
        self,
        request: DescribeUsersRequest,
        callback: Callable[[AsyncResult[DescribeUsersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeUsersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_users(
        self,
        request: DescribeUsersRequest,
    ) -> DescribeUsersResult:
        async_result = []
        with timeout(30):
            self._describe_users(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_users_async(
        self,
        request: DescribeUsersRequest,
    ) -> DescribeUsersResult:
        async_result = []
        self._describe_users(
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

    def _create_user(
        self,
        request: CreateUserRequest,
        callback: Callable[[AsyncResult[CreateUserResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateUserResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_user(
        self,
        request: CreateUserRequest,
    ) -> CreateUserResult:
        async_result = []
        with timeout(30):
            self._create_user(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_user_async(
        self,
        request: CreateUserRequest,
    ) -> CreateUserResult:
        async_result = []
        self._create_user(
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

    def _update_user(
        self,
        request: UpdateUserRequest,
        callback: Callable[[AsyncResult[UpdateUserResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateUserResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_user(
        self,
        request: UpdateUserRequest,
    ) -> UpdateUserResult:
        async_result = []
        with timeout(30):
            self._update_user(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_user_async(
        self,
        request: UpdateUserRequest,
    ) -> UpdateUserResult:
        async_result = []
        self._update_user(
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

    def _get_user(
        self,
        request: GetUserRequest,
        callback: Callable[[AsyncResult[GetUserResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetUserResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_user(
        self,
        request: GetUserRequest,
    ) -> GetUserResult:
        async_result = []
        with timeout(30):
            self._get_user(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_user_async(
        self,
        request: GetUserRequest,
    ) -> GetUserResult:
        async_result = []
        self._get_user(
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

    def _delete_user(
        self,
        request: DeleteUserRequest,
        callback: Callable[[AsyncResult[DeleteUserResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteUserResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_user(
        self,
        request: DeleteUserRequest,
    ) -> DeleteUserResult:
        async_result = []
        with timeout(30):
            self._delete_user(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_user_async(
        self,
        request: DeleteUserRequest,
    ) -> DeleteUserResult:
        async_result = []
        self._delete_user(
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

    def _describe_security_policies(
        self,
        request: DescribeSecurityPoliciesRequest,
        callback: Callable[[AsyncResult[DescribeSecurityPoliciesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/securityPolicy"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeSecurityPoliciesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_security_policies(
        self,
        request: DescribeSecurityPoliciesRequest,
    ) -> DescribeSecurityPoliciesResult:
        async_result = []
        with timeout(30):
            self._describe_security_policies(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_security_policies_async(
        self,
        request: DescribeSecurityPoliciesRequest,
    ) -> DescribeSecurityPoliciesResult:
        async_result = []
        self._describe_security_policies(
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

    def _describe_common_security_policies(
        self,
        request: DescribeCommonSecurityPoliciesRequest,
        callback: Callable[[AsyncResult[DescribeCommonSecurityPoliciesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/securityPolicy/common"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeCommonSecurityPoliciesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_common_security_policies(
        self,
        request: DescribeCommonSecurityPoliciesRequest,
    ) -> DescribeCommonSecurityPoliciesResult:
        async_result = []
        with timeout(30):
            self._describe_common_security_policies(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_common_security_policies_async(
        self,
        request: DescribeCommonSecurityPoliciesRequest,
    ) -> DescribeCommonSecurityPoliciesResult:
        async_result = []
        self._describe_common_security_policies(
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

    def _create_security_policy(
        self,
        request: CreateSecurityPolicyRequest,
        callback: Callable[[AsyncResult[CreateSecurityPolicyResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/securityPolicy"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.policy is not None:
            body["policy"] = request.policy

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateSecurityPolicyResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_security_policy(
        self,
        request: CreateSecurityPolicyRequest,
    ) -> CreateSecurityPolicyResult:
        async_result = []
        with timeout(30):
            self._create_security_policy(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_security_policy_async(
        self,
        request: CreateSecurityPolicyRequest,
    ) -> CreateSecurityPolicyResult:
        async_result = []
        self._create_security_policy(
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

    def _update_security_policy(
        self,
        request: UpdateSecurityPolicyRequest,
        callback: Callable[[AsyncResult[UpdateSecurityPolicyResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/securityPolicy/{securityPolicyName}".format(
            securityPolicyName=request.security_policy_name if request.security_policy_name is not None and request.security_policy_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.policy is not None:
            body["policy"] = request.policy

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateSecurityPolicyResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_security_policy(
        self,
        request: UpdateSecurityPolicyRequest,
    ) -> UpdateSecurityPolicyResult:
        async_result = []
        with timeout(30):
            self._update_security_policy(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_security_policy_async(
        self,
        request: UpdateSecurityPolicyRequest,
    ) -> UpdateSecurityPolicyResult:
        async_result = []
        self._update_security_policy(
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

    def _get_security_policy(
        self,
        request: GetSecurityPolicyRequest,
        callback: Callable[[AsyncResult[GetSecurityPolicyResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/securityPolicy/{securityPolicyName}".format(
            securityPolicyName=request.security_policy_name if request.security_policy_name is not None and request.security_policy_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSecurityPolicyResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_security_policy(
        self,
        request: GetSecurityPolicyRequest,
    ) -> GetSecurityPolicyResult:
        async_result = []
        with timeout(30):
            self._get_security_policy(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_security_policy_async(
        self,
        request: GetSecurityPolicyRequest,
    ) -> GetSecurityPolicyResult:
        async_result = []
        self._get_security_policy(
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

    def _delete_security_policy(
        self,
        request: DeleteSecurityPolicyRequest,
        callback: Callable[[AsyncResult[DeleteSecurityPolicyResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/securityPolicy/{securityPolicyName}".format(
            securityPolicyName=request.security_policy_name if request.security_policy_name is not None and request.security_policy_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteSecurityPolicyResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_security_policy(
        self,
        request: DeleteSecurityPolicyRequest,
    ) -> DeleteSecurityPolicyResult:
        async_result = []
        with timeout(30):
            self._delete_security_policy(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_security_policy_async(
        self,
        request: DeleteSecurityPolicyRequest,
    ) -> DeleteSecurityPolicyResult:
        async_result = []
        self._delete_security_policy(
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

    def _describe_identifiers(
        self,
        request: DescribeIdentifiersRequest,
        callback: Callable[[AsyncResult[DescribeIdentifiersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/identifier".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeIdentifiersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_identifiers(
        self,
        request: DescribeIdentifiersRequest,
    ) -> DescribeIdentifiersResult:
        async_result = []
        with timeout(30):
            self._describe_identifiers(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_identifiers_async(
        self,
        request: DescribeIdentifiersRequest,
    ) -> DescribeIdentifiersResult:
        async_result = []
        self._describe_identifiers(
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

    def _create_identifier(
        self,
        request: CreateIdentifierRequest,
        callback: Callable[[AsyncResult[CreateIdentifierResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/identifier".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateIdentifierResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_identifier(
        self,
        request: CreateIdentifierRequest,
    ) -> CreateIdentifierResult:
        async_result = []
        with timeout(30):
            self._create_identifier(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_identifier_async(
        self,
        request: CreateIdentifierRequest,
    ) -> CreateIdentifierResult:
        async_result = []
        self._create_identifier(
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

    def _get_identifier(
        self,
        request: GetIdentifierRequest,
        callback: Callable[[AsyncResult[GetIdentifierResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/identifier/{clientId}".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
            clientId=request.client_id if request.client_id is not None and request.client_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetIdentifierResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_identifier(
        self,
        request: GetIdentifierRequest,
    ) -> GetIdentifierResult:
        async_result = []
        with timeout(30):
            self._get_identifier(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_identifier_async(
        self,
        request: GetIdentifierRequest,
    ) -> GetIdentifierResult:
        async_result = []
        self._get_identifier(
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

    def _delete_identifier(
        self,
        request: DeleteIdentifierRequest,
        callback: Callable[[AsyncResult[DeleteIdentifierResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/identifier/{clientId}".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
            clientId=request.client_id if request.client_id is not None and request.client_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteIdentifierResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_identifier(
        self,
        request: DeleteIdentifierRequest,
    ) -> DeleteIdentifierResult:
        async_result = []
        with timeout(30):
            self._delete_identifier(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_identifier_async(
        self,
        request: DeleteIdentifierRequest,
    ) -> DeleteIdentifierResult:
        async_result = []
        self._delete_identifier(
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

    def _describe_attached_guards(
        self,
        request: DescribeAttachedGuardsRequest,
        callback: Callable[[AsyncResult[DescribeAttachedGuardsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/identifier/{clientId}/guard".format(
            clientId=request.client_id if request.client_id is not None and request.client_id != '' else 'null',
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeAttachedGuardsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_attached_guards(
        self,
        request: DescribeAttachedGuardsRequest,
    ) -> DescribeAttachedGuardsResult:
        async_result = []
        with timeout(30):
            self._describe_attached_guards(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_attached_guards_async(
        self,
        request: DescribeAttachedGuardsRequest,
    ) -> DescribeAttachedGuardsResult:
        async_result = []
        self._describe_attached_guards(
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

    def _attach_guard(
        self,
        request: AttachGuardRequest,
        callback: Callable[[AsyncResult[AttachGuardResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/identifier/{clientId}/guard".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
            clientId=request.client_id if request.client_id is not None and request.client_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.guard_namespace_id is not None:
            body["guardNamespaceId"] = request.guard_namespace_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AttachGuardResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def attach_guard(
        self,
        request: AttachGuardRequest,
    ) -> AttachGuardResult:
        async_result = []
        with timeout(30):
            self._attach_guard(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def attach_guard_async(
        self,
        request: AttachGuardRequest,
    ) -> AttachGuardResult:
        async_result = []
        self._attach_guard(
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

    def _detach_guard(
        self,
        request: DetachGuardRequest,
        callback: Callable[[AsyncResult[DetachGuardResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/identifier/{clientId}/guard/{guardNamespaceId}".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
            clientId=request.client_id if request.client_id is not None and request.client_id != '' else 'null',
            guardNamespaceId=request.guard_namespace_id if request.guard_namespace_id is not None and request.guard_namespace_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DetachGuardResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def detach_guard(
        self,
        request: DetachGuardRequest,
    ) -> DetachGuardResult:
        async_result = []
        with timeout(30):
            self._detach_guard(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def detach_guard_async(
        self,
        request: DetachGuardRequest,
    ) -> DetachGuardResult:
        async_result = []
        self._detach_guard(
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
            service='identifier',
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

    def _create_password(
        self,
        request: CreatePasswordRequest,
        callback: Callable[[AsyncResult[CreatePasswordResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/password".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreatePasswordResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_password(
        self,
        request: CreatePasswordRequest,
    ) -> CreatePasswordResult:
        async_result = []
        with timeout(30):
            self._create_password(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_password_async(
        self,
        request: CreatePasswordRequest,
    ) -> CreatePasswordResult:
        async_result = []
        self._create_password(
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

    def _get_password(
        self,
        request: GetPasswordRequest,
        callback: Callable[[AsyncResult[GetPasswordResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/password/entity".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetPasswordResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_password(
        self,
        request: GetPasswordRequest,
    ) -> GetPasswordResult:
        async_result = []
        with timeout(30):
            self._get_password(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_password_async(
        self,
        request: GetPasswordRequest,
    ) -> GetPasswordResult:
        async_result = []
        self._get_password(
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

    def _enable_mfa(
        self,
        request: EnableMfaRequest,
        callback: Callable[[AsyncResult[EnableMfaResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/mfa".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=EnableMfaResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def enable_mfa(
        self,
        request: EnableMfaRequest,
    ) -> EnableMfaResult:
        async_result = []
        with timeout(30):
            self._enable_mfa(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def enable_mfa_async(
        self,
        request: EnableMfaRequest,
    ) -> EnableMfaResult:
        async_result = []
        self._enable_mfa(
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

    def _challenge_mfa(
        self,
        request: ChallengeMfaRequest,
        callback: Callable[[AsyncResult[ChallengeMfaResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/mfa/challenge".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.passcode is not None:
            body["passcode"] = request.passcode

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ChallengeMfaResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def challenge_mfa(
        self,
        request: ChallengeMfaRequest,
    ) -> ChallengeMfaResult:
        async_result = []
        with timeout(30):
            self._challenge_mfa(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def challenge_mfa_async(
        self,
        request: ChallengeMfaRequest,
    ) -> ChallengeMfaResult:
        async_result = []
        self._challenge_mfa(
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

    def _disable_mfa(
        self,
        request: DisableMfaRequest,
        callback: Callable[[AsyncResult[DisableMfaResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/mfa".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DisableMfaResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def disable_mfa(
        self,
        request: DisableMfaRequest,
    ) -> DisableMfaResult:
        async_result = []
        with timeout(30):
            self._disable_mfa(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def disable_mfa_async(
        self,
        request: DisableMfaRequest,
    ) -> DisableMfaResult:
        async_result = []
        self._disable_mfa(
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

    def _delete_password(
        self,
        request: DeletePasswordRequest,
        callback: Callable[[AsyncResult[DeletePasswordResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/password/entity".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeletePasswordResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_password(
        self,
        request: DeletePasswordRequest,
    ) -> DeletePasswordResult:
        async_result = []
        with timeout(30):
            self._delete_password(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_password_async(
        self,
        request: DeletePasswordRequest,
    ) -> DeletePasswordResult:
        async_result = []
        self._delete_password(
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

    def _get_has_security_policy(
        self,
        request: GetHasSecurityPolicyRequest,
        callback: Callable[[AsyncResult[GetHasSecurityPolicyResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/securityPolicy".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetHasSecurityPolicyResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_has_security_policy(
        self,
        request: GetHasSecurityPolicyRequest,
    ) -> GetHasSecurityPolicyResult:
        async_result = []
        with timeout(30):
            self._get_has_security_policy(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_has_security_policy_async(
        self,
        request: GetHasSecurityPolicyRequest,
    ) -> GetHasSecurityPolicyResult:
        async_result = []
        self._get_has_security_policy(
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

    def _attach_security_policy(
        self,
        request: AttachSecurityPolicyRequest,
        callback: Callable[[AsyncResult[AttachSecurityPolicyResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/securityPolicy".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.security_policy_id is not None:
            body["securityPolicyId"] = request.security_policy_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AttachSecurityPolicyResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def attach_security_policy(
        self,
        request: AttachSecurityPolicyRequest,
    ) -> AttachSecurityPolicyResult:
        async_result = []
        with timeout(30):
            self._attach_security_policy(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def attach_security_policy_async(
        self,
        request: AttachSecurityPolicyRequest,
    ) -> AttachSecurityPolicyResult:
        async_result = []
        self._attach_security_policy(
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

    def _detach_security_policy(
        self,
        request: DetachSecurityPolicyRequest,
        callback: Callable[[AsyncResult[DetachSecurityPolicyResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/user/{userName}/securityPolicy/{securityPolicyId}".format(
            userName=request.user_name if request.user_name is not None and request.user_name != '' else 'null',
            securityPolicyId=request.security_policy_id if request.security_policy_id is not None and request.security_policy_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DetachSecurityPolicyResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def detach_security_policy(
        self,
        request: DetachSecurityPolicyRequest,
    ) -> DetachSecurityPolicyResult:
        async_result = []
        with timeout(30):
            self._detach_security_policy(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def detach_security_policy_async(
        self,
        request: DetachSecurityPolicyRequest,
    ) -> DetachSecurityPolicyResult:
        async_result = []
        self._detach_security_policy(
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

    def _login(
        self,
        request: LoginRequest,
        callback: Callable[[AsyncResult[LoginResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/projectToken/login"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.client_id is not None:
            body["client_id"] = request.client_id
        if request.client_secret is not None:
            body["client_secret"] = request.client_secret

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
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

    def _login_by_user(
        self,
        request: LoginByUserRequest,
        callback: Callable[[AsyncResult[LoginByUserResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='identifier',
            region=self.session.region,
        ) + "/projectToken/login/user"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.password is not None:
            body["password"] = request.password
        if request.otp is not None:
            body["otp"] = request.otp

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=LoginByUserResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def login_by_user(
        self,
        request: LoginByUserRequest,
    ) -> LoginByUserResult:
        async_result = []
        with timeout(30):
            self._login_by_user(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def login_by_user_async(
        self,
        request: LoginByUserRequest,
    ) -> LoginByUserResult:
        async_result = []
        self._login_by_user(
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