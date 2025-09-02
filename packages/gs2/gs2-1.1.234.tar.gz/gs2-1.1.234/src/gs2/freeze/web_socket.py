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


class Gs2FreezeWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_stages(
        self,
        request: DescribeStagesRequest,
        callback: Callable[[AsyncResult[DescribeStagesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="freeze",
            component='stage',
            function='describeStages',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeStagesResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="freeze",
            component='stage',
            function='getStage',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stage_name is not None:
            body["stageName"] = request.stage_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStageResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="freeze",
            component='stage',
            function='promoteStage',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stage_name is not None:
            body["stageName"] = request.stage_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PromoteStageResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="freeze",
            component='stage',
            function='rollbackStage',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stage_name is not None:
            body["stageName"] = request.stage_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=RollbackStageResult,
                callback=callback,
                body=body,
            )
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
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

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
            service="freeze",
            component='output',
            function='describeOutputs',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stage_name is not None:
            body["stageName"] = request.stage_name
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
            service="freeze",
            component='output',
            function='getOutput',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stage_name is not None:
            body["stageName"] = request.stage_name
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