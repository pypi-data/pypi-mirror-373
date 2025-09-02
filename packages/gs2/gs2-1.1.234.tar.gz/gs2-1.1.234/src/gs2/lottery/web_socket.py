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


class Gs2LotteryWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
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
            service="lottery",
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
        if request.lottery_trigger_script_id is not None:
            body["lotteryTriggerScriptId"] = request.lottery_trigger_script_id
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
            service="lottery",
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
            service="lottery",
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
            service="lottery",
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
        if request.lottery_trigger_script_id is not None:
            body["lotteryTriggerScriptId"] = request.lottery_trigger_script_id
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
            service="lottery",
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
            service="lottery",
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
            service="lottery",
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
            service="lottery",
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
            service="lottery",
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
            service="lottery",
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
            service="lottery",
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
            service="lottery",
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
            service="lottery",
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

    def _describe_lottery_model_masters(
        self,
        request: DescribeLotteryModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeLotteryModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lotteryModelMaster',
            function='describeLotteryModelMasters',
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
                result_type=DescribeLotteryModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_lottery_model_masters(
        self,
        request: DescribeLotteryModelMastersRequest,
    ) -> DescribeLotteryModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_lottery_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_lottery_model_masters_async(
        self,
        request: DescribeLotteryModelMastersRequest,
    ) -> DescribeLotteryModelMastersResult:
        async_result = []
        self._describe_lottery_model_masters(
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

    def _create_lottery_model_master(
        self,
        request: CreateLotteryModelMasterRequest,
        callback: Callable[[AsyncResult[CreateLotteryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lotteryModelMaster',
            function='createLotteryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.mode is not None:
            body["mode"] = request.mode
        if request.method is not None:
            body["method"] = request.method
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.choice_prize_table_script_id is not None:
            body["choicePrizeTableScriptId"] = request.choice_prize_table_script_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateLotteryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_lottery_model_master(
        self,
        request: CreateLotteryModelMasterRequest,
    ) -> CreateLotteryModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_lottery_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_lottery_model_master_async(
        self,
        request: CreateLotteryModelMasterRequest,
    ) -> CreateLotteryModelMasterResult:
        async_result = []
        self._create_lottery_model_master(
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

    def _get_lottery_model_master(
        self,
        request: GetLotteryModelMasterRequest,
        callback: Callable[[AsyncResult[GetLotteryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lotteryModelMaster',
            function='getLotteryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetLotteryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_lottery_model_master(
        self,
        request: GetLotteryModelMasterRequest,
    ) -> GetLotteryModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_lottery_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_lottery_model_master_async(
        self,
        request: GetLotteryModelMasterRequest,
    ) -> GetLotteryModelMasterResult:
        async_result = []
        self._get_lottery_model_master(
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

    def _update_lottery_model_master(
        self,
        request: UpdateLotteryModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateLotteryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lotteryModelMaster',
            function='updateLotteryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.mode is not None:
            body["mode"] = request.mode
        if request.method is not None:
            body["method"] = request.method
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.choice_prize_table_script_id is not None:
            body["choicePrizeTableScriptId"] = request.choice_prize_table_script_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateLotteryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_lottery_model_master(
        self,
        request: UpdateLotteryModelMasterRequest,
    ) -> UpdateLotteryModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_lottery_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_lottery_model_master_async(
        self,
        request: UpdateLotteryModelMasterRequest,
    ) -> UpdateLotteryModelMasterResult:
        async_result = []
        self._update_lottery_model_master(
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

    def _delete_lottery_model_master(
        self,
        request: DeleteLotteryModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteLotteryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lotteryModelMaster',
            function='deleteLotteryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteLotteryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_lottery_model_master(
        self,
        request: DeleteLotteryModelMasterRequest,
    ) -> DeleteLotteryModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_lottery_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_lottery_model_master_async(
        self,
        request: DeleteLotteryModelMasterRequest,
    ) -> DeleteLotteryModelMasterResult:
        async_result = []
        self._delete_lottery_model_master(
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

    def _describe_prize_table_masters(
        self,
        request: DescribePrizeTableMastersRequest,
        callback: Callable[[AsyncResult[DescribePrizeTableMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeTableMaster',
            function='describePrizeTableMasters',
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
                result_type=DescribePrizeTableMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_prize_table_masters(
        self,
        request: DescribePrizeTableMastersRequest,
    ) -> DescribePrizeTableMastersResult:
        async_result = []
        with timeout(30):
            self._describe_prize_table_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_prize_table_masters_async(
        self,
        request: DescribePrizeTableMastersRequest,
    ) -> DescribePrizeTableMastersResult:
        async_result = []
        self._describe_prize_table_masters(
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

    def _create_prize_table_master(
        self,
        request: CreatePrizeTableMasterRequest,
        callback: Callable[[AsyncResult[CreatePrizeTableMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeTableMaster',
            function='createPrizeTableMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.prizes is not None:
            body["prizes"] = [
                item.to_dict()
                for item in request.prizes
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreatePrizeTableMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_prize_table_master(
        self,
        request: CreatePrizeTableMasterRequest,
    ) -> CreatePrizeTableMasterResult:
        async_result = []
        with timeout(30):
            self._create_prize_table_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_prize_table_master_async(
        self,
        request: CreatePrizeTableMasterRequest,
    ) -> CreatePrizeTableMasterResult:
        async_result = []
        self._create_prize_table_master(
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

    def _get_prize_table_master(
        self,
        request: GetPrizeTableMasterRequest,
        callback: Callable[[AsyncResult[GetPrizeTableMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeTableMaster',
            function='getPrizeTableMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPrizeTableMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_prize_table_master(
        self,
        request: GetPrizeTableMasterRequest,
    ) -> GetPrizeTableMasterResult:
        async_result = []
        with timeout(30):
            self._get_prize_table_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_prize_table_master_async(
        self,
        request: GetPrizeTableMasterRequest,
    ) -> GetPrizeTableMasterResult:
        async_result = []
        self._get_prize_table_master(
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

    def _update_prize_table_master(
        self,
        request: UpdatePrizeTableMasterRequest,
        callback: Callable[[AsyncResult[UpdatePrizeTableMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeTableMaster',
            function='updatePrizeTableMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.prizes is not None:
            body["prizes"] = [
                item.to_dict()
                for item in request.prizes
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdatePrizeTableMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_prize_table_master(
        self,
        request: UpdatePrizeTableMasterRequest,
    ) -> UpdatePrizeTableMasterResult:
        async_result = []
        with timeout(30):
            self._update_prize_table_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_prize_table_master_async(
        self,
        request: UpdatePrizeTableMasterRequest,
    ) -> UpdatePrizeTableMasterResult:
        async_result = []
        self._update_prize_table_master(
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

    def _delete_prize_table_master(
        self,
        request: DeletePrizeTableMasterRequest,
        callback: Callable[[AsyncResult[DeletePrizeTableMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeTableMaster',
            function='deletePrizeTableMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeletePrizeTableMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_prize_table_master(
        self,
        request: DeletePrizeTableMasterRequest,
    ) -> DeletePrizeTableMasterResult:
        async_result = []
        with timeout(30):
            self._delete_prize_table_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_prize_table_master_async(
        self,
        request: DeletePrizeTableMasterRequest,
    ) -> DeletePrizeTableMasterResult:
        async_result = []
        self._delete_prize_table_master(
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

    def _describe_lottery_models(
        self,
        request: DescribeLotteryModelsRequest,
        callback: Callable[[AsyncResult[DescribeLotteryModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lotteryModel',
            function='describeLotteryModels',
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
                result_type=DescribeLotteryModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_lottery_models(
        self,
        request: DescribeLotteryModelsRequest,
    ) -> DescribeLotteryModelsResult:
        async_result = []
        with timeout(30):
            self._describe_lottery_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_lottery_models_async(
        self,
        request: DescribeLotteryModelsRequest,
    ) -> DescribeLotteryModelsResult:
        async_result = []
        self._describe_lottery_models(
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

    def _get_lottery_model(
        self,
        request: GetLotteryModelRequest,
        callback: Callable[[AsyncResult[GetLotteryModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lotteryModel',
            function='getLotteryModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetLotteryModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_lottery_model(
        self,
        request: GetLotteryModelRequest,
    ) -> GetLotteryModelResult:
        async_result = []
        with timeout(30):
            self._get_lottery_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_lottery_model_async(
        self,
        request: GetLotteryModelRequest,
    ) -> GetLotteryModelResult:
        async_result = []
        self._get_lottery_model(
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

    def _describe_prize_tables(
        self,
        request: DescribePrizeTablesRequest,
        callback: Callable[[AsyncResult[DescribePrizeTablesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeTable',
            function='describePrizeTables',
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
                result_type=DescribePrizeTablesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_prize_tables(
        self,
        request: DescribePrizeTablesRequest,
    ) -> DescribePrizeTablesResult:
        async_result = []
        with timeout(30):
            self._describe_prize_tables(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_prize_tables_async(
        self,
        request: DescribePrizeTablesRequest,
    ) -> DescribePrizeTablesResult:
        async_result = []
        self._describe_prize_tables(
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

    def _get_prize_table(
        self,
        request: GetPrizeTableRequest,
        callback: Callable[[AsyncResult[GetPrizeTableResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeTable',
            function='getPrizeTable',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPrizeTableResult,
                callback=callback,
                body=body,
            )
        )

    def get_prize_table(
        self,
        request: GetPrizeTableRequest,
    ) -> GetPrizeTableResult:
        async_result = []
        with timeout(30):
            self._get_prize_table(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_prize_table_async(
        self,
        request: GetPrizeTableRequest,
    ) -> GetPrizeTableResult:
        async_result = []
        self._get_prize_table(
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

    def _draw_by_user_id(
        self,
        request: DrawByUserIdRequest,
        callback: Callable[[AsyncResult[DrawByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lottery',
            function='drawByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.count is not None:
            body["count"] = request.count
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
                result_type=DrawByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def draw_by_user_id(
        self,
        request: DrawByUserIdRequest,
    ) -> DrawByUserIdResult:
        async_result = []
        with timeout(30):
            self._draw_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def draw_by_user_id_async(
        self,
        request: DrawByUserIdRequest,
    ) -> DrawByUserIdResult:
        async_result = []
        self._draw_by_user_id(
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

    def _prediction(
        self,
        request: PredictionRequest,
        callback: Callable[[AsyncResult[PredictionResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lottery',
            function='prediction',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.random_seed is not None:
            body["randomSeed"] = request.random_seed
        if request.count is not None:
            body["count"] = request.count

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PredictionResult,
                callback=callback,
                body=body,
            )
        )

    def prediction(
        self,
        request: PredictionRequest,
    ) -> PredictionResult:
        async_result = []
        with timeout(30):
            self._prediction(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def prediction_async(
        self,
        request: PredictionRequest,
    ) -> PredictionResult:
        async_result = []
        self._prediction(
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

    def _prediction_by_user_id(
        self,
        request: PredictionByUserIdRequest,
        callback: Callable[[AsyncResult[PredictionByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lottery',
            function='predictionByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.random_seed is not None:
            body["randomSeed"] = request.random_seed
        if request.count is not None:
            body["count"] = request.count
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PredictionByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def prediction_by_user_id(
        self,
        request: PredictionByUserIdRequest,
    ) -> PredictionByUserIdResult:
        async_result = []
        with timeout(30):
            self._prediction_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def prediction_by_user_id_async(
        self,
        request: PredictionByUserIdRequest,
    ) -> PredictionByUserIdResult:
        async_result = []
        self._prediction_by_user_id(
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

    def _draw_with_random_seed_by_user_id(
        self,
        request: DrawWithRandomSeedByUserIdRequest,
        callback: Callable[[AsyncResult[DrawWithRandomSeedByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lottery',
            function='drawWithRandomSeedByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.random_seed is not None:
            body["randomSeed"] = request.random_seed
        if request.count is not None:
            body["count"] = request.count
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
                result_type=DrawWithRandomSeedByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def draw_with_random_seed_by_user_id(
        self,
        request: DrawWithRandomSeedByUserIdRequest,
    ) -> DrawWithRandomSeedByUserIdResult:
        async_result = []
        with timeout(30):
            self._draw_with_random_seed_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def draw_with_random_seed_by_user_id_async(
        self,
        request: DrawWithRandomSeedByUserIdRequest,
    ) -> DrawWithRandomSeedByUserIdResult:
        async_result = []
        self._draw_with_random_seed_by_user_id(
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

    def _draw_by_stamp_sheet(
        self,
        request: DrawByStampSheetRequest,
        callback: Callable[[AsyncResult[DrawByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='lottery',
            function='drawByStampSheet',
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
                result_type=DrawByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def draw_by_stamp_sheet(
        self,
        request: DrawByStampSheetRequest,
    ) -> DrawByStampSheetResult:
        async_result = []
        with timeout(30):
            self._draw_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def draw_by_stamp_sheet_async(
        self,
        request: DrawByStampSheetRequest,
    ) -> DrawByStampSheetResult:
        async_result = []
        self._draw_by_stamp_sheet(
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

    def _describe_probabilities(
        self,
        request: DescribeProbabilitiesRequest,
        callback: Callable[[AsyncResult[DescribeProbabilitiesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='probability',
            function='describeProbabilities',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeProbabilitiesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_probabilities(
        self,
        request: DescribeProbabilitiesRequest,
    ) -> DescribeProbabilitiesResult:
        async_result = []
        with timeout(30):
            self._describe_probabilities(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_probabilities_async(
        self,
        request: DescribeProbabilitiesRequest,
    ) -> DescribeProbabilitiesResult:
        async_result = []
        self._describe_probabilities(
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

    def _describe_probabilities_by_user_id(
        self,
        request: DescribeProbabilitiesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeProbabilitiesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='probability',
            function='describeProbabilitiesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.lottery_name is not None:
            body["lotteryName"] = request.lottery_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeProbabilitiesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_probabilities_by_user_id(
        self,
        request: DescribeProbabilitiesByUserIdRequest,
    ) -> DescribeProbabilitiesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_probabilities_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_probabilities_by_user_id_async(
        self,
        request: DescribeProbabilitiesByUserIdRequest,
    ) -> DescribeProbabilitiesByUserIdResult:
        async_result = []
        self._describe_probabilities_by_user_id(
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
            service="lottery",
            component='currentLotteryMaster',
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

    def _get_current_lottery_master(
        self,
        request: GetCurrentLotteryMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentLotteryMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='currentLotteryMaster',
            function='getCurrentLotteryMaster',
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
                result_type=GetCurrentLotteryMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_lottery_master(
        self,
        request: GetCurrentLotteryMasterRequest,
    ) -> GetCurrentLotteryMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_lottery_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_lottery_master_async(
        self,
        request: GetCurrentLotteryMasterRequest,
    ) -> GetCurrentLotteryMasterResult:
        async_result = []
        self._get_current_lottery_master(
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

    def _pre_update_current_lottery_master(
        self,
        request: PreUpdateCurrentLotteryMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentLotteryMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='currentLotteryMaster',
            function='preUpdateCurrentLotteryMaster',
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
                result_type=PreUpdateCurrentLotteryMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_lottery_master(
        self,
        request: PreUpdateCurrentLotteryMasterRequest,
    ) -> PreUpdateCurrentLotteryMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_lottery_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_lottery_master_async(
        self,
        request: PreUpdateCurrentLotteryMasterRequest,
    ) -> PreUpdateCurrentLotteryMasterResult:
        async_result = []
        self._pre_update_current_lottery_master(
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

    def _update_current_lottery_master(
        self,
        request: UpdateCurrentLotteryMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentLotteryMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='currentLotteryMaster',
            function='updateCurrentLotteryMaster',
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
                result_type=UpdateCurrentLotteryMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_lottery_master(
        self,
        request: UpdateCurrentLotteryMasterRequest,
    ) -> UpdateCurrentLotteryMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_lottery_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_lottery_master_async(
        self,
        request: UpdateCurrentLotteryMasterRequest,
    ) -> UpdateCurrentLotteryMasterResult:
        async_result = []
        self._update_current_lottery_master(
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

    def _update_current_lottery_master_from_git_hub(
        self,
        request: UpdateCurrentLotteryMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentLotteryMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='currentLotteryMaster',
            function='updateCurrentLotteryMasterFromGitHub',
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
                result_type=UpdateCurrentLotteryMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_lottery_master_from_git_hub(
        self,
        request: UpdateCurrentLotteryMasterFromGitHubRequest,
    ) -> UpdateCurrentLotteryMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_lottery_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_lottery_master_from_git_hub_async(
        self,
        request: UpdateCurrentLotteryMasterFromGitHubRequest,
    ) -> UpdateCurrentLotteryMasterFromGitHubResult:
        async_result = []
        self._update_current_lottery_master_from_git_hub(
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

    def _describe_prize_limits(
        self,
        request: DescribePrizeLimitsRequest,
        callback: Callable[[AsyncResult[DescribePrizeLimitsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeLimit',
            function='describePrizeLimits',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribePrizeLimitsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_prize_limits(
        self,
        request: DescribePrizeLimitsRequest,
    ) -> DescribePrizeLimitsResult:
        async_result = []
        with timeout(30):
            self._describe_prize_limits(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_prize_limits_async(
        self,
        request: DescribePrizeLimitsRequest,
    ) -> DescribePrizeLimitsResult:
        async_result = []
        self._describe_prize_limits(
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

    def _get_prize_limit(
        self,
        request: GetPrizeLimitRequest,
        callback: Callable[[AsyncResult[GetPrizeLimitResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeLimit',
            function='getPrizeLimit',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.prize_id is not None:
            body["prizeId"] = request.prize_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPrizeLimitResult,
                callback=callback,
                body=body,
            )
        )

    def get_prize_limit(
        self,
        request: GetPrizeLimitRequest,
    ) -> GetPrizeLimitResult:
        async_result = []
        with timeout(30):
            self._get_prize_limit(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_prize_limit_async(
        self,
        request: GetPrizeLimitRequest,
    ) -> GetPrizeLimitResult:
        async_result = []
        self._get_prize_limit(
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

    def _reset_prize_limit(
        self,
        request: ResetPrizeLimitRequest,
        callback: Callable[[AsyncResult[ResetPrizeLimitResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='prizeLimit',
            function='resetPrizeLimit',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.prize_id is not None:
            body["prizeId"] = request.prize_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ResetPrizeLimitResult,
                callback=callback,
                body=body,
            )
        )

    def reset_prize_limit(
        self,
        request: ResetPrizeLimitRequest,
    ) -> ResetPrizeLimitResult:
        async_result = []
        with timeout(30):
            self._reset_prize_limit(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reset_prize_limit_async(
        self,
        request: ResetPrizeLimitRequest,
    ) -> ResetPrizeLimitResult:
        async_result = []
        self._reset_prize_limit(
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

    def _describe_boxes(
        self,
        request: DescribeBoxesRequest,
        callback: Callable[[AsyncResult[DescribeBoxesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='boxItems',
            function='describeBoxes',
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
                result_type=DescribeBoxesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_boxes(
        self,
        request: DescribeBoxesRequest,
    ) -> DescribeBoxesResult:
        async_result = []
        with timeout(30):
            self._describe_boxes(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_boxes_async(
        self,
        request: DescribeBoxesRequest,
    ) -> DescribeBoxesResult:
        async_result = []
        self._describe_boxes(
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

    def _describe_boxes_by_user_id(
        self,
        request: DescribeBoxesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeBoxesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='boxItems',
            function='describeBoxesByUserId',
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
                result_type=DescribeBoxesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_boxes_by_user_id(
        self,
        request: DescribeBoxesByUserIdRequest,
    ) -> DescribeBoxesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_boxes_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_boxes_by_user_id_async(
        self,
        request: DescribeBoxesByUserIdRequest,
    ) -> DescribeBoxesByUserIdResult:
        async_result = []
        self._describe_boxes_by_user_id(
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

    def _get_box(
        self,
        request: GetBoxRequest,
        callback: Callable[[AsyncResult[GetBoxResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='boxItems',
            function='getBox',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetBoxResult,
                callback=callback,
                body=body,
            )
        )

    def get_box(
        self,
        request: GetBoxRequest,
    ) -> GetBoxResult:
        async_result = []
        with timeout(30):
            self._get_box(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_box_async(
        self,
        request: GetBoxRequest,
    ) -> GetBoxResult:
        async_result = []
        self._get_box(
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

    def _get_box_by_user_id(
        self,
        request: GetBoxByUserIdRequest,
        callback: Callable[[AsyncResult[GetBoxByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='boxItems',
            function='getBoxByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetBoxByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_box_by_user_id(
        self,
        request: GetBoxByUserIdRequest,
    ) -> GetBoxByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_box_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_box_by_user_id_async(
        self,
        request: GetBoxByUserIdRequest,
    ) -> GetBoxByUserIdResult:
        async_result = []
        self._get_box_by_user_id(
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

    def _reset_box(
        self,
        request: ResetBoxRequest,
        callback: Callable[[AsyncResult[ResetBoxResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='boxItems',
            function='resetBox',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=ResetBoxResult,
                callback=callback,
                body=body,
            )
        )

    def reset_box(
        self,
        request: ResetBoxRequest,
    ) -> ResetBoxResult:
        async_result = []
        with timeout(30):
            self._reset_box(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reset_box_async(
        self,
        request: ResetBoxRequest,
    ) -> ResetBoxResult:
        async_result = []
        self._reset_box(
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

    def _reset_box_by_user_id(
        self,
        request: ResetBoxByUserIdRequest,
        callback: Callable[[AsyncResult[ResetBoxByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='boxItems',
            function='resetBoxByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.prize_table_name is not None:
            body["prizeTableName"] = request.prize_table_name
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
                result_type=ResetBoxByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def reset_box_by_user_id(
        self,
        request: ResetBoxByUserIdRequest,
    ) -> ResetBoxByUserIdResult:
        async_result = []
        with timeout(30):
            self._reset_box_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reset_box_by_user_id_async(
        self,
        request: ResetBoxByUserIdRequest,
    ) -> ResetBoxByUserIdResult:
        async_result = []
        self._reset_box_by_user_id(
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

    def _reset_by_stamp_sheet(
        self,
        request: ResetByStampSheetRequest,
        callback: Callable[[AsyncResult[ResetByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="lottery",
            component='boxItems',
            function='resetByStampSheet',
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
                result_type=ResetByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def reset_by_stamp_sheet(
        self,
        request: ResetByStampSheetRequest,
    ) -> ResetByStampSheetResult:
        async_result = []
        with timeout(30):
            self._reset_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reset_by_stamp_sheet_async(
        self,
        request: ResetByStampSheetRequest,
    ) -> ResetByStampSheetResult:
        async_result = []
        self._reset_by_stamp_sheet(
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