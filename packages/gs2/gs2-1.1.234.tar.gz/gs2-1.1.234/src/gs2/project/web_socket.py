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


class Gs2ProjectWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _create_account(
        self,
        request: CreateAccountRequest,
        callback: Callable[[AsyncResult[CreateAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='createAccount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.email is not None:
            body["email"] = request.email
        if request.full_name is not None:
            body["fullName"] = request.full_name
        if request.company_name is not None:
            body["companyName"] = request.company_name
        if request.password is not None:
            body["password"] = request.password
        if request.lang is not None:
            body["lang"] = request.lang

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateAccountResult,
                callback=callback,
                body=body,
            )
        )

    def create_account(
        self,
        request: CreateAccountRequest,
    ) -> CreateAccountResult:
        async_result = []
        with timeout(30):
            self._create_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_account_async(
        self,
        request: CreateAccountRequest,
    ) -> CreateAccountResult:
        async_result = []
        self._create_account(
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

    def _verify(
        self,
        request: VerifyRequest,
        callback: Callable[[AsyncResult[VerifyResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='verify',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.verify_token is not None:
            body["verifyToken"] = request.verify_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyResult,
                callback=callback,
                body=body,
            )
        )

    def verify(
        self,
        request: VerifyRequest,
    ) -> VerifyResult:
        async_result = []
        with timeout(30):
            self._verify(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_async(
        self,
        request: VerifyRequest,
    ) -> VerifyResult:
        async_result = []
        self._verify(
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

    def _sign_in(
        self,
        request: SignInRequest,
        callback: Callable[[AsyncResult[SignInResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='signIn',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.email is not None:
            body["email"] = request.email
        if request.password is not None:
            body["password"] = request.password
        if request.otp is not None:
            body["otp"] = request.otp

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SignInResult,
                callback=callback,
                body=body,
            )
        )

    def sign_in(
        self,
        request: SignInRequest,
    ) -> SignInResult:
        async_result = []
        with timeout(30):
            self._sign_in(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sign_in_async(
        self,
        request: SignInRequest,
    ) -> SignInResult:
        async_result = []
        self._sign_in(
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

    def _forget(
        self,
        request: ForgetRequest,
        callback: Callable[[AsyncResult[ForgetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='forget',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.email is not None:
            body["email"] = request.email
        if request.lang is not None:
            body["lang"] = request.lang

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ForgetResult,
                callback=callback,
                body=body,
            )
        )

    def forget(
        self,
        request: ForgetRequest,
    ) -> ForgetResult:
        async_result = []
        with timeout(30):
            self._forget(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def forget_async(
        self,
        request: ForgetRequest,
    ) -> ForgetResult:
        async_result = []
        self._forget(
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

    def _issue_password(
        self,
        request: IssuePasswordRequest,
        callback: Callable[[AsyncResult[IssuePasswordResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='issuePassword',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.issue_password_token is not None:
            body["issuePasswordToken"] = request.issue_password_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=IssuePasswordResult,
                callback=callback,
                body=body,
            )
        )

    def issue_password(
        self,
        request: IssuePasswordRequest,
    ) -> IssuePasswordResult:
        async_result = []
        with timeout(30):
            self._issue_password(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def issue_password_async(
        self,
        request: IssuePasswordRequest,
    ) -> IssuePasswordResult:
        async_result = []
        self._issue_password(
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

    def _update_account(
        self,
        request: UpdateAccountRequest,
        callback: Callable[[AsyncResult[UpdateAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='updateAccount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.email is not None:
            body["email"] = request.email
        if request.full_name is not None:
            body["fullName"] = request.full_name
        if request.company_name is not None:
            body["companyName"] = request.company_name
        if request.password is not None:
            body["password"] = request.password
        if request.account_token is not None:
            body["accountToken"] = request.account_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateAccountResult,
                callback=callback,
                body=body,
            )
        )

    def update_account(
        self,
        request: UpdateAccountRequest,
    ) -> UpdateAccountResult:
        async_result = []
        with timeout(30):
            self._update_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_account_async(
        self,
        request: UpdateAccountRequest,
    ) -> UpdateAccountResult:
        async_result = []
        self._update_account(
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
            service="project",
            component='account',
            function='enableMfa',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token

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
            service="project",
            component='account',
            function='challengeMfa',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
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
            service="project",
            component='account',
            function='disableMfa',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token

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

    def _delete_account(
        self,
        request: DeleteAccountRequest,
        callback: Callable[[AsyncResult[DeleteAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='account',
            function='deleteAccount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteAccountResult,
                callback=callback,
                body=body,
            )
        )

    def delete_account(
        self,
        request: DeleteAccountRequest,
    ) -> DeleteAccountResult:
        async_result = []
        with timeout(30):
            self._delete_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_account_async(
        self,
        request: DeleteAccountRequest,
    ) -> DeleteAccountResult:
        async_result = []
        self._delete_account(
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

    def _describe_projects(
        self,
        request: DescribeProjectsRequest,
        callback: Callable[[AsyncResult[DescribeProjectsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='describeProjects',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeProjectsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_projects(
        self,
        request: DescribeProjectsRequest,
    ) -> DescribeProjectsResult:
        async_result = []
        with timeout(30):
            self._describe_projects(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_projects_async(
        self,
        request: DescribeProjectsRequest,
    ) -> DescribeProjectsResult:
        async_result = []
        self._describe_projects(
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

    def _create_project(
        self,
        request: CreateProjectRequest,
        callback: Callable[[AsyncResult[CreateProjectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='createProject',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.plan is not None:
            body["plan"] = request.plan
        if request.currency is not None:
            body["currency"] = request.currency
        if request.activate_region_name is not None:
            body["activateRegionName"] = request.activate_region_name
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name
        if request.enable_event_bridge is not None:
            body["enableEventBridge"] = request.enable_event_bridge
        if request.event_bridge_aws_account_id is not None:
            body["eventBridgeAwsAccountId"] = request.event_bridge_aws_account_id
        if request.event_bridge_aws_region is not None:
            body["eventBridgeAwsRegion"] = request.event_bridge_aws_region

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateProjectResult,
                callback=callback,
                body=body,
            )
        )

    def create_project(
        self,
        request: CreateProjectRequest,
    ) -> CreateProjectResult:
        async_result = []
        with timeout(30):
            self._create_project(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_project_async(
        self,
        request: CreateProjectRequest,
    ) -> CreateProjectResult:
        async_result = []
        self._create_project(
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

    def _get_project(
        self,
        request: GetProjectRequest,
        callback: Callable[[AsyncResult[GetProjectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='getProject',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetProjectResult,
                callback=callback,
                body=body,
            )
        )

    def get_project(
        self,
        request: GetProjectRequest,
    ) -> GetProjectResult:
        async_result = []
        with timeout(30):
            self._get_project(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_project_async(
        self,
        request: GetProjectRequest,
    ) -> GetProjectResult:
        async_result = []
        self._get_project(
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

    def _get_project_token(
        self,
        request: GetProjectTokenRequest,
        callback: Callable[[AsyncResult[GetProjectTokenResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='getProjectToken',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.account_token is not None:
            body["accountToken"] = request.account_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetProjectTokenResult,
                callback=callback,
                body=body,
            )
        )

    def get_project_token(
        self,
        request: GetProjectTokenRequest,
    ) -> GetProjectTokenResult:
        async_result = []
        with timeout(30):
            self._get_project_token(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_project_token_async(
        self,
        request: GetProjectTokenRequest,
    ) -> GetProjectTokenResult:
        async_result = []
        self._get_project_token(
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

    def _get_project_token_by_identifier(
        self,
        request: GetProjectTokenByIdentifierRequest,
        callback: Callable[[AsyncResult[GetProjectTokenByIdentifierResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='getProjectTokenByIdentifier',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_name is not None:
            body["accountName"] = request.account_name
        if request.project_name is not None:
            body["projectName"] = request.project_name
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
                result_type=GetProjectTokenByIdentifierResult,
                callback=callback,
                body=body,
            )
        )

    def get_project_token_by_identifier(
        self,
        request: GetProjectTokenByIdentifierRequest,
    ) -> GetProjectTokenByIdentifierResult:
        async_result = []
        with timeout(30):
            self._get_project_token_by_identifier(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_project_token_by_identifier_async(
        self,
        request: GetProjectTokenByIdentifierRequest,
    ) -> GetProjectTokenByIdentifierResult:
        async_result = []
        self._get_project_token_by_identifier(
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

    def _update_project(
        self,
        request: UpdateProjectRequest,
        callback: Callable[[AsyncResult[UpdateProjectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='updateProject',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.description is not None:
            body["description"] = request.description
        if request.plan is not None:
            body["plan"] = request.plan
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name
        if request.enable_event_bridge is not None:
            body["enableEventBridge"] = request.enable_event_bridge
        if request.event_bridge_aws_account_id is not None:
            body["eventBridgeAwsAccountId"] = request.event_bridge_aws_account_id
        if request.event_bridge_aws_region is not None:
            body["eventBridgeAwsRegion"] = request.event_bridge_aws_region

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateProjectResult,
                callback=callback,
                body=body,
            )
        )

    def update_project(
        self,
        request: UpdateProjectRequest,
    ) -> UpdateProjectResult:
        async_result = []
        with timeout(30):
            self._update_project(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_project_async(
        self,
        request: UpdateProjectRequest,
    ) -> UpdateProjectResult:
        async_result = []
        self._update_project(
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

    def _activate_region(
        self,
        request: ActivateRegionRequest,
        callback: Callable[[AsyncResult[ActivateRegionResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='activateRegion',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.region_name is not None:
            body["regionName"] = request.region_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ActivateRegionResult,
                callback=callback,
                body=body,
            )
        )

    def activate_region(
        self,
        request: ActivateRegionRequest,
    ) -> ActivateRegionResult:
        async_result = []
        with timeout(30):
            self._activate_region(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def activate_region_async(
        self,
        request: ActivateRegionRequest,
    ) -> ActivateRegionResult:
        async_result = []
        self._activate_region(
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

    def _wait_activate_region(
        self,
        request: WaitActivateRegionRequest,
        callback: Callable[[AsyncResult[WaitActivateRegionResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='waitActivateRegion',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.region_name is not None:
            body["regionName"] = request.region_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=WaitActivateRegionResult,
                callback=callback,
                body=body,
            )
        )

    def wait_activate_region(
        self,
        request: WaitActivateRegionRequest,
    ) -> WaitActivateRegionResult:
        async_result = []
        with timeout(30):
            self._wait_activate_region(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def wait_activate_region_async(
        self,
        request: WaitActivateRegionRequest,
    ) -> WaitActivateRegionResult:
        async_result = []
        self._wait_activate_region(
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

    def _delete_project(
        self,
        request: DeleteProjectRequest,
        callback: Callable[[AsyncResult[DeleteProjectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='project',
            function='deleteProject',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteProjectResult,
                callback=callback,
                body=body,
            )
        )

    def delete_project(
        self,
        request: DeleteProjectRequest,
    ) -> DeleteProjectResult:
        async_result = []
        with timeout(30):
            self._delete_project(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_project_async(
        self,
        request: DeleteProjectRequest,
    ) -> DeleteProjectResult:
        async_result = []
        self._delete_project(
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

    def _describe_billing_methods(
        self,
        request: DescribeBillingMethodsRequest,
        callback: Callable[[AsyncResult[DescribeBillingMethodsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='describeBillingMethods',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeBillingMethodsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_billing_methods(
        self,
        request: DescribeBillingMethodsRequest,
    ) -> DescribeBillingMethodsResult:
        async_result = []
        with timeout(30):
            self._describe_billing_methods(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_billing_methods_async(
        self,
        request: DescribeBillingMethodsRequest,
    ) -> DescribeBillingMethodsResult:
        async_result = []
        self._describe_billing_methods(
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

    def _create_billing_method(
        self,
        request: CreateBillingMethodRequest,
        callback: Callable[[AsyncResult[CreateBillingMethodResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='createBillingMethod',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.description is not None:
            body["description"] = request.description
        if request.method_type is not None:
            body["methodType"] = request.method_type
        if request.card_customer_id is not None:
            body["cardCustomerId"] = request.card_customer_id
        if request.partner_id is not None:
            body["partnerId"] = request.partner_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateBillingMethodResult,
                callback=callback,
                body=body,
            )
        )

    def create_billing_method(
        self,
        request: CreateBillingMethodRequest,
    ) -> CreateBillingMethodResult:
        async_result = []
        with timeout(30):
            self._create_billing_method(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_billing_method_async(
        self,
        request: CreateBillingMethodRequest,
    ) -> CreateBillingMethodResult:
        async_result = []
        self._create_billing_method(
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

    def _get_billing_method(
        self,
        request: GetBillingMethodRequest,
        callback: Callable[[AsyncResult[GetBillingMethodResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='getBillingMethod',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetBillingMethodResult,
                callback=callback,
                body=body,
            )
        )

    def get_billing_method(
        self,
        request: GetBillingMethodRequest,
    ) -> GetBillingMethodResult:
        async_result = []
        with timeout(30):
            self._get_billing_method(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_billing_method_async(
        self,
        request: GetBillingMethodRequest,
    ) -> GetBillingMethodResult:
        async_result = []
        self._get_billing_method(
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

    def _update_billing_method(
        self,
        request: UpdateBillingMethodRequest,
        callback: Callable[[AsyncResult[UpdateBillingMethodResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='updateBillingMethod',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name
        if request.description is not None:
            body["description"] = request.description

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateBillingMethodResult,
                callback=callback,
                body=body,
            )
        )

    def update_billing_method(
        self,
        request: UpdateBillingMethodRequest,
    ) -> UpdateBillingMethodResult:
        async_result = []
        with timeout(30):
            self._update_billing_method(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_billing_method_async(
        self,
        request: UpdateBillingMethodRequest,
    ) -> UpdateBillingMethodResult:
        async_result = []
        self._update_billing_method(
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

    def _delete_billing_method(
        self,
        request: DeleteBillingMethodRequest,
        callback: Callable[[AsyncResult[DeleteBillingMethodResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billingMethod',
            function='deleteBillingMethod',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.billing_method_name is not None:
            body["billingMethodName"] = request.billing_method_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteBillingMethodResult,
                callback=callback,
                body=body,
            )
        )

    def delete_billing_method(
        self,
        request: DeleteBillingMethodRequest,
    ) -> DeleteBillingMethodResult:
        async_result = []
        with timeout(30):
            self._delete_billing_method(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_billing_method_async(
        self,
        request: DeleteBillingMethodRequest,
    ) -> DeleteBillingMethodResult:
        async_result = []
        self._delete_billing_method(
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

    def _describe_receipts(
        self,
        request: DescribeReceiptsRequest,
        callback: Callable[[AsyncResult[DescribeReceiptsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='receipt',
            function='describeReceipts',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeReceiptsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_receipts(
        self,
        request: DescribeReceiptsRequest,
    ) -> DescribeReceiptsResult:
        async_result = []
        with timeout(30):
            self._describe_receipts(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_receipts_async(
        self,
        request: DescribeReceiptsRequest,
    ) -> DescribeReceiptsResult:
        async_result = []
        self._describe_receipts(
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

    def _describe_billings(
        self,
        request: DescribeBillingsRequest,
        callback: Callable[[AsyncResult[DescribeBillingsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='billing',
            function='describeBillings',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.account_token is not None:
            body["accountToken"] = request.account_token
        if request.project_name is not None:
            body["projectName"] = request.project_name
        if request.year is not None:
            body["year"] = request.year
        if request.month is not None:
            body["month"] = request.month
        if request.region is not None:
            body["region"] = request.region
        if request.service is not None:
            body["service"] = request.service

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeBillingsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_billings(
        self,
        request: DescribeBillingsRequest,
    ) -> DescribeBillingsResult:
        async_result = []
        with timeout(30):
            self._describe_billings(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_billings_async(
        self,
        request: DescribeBillingsRequest,
    ) -> DescribeBillingsResult:
        async_result = []
        self._describe_billings(
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

    def _describe_dump_progresses(
        self,
        request: DescribeDumpProgressesRequest,
        callback: Callable[[AsyncResult[DescribeDumpProgressesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='dumpProgress',
            function='describeDumpProgresses',
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
                result_type=DescribeDumpProgressesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_dump_progresses(
        self,
        request: DescribeDumpProgressesRequest,
    ) -> DescribeDumpProgressesResult:
        async_result = []
        with timeout(30):
            self._describe_dump_progresses(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_dump_progresses_async(
        self,
        request: DescribeDumpProgressesRequest,
    ) -> DescribeDumpProgressesResult:
        async_result = []
        self._describe_dump_progresses(
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

    def _get_dump_progress(
        self,
        request: GetDumpProgressRequest,
        callback: Callable[[AsyncResult[GetDumpProgressResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='dumpProgress',
            function='getDumpProgress',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetDumpProgressResult,
                callback=callback,
                body=body,
            )
        )

    def get_dump_progress(
        self,
        request: GetDumpProgressRequest,
    ) -> GetDumpProgressResult:
        async_result = []
        with timeout(30):
            self._get_dump_progress(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_dump_progress_async(
        self,
        request: GetDumpProgressRequest,
    ) -> GetDumpProgressResult:
        async_result = []
        self._get_dump_progress(
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

    def _wait_dump_user_data(
        self,
        request: WaitDumpUserDataRequest,
        callback: Callable[[AsyncResult[WaitDumpUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='dumpProgress',
            function='waitDumpUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.owner_id is not None:
            body["ownerId"] = request.owner_id
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.microservice_name is not None:
            body["microserviceName"] = request.microservice_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=WaitDumpUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def wait_dump_user_data(
        self,
        request: WaitDumpUserDataRequest,
    ) -> WaitDumpUserDataResult:
        async_result = []
        with timeout(30):
            self._wait_dump_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def wait_dump_user_data_async(
        self,
        request: WaitDumpUserDataRequest,
    ) -> WaitDumpUserDataResult:
        async_result = []
        self._wait_dump_user_data(
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

    def _archive_dump_user_data(
        self,
        request: ArchiveDumpUserDataRequest,
        callback: Callable[[AsyncResult[ArchiveDumpUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='dumpProgress',
            function='archiveDumpUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.owner_id is not None:
            body["ownerId"] = request.owner_id
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ArchiveDumpUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def archive_dump_user_data(
        self,
        request: ArchiveDumpUserDataRequest,
    ) -> ArchiveDumpUserDataResult:
        async_result = []
        with timeout(30):
            self._archive_dump_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def archive_dump_user_data_async(
        self,
        request: ArchiveDumpUserDataRequest,
    ) -> ArchiveDumpUserDataResult:
        async_result = []
        self._archive_dump_user_data(
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

    def _dump_user_data(
        self,
        request: DumpUserDataRequest,
        callback: Callable[[AsyncResult[DumpUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='dumpProgress',
            function='dumpUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DumpUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def dump_user_data(
        self,
        request: DumpUserDataRequest,
    ) -> DumpUserDataResult:
        async_result = []
        with timeout(30):
            self._dump_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def dump_user_data_async(
        self,
        request: DumpUserDataRequest,
    ) -> DumpUserDataResult:
        async_result = []
        self._dump_user_data(
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

    def _get_dump_user_data(
        self,
        request: GetDumpUserDataRequest,
        callback: Callable[[AsyncResult[GetDumpUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='dumpProgress',
            function='getDumpUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetDumpUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def get_dump_user_data(
        self,
        request: GetDumpUserDataRequest,
    ) -> GetDumpUserDataResult:
        async_result = []
        with timeout(30):
            self._get_dump_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_dump_user_data_async(
        self,
        request: GetDumpUserDataRequest,
    ) -> GetDumpUserDataResult:
        async_result = []
        self._get_dump_user_data(
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

    def _describe_clean_progresses(
        self,
        request: DescribeCleanProgressesRequest,
        callback: Callable[[AsyncResult[DescribeCleanProgressesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='cleanProgress',
            function='describeCleanProgresses',
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
                result_type=DescribeCleanProgressesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_clean_progresses(
        self,
        request: DescribeCleanProgressesRequest,
    ) -> DescribeCleanProgressesResult:
        async_result = []
        with timeout(30):
            self._describe_clean_progresses(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_clean_progresses_async(
        self,
        request: DescribeCleanProgressesRequest,
    ) -> DescribeCleanProgressesResult:
        async_result = []
        self._describe_clean_progresses(
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

    def _get_clean_progress(
        self,
        request: GetCleanProgressRequest,
        callback: Callable[[AsyncResult[GetCleanProgressResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='cleanProgress',
            function='getCleanProgress',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCleanProgressResult,
                callback=callback,
                body=body,
            )
        )

    def get_clean_progress(
        self,
        request: GetCleanProgressRequest,
    ) -> GetCleanProgressResult:
        async_result = []
        with timeout(30):
            self._get_clean_progress(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_clean_progress_async(
        self,
        request: GetCleanProgressRequest,
    ) -> GetCleanProgressResult:
        async_result = []
        self._get_clean_progress(
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

    def _wait_clean_user_data(
        self,
        request: WaitCleanUserDataRequest,
        callback: Callable[[AsyncResult[WaitCleanUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='cleanProgress',
            function='waitCleanUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.microservice_name is not None:
            body["microserviceName"] = request.microservice_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=WaitCleanUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def wait_clean_user_data(
        self,
        request: WaitCleanUserDataRequest,
    ) -> WaitCleanUserDataResult:
        async_result = []
        with timeout(30):
            self._wait_clean_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def wait_clean_user_data_async(
        self,
        request: WaitCleanUserDataRequest,
    ) -> WaitCleanUserDataResult:
        async_result = []
        self._wait_clean_user_data(
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

    def _clean_user_data(
        self,
        request: CleanUserDataRequest,
        callback: Callable[[AsyncResult[CleanUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='cleanProgress',
            function='cleanUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CleanUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def clean_user_data(
        self,
        request: CleanUserDataRequest,
    ) -> CleanUserDataResult:
        async_result = []
        with timeout(30):
            self._clean_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def clean_user_data_async(
        self,
        request: CleanUserDataRequest,
    ) -> CleanUserDataResult:
        async_result = []
        self._clean_user_data(
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

    def _describe_import_progresses(
        self,
        request: DescribeImportProgressesRequest,
        callback: Callable[[AsyncResult[DescribeImportProgressesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='importProgress',
            function='describeImportProgresses',
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
                result_type=DescribeImportProgressesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_import_progresses(
        self,
        request: DescribeImportProgressesRequest,
    ) -> DescribeImportProgressesResult:
        async_result = []
        with timeout(30):
            self._describe_import_progresses(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_import_progresses_async(
        self,
        request: DescribeImportProgressesRequest,
    ) -> DescribeImportProgressesResult:
        async_result = []
        self._describe_import_progresses(
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

    def _get_import_progress(
        self,
        request: GetImportProgressRequest,
        callback: Callable[[AsyncResult[GetImportProgressResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='importProgress',
            function='getImportProgress',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetImportProgressResult,
                callback=callback,
                body=body,
            )
        )

    def get_import_progress(
        self,
        request: GetImportProgressRequest,
    ) -> GetImportProgressResult:
        async_result = []
        with timeout(30):
            self._get_import_progress(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_import_progress_async(
        self,
        request: GetImportProgressRequest,
    ) -> GetImportProgressResult:
        async_result = []
        self._get_import_progress(
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

    def _wait_import_user_data(
        self,
        request: WaitImportUserDataRequest,
        callback: Callable[[AsyncResult[WaitImportUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='importProgress',
            function='waitImportUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.microservice_name is not None:
            body["microserviceName"] = request.microservice_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=WaitImportUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def wait_import_user_data(
        self,
        request: WaitImportUserDataRequest,
    ) -> WaitImportUserDataResult:
        async_result = []
        with timeout(30):
            self._wait_import_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def wait_import_user_data_async(
        self,
        request: WaitImportUserDataRequest,
    ) -> WaitImportUserDataResult:
        async_result = []
        self._wait_import_user_data(
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

    def _prepare_import_user_data(
        self,
        request: PrepareImportUserDataRequest,
        callback: Callable[[AsyncResult[PrepareImportUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='importProgress',
            function='prepareImportUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PrepareImportUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def prepare_import_user_data(
        self,
        request: PrepareImportUserDataRequest,
    ) -> PrepareImportUserDataResult:
        async_result = []
        with timeout(30):
            self._prepare_import_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def prepare_import_user_data_async(
        self,
        request: PrepareImportUserDataRequest,
    ) -> PrepareImportUserDataResult:
        async_result = []
        self._prepare_import_user_data(
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

    def _import_user_data(
        self,
        request: ImportUserDataRequest,
        callback: Callable[[AsyncResult[ImportUserDataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='importProgress',
            function='importUserData',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ImportUserDataResult,
                callback=callback,
                body=body,
            )
        )

    def import_user_data(
        self,
        request: ImportUserDataRequest,
    ) -> ImportUserDataResult:
        async_result = []
        with timeout(30):
            self._import_user_data(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def import_user_data_async(
        self,
        request: ImportUserDataRequest,
    ) -> ImportUserDataResult:
        async_result = []
        self._import_user_data(
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

    def _describe_import_error_logs(
        self,
        request: DescribeImportErrorLogsRequest,
        callback: Callable[[AsyncResult[DescribeImportErrorLogsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='importErrorLog',
            function='describeImportErrorLogs',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeImportErrorLogsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_import_error_logs(
        self,
        request: DescribeImportErrorLogsRequest,
    ) -> DescribeImportErrorLogsResult:
        async_result = []
        with timeout(30):
            self._describe_import_error_logs(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_import_error_logs_async(
        self,
        request: DescribeImportErrorLogsRequest,
    ) -> DescribeImportErrorLogsResult:
        async_result = []
        self._describe_import_error_logs(
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

    def _get_import_error_log(
        self,
        request: GetImportErrorLogRequest,
        callback: Callable[[AsyncResult[GetImportErrorLogResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="project",
            component='importErrorLog',
            function='getImportErrorLog',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.transaction_id is not None:
            body["transactionId"] = request.transaction_id
        if request.error_log_name is not None:
            body["errorLogName"] = request.error_log_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetImportErrorLogResult,
                callback=callback,
                body=body,
            )
        )

    def get_import_error_log(
        self,
        request: GetImportErrorLogRequest,
    ) -> GetImportErrorLogResult:
        async_result = []
        with timeout(30):
            self._get_import_error_log(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_import_error_log_async(
        self,
        request: GetImportErrorLogRequest,
    ) -> GetImportErrorLogResult:
        async_result = []
        self._get_import_error_log(
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