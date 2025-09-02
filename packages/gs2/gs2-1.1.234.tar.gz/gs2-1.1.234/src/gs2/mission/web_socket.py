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


class Gs2MissionWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_completes(
        self,
        request: DescribeCompletesRequest,
        callback: Callable[[AsyncResult[DescribeCompletesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='describeCompletes',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeCompletesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_completes(
        self,
        request: DescribeCompletesRequest,
    ) -> DescribeCompletesResult:
        async_result = []
        with timeout(30):
            self._describe_completes(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_completes_async(
        self,
        request: DescribeCompletesRequest,
    ) -> DescribeCompletesResult:
        async_result = []
        self._describe_completes(
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

    def _describe_completes_by_user_id(
        self,
        request: DescribeCompletesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeCompletesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='describeCompletesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeCompletesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_completes_by_user_id(
        self,
        request: DescribeCompletesByUserIdRequest,
    ) -> DescribeCompletesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_completes_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_completes_by_user_id_async(
        self,
        request: DescribeCompletesByUserIdRequest,
    ) -> DescribeCompletesByUserIdResult:
        async_result = []
        self._describe_completes_by_user_id(
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

    def _complete(
        self,
        request: CompleteRequest,
        callback: Callable[[AsyncResult[CompleteResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='complete',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CompleteResult,
                callback=callback,
                body=body,
            )
        )

    def complete(
        self,
        request: CompleteRequest,
    ) -> CompleteResult:
        async_result = []
        with timeout(30):
            self._complete(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def complete_async(
        self,
        request: CompleteRequest,
    ) -> CompleteResult:
        async_result = []
        self._complete(
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

    def _complete_by_user_id(
        self,
        request: CompleteByUserIdRequest,
        callback: Callable[[AsyncResult[CompleteByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='completeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CompleteByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def complete_by_user_id(
        self,
        request: CompleteByUserIdRequest,
    ) -> CompleteByUserIdResult:
        async_result = []
        with timeout(30):
            self._complete_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def complete_by_user_id_async(
        self,
        request: CompleteByUserIdRequest,
    ) -> CompleteByUserIdResult:
        async_result = []
        self._complete_by_user_id(
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

    def _batch_complete(
        self,
        request: BatchCompleteRequest,
        callback: Callable[[AsyncResult[BatchCompleteResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='batchComplete',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mission_task_names is not None:
            body["missionTaskNames"] = [
                item
                for item in request.mission_task_names
            ]
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=BatchCompleteResult,
                callback=callback,
                body=body,
            )
        )

    def batch_complete(
        self,
        request: BatchCompleteRequest,
    ) -> BatchCompleteResult:
        async_result = []
        with timeout(30):
            self._batch_complete(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def batch_complete_async(
        self,
        request: BatchCompleteRequest,
    ) -> BatchCompleteResult:
        async_result = []
        self._batch_complete(
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

    def _batch_complete_by_user_id(
        self,
        request: BatchCompleteByUserIdRequest,
        callback: Callable[[AsyncResult[BatchCompleteByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='batchCompleteByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mission_task_names is not None:
            body["missionTaskNames"] = [
                item
                for item in request.mission_task_names
            ]
        if request.config is not None:
            body["config"] = [
                item.to_dict()
                for item in request.config
            ]
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=BatchCompleteByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def batch_complete_by_user_id(
        self,
        request: BatchCompleteByUserIdRequest,
    ) -> BatchCompleteByUserIdResult:
        async_result = []
        with timeout(30):
            self._batch_complete_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def batch_complete_by_user_id_async(
        self,
        request: BatchCompleteByUserIdRequest,
    ) -> BatchCompleteByUserIdResult:
        async_result = []
        self._batch_complete_by_user_id(
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

    def _receive_by_user_id(
        self,
        request: ReceiveByUserIdRequest,
        callback: Callable[[AsyncResult[ReceiveByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='receiveByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name
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
                result_type=ReceiveByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def receive_by_user_id(
        self,
        request: ReceiveByUserIdRequest,
    ) -> ReceiveByUserIdResult:
        async_result = []
        with timeout(30):
            self._receive_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def receive_by_user_id_async(
        self,
        request: ReceiveByUserIdRequest,
    ) -> ReceiveByUserIdResult:
        async_result = []
        self._receive_by_user_id(
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

    def _batch_receive_by_user_id(
        self,
        request: BatchReceiveByUserIdRequest,
        callback: Callable[[AsyncResult[BatchReceiveByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='batchReceiveByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mission_task_names is not None:
            body["missionTaskNames"] = [
                item
                for item in request.mission_task_names
            ]
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=BatchReceiveByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def batch_receive_by_user_id(
        self,
        request: BatchReceiveByUserIdRequest,
    ) -> BatchReceiveByUserIdResult:
        async_result = []
        with timeout(30):
            self._batch_receive_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def batch_receive_by_user_id_async(
        self,
        request: BatchReceiveByUserIdRequest,
    ) -> BatchReceiveByUserIdResult:
        async_result = []
        self._batch_receive_by_user_id(
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

    def _revert_receive_by_user_id(
        self,
        request: RevertReceiveByUserIdRequest,
        callback: Callable[[AsyncResult[RevertReceiveByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='revertReceiveByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name
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
                result_type=RevertReceiveByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def revert_receive_by_user_id(
        self,
        request: RevertReceiveByUserIdRequest,
    ) -> RevertReceiveByUserIdResult:
        async_result = []
        with timeout(30):
            self._revert_receive_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def revert_receive_by_user_id_async(
        self,
        request: RevertReceiveByUserIdRequest,
    ) -> RevertReceiveByUserIdResult:
        async_result = []
        self._revert_receive_by_user_id(
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

    def _get_complete(
        self,
        request: GetCompleteRequest,
        callback: Callable[[AsyncResult[GetCompleteResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='getComplete',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCompleteResult,
                callback=callback,
                body=body,
            )
        )

    def get_complete(
        self,
        request: GetCompleteRequest,
    ) -> GetCompleteResult:
        async_result = []
        with timeout(30):
            self._get_complete(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_complete_async(
        self,
        request: GetCompleteRequest,
    ) -> GetCompleteResult:
        async_result = []
        self._get_complete(
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

    def _get_complete_by_user_id(
        self,
        request: GetCompleteByUserIdRequest,
        callback: Callable[[AsyncResult[GetCompleteByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='getCompleteByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCompleteByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_complete_by_user_id(
        self,
        request: GetCompleteByUserIdRequest,
    ) -> GetCompleteByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_complete_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_complete_by_user_id_async(
        self,
        request: GetCompleteByUserIdRequest,
    ) -> GetCompleteByUserIdResult:
        async_result = []
        self._get_complete_by_user_id(
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

    def _evaluate_complete(
        self,
        request: EvaluateCompleteRequest,
        callback: Callable[[AsyncResult[EvaluateCompleteResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='evaluateComplete',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=EvaluateCompleteResult,
                callback=callback,
                body=body,
            )
        )

    def evaluate_complete(
        self,
        request: EvaluateCompleteRequest,
    ) -> EvaluateCompleteResult:
        async_result = []
        with timeout(30):
            self._evaluate_complete(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def evaluate_complete_async(
        self,
        request: EvaluateCompleteRequest,
    ) -> EvaluateCompleteResult:
        async_result = []
        self._evaluate_complete(
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

    def _evaluate_complete_by_user_id(
        self,
        request: EvaluateCompleteByUserIdRequest,
        callback: Callable[[AsyncResult[EvaluateCompleteByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='evaluateCompleteByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=EvaluateCompleteByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def evaluate_complete_by_user_id(
        self,
        request: EvaluateCompleteByUserIdRequest,
    ) -> EvaluateCompleteByUserIdResult:
        async_result = []
        with timeout(30):
            self._evaluate_complete_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def evaluate_complete_by_user_id_async(
        self,
        request: EvaluateCompleteByUserIdRequest,
    ) -> EvaluateCompleteByUserIdResult:
        async_result = []
        self._evaluate_complete_by_user_id(
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

    def _delete_complete_by_user_id(
        self,
        request: DeleteCompleteByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteCompleteByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='deleteCompleteByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteCompleteByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_complete_by_user_id(
        self,
        request: DeleteCompleteByUserIdRequest,
    ) -> DeleteCompleteByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_complete_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_complete_by_user_id_async(
        self,
        request: DeleteCompleteByUserIdRequest,
    ) -> DeleteCompleteByUserIdResult:
        async_result = []
        self._delete_complete_by_user_id(
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

    def _verify_complete(
        self,
        request: VerifyCompleteRequest,
        callback: Callable[[AsyncResult[VerifyCompleteResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='verifyComplete',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyCompleteResult,
                callback=callback,
                body=body,
            )
        )

    def verify_complete(
        self,
        request: VerifyCompleteRequest,
    ) -> VerifyCompleteResult:
        async_result = []
        with timeout(30):
            self._verify_complete(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_complete_async(
        self,
        request: VerifyCompleteRequest,
    ) -> VerifyCompleteResult:
        async_result = []
        self._verify_complete(
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

    def _verify_complete_by_user_id(
        self,
        request: VerifyCompleteByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyCompleteByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='verifyCompleteByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyCompleteByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_complete_by_user_id(
        self,
        request: VerifyCompleteByUserIdRequest,
    ) -> VerifyCompleteByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_complete_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_complete_by_user_id_async(
        self,
        request: VerifyCompleteByUserIdRequest,
    ) -> VerifyCompleteByUserIdResult:
        async_result = []
        self._verify_complete_by_user_id(
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

    def _receive_by_stamp_task(
        self,
        request: ReceiveByStampTaskRequest,
        callback: Callable[[AsyncResult[ReceiveByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='receiveByStampTask',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ReceiveByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def receive_by_stamp_task(
        self,
        request: ReceiveByStampTaskRequest,
    ) -> ReceiveByStampTaskResult:
        async_result = []
        with timeout(30):
            self._receive_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def receive_by_stamp_task_async(
        self,
        request: ReceiveByStampTaskRequest,
    ) -> ReceiveByStampTaskResult:
        async_result = []
        self._receive_by_stamp_task(
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

    def _batch_receive_by_stamp_task(
        self,
        request: BatchReceiveByStampTaskRequest,
        callback: Callable[[AsyncResult[BatchReceiveByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='batchReceiveByStampTask',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=BatchReceiveByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def batch_receive_by_stamp_task(
        self,
        request: BatchReceiveByStampTaskRequest,
    ) -> BatchReceiveByStampTaskResult:
        async_result = []
        with timeout(30):
            self._batch_receive_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def batch_receive_by_stamp_task_async(
        self,
        request: BatchReceiveByStampTaskRequest,
    ) -> BatchReceiveByStampTaskResult:
        async_result = []
        self._batch_receive_by_stamp_task(
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

    def _revert_receive_by_stamp_sheet(
        self,
        request: RevertReceiveByStampSheetRequest,
        callback: Callable[[AsyncResult[RevertReceiveByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='revertReceiveByStampSheet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=RevertReceiveByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def revert_receive_by_stamp_sheet(
        self,
        request: RevertReceiveByStampSheetRequest,
    ) -> RevertReceiveByStampSheetResult:
        async_result = []
        with timeout(30):
            self._revert_receive_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def revert_receive_by_stamp_sheet_async(
        self,
        request: RevertReceiveByStampSheetRequest,
    ) -> RevertReceiveByStampSheetResult:
        async_result = []
        self._revert_receive_by_stamp_sheet(
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

    def _verify_complete_by_stamp_task(
        self,
        request: VerifyCompleteByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyCompleteByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='complete',
            function='verifyCompleteByStampTask',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyCompleteByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_complete_by_stamp_task(
        self,
        request: VerifyCompleteByStampTaskRequest,
    ) -> VerifyCompleteByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_complete_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_complete_by_stamp_task_async(
        self,
        request: VerifyCompleteByStampTaskRequest,
    ) -> VerifyCompleteByStampTaskResult:
        async_result = []
        self._verify_complete_by_stamp_task(
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

    def _describe_counter_model_masters(
        self,
        request: DescribeCounterModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeCounterModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counterModelMaster',
            function='describeCounterModelMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeCounterModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_counter_model_masters(
        self,
        request: DescribeCounterModelMastersRequest,
    ) -> DescribeCounterModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_counter_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_counter_model_masters_async(
        self,
        request: DescribeCounterModelMastersRequest,
    ) -> DescribeCounterModelMastersResult:
        async_result = []
        self._describe_counter_model_masters(
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

    def _create_counter_model_master(
        self,
        request: CreateCounterModelMasterRequest,
        callback: Callable[[AsyncResult[CreateCounterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counterModelMaster',
            function='createCounterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.description is not None:
            body["description"] = request.description
        if request.scopes is not None:
            body["scopes"] = [
                item.to_dict()
                for item in request.scopes
            ]
        if request.challenge_period_event_id is not None:
            body["challengePeriodEventId"] = request.challenge_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateCounterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_counter_model_master(
        self,
        request: CreateCounterModelMasterRequest,
    ) -> CreateCounterModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_counter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_counter_model_master_async(
        self,
        request: CreateCounterModelMasterRequest,
    ) -> CreateCounterModelMasterResult:
        async_result = []
        self._create_counter_model_master(
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

    def _get_counter_model_master(
        self,
        request: GetCounterModelMasterRequest,
        callback: Callable[[AsyncResult[GetCounterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counterModelMaster',
            function='getCounterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCounterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_counter_model_master(
        self,
        request: GetCounterModelMasterRequest,
    ) -> GetCounterModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_counter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_counter_model_master_async(
        self,
        request: GetCounterModelMasterRequest,
    ) -> GetCounterModelMasterResult:
        async_result = []
        self._get_counter_model_master(
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

    def _update_counter_model_master(
        self,
        request: UpdateCounterModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateCounterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counterModelMaster',
            function='updateCounterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.description is not None:
            body["description"] = request.description
        if request.scopes is not None:
            body["scopes"] = [
                item.to_dict()
                for item in request.scopes
            ]
        if request.challenge_period_event_id is not None:
            body["challengePeriodEventId"] = request.challenge_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateCounterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_counter_model_master(
        self,
        request: UpdateCounterModelMasterRequest,
    ) -> UpdateCounterModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_counter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_counter_model_master_async(
        self,
        request: UpdateCounterModelMasterRequest,
    ) -> UpdateCounterModelMasterResult:
        async_result = []
        self._update_counter_model_master(
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

    def _delete_counter_model_master(
        self,
        request: DeleteCounterModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteCounterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counterModelMaster',
            function='deleteCounterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteCounterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_counter_model_master(
        self,
        request: DeleteCounterModelMasterRequest,
    ) -> DeleteCounterModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_counter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_counter_model_master_async(
        self,
        request: DeleteCounterModelMasterRequest,
    ) -> DeleteCounterModelMasterResult:
        async_result = []
        self._delete_counter_model_master(
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

    def _describe_mission_group_model_masters(
        self,
        request: DescribeMissionGroupModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeMissionGroupModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionGroupModelMaster',
            function='describeMissionGroupModelMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeMissionGroupModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_mission_group_model_masters(
        self,
        request: DescribeMissionGroupModelMastersRequest,
    ) -> DescribeMissionGroupModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_mission_group_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_mission_group_model_masters_async(
        self,
        request: DescribeMissionGroupModelMastersRequest,
    ) -> DescribeMissionGroupModelMastersResult:
        async_result = []
        self._describe_mission_group_model_masters(
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

    def _create_mission_group_model_master(
        self,
        request: CreateMissionGroupModelMasterRequest,
        callback: Callable[[AsyncResult[CreateMissionGroupModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionGroupModelMaster',
            function='createMissionGroupModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.description is not None:
            body["description"] = request.description
        if request.reset_type is not None:
            body["resetType"] = request.reset_type
        if request.reset_day_of_month is not None:
            body["resetDayOfMonth"] = request.reset_day_of_month
        if request.reset_day_of_week is not None:
            body["resetDayOfWeek"] = request.reset_day_of_week
        if request.reset_hour is not None:
            body["resetHour"] = request.reset_hour
        if request.anchor_timestamp is not None:
            body["anchorTimestamp"] = request.anchor_timestamp
        if request.days is not None:
            body["days"] = request.days
        if request.complete_notification_namespace_id is not None:
            body["completeNotificationNamespaceId"] = request.complete_notification_namespace_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateMissionGroupModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_mission_group_model_master(
        self,
        request: CreateMissionGroupModelMasterRequest,
    ) -> CreateMissionGroupModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_mission_group_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_mission_group_model_master_async(
        self,
        request: CreateMissionGroupModelMasterRequest,
    ) -> CreateMissionGroupModelMasterResult:
        async_result = []
        self._create_mission_group_model_master(
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

    def _get_mission_group_model_master(
        self,
        request: GetMissionGroupModelMasterRequest,
        callback: Callable[[AsyncResult[GetMissionGroupModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionGroupModelMaster',
            function='getMissionGroupModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMissionGroupModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_mission_group_model_master(
        self,
        request: GetMissionGroupModelMasterRequest,
    ) -> GetMissionGroupModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_mission_group_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_mission_group_model_master_async(
        self,
        request: GetMissionGroupModelMasterRequest,
    ) -> GetMissionGroupModelMasterResult:
        async_result = []
        self._get_mission_group_model_master(
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

    def _update_mission_group_model_master(
        self,
        request: UpdateMissionGroupModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateMissionGroupModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionGroupModelMaster',
            function='updateMissionGroupModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.description is not None:
            body["description"] = request.description
        if request.reset_type is not None:
            body["resetType"] = request.reset_type
        if request.reset_day_of_month is not None:
            body["resetDayOfMonth"] = request.reset_day_of_month
        if request.reset_day_of_week is not None:
            body["resetDayOfWeek"] = request.reset_day_of_week
        if request.reset_hour is not None:
            body["resetHour"] = request.reset_hour
        if request.anchor_timestamp is not None:
            body["anchorTimestamp"] = request.anchor_timestamp
        if request.days is not None:
            body["days"] = request.days
        if request.complete_notification_namespace_id is not None:
            body["completeNotificationNamespaceId"] = request.complete_notification_namespace_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateMissionGroupModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_mission_group_model_master(
        self,
        request: UpdateMissionGroupModelMasterRequest,
    ) -> UpdateMissionGroupModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_mission_group_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_mission_group_model_master_async(
        self,
        request: UpdateMissionGroupModelMasterRequest,
    ) -> UpdateMissionGroupModelMasterResult:
        async_result = []
        self._update_mission_group_model_master(
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

    def _delete_mission_group_model_master(
        self,
        request: DeleteMissionGroupModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteMissionGroupModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionGroupModelMaster',
            function='deleteMissionGroupModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteMissionGroupModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_mission_group_model_master(
        self,
        request: DeleteMissionGroupModelMasterRequest,
    ) -> DeleteMissionGroupModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_mission_group_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_mission_group_model_master_async(
        self,
        request: DeleteMissionGroupModelMasterRequest,
    ) -> DeleteMissionGroupModelMasterResult:
        async_result = []
        self._delete_mission_group_model_master(
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

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='describeNamespaces',
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
                result_type=DescribeNamespacesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
    ) -> DescribeNamespacesResult:
        async_result = []
        with timeout(30):
            self._describe_namespaces(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_namespaces_async(
        self,
        request: DescribeNamespacesRequest,
    ) -> DescribeNamespacesResult:
        async_result = []
        self._describe_namespaces(
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

    def _create_namespace(
        self,
        request: CreateNamespaceRequest,
        callback: Callable[[AsyncResult[CreateNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='createNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.transaction_setting is not None:
            body["transactionSetting"] = request.transaction_setting.to_dict()
        if request.mission_complete_script is not None:
            body["missionCompleteScript"] = request.mission_complete_script.to_dict()
        if request.counter_increment_script is not None:
            body["counterIncrementScript"] = request.counter_increment_script.to_dict()
        if request.receive_rewards_script is not None:
            body["receiveRewardsScript"] = request.receive_rewards_script.to_dict()
        if request.complete_notification is not None:
            body["completeNotification"] = request.complete_notification.to_dict()
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()
        if request.queue_namespace_id is not None:
            body["queueNamespaceId"] = request.queue_namespace_id
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def create_namespace(
        self,
        request: CreateNamespaceRequest,
    ) -> CreateNamespaceResult:
        async_result = []
        with timeout(30):
            self._create_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_namespace_async(
        self,
        request: CreateNamespaceRequest,
    ) -> CreateNamespaceResult:
        async_result = []
        self._create_namespace(
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

    def _get_namespace_status(
        self,
        request: GetNamespaceStatusRequest,
        callback: Callable[[AsyncResult[GetNamespaceStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='getNamespaceStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetNamespaceStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_namespace_status(
        self,
        request: GetNamespaceStatusRequest,
    ) -> GetNamespaceStatusResult:
        async_result = []
        with timeout(30):
            self._get_namespace_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_namespace_status_async(
        self,
        request: GetNamespaceStatusRequest,
    ) -> GetNamespaceStatusResult:
        async_result = []
        self._get_namespace_status(
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

    def _get_namespace(
        self,
        request: GetNamespaceRequest,
        callback: Callable[[AsyncResult[GetNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='getNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def get_namespace(
        self,
        request: GetNamespaceRequest,
    ) -> GetNamespaceResult:
        async_result = []
        with timeout(30):
            self._get_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_namespace_async(
        self,
        request: GetNamespaceRequest,
    ) -> GetNamespaceResult:
        async_result = []
        self._get_namespace(
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

    def _update_namespace(
        self,
        request: UpdateNamespaceRequest,
        callback: Callable[[AsyncResult[UpdateNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='updateNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.description is not None:
            body["description"] = request.description
        if request.transaction_setting is not None:
            body["transactionSetting"] = request.transaction_setting.to_dict()
        if request.mission_complete_script is not None:
            body["missionCompleteScript"] = request.mission_complete_script.to_dict()
        if request.counter_increment_script is not None:
            body["counterIncrementScript"] = request.counter_increment_script.to_dict()
        if request.receive_rewards_script is not None:
            body["receiveRewardsScript"] = request.receive_rewards_script.to_dict()
        if request.complete_notification is not None:
            body["completeNotification"] = request.complete_notification.to_dict()
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()
        if request.queue_namespace_id is not None:
            body["queueNamespaceId"] = request.queue_namespace_id
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def update_namespace(
        self,
        request: UpdateNamespaceRequest,
    ) -> UpdateNamespaceResult:
        async_result = []
        with timeout(30):
            self._update_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_namespace_async(
        self,
        request: UpdateNamespaceRequest,
    ) -> UpdateNamespaceResult:
        async_result = []
        self._update_namespace(
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

    def _delete_namespace(
        self,
        request: DeleteNamespaceRequest,
        callback: Callable[[AsyncResult[DeleteNamespaceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='deleteNamespace',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteNamespaceResult,
                callback=callback,
                body=body,
            )
        )

    def delete_namespace(
        self,
        request: DeleteNamespaceRequest,
    ) -> DeleteNamespaceResult:
        async_result = []
        with timeout(30):
            self._delete_namespace(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_namespace_async(
        self,
        request: DeleteNamespaceRequest,
    ) -> DeleteNamespaceResult:
        async_result = []
        self._delete_namespace(
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
            service="mission",
            component='namespace',
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

    def _dump_user_data_by_user_id(
        self,
        request: DumpUserDataByUserIdRequest,
        callback: Callable[[AsyncResult[DumpUserDataByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='dumpUserDataByUserId',
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

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DumpUserDataByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def dump_user_data_by_user_id(
        self,
        request: DumpUserDataByUserIdRequest,
    ) -> DumpUserDataByUserIdResult:
        async_result = []
        with timeout(30):
            self._dump_user_data_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def dump_user_data_by_user_id_async(
        self,
        request: DumpUserDataByUserIdRequest,
    ) -> DumpUserDataByUserIdResult:
        async_result = []
        self._dump_user_data_by_user_id(
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

    def _check_dump_user_data_by_user_id(
        self,
        request: CheckDumpUserDataByUserIdRequest,
        callback: Callable[[AsyncResult[CheckDumpUserDataByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='checkDumpUserDataByUserId',
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

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CheckDumpUserDataByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def check_dump_user_data_by_user_id(
        self,
        request: CheckDumpUserDataByUserIdRequest,
    ) -> CheckDumpUserDataByUserIdResult:
        async_result = []
        with timeout(30):
            self._check_dump_user_data_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def check_dump_user_data_by_user_id_async(
        self,
        request: CheckDumpUserDataByUserIdRequest,
    ) -> CheckDumpUserDataByUserIdResult:
        async_result = []
        self._check_dump_user_data_by_user_id(
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

    def _clean_user_data_by_user_id(
        self,
        request: CleanUserDataByUserIdRequest,
        callback: Callable[[AsyncResult[CleanUserDataByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='cleanUserDataByUserId',
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

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CleanUserDataByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def clean_user_data_by_user_id(
        self,
        request: CleanUserDataByUserIdRequest,
    ) -> CleanUserDataByUserIdResult:
        async_result = []
        with timeout(30):
            self._clean_user_data_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def clean_user_data_by_user_id_async(
        self,
        request: CleanUserDataByUserIdRequest,
    ) -> CleanUserDataByUserIdResult:
        async_result = []
        self._clean_user_data_by_user_id(
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

    def _check_clean_user_data_by_user_id(
        self,
        request: CheckCleanUserDataByUserIdRequest,
        callback: Callable[[AsyncResult[CheckCleanUserDataByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='checkCleanUserDataByUserId',
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

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CheckCleanUserDataByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def check_clean_user_data_by_user_id(
        self,
        request: CheckCleanUserDataByUserIdRequest,
    ) -> CheckCleanUserDataByUserIdResult:
        async_result = []
        with timeout(30):
            self._check_clean_user_data_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def check_clean_user_data_by_user_id_async(
        self,
        request: CheckCleanUserDataByUserIdRequest,
    ) -> CheckCleanUserDataByUserIdResult:
        async_result = []
        self._check_clean_user_data_by_user_id(
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

    def _prepare_import_user_data_by_user_id(
        self,
        request: PrepareImportUserDataByUserIdRequest,
        callback: Callable[[AsyncResult[PrepareImportUserDataByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='prepareImportUserDataByUserId',
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

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PrepareImportUserDataByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def prepare_import_user_data_by_user_id(
        self,
        request: PrepareImportUserDataByUserIdRequest,
    ) -> PrepareImportUserDataByUserIdResult:
        async_result = []
        with timeout(30):
            self._prepare_import_user_data_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def prepare_import_user_data_by_user_id_async(
        self,
        request: PrepareImportUserDataByUserIdRequest,
    ) -> PrepareImportUserDataByUserIdResult:
        async_result = []
        self._prepare_import_user_data_by_user_id(
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

    def _import_user_data_by_user_id(
        self,
        request: ImportUserDataByUserIdRequest,
        callback: Callable[[AsyncResult[ImportUserDataByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='importUserDataByUserId',
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

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ImportUserDataByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def import_user_data_by_user_id(
        self,
        request: ImportUserDataByUserIdRequest,
    ) -> ImportUserDataByUserIdResult:
        async_result = []
        with timeout(30):
            self._import_user_data_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def import_user_data_by_user_id_async(
        self,
        request: ImportUserDataByUserIdRequest,
    ) -> ImportUserDataByUserIdResult:
        async_result = []
        self._import_user_data_by_user_id(
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

    def _check_import_user_data_by_user_id(
        self,
        request: CheckImportUserDataByUserIdRequest,
        callback: Callable[[AsyncResult[CheckImportUserDataByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='namespace',
            function='checkImportUserDataByUserId',
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

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CheckImportUserDataByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def check_import_user_data_by_user_id(
        self,
        request: CheckImportUserDataByUserIdRequest,
    ) -> CheckImportUserDataByUserIdResult:
        async_result = []
        with timeout(30):
            self._check_import_user_data_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def check_import_user_data_by_user_id_async(
        self,
        request: CheckImportUserDataByUserIdRequest,
    ) -> CheckImportUserDataByUserIdResult:
        async_result = []
        self._check_import_user_data_by_user_id(
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

    def _describe_counters(
        self,
        request: DescribeCountersRequest,
        callback: Callable[[AsyncResult[DescribeCountersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='describeCounters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeCountersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_counters(
        self,
        request: DescribeCountersRequest,
    ) -> DescribeCountersResult:
        async_result = []
        with timeout(30):
            self._describe_counters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_counters_async(
        self,
        request: DescribeCountersRequest,
    ) -> DescribeCountersResult:
        async_result = []
        self._describe_counters(
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

    def _describe_counters_by_user_id(
        self,
        request: DescribeCountersByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeCountersByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='describeCountersByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeCountersByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_counters_by_user_id(
        self,
        request: DescribeCountersByUserIdRequest,
    ) -> DescribeCountersByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_counters_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_counters_by_user_id_async(
        self,
        request: DescribeCountersByUserIdRequest,
    ) -> DescribeCountersByUserIdResult:
        async_result = []
        self._describe_counters_by_user_id(
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

    def _increase_counter_by_user_id(
        self,
        request: IncreaseCounterByUserIdRequest,
        callback: Callable[[AsyncResult[IncreaseCounterByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='increaseCounterByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.value is not None:
            body["value"] = request.value
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=IncreaseCounterByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def increase_counter_by_user_id(
        self,
        request: IncreaseCounterByUserIdRequest,
    ) -> IncreaseCounterByUserIdResult:
        async_result = []
        with timeout(30):
            self._increase_counter_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def increase_counter_by_user_id_async(
        self,
        request: IncreaseCounterByUserIdRequest,
    ) -> IncreaseCounterByUserIdResult:
        async_result = []
        self._increase_counter_by_user_id(
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

    def _set_counter_by_user_id(
        self,
        request: SetCounterByUserIdRequest,
        callback: Callable[[AsyncResult[SetCounterByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='setCounterByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.values is not None:
            body["values"] = [
                item.to_dict()
                for item in request.values
            ]
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SetCounterByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_counter_by_user_id(
        self,
        request: SetCounterByUserIdRequest,
    ) -> SetCounterByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_counter_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_counter_by_user_id_async(
        self,
        request: SetCounterByUserIdRequest,
    ) -> SetCounterByUserIdResult:
        async_result = []
        self._set_counter_by_user_id(
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

    def _decrease_counter(
        self,
        request: DecreaseCounterRequest,
        callback: Callable[[AsyncResult[DecreaseCounterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='decreaseCounter',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.value is not None:
            body["value"] = request.value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DecreaseCounterResult,
                callback=callback,
                body=body,
            )
        )

    def decrease_counter(
        self,
        request: DecreaseCounterRequest,
    ) -> DecreaseCounterResult:
        async_result = []
        with timeout(30):
            self._decrease_counter(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_counter_async(
        self,
        request: DecreaseCounterRequest,
    ) -> DecreaseCounterResult:
        async_result = []
        self._decrease_counter(
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

    def _decrease_counter_by_user_id(
        self,
        request: DecreaseCounterByUserIdRequest,
        callback: Callable[[AsyncResult[DecreaseCounterByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='decreaseCounterByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.value is not None:
            body["value"] = request.value
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DecreaseCounterByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def decrease_counter_by_user_id(
        self,
        request: DecreaseCounterByUserIdRequest,
    ) -> DecreaseCounterByUserIdResult:
        async_result = []
        with timeout(30):
            self._decrease_counter_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_counter_by_user_id_async(
        self,
        request: DecreaseCounterByUserIdRequest,
    ) -> DecreaseCounterByUserIdResult:
        async_result = []
        self._decrease_counter_by_user_id(
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

    def _get_counter(
        self,
        request: GetCounterRequest,
        callback: Callable[[AsyncResult[GetCounterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='getCounter',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCounterResult,
                callback=callback,
                body=body,
            )
        )

    def get_counter(
        self,
        request: GetCounterRequest,
    ) -> GetCounterResult:
        async_result = []
        with timeout(30):
            self._get_counter(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_counter_async(
        self,
        request: GetCounterRequest,
    ) -> GetCounterResult:
        async_result = []
        self._get_counter(
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

    def _get_counter_by_user_id(
        self,
        request: GetCounterByUserIdRequest,
        callback: Callable[[AsyncResult[GetCounterByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='getCounterByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCounterByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_counter_by_user_id(
        self,
        request: GetCounterByUserIdRequest,
    ) -> GetCounterByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_counter_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_counter_by_user_id_async(
        self,
        request: GetCounterByUserIdRequest,
    ) -> GetCounterByUserIdResult:
        async_result = []
        self._get_counter_by_user_id(
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

    def _verify_counter_value(
        self,
        request: VerifyCounterValueRequest,
        callback: Callable[[AsyncResult[VerifyCounterValueResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='verifyCounterValue',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.scope_type is not None:
            body["scopeType"] = request.scope_type
        if request.reset_type is not None:
            body["resetType"] = request.reset_type
        if request.condition_name is not None:
            body["conditionName"] = request.condition_name
        if request.value is not None:
            body["value"] = request.value
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyCounterValueResult,
                callback=callback,
                body=body,
            )
        )

    def verify_counter_value(
        self,
        request: VerifyCounterValueRequest,
    ) -> VerifyCounterValueResult:
        async_result = []
        with timeout(30):
            self._verify_counter_value(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_counter_value_async(
        self,
        request: VerifyCounterValueRequest,
    ) -> VerifyCounterValueResult:
        async_result = []
        self._verify_counter_value(
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

    def _verify_counter_value_by_user_id(
        self,
        request: VerifyCounterValueByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyCounterValueByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='verifyCounterValueByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.scope_type is not None:
            body["scopeType"] = request.scope_type
        if request.reset_type is not None:
            body["resetType"] = request.reset_type
        if request.condition_name is not None:
            body["conditionName"] = request.condition_name
        if request.value is not None:
            body["value"] = request.value
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyCounterValueByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_counter_value_by_user_id(
        self,
        request: VerifyCounterValueByUserIdRequest,
    ) -> VerifyCounterValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_counter_value_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_counter_value_by_user_id_async(
        self,
        request: VerifyCounterValueByUserIdRequest,
    ) -> VerifyCounterValueByUserIdResult:
        async_result = []
        self._verify_counter_value_by_user_id(
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

    def _reset_counter(
        self,
        request: ResetCounterRequest,
        callback: Callable[[AsyncResult[ResetCounterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='resetCounter',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.scopes is not None:
            body["scopes"] = [
                item.to_dict()
                for item in request.scopes
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ResetCounterResult,
                callback=callback,
                body=body,
            )
        )

    def reset_counter(
        self,
        request: ResetCounterRequest,
    ) -> ResetCounterResult:
        async_result = []
        with timeout(30):
            self._reset_counter(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reset_counter_async(
        self,
        request: ResetCounterRequest,
    ) -> ResetCounterResult:
        async_result = []
        self._reset_counter(
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

    def _reset_counter_by_user_id(
        self,
        request: ResetCounterByUserIdRequest,
        callback: Callable[[AsyncResult[ResetCounterByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='resetCounterByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.scopes is not None:
            body["scopes"] = [
                item.to_dict()
                for item in request.scopes
            ]
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ResetCounterByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def reset_counter_by_user_id(
        self,
        request: ResetCounterByUserIdRequest,
    ) -> ResetCounterByUserIdResult:
        async_result = []
        with timeout(30):
            self._reset_counter_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reset_counter_by_user_id_async(
        self,
        request: ResetCounterByUserIdRequest,
    ) -> ResetCounterByUserIdResult:
        async_result = []
        self._reset_counter_by_user_id(
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

    def _delete_counter(
        self,
        request: DeleteCounterRequest,
        callback: Callable[[AsyncResult[DeleteCounterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='deleteCounter',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.counter_name is not None:
            body["counterName"] = request.counter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteCounterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_counter(
        self,
        request: DeleteCounterRequest,
    ) -> DeleteCounterResult:
        async_result = []
        with timeout(30):
            self._delete_counter(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_counter_async(
        self,
        request: DeleteCounterRequest,
    ) -> DeleteCounterResult:
        async_result = []
        self._delete_counter(
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

    def _delete_counter_by_user_id(
        self,
        request: DeleteCounterByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteCounterByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='deleteCounterByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteCounterByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_counter_by_user_id(
        self,
        request: DeleteCounterByUserIdRequest,
    ) -> DeleteCounterByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_counter_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_counter_by_user_id_async(
        self,
        request: DeleteCounterByUserIdRequest,
    ) -> DeleteCounterByUserIdResult:
        async_result = []
        self._delete_counter_by_user_id(
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

    def _increase_by_stamp_sheet(
        self,
        request: IncreaseByStampSheetRequest,
        callback: Callable[[AsyncResult[IncreaseByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='increaseByStampSheet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=IncreaseByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def increase_by_stamp_sheet(
        self,
        request: IncreaseByStampSheetRequest,
    ) -> IncreaseByStampSheetResult:
        async_result = []
        with timeout(30):
            self._increase_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def increase_by_stamp_sheet_async(
        self,
        request: IncreaseByStampSheetRequest,
    ) -> IncreaseByStampSheetResult:
        async_result = []
        self._increase_by_stamp_sheet(
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

    def _set_by_stamp_sheet(
        self,
        request: SetByStampSheetRequest,
        callback: Callable[[AsyncResult[SetByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='setByStampSheet',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SetByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_by_stamp_sheet(
        self,
        request: SetByStampSheetRequest,
    ) -> SetByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_by_stamp_sheet_async(
        self,
        request: SetByStampSheetRequest,
    ) -> SetByStampSheetResult:
        async_result = []
        self._set_by_stamp_sheet(
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

    def _decrease_by_stamp_task(
        self,
        request: DecreaseByStampTaskRequest,
        callback: Callable[[AsyncResult[DecreaseByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='decreaseByStampTask',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DecreaseByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def decrease_by_stamp_task(
        self,
        request: DecreaseByStampTaskRequest,
    ) -> DecreaseByStampTaskResult:
        async_result = []
        with timeout(30):
            self._decrease_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_by_stamp_task_async(
        self,
        request: DecreaseByStampTaskRequest,
    ) -> DecreaseByStampTaskResult:
        async_result = []
        self._decrease_by_stamp_task(
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

    def _reset_by_stamp_task(
        self,
        request: ResetByStampTaskRequest,
        callback: Callable[[AsyncResult[ResetByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='resetByStampTask',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ResetByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def reset_by_stamp_task(
        self,
        request: ResetByStampTaskRequest,
    ) -> ResetByStampTaskResult:
        async_result = []
        with timeout(30):
            self._reset_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reset_by_stamp_task_async(
        self,
        request: ResetByStampTaskRequest,
    ) -> ResetByStampTaskResult:
        async_result = []
        self._reset_by_stamp_task(
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

    def _verify_counter_value_by_stamp_task(
        self,
        request: VerifyCounterValueByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyCounterValueByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counter',
            function='verifyCounterValueByStampTask',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyCounterValueByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_counter_value_by_stamp_task(
        self,
        request: VerifyCounterValueByStampTaskRequest,
    ) -> VerifyCounterValueByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_counter_value_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_counter_value_by_stamp_task_async(
        self,
        request: VerifyCounterValueByStampTaskRequest,
    ) -> VerifyCounterValueByStampTaskResult:
        async_result = []
        self._verify_counter_value_by_stamp_task(
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

    def _export_master(
        self,
        request: ExportMasterRequest,
        callback: Callable[[AsyncResult[ExportMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='currentMissionMaster',
            function='exportMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ExportMasterResult,
                callback=callback,
                body=body,
            )
        )

    def export_master(
        self,
        request: ExportMasterRequest,
    ) -> ExportMasterResult:
        async_result = []
        with timeout(30):
            self._export_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def export_master_async(
        self,
        request: ExportMasterRequest,
    ) -> ExportMasterResult:
        async_result = []
        self._export_master(
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

    def _get_current_mission_master(
        self,
        request: GetCurrentMissionMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentMissionMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='currentMissionMaster',
            function='getCurrentMissionMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCurrentMissionMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_mission_master(
        self,
        request: GetCurrentMissionMasterRequest,
    ) -> GetCurrentMissionMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_mission_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_mission_master_async(
        self,
        request: GetCurrentMissionMasterRequest,
    ) -> GetCurrentMissionMasterResult:
        async_result = []
        self._get_current_mission_master(
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

    def _pre_update_current_mission_master(
        self,
        request: PreUpdateCurrentMissionMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentMissionMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='currentMissionMaster',
            function='preUpdateCurrentMissionMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PreUpdateCurrentMissionMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_mission_master(
        self,
        request: PreUpdateCurrentMissionMasterRequest,
    ) -> PreUpdateCurrentMissionMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_mission_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_mission_master_async(
        self,
        request: PreUpdateCurrentMissionMasterRequest,
    ) -> PreUpdateCurrentMissionMasterResult:
        async_result = []
        self._pre_update_current_mission_master(
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

    def _update_current_mission_master(
        self,
        request: UpdateCurrentMissionMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentMissionMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='currentMissionMaster',
            function='updateCurrentMissionMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mode is not None:
            body["mode"] = request.mode
        if request.settings is not None:
            body["settings"] = request.settings
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateCurrentMissionMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_mission_master(
        self,
        request: UpdateCurrentMissionMasterRequest,
    ) -> UpdateCurrentMissionMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_mission_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_mission_master_async(
        self,
        request: UpdateCurrentMissionMasterRequest,
    ) -> UpdateCurrentMissionMasterResult:
        async_result = []
        self._update_current_mission_master(
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

    def _update_current_mission_master_from_git_hub(
        self,
        request: UpdateCurrentMissionMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentMissionMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='currentMissionMaster',
            function='updateCurrentMissionMasterFromGitHub',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateCurrentMissionMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_mission_master_from_git_hub(
        self,
        request: UpdateCurrentMissionMasterFromGitHubRequest,
    ) -> UpdateCurrentMissionMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_mission_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_mission_master_from_git_hub_async(
        self,
        request: UpdateCurrentMissionMasterFromGitHubRequest,
    ) -> UpdateCurrentMissionMasterFromGitHubResult:
        async_result = []
        self._update_current_mission_master_from_git_hub(
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

    def _describe_counter_models(
        self,
        request: DescribeCounterModelsRequest,
        callback: Callable[[AsyncResult[DescribeCounterModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counterModel',
            function='describeCounterModels',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeCounterModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_counter_models(
        self,
        request: DescribeCounterModelsRequest,
    ) -> DescribeCounterModelsResult:
        async_result = []
        with timeout(30):
            self._describe_counter_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_counter_models_async(
        self,
        request: DescribeCounterModelsRequest,
    ) -> DescribeCounterModelsResult:
        async_result = []
        self._describe_counter_models(
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

    def _get_counter_model(
        self,
        request: GetCounterModelRequest,
        callback: Callable[[AsyncResult[GetCounterModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='counterModel',
            function='getCounterModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCounterModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_counter_model(
        self,
        request: GetCounterModelRequest,
    ) -> GetCounterModelResult:
        async_result = []
        with timeout(30):
            self._get_counter_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_counter_model_async(
        self,
        request: GetCounterModelRequest,
    ) -> GetCounterModelResult:
        async_result = []
        self._get_counter_model(
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

    def _describe_mission_group_models(
        self,
        request: DescribeMissionGroupModelsRequest,
        callback: Callable[[AsyncResult[DescribeMissionGroupModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionGroupModel',
            function='describeMissionGroupModels',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeMissionGroupModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_mission_group_models(
        self,
        request: DescribeMissionGroupModelsRequest,
    ) -> DescribeMissionGroupModelsResult:
        async_result = []
        with timeout(30):
            self._describe_mission_group_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_mission_group_models_async(
        self,
        request: DescribeMissionGroupModelsRequest,
    ) -> DescribeMissionGroupModelsResult:
        async_result = []
        self._describe_mission_group_models(
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

    def _get_mission_group_model(
        self,
        request: GetMissionGroupModelRequest,
        callback: Callable[[AsyncResult[GetMissionGroupModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionGroupModel',
            function='getMissionGroupModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMissionGroupModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_mission_group_model(
        self,
        request: GetMissionGroupModelRequest,
    ) -> GetMissionGroupModelResult:
        async_result = []
        with timeout(30):
            self._get_mission_group_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_mission_group_model_async(
        self,
        request: GetMissionGroupModelRequest,
    ) -> GetMissionGroupModelResult:
        async_result = []
        self._get_mission_group_model(
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

    def _describe_mission_task_models(
        self,
        request: DescribeMissionTaskModelsRequest,
        callback: Callable[[AsyncResult[DescribeMissionTaskModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionTaskModel',
            function='describeMissionTaskModels',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeMissionTaskModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_mission_task_models(
        self,
        request: DescribeMissionTaskModelsRequest,
    ) -> DescribeMissionTaskModelsResult:
        async_result = []
        with timeout(30):
            self._describe_mission_task_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_mission_task_models_async(
        self,
        request: DescribeMissionTaskModelsRequest,
    ) -> DescribeMissionTaskModelsResult:
        async_result = []
        self._describe_mission_task_models(
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

    def _get_mission_task_model(
        self,
        request: GetMissionTaskModelRequest,
        callback: Callable[[AsyncResult[GetMissionTaskModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionTaskModel',
            function='getMissionTaskModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMissionTaskModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_mission_task_model(
        self,
        request: GetMissionTaskModelRequest,
    ) -> GetMissionTaskModelResult:
        async_result = []
        with timeout(30):
            self._get_mission_task_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_mission_task_model_async(
        self,
        request: GetMissionTaskModelRequest,
    ) -> GetMissionTaskModelResult:
        async_result = []
        self._get_mission_task_model(
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

    def _describe_mission_task_model_masters(
        self,
        request: DescribeMissionTaskModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeMissionTaskModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionTaskModelMaster',
            function='describeMissionTaskModelMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeMissionTaskModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_mission_task_model_masters(
        self,
        request: DescribeMissionTaskModelMastersRequest,
    ) -> DescribeMissionTaskModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_mission_task_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_mission_task_model_masters_async(
        self,
        request: DescribeMissionTaskModelMastersRequest,
    ) -> DescribeMissionTaskModelMastersResult:
        async_result = []
        self._describe_mission_task_model_masters(
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

    def _create_mission_task_model_master(
        self,
        request: CreateMissionTaskModelMasterRequest,
        callback: Callable[[AsyncResult[CreateMissionTaskModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionTaskModelMaster',
            function='createMissionTaskModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.name is not None:
            body["name"] = request.name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.description is not None:
            body["description"] = request.description
        if request.verify_complete_type is not None:
            body["verifyCompleteType"] = request.verify_complete_type
        if request.target_counter is not None:
            body["targetCounter"] = request.target_counter.to_dict()
        if request.verify_complete_consume_actions is not None:
            body["verifyCompleteConsumeActions"] = [
                item.to_dict()
                for item in request.verify_complete_consume_actions
            ]
        if request.complete_acquire_actions is not None:
            body["completeAcquireActions"] = [
                item.to_dict()
                for item in request.complete_acquire_actions
            ]
        if request.challenge_period_event_id is not None:
            body["challengePeriodEventId"] = request.challenge_period_event_id
        if request.premise_mission_task_name is not None:
            body["premiseMissionTaskName"] = request.premise_mission_task_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.target_reset_type is not None:
            body["targetResetType"] = request.target_reset_type
        if request.target_value is not None:
            body["targetValue"] = request.target_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateMissionTaskModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_mission_task_model_master(
        self,
        request: CreateMissionTaskModelMasterRequest,
    ) -> CreateMissionTaskModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_mission_task_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_mission_task_model_master_async(
        self,
        request: CreateMissionTaskModelMasterRequest,
    ) -> CreateMissionTaskModelMasterResult:
        async_result = []
        self._create_mission_task_model_master(
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

    def _get_mission_task_model_master(
        self,
        request: GetMissionTaskModelMasterRequest,
        callback: Callable[[AsyncResult[GetMissionTaskModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionTaskModelMaster',
            function='getMissionTaskModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMissionTaskModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_mission_task_model_master(
        self,
        request: GetMissionTaskModelMasterRequest,
    ) -> GetMissionTaskModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_mission_task_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_mission_task_model_master_async(
        self,
        request: GetMissionTaskModelMasterRequest,
    ) -> GetMissionTaskModelMasterResult:
        async_result = []
        self._get_mission_task_model_master(
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

    def _update_mission_task_model_master(
        self,
        request: UpdateMissionTaskModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateMissionTaskModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionTaskModelMaster',
            function='updateMissionTaskModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.description is not None:
            body["description"] = request.description
        if request.verify_complete_type is not None:
            body["verifyCompleteType"] = request.verify_complete_type
        if request.target_counter is not None:
            body["targetCounter"] = request.target_counter.to_dict()
        if request.verify_complete_consume_actions is not None:
            body["verifyCompleteConsumeActions"] = [
                item.to_dict()
                for item in request.verify_complete_consume_actions
            ]
        if request.complete_acquire_actions is not None:
            body["completeAcquireActions"] = [
                item.to_dict()
                for item in request.complete_acquire_actions
            ]
        if request.challenge_period_event_id is not None:
            body["challengePeriodEventId"] = request.challenge_period_event_id
        if request.premise_mission_task_name is not None:
            body["premiseMissionTaskName"] = request.premise_mission_task_name
        if request.counter_name is not None:
            body["counterName"] = request.counter_name
        if request.target_reset_type is not None:
            body["targetResetType"] = request.target_reset_type
        if request.target_value is not None:
            body["targetValue"] = request.target_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateMissionTaskModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_mission_task_model_master(
        self,
        request: UpdateMissionTaskModelMasterRequest,
    ) -> UpdateMissionTaskModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_mission_task_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_mission_task_model_master_async(
        self,
        request: UpdateMissionTaskModelMasterRequest,
    ) -> UpdateMissionTaskModelMasterResult:
        async_result = []
        self._update_mission_task_model_master(
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

    def _delete_mission_task_model_master(
        self,
        request: DeleteMissionTaskModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteMissionTaskModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="mission",
            component='missionTaskModelMaster',
            function='deleteMissionTaskModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mission_group_name is not None:
            body["missionGroupName"] = request.mission_group_name
        if request.mission_task_name is not None:
            body["missionTaskName"] = request.mission_task_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteMissionTaskModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_mission_task_model_master(
        self,
        request: DeleteMissionTaskModelMasterRequest,
    ) -> DeleteMissionTaskModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_mission_task_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_mission_task_model_master_async(
        self,
        request: DeleteMissionTaskModelMasterRequest,
    ) -> DeleteMissionTaskModelMasterResult:
        async_result = []
        self._delete_mission_task_model_master(
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