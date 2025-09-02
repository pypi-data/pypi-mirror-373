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
import time


class Gs2IdentifierWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_users(
        self,
        request: DescribeUsersRequest,
        callback: Callable[[AsyncResult[DescribeUsersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='user',
            function='describeUsers',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeUsersResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='user',
            function='createUser',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateUserResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='user',
            function='updateUser',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.description is not None:
            body["description"] = request.description

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateUserResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='user',
            function='getUser',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetUserResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='user',
            function='deleteUser',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteUserResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='securityPolicy',
            function='describeSecurityPolicies',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeSecurityPoliciesResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='securityPolicy',
            function='describeCommonSecurityPolicies',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeCommonSecurityPoliciesResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='securityPolicy',
            function='createSecurityPolicy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.policy is not None:
            body["policy"] = request.policy

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateSecurityPolicyResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='securityPolicy',
            function='updateSecurityPolicy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.security_policy_name is not None:
            body["securityPolicyName"] = request.security_policy_name
        if request.description is not None:
            body["description"] = request.description
        if request.policy is not None:
            body["policy"] = request.policy

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateSecurityPolicyResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='securityPolicy',
            function='getSecurityPolicy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.security_policy_name is not None:
            body["securityPolicyName"] = request.security_policy_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSecurityPolicyResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='securityPolicy',
            function='deleteSecurityPolicy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.security_policy_name is not None:
            body["securityPolicyName"] = request.security_policy_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteSecurityPolicyResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='identifier',
            function='describeIdentifiers',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeIdentifiersResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='identifier',
            function='createIdentifier',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateIdentifierResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='identifier',
            function='getIdentifier',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.client_id is not None:
            body["clientId"] = request.client_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetIdentifierResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='identifier',
            function='deleteIdentifier',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.client_id is not None:
            body["clientId"] = request.client_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteIdentifierResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='identifier',
            function='describeAttachedGuards',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.client_id is not None:
            body["clientId"] = request.client_id
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeAttachedGuardsResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='identifier',
            function='attachGuard',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.client_id is not None:
            body["clientId"] = request.client_id
        if request.guard_namespace_id is not None:
            body["guardNamespaceId"] = request.guard_namespace_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AttachGuardResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='identifier',
            function='detachGuard',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.client_id is not None:
            body["clientId"] = request.client_id
        if request.guard_namespace_id is not None:
            body["guardNamespaceId"] = request.guard_namespace_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DetachGuardResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='identifier',
            function='getServiceVersion',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetServiceVersionResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='password',
            function='createPassword',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreatePasswordResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='password',
            function='getPassword',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPasswordResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='password',
            function='enableMfa',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=EnableMfaResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='password',
            function='challengeMfa',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.passcode is not None:
            body["passcode"] = request.passcode

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ChallengeMfaResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='password',
            function='disableMfa',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DisableMfaResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='password',
            function='deletePassword',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeletePasswordResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='attachSecurityPolicy',
            function='getHasSecurityPolicy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetHasSecurityPolicyResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='attachSecurityPolicy',
            function='attachSecurityPolicy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.security_policy_id is not None:
            body["securityPolicyId"] = request.security_policy_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AttachSecurityPolicyResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='attachSecurityPolicy',
            function='detachSecurityPolicy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.security_policy_id is not None:
            body["securityPolicyId"] = request.security_policy_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DetachSecurityPolicyResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='projectToken',
            function='login',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.client_id is not None:
            body["clientId"] = request.client_id
        if request.client_secret is not None:
            body["clientSecret"] = request.client_secret

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=LoginResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="identifier",
            component='projectToken',
            function='loginByUser',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_name is not None:
            body["userName"] = request.user_name
        if request.password is not None:
            body["password"] = request.password
        if request.otp is not None:
            body["otp"] = request.otp

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=LoginByUserResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result