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


class Gs2EnchantWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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
            service="enchant",
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

    def _describe_balance_parameter_models(
        self,
        request: DescribeBalanceParameterModelsRequest,
        callback: Callable[[AsyncResult[DescribeBalanceParameterModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterModel',
            function='describeBalanceParameterModels',
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
                result_type=DescribeBalanceParameterModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_balance_parameter_models(
        self,
        request: DescribeBalanceParameterModelsRequest,
    ) -> DescribeBalanceParameterModelsResult:
        async_result = []
        with timeout(30):
            self._describe_balance_parameter_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_balance_parameter_models_async(
        self,
        request: DescribeBalanceParameterModelsRequest,
    ) -> DescribeBalanceParameterModelsResult:
        async_result = []
        self._describe_balance_parameter_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_balance_parameter_model(
        self,
        request: GetBalanceParameterModelRequest,
        callback: Callable[[AsyncResult[GetBalanceParameterModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterModel',
            function='getBalanceParameterModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetBalanceParameterModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_balance_parameter_model(
        self,
        request: GetBalanceParameterModelRequest,
    ) -> GetBalanceParameterModelResult:
        async_result = []
        with timeout(30):
            self._get_balance_parameter_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_balance_parameter_model_async(
        self,
        request: GetBalanceParameterModelRequest,
    ) -> GetBalanceParameterModelResult:
        async_result = []
        self._get_balance_parameter_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_balance_parameter_model_masters(
        self,
        request: DescribeBalanceParameterModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeBalanceParameterModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterModelMaster',
            function='describeBalanceParameterModelMasters',
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
                result_type=DescribeBalanceParameterModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_balance_parameter_model_masters(
        self,
        request: DescribeBalanceParameterModelMastersRequest,
    ) -> DescribeBalanceParameterModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_balance_parameter_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_balance_parameter_model_masters_async(
        self,
        request: DescribeBalanceParameterModelMastersRequest,
    ) -> DescribeBalanceParameterModelMastersResult:
        async_result = []
        self._describe_balance_parameter_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_balance_parameter_model_master(
        self,
        request: CreateBalanceParameterModelMasterRequest,
        callback: Callable[[AsyncResult[CreateBalanceParameterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterModelMaster',
            function='createBalanceParameterModelMaster',
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
        if request.total_value is not None:
            body["totalValue"] = request.total_value
        if request.initial_value_strategy is not None:
            body["initialValueStrategy"] = request.initial_value_strategy
        if request.parameters is not None:
            body["parameters"] = [
                item.to_dict()
                for item in request.parameters
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateBalanceParameterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_balance_parameter_model_master(
        self,
        request: CreateBalanceParameterModelMasterRequest,
    ) -> CreateBalanceParameterModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_balance_parameter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_balance_parameter_model_master_async(
        self,
        request: CreateBalanceParameterModelMasterRequest,
    ) -> CreateBalanceParameterModelMasterResult:
        async_result = []
        self._create_balance_parameter_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_balance_parameter_model_master(
        self,
        request: GetBalanceParameterModelMasterRequest,
        callback: Callable[[AsyncResult[GetBalanceParameterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterModelMaster',
            function='getBalanceParameterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetBalanceParameterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_balance_parameter_model_master(
        self,
        request: GetBalanceParameterModelMasterRequest,
    ) -> GetBalanceParameterModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_balance_parameter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_balance_parameter_model_master_async(
        self,
        request: GetBalanceParameterModelMasterRequest,
    ) -> GetBalanceParameterModelMasterResult:
        async_result = []
        self._get_balance_parameter_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_balance_parameter_model_master(
        self,
        request: UpdateBalanceParameterModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateBalanceParameterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterModelMaster',
            function='updateBalanceParameterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.total_value is not None:
            body["totalValue"] = request.total_value
        if request.initial_value_strategy is not None:
            body["initialValueStrategy"] = request.initial_value_strategy
        if request.parameters is not None:
            body["parameters"] = [
                item.to_dict()
                for item in request.parameters
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateBalanceParameterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_balance_parameter_model_master(
        self,
        request: UpdateBalanceParameterModelMasterRequest,
    ) -> UpdateBalanceParameterModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_balance_parameter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_balance_parameter_model_master_async(
        self,
        request: UpdateBalanceParameterModelMasterRequest,
    ) -> UpdateBalanceParameterModelMasterResult:
        async_result = []
        self._update_balance_parameter_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_balance_parameter_model_master(
        self,
        request: DeleteBalanceParameterModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteBalanceParameterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterModelMaster',
            function='deleteBalanceParameterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteBalanceParameterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_balance_parameter_model_master(
        self,
        request: DeleteBalanceParameterModelMasterRequest,
    ) -> DeleteBalanceParameterModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_balance_parameter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_balance_parameter_model_master_async(
        self,
        request: DeleteBalanceParameterModelMasterRequest,
    ) -> DeleteBalanceParameterModelMasterResult:
        async_result = []
        self._delete_balance_parameter_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_rarity_parameter_models(
        self,
        request: DescribeRarityParameterModelsRequest,
        callback: Callable[[AsyncResult[DescribeRarityParameterModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterModel',
            function='describeRarityParameterModels',
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
                result_type=DescribeRarityParameterModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_rarity_parameter_models(
        self,
        request: DescribeRarityParameterModelsRequest,
    ) -> DescribeRarityParameterModelsResult:
        async_result = []
        with timeout(30):
            self._describe_rarity_parameter_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rarity_parameter_models_async(
        self,
        request: DescribeRarityParameterModelsRequest,
    ) -> DescribeRarityParameterModelsResult:
        async_result = []
        self._describe_rarity_parameter_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_rarity_parameter_model(
        self,
        request: GetRarityParameterModelRequest,
        callback: Callable[[AsyncResult[GetRarityParameterModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterModel',
            function='getRarityParameterModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRarityParameterModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_rarity_parameter_model(
        self,
        request: GetRarityParameterModelRequest,
    ) -> GetRarityParameterModelResult:
        async_result = []
        with timeout(30):
            self._get_rarity_parameter_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rarity_parameter_model_async(
        self,
        request: GetRarityParameterModelRequest,
    ) -> GetRarityParameterModelResult:
        async_result = []
        self._get_rarity_parameter_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_rarity_parameter_model_masters(
        self,
        request: DescribeRarityParameterModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeRarityParameterModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterModelMaster',
            function='describeRarityParameterModelMasters',
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
                result_type=DescribeRarityParameterModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_rarity_parameter_model_masters(
        self,
        request: DescribeRarityParameterModelMastersRequest,
    ) -> DescribeRarityParameterModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_rarity_parameter_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rarity_parameter_model_masters_async(
        self,
        request: DescribeRarityParameterModelMastersRequest,
    ) -> DescribeRarityParameterModelMastersResult:
        async_result = []
        self._describe_rarity_parameter_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_rarity_parameter_model_master(
        self,
        request: CreateRarityParameterModelMasterRequest,
        callback: Callable[[AsyncResult[CreateRarityParameterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterModelMaster',
            function='createRarityParameterModelMaster',
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
        if request.maximum_parameter_count is not None:
            body["maximumParameterCount"] = request.maximum_parameter_count
        if request.parameter_counts is not None:
            body["parameterCounts"] = [
                item.to_dict()
                for item in request.parameter_counts
            ]
        if request.parameters is not None:
            body["parameters"] = [
                item.to_dict()
                for item in request.parameters
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateRarityParameterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_rarity_parameter_model_master(
        self,
        request: CreateRarityParameterModelMasterRequest,
    ) -> CreateRarityParameterModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_rarity_parameter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_rarity_parameter_model_master_async(
        self,
        request: CreateRarityParameterModelMasterRequest,
    ) -> CreateRarityParameterModelMasterResult:
        async_result = []
        self._create_rarity_parameter_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_rarity_parameter_model_master(
        self,
        request: GetRarityParameterModelMasterRequest,
        callback: Callable[[AsyncResult[GetRarityParameterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterModelMaster',
            function='getRarityParameterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRarityParameterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_rarity_parameter_model_master(
        self,
        request: GetRarityParameterModelMasterRequest,
    ) -> GetRarityParameterModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_rarity_parameter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rarity_parameter_model_master_async(
        self,
        request: GetRarityParameterModelMasterRequest,
    ) -> GetRarityParameterModelMasterResult:
        async_result = []
        self._get_rarity_parameter_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_rarity_parameter_model_master(
        self,
        request: UpdateRarityParameterModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateRarityParameterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterModelMaster',
            function='updateRarityParameterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.maximum_parameter_count is not None:
            body["maximumParameterCount"] = request.maximum_parameter_count
        if request.parameter_counts is not None:
            body["parameterCounts"] = [
                item.to_dict()
                for item in request.parameter_counts
            ]
        if request.parameters is not None:
            body["parameters"] = [
                item.to_dict()
                for item in request.parameters
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateRarityParameterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_rarity_parameter_model_master(
        self,
        request: UpdateRarityParameterModelMasterRequest,
    ) -> UpdateRarityParameterModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_rarity_parameter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_rarity_parameter_model_master_async(
        self,
        request: UpdateRarityParameterModelMasterRequest,
    ) -> UpdateRarityParameterModelMasterResult:
        async_result = []
        self._update_rarity_parameter_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_rarity_parameter_model_master(
        self,
        request: DeleteRarityParameterModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteRarityParameterModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterModelMaster',
            function='deleteRarityParameterModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteRarityParameterModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_rarity_parameter_model_master(
        self,
        request: DeleteRarityParameterModelMasterRequest,
    ) -> DeleteRarityParameterModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_rarity_parameter_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_rarity_parameter_model_master_async(
        self,
        request: DeleteRarityParameterModelMasterRequest,
    ) -> DeleteRarityParameterModelMasterResult:
        async_result = []
        self._delete_rarity_parameter_model_master(
            request,
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
            service="enchant",
            component='currentParameterMaster',
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

    def _get_current_parameter_master(
        self,
        request: GetCurrentParameterMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentParameterMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='currentParameterMaster',
            function='getCurrentParameterMaster',
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
                result_type=GetCurrentParameterMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_parameter_master(
        self,
        request: GetCurrentParameterMasterRequest,
    ) -> GetCurrentParameterMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_parameter_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_parameter_master_async(
        self,
        request: GetCurrentParameterMasterRequest,
    ) -> GetCurrentParameterMasterResult:
        async_result = []
        self._get_current_parameter_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _pre_update_current_parameter_master(
        self,
        request: PreUpdateCurrentParameterMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentParameterMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='currentParameterMaster',
            function='preUpdateCurrentParameterMaster',
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
                result_type=PreUpdateCurrentParameterMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_parameter_master(
        self,
        request: PreUpdateCurrentParameterMasterRequest,
    ) -> PreUpdateCurrentParameterMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_parameter_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_parameter_master_async(
        self,
        request: PreUpdateCurrentParameterMasterRequest,
    ) -> PreUpdateCurrentParameterMasterResult:
        async_result = []
        self._pre_update_current_parameter_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_parameter_master(
        self,
        request: UpdateCurrentParameterMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentParameterMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='currentParameterMaster',
            function='updateCurrentParameterMaster',
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
                result_type=UpdateCurrentParameterMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_parameter_master(
        self,
        request: UpdateCurrentParameterMasterRequest,
    ) -> UpdateCurrentParameterMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_parameter_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_parameter_master_async(
        self,
        request: UpdateCurrentParameterMasterRequest,
    ) -> UpdateCurrentParameterMasterResult:
        async_result = []
        self._update_current_parameter_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_parameter_master_from_git_hub(
        self,
        request: UpdateCurrentParameterMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentParameterMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='currentParameterMaster',
            function='updateCurrentParameterMasterFromGitHub',
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
                result_type=UpdateCurrentParameterMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_parameter_master_from_git_hub(
        self,
        request: UpdateCurrentParameterMasterFromGitHubRequest,
    ) -> UpdateCurrentParameterMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_parameter_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_parameter_master_from_git_hub_async(
        self,
        request: UpdateCurrentParameterMasterFromGitHubRequest,
    ) -> UpdateCurrentParameterMasterFromGitHubResult:
        async_result = []
        self._update_current_parameter_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_balance_parameter_statuses(
        self,
        request: DescribeBalanceParameterStatusesRequest,
        callback: Callable[[AsyncResult[DescribeBalanceParameterStatusesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='describeBalanceParameterStatuses',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
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
                result_type=DescribeBalanceParameterStatusesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_balance_parameter_statuses(
        self,
        request: DescribeBalanceParameterStatusesRequest,
    ) -> DescribeBalanceParameterStatusesResult:
        async_result = []
        with timeout(30):
            self._describe_balance_parameter_statuses(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_balance_parameter_statuses_async(
        self,
        request: DescribeBalanceParameterStatusesRequest,
    ) -> DescribeBalanceParameterStatusesResult:
        async_result = []
        self._describe_balance_parameter_statuses(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_balance_parameter_statuses_by_user_id(
        self,
        request: DescribeBalanceParameterStatusesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeBalanceParameterStatusesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='describeBalanceParameterStatusesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
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
                result_type=DescribeBalanceParameterStatusesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_balance_parameter_statuses_by_user_id(
        self,
        request: DescribeBalanceParameterStatusesByUserIdRequest,
    ) -> DescribeBalanceParameterStatusesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_balance_parameter_statuses_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_balance_parameter_statuses_by_user_id_async(
        self,
        request: DescribeBalanceParameterStatusesByUserIdRequest,
    ) -> DescribeBalanceParameterStatusesByUserIdResult:
        async_result = []
        self._describe_balance_parameter_statuses_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_balance_parameter_status(
        self,
        request: GetBalanceParameterStatusRequest,
        callback: Callable[[AsyncResult[GetBalanceParameterStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='getBalanceParameterStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetBalanceParameterStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_balance_parameter_status(
        self,
        request: GetBalanceParameterStatusRequest,
    ) -> GetBalanceParameterStatusResult:
        async_result = []
        with timeout(30):
            self._get_balance_parameter_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_balance_parameter_status_async(
        self,
        request: GetBalanceParameterStatusRequest,
    ) -> GetBalanceParameterStatusResult:
        async_result = []
        self._get_balance_parameter_status(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_balance_parameter_status_by_user_id(
        self,
        request: GetBalanceParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[GetBalanceParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='getBalanceParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetBalanceParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_balance_parameter_status_by_user_id(
        self,
        request: GetBalanceParameterStatusByUserIdRequest,
    ) -> GetBalanceParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_balance_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_balance_parameter_status_by_user_id_async(
        self,
        request: GetBalanceParameterStatusByUserIdRequest,
    ) -> GetBalanceParameterStatusByUserIdResult:
        async_result = []
        self._get_balance_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_balance_parameter_status_by_user_id(
        self,
        request: DeleteBalanceParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteBalanceParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='deleteBalanceParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteBalanceParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_balance_parameter_status_by_user_id(
        self,
        request: DeleteBalanceParameterStatusByUserIdRequest,
    ) -> DeleteBalanceParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_balance_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_balance_parameter_status_by_user_id_async(
        self,
        request: DeleteBalanceParameterStatusByUserIdRequest,
    ) -> DeleteBalanceParameterStatusByUserIdResult:
        async_result = []
        self._delete_balance_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _re_draw_balance_parameter_status_by_user_id(
        self,
        request: ReDrawBalanceParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[ReDrawBalanceParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='reDrawBalanceParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.fixed_parameter_names is not None:
            body["fixedParameterNames"] = [
                item
                for item in request.fixed_parameter_names
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
                result_type=ReDrawBalanceParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def re_draw_balance_parameter_status_by_user_id(
        self,
        request: ReDrawBalanceParameterStatusByUserIdRequest,
    ) -> ReDrawBalanceParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._re_draw_balance_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def re_draw_balance_parameter_status_by_user_id_async(
        self,
        request: ReDrawBalanceParameterStatusByUserIdRequest,
    ) -> ReDrawBalanceParameterStatusByUserIdResult:
        async_result = []
        self._re_draw_balance_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _re_draw_balance_parameter_status_by_stamp_sheet(
        self,
        request: ReDrawBalanceParameterStatusByStampSheetRequest,
        callback: Callable[[AsyncResult[ReDrawBalanceParameterStatusByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='reDrawBalanceParameterStatusByStampSheet',
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
                result_type=ReDrawBalanceParameterStatusByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def re_draw_balance_parameter_status_by_stamp_sheet(
        self,
        request: ReDrawBalanceParameterStatusByStampSheetRequest,
    ) -> ReDrawBalanceParameterStatusByStampSheetResult:
        async_result = []
        with timeout(30):
            self._re_draw_balance_parameter_status_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def re_draw_balance_parameter_status_by_stamp_sheet_async(
        self,
        request: ReDrawBalanceParameterStatusByStampSheetRequest,
    ) -> ReDrawBalanceParameterStatusByStampSheetResult:
        async_result = []
        self._re_draw_balance_parameter_status_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_balance_parameter_status_by_user_id(
        self,
        request: SetBalanceParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[SetBalanceParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='setBalanceParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.parameter_values is not None:
            body["parameterValues"] = [
                item.to_dict()
                for item in request.parameter_values
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
                result_type=SetBalanceParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_balance_parameter_status_by_user_id(
        self,
        request: SetBalanceParameterStatusByUserIdRequest,
    ) -> SetBalanceParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_balance_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_balance_parameter_status_by_user_id_async(
        self,
        request: SetBalanceParameterStatusByUserIdRequest,
    ) -> SetBalanceParameterStatusByUserIdResult:
        async_result = []
        self._set_balance_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_balance_parameter_status_by_stamp_sheet(
        self,
        request: SetBalanceParameterStatusByStampSheetRequest,
        callback: Callable[[AsyncResult[SetBalanceParameterStatusByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='balanceParameterStatus',
            function='setBalanceParameterStatusByStampSheet',
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
                result_type=SetBalanceParameterStatusByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_balance_parameter_status_by_stamp_sheet(
        self,
        request: SetBalanceParameterStatusByStampSheetRequest,
    ) -> SetBalanceParameterStatusByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_balance_parameter_status_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_balance_parameter_status_by_stamp_sheet_async(
        self,
        request: SetBalanceParameterStatusByStampSheetRequest,
    ) -> SetBalanceParameterStatusByStampSheetResult:
        async_result = []
        self._set_balance_parameter_status_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_rarity_parameter_statuses(
        self,
        request: DescribeRarityParameterStatusesRequest,
        callback: Callable[[AsyncResult[DescribeRarityParameterStatusesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='describeRarityParameterStatuses',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
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
                result_type=DescribeRarityParameterStatusesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_rarity_parameter_statuses(
        self,
        request: DescribeRarityParameterStatusesRequest,
    ) -> DescribeRarityParameterStatusesResult:
        async_result = []
        with timeout(30):
            self._describe_rarity_parameter_statuses(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rarity_parameter_statuses_async(
        self,
        request: DescribeRarityParameterStatusesRequest,
    ) -> DescribeRarityParameterStatusesResult:
        async_result = []
        self._describe_rarity_parameter_statuses(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_rarity_parameter_statuses_by_user_id(
        self,
        request: DescribeRarityParameterStatusesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeRarityParameterStatusesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='describeRarityParameterStatusesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
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
                result_type=DescribeRarityParameterStatusesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_rarity_parameter_statuses_by_user_id(
        self,
        request: DescribeRarityParameterStatusesByUserIdRequest,
    ) -> DescribeRarityParameterStatusesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_rarity_parameter_statuses_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rarity_parameter_statuses_by_user_id_async(
        self,
        request: DescribeRarityParameterStatusesByUserIdRequest,
    ) -> DescribeRarityParameterStatusesByUserIdResult:
        async_result = []
        self._describe_rarity_parameter_statuses_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_rarity_parameter_status(
        self,
        request: GetRarityParameterStatusRequest,
        callback: Callable[[AsyncResult[GetRarityParameterStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='getRarityParameterStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRarityParameterStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_rarity_parameter_status(
        self,
        request: GetRarityParameterStatusRequest,
    ) -> GetRarityParameterStatusResult:
        async_result = []
        with timeout(30):
            self._get_rarity_parameter_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rarity_parameter_status_async(
        self,
        request: GetRarityParameterStatusRequest,
    ) -> GetRarityParameterStatusResult:
        async_result = []
        self._get_rarity_parameter_status(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_rarity_parameter_status_by_user_id(
        self,
        request: GetRarityParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[GetRarityParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='getRarityParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRarityParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_rarity_parameter_status_by_user_id(
        self,
        request: GetRarityParameterStatusByUserIdRequest,
    ) -> GetRarityParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_rarity_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_rarity_parameter_status_by_user_id_async(
        self,
        request: GetRarityParameterStatusByUserIdRequest,
    ) -> GetRarityParameterStatusByUserIdResult:
        async_result = []
        self._get_rarity_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_rarity_parameter_status_by_user_id(
        self,
        request: DeleteRarityParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteRarityParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='deleteRarityParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteRarityParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_rarity_parameter_status_by_user_id(
        self,
        request: DeleteRarityParameterStatusByUserIdRequest,
    ) -> DeleteRarityParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_rarity_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_rarity_parameter_status_by_user_id_async(
        self,
        request: DeleteRarityParameterStatusByUserIdRequest,
    ) -> DeleteRarityParameterStatusByUserIdResult:
        async_result = []
        self._delete_rarity_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _re_draw_rarity_parameter_status_by_user_id(
        self,
        request: ReDrawRarityParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[ReDrawRarityParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='reDrawRarityParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.fixed_parameter_names is not None:
            body["fixedParameterNames"] = [
                item
                for item in request.fixed_parameter_names
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
                result_type=ReDrawRarityParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def re_draw_rarity_parameter_status_by_user_id(
        self,
        request: ReDrawRarityParameterStatusByUserIdRequest,
    ) -> ReDrawRarityParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._re_draw_rarity_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def re_draw_rarity_parameter_status_by_user_id_async(
        self,
        request: ReDrawRarityParameterStatusByUserIdRequest,
    ) -> ReDrawRarityParameterStatusByUserIdResult:
        async_result = []
        self._re_draw_rarity_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _re_draw_rarity_parameter_status_by_stamp_sheet(
        self,
        request: ReDrawRarityParameterStatusByStampSheetRequest,
        callback: Callable[[AsyncResult[ReDrawRarityParameterStatusByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='reDrawRarityParameterStatusByStampSheet',
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
                result_type=ReDrawRarityParameterStatusByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def re_draw_rarity_parameter_status_by_stamp_sheet(
        self,
        request: ReDrawRarityParameterStatusByStampSheetRequest,
    ) -> ReDrawRarityParameterStatusByStampSheetResult:
        async_result = []
        with timeout(30):
            self._re_draw_rarity_parameter_status_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def re_draw_rarity_parameter_status_by_stamp_sheet_async(
        self,
        request: ReDrawRarityParameterStatusByStampSheetRequest,
    ) -> ReDrawRarityParameterStatusByStampSheetResult:
        async_result = []
        self._re_draw_rarity_parameter_status_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_rarity_parameter_status_by_user_id(
        self,
        request: AddRarityParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[AddRarityParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='addRarityParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
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
                result_type=AddRarityParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_rarity_parameter_status_by_user_id(
        self,
        request: AddRarityParameterStatusByUserIdRequest,
    ) -> AddRarityParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_rarity_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_rarity_parameter_status_by_user_id_async(
        self,
        request: AddRarityParameterStatusByUserIdRequest,
    ) -> AddRarityParameterStatusByUserIdResult:
        async_result = []
        self._add_rarity_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_rarity_parameter_status_by_stamp_sheet(
        self,
        request: AddRarityParameterStatusByStampSheetRequest,
        callback: Callable[[AsyncResult[AddRarityParameterStatusByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='addRarityParameterStatusByStampSheet',
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
                result_type=AddRarityParameterStatusByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def add_rarity_parameter_status_by_stamp_sheet(
        self,
        request: AddRarityParameterStatusByStampSheetRequest,
    ) -> AddRarityParameterStatusByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_rarity_parameter_status_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_rarity_parameter_status_by_stamp_sheet_async(
        self,
        request: AddRarityParameterStatusByStampSheetRequest,
    ) -> AddRarityParameterStatusByStampSheetResult:
        async_result = []
        self._add_rarity_parameter_status_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rarity_parameter_status(
        self,
        request: VerifyRarityParameterStatusRequest,
        callback: Callable[[AsyncResult[VerifyRarityParameterStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='verifyRarityParameterStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.parameter_value_name is not None:
            body["parameterValueName"] = request.parameter_value_name
        if request.parameter_count is not None:
            body["parameterCount"] = request.parameter_count
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
                result_type=VerifyRarityParameterStatusResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rarity_parameter_status(
        self,
        request: VerifyRarityParameterStatusRequest,
    ) -> VerifyRarityParameterStatusResult:
        async_result = []
        with timeout(30):
            self._verify_rarity_parameter_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rarity_parameter_status_async(
        self,
        request: VerifyRarityParameterStatusRequest,
    ) -> VerifyRarityParameterStatusResult:
        async_result = []
        self._verify_rarity_parameter_status(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rarity_parameter_status_by_user_id(
        self,
        request: VerifyRarityParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyRarityParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='verifyRarityParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.parameter_value_name is not None:
            body["parameterValueName"] = request.parameter_value_name
        if request.parameter_count is not None:
            body["parameterCount"] = request.parameter_count
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
                result_type=VerifyRarityParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rarity_parameter_status_by_user_id(
        self,
        request: VerifyRarityParameterStatusByUserIdRequest,
    ) -> VerifyRarityParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_rarity_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rarity_parameter_status_by_user_id_async(
        self,
        request: VerifyRarityParameterStatusByUserIdRequest,
    ) -> VerifyRarityParameterStatusByUserIdResult:
        async_result = []
        self._verify_rarity_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rarity_parameter_status_by_stamp_task(
        self,
        request: VerifyRarityParameterStatusByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyRarityParameterStatusByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='verifyRarityParameterStatusByStampTask',
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
                result_type=VerifyRarityParameterStatusByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rarity_parameter_status_by_stamp_task(
        self,
        request: VerifyRarityParameterStatusByStampTaskRequest,
    ) -> VerifyRarityParameterStatusByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_rarity_parameter_status_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rarity_parameter_status_by_stamp_task_async(
        self,
        request: VerifyRarityParameterStatusByStampTaskRequest,
    ) -> VerifyRarityParameterStatusByStampTaskResult:
        async_result = []
        self._verify_rarity_parameter_status_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_rarity_parameter_status_by_user_id(
        self,
        request: SetRarityParameterStatusByUserIdRequest,
        callback: Callable[[AsyncResult[SetRarityParameterStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='setRarityParameterStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.parameter_name is not None:
            body["parameterName"] = request.parameter_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.parameter_values is not None:
            body["parameterValues"] = [
                item.to_dict()
                for item in request.parameter_values
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
                result_type=SetRarityParameterStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_rarity_parameter_status_by_user_id(
        self,
        request: SetRarityParameterStatusByUserIdRequest,
    ) -> SetRarityParameterStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_rarity_parameter_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_rarity_parameter_status_by_user_id_async(
        self,
        request: SetRarityParameterStatusByUserIdRequest,
    ) -> SetRarityParameterStatusByUserIdResult:
        async_result = []
        self._set_rarity_parameter_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_rarity_parameter_status_by_stamp_sheet(
        self,
        request: SetRarityParameterStatusByStampSheetRequest,
        callback: Callable[[AsyncResult[SetRarityParameterStatusByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="enchant",
            component='rarityParameterStatus',
            function='setRarityParameterStatusByStampSheet',
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
                result_type=SetRarityParameterStatusByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_rarity_parameter_status_by_stamp_sheet(
        self,
        request: SetRarityParameterStatusByStampSheetRequest,
    ) -> SetRarityParameterStatusByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_rarity_parameter_status_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_rarity_parameter_status_by_stamp_sheet_async(
        self,
        request: SetRarityParameterStatusByStampSheetRequest,
    ) -> SetRarityParameterStatusByStampSheetResult:
        async_result = []
        self._set_rarity_parameter_status_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result