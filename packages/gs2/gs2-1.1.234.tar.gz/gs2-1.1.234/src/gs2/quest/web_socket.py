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


class Gs2QuestWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
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
            service="quest",
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
        if request.start_quest_script is not None:
            body["startQuestScript"] = request.start_quest_script.to_dict()
        if request.complete_quest_script is not None:
            body["completeQuestScript"] = request.complete_quest_script.to_dict()
        if request.failed_quest_script is not None:
            body["failedQuestScript"] = request.failed_quest_script.to_dict()
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
            service="quest",
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
            service="quest",
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
            service="quest",
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
        if request.start_quest_script is not None:
            body["startQuestScript"] = request.start_quest_script.to_dict()
        if request.complete_quest_script is not None:
            body["completeQuestScript"] = request.complete_quest_script.to_dict()
        if request.failed_quest_script is not None:
            body["failedQuestScript"] = request.failed_quest_script.to_dict()
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
            service="quest",
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
            service="quest",
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
            service="quest",
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
            service="quest",
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
            service="quest",
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
            service="quest",
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
            service="quest",
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
            service="quest",
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
            service="quest",
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

    def _describe_quest_group_model_masters(
        self,
        request: DescribeQuestGroupModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeQuestGroupModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questGroupModelMaster',
            function='describeQuestGroupModelMasters',
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
                result_type=DescribeQuestGroupModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_quest_group_model_masters(
        self,
        request: DescribeQuestGroupModelMastersRequest,
    ) -> DescribeQuestGroupModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_quest_group_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_quest_group_model_masters_async(
        self,
        request: DescribeQuestGroupModelMastersRequest,
    ) -> DescribeQuestGroupModelMastersResult:
        async_result = []
        self._describe_quest_group_model_masters(
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

    def _create_quest_group_model_master(
        self,
        request: CreateQuestGroupModelMasterRequest,
        callback: Callable[[AsyncResult[CreateQuestGroupModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questGroupModelMaster',
            function='createQuestGroupModelMaster',
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
        if request.challenge_period_event_id is not None:
            body["challengePeriodEventId"] = request.challenge_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateQuestGroupModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_quest_group_model_master(
        self,
        request: CreateQuestGroupModelMasterRequest,
    ) -> CreateQuestGroupModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_quest_group_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_quest_group_model_master_async(
        self,
        request: CreateQuestGroupModelMasterRequest,
    ) -> CreateQuestGroupModelMasterResult:
        async_result = []
        self._create_quest_group_model_master(
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

    def _get_quest_group_model_master(
        self,
        request: GetQuestGroupModelMasterRequest,
        callback: Callable[[AsyncResult[GetQuestGroupModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questGroupModelMaster',
            function='getQuestGroupModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetQuestGroupModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_quest_group_model_master(
        self,
        request: GetQuestGroupModelMasterRequest,
    ) -> GetQuestGroupModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_quest_group_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_quest_group_model_master_async(
        self,
        request: GetQuestGroupModelMasterRequest,
    ) -> GetQuestGroupModelMasterResult:
        async_result = []
        self._get_quest_group_model_master(
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

    def _update_quest_group_model_master(
        self,
        request: UpdateQuestGroupModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateQuestGroupModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questGroupModelMaster',
            function='updateQuestGroupModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.challenge_period_event_id is not None:
            body["challengePeriodEventId"] = request.challenge_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateQuestGroupModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_quest_group_model_master(
        self,
        request: UpdateQuestGroupModelMasterRequest,
    ) -> UpdateQuestGroupModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_quest_group_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_quest_group_model_master_async(
        self,
        request: UpdateQuestGroupModelMasterRequest,
    ) -> UpdateQuestGroupModelMasterResult:
        async_result = []
        self._update_quest_group_model_master(
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

    def _delete_quest_group_model_master(
        self,
        request: DeleteQuestGroupModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteQuestGroupModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questGroupModelMaster',
            function='deleteQuestGroupModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteQuestGroupModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_quest_group_model_master(
        self,
        request: DeleteQuestGroupModelMasterRequest,
    ) -> DeleteQuestGroupModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_quest_group_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_quest_group_model_master_async(
        self,
        request: DeleteQuestGroupModelMasterRequest,
    ) -> DeleteQuestGroupModelMasterResult:
        async_result = []
        self._delete_quest_group_model_master(
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

    def _describe_quest_model_masters(
        self,
        request: DescribeQuestModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeQuestModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questModelMaster',
            function='describeQuestModelMasters',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeQuestModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_quest_model_masters(
        self,
        request: DescribeQuestModelMastersRequest,
    ) -> DescribeQuestModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_quest_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_quest_model_masters_async(
        self,
        request: DescribeQuestModelMastersRequest,
    ) -> DescribeQuestModelMastersResult:
        async_result = []
        self._describe_quest_model_masters(
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

    def _create_quest_model_master(
        self,
        request: CreateQuestModelMasterRequest,
        callback: Callable[[AsyncResult[CreateQuestModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questModelMaster',
            function='createQuestModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.contents is not None:
            body["contents"] = [
                item.to_dict()
                for item in request.contents
            ]
        if request.challenge_period_event_id is not None:
            body["challengePeriodEventId"] = request.challenge_period_event_id
        if request.first_complete_acquire_actions is not None:
            body["firstCompleteAcquireActions"] = [
                item.to_dict()
                for item in request.first_complete_acquire_actions
            ]
        if request.verify_actions is not None:
            body["verifyActions"] = [
                item.to_dict()
                for item in request.verify_actions
            ]
        if request.consume_actions is not None:
            body["consumeActions"] = [
                item.to_dict()
                for item in request.consume_actions
            ]
        if request.failed_acquire_actions is not None:
            body["failedAcquireActions"] = [
                item.to_dict()
                for item in request.failed_acquire_actions
            ]
        if request.premise_quest_names is not None:
            body["premiseQuestNames"] = [
                item
                for item in request.premise_quest_names
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateQuestModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_quest_model_master(
        self,
        request: CreateQuestModelMasterRequest,
    ) -> CreateQuestModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_quest_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_quest_model_master_async(
        self,
        request: CreateQuestModelMasterRequest,
    ) -> CreateQuestModelMasterResult:
        async_result = []
        self._create_quest_model_master(
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

    def _get_quest_model_master(
        self,
        request: GetQuestModelMasterRequest,
        callback: Callable[[AsyncResult[GetQuestModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questModelMaster',
            function='getQuestModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.quest_name is not None:
            body["questName"] = request.quest_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetQuestModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_quest_model_master(
        self,
        request: GetQuestModelMasterRequest,
    ) -> GetQuestModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_quest_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_quest_model_master_async(
        self,
        request: GetQuestModelMasterRequest,
    ) -> GetQuestModelMasterResult:
        async_result = []
        self._get_quest_model_master(
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

    def _update_quest_model_master(
        self,
        request: UpdateQuestModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateQuestModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questModelMaster',
            function='updateQuestModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.quest_name is not None:
            body["questName"] = request.quest_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.contents is not None:
            body["contents"] = [
                item.to_dict()
                for item in request.contents
            ]
        if request.challenge_period_event_id is not None:
            body["challengePeriodEventId"] = request.challenge_period_event_id
        if request.first_complete_acquire_actions is not None:
            body["firstCompleteAcquireActions"] = [
                item.to_dict()
                for item in request.first_complete_acquire_actions
            ]
        if request.verify_actions is not None:
            body["verifyActions"] = [
                item.to_dict()
                for item in request.verify_actions
            ]
        if request.consume_actions is not None:
            body["consumeActions"] = [
                item.to_dict()
                for item in request.consume_actions
            ]
        if request.failed_acquire_actions is not None:
            body["failedAcquireActions"] = [
                item.to_dict()
                for item in request.failed_acquire_actions
            ]
        if request.premise_quest_names is not None:
            body["premiseQuestNames"] = [
                item
                for item in request.premise_quest_names
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateQuestModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_quest_model_master(
        self,
        request: UpdateQuestModelMasterRequest,
    ) -> UpdateQuestModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_quest_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_quest_model_master_async(
        self,
        request: UpdateQuestModelMasterRequest,
    ) -> UpdateQuestModelMasterResult:
        async_result = []
        self._update_quest_model_master(
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

    def _delete_quest_model_master(
        self,
        request: DeleteQuestModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteQuestModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questModelMaster',
            function='deleteQuestModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.quest_name is not None:
            body["questName"] = request.quest_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteQuestModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_quest_model_master(
        self,
        request: DeleteQuestModelMasterRequest,
    ) -> DeleteQuestModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_quest_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_quest_model_master_async(
        self,
        request: DeleteQuestModelMasterRequest,
    ) -> DeleteQuestModelMasterResult:
        async_result = []
        self._delete_quest_model_master(
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
            service="quest",
            component='currentQuestMaster',
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

    def _get_current_quest_master(
        self,
        request: GetCurrentQuestMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentQuestMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='currentQuestMaster',
            function='getCurrentQuestMaster',
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
                result_type=GetCurrentQuestMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_quest_master(
        self,
        request: GetCurrentQuestMasterRequest,
    ) -> GetCurrentQuestMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_quest_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_quest_master_async(
        self,
        request: GetCurrentQuestMasterRequest,
    ) -> GetCurrentQuestMasterResult:
        async_result = []
        self._get_current_quest_master(
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

    def _pre_update_current_quest_master(
        self,
        request: PreUpdateCurrentQuestMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentQuestMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='currentQuestMaster',
            function='preUpdateCurrentQuestMaster',
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
                result_type=PreUpdateCurrentQuestMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_quest_master(
        self,
        request: PreUpdateCurrentQuestMasterRequest,
    ) -> PreUpdateCurrentQuestMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_quest_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_quest_master_async(
        self,
        request: PreUpdateCurrentQuestMasterRequest,
    ) -> PreUpdateCurrentQuestMasterResult:
        async_result = []
        self._pre_update_current_quest_master(
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

    def _update_current_quest_master(
        self,
        request: UpdateCurrentQuestMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentQuestMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='currentQuestMaster',
            function='updateCurrentQuestMaster',
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
                result_type=UpdateCurrentQuestMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_quest_master(
        self,
        request: UpdateCurrentQuestMasterRequest,
    ) -> UpdateCurrentQuestMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_quest_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_quest_master_async(
        self,
        request: UpdateCurrentQuestMasterRequest,
    ) -> UpdateCurrentQuestMasterResult:
        async_result = []
        self._update_current_quest_master(
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

    def _update_current_quest_master_from_git_hub(
        self,
        request: UpdateCurrentQuestMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentQuestMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='currentQuestMaster',
            function='updateCurrentQuestMasterFromGitHub',
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
                result_type=UpdateCurrentQuestMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_quest_master_from_git_hub(
        self,
        request: UpdateCurrentQuestMasterFromGitHubRequest,
    ) -> UpdateCurrentQuestMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_quest_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_quest_master_from_git_hub_async(
        self,
        request: UpdateCurrentQuestMasterFromGitHubRequest,
    ) -> UpdateCurrentQuestMasterFromGitHubResult:
        async_result = []
        self._update_current_quest_master_from_git_hub(
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

    def _describe_progresses_by_user_id(
        self,
        request: DescribeProgressesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeProgressesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='describeProgressesByUserId',
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
                result_type=DescribeProgressesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_progresses_by_user_id(
        self,
        request: DescribeProgressesByUserIdRequest,
    ) -> DescribeProgressesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_progresses_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_progresses_by_user_id_async(
        self,
        request: DescribeProgressesByUserIdRequest,
    ) -> DescribeProgressesByUserIdResult:
        async_result = []
        self._describe_progresses_by_user_id(
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

    def _create_progress_by_user_id(
        self,
        request: CreateProgressByUserIdRequest,
        callback: Callable[[AsyncResult[CreateProgressByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='createProgressByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.quest_model_id is not None:
            body["questModelId"] = request.quest_model_id
        if request.force is not None:
            body["force"] = request.force
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
                result_type=CreateProgressByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_progress_by_user_id(
        self,
        request: CreateProgressByUserIdRequest,
    ) -> CreateProgressByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_progress_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_progress_by_user_id_async(
        self,
        request: CreateProgressByUserIdRequest,
    ) -> CreateProgressByUserIdResult:
        async_result = []
        self._create_progress_by_user_id(
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

    def _get_progress(
        self,
        request: GetProgressRequest,
        callback: Callable[[AsyncResult[GetProgressResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='getProgress',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetProgressResult,
                callback=callback,
                body=body,
            )
        )

    def get_progress(
        self,
        request: GetProgressRequest,
    ) -> GetProgressResult:
        async_result = []
        with timeout(30):
            self._get_progress(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_progress_async(
        self,
        request: GetProgressRequest,
    ) -> GetProgressResult:
        async_result = []
        self._get_progress(
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

    def _get_progress_by_user_id(
        self,
        request: GetProgressByUserIdRequest,
        callback: Callable[[AsyncResult[GetProgressByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='getProgressByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetProgressByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_progress_by_user_id(
        self,
        request: GetProgressByUserIdRequest,
    ) -> GetProgressByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_progress_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_progress_by_user_id_async(
        self,
        request: GetProgressByUserIdRequest,
    ) -> GetProgressByUserIdResult:
        async_result = []
        self._get_progress_by_user_id(
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

    def _start(
        self,
        request: StartRequest,
        callback: Callable[[AsyncResult[StartResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='start',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.quest_name is not None:
            body["questName"] = request.quest_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.force is not None:
            body["force"] = request.force
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
                result_type=StartResult,
                callback=callback,
                body=body,
            )
        )

    def start(
        self,
        request: StartRequest,
    ) -> StartResult:
        async_result = []
        with timeout(30):
            self._start(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def start_async(
        self,
        request: StartRequest,
    ) -> StartResult:
        async_result = []
        self._start(
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

    def _start_by_user_id(
        self,
        request: StartByUserIdRequest,
        callback: Callable[[AsyncResult[StartByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='startByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.quest_name is not None:
            body["questName"] = request.quest_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.force is not None:
            body["force"] = request.force
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
                result_type=StartByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def start_by_user_id(
        self,
        request: StartByUserIdRequest,
    ) -> StartByUserIdResult:
        async_result = []
        with timeout(30):
            self._start_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def start_by_user_id_async(
        self,
        request: StartByUserIdRequest,
    ) -> StartByUserIdResult:
        async_result = []
        self._start_by_user_id(
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

    def _end(
        self,
        request: EndRequest,
        callback: Callable[[AsyncResult[EndResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='end',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.rewards is not None:
            body["rewards"] = [
                item.to_dict()
                for item in request.rewards
            ]
        if request.is_complete is not None:
            body["isComplete"] = request.is_complete
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
                result_type=EndResult,
                callback=callback,
                body=body,
            )
        )

    def end(
        self,
        request: EndRequest,
    ) -> EndResult:
        async_result = []
        with timeout(30):
            self._end(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def end_async(
        self,
        request: EndRequest,
    ) -> EndResult:
        async_result = []
        self._end(
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

    def _end_by_user_id(
        self,
        request: EndByUserIdRequest,
        callback: Callable[[AsyncResult[EndByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='endByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.rewards is not None:
            body["rewards"] = [
                item.to_dict()
                for item in request.rewards
            ]
        if request.is_complete is not None:
            body["isComplete"] = request.is_complete
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
                result_type=EndByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def end_by_user_id(
        self,
        request: EndByUserIdRequest,
    ) -> EndByUserIdResult:
        async_result = []
        with timeout(30):
            self._end_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def end_by_user_id_async(
        self,
        request: EndByUserIdRequest,
    ) -> EndByUserIdResult:
        async_result = []
        self._end_by_user_id(
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

    def _delete_progress(
        self,
        request: DeleteProgressRequest,
        callback: Callable[[AsyncResult[DeleteProgressResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='deleteProgress',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
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
                result_type=DeleteProgressResult,
                callback=callback,
                body=body,
            )
        )

    def delete_progress(
        self,
        request: DeleteProgressRequest,
    ) -> DeleteProgressResult:
        async_result = []
        with timeout(30):
            self._delete_progress(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_progress_async(
        self,
        request: DeleteProgressRequest,
    ) -> DeleteProgressResult:
        async_result = []
        self._delete_progress(
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

    def _delete_progress_by_user_id(
        self,
        request: DeleteProgressByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteProgressByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='deleteProgressByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
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
                result_type=DeleteProgressByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_progress_by_user_id(
        self,
        request: DeleteProgressByUserIdRequest,
    ) -> DeleteProgressByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_progress_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_progress_by_user_id_async(
        self,
        request: DeleteProgressByUserIdRequest,
    ) -> DeleteProgressByUserIdResult:
        async_result = []
        self._delete_progress_by_user_id(
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

    def _create_progress_by_stamp_sheet(
        self,
        request: CreateProgressByStampSheetRequest,
        callback: Callable[[AsyncResult[CreateProgressByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='createProgressByStampSheet',
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
                result_type=CreateProgressByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def create_progress_by_stamp_sheet(
        self,
        request: CreateProgressByStampSheetRequest,
    ) -> CreateProgressByStampSheetResult:
        async_result = []
        with timeout(30):
            self._create_progress_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_progress_by_stamp_sheet_async(
        self,
        request: CreateProgressByStampSheetRequest,
    ) -> CreateProgressByStampSheetResult:
        async_result = []
        self._create_progress_by_stamp_sheet(
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

    def _delete_progress_by_stamp_task(
        self,
        request: DeleteProgressByStampTaskRequest,
        callback: Callable[[AsyncResult[DeleteProgressByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='progress',
            function='deleteProgressByStampTask',
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
                result_type=DeleteProgressByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def delete_progress_by_stamp_task(
        self,
        request: DeleteProgressByStampTaskRequest,
    ) -> DeleteProgressByStampTaskResult:
        async_result = []
        with timeout(30):
            self._delete_progress_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_progress_by_stamp_task_async(
        self,
        request: DeleteProgressByStampTaskRequest,
    ) -> DeleteProgressByStampTaskResult:
        async_result = []
        self._delete_progress_by_stamp_task(
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

    def _describe_completed_quest_lists(
        self,
        request: DescribeCompletedQuestListsRequest,
        callback: Callable[[AsyncResult[DescribeCompletedQuestListsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='completedQuestList',
            function='describeCompletedQuestLists',
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
                result_type=DescribeCompletedQuestListsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_completed_quest_lists(
        self,
        request: DescribeCompletedQuestListsRequest,
    ) -> DescribeCompletedQuestListsResult:
        async_result = []
        with timeout(30):
            self._describe_completed_quest_lists(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_completed_quest_lists_async(
        self,
        request: DescribeCompletedQuestListsRequest,
    ) -> DescribeCompletedQuestListsResult:
        async_result = []
        self._describe_completed_quest_lists(
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

    def _describe_completed_quest_lists_by_user_id(
        self,
        request: DescribeCompletedQuestListsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeCompletedQuestListsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='completedQuestList',
            function='describeCompletedQuestListsByUserId',
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
                result_type=DescribeCompletedQuestListsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_completed_quest_lists_by_user_id(
        self,
        request: DescribeCompletedQuestListsByUserIdRequest,
    ) -> DescribeCompletedQuestListsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_completed_quest_lists_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_completed_quest_lists_by_user_id_async(
        self,
        request: DescribeCompletedQuestListsByUserIdRequest,
    ) -> DescribeCompletedQuestListsByUserIdResult:
        async_result = []
        self._describe_completed_quest_lists_by_user_id(
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

    def _get_completed_quest_list(
        self,
        request: GetCompletedQuestListRequest,
        callback: Callable[[AsyncResult[GetCompletedQuestListResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='completedQuestList',
            function='getCompletedQuestList',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCompletedQuestListResult,
                callback=callback,
                body=body,
            )
        )

    def get_completed_quest_list(
        self,
        request: GetCompletedQuestListRequest,
    ) -> GetCompletedQuestListResult:
        async_result = []
        with timeout(30):
            self._get_completed_quest_list(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_completed_quest_list_async(
        self,
        request: GetCompletedQuestListRequest,
    ) -> GetCompletedQuestListResult:
        async_result = []
        self._get_completed_quest_list(
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

    def _get_completed_quest_list_by_user_id(
        self,
        request: GetCompletedQuestListByUserIdRequest,
        callback: Callable[[AsyncResult[GetCompletedQuestListByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='completedQuestList',
            function='getCompletedQuestListByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCompletedQuestListByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_completed_quest_list_by_user_id(
        self,
        request: GetCompletedQuestListByUserIdRequest,
    ) -> GetCompletedQuestListByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_completed_quest_list_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_completed_quest_list_by_user_id_async(
        self,
        request: GetCompletedQuestListByUserIdRequest,
    ) -> GetCompletedQuestListByUserIdResult:
        async_result = []
        self._get_completed_quest_list_by_user_id(
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

    def _delete_completed_quest_list_by_user_id(
        self,
        request: DeleteCompletedQuestListByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteCompletedQuestListByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='completedQuestList',
            function='deleteCompletedQuestListByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
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
                result_type=DeleteCompletedQuestListByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_completed_quest_list_by_user_id(
        self,
        request: DeleteCompletedQuestListByUserIdRequest,
    ) -> DeleteCompletedQuestListByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_completed_quest_list_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_completed_quest_list_by_user_id_async(
        self,
        request: DeleteCompletedQuestListByUserIdRequest,
    ) -> DeleteCompletedQuestListByUserIdResult:
        async_result = []
        self._delete_completed_quest_list_by_user_id(
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

    def _describe_quest_group_models(
        self,
        request: DescribeQuestGroupModelsRequest,
        callback: Callable[[AsyncResult[DescribeQuestGroupModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questGroupModel',
            function='describeQuestGroupModels',
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
                result_type=DescribeQuestGroupModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_quest_group_models(
        self,
        request: DescribeQuestGroupModelsRequest,
    ) -> DescribeQuestGroupModelsResult:
        async_result = []
        with timeout(30):
            self._describe_quest_group_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_quest_group_models_async(
        self,
        request: DescribeQuestGroupModelsRequest,
    ) -> DescribeQuestGroupModelsResult:
        async_result = []
        self._describe_quest_group_models(
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

    def _get_quest_group_model(
        self,
        request: GetQuestGroupModelRequest,
        callback: Callable[[AsyncResult[GetQuestGroupModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questGroupModel',
            function='getQuestGroupModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetQuestGroupModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_quest_group_model(
        self,
        request: GetQuestGroupModelRequest,
    ) -> GetQuestGroupModelResult:
        async_result = []
        with timeout(30):
            self._get_quest_group_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_quest_group_model_async(
        self,
        request: GetQuestGroupModelRequest,
    ) -> GetQuestGroupModelResult:
        async_result = []
        self._get_quest_group_model(
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

    def _describe_quest_models(
        self,
        request: DescribeQuestModelsRequest,
        callback: Callable[[AsyncResult[DescribeQuestModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questModel',
            function='describeQuestModels',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeQuestModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_quest_models(
        self,
        request: DescribeQuestModelsRequest,
    ) -> DescribeQuestModelsResult:
        async_result = []
        with timeout(30):
            self._describe_quest_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_quest_models_async(
        self,
        request: DescribeQuestModelsRequest,
    ) -> DescribeQuestModelsResult:
        async_result = []
        self._describe_quest_models(
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

    def _get_quest_model(
        self,
        request: GetQuestModelRequest,
        callback: Callable[[AsyncResult[GetQuestModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="quest",
            component='questModel',
            function='getQuestModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.quest_group_name is not None:
            body["questGroupName"] = request.quest_group_name
        if request.quest_name is not None:
            body["questName"] = request.quest_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetQuestModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_quest_model(
        self,
        request: GetQuestModelRequest,
    ) -> GetQuestModelResult:
        async_result = []
        with timeout(30):
            self._get_quest_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_quest_model_async(
        self,
        request: GetQuestModelRequest,
    ) -> GetQuestModelResult:
        async_result = []
        self._get_quest_model(
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