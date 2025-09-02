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


class Gs2ShowcaseWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
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
            service="showcase",
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
        if request.buy_script is not None:
            body["buyScript"] = request.buy_script.to_dict()
        if request.queue_namespace_id is not None:
            body["queueNamespaceId"] = request.queue_namespace_id
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()

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
            service="showcase",
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
            service="showcase",
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
            service="showcase",
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
        if request.buy_script is not None:
            body["buyScript"] = request.buy_script.to_dict()
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
            service="showcase",
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
            service="showcase",
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
            service="showcase",
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
            service="showcase",
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
            service="showcase",
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
            service="showcase",
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
            service="showcase",
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
            service="showcase",
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
            service="showcase",
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

    def _describe_sales_item_masters(
        self,
        request: DescribeSalesItemMastersRequest,
        callback: Callable[[AsyncResult[DescribeSalesItemMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemMaster',
            function='describeSalesItemMasters',
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
                result_type=DescribeSalesItemMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_sales_item_masters(
        self,
        request: DescribeSalesItemMastersRequest,
    ) -> DescribeSalesItemMastersResult:
        async_result = []
        with timeout(30):
            self._describe_sales_item_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_sales_item_masters_async(
        self,
        request: DescribeSalesItemMastersRequest,
    ) -> DescribeSalesItemMastersResult:
        async_result = []
        self._describe_sales_item_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_sales_item_master(
        self,
        request: CreateSalesItemMasterRequest,
        callback: Callable[[AsyncResult[CreateSalesItemMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemMaster',
            function='createSalesItemMaster',
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
        if request.acquire_actions is not None:
            body["acquireActions"] = [
                item.to_dict()
                for item in request.acquire_actions
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateSalesItemMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_sales_item_master(
        self,
        request: CreateSalesItemMasterRequest,
    ) -> CreateSalesItemMasterResult:
        async_result = []
        with timeout(30):
            self._create_sales_item_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_sales_item_master_async(
        self,
        request: CreateSalesItemMasterRequest,
    ) -> CreateSalesItemMasterResult:
        async_result = []
        self._create_sales_item_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_sales_item_master(
        self,
        request: GetSalesItemMasterRequest,
        callback: Callable[[AsyncResult[GetSalesItemMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemMaster',
            function='getSalesItemMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.sales_item_name is not None:
            body["salesItemName"] = request.sales_item_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSalesItemMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_sales_item_master(
        self,
        request: GetSalesItemMasterRequest,
    ) -> GetSalesItemMasterResult:
        async_result = []
        with timeout(30):
            self._get_sales_item_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_sales_item_master_async(
        self,
        request: GetSalesItemMasterRequest,
    ) -> GetSalesItemMasterResult:
        async_result = []
        self._get_sales_item_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_sales_item_master(
        self,
        request: UpdateSalesItemMasterRequest,
        callback: Callable[[AsyncResult[UpdateSalesItemMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemMaster',
            function='updateSalesItemMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.sales_item_name is not None:
            body["salesItemName"] = request.sales_item_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
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
        if request.acquire_actions is not None:
            body["acquireActions"] = [
                item.to_dict()
                for item in request.acquire_actions
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateSalesItemMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_sales_item_master(
        self,
        request: UpdateSalesItemMasterRequest,
    ) -> UpdateSalesItemMasterResult:
        async_result = []
        with timeout(30):
            self._update_sales_item_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_sales_item_master_async(
        self,
        request: UpdateSalesItemMasterRequest,
    ) -> UpdateSalesItemMasterResult:
        async_result = []
        self._update_sales_item_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_sales_item_master(
        self,
        request: DeleteSalesItemMasterRequest,
        callback: Callable[[AsyncResult[DeleteSalesItemMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemMaster',
            function='deleteSalesItemMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.sales_item_name is not None:
            body["salesItemName"] = request.sales_item_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteSalesItemMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_sales_item_master(
        self,
        request: DeleteSalesItemMasterRequest,
    ) -> DeleteSalesItemMasterResult:
        async_result = []
        with timeout(30):
            self._delete_sales_item_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_sales_item_master_async(
        self,
        request: DeleteSalesItemMasterRequest,
    ) -> DeleteSalesItemMasterResult:
        async_result = []
        self._delete_sales_item_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_sales_item_group_masters(
        self,
        request: DescribeSalesItemGroupMastersRequest,
        callback: Callable[[AsyncResult[DescribeSalesItemGroupMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemGroupMaster',
            function='describeSalesItemGroupMasters',
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
                result_type=DescribeSalesItemGroupMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_sales_item_group_masters(
        self,
        request: DescribeSalesItemGroupMastersRequest,
    ) -> DescribeSalesItemGroupMastersResult:
        async_result = []
        with timeout(30):
            self._describe_sales_item_group_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_sales_item_group_masters_async(
        self,
        request: DescribeSalesItemGroupMastersRequest,
    ) -> DescribeSalesItemGroupMastersResult:
        async_result = []
        self._describe_sales_item_group_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_sales_item_group_master(
        self,
        request: CreateSalesItemGroupMasterRequest,
        callback: Callable[[AsyncResult[CreateSalesItemGroupMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemGroupMaster',
            function='createSalesItemGroupMaster',
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
        if request.sales_item_names is not None:
            body["salesItemNames"] = [
                item
                for item in request.sales_item_names
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateSalesItemGroupMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_sales_item_group_master(
        self,
        request: CreateSalesItemGroupMasterRequest,
    ) -> CreateSalesItemGroupMasterResult:
        async_result = []
        with timeout(30):
            self._create_sales_item_group_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_sales_item_group_master_async(
        self,
        request: CreateSalesItemGroupMasterRequest,
    ) -> CreateSalesItemGroupMasterResult:
        async_result = []
        self._create_sales_item_group_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_sales_item_group_master(
        self,
        request: GetSalesItemGroupMasterRequest,
        callback: Callable[[AsyncResult[GetSalesItemGroupMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemGroupMaster',
            function='getSalesItemGroupMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.sales_item_group_name is not None:
            body["salesItemGroupName"] = request.sales_item_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSalesItemGroupMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_sales_item_group_master(
        self,
        request: GetSalesItemGroupMasterRequest,
    ) -> GetSalesItemGroupMasterResult:
        async_result = []
        with timeout(30):
            self._get_sales_item_group_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_sales_item_group_master_async(
        self,
        request: GetSalesItemGroupMasterRequest,
    ) -> GetSalesItemGroupMasterResult:
        async_result = []
        self._get_sales_item_group_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_sales_item_group_master(
        self,
        request: UpdateSalesItemGroupMasterRequest,
        callback: Callable[[AsyncResult[UpdateSalesItemGroupMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemGroupMaster',
            function='updateSalesItemGroupMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.sales_item_group_name is not None:
            body["salesItemGroupName"] = request.sales_item_group_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.sales_item_names is not None:
            body["salesItemNames"] = [
                item
                for item in request.sales_item_names
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateSalesItemGroupMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_sales_item_group_master(
        self,
        request: UpdateSalesItemGroupMasterRequest,
    ) -> UpdateSalesItemGroupMasterResult:
        async_result = []
        with timeout(30):
            self._update_sales_item_group_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_sales_item_group_master_async(
        self,
        request: UpdateSalesItemGroupMasterRequest,
    ) -> UpdateSalesItemGroupMasterResult:
        async_result = []
        self._update_sales_item_group_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_sales_item_group_master(
        self,
        request: DeleteSalesItemGroupMasterRequest,
        callback: Callable[[AsyncResult[DeleteSalesItemGroupMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='salesItemGroupMaster',
            function='deleteSalesItemGroupMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.sales_item_group_name is not None:
            body["salesItemGroupName"] = request.sales_item_group_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteSalesItemGroupMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_sales_item_group_master(
        self,
        request: DeleteSalesItemGroupMasterRequest,
    ) -> DeleteSalesItemGroupMasterResult:
        async_result = []
        with timeout(30):
            self._delete_sales_item_group_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_sales_item_group_master_async(
        self,
        request: DeleteSalesItemGroupMasterRequest,
    ) -> DeleteSalesItemGroupMasterResult:
        async_result = []
        self._delete_sales_item_group_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_showcase_masters(
        self,
        request: DescribeShowcaseMastersRequest,
        callback: Callable[[AsyncResult[DescribeShowcaseMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcaseMaster',
            function='describeShowcaseMasters',
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
                result_type=DescribeShowcaseMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_showcase_masters(
        self,
        request: DescribeShowcaseMastersRequest,
    ) -> DescribeShowcaseMastersResult:
        async_result = []
        with timeout(30):
            self._describe_showcase_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_showcase_masters_async(
        self,
        request: DescribeShowcaseMastersRequest,
    ) -> DescribeShowcaseMastersResult:
        async_result = []
        self._describe_showcase_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_showcase_master(
        self,
        request: CreateShowcaseMasterRequest,
        callback: Callable[[AsyncResult[CreateShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcaseMaster',
            function='createShowcaseMaster',
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
        if request.display_items is not None:
            body["displayItems"] = [
                item.to_dict()
                for item in request.display_items
            ]
        if request.sales_period_event_id is not None:
            body["salesPeriodEventId"] = request.sales_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_showcase_master(
        self,
        request: CreateShowcaseMasterRequest,
    ) -> CreateShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._create_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_showcase_master_async(
        self,
        request: CreateShowcaseMasterRequest,
    ) -> CreateShowcaseMasterResult:
        async_result = []
        self._create_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_showcase_master(
        self,
        request: GetShowcaseMasterRequest,
        callback: Callable[[AsyncResult[GetShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcaseMaster',
            function='getShowcaseMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_showcase_master(
        self,
        request: GetShowcaseMasterRequest,
    ) -> GetShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._get_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_showcase_master_async(
        self,
        request: GetShowcaseMasterRequest,
    ) -> GetShowcaseMasterResult:
        async_result = []
        self._get_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_showcase_master(
        self,
        request: UpdateShowcaseMasterRequest,
        callback: Callable[[AsyncResult[UpdateShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcaseMaster',
            function='updateShowcaseMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.display_items is not None:
            body["displayItems"] = [
                item.to_dict()
                for item in request.display_items
            ]
        if request.sales_period_event_id is not None:
            body["salesPeriodEventId"] = request.sales_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_showcase_master(
        self,
        request: UpdateShowcaseMasterRequest,
    ) -> UpdateShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._update_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_showcase_master_async(
        self,
        request: UpdateShowcaseMasterRequest,
    ) -> UpdateShowcaseMasterResult:
        async_result = []
        self._update_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_showcase_master(
        self,
        request: DeleteShowcaseMasterRequest,
        callback: Callable[[AsyncResult[DeleteShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcaseMaster',
            function='deleteShowcaseMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_showcase_master(
        self,
        request: DeleteShowcaseMasterRequest,
    ) -> DeleteShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._delete_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_showcase_master_async(
        self,
        request: DeleteShowcaseMasterRequest,
    ) -> DeleteShowcaseMasterResult:
        async_result = []
        self._delete_showcase_master(
            request,
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
            service="showcase",
            component='currentShowcaseMaster',
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

    def _get_current_showcase_master(
        self,
        request: GetCurrentShowcaseMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='currentShowcaseMaster',
            function='getCurrentShowcaseMaster',
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
                result_type=GetCurrentShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_showcase_master(
        self,
        request: GetCurrentShowcaseMasterRequest,
    ) -> GetCurrentShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_showcase_master_async(
        self,
        request: GetCurrentShowcaseMasterRequest,
    ) -> GetCurrentShowcaseMasterResult:
        async_result = []
        self._get_current_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _pre_update_current_showcase_master(
        self,
        request: PreUpdateCurrentShowcaseMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='currentShowcaseMaster',
            function='preUpdateCurrentShowcaseMaster',
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
                result_type=PreUpdateCurrentShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_showcase_master(
        self,
        request: PreUpdateCurrentShowcaseMasterRequest,
    ) -> PreUpdateCurrentShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_showcase_master_async(
        self,
        request: PreUpdateCurrentShowcaseMasterRequest,
    ) -> PreUpdateCurrentShowcaseMasterResult:
        async_result = []
        self._pre_update_current_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_showcase_master(
        self,
        request: UpdateCurrentShowcaseMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='currentShowcaseMaster',
            function='updateCurrentShowcaseMaster',
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
                result_type=UpdateCurrentShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_showcase_master(
        self,
        request: UpdateCurrentShowcaseMasterRequest,
    ) -> UpdateCurrentShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_showcase_master_async(
        self,
        request: UpdateCurrentShowcaseMasterRequest,
    ) -> UpdateCurrentShowcaseMasterResult:
        async_result = []
        self._update_current_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_showcase_master_from_git_hub(
        self,
        request: UpdateCurrentShowcaseMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentShowcaseMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='currentShowcaseMaster',
            function='updateCurrentShowcaseMasterFromGitHub',
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
                result_type=UpdateCurrentShowcaseMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_showcase_master_from_git_hub(
        self,
        request: UpdateCurrentShowcaseMasterFromGitHubRequest,
    ) -> UpdateCurrentShowcaseMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_showcase_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_showcase_master_from_git_hub_async(
        self,
        request: UpdateCurrentShowcaseMasterFromGitHubRequest,
    ) -> UpdateCurrentShowcaseMasterFromGitHubResult:
        async_result = []
        self._update_current_showcase_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_showcases(
        self,
        request: DescribeShowcasesRequest,
        callback: Callable[[AsyncResult[DescribeShowcasesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcase',
            function='describeShowcases',
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
                result_type=DescribeShowcasesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_showcases(
        self,
        request: DescribeShowcasesRequest,
    ) -> DescribeShowcasesResult:
        async_result = []
        with timeout(30):
            self._describe_showcases(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_showcases_async(
        self,
        request: DescribeShowcasesRequest,
    ) -> DescribeShowcasesResult:
        async_result = []
        self._describe_showcases(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_showcases_by_user_id(
        self,
        request: DescribeShowcasesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeShowcasesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcase',
            function='describeShowcasesByUserId',
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
                result_type=DescribeShowcasesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_showcases_by_user_id(
        self,
        request: DescribeShowcasesByUserIdRequest,
    ) -> DescribeShowcasesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_showcases_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_showcases_by_user_id_async(
        self,
        request: DescribeShowcasesByUserIdRequest,
    ) -> DescribeShowcasesByUserIdResult:
        async_result = []
        self._describe_showcases_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_showcase(
        self,
        request: GetShowcaseRequest,
        callback: Callable[[AsyncResult[GetShowcaseResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcase',
            function='getShowcase',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetShowcaseResult,
                callback=callback,
                body=body,
            )
        )

    def get_showcase(
        self,
        request: GetShowcaseRequest,
    ) -> GetShowcaseResult:
        async_result = []
        with timeout(30):
            self._get_showcase(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_showcase_async(
        self,
        request: GetShowcaseRequest,
    ) -> GetShowcaseResult:
        async_result = []
        self._get_showcase(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_showcase_by_user_id(
        self,
        request: GetShowcaseByUserIdRequest,
        callback: Callable[[AsyncResult[GetShowcaseByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='showcase',
            function='getShowcaseByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetShowcaseByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_showcase_by_user_id(
        self,
        request: GetShowcaseByUserIdRequest,
    ) -> GetShowcaseByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_showcase_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_showcase_by_user_id_async(
        self,
        request: GetShowcaseByUserIdRequest,
    ) -> GetShowcaseByUserIdResult:
        async_result = []
        self._get_showcase_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _buy(
        self,
        request: BuyRequest,
        callback: Callable[[AsyncResult[BuyResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='displayItem',
            function='buy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_id is not None:
            body["displayItemId"] = request.display_item_id
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.quantity is not None:
            body["quantity"] = request.quantity
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
                result_type=BuyResult,
                callback=callback,
                body=body,
            )
        )

    def buy(
        self,
        request: BuyRequest,
    ) -> BuyResult:
        async_result = []
        with timeout(30):
            self._buy(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def buy_async(
        self,
        request: BuyRequest,
    ) -> BuyResult:
        async_result = []
        self._buy(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _buy_by_user_id(
        self,
        request: BuyByUserIdRequest,
        callback: Callable[[AsyncResult[BuyByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='displayItem',
            function='buyByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_id is not None:
            body["displayItemId"] = request.display_item_id
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.quantity is not None:
            body["quantity"] = request.quantity
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
                result_type=BuyByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def buy_by_user_id(
        self,
        request: BuyByUserIdRequest,
    ) -> BuyByUserIdResult:
        async_result = []
        with timeout(30):
            self._buy_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def buy_by_user_id_async(
        self,
        request: BuyByUserIdRequest,
    ) -> BuyByUserIdResult:
        async_result = []
        self._buy_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_random_showcase_masters(
        self,
        request: DescribeRandomShowcaseMastersRequest,
        callback: Callable[[AsyncResult[DescribeRandomShowcaseMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseMaster',
            function='describeRandomShowcaseMasters',
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
                result_type=DescribeRandomShowcaseMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_random_showcase_masters(
        self,
        request: DescribeRandomShowcaseMastersRequest,
    ) -> DescribeRandomShowcaseMastersResult:
        async_result = []
        with timeout(30):
            self._describe_random_showcase_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_random_showcase_masters_async(
        self,
        request: DescribeRandomShowcaseMastersRequest,
    ) -> DescribeRandomShowcaseMastersResult:
        async_result = []
        self._describe_random_showcase_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_random_showcase_master(
        self,
        request: CreateRandomShowcaseMasterRequest,
        callback: Callable[[AsyncResult[CreateRandomShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseMaster',
            function='createRandomShowcaseMaster',
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
        if request.maximum_number_of_choice is not None:
            body["maximumNumberOfChoice"] = request.maximum_number_of_choice
        if request.display_items is not None:
            body["displayItems"] = [
                item.to_dict()
                for item in request.display_items
            ]
        if request.base_timestamp is not None:
            body["baseTimestamp"] = request.base_timestamp
        if request.reset_interval_hours is not None:
            body["resetIntervalHours"] = request.reset_interval_hours
        if request.sales_period_event_id is not None:
            body["salesPeriodEventId"] = request.sales_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateRandomShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_random_showcase_master(
        self,
        request: CreateRandomShowcaseMasterRequest,
    ) -> CreateRandomShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._create_random_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_random_showcase_master_async(
        self,
        request: CreateRandomShowcaseMasterRequest,
    ) -> CreateRandomShowcaseMasterResult:
        async_result = []
        self._create_random_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_random_showcase_master(
        self,
        request: GetRandomShowcaseMasterRequest,
        callback: Callable[[AsyncResult[GetRandomShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseMaster',
            function='getRandomShowcaseMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRandomShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_random_showcase_master(
        self,
        request: GetRandomShowcaseMasterRequest,
    ) -> GetRandomShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._get_random_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_random_showcase_master_async(
        self,
        request: GetRandomShowcaseMasterRequest,
    ) -> GetRandomShowcaseMasterResult:
        async_result = []
        self._get_random_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_random_showcase_master(
        self,
        request: UpdateRandomShowcaseMasterRequest,
        callback: Callable[[AsyncResult[UpdateRandomShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseMaster',
            function='updateRandomShowcaseMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.maximum_number_of_choice is not None:
            body["maximumNumberOfChoice"] = request.maximum_number_of_choice
        if request.display_items is not None:
            body["displayItems"] = [
                item.to_dict()
                for item in request.display_items
            ]
        if request.base_timestamp is not None:
            body["baseTimestamp"] = request.base_timestamp
        if request.reset_interval_hours is not None:
            body["resetIntervalHours"] = request.reset_interval_hours
        if request.sales_period_event_id is not None:
            body["salesPeriodEventId"] = request.sales_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateRandomShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_random_showcase_master(
        self,
        request: UpdateRandomShowcaseMasterRequest,
    ) -> UpdateRandomShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._update_random_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_random_showcase_master_async(
        self,
        request: UpdateRandomShowcaseMasterRequest,
    ) -> UpdateRandomShowcaseMasterResult:
        async_result = []
        self._update_random_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_random_showcase_master(
        self,
        request: DeleteRandomShowcaseMasterRequest,
        callback: Callable[[AsyncResult[DeleteRandomShowcaseMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseMaster',
            function='deleteRandomShowcaseMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteRandomShowcaseMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_random_showcase_master(
        self,
        request: DeleteRandomShowcaseMasterRequest,
    ) -> DeleteRandomShowcaseMasterResult:
        async_result = []
        with timeout(30):
            self._delete_random_showcase_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_random_showcase_master_async(
        self,
        request: DeleteRandomShowcaseMasterRequest,
    ) -> DeleteRandomShowcaseMasterResult:
        async_result = []
        self._delete_random_showcase_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _increment_purchase_count(
        self,
        request: IncrementPurchaseCountRequest,
        callback: Callable[[AsyncResult[IncrementPurchaseCountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseStatus',
            function='incrementPurchaseCount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_name is not None:
            body["displayItemName"] = request.display_item_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
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
                result_type=IncrementPurchaseCountResult,
                callback=callback,
                body=body,
            )
        )

    def increment_purchase_count(
        self,
        request: IncrementPurchaseCountRequest,
    ) -> IncrementPurchaseCountResult:
        async_result = []
        with timeout(30):
            self._increment_purchase_count(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def increment_purchase_count_async(
        self,
        request: IncrementPurchaseCountRequest,
    ) -> IncrementPurchaseCountResult:
        async_result = []
        self._increment_purchase_count(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _increment_purchase_count_by_user_id(
        self,
        request: IncrementPurchaseCountByUserIdRequest,
        callback: Callable[[AsyncResult[IncrementPurchaseCountByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseStatus',
            function='incrementPurchaseCountByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_name is not None:
            body["displayItemName"] = request.display_item_name
        if request.user_id is not None:
            body["userId"] = request.user_id
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
                result_type=IncrementPurchaseCountByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def increment_purchase_count_by_user_id(
        self,
        request: IncrementPurchaseCountByUserIdRequest,
    ) -> IncrementPurchaseCountByUserIdResult:
        async_result = []
        with timeout(30):
            self._increment_purchase_count_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def increment_purchase_count_by_user_id_async(
        self,
        request: IncrementPurchaseCountByUserIdRequest,
    ) -> IncrementPurchaseCountByUserIdResult:
        async_result = []
        self._increment_purchase_count_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _decrement_purchase_count_by_user_id(
        self,
        request: DecrementPurchaseCountByUserIdRequest,
        callback: Callable[[AsyncResult[DecrementPurchaseCountByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseStatus',
            function='decrementPurchaseCountByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_name is not None:
            body["displayItemName"] = request.display_item_name
        if request.user_id is not None:
            body["userId"] = request.user_id
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
                result_type=DecrementPurchaseCountByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def decrement_purchase_count_by_user_id(
        self,
        request: DecrementPurchaseCountByUserIdRequest,
    ) -> DecrementPurchaseCountByUserIdResult:
        async_result = []
        with timeout(30):
            self._decrement_purchase_count_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrement_purchase_count_by_user_id_async(
        self,
        request: DecrementPurchaseCountByUserIdRequest,
    ) -> DecrementPurchaseCountByUserIdResult:
        async_result = []
        self._decrement_purchase_count_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _increment_purchase_count_by_stamp_task(
        self,
        request: IncrementPurchaseCountByStampTaskRequest,
        callback: Callable[[AsyncResult[IncrementPurchaseCountByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseStatus',
            function='incrementPurchaseCountByStampTask',
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
                result_type=IncrementPurchaseCountByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def increment_purchase_count_by_stamp_task(
        self,
        request: IncrementPurchaseCountByStampTaskRequest,
    ) -> IncrementPurchaseCountByStampTaskResult:
        async_result = []
        with timeout(30):
            self._increment_purchase_count_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def increment_purchase_count_by_stamp_task_async(
        self,
        request: IncrementPurchaseCountByStampTaskRequest,
    ) -> IncrementPurchaseCountByStampTaskResult:
        async_result = []
        self._increment_purchase_count_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _decrement_purchase_count_by_stamp_sheet(
        self,
        request: DecrementPurchaseCountByStampSheetRequest,
        callback: Callable[[AsyncResult[DecrementPurchaseCountByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseStatus',
            function='decrementPurchaseCountByStampSheet',
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
                result_type=DecrementPurchaseCountByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def decrement_purchase_count_by_stamp_sheet(
        self,
        request: DecrementPurchaseCountByStampSheetRequest,
    ) -> DecrementPurchaseCountByStampSheetResult:
        async_result = []
        with timeout(30):
            self._decrement_purchase_count_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrement_purchase_count_by_stamp_sheet_async(
        self,
        request: DecrementPurchaseCountByStampSheetRequest,
    ) -> DecrementPurchaseCountByStampSheetResult:
        async_result = []
        self._decrement_purchase_count_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _force_re_draw_by_user_id(
        self,
        request: ForceReDrawByUserIdRequest,
        callback: Callable[[AsyncResult[ForceReDrawByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseStatus',
            function='forceReDrawByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
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
                result_type=ForceReDrawByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def force_re_draw_by_user_id(
        self,
        request: ForceReDrawByUserIdRequest,
    ) -> ForceReDrawByUserIdResult:
        async_result = []
        with timeout(30):
            self._force_re_draw_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def force_re_draw_by_user_id_async(
        self,
        request: ForceReDrawByUserIdRequest,
    ) -> ForceReDrawByUserIdResult:
        async_result = []
        self._force_re_draw_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _force_re_draw_by_user_id_by_stamp_sheet(
        self,
        request: ForceReDrawByUserIdByStampSheetRequest,
        callback: Callable[[AsyncResult[ForceReDrawByUserIdByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomShowcaseStatus',
            function='forceReDrawByUserIdByStampSheet',
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
                result_type=ForceReDrawByUserIdByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def force_re_draw_by_user_id_by_stamp_sheet(
        self,
        request: ForceReDrawByUserIdByStampSheetRequest,
    ) -> ForceReDrawByUserIdByStampSheetResult:
        async_result = []
        with timeout(30):
            self._force_re_draw_by_user_id_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def force_re_draw_by_user_id_by_stamp_sheet_async(
        self,
        request: ForceReDrawByUserIdByStampSheetRequest,
    ) -> ForceReDrawByUserIdByStampSheetResult:
        async_result = []
        self._force_re_draw_by_user_id_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_random_display_items(
        self,
        request: DescribeRandomDisplayItemsRequest,
        callback: Callable[[AsyncResult[DescribeRandomDisplayItemsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomDisplayItem',
            function='describeRandomDisplayItems',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeRandomDisplayItemsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_random_display_items(
        self,
        request: DescribeRandomDisplayItemsRequest,
    ) -> DescribeRandomDisplayItemsResult:
        async_result = []
        with timeout(30):
            self._describe_random_display_items(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_random_display_items_async(
        self,
        request: DescribeRandomDisplayItemsRequest,
    ) -> DescribeRandomDisplayItemsResult:
        async_result = []
        self._describe_random_display_items(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_random_display_items_by_user_id(
        self,
        request: DescribeRandomDisplayItemsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeRandomDisplayItemsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomDisplayItem',
            function='describeRandomDisplayItemsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeRandomDisplayItemsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_random_display_items_by_user_id(
        self,
        request: DescribeRandomDisplayItemsByUserIdRequest,
    ) -> DescribeRandomDisplayItemsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_random_display_items_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_random_display_items_by_user_id_async(
        self,
        request: DescribeRandomDisplayItemsByUserIdRequest,
    ) -> DescribeRandomDisplayItemsByUserIdResult:
        async_result = []
        self._describe_random_display_items_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_random_display_item(
        self,
        request: GetRandomDisplayItemRequest,
        callback: Callable[[AsyncResult[GetRandomDisplayItemResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomDisplayItem',
            function='getRandomDisplayItem',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_name is not None:
            body["displayItemName"] = request.display_item_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRandomDisplayItemResult,
                callback=callback,
                body=body,
            )
        )

    def get_random_display_item(
        self,
        request: GetRandomDisplayItemRequest,
    ) -> GetRandomDisplayItemResult:
        async_result = []
        with timeout(30):
            self._get_random_display_item(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_random_display_item_async(
        self,
        request: GetRandomDisplayItemRequest,
    ) -> GetRandomDisplayItemResult:
        async_result = []
        self._get_random_display_item(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_random_display_item_by_user_id(
        self,
        request: GetRandomDisplayItemByUserIdRequest,
        callback: Callable[[AsyncResult[GetRandomDisplayItemByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomDisplayItem',
            function='getRandomDisplayItemByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_name is not None:
            body["displayItemName"] = request.display_item_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRandomDisplayItemByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_random_display_item_by_user_id(
        self,
        request: GetRandomDisplayItemByUserIdRequest,
    ) -> GetRandomDisplayItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_random_display_item_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_random_display_item_by_user_id_async(
        self,
        request: GetRandomDisplayItemByUserIdRequest,
    ) -> GetRandomDisplayItemByUserIdResult:
        async_result = []
        self._get_random_display_item_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _random_showcase_buy(
        self,
        request: RandomShowcaseBuyRequest,
        callback: Callable[[AsyncResult[RandomShowcaseBuyResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomDisplayItem',
            function='randomShowcaseBuy',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_name is not None:
            body["displayItemName"] = request.display_item_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.quantity is not None:
            body["quantity"] = request.quantity
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
                result_type=RandomShowcaseBuyResult,
                callback=callback,
                body=body,
            )
        )

    def random_showcase_buy(
        self,
        request: RandomShowcaseBuyRequest,
    ) -> RandomShowcaseBuyResult:
        async_result = []
        with timeout(30):
            self._random_showcase_buy(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def random_showcase_buy_async(
        self,
        request: RandomShowcaseBuyRequest,
    ) -> RandomShowcaseBuyResult:
        async_result = []
        self._random_showcase_buy(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _random_showcase_buy_by_user_id(
        self,
        request: RandomShowcaseBuyByUserIdRequest,
        callback: Callable[[AsyncResult[RandomShowcaseBuyByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="showcase",
            component='randomDisplayItem',
            function='randomShowcaseBuyByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.showcase_name is not None:
            body["showcaseName"] = request.showcase_name
        if request.display_item_name is not None:
            body["displayItemName"] = request.display_item_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.quantity is not None:
            body["quantity"] = request.quantity
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
                result_type=RandomShowcaseBuyByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def random_showcase_buy_by_user_id(
        self,
        request: RandomShowcaseBuyByUserIdRequest,
    ) -> RandomShowcaseBuyByUserIdResult:
        async_result = []
        with timeout(30):
            self._random_showcase_buy_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def random_showcase_buy_by_user_id_async(
        self,
        request: RandomShowcaseBuyByUserIdRequest,
    ) -> RandomShowcaseBuyByUserIdResult:
        async_result = []
        self._random_showcase_buy_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result