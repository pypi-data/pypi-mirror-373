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


class Gs2FreezeRestClient(rest.AbstractGs2RestClient):

    def _describe_stages(
        self,
        request: DescribeStagesRequest,
        callback: Callable[[AsyncResult[DescribeStagesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='freeze',
            region=self.session.region,
        ) + "/"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeStagesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_stages(
        self,
        request: DescribeStagesRequest,
    ) -> DescribeStagesResult:
        async_result = []
        with timeout(30):
            self._describe_stages(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_stages_async(
        self,
        request: DescribeStagesRequest,
    ) -> DescribeStagesResult:
        async_result = []
        self._describe_stages(
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

    def _get_stage(
        self,
        request: GetStageRequest,
        callback: Callable[[AsyncResult[GetStageResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='freeze',
            region=self.session.region,
        ) + "/{stageName}".format(
            stageName=request.stage_name if request.stage_name is not None and request.stage_name != '' else 'null',
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
            result_type=GetStageResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_stage(
        self,
        request: GetStageRequest,
    ) -> GetStageResult:
        async_result = []
        with timeout(30):
            self._get_stage(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stage_async(
        self,
        request: GetStageRequest,
    ) -> GetStageResult:
        async_result = []
        self._get_stage(
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

    def _promote_stage(
        self,
        request: PromoteStageRequest,
        callback: Callable[[AsyncResult[PromoteStageResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='freeze',
            region=self.session.region,
        ) + "/{stageName}/promote".format(
            stageName=request.stage_name if request.stage_name is not None and request.stage_name != '' else 'null',
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
            result_type=PromoteStageResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def promote_stage(
        self,
        request: PromoteStageRequest,
    ) -> PromoteStageResult:
        async_result = []
        with timeout(30):
            self._promote_stage(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def promote_stage_async(
        self,
        request: PromoteStageRequest,
    ) -> PromoteStageResult:
        async_result = []
        self._promote_stage(
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

    def _rollback_stage(
        self,
        request: RollbackStageRequest,
        callback: Callable[[AsyncResult[RollbackStageResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='freeze',
            region=self.session.region,
        ) + "/{stageName}/rollback".format(
            stageName=request.stage_name if request.stage_name is not None and request.stage_name != '' else 'null',
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
            result_type=RollbackStageResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def rollback_stage(
        self,
        request: RollbackStageRequest,
    ) -> RollbackStageResult:
        async_result = []
        with timeout(30):
            self._rollback_stage(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def rollback_stage_async(
        self,
        request: RollbackStageRequest,
    ) -> RollbackStageResult:
        async_result = []
        self._rollback_stage(
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
            service='freeze',
            region=self.session.region,
        ) + "/{stageName}/progress/output".format(
            stageName=request.stage_name if request.stage_name is not None and request.stage_name != '' else 'null',
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
            service='freeze',
            region=self.session.region,
        ) + "/{stageName}/progress/output/{outputName}".format(
            stageName=request.stage_name if request.stage_name is not None and request.stage_name != '' else 'null',
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