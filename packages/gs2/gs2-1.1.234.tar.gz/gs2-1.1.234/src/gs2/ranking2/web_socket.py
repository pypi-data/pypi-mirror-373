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


class Gs2Ranking2WebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
        if request.log_setting is not None:
            body["logSetting"] = request.log_setting.to_dict()

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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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
            service="ranking2",
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

    def _describe_global_ranking_models(
        self,
        request: DescribeGlobalRankingModelsRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingModel',
            function='describeGlobalRankingModels',
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
                result_type=DescribeGlobalRankingModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_global_ranking_models(
        self,
        request: DescribeGlobalRankingModelsRequest,
    ) -> DescribeGlobalRankingModelsResult:
        async_result = []
        with timeout(30):
            self._describe_global_ranking_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_global_ranking_models_async(
        self,
        request: DescribeGlobalRankingModelsRequest,
    ) -> DescribeGlobalRankingModelsResult:
        async_result = []
        self._describe_global_ranking_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_global_ranking_model(
        self,
        request: GetGlobalRankingModelRequest,
        callback: Callable[[AsyncResult[GetGlobalRankingModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingModel',
            function='getGlobalRankingModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGlobalRankingModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_global_ranking_model(
        self,
        request: GetGlobalRankingModelRequest,
    ) -> GetGlobalRankingModelResult:
        async_result = []
        with timeout(30):
            self._get_global_ranking_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_global_ranking_model_async(
        self,
        request: GetGlobalRankingModelRequest,
    ) -> GetGlobalRankingModelResult:
        async_result = []
        self._get_global_ranking_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_global_ranking_model_masters(
        self,
        request: DescribeGlobalRankingModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingModelMaster',
            function='describeGlobalRankingModelMasters',
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
                result_type=DescribeGlobalRankingModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_global_ranking_model_masters(
        self,
        request: DescribeGlobalRankingModelMastersRequest,
    ) -> DescribeGlobalRankingModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_global_ranking_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_global_ranking_model_masters_async(
        self,
        request: DescribeGlobalRankingModelMastersRequest,
    ) -> DescribeGlobalRankingModelMastersResult:
        async_result = []
        self._describe_global_ranking_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_global_ranking_model_master(
        self,
        request: CreateGlobalRankingModelMasterRequest,
        callback: Callable[[AsyncResult[CreateGlobalRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingModelMaster',
            function='createGlobalRankingModelMaster',
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
        if request.minimum_value is not None:
            body["minimumValue"] = request.minimum_value
        if request.maximum_value is not None:
            body["maximumValue"] = request.maximum_value
        if request.sum is not None:
            body["sum"] = request.sum
        if request.order_direction is not None:
            body["orderDirection"] = request.order_direction
        if request.ranking_rewards is not None:
            body["rankingRewards"] = [
                item.to_dict()
                for item in request.ranking_rewards
            ]
        if request.reward_calculation_index is not None:
            body["rewardCalculationIndex"] = request.reward_calculation_index
        if request.entry_period_event_id is not None:
            body["entryPeriodEventId"] = request.entry_period_event_id
        if request.access_period_event_id is not None:
            body["accessPeriodEventId"] = request.access_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateGlobalRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_global_ranking_model_master(
        self,
        request: CreateGlobalRankingModelMasterRequest,
    ) -> CreateGlobalRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_global_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_global_ranking_model_master_async(
        self,
        request: CreateGlobalRankingModelMasterRequest,
    ) -> CreateGlobalRankingModelMasterResult:
        async_result = []
        self._create_global_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_global_ranking_model_master(
        self,
        request: GetGlobalRankingModelMasterRequest,
        callback: Callable[[AsyncResult[GetGlobalRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingModelMaster',
            function='getGlobalRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGlobalRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_global_ranking_model_master(
        self,
        request: GetGlobalRankingModelMasterRequest,
    ) -> GetGlobalRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_global_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_global_ranking_model_master_async(
        self,
        request: GetGlobalRankingModelMasterRequest,
    ) -> GetGlobalRankingModelMasterResult:
        async_result = []
        self._get_global_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_global_ranking_model_master(
        self,
        request: UpdateGlobalRankingModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateGlobalRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingModelMaster',
            function='updateGlobalRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.minimum_value is not None:
            body["minimumValue"] = request.minimum_value
        if request.maximum_value is not None:
            body["maximumValue"] = request.maximum_value
        if request.sum is not None:
            body["sum"] = request.sum
        if request.order_direction is not None:
            body["orderDirection"] = request.order_direction
        if request.ranking_rewards is not None:
            body["rankingRewards"] = [
                item.to_dict()
                for item in request.ranking_rewards
            ]
        if request.reward_calculation_index is not None:
            body["rewardCalculationIndex"] = request.reward_calculation_index
        if request.entry_period_event_id is not None:
            body["entryPeriodEventId"] = request.entry_period_event_id
        if request.access_period_event_id is not None:
            body["accessPeriodEventId"] = request.access_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateGlobalRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_global_ranking_model_master(
        self,
        request: UpdateGlobalRankingModelMasterRequest,
    ) -> UpdateGlobalRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_global_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_global_ranking_model_master_async(
        self,
        request: UpdateGlobalRankingModelMasterRequest,
    ) -> UpdateGlobalRankingModelMasterResult:
        async_result = []
        self._update_global_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_global_ranking_model_master(
        self,
        request: DeleteGlobalRankingModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteGlobalRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingModelMaster',
            function='deleteGlobalRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteGlobalRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_global_ranking_model_master(
        self,
        request: DeleteGlobalRankingModelMasterRequest,
    ) -> DeleteGlobalRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_global_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_global_ranking_model_master_async(
        self,
        request: DeleteGlobalRankingModelMasterRequest,
    ) -> DeleteGlobalRankingModelMasterResult:
        async_result = []
        self._delete_global_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_global_ranking_scores(
        self,
        request: DescribeGlobalRankingScoresRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingScoresResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='describeGlobalRankingScores',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
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
                result_type=DescribeGlobalRankingScoresResult,
                callback=callback,
                body=body,
            )
        )

    def describe_global_ranking_scores(
        self,
        request: DescribeGlobalRankingScoresRequest,
    ) -> DescribeGlobalRankingScoresResult:
        async_result = []
        with timeout(30):
            self._describe_global_ranking_scores(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_global_ranking_scores_async(
        self,
        request: DescribeGlobalRankingScoresRequest,
    ) -> DescribeGlobalRankingScoresResult:
        async_result = []
        self._describe_global_ranking_scores(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_global_ranking_scores_by_user_id(
        self,
        request: DescribeGlobalRankingScoresByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingScoresByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='describeGlobalRankingScoresByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
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
                result_type=DescribeGlobalRankingScoresByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_global_ranking_scores_by_user_id(
        self,
        request: DescribeGlobalRankingScoresByUserIdRequest,
    ) -> DescribeGlobalRankingScoresByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_global_ranking_scores_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_global_ranking_scores_by_user_id_async(
        self,
        request: DescribeGlobalRankingScoresByUserIdRequest,
    ) -> DescribeGlobalRankingScoresByUserIdResult:
        async_result = []
        self._describe_global_ranking_scores_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _put_global_ranking_score(
        self,
        request: PutGlobalRankingScoreRequest,
        callback: Callable[[AsyncResult[PutGlobalRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='putGlobalRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PutGlobalRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def put_global_ranking_score(
        self,
        request: PutGlobalRankingScoreRequest,
    ) -> PutGlobalRankingScoreResult:
        async_result = []
        with timeout(30):
            self._put_global_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_global_ranking_score_async(
        self,
        request: PutGlobalRankingScoreRequest,
    ) -> PutGlobalRankingScoreResult:
        async_result = []
        self._put_global_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _put_global_ranking_score_by_user_id(
        self,
        request: PutGlobalRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[PutGlobalRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='putGlobalRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PutGlobalRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def put_global_ranking_score_by_user_id(
        self,
        request: PutGlobalRankingScoreByUserIdRequest,
    ) -> PutGlobalRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._put_global_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_global_ranking_score_by_user_id_async(
        self,
        request: PutGlobalRankingScoreByUserIdRequest,
    ) -> PutGlobalRankingScoreByUserIdResult:
        async_result = []
        self._put_global_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_global_ranking_score(
        self,
        request: GetGlobalRankingScoreRequest,
        callback: Callable[[AsyncResult[GetGlobalRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='getGlobalRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGlobalRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def get_global_ranking_score(
        self,
        request: GetGlobalRankingScoreRequest,
    ) -> GetGlobalRankingScoreResult:
        async_result = []
        with timeout(30):
            self._get_global_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_global_ranking_score_async(
        self,
        request: GetGlobalRankingScoreRequest,
    ) -> GetGlobalRankingScoreResult:
        async_result = []
        self._get_global_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_global_ranking_score_by_user_id(
        self,
        request: GetGlobalRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[GetGlobalRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='getGlobalRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGlobalRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_global_ranking_score_by_user_id(
        self,
        request: GetGlobalRankingScoreByUserIdRequest,
    ) -> GetGlobalRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_global_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_global_ranking_score_by_user_id_async(
        self,
        request: GetGlobalRankingScoreByUserIdRequest,
    ) -> GetGlobalRankingScoreByUserIdResult:
        async_result = []
        self._get_global_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_global_ranking_score_by_user_id(
        self,
        request: DeleteGlobalRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteGlobalRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='deleteGlobalRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteGlobalRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_global_ranking_score_by_user_id(
        self,
        request: DeleteGlobalRankingScoreByUserIdRequest,
    ) -> DeleteGlobalRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_global_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_global_ranking_score_by_user_id_async(
        self,
        request: DeleteGlobalRankingScoreByUserIdRequest,
    ) -> DeleteGlobalRankingScoreByUserIdResult:
        async_result = []
        self._delete_global_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_global_ranking_score(
        self,
        request: VerifyGlobalRankingScoreRequest,
        callback: Callable[[AsyncResult[VerifyGlobalRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='verifyGlobalRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
                result_type=VerifyGlobalRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def verify_global_ranking_score(
        self,
        request: VerifyGlobalRankingScoreRequest,
    ) -> VerifyGlobalRankingScoreResult:
        async_result = []
        with timeout(30):
            self._verify_global_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_global_ranking_score_async(
        self,
        request: VerifyGlobalRankingScoreRequest,
    ) -> VerifyGlobalRankingScoreResult:
        async_result = []
        self._verify_global_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_global_ranking_score_by_user_id(
        self,
        request: VerifyGlobalRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyGlobalRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='verifyGlobalRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
                result_type=VerifyGlobalRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_global_ranking_score_by_user_id(
        self,
        request: VerifyGlobalRankingScoreByUserIdRequest,
    ) -> VerifyGlobalRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_global_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_global_ranking_score_by_user_id_async(
        self,
        request: VerifyGlobalRankingScoreByUserIdRequest,
    ) -> VerifyGlobalRankingScoreByUserIdResult:
        async_result = []
        self._verify_global_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_global_ranking_score_by_stamp_task(
        self,
        request: VerifyGlobalRankingScoreByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyGlobalRankingScoreByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingScore',
            function='verifyGlobalRankingScoreByStampTask',
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
                result_type=VerifyGlobalRankingScoreByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_global_ranking_score_by_stamp_task(
        self,
        request: VerifyGlobalRankingScoreByStampTaskRequest,
    ) -> VerifyGlobalRankingScoreByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_global_ranking_score_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_global_ranking_score_by_stamp_task_async(
        self,
        request: VerifyGlobalRankingScoreByStampTaskRequest,
    ) -> VerifyGlobalRankingScoreByStampTaskResult:
        async_result = []
        self._verify_global_ranking_score_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_global_ranking_received_rewards(
        self,
        request: DescribeGlobalRankingReceivedRewardsRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingReceivedRewardsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='describeGlobalRankingReceivedRewards',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeGlobalRankingReceivedRewardsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_global_ranking_received_rewards(
        self,
        request: DescribeGlobalRankingReceivedRewardsRequest,
    ) -> DescribeGlobalRankingReceivedRewardsResult:
        async_result = []
        with timeout(30):
            self._describe_global_ranking_received_rewards(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_global_ranking_received_rewards_async(
        self,
        request: DescribeGlobalRankingReceivedRewardsRequest,
    ) -> DescribeGlobalRankingReceivedRewardsResult:
        async_result = []
        self._describe_global_ranking_received_rewards(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_global_ranking_received_rewards_by_user_id(
        self,
        request: DescribeGlobalRankingReceivedRewardsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingReceivedRewardsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='describeGlobalRankingReceivedRewardsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeGlobalRankingReceivedRewardsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_global_ranking_received_rewards_by_user_id(
        self,
        request: DescribeGlobalRankingReceivedRewardsByUserIdRequest,
    ) -> DescribeGlobalRankingReceivedRewardsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_global_ranking_received_rewards_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_global_ranking_received_rewards_by_user_id_async(
        self,
        request: DescribeGlobalRankingReceivedRewardsByUserIdRequest,
    ) -> DescribeGlobalRankingReceivedRewardsByUserIdResult:
        async_result = []
        self._describe_global_ranking_received_rewards_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_global_ranking_received_reward(
        self,
        request: CreateGlobalRankingReceivedRewardRequest,
        callback: Callable[[AsyncResult[CreateGlobalRankingReceivedRewardResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='createGlobalRankingReceivedReward',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateGlobalRankingReceivedRewardResult,
                callback=callback,
                body=body,
            )
        )

    def create_global_ranking_received_reward(
        self,
        request: CreateGlobalRankingReceivedRewardRequest,
    ) -> CreateGlobalRankingReceivedRewardResult:
        async_result = []
        with timeout(30):
            self._create_global_ranking_received_reward(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_global_ranking_received_reward_async(
        self,
        request: CreateGlobalRankingReceivedRewardRequest,
    ) -> CreateGlobalRankingReceivedRewardResult:
        async_result = []
        self._create_global_ranking_received_reward(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_global_ranking_received_reward_by_user_id(
        self,
        request: CreateGlobalRankingReceivedRewardByUserIdRequest,
        callback: Callable[[AsyncResult[CreateGlobalRankingReceivedRewardByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='createGlobalRankingReceivedRewardByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateGlobalRankingReceivedRewardByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_global_ranking_received_reward_by_user_id(
        self,
        request: CreateGlobalRankingReceivedRewardByUserIdRequest,
    ) -> CreateGlobalRankingReceivedRewardByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_global_ranking_received_reward_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_global_ranking_received_reward_by_user_id_async(
        self,
        request: CreateGlobalRankingReceivedRewardByUserIdRequest,
    ) -> CreateGlobalRankingReceivedRewardByUserIdResult:
        async_result = []
        self._create_global_ranking_received_reward_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _receive_global_ranking_received_reward(
        self,
        request: ReceiveGlobalRankingReceivedRewardRequest,
        callback: Callable[[AsyncResult[ReceiveGlobalRankingReceivedRewardResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='receiveGlobalRankingReceivedReward',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=ReceiveGlobalRankingReceivedRewardResult,
                callback=callback,
                body=body,
            )
        )

    def receive_global_ranking_received_reward(
        self,
        request: ReceiveGlobalRankingReceivedRewardRequest,
    ) -> ReceiveGlobalRankingReceivedRewardResult:
        async_result = []
        with timeout(30):
            self._receive_global_ranking_received_reward(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def receive_global_ranking_received_reward_async(
        self,
        request: ReceiveGlobalRankingReceivedRewardRequest,
    ) -> ReceiveGlobalRankingReceivedRewardResult:
        async_result = []
        self._receive_global_ranking_received_reward(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _receive_global_ranking_received_reward_by_user_id(
        self,
        request: ReceiveGlobalRankingReceivedRewardByUserIdRequest,
        callback: Callable[[AsyncResult[ReceiveGlobalRankingReceivedRewardByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='receiveGlobalRankingReceivedRewardByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=ReceiveGlobalRankingReceivedRewardByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def receive_global_ranking_received_reward_by_user_id(
        self,
        request: ReceiveGlobalRankingReceivedRewardByUserIdRequest,
    ) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        async_result = []
        with timeout(30):
            self._receive_global_ranking_received_reward_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def receive_global_ranking_received_reward_by_user_id_async(
        self,
        request: ReceiveGlobalRankingReceivedRewardByUserIdRequest,
    ) -> ReceiveGlobalRankingReceivedRewardByUserIdResult:
        async_result = []
        self._receive_global_ranking_received_reward_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_global_ranking_received_reward(
        self,
        request: GetGlobalRankingReceivedRewardRequest,
        callback: Callable[[AsyncResult[GetGlobalRankingReceivedRewardResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='getGlobalRankingReceivedReward',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGlobalRankingReceivedRewardResult,
                callback=callback,
                body=body,
            )
        )

    def get_global_ranking_received_reward(
        self,
        request: GetGlobalRankingReceivedRewardRequest,
    ) -> GetGlobalRankingReceivedRewardResult:
        async_result = []
        with timeout(30):
            self._get_global_ranking_received_reward(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_global_ranking_received_reward_async(
        self,
        request: GetGlobalRankingReceivedRewardRequest,
    ) -> GetGlobalRankingReceivedRewardResult:
        async_result = []
        self._get_global_ranking_received_reward(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_global_ranking_received_reward_by_user_id(
        self,
        request: GetGlobalRankingReceivedRewardByUserIdRequest,
        callback: Callable[[AsyncResult[GetGlobalRankingReceivedRewardByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='getGlobalRankingReceivedRewardByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGlobalRankingReceivedRewardByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_global_ranking_received_reward_by_user_id(
        self,
        request: GetGlobalRankingReceivedRewardByUserIdRequest,
    ) -> GetGlobalRankingReceivedRewardByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_global_ranking_received_reward_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_global_ranking_received_reward_by_user_id_async(
        self,
        request: GetGlobalRankingReceivedRewardByUserIdRequest,
    ) -> GetGlobalRankingReceivedRewardByUserIdResult:
        async_result = []
        self._get_global_ranking_received_reward_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_global_ranking_received_reward_by_user_id(
        self,
        request: DeleteGlobalRankingReceivedRewardByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteGlobalRankingReceivedRewardByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='deleteGlobalRankingReceivedRewardByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteGlobalRankingReceivedRewardByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_global_ranking_received_reward_by_user_id(
        self,
        request: DeleteGlobalRankingReceivedRewardByUserIdRequest,
    ) -> DeleteGlobalRankingReceivedRewardByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_global_ranking_received_reward_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_global_ranking_received_reward_by_user_id_async(
        self,
        request: DeleteGlobalRankingReceivedRewardByUserIdRequest,
    ) -> DeleteGlobalRankingReceivedRewardByUserIdResult:
        async_result = []
        self._delete_global_ranking_received_reward_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_global_ranking_received_reward_by_stamp_task(
        self,
        request: CreateGlobalRankingReceivedRewardByStampTaskRequest,
        callback: Callable[[AsyncResult[CreateGlobalRankingReceivedRewardByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingReceivedReward',
            function='createGlobalRankingReceivedRewardByStampTask',
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
                result_type=CreateGlobalRankingReceivedRewardByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def create_global_ranking_received_reward_by_stamp_task(
        self,
        request: CreateGlobalRankingReceivedRewardByStampTaskRequest,
    ) -> CreateGlobalRankingReceivedRewardByStampTaskResult:
        async_result = []
        with timeout(30):
            self._create_global_ranking_received_reward_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_global_ranking_received_reward_by_stamp_task_async(
        self,
        request: CreateGlobalRankingReceivedRewardByStampTaskRequest,
    ) -> CreateGlobalRankingReceivedRewardByStampTaskResult:
        async_result = []
        self._create_global_ranking_received_reward_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_global_rankings(
        self,
        request: DescribeGlobalRankingsRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingData',
            function='describeGlobalRankings',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeGlobalRankingsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_global_rankings(
        self,
        request: DescribeGlobalRankingsRequest,
    ) -> DescribeGlobalRankingsResult:
        async_result = []
        with timeout(30):
            self._describe_global_rankings(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_global_rankings_async(
        self,
        request: DescribeGlobalRankingsRequest,
    ) -> DescribeGlobalRankingsResult:
        async_result = []
        self._describe_global_rankings(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_global_rankings_by_user_id(
        self,
        request: DescribeGlobalRankingsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeGlobalRankingsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingData',
            function='describeGlobalRankingsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeGlobalRankingsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_global_rankings_by_user_id(
        self,
        request: DescribeGlobalRankingsByUserIdRequest,
    ) -> DescribeGlobalRankingsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_global_rankings_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_global_rankings_by_user_id_async(
        self,
        request: DescribeGlobalRankingsByUserIdRequest,
    ) -> DescribeGlobalRankingsByUserIdResult:
        async_result = []
        self._describe_global_rankings_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_global_ranking(
        self,
        request: GetGlobalRankingRequest,
        callback: Callable[[AsyncResult[GetGlobalRankingResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingData',
            function='getGlobalRanking',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGlobalRankingResult,
                callback=callback,
                body=body,
            )
        )

    def get_global_ranking(
        self,
        request: GetGlobalRankingRequest,
    ) -> GetGlobalRankingResult:
        async_result = []
        with timeout(30):
            self._get_global_ranking(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_global_ranking_async(
        self,
        request: GetGlobalRankingRequest,
    ) -> GetGlobalRankingResult:
        async_result = []
        self._get_global_ranking(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_global_ranking_by_user_id(
        self,
        request: GetGlobalRankingByUserIdRequest,
        callback: Callable[[AsyncResult[GetGlobalRankingByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='globalRankingData',
            function='getGlobalRankingByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGlobalRankingByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_global_ranking_by_user_id(
        self,
        request: GetGlobalRankingByUserIdRequest,
    ) -> GetGlobalRankingByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_global_ranking_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_global_ranking_by_user_id_async(
        self,
        request: GetGlobalRankingByUserIdRequest,
    ) -> GetGlobalRankingByUserIdResult:
        async_result = []
        self._get_global_ranking_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_cluster_ranking_models(
        self,
        request: DescribeClusterRankingModelsRequest,
        callback: Callable[[AsyncResult[DescribeClusterRankingModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingModel',
            function='describeClusterRankingModels',
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
                result_type=DescribeClusterRankingModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_cluster_ranking_models(
        self,
        request: DescribeClusterRankingModelsRequest,
    ) -> DescribeClusterRankingModelsResult:
        async_result = []
        with timeout(30):
            self._describe_cluster_ranking_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_cluster_ranking_models_async(
        self,
        request: DescribeClusterRankingModelsRequest,
    ) -> DescribeClusterRankingModelsResult:
        async_result = []
        self._describe_cluster_ranking_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_cluster_ranking_model(
        self,
        request: GetClusterRankingModelRequest,
        callback: Callable[[AsyncResult[GetClusterRankingModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingModel',
            function='getClusterRankingModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetClusterRankingModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_cluster_ranking_model(
        self,
        request: GetClusterRankingModelRequest,
    ) -> GetClusterRankingModelResult:
        async_result = []
        with timeout(30):
            self._get_cluster_ranking_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cluster_ranking_model_async(
        self,
        request: GetClusterRankingModelRequest,
    ) -> GetClusterRankingModelResult:
        async_result = []
        self._get_cluster_ranking_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_cluster_ranking_model_masters(
        self,
        request: DescribeClusterRankingModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeClusterRankingModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingModelMaster',
            function='describeClusterRankingModelMasters',
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
                result_type=DescribeClusterRankingModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_cluster_ranking_model_masters(
        self,
        request: DescribeClusterRankingModelMastersRequest,
    ) -> DescribeClusterRankingModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_cluster_ranking_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_cluster_ranking_model_masters_async(
        self,
        request: DescribeClusterRankingModelMastersRequest,
    ) -> DescribeClusterRankingModelMastersResult:
        async_result = []
        self._describe_cluster_ranking_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_cluster_ranking_model_master(
        self,
        request: CreateClusterRankingModelMasterRequest,
        callback: Callable[[AsyncResult[CreateClusterRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingModelMaster',
            function='createClusterRankingModelMaster',
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
        if request.cluster_type is not None:
            body["clusterType"] = request.cluster_type
        if request.minimum_value is not None:
            body["minimumValue"] = request.minimum_value
        if request.maximum_value is not None:
            body["maximumValue"] = request.maximum_value
        if request.sum is not None:
            body["sum"] = request.sum
        if request.order_direction is not None:
            body["orderDirection"] = request.order_direction
        if request.ranking_rewards is not None:
            body["rankingRewards"] = [
                item.to_dict()
                for item in request.ranking_rewards
            ]
        if request.reward_calculation_index is not None:
            body["rewardCalculationIndex"] = request.reward_calculation_index
        if request.entry_period_event_id is not None:
            body["entryPeriodEventId"] = request.entry_period_event_id
        if request.access_period_event_id is not None:
            body["accessPeriodEventId"] = request.access_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateClusterRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_cluster_ranking_model_master(
        self,
        request: CreateClusterRankingModelMasterRequest,
    ) -> CreateClusterRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_cluster_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_cluster_ranking_model_master_async(
        self,
        request: CreateClusterRankingModelMasterRequest,
    ) -> CreateClusterRankingModelMasterResult:
        async_result = []
        self._create_cluster_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_cluster_ranking_model_master(
        self,
        request: GetClusterRankingModelMasterRequest,
        callback: Callable[[AsyncResult[GetClusterRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingModelMaster',
            function='getClusterRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetClusterRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_cluster_ranking_model_master(
        self,
        request: GetClusterRankingModelMasterRequest,
    ) -> GetClusterRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_cluster_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cluster_ranking_model_master_async(
        self,
        request: GetClusterRankingModelMasterRequest,
    ) -> GetClusterRankingModelMasterResult:
        async_result = []
        self._get_cluster_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_cluster_ranking_model_master(
        self,
        request: UpdateClusterRankingModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateClusterRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingModelMaster',
            function='updateClusterRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.cluster_type is not None:
            body["clusterType"] = request.cluster_type
        if request.minimum_value is not None:
            body["minimumValue"] = request.minimum_value
        if request.maximum_value is not None:
            body["maximumValue"] = request.maximum_value
        if request.sum is not None:
            body["sum"] = request.sum
        if request.order_direction is not None:
            body["orderDirection"] = request.order_direction
        if request.ranking_rewards is not None:
            body["rankingRewards"] = [
                item.to_dict()
                for item in request.ranking_rewards
            ]
        if request.reward_calculation_index is not None:
            body["rewardCalculationIndex"] = request.reward_calculation_index
        if request.entry_period_event_id is not None:
            body["entryPeriodEventId"] = request.entry_period_event_id
        if request.access_period_event_id is not None:
            body["accessPeriodEventId"] = request.access_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateClusterRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_cluster_ranking_model_master(
        self,
        request: UpdateClusterRankingModelMasterRequest,
    ) -> UpdateClusterRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_cluster_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_cluster_ranking_model_master_async(
        self,
        request: UpdateClusterRankingModelMasterRequest,
    ) -> UpdateClusterRankingModelMasterResult:
        async_result = []
        self._update_cluster_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_cluster_ranking_model_master(
        self,
        request: DeleteClusterRankingModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteClusterRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingModelMaster',
            function='deleteClusterRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteClusterRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_cluster_ranking_model_master(
        self,
        request: DeleteClusterRankingModelMasterRequest,
    ) -> DeleteClusterRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_cluster_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_cluster_ranking_model_master_async(
        self,
        request: DeleteClusterRankingModelMasterRequest,
    ) -> DeleteClusterRankingModelMasterResult:
        async_result = []
        self._delete_cluster_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_cluster_ranking_scores(
        self,
        request: DescribeClusterRankingScoresRequest,
        callback: Callable[[AsyncResult[DescribeClusterRankingScoresResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='describeClusterRankingScores',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeClusterRankingScoresResult,
                callback=callback,
                body=body,
            )
        )

    def describe_cluster_ranking_scores(
        self,
        request: DescribeClusterRankingScoresRequest,
    ) -> DescribeClusterRankingScoresResult:
        async_result = []
        with timeout(30):
            self._describe_cluster_ranking_scores(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_cluster_ranking_scores_async(
        self,
        request: DescribeClusterRankingScoresRequest,
    ) -> DescribeClusterRankingScoresResult:
        async_result = []
        self._describe_cluster_ranking_scores(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_cluster_ranking_scores_by_user_id(
        self,
        request: DescribeClusterRankingScoresByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeClusterRankingScoresByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='describeClusterRankingScoresByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeClusterRankingScoresByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_cluster_ranking_scores_by_user_id(
        self,
        request: DescribeClusterRankingScoresByUserIdRequest,
    ) -> DescribeClusterRankingScoresByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_cluster_ranking_scores_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_cluster_ranking_scores_by_user_id_async(
        self,
        request: DescribeClusterRankingScoresByUserIdRequest,
    ) -> DescribeClusterRankingScoresByUserIdResult:
        async_result = []
        self._describe_cluster_ranking_scores_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _put_cluster_ranking_score(
        self,
        request: PutClusterRankingScoreRequest,
        callback: Callable[[AsyncResult[PutClusterRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='putClusterRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PutClusterRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def put_cluster_ranking_score(
        self,
        request: PutClusterRankingScoreRequest,
    ) -> PutClusterRankingScoreResult:
        async_result = []
        with timeout(30):
            self._put_cluster_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_cluster_ranking_score_async(
        self,
        request: PutClusterRankingScoreRequest,
    ) -> PutClusterRankingScoreResult:
        async_result = []
        self._put_cluster_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _put_cluster_ranking_score_by_user_id(
        self,
        request: PutClusterRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[PutClusterRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='putClusterRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PutClusterRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def put_cluster_ranking_score_by_user_id(
        self,
        request: PutClusterRankingScoreByUserIdRequest,
    ) -> PutClusterRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._put_cluster_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_cluster_ranking_score_by_user_id_async(
        self,
        request: PutClusterRankingScoreByUserIdRequest,
    ) -> PutClusterRankingScoreByUserIdResult:
        async_result = []
        self._put_cluster_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_cluster_ranking_score(
        self,
        request: GetClusterRankingScoreRequest,
        callback: Callable[[AsyncResult[GetClusterRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='getClusterRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetClusterRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def get_cluster_ranking_score(
        self,
        request: GetClusterRankingScoreRequest,
    ) -> GetClusterRankingScoreResult:
        async_result = []
        with timeout(30):
            self._get_cluster_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cluster_ranking_score_async(
        self,
        request: GetClusterRankingScoreRequest,
    ) -> GetClusterRankingScoreResult:
        async_result = []
        self._get_cluster_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_cluster_ranking_score_by_user_id(
        self,
        request: GetClusterRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[GetClusterRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='getClusterRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetClusterRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_cluster_ranking_score_by_user_id(
        self,
        request: GetClusterRankingScoreByUserIdRequest,
    ) -> GetClusterRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_cluster_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cluster_ranking_score_by_user_id_async(
        self,
        request: GetClusterRankingScoreByUserIdRequest,
    ) -> GetClusterRankingScoreByUserIdResult:
        async_result = []
        self._get_cluster_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_cluster_ranking_score_by_user_id(
        self,
        request: DeleteClusterRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteClusterRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='deleteClusterRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteClusterRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_cluster_ranking_score_by_user_id(
        self,
        request: DeleteClusterRankingScoreByUserIdRequest,
    ) -> DeleteClusterRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_cluster_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_cluster_ranking_score_by_user_id_async(
        self,
        request: DeleteClusterRankingScoreByUserIdRequest,
    ) -> DeleteClusterRankingScoreByUserIdResult:
        async_result = []
        self._delete_cluster_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_cluster_ranking_score(
        self,
        request: VerifyClusterRankingScoreRequest,
        callback: Callable[[AsyncResult[VerifyClusterRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='verifyClusterRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
                result_type=VerifyClusterRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def verify_cluster_ranking_score(
        self,
        request: VerifyClusterRankingScoreRequest,
    ) -> VerifyClusterRankingScoreResult:
        async_result = []
        with timeout(30):
            self._verify_cluster_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_cluster_ranking_score_async(
        self,
        request: VerifyClusterRankingScoreRequest,
    ) -> VerifyClusterRankingScoreResult:
        async_result = []
        self._verify_cluster_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_cluster_ranking_score_by_user_id(
        self,
        request: VerifyClusterRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyClusterRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='verifyClusterRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
                result_type=VerifyClusterRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_cluster_ranking_score_by_user_id(
        self,
        request: VerifyClusterRankingScoreByUserIdRequest,
    ) -> VerifyClusterRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_cluster_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_cluster_ranking_score_by_user_id_async(
        self,
        request: VerifyClusterRankingScoreByUserIdRequest,
    ) -> VerifyClusterRankingScoreByUserIdResult:
        async_result = []
        self._verify_cluster_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_cluster_ranking_score_by_stamp_task(
        self,
        request: VerifyClusterRankingScoreByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyClusterRankingScoreByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingScore',
            function='verifyClusterRankingScoreByStampTask',
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
                result_type=VerifyClusterRankingScoreByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_cluster_ranking_score_by_stamp_task(
        self,
        request: VerifyClusterRankingScoreByStampTaskRequest,
    ) -> VerifyClusterRankingScoreByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_cluster_ranking_score_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_cluster_ranking_score_by_stamp_task_async(
        self,
        request: VerifyClusterRankingScoreByStampTaskRequest,
    ) -> VerifyClusterRankingScoreByStampTaskResult:
        async_result = []
        self._verify_cluster_ranking_score_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_cluster_ranking_received_rewards(
        self,
        request: DescribeClusterRankingReceivedRewardsRequest,
        callback: Callable[[AsyncResult[DescribeClusterRankingReceivedRewardsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='describeClusterRankingReceivedRewards',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeClusterRankingReceivedRewardsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_cluster_ranking_received_rewards(
        self,
        request: DescribeClusterRankingReceivedRewardsRequest,
    ) -> DescribeClusterRankingReceivedRewardsResult:
        async_result = []
        with timeout(30):
            self._describe_cluster_ranking_received_rewards(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_cluster_ranking_received_rewards_async(
        self,
        request: DescribeClusterRankingReceivedRewardsRequest,
    ) -> DescribeClusterRankingReceivedRewardsResult:
        async_result = []
        self._describe_cluster_ranking_received_rewards(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_cluster_ranking_received_rewards_by_user_id(
        self,
        request: DescribeClusterRankingReceivedRewardsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeClusterRankingReceivedRewardsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='describeClusterRankingReceivedRewardsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeClusterRankingReceivedRewardsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_cluster_ranking_received_rewards_by_user_id(
        self,
        request: DescribeClusterRankingReceivedRewardsByUserIdRequest,
    ) -> DescribeClusterRankingReceivedRewardsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_cluster_ranking_received_rewards_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_cluster_ranking_received_rewards_by_user_id_async(
        self,
        request: DescribeClusterRankingReceivedRewardsByUserIdRequest,
    ) -> DescribeClusterRankingReceivedRewardsByUserIdResult:
        async_result = []
        self._describe_cluster_ranking_received_rewards_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_cluster_ranking_received_reward(
        self,
        request: CreateClusterRankingReceivedRewardRequest,
        callback: Callable[[AsyncResult[CreateClusterRankingReceivedRewardResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='createClusterRankingReceivedReward',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateClusterRankingReceivedRewardResult,
                callback=callback,
                body=body,
            )
        )

    def create_cluster_ranking_received_reward(
        self,
        request: CreateClusterRankingReceivedRewardRequest,
    ) -> CreateClusterRankingReceivedRewardResult:
        async_result = []
        with timeout(30):
            self._create_cluster_ranking_received_reward(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_cluster_ranking_received_reward_async(
        self,
        request: CreateClusterRankingReceivedRewardRequest,
    ) -> CreateClusterRankingReceivedRewardResult:
        async_result = []
        self._create_cluster_ranking_received_reward(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_cluster_ranking_received_reward_by_user_id(
        self,
        request: CreateClusterRankingReceivedRewardByUserIdRequest,
        callback: Callable[[AsyncResult[CreateClusterRankingReceivedRewardByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='createClusterRankingReceivedRewardByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateClusterRankingReceivedRewardByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_cluster_ranking_received_reward_by_user_id(
        self,
        request: CreateClusterRankingReceivedRewardByUserIdRequest,
    ) -> CreateClusterRankingReceivedRewardByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_cluster_ranking_received_reward_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_cluster_ranking_received_reward_by_user_id_async(
        self,
        request: CreateClusterRankingReceivedRewardByUserIdRequest,
    ) -> CreateClusterRankingReceivedRewardByUserIdResult:
        async_result = []
        self._create_cluster_ranking_received_reward_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _receive_cluster_ranking_received_reward(
        self,
        request: ReceiveClusterRankingReceivedRewardRequest,
        callback: Callable[[AsyncResult[ReceiveClusterRankingReceivedRewardResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='receiveClusterRankingReceivedReward',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=ReceiveClusterRankingReceivedRewardResult,
                callback=callback,
                body=body,
            )
        )

    def receive_cluster_ranking_received_reward(
        self,
        request: ReceiveClusterRankingReceivedRewardRequest,
    ) -> ReceiveClusterRankingReceivedRewardResult:
        async_result = []
        with timeout(30):
            self._receive_cluster_ranking_received_reward(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def receive_cluster_ranking_received_reward_async(
        self,
        request: ReceiveClusterRankingReceivedRewardRequest,
    ) -> ReceiveClusterRankingReceivedRewardResult:
        async_result = []
        self._receive_cluster_ranking_received_reward(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _receive_cluster_ranking_received_reward_by_user_id(
        self,
        request: ReceiveClusterRankingReceivedRewardByUserIdRequest,
        callback: Callable[[AsyncResult[ReceiveClusterRankingReceivedRewardByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='receiveClusterRankingReceivedRewardByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=ReceiveClusterRankingReceivedRewardByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def receive_cluster_ranking_received_reward_by_user_id(
        self,
        request: ReceiveClusterRankingReceivedRewardByUserIdRequest,
    ) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        async_result = []
        with timeout(30):
            self._receive_cluster_ranking_received_reward_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def receive_cluster_ranking_received_reward_by_user_id_async(
        self,
        request: ReceiveClusterRankingReceivedRewardByUserIdRequest,
    ) -> ReceiveClusterRankingReceivedRewardByUserIdResult:
        async_result = []
        self._receive_cluster_ranking_received_reward_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_cluster_ranking_received_reward(
        self,
        request: GetClusterRankingReceivedRewardRequest,
        callback: Callable[[AsyncResult[GetClusterRankingReceivedRewardResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='getClusterRankingReceivedReward',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetClusterRankingReceivedRewardResult,
                callback=callback,
                body=body,
            )
        )

    def get_cluster_ranking_received_reward(
        self,
        request: GetClusterRankingReceivedRewardRequest,
    ) -> GetClusterRankingReceivedRewardResult:
        async_result = []
        with timeout(30):
            self._get_cluster_ranking_received_reward(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cluster_ranking_received_reward_async(
        self,
        request: GetClusterRankingReceivedRewardRequest,
    ) -> GetClusterRankingReceivedRewardResult:
        async_result = []
        self._get_cluster_ranking_received_reward(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_cluster_ranking_received_reward_by_user_id(
        self,
        request: GetClusterRankingReceivedRewardByUserIdRequest,
        callback: Callable[[AsyncResult[GetClusterRankingReceivedRewardByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='getClusterRankingReceivedRewardByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetClusterRankingReceivedRewardByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_cluster_ranking_received_reward_by_user_id(
        self,
        request: GetClusterRankingReceivedRewardByUserIdRequest,
    ) -> GetClusterRankingReceivedRewardByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_cluster_ranking_received_reward_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cluster_ranking_received_reward_by_user_id_async(
        self,
        request: GetClusterRankingReceivedRewardByUserIdRequest,
    ) -> GetClusterRankingReceivedRewardByUserIdResult:
        async_result = []
        self._get_cluster_ranking_received_reward_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_cluster_ranking_received_reward_by_user_id(
        self,
        request: DeleteClusterRankingReceivedRewardByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteClusterRankingReceivedRewardByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='deleteClusterRankingReceivedRewardByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteClusterRankingReceivedRewardByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_cluster_ranking_received_reward_by_user_id(
        self,
        request: DeleteClusterRankingReceivedRewardByUserIdRequest,
    ) -> DeleteClusterRankingReceivedRewardByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_cluster_ranking_received_reward_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_cluster_ranking_received_reward_by_user_id_async(
        self,
        request: DeleteClusterRankingReceivedRewardByUserIdRequest,
    ) -> DeleteClusterRankingReceivedRewardByUserIdResult:
        async_result = []
        self._delete_cluster_ranking_received_reward_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_cluster_ranking_received_reward_by_stamp_task(
        self,
        request: CreateClusterRankingReceivedRewardByStampTaskRequest,
        callback: Callable[[AsyncResult[CreateClusterRankingReceivedRewardByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingReceivedReward',
            function='createClusterRankingReceivedRewardByStampTask',
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
                result_type=CreateClusterRankingReceivedRewardByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def create_cluster_ranking_received_reward_by_stamp_task(
        self,
        request: CreateClusterRankingReceivedRewardByStampTaskRequest,
    ) -> CreateClusterRankingReceivedRewardByStampTaskResult:
        async_result = []
        with timeout(30):
            self._create_cluster_ranking_received_reward_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_cluster_ranking_received_reward_by_stamp_task_async(
        self,
        request: CreateClusterRankingReceivedRewardByStampTaskRequest,
    ) -> CreateClusterRankingReceivedRewardByStampTaskResult:
        async_result = []
        self._create_cluster_ranking_received_reward_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_cluster_rankings(
        self,
        request: DescribeClusterRankingsRequest,
        callback: Callable[[AsyncResult[DescribeClusterRankingsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingData',
            function='describeClusterRankings',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeClusterRankingsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_cluster_rankings(
        self,
        request: DescribeClusterRankingsRequest,
    ) -> DescribeClusterRankingsResult:
        async_result = []
        with timeout(30):
            self._describe_cluster_rankings(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_cluster_rankings_async(
        self,
        request: DescribeClusterRankingsRequest,
    ) -> DescribeClusterRankingsResult:
        async_result = []
        self._describe_cluster_rankings(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_cluster_rankings_by_user_id(
        self,
        request: DescribeClusterRankingsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeClusterRankingsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingData',
            function='describeClusterRankingsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeClusterRankingsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_cluster_rankings_by_user_id(
        self,
        request: DescribeClusterRankingsByUserIdRequest,
    ) -> DescribeClusterRankingsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_cluster_rankings_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_cluster_rankings_by_user_id_async(
        self,
        request: DescribeClusterRankingsByUserIdRequest,
    ) -> DescribeClusterRankingsByUserIdResult:
        async_result = []
        self._describe_cluster_rankings_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_cluster_ranking(
        self,
        request: GetClusterRankingRequest,
        callback: Callable[[AsyncResult[GetClusterRankingResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingData',
            function='getClusterRanking',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetClusterRankingResult,
                callback=callback,
                body=body,
            )
        )

    def get_cluster_ranking(
        self,
        request: GetClusterRankingRequest,
    ) -> GetClusterRankingResult:
        async_result = []
        with timeout(30):
            self._get_cluster_ranking(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cluster_ranking_async(
        self,
        request: GetClusterRankingRequest,
    ) -> GetClusterRankingResult:
        async_result = []
        self._get_cluster_ranking(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_cluster_ranking_by_user_id(
        self,
        request: GetClusterRankingByUserIdRequest,
        callback: Callable[[AsyncResult[GetClusterRankingByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='clusterRankingData',
            function='getClusterRankingByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.cluster_name is not None:
            body["clusterName"] = request.cluster_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetClusterRankingByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_cluster_ranking_by_user_id(
        self,
        request: GetClusterRankingByUserIdRequest,
    ) -> GetClusterRankingByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_cluster_ranking_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_cluster_ranking_by_user_id_async(
        self,
        request: GetClusterRankingByUserIdRequest,
    ) -> GetClusterRankingByUserIdResult:
        async_result = []
        self._get_cluster_ranking_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribe_ranking_models(
        self,
        request: DescribeSubscribeRankingModelsRequest,
        callback: Callable[[AsyncResult[DescribeSubscribeRankingModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingModel',
            function='describeSubscribeRankingModels',
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
                result_type=DescribeSubscribeRankingModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribe_ranking_models(
        self,
        request: DescribeSubscribeRankingModelsRequest,
    ) -> DescribeSubscribeRankingModelsResult:
        async_result = []
        with timeout(30):
            self._describe_subscribe_ranking_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribe_ranking_models_async(
        self,
        request: DescribeSubscribeRankingModelsRequest,
    ) -> DescribeSubscribeRankingModelsResult:
        async_result = []
        self._describe_subscribe_ranking_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_subscribe_ranking_model(
        self,
        request: GetSubscribeRankingModelRequest,
        callback: Callable[[AsyncResult[GetSubscribeRankingModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingModel',
            function='getSubscribeRankingModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeRankingModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe_ranking_model(
        self,
        request: GetSubscribeRankingModelRequest,
    ) -> GetSubscribeRankingModelResult:
        async_result = []
        with timeout(30):
            self._get_subscribe_ranking_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_ranking_model_async(
        self,
        request: GetSubscribeRankingModelRequest,
    ) -> GetSubscribeRankingModelResult:
        async_result = []
        self._get_subscribe_ranking_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribe_ranking_model_masters(
        self,
        request: DescribeSubscribeRankingModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeSubscribeRankingModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingModelMaster',
            function='describeSubscribeRankingModelMasters',
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
                result_type=DescribeSubscribeRankingModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribe_ranking_model_masters(
        self,
        request: DescribeSubscribeRankingModelMastersRequest,
    ) -> DescribeSubscribeRankingModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_subscribe_ranking_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribe_ranking_model_masters_async(
        self,
        request: DescribeSubscribeRankingModelMastersRequest,
    ) -> DescribeSubscribeRankingModelMastersResult:
        async_result = []
        self._describe_subscribe_ranking_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_subscribe_ranking_model_master(
        self,
        request: CreateSubscribeRankingModelMasterRequest,
        callback: Callable[[AsyncResult[CreateSubscribeRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingModelMaster',
            function='createSubscribeRankingModelMaster',
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
        if request.minimum_value is not None:
            body["minimumValue"] = request.minimum_value
        if request.maximum_value is not None:
            body["maximumValue"] = request.maximum_value
        if request.sum is not None:
            body["sum"] = request.sum
        if request.order_direction is not None:
            body["orderDirection"] = request.order_direction
        if request.entry_period_event_id is not None:
            body["entryPeriodEventId"] = request.entry_period_event_id
        if request.access_period_event_id is not None:
            body["accessPeriodEventId"] = request.access_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateSubscribeRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_subscribe_ranking_model_master(
        self,
        request: CreateSubscribeRankingModelMasterRequest,
    ) -> CreateSubscribeRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_subscribe_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_subscribe_ranking_model_master_async(
        self,
        request: CreateSubscribeRankingModelMasterRequest,
    ) -> CreateSubscribeRankingModelMasterResult:
        async_result = []
        self._create_subscribe_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_subscribe_ranking_model_master(
        self,
        request: GetSubscribeRankingModelMasterRequest,
        callback: Callable[[AsyncResult[GetSubscribeRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingModelMaster',
            function='getSubscribeRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe_ranking_model_master(
        self,
        request: GetSubscribeRankingModelMasterRequest,
    ) -> GetSubscribeRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_subscribe_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_ranking_model_master_async(
        self,
        request: GetSubscribeRankingModelMasterRequest,
    ) -> GetSubscribeRankingModelMasterResult:
        async_result = []
        self._get_subscribe_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_subscribe_ranking_model_master(
        self,
        request: UpdateSubscribeRankingModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateSubscribeRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingModelMaster',
            function='updateSubscribeRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.minimum_value is not None:
            body["minimumValue"] = request.minimum_value
        if request.maximum_value is not None:
            body["maximumValue"] = request.maximum_value
        if request.sum is not None:
            body["sum"] = request.sum
        if request.order_direction is not None:
            body["orderDirection"] = request.order_direction
        if request.entry_period_event_id is not None:
            body["entryPeriodEventId"] = request.entry_period_event_id
        if request.access_period_event_id is not None:
            body["accessPeriodEventId"] = request.access_period_event_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateSubscribeRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_subscribe_ranking_model_master(
        self,
        request: UpdateSubscribeRankingModelMasterRequest,
    ) -> UpdateSubscribeRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_subscribe_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_subscribe_ranking_model_master_async(
        self,
        request: UpdateSubscribeRankingModelMasterRequest,
    ) -> UpdateSubscribeRankingModelMasterResult:
        async_result = []
        self._update_subscribe_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_subscribe_ranking_model_master(
        self,
        request: DeleteSubscribeRankingModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteSubscribeRankingModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingModelMaster',
            function='deleteSubscribeRankingModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteSubscribeRankingModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_subscribe_ranking_model_master(
        self,
        request: DeleteSubscribeRankingModelMasterRequest,
    ) -> DeleteSubscribeRankingModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_subscribe_ranking_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_subscribe_ranking_model_master_async(
        self,
        request: DeleteSubscribeRankingModelMasterRequest,
    ) -> DeleteSubscribeRankingModelMasterResult:
        async_result = []
        self._delete_subscribe_ranking_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribes(
        self,
        request: DescribeSubscribesRequest,
        callback: Callable[[AsyncResult[DescribeSubscribesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribe',
            function='describeSubscribes',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
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
                result_type=DescribeSubscribesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribes(
        self,
        request: DescribeSubscribesRequest,
    ) -> DescribeSubscribesResult:
        async_result = []
        with timeout(30):
            self._describe_subscribes(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribes_async(
        self,
        request: DescribeSubscribesRequest,
    ) -> DescribeSubscribesResult:
        async_result = []
        self._describe_subscribes(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribes_by_user_id(
        self,
        request: DescribeSubscribesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeSubscribesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribe',
            function='describeSubscribesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
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
                result_type=DescribeSubscribesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribes_by_user_id(
        self,
        request: DescribeSubscribesByUserIdRequest,
    ) -> DescribeSubscribesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_subscribes_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribes_by_user_id_async(
        self,
        request: DescribeSubscribesByUserIdRequest,
    ) -> DescribeSubscribesByUserIdResult:
        async_result = []
        self._describe_subscribes_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_subscribe(
        self,
        request: AddSubscribeRequest,
        callback: Callable[[AsyncResult[AddSubscribeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribe',
            function='addSubscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AddSubscribeResult,
                callback=callback,
                body=body,
            )
        )

    def add_subscribe(
        self,
        request: AddSubscribeRequest,
    ) -> AddSubscribeResult:
        async_result = []
        with timeout(30):
            self._add_subscribe(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_subscribe_async(
        self,
        request: AddSubscribeRequest,
    ) -> AddSubscribeResult:
        async_result = []
        self._add_subscribe(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_subscribe_by_user_id(
        self,
        request: AddSubscribeByUserIdRequest,
        callback: Callable[[AsyncResult[AddSubscribeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribe',
            function='addSubscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AddSubscribeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_subscribe_by_user_id(
        self,
        request: AddSubscribeByUserIdRequest,
    ) -> AddSubscribeByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_subscribe_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_subscribe_by_user_id_async(
        self,
        request: AddSubscribeByUserIdRequest,
    ) -> AddSubscribeByUserIdResult:
        async_result = []
        self._add_subscribe_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribe_ranking_scores(
        self,
        request: DescribeSubscribeRankingScoresRequest,
        callback: Callable[[AsyncResult[DescribeSubscribeRankingScoresResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='describeSubscribeRankingScores',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
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
                result_type=DescribeSubscribeRankingScoresResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribe_ranking_scores(
        self,
        request: DescribeSubscribeRankingScoresRequest,
    ) -> DescribeSubscribeRankingScoresResult:
        async_result = []
        with timeout(30):
            self._describe_subscribe_ranking_scores(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribe_ranking_scores_async(
        self,
        request: DescribeSubscribeRankingScoresRequest,
    ) -> DescribeSubscribeRankingScoresResult:
        async_result = []
        self._describe_subscribe_ranking_scores(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribe_ranking_scores_by_user_id(
        self,
        request: DescribeSubscribeRankingScoresByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeSubscribeRankingScoresByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='describeSubscribeRankingScoresByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
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
                result_type=DescribeSubscribeRankingScoresByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribe_ranking_scores_by_user_id(
        self,
        request: DescribeSubscribeRankingScoresByUserIdRequest,
    ) -> DescribeSubscribeRankingScoresByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_subscribe_ranking_scores_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribe_ranking_scores_by_user_id_async(
        self,
        request: DescribeSubscribeRankingScoresByUserIdRequest,
    ) -> DescribeSubscribeRankingScoresByUserIdResult:
        async_result = []
        self._describe_subscribe_ranking_scores_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _put_subscribe_ranking_score(
        self,
        request: PutSubscribeRankingScoreRequest,
        callback: Callable[[AsyncResult[PutSubscribeRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='putSubscribeRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PutSubscribeRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def put_subscribe_ranking_score(
        self,
        request: PutSubscribeRankingScoreRequest,
    ) -> PutSubscribeRankingScoreResult:
        async_result = []
        with timeout(30):
            self._put_subscribe_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_subscribe_ranking_score_async(
        self,
        request: PutSubscribeRankingScoreRequest,
    ) -> PutSubscribeRankingScoreResult:
        async_result = []
        self._put_subscribe_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _put_subscribe_ranking_score_by_user_id(
        self,
        request: PutSubscribeRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[PutSubscribeRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='putSubscribeRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.score is not None:
            body["score"] = request.score
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PutSubscribeRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def put_subscribe_ranking_score_by_user_id(
        self,
        request: PutSubscribeRankingScoreByUserIdRequest,
    ) -> PutSubscribeRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._put_subscribe_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def put_subscribe_ranking_score_by_user_id_async(
        self,
        request: PutSubscribeRankingScoreByUserIdRequest,
    ) -> PutSubscribeRankingScoreByUserIdResult:
        async_result = []
        self._put_subscribe_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_subscribe_ranking_score(
        self,
        request: GetSubscribeRankingScoreRequest,
        callback: Callable[[AsyncResult[GetSubscribeRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='getSubscribeRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe_ranking_score(
        self,
        request: GetSubscribeRankingScoreRequest,
    ) -> GetSubscribeRankingScoreResult:
        async_result = []
        with timeout(30):
            self._get_subscribe_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_ranking_score_async(
        self,
        request: GetSubscribeRankingScoreRequest,
    ) -> GetSubscribeRankingScoreResult:
        async_result = []
        self._get_subscribe_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_subscribe_ranking_score_by_user_id(
        self,
        request: GetSubscribeRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[GetSubscribeRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='getSubscribeRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe_ranking_score_by_user_id(
        self,
        request: GetSubscribeRankingScoreByUserIdRequest,
    ) -> GetSubscribeRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_subscribe_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_ranking_score_by_user_id_async(
        self,
        request: GetSubscribeRankingScoreByUserIdRequest,
    ) -> GetSubscribeRankingScoreByUserIdResult:
        async_result = []
        self._get_subscribe_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_subscribe_ranking_score_by_user_id(
        self,
        request: DeleteSubscribeRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteSubscribeRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='deleteSubscribeRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteSubscribeRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_subscribe_ranking_score_by_user_id(
        self,
        request: DeleteSubscribeRankingScoreByUserIdRequest,
    ) -> DeleteSubscribeRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_subscribe_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_subscribe_ranking_score_by_user_id_async(
        self,
        request: DeleteSubscribeRankingScoreByUserIdRequest,
    ) -> DeleteSubscribeRankingScoreByUserIdResult:
        async_result = []
        self._delete_subscribe_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_subscribe_ranking_score(
        self,
        request: VerifySubscribeRankingScoreRequest,
        callback: Callable[[AsyncResult[VerifySubscribeRankingScoreResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='verifySubscribeRankingScore',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
                result_type=VerifySubscribeRankingScoreResult,
                callback=callback,
                body=body,
            )
        )

    def verify_subscribe_ranking_score(
        self,
        request: VerifySubscribeRankingScoreRequest,
    ) -> VerifySubscribeRankingScoreResult:
        async_result = []
        with timeout(30):
            self._verify_subscribe_ranking_score(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_subscribe_ranking_score_async(
        self,
        request: VerifySubscribeRankingScoreRequest,
    ) -> VerifySubscribeRankingScoreResult:
        async_result = []
        self._verify_subscribe_ranking_score(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_subscribe_ranking_score_by_user_id(
        self,
        request: VerifySubscribeRankingScoreByUserIdRequest,
        callback: Callable[[AsyncResult[VerifySubscribeRankingScoreByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='verifySubscribeRankingScoreByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.season is not None:
            body["season"] = request.season
        if request.score is not None:
            body["score"] = request.score
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
                result_type=VerifySubscribeRankingScoreByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_subscribe_ranking_score_by_user_id(
        self,
        request: VerifySubscribeRankingScoreByUserIdRequest,
    ) -> VerifySubscribeRankingScoreByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_subscribe_ranking_score_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_subscribe_ranking_score_by_user_id_async(
        self,
        request: VerifySubscribeRankingScoreByUserIdRequest,
    ) -> VerifySubscribeRankingScoreByUserIdResult:
        async_result = []
        self._verify_subscribe_ranking_score_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_subscribe_ranking_score_by_stamp_task(
        self,
        request: VerifySubscribeRankingScoreByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifySubscribeRankingScoreByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingScore',
            function='verifySubscribeRankingScoreByStampTask',
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
                result_type=VerifySubscribeRankingScoreByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_subscribe_ranking_score_by_stamp_task(
        self,
        request: VerifySubscribeRankingScoreByStampTaskRequest,
    ) -> VerifySubscribeRankingScoreByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_subscribe_ranking_score_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_subscribe_ranking_score_by_stamp_task_async(
        self,
        request: VerifySubscribeRankingScoreByStampTaskRequest,
    ) -> VerifySubscribeRankingScoreByStampTaskResult:
        async_result = []
        self._verify_subscribe_ranking_score_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribe_rankings(
        self,
        request: DescribeSubscribeRankingsRequest,
        callback: Callable[[AsyncResult[DescribeSubscribeRankingsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingData',
            function='describeSubscribeRankings',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeSubscribeRankingsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribe_rankings(
        self,
        request: DescribeSubscribeRankingsRequest,
    ) -> DescribeSubscribeRankingsResult:
        async_result = []
        with timeout(30):
            self._describe_subscribe_rankings(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribe_rankings_async(
        self,
        request: DescribeSubscribeRankingsRequest,
    ) -> DescribeSubscribeRankingsResult:
        async_result = []
        self._describe_subscribe_rankings(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_subscribe_rankings_by_user_id(
        self,
        request: DescribeSubscribeRankingsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeSubscribeRankingsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingData',
            function='describeSubscribeRankingsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.season is not None:
            body["season"] = request.season
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
                result_type=DescribeSubscribeRankingsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribe_rankings_by_user_id(
        self,
        request: DescribeSubscribeRankingsByUserIdRequest,
    ) -> DescribeSubscribeRankingsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_subscribe_rankings_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribe_rankings_by_user_id_async(
        self,
        request: DescribeSubscribeRankingsByUserIdRequest,
    ) -> DescribeSubscribeRankingsByUserIdResult:
        async_result = []
        self._describe_subscribe_rankings_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_subscribe_ranking(
        self,
        request: GetSubscribeRankingRequest,
        callback: Callable[[AsyncResult[GetSubscribeRankingResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingData',
            function='getSubscribeRanking',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.season is not None:
            body["season"] = request.season
        if request.scorer_user_id is not None:
            body["scorerUserId"] = request.scorer_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeRankingResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe_ranking(
        self,
        request: GetSubscribeRankingRequest,
    ) -> GetSubscribeRankingResult:
        async_result = []
        with timeout(30):
            self._get_subscribe_ranking(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_ranking_async(
        self,
        request: GetSubscribeRankingRequest,
    ) -> GetSubscribeRankingResult:
        async_result = []
        self._get_subscribe_ranking(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_subscribe_ranking_by_user_id(
        self,
        request: GetSubscribeRankingByUserIdRequest,
        callback: Callable[[AsyncResult[GetSubscribeRankingByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeRankingData',
            function='getSubscribeRankingByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.season is not None:
            body["season"] = request.season
        if request.scorer_user_id is not None:
            body["scorerUserId"] = request.scorer_user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeRankingByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe_ranking_by_user_id(
        self,
        request: GetSubscribeRankingByUserIdRequest,
    ) -> GetSubscribeRankingByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_subscribe_ranking_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_ranking_by_user_id_async(
        self,
        request: GetSubscribeRankingByUserIdRequest,
    ) -> GetSubscribeRankingByUserIdResult:
        async_result = []
        self._get_subscribe_ranking_by_user_id(
            request,
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
            service="ranking2",
            component='currentRankingMaster',
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

    def _get_current_ranking_master(
        self,
        request: GetCurrentRankingMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentRankingMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='currentRankingMaster',
            function='getCurrentRankingMaster',
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
                result_type=GetCurrentRankingMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_ranking_master(
        self,
        request: GetCurrentRankingMasterRequest,
    ) -> GetCurrentRankingMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_ranking_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_ranking_master_async(
        self,
        request: GetCurrentRankingMasterRequest,
    ) -> GetCurrentRankingMasterResult:
        async_result = []
        self._get_current_ranking_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _pre_update_current_ranking_master(
        self,
        request: PreUpdateCurrentRankingMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentRankingMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='currentRankingMaster',
            function='preUpdateCurrentRankingMaster',
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
                result_type=PreUpdateCurrentRankingMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_ranking_master(
        self,
        request: PreUpdateCurrentRankingMasterRequest,
    ) -> PreUpdateCurrentRankingMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_ranking_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_ranking_master_async(
        self,
        request: PreUpdateCurrentRankingMasterRequest,
    ) -> PreUpdateCurrentRankingMasterResult:
        async_result = []
        self._pre_update_current_ranking_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_ranking_master(
        self,
        request: UpdateCurrentRankingMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentRankingMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='currentRankingMaster',
            function='updateCurrentRankingMaster',
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
                result_type=UpdateCurrentRankingMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_ranking_master(
        self,
        request: UpdateCurrentRankingMasterRequest,
    ) -> UpdateCurrentRankingMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_ranking_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_ranking_master_async(
        self,
        request: UpdateCurrentRankingMasterRequest,
    ) -> UpdateCurrentRankingMasterResult:
        async_result = []
        self._update_current_ranking_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_ranking_master_from_git_hub(
        self,
        request: UpdateCurrentRankingMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentRankingMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='currentRankingMaster',
            function='updateCurrentRankingMasterFromGitHub',
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
                result_type=UpdateCurrentRankingMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_ranking_master_from_git_hub(
        self,
        request: UpdateCurrentRankingMasterFromGitHubRequest,
    ) -> UpdateCurrentRankingMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_ranking_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_ranking_master_from_git_hub_async(
        self,
        request: UpdateCurrentRankingMasterFromGitHubRequest,
    ) -> UpdateCurrentRankingMasterFromGitHubResult:
        async_result = []
        self._update_current_ranking_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_subscribe(
        self,
        request: GetSubscribeRequest,
        callback: Callable[[AsyncResult[GetSubscribeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeUser',
            function='getSubscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe(
        self,
        request: GetSubscribeRequest,
    ) -> GetSubscribeResult:
        async_result = []
        with timeout(30):
            self._get_subscribe(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_async(
        self,
        request: GetSubscribeRequest,
    ) -> GetSubscribeResult:
        async_result = []
        self._get_subscribe(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_subscribe_by_user_id(
        self,
        request: GetSubscribeByUserIdRequest,
        callback: Callable[[AsyncResult[GetSubscribeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeUser',
            function='getSubscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSubscribeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_subscribe_by_user_id(
        self,
        request: GetSubscribeByUserIdRequest,
    ) -> GetSubscribeByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_subscribe_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_subscribe_by_user_id_async(
        self,
        request: GetSubscribeByUserIdRequest,
    ) -> GetSubscribeByUserIdResult:
        async_result = []
        self._get_subscribe_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_subscribe(
        self,
        request: DeleteSubscribeRequest,
        callback: Callable[[AsyncResult[DeleteSubscribeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeUser',
            function='deleteSubscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteSubscribeResult,
                callback=callback,
                body=body,
            )
        )

    def delete_subscribe(
        self,
        request: DeleteSubscribeRequest,
    ) -> DeleteSubscribeResult:
        async_result = []
        with timeout(30):
            self._delete_subscribe(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_subscribe_async(
        self,
        request: DeleteSubscribeRequest,
    ) -> DeleteSubscribeResult:
        async_result = []
        self._delete_subscribe(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_subscribe_by_user_id(
        self,
        request: DeleteSubscribeByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteSubscribeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="ranking2",
            component='subscribeUser',
            function='deleteSubscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.ranking_name is not None:
            body["rankingName"] = request.ranking_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteSubscribeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_subscribe_by_user_id(
        self,
        request: DeleteSubscribeByUserIdRequest,
    ) -> DeleteSubscribeByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_subscribe_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_subscribe_by_user_id_async(
        self,
        request: DeleteSubscribeByUserIdRequest,
    ) -> DeleteSubscribeByUserIdResult:
        async_result = []
        self._delete_subscribe_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result