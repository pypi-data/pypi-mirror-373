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


class Gs2DeployRestClient(rest.AbstractGs2RestClient):

    def _describe_stacks(
        self,
        request: DescribeStacksRequest,
        callback: Callable[[AsyncResult[DescribeStacksResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack"

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
            result_type=DescribeStacksResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/pre"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=PreCreateStackResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        if request.template is not None:
            res = self.pre_create_stack(
                PreCreateStackRequest() \
                    .with_context_stack(request.context_stack) \
            )
            import requests
            requests.put(res.upload_url, data=request.template, headers={
                'Content-Type': 'application/json',
            })
            request.mode = "preUpload"
            request.upload_token = res.upload_token
            request.template = None

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateStackResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/from_git_hub"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateStackFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/validate/pre"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=PreValidateResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        if request.template is not None:
            res = self.pre_validate(
                PreValidateRequest() \
                    .with_context_stack(request.context_stack) \
            )
            import requests
            requests.put(res.upload_url, data=request.template, headers={
                'Content-Type': 'application/json',
            })
            request.mode = "preUpload"
            request.upload_token = res.upload_token
            request.template = None

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/validate"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.mode is not None:
            body["mode"] = request.mode
        if request.template is not None:
            body["template"] = request.template
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ValidateResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/status".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=GetStackStatusResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=GetStackResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/pre".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=PreUpdateStackResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        if request.template is not None:
            res = self.pre_update_stack(
                PreUpdateStackRequest() \
                    .with_context_stack(request.context_stack) \
                    .with_stack_name(request.stack_name)
            )
            import requests
            requests.put(res.upload_url, data=request.template, headers={
                'Content-Type': 'application/json',
            })
            request.mode = "preUpload"
            request.upload_token = res.upload_token
            request.template = None

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.mode is not None:
            body["mode"] = request.mode
        if request.template is not None:
            body["template"] = request.template
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateStackResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/pre".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=PreChangeSetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        if request.template is not None:
            res = self.pre_change_set(
                PreChangeSetRequest() \
                    .with_context_stack(request.context_stack) \
                    .with_stack_name(request.stack_name)
            )
            import requests
            requests.put(res.upload_url, data=request.template, headers={
                'Content-Type': 'application/json',
            })
            request.mode = "preUpload"
            request.upload_token = res.upload_token
            request.template = None

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.mode is not None:
            body["mode"] = request.mode
        if request.template is not None:
            body["template"] = request.template
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ChangeSetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/from_git_hub".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateStackFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=DeleteStackResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/force".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=ForceDeleteStackResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/resources".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=DeleteStackResourcesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/entity".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=DeleteStackEntityResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            service='deploy',
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

    def _describe_resources(
        self,
        request: DescribeResourcesRequest,
        callback: Callable[[AsyncResult[DescribeResourcesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/resource".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=DescribeResourcesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/resource/{resourceName}".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
            resourceName=request.resource_name if request.resource_name is not None and request.resource_name != '' else 'null',
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
            result_type=GetResourceResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/event".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=DescribeEventsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/event/{eventName}".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
            eventName=request.event_name if request.event_name is not None and request.event_name != '' else 'null',
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
            result_type=GetEventResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/output".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
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
            result_type=DescribeOutputsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='deploy',
            region=self.session.region,
        ) + "/stack/{stackName}/output/{outputName}".format(
            stackName=request.stack_name if request.stack_name is not None and request.stack_name != '' else 'null',
            outputName=request.output_name if request.output_name is not None and request.output_name != '' else 'null',
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
            result_type=GetOutputResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result