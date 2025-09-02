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


class Gs2DeployWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_stacks(
        self,
        request: DescribeStacksRequest,
        callback: Callable[[AsyncResult[DescribeStacksResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='describeStacks',
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
                result_type=DescribeStacksResult,
                callback=callback,
                body=body,
            )
        )

    def describe_stacks(
        self,
        request: DescribeStacksRequest,
    ) -> DescribeStacksResult:
        async_result = []
        with timeout(30):
            self._describe_stacks(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_stacks_async(
        self,
        request: DescribeStacksRequest,
    ) -> DescribeStacksResult:
        async_result = []
        self._describe_stacks(
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

    def _pre_create_stack(
        self,
        request: PreCreateStackRequest,
        callback: Callable[[AsyncResult[PreCreateStackResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='preCreateStack',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PreCreateStackResult,
                callback=callback,
                body=body,
            )
        )

    def pre_create_stack(
        self,
        request: PreCreateStackRequest,
    ) -> PreCreateStackResult:
        async_result = []
        with timeout(30):
            self._pre_create_stack(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_create_stack_async(
        self,
        request: PreCreateStackRequest,
    ) -> PreCreateStackResult:
        async_result = []
        self._pre_create_stack(
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

    def _create_stack(
        self,
        request: CreateStackRequest,
        callback: Callable[[AsyncResult[CreateStackResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='createStack',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.mode is not None:
            body["mode"] = request.mode
        if request.template is not None:
            body["template"] = request.template
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateStackResult,
                callback=callback,
                body=body,
            )
        )

    def create_stack(
        self,
        request: CreateStackRequest,
    ) -> CreateStackResult:
        async_result = []
        with timeout(30):
            self._create_stack(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_stack_async(
        self,
        request: CreateStackRequest,
    ) -> CreateStackResult:
        async_result = []
        self._create_stack(
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

    def _create_stack_from_git_hub(
        self,
        request: CreateStackFromGitHubRequest,
        callback: Callable[[AsyncResult[CreateStackFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='createStackFromGitHub',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateStackFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def create_stack_from_git_hub(
        self,
        request: CreateStackFromGitHubRequest,
    ) -> CreateStackFromGitHubResult:
        async_result = []
        with timeout(30):
            self._create_stack_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_stack_from_git_hub_async(
        self,
        request: CreateStackFromGitHubRequest,
    ) -> CreateStackFromGitHubResult:
        async_result = []
        self._create_stack_from_git_hub(
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

    def _pre_validate(
        self,
        request: PreValidateRequest,
        callback: Callable[[AsyncResult[PreValidateResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='preValidate',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PreValidateResult,
                callback=callback,
                body=body,
            )
        )

    def pre_validate(
        self,
        request: PreValidateRequest,
    ) -> PreValidateResult:
        async_result = []
        with timeout(30):
            self._pre_validate(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_validate_async(
        self,
        request: PreValidateRequest,
    ) -> PreValidateResult:
        async_result = []
        self._pre_validate(
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

    def _validate(
        self,
        request: ValidateRequest,
        callback: Callable[[AsyncResult[ValidateResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='validate',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.mode is not None:
            body["mode"] = request.mode
        if request.template is not None:
            body["template"] = request.template
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ValidateResult,
                callback=callback,
                body=body,
            )
        )

    def validate(
        self,
        request: ValidateRequest,
    ) -> ValidateResult:
        async_result = []
        with timeout(30):
            self._validate(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def validate_async(
        self,
        request: ValidateRequest,
    ) -> ValidateResult:
        async_result = []
        self._validate(
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

    def _get_stack_status(
        self,
        request: GetStackStatusRequest,
        callback: Callable[[AsyncResult[GetStackStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='getStackStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStackStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_stack_status(
        self,
        request: GetStackStatusRequest,
    ) -> GetStackStatusResult:
        async_result = []
        with timeout(30):
            self._get_stack_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stack_status_async(
        self,
        request: GetStackStatusRequest,
    ) -> GetStackStatusResult:
        async_result = []
        self._get_stack_status(
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

    def _get_stack(
        self,
        request: GetStackRequest,
        callback: Callable[[AsyncResult[GetStackResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='getStack',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStackResult,
                callback=callback,
                body=body,
            )
        )

    def get_stack(
        self,
        request: GetStackRequest,
    ) -> GetStackResult:
        async_result = []
        with timeout(30):
            self._get_stack(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stack_async(
        self,
        request: GetStackRequest,
    ) -> GetStackResult:
        async_result = []
        self._get_stack(
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

    def _pre_update_stack(
        self,
        request: PreUpdateStackRequest,
        callback: Callable[[AsyncResult[PreUpdateStackResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='preUpdateStack',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PreUpdateStackResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_stack(
        self,
        request: PreUpdateStackRequest,
    ) -> PreUpdateStackResult:
        async_result = []
        with timeout(30):
            self._pre_update_stack(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_stack_async(
        self,
        request: PreUpdateStackRequest,
    ) -> PreUpdateStackResult:
        async_result = []
        self._pre_update_stack(
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

    def _update_stack(
        self,
        request: UpdateStackRequest,
        callback: Callable[[AsyncResult[UpdateStackResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='updateStack',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.description is not None:
            body["description"] = request.description
        if request.mode is not None:
            body["mode"] = request.mode
        if request.template is not None:
            body["template"] = request.template
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateStackResult,
                callback=callback,
                body=body,
            )
        )

    def update_stack(
        self,
        request: UpdateStackRequest,
    ) -> UpdateStackResult:
        async_result = []
        with timeout(30):
            self._update_stack(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_stack_async(
        self,
        request: UpdateStackRequest,
    ) -> UpdateStackResult:
        async_result = []
        self._update_stack(
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

    def _pre_change_set(
        self,
        request: PreChangeSetRequest,
        callback: Callable[[AsyncResult[PreChangeSetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='preChangeSet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PreChangeSetResult,
                callback=callback,
                body=body,
            )
        )

    def pre_change_set(
        self,
        request: PreChangeSetRequest,
    ) -> PreChangeSetResult:
        async_result = []
        with timeout(30):
            self._pre_change_set(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_change_set_async(
        self,
        request: PreChangeSetRequest,
    ) -> PreChangeSetResult:
        async_result = []
        self._pre_change_set(
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

    def _change_set(
        self,
        request: ChangeSetRequest,
        callback: Callable[[AsyncResult[ChangeSetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='changeSet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.mode is not None:
            body["mode"] = request.mode
        if request.template is not None:
            body["template"] = request.template
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ChangeSetResult,
                callback=callback,
                body=body,
            )
        )

    def change_set(
        self,
        request: ChangeSetRequest,
    ) -> ChangeSetResult:
        async_result = []
        with timeout(30):
            self._change_set(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def change_set_async(
        self,
        request: ChangeSetRequest,
    ) -> ChangeSetResult:
        async_result = []
        self._change_set(
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

    def _update_stack_from_git_hub(
        self,
        request: UpdateStackFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateStackFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='updateStackFromGitHub',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.description is not None:
            body["description"] = request.description
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateStackFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_stack_from_git_hub(
        self,
        request: UpdateStackFromGitHubRequest,
    ) -> UpdateStackFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_stack_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_stack_from_git_hub_async(
        self,
        request: UpdateStackFromGitHubRequest,
    ) -> UpdateStackFromGitHubResult:
        async_result = []
        self._update_stack_from_git_hub(
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

    def _delete_stack(
        self,
        request: DeleteStackRequest,
        callback: Callable[[AsyncResult[DeleteStackResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='deleteStack',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteStackResult,
                callback=callback,
                body=body,
            )
        )

    def delete_stack(
        self,
        request: DeleteStackRequest,
    ) -> DeleteStackResult:
        async_result = []
        with timeout(30):
            self._delete_stack(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_stack_async(
        self,
        request: DeleteStackRequest,
    ) -> DeleteStackResult:
        async_result = []
        self._delete_stack(
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

    def _force_delete_stack(
        self,
        request: ForceDeleteStackRequest,
        callback: Callable[[AsyncResult[ForceDeleteStackResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='forceDeleteStack',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ForceDeleteStackResult,
                callback=callback,
                body=body,
            )
        )

    def force_delete_stack(
        self,
        request: ForceDeleteStackRequest,
    ) -> ForceDeleteStackResult:
        async_result = []
        with timeout(30):
            self._force_delete_stack(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def force_delete_stack_async(
        self,
        request: ForceDeleteStackRequest,
    ) -> ForceDeleteStackResult:
        async_result = []
        self._force_delete_stack(
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

    def _delete_stack_resources(
        self,
        request: DeleteStackResourcesRequest,
        callback: Callable[[AsyncResult[DeleteStackResourcesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='deleteStackResources',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteStackResourcesResult,
                callback=callback,
                body=body,
            )
        )

    def delete_stack_resources(
        self,
        request: DeleteStackResourcesRequest,
    ) -> DeleteStackResourcesResult:
        async_result = []
        with timeout(30):
            self._delete_stack_resources(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_stack_resources_async(
        self,
        request: DeleteStackResourcesRequest,
    ) -> DeleteStackResourcesResult:
        async_result = []
        self._delete_stack_resources(
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

    def _delete_stack_entity(
        self,
        request: DeleteStackEntityRequest,
        callback: Callable[[AsyncResult[DeleteStackEntityResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='stack',
            function='deleteStackEntity',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteStackEntityResult,
                callback=callback,
                body=body,
            )
        )

    def delete_stack_entity(
        self,
        request: DeleteStackEntityRequest,
    ) -> DeleteStackEntityResult:
        async_result = []
        with timeout(30):
            self._delete_stack_entity(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_stack_entity_async(
        self,
        request: DeleteStackEntityRequest,
    ) -> DeleteStackEntityResult:
        async_result = []
        self._delete_stack_entity(
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
            service="deploy",
            component='stack',
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

    def _describe_resources(
        self,
        request: DescribeResourcesRequest,
        callback: Callable[[AsyncResult[DescribeResourcesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='resource',
            function='describeResources',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeResourcesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_resources(
        self,
        request: DescribeResourcesRequest,
    ) -> DescribeResourcesResult:
        async_result = []
        with timeout(30):
            self._describe_resources(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_resources_async(
        self,
        request: DescribeResourcesRequest,
    ) -> DescribeResourcesResult:
        async_result = []
        self._describe_resources(
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

    def _get_resource(
        self,
        request: GetResourceRequest,
        callback: Callable[[AsyncResult[GetResourceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='resource',
            function='getResource',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.resource_name is not None:
            body["resourceName"] = request.resource_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetResourceResult,
                callback=callback,
                body=body,
            )
        )

    def get_resource(
        self,
        request: GetResourceRequest,
    ) -> GetResourceResult:
        async_result = []
        with timeout(30):
            self._get_resource(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_resource_async(
        self,
        request: GetResourceRequest,
    ) -> GetResourceResult:
        async_result = []
        self._get_resource(
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

    def _describe_events(
        self,
        request: DescribeEventsRequest,
        callback: Callable[[AsyncResult[DescribeEventsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='event',
            function='describeEvents',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeEventsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_events(
        self,
        request: DescribeEventsRequest,
    ) -> DescribeEventsResult:
        async_result = []
        with timeout(30):
            self._describe_events(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_events_async(
        self,
        request: DescribeEventsRequest,
    ) -> DescribeEventsResult:
        async_result = []
        self._describe_events(
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

    def _get_event(
        self,
        request: GetEventRequest,
        callback: Callable[[AsyncResult[GetEventResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='event',
            function='getEvent',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.event_name is not None:
            body["eventName"] = request.event_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetEventResult,
                callback=callback,
                body=body,
            )
        )

    def get_event(
        self,
        request: GetEventRequest,
    ) -> GetEventResult:
        async_result = []
        with timeout(30):
            self._get_event(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_event_async(
        self,
        request: GetEventRequest,
    ) -> GetEventResult:
        async_result = []
        self._get_event(
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

    def _describe_outputs(
        self,
        request: DescribeOutputsRequest,
        callback: Callable[[AsyncResult[DescribeOutputsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='output',
            function='describeOutputs',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeOutputsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_outputs(
        self,
        request: DescribeOutputsRequest,
    ) -> DescribeOutputsResult:
        async_result = []
        with timeout(30):
            self._describe_outputs(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_outputs_async(
        self,
        request: DescribeOutputsRequest,
    ) -> DescribeOutputsResult:
        async_result = []
        self._describe_outputs(
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

    def _get_output(
        self,
        request: GetOutputRequest,
        callback: Callable[[AsyncResult[GetOutputResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="deploy",
            component='output',
            function='getOutput',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stack_name is not None:
            body["stackName"] = request.stack_name
        if request.output_name is not None:
            body["outputName"] = request.output_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetOutputResult,
                callback=callback,
                body=body,
            )
        )

    def get_output(
        self,
        request: GetOutputRequest,
    ) -> GetOutputResult:
        async_result = []
        with timeout(30):
            self._get_output(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_output_async(
        self,
        request: GetOutputRequest,
    ) -> GetOutputResult:
        async_result = []
        self._get_output(
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