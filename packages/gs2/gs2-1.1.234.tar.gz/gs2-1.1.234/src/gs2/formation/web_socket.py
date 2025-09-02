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


class Gs2FormationWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
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
            service="formation",
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
        if request.update_mold_script is not None:
            body["updateMoldScript"] = request.update_mold_script.to_dict()
        if request.update_form_script is not None:
            body["updateFormScript"] = request.update_form_script.to_dict()
        if request.update_property_form_script is not None:
            body["updatePropertyFormScript"] = request.update_property_form_script.to_dict()
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
            service="formation",
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
            service="formation",
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
            service="formation",
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
        if request.update_mold_script is not None:
            body["updateMoldScript"] = request.update_mold_script.to_dict()
        if request.update_form_script is not None:
            body["updateFormScript"] = request.update_form_script.to_dict()
        if request.update_property_form_script is not None:
            body["updatePropertyFormScript"] = request.update_property_form_script.to_dict()
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
            service="formation",
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
            service="formation",
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
            service="formation",
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
            service="formation",
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
            service="formation",
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
            service="formation",
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
            service="formation",
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
            service="formation",
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
            service="formation",
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

    def _get_form_model(
        self,
        request: GetFormModelRequest,
        callback: Callable[[AsyncResult[GetFormModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='formModel',
            function='getFormModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetFormModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_form_model(
        self,
        request: GetFormModelRequest,
    ) -> GetFormModelResult:
        async_result = []
        with timeout(30):
            self._get_form_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_form_model_async(
        self,
        request: GetFormModelRequest,
    ) -> GetFormModelResult:
        async_result = []
        self._get_form_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_form_model_masters(
        self,
        request: DescribeFormModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeFormModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='formModelMaster',
            function='describeFormModelMasters',
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
                result_type=DescribeFormModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_form_model_masters(
        self,
        request: DescribeFormModelMastersRequest,
    ) -> DescribeFormModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_form_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_form_model_masters_async(
        self,
        request: DescribeFormModelMastersRequest,
    ) -> DescribeFormModelMastersResult:
        async_result = []
        self._describe_form_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_form_model_master(
        self,
        request: CreateFormModelMasterRequest,
        callback: Callable[[AsyncResult[CreateFormModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='formModelMaster',
            function='createFormModelMaster',
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
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateFormModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_form_model_master(
        self,
        request: CreateFormModelMasterRequest,
    ) -> CreateFormModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_form_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_form_model_master_async(
        self,
        request: CreateFormModelMasterRequest,
    ) -> CreateFormModelMasterResult:
        async_result = []
        self._create_form_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_form_model_master(
        self,
        request: GetFormModelMasterRequest,
        callback: Callable[[AsyncResult[GetFormModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='formModelMaster',
            function='getFormModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.form_model_name is not None:
            body["formModelName"] = request.form_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetFormModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_form_model_master(
        self,
        request: GetFormModelMasterRequest,
    ) -> GetFormModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_form_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_form_model_master_async(
        self,
        request: GetFormModelMasterRequest,
    ) -> GetFormModelMasterResult:
        async_result = []
        self._get_form_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_form_model_master(
        self,
        request: UpdateFormModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateFormModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='formModelMaster',
            function='updateFormModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.form_model_name is not None:
            body["formModelName"] = request.form_model_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateFormModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_form_model_master(
        self,
        request: UpdateFormModelMasterRequest,
    ) -> UpdateFormModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_form_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_form_model_master_async(
        self,
        request: UpdateFormModelMasterRequest,
    ) -> UpdateFormModelMasterResult:
        async_result = []
        self._update_form_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_form_model_master(
        self,
        request: DeleteFormModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteFormModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='formModelMaster',
            function='deleteFormModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.form_model_name is not None:
            body["formModelName"] = request.form_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteFormModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_form_model_master(
        self,
        request: DeleteFormModelMasterRequest,
    ) -> DeleteFormModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_form_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_form_model_master_async(
        self,
        request: DeleteFormModelMasterRequest,
    ) -> DeleteFormModelMasterResult:
        async_result = []
        self._delete_form_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_mold_models(
        self,
        request: DescribeMoldModelsRequest,
        callback: Callable[[AsyncResult[DescribeMoldModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='moldModel',
            function='describeMoldModels',
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
                result_type=DescribeMoldModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_mold_models(
        self,
        request: DescribeMoldModelsRequest,
    ) -> DescribeMoldModelsResult:
        async_result = []
        with timeout(30):
            self._describe_mold_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_mold_models_async(
        self,
        request: DescribeMoldModelsRequest,
    ) -> DescribeMoldModelsResult:
        async_result = []
        self._describe_mold_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_mold_model(
        self,
        request: GetMoldModelRequest,
        callback: Callable[[AsyncResult[GetMoldModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='moldModel',
            function='getMoldModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMoldModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_mold_model(
        self,
        request: GetMoldModelRequest,
    ) -> GetMoldModelResult:
        async_result = []
        with timeout(30):
            self._get_mold_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_mold_model_async(
        self,
        request: GetMoldModelRequest,
    ) -> GetMoldModelResult:
        async_result = []
        self._get_mold_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_mold_model_masters(
        self,
        request: DescribeMoldModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeMoldModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='moldModelMaster',
            function='describeMoldModelMasters',
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
                result_type=DescribeMoldModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_mold_model_masters(
        self,
        request: DescribeMoldModelMastersRequest,
    ) -> DescribeMoldModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_mold_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_mold_model_masters_async(
        self,
        request: DescribeMoldModelMastersRequest,
    ) -> DescribeMoldModelMastersResult:
        async_result = []
        self._describe_mold_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_mold_model_master(
        self,
        request: CreateMoldModelMasterRequest,
        callback: Callable[[AsyncResult[CreateMoldModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='moldModelMaster',
            function='createMoldModelMaster',
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
        if request.form_model_name is not None:
            body["formModelName"] = request.form_model_name
        if request.initial_max_capacity is not None:
            body["initialMaxCapacity"] = request.initial_max_capacity
        if request.max_capacity is not None:
            body["maxCapacity"] = request.max_capacity

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateMoldModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_mold_model_master(
        self,
        request: CreateMoldModelMasterRequest,
    ) -> CreateMoldModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_mold_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_mold_model_master_async(
        self,
        request: CreateMoldModelMasterRequest,
    ) -> CreateMoldModelMasterResult:
        async_result = []
        self._create_mold_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_mold_model_master(
        self,
        request: GetMoldModelMasterRequest,
        callback: Callable[[AsyncResult[GetMoldModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='moldModelMaster',
            function='getMoldModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMoldModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_mold_model_master(
        self,
        request: GetMoldModelMasterRequest,
    ) -> GetMoldModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_mold_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_mold_model_master_async(
        self,
        request: GetMoldModelMasterRequest,
    ) -> GetMoldModelMasterResult:
        async_result = []
        self._get_mold_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_mold_model_master(
        self,
        request: UpdateMoldModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateMoldModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='moldModelMaster',
            function='updateMoldModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.form_model_name is not None:
            body["formModelName"] = request.form_model_name
        if request.initial_max_capacity is not None:
            body["initialMaxCapacity"] = request.initial_max_capacity
        if request.max_capacity is not None:
            body["maxCapacity"] = request.max_capacity

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateMoldModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_mold_model_master(
        self,
        request: UpdateMoldModelMasterRequest,
    ) -> UpdateMoldModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_mold_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_mold_model_master_async(
        self,
        request: UpdateMoldModelMasterRequest,
    ) -> UpdateMoldModelMasterResult:
        async_result = []
        self._update_mold_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_mold_model_master(
        self,
        request: DeleteMoldModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteMoldModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='moldModelMaster',
            function='deleteMoldModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteMoldModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_mold_model_master(
        self,
        request: DeleteMoldModelMasterRequest,
    ) -> DeleteMoldModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_mold_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_mold_model_master_async(
        self,
        request: DeleteMoldModelMasterRequest,
    ) -> DeleteMoldModelMasterResult:
        async_result = []
        self._delete_mold_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_property_form_models(
        self,
        request: DescribePropertyFormModelsRequest,
        callback: Callable[[AsyncResult[DescribePropertyFormModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyFormModel',
            function='describePropertyFormModels',
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
                result_type=DescribePropertyFormModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_property_form_models(
        self,
        request: DescribePropertyFormModelsRequest,
    ) -> DescribePropertyFormModelsResult:
        async_result = []
        with timeout(30):
            self._describe_property_form_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_property_form_models_async(
        self,
        request: DescribePropertyFormModelsRequest,
    ) -> DescribePropertyFormModelsResult:
        async_result = []
        self._describe_property_form_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_property_form_model(
        self,
        request: GetPropertyFormModelRequest,
        callback: Callable[[AsyncResult[GetPropertyFormModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyFormModel',
            function='getPropertyFormModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPropertyFormModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_property_form_model(
        self,
        request: GetPropertyFormModelRequest,
    ) -> GetPropertyFormModelResult:
        async_result = []
        with timeout(30):
            self._get_property_form_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_property_form_model_async(
        self,
        request: GetPropertyFormModelRequest,
    ) -> GetPropertyFormModelResult:
        async_result = []
        self._get_property_form_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_property_form_model_masters(
        self,
        request: DescribePropertyFormModelMastersRequest,
        callback: Callable[[AsyncResult[DescribePropertyFormModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyFormModelMaster',
            function='describePropertyFormModelMasters',
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
                result_type=DescribePropertyFormModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_property_form_model_masters(
        self,
        request: DescribePropertyFormModelMastersRequest,
    ) -> DescribePropertyFormModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_property_form_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_property_form_model_masters_async(
        self,
        request: DescribePropertyFormModelMastersRequest,
    ) -> DescribePropertyFormModelMastersResult:
        async_result = []
        self._describe_property_form_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_property_form_model_master(
        self,
        request: CreatePropertyFormModelMasterRequest,
        callback: Callable[[AsyncResult[CreatePropertyFormModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyFormModelMaster',
            function='createPropertyFormModelMaster',
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
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreatePropertyFormModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_property_form_model_master(
        self,
        request: CreatePropertyFormModelMasterRequest,
    ) -> CreatePropertyFormModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_property_form_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_property_form_model_master_async(
        self,
        request: CreatePropertyFormModelMasterRequest,
    ) -> CreatePropertyFormModelMasterResult:
        async_result = []
        self._create_property_form_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_property_form_model_master(
        self,
        request: GetPropertyFormModelMasterRequest,
        callback: Callable[[AsyncResult[GetPropertyFormModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyFormModelMaster',
            function='getPropertyFormModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPropertyFormModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_property_form_model_master(
        self,
        request: GetPropertyFormModelMasterRequest,
    ) -> GetPropertyFormModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_property_form_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_property_form_model_master_async(
        self,
        request: GetPropertyFormModelMasterRequest,
    ) -> GetPropertyFormModelMasterResult:
        async_result = []
        self._get_property_form_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_property_form_model_master(
        self,
        request: UpdatePropertyFormModelMasterRequest,
        callback: Callable[[AsyncResult[UpdatePropertyFormModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyFormModelMaster',
            function='updatePropertyFormModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdatePropertyFormModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_property_form_model_master(
        self,
        request: UpdatePropertyFormModelMasterRequest,
    ) -> UpdatePropertyFormModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_property_form_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_property_form_model_master_async(
        self,
        request: UpdatePropertyFormModelMasterRequest,
    ) -> UpdatePropertyFormModelMasterResult:
        async_result = []
        self._update_property_form_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_property_form_model_master(
        self,
        request: DeletePropertyFormModelMasterRequest,
        callback: Callable[[AsyncResult[DeletePropertyFormModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyFormModelMaster',
            function='deletePropertyFormModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeletePropertyFormModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_property_form_model_master(
        self,
        request: DeletePropertyFormModelMasterRequest,
    ) -> DeletePropertyFormModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_property_form_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_property_form_model_master_async(
        self,
        request: DeletePropertyFormModelMasterRequest,
    ) -> DeletePropertyFormModelMasterResult:
        async_result = []
        self._delete_property_form_model_master(
            request,
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
            service="formation",
            component='currentFormMaster',
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

    def _get_current_form_master(
        self,
        request: GetCurrentFormMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentFormMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='currentFormMaster',
            function='getCurrentFormMaster',
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
                result_type=GetCurrentFormMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_form_master(
        self,
        request: GetCurrentFormMasterRequest,
    ) -> GetCurrentFormMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_form_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_form_master_async(
        self,
        request: GetCurrentFormMasterRequest,
    ) -> GetCurrentFormMasterResult:
        async_result = []
        self._get_current_form_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _pre_update_current_form_master(
        self,
        request: PreUpdateCurrentFormMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentFormMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='currentFormMaster',
            function='preUpdateCurrentFormMaster',
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
                result_type=PreUpdateCurrentFormMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_form_master(
        self,
        request: PreUpdateCurrentFormMasterRequest,
    ) -> PreUpdateCurrentFormMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_form_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_form_master_async(
        self,
        request: PreUpdateCurrentFormMasterRequest,
    ) -> PreUpdateCurrentFormMasterResult:
        async_result = []
        self._pre_update_current_form_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_form_master(
        self,
        request: UpdateCurrentFormMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentFormMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='currentFormMaster',
            function='updateCurrentFormMaster',
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
                result_type=UpdateCurrentFormMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_form_master(
        self,
        request: UpdateCurrentFormMasterRequest,
    ) -> UpdateCurrentFormMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_form_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_form_master_async(
        self,
        request: UpdateCurrentFormMasterRequest,
    ) -> UpdateCurrentFormMasterResult:
        async_result = []
        self._update_current_form_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_form_master_from_git_hub(
        self,
        request: UpdateCurrentFormMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentFormMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='currentFormMaster',
            function='updateCurrentFormMasterFromGitHub',
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
                result_type=UpdateCurrentFormMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_form_master_from_git_hub(
        self,
        request: UpdateCurrentFormMasterFromGitHubRequest,
    ) -> UpdateCurrentFormMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_form_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_form_master_from_git_hub_async(
        self,
        request: UpdateCurrentFormMasterFromGitHubRequest,
    ) -> UpdateCurrentFormMasterFromGitHubResult:
        async_result = []
        self._update_current_form_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_molds(
        self,
        request: DescribeMoldsRequest,
        callback: Callable[[AsyncResult[DescribeMoldsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='describeMolds',
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
                result_type=DescribeMoldsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_molds(
        self,
        request: DescribeMoldsRequest,
    ) -> DescribeMoldsResult:
        async_result = []
        with timeout(30):
            self._describe_molds(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_molds_async(
        self,
        request: DescribeMoldsRequest,
    ) -> DescribeMoldsResult:
        async_result = []
        self._describe_molds(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_molds_by_user_id(
        self,
        request: DescribeMoldsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeMoldsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='describeMoldsByUserId',
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
                result_type=DescribeMoldsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_molds_by_user_id(
        self,
        request: DescribeMoldsByUserIdRequest,
    ) -> DescribeMoldsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_molds_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_molds_by_user_id_async(
        self,
        request: DescribeMoldsByUserIdRequest,
    ) -> DescribeMoldsByUserIdResult:
        async_result = []
        self._describe_molds_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_mold(
        self,
        request: GetMoldRequest,
        callback: Callable[[AsyncResult[GetMoldResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='getMold',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMoldResult,
                callback=callback,
                body=body,
            )
        )

    def get_mold(
        self,
        request: GetMoldRequest,
    ) -> GetMoldResult:
        async_result = []
        with timeout(30):
            self._get_mold(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_mold_async(
        self,
        request: GetMoldRequest,
    ) -> GetMoldResult:
        async_result = []
        self._get_mold(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_mold_by_user_id(
        self,
        request: GetMoldByUserIdRequest,
        callback: Callable[[AsyncResult[GetMoldByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='getMoldByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMoldByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_mold_by_user_id(
        self,
        request: GetMoldByUserIdRequest,
    ) -> GetMoldByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_mold_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_mold_by_user_id_async(
        self,
        request: GetMoldByUserIdRequest,
    ) -> GetMoldByUserIdResult:
        async_result = []
        self._get_mold_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_mold_capacity_by_user_id(
        self,
        request: SetMoldCapacityByUserIdRequest,
        callback: Callable[[AsyncResult[SetMoldCapacityByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='setMoldCapacityByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.capacity is not None:
            body["capacity"] = request.capacity
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SetMoldCapacityByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_mold_capacity_by_user_id(
        self,
        request: SetMoldCapacityByUserIdRequest,
    ) -> SetMoldCapacityByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_mold_capacity_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_mold_capacity_by_user_id_async(
        self,
        request: SetMoldCapacityByUserIdRequest,
    ) -> SetMoldCapacityByUserIdResult:
        async_result = []
        self._set_mold_capacity_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_mold_capacity_by_user_id(
        self,
        request: AddMoldCapacityByUserIdRequest,
        callback: Callable[[AsyncResult[AddMoldCapacityByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='addMoldCapacityByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.capacity is not None:
            body["capacity"] = request.capacity
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AddMoldCapacityByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_mold_capacity_by_user_id(
        self,
        request: AddMoldCapacityByUserIdRequest,
    ) -> AddMoldCapacityByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_mold_capacity_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_mold_capacity_by_user_id_async(
        self,
        request: AddMoldCapacityByUserIdRequest,
    ) -> AddMoldCapacityByUserIdResult:
        async_result = []
        self._add_mold_capacity_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_mold_capacity(
        self,
        request: SubMoldCapacityRequest,
        callback: Callable[[AsyncResult[SubMoldCapacityResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='subMoldCapacity',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.capacity is not None:
            body["capacity"] = request.capacity

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SubMoldCapacityResult,
                callback=callback,
                body=body,
            )
        )

    def sub_mold_capacity(
        self,
        request: SubMoldCapacityRequest,
    ) -> SubMoldCapacityResult:
        async_result = []
        with timeout(30):
            self._sub_mold_capacity(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_mold_capacity_async(
        self,
        request: SubMoldCapacityRequest,
    ) -> SubMoldCapacityResult:
        async_result = []
        self._sub_mold_capacity(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_mold_capacity_by_user_id(
        self,
        request: SubMoldCapacityByUserIdRequest,
        callback: Callable[[AsyncResult[SubMoldCapacityByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='subMoldCapacityByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.capacity is not None:
            body["capacity"] = request.capacity
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SubMoldCapacityByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def sub_mold_capacity_by_user_id(
        self,
        request: SubMoldCapacityByUserIdRequest,
    ) -> SubMoldCapacityByUserIdResult:
        async_result = []
        with timeout(30):
            self._sub_mold_capacity_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_mold_capacity_by_user_id_async(
        self,
        request: SubMoldCapacityByUserIdRequest,
    ) -> SubMoldCapacityByUserIdResult:
        async_result = []
        self._sub_mold_capacity_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_mold(
        self,
        request: DeleteMoldRequest,
        callback: Callable[[AsyncResult[DeleteMoldResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='deleteMold',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteMoldResult,
                callback=callback,
                body=body,
            )
        )

    def delete_mold(
        self,
        request: DeleteMoldRequest,
    ) -> DeleteMoldResult:
        async_result = []
        with timeout(30):
            self._delete_mold(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_mold_async(
        self,
        request: DeleteMoldRequest,
    ) -> DeleteMoldResult:
        async_result = []
        self._delete_mold(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_mold_by_user_id(
        self,
        request: DeleteMoldByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteMoldByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='deleteMoldByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteMoldByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_mold_by_user_id(
        self,
        request: DeleteMoldByUserIdRequest,
    ) -> DeleteMoldByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_mold_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_mold_by_user_id_async(
        self,
        request: DeleteMoldByUserIdRequest,
    ) -> DeleteMoldByUserIdResult:
        async_result = []
        self._delete_mold_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_capacity_by_stamp_sheet(
        self,
        request: AddCapacityByStampSheetRequest,
        callback: Callable[[AsyncResult[AddCapacityByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='addCapacityByStampSheet',
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
                result_type=AddCapacityByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def add_capacity_by_stamp_sheet(
        self,
        request: AddCapacityByStampSheetRequest,
    ) -> AddCapacityByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_capacity_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_capacity_by_stamp_sheet_async(
        self,
        request: AddCapacityByStampSheetRequest,
    ) -> AddCapacityByStampSheetResult:
        async_result = []
        self._add_capacity_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_capacity_by_stamp_task(
        self,
        request: SubCapacityByStampTaskRequest,
        callback: Callable[[AsyncResult[SubCapacityByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='subCapacityByStampTask',
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
                result_type=SubCapacityByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def sub_capacity_by_stamp_task(
        self,
        request: SubCapacityByStampTaskRequest,
    ) -> SubCapacityByStampTaskResult:
        async_result = []
        with timeout(30):
            self._sub_capacity_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_capacity_by_stamp_task_async(
        self,
        request: SubCapacityByStampTaskRequest,
    ) -> SubCapacityByStampTaskResult:
        async_result = []
        self._sub_capacity_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_capacity_by_stamp_sheet(
        self,
        request: SetCapacityByStampSheetRequest,
        callback: Callable[[AsyncResult[SetCapacityByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='mold',
            function='setCapacityByStampSheet',
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
                result_type=SetCapacityByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_capacity_by_stamp_sheet(
        self,
        request: SetCapacityByStampSheetRequest,
    ) -> SetCapacityByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_capacity_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_capacity_by_stamp_sheet_async(
        self,
        request: SetCapacityByStampSheetRequest,
    ) -> SetCapacityByStampSheetResult:
        async_result = []
        self._set_capacity_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_forms(
        self,
        request: DescribeFormsRequest,
        callback: Callable[[AsyncResult[DescribeFormsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='describeForms',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
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
                result_type=DescribeFormsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_forms(
        self,
        request: DescribeFormsRequest,
    ) -> DescribeFormsResult:
        async_result = []
        with timeout(30):
            self._describe_forms(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_forms_async(
        self,
        request: DescribeFormsRequest,
    ) -> DescribeFormsResult:
        async_result = []
        self._describe_forms(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_forms_by_user_id(
        self,
        request: DescribeFormsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeFormsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='describeFormsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
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
                result_type=DescribeFormsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_forms_by_user_id(
        self,
        request: DescribeFormsByUserIdRequest,
    ) -> DescribeFormsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_forms_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_forms_by_user_id_async(
        self,
        request: DescribeFormsByUserIdRequest,
    ) -> DescribeFormsByUserIdResult:
        async_result = []
        self._describe_forms_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_form(
        self,
        request: GetFormRequest,
        callback: Callable[[AsyncResult[GetFormResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='getForm',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetFormResult,
                callback=callback,
                body=body,
            )
        )

    def get_form(
        self,
        request: GetFormRequest,
    ) -> GetFormResult:
        async_result = []
        with timeout(30):
            self._get_form(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_form_async(
        self,
        request: GetFormRequest,
    ) -> GetFormResult:
        async_result = []
        self._get_form(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_form_by_user_id(
        self,
        request: GetFormByUserIdRequest,
        callback: Callable[[AsyncResult[GetFormByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='getFormByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetFormByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_form_by_user_id(
        self,
        request: GetFormByUserIdRequest,
    ) -> GetFormByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_form_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_form_by_user_id_async(
        self,
        request: GetFormByUserIdRequest,
    ) -> GetFormByUserIdResult:
        async_result = []
        self._get_form_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_form_with_signature(
        self,
        request: GetFormWithSignatureRequest,
        callback: Callable[[AsyncResult[GetFormWithSignatureResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='getFormWithSignature',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetFormWithSignatureResult,
                callback=callback,
                body=body,
            )
        )

    def get_form_with_signature(
        self,
        request: GetFormWithSignatureRequest,
    ) -> GetFormWithSignatureResult:
        async_result = []
        with timeout(30):
            self._get_form_with_signature(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_form_with_signature_async(
        self,
        request: GetFormWithSignatureRequest,
    ) -> GetFormWithSignatureResult:
        async_result = []
        self._get_form_with_signature(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_form_with_signature_by_user_id(
        self,
        request: GetFormWithSignatureByUserIdRequest,
        callback: Callable[[AsyncResult[GetFormWithSignatureByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='getFormWithSignatureByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetFormWithSignatureByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_form_with_signature_by_user_id(
        self,
        request: GetFormWithSignatureByUserIdRequest,
    ) -> GetFormWithSignatureByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_form_with_signature_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_form_with_signature_by_user_id_async(
        self,
        request: GetFormWithSignatureByUserIdRequest,
    ) -> GetFormWithSignatureByUserIdResult:
        async_result = []
        self._get_form_with_signature_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_form(
        self,
        request: SetFormRequest,
        callback: Callable[[AsyncResult[SetFormResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='setForm',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
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
                result_type=SetFormResult,
                callback=callback,
                body=body,
            )
        )

    def set_form(
        self,
        request: SetFormRequest,
    ) -> SetFormResult:
        async_result = []
        with timeout(30):
            self._set_form(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_form_async(
        self,
        request: SetFormRequest,
    ) -> SetFormResult:
        async_result = []
        self._set_form(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_form_by_user_id(
        self,
        request: SetFormByUserIdRequest,
        callback: Callable[[AsyncResult[SetFormByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='setFormByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
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
                result_type=SetFormByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_form_by_user_id(
        self,
        request: SetFormByUserIdRequest,
    ) -> SetFormByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_form_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_form_by_user_id_async(
        self,
        request: SetFormByUserIdRequest,
    ) -> SetFormByUserIdResult:
        async_result = []
        self._set_form_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_form_with_signature(
        self,
        request: SetFormWithSignatureRequest,
        callback: Callable[[AsyncResult[SetFormWithSignatureResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='setFormWithSignature',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
            ]
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SetFormWithSignatureResult,
                callback=callback,
                body=body,
            )
        )

    def set_form_with_signature(
        self,
        request: SetFormWithSignatureRequest,
    ) -> SetFormWithSignatureResult:
        async_result = []
        with timeout(30):
            self._set_form_with_signature(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_form_with_signature_async(
        self,
        request: SetFormWithSignatureRequest,
    ) -> SetFormWithSignatureResult:
        async_result = []
        self._set_form_with_signature(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _acquire_actions_to_form_properties(
        self,
        request: AcquireActionsToFormPropertiesRequest,
        callback: Callable[[AsyncResult[AcquireActionsToFormPropertiesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='acquireActionsToFormProperties',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index
        if request.acquire_action is not None:
            body["acquireAction"] = request.acquire_action.to_dict()
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
                result_type=AcquireActionsToFormPropertiesResult,
                callback=callback,
                body=body,
            )
        )

    def acquire_actions_to_form_properties(
        self,
        request: AcquireActionsToFormPropertiesRequest,
    ) -> AcquireActionsToFormPropertiesResult:
        async_result = []
        with timeout(30):
            self._acquire_actions_to_form_properties(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_actions_to_form_properties_async(
        self,
        request: AcquireActionsToFormPropertiesRequest,
    ) -> AcquireActionsToFormPropertiesResult:
        async_result = []
        self._acquire_actions_to_form_properties(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_form(
        self,
        request: DeleteFormRequest,
        callback: Callable[[AsyncResult[DeleteFormResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='deleteForm',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteFormResult,
                callback=callback,
                body=body,
            )
        )

    def delete_form(
        self,
        request: DeleteFormRequest,
    ) -> DeleteFormResult:
        async_result = []
        with timeout(30):
            self._delete_form(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_form_async(
        self,
        request: DeleteFormRequest,
    ) -> DeleteFormResult:
        async_result = []
        self._delete_form(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_form_by_user_id(
        self,
        request: DeleteFormByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteFormByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='deleteFormByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.mold_model_name is not None:
            body["moldModelName"] = request.mold_model_name
        if request.index is not None:
            body["index"] = request.index
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteFormByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_form_by_user_id(
        self,
        request: DeleteFormByUserIdRequest,
    ) -> DeleteFormByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_form_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_form_by_user_id_async(
        self,
        request: DeleteFormByUserIdRequest,
    ) -> DeleteFormByUserIdResult:
        async_result = []
        self._delete_form_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _acquire_action_to_form_properties_by_stamp_sheet(
        self,
        request: AcquireActionToFormPropertiesByStampSheetRequest,
        callback: Callable[[AsyncResult[AcquireActionToFormPropertiesByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='acquireActionToFormPropertiesByStampSheet',
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
                result_type=AcquireActionToFormPropertiesByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def acquire_action_to_form_properties_by_stamp_sheet(
        self,
        request: AcquireActionToFormPropertiesByStampSheetRequest,
    ) -> AcquireActionToFormPropertiesByStampSheetResult:
        async_result = []
        with timeout(30):
            self._acquire_action_to_form_properties_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_action_to_form_properties_by_stamp_sheet_async(
        self,
        request: AcquireActionToFormPropertiesByStampSheetRequest,
    ) -> AcquireActionToFormPropertiesByStampSheetResult:
        async_result = []
        self._acquire_action_to_form_properties_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_form_by_stamp_sheet(
        self,
        request: SetFormByStampSheetRequest,
        callback: Callable[[AsyncResult[SetFormByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='form',
            function='setFormByStampSheet',
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
                result_type=SetFormByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_form_by_stamp_sheet(
        self,
        request: SetFormByStampSheetRequest,
    ) -> SetFormByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_form_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_form_by_stamp_sheet_async(
        self,
        request: SetFormByStampSheetRequest,
    ) -> SetFormByStampSheetResult:
        async_result = []
        self._set_form_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_property_forms(
        self,
        request: DescribePropertyFormsRequest,
        callback: Callable[[AsyncResult[DescribePropertyFormsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='describePropertyForms',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
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
                result_type=DescribePropertyFormsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_property_forms(
        self,
        request: DescribePropertyFormsRequest,
    ) -> DescribePropertyFormsResult:
        async_result = []
        with timeout(30):
            self._describe_property_forms(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_property_forms_async(
        self,
        request: DescribePropertyFormsRequest,
    ) -> DescribePropertyFormsResult:
        async_result = []
        self._describe_property_forms(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_property_forms_by_user_id(
        self,
        request: DescribePropertyFormsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribePropertyFormsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='describePropertyFormsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
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
                result_type=DescribePropertyFormsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_property_forms_by_user_id(
        self,
        request: DescribePropertyFormsByUserIdRequest,
    ) -> DescribePropertyFormsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_property_forms_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_property_forms_by_user_id_async(
        self,
        request: DescribePropertyFormsByUserIdRequest,
    ) -> DescribePropertyFormsByUserIdResult:
        async_result = []
        self._describe_property_forms_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_property_form(
        self,
        request: GetPropertyFormRequest,
        callback: Callable[[AsyncResult[GetPropertyFormResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='getPropertyForm',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPropertyFormResult,
                callback=callback,
                body=body,
            )
        )

    def get_property_form(
        self,
        request: GetPropertyFormRequest,
    ) -> GetPropertyFormResult:
        async_result = []
        with timeout(30):
            self._get_property_form(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_property_form_async(
        self,
        request: GetPropertyFormRequest,
    ) -> GetPropertyFormResult:
        async_result = []
        self._get_property_form(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_property_form_by_user_id(
        self,
        request: GetPropertyFormByUserIdRequest,
        callback: Callable[[AsyncResult[GetPropertyFormByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='getPropertyFormByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPropertyFormByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_property_form_by_user_id(
        self,
        request: GetPropertyFormByUserIdRequest,
    ) -> GetPropertyFormByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_property_form_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_property_form_by_user_id_async(
        self,
        request: GetPropertyFormByUserIdRequest,
    ) -> GetPropertyFormByUserIdResult:
        async_result = []
        self._get_property_form_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_property_form_with_signature(
        self,
        request: GetPropertyFormWithSignatureRequest,
        callback: Callable[[AsyncResult[GetPropertyFormWithSignatureResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='getPropertyFormWithSignature',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPropertyFormWithSignatureResult,
                callback=callback,
                body=body,
            )
        )

    def get_property_form_with_signature(
        self,
        request: GetPropertyFormWithSignatureRequest,
    ) -> GetPropertyFormWithSignatureResult:
        async_result = []
        with timeout(30):
            self._get_property_form_with_signature(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_property_form_with_signature_async(
        self,
        request: GetPropertyFormWithSignatureRequest,
    ) -> GetPropertyFormWithSignatureResult:
        async_result = []
        self._get_property_form_with_signature(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_property_form_with_signature_by_user_id(
        self,
        request: GetPropertyFormWithSignatureByUserIdRequest,
        callback: Callable[[AsyncResult[GetPropertyFormWithSignatureByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='getPropertyFormWithSignatureByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPropertyFormWithSignatureByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_property_form_with_signature_by_user_id(
        self,
        request: GetPropertyFormWithSignatureByUserIdRequest,
    ) -> GetPropertyFormWithSignatureByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_property_form_with_signature_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_property_form_with_signature_by_user_id_async(
        self,
        request: GetPropertyFormWithSignatureByUserIdRequest,
    ) -> GetPropertyFormWithSignatureByUserIdResult:
        async_result = []
        self._get_property_form_with_signature_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_property_form(
        self,
        request: SetPropertyFormRequest,
        callback: Callable[[AsyncResult[SetPropertyFormResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='setPropertyForm',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
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
                result_type=SetPropertyFormResult,
                callback=callback,
                body=body,
            )
        )

    def set_property_form(
        self,
        request: SetPropertyFormRequest,
    ) -> SetPropertyFormResult:
        async_result = []
        with timeout(30):
            self._set_property_form(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_property_form_async(
        self,
        request: SetPropertyFormRequest,
    ) -> SetPropertyFormResult:
        async_result = []
        self._set_property_form(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_property_form_by_user_id(
        self,
        request: SetPropertyFormByUserIdRequest,
        callback: Callable[[AsyncResult[SetPropertyFormByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='setPropertyFormByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
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
                result_type=SetPropertyFormByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_property_form_by_user_id(
        self,
        request: SetPropertyFormByUserIdRequest,
    ) -> SetPropertyFormByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_property_form_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_property_form_by_user_id_async(
        self,
        request: SetPropertyFormByUserIdRequest,
    ) -> SetPropertyFormByUserIdResult:
        async_result = []
        self._set_property_form_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_property_form_with_signature(
        self,
        request: SetPropertyFormWithSignatureRequest,
        callback: Callable[[AsyncResult[SetPropertyFormWithSignatureResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='setPropertyFormWithSignature',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.slots is not None:
            body["slots"] = [
                item.to_dict()
                for item in request.slots
            ]
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SetPropertyFormWithSignatureResult,
                callback=callback,
                body=body,
            )
        )

    def set_property_form_with_signature(
        self,
        request: SetPropertyFormWithSignatureRequest,
    ) -> SetPropertyFormWithSignatureResult:
        async_result = []
        with timeout(30):
            self._set_property_form_with_signature(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_property_form_with_signature_async(
        self,
        request: SetPropertyFormWithSignatureRequest,
    ) -> SetPropertyFormWithSignatureResult:
        async_result = []
        self._set_property_form_with_signature(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _acquire_actions_to_property_form_properties(
        self,
        request: AcquireActionsToPropertyFormPropertiesRequest,
        callback: Callable[[AsyncResult[AcquireActionsToPropertyFormPropertiesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='acquireActionsToPropertyFormProperties',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.acquire_action is not None:
            body["acquireAction"] = request.acquire_action.to_dict()
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
                result_type=AcquireActionsToPropertyFormPropertiesResult,
                callback=callback,
                body=body,
            )
        )

    def acquire_actions_to_property_form_properties(
        self,
        request: AcquireActionsToPropertyFormPropertiesRequest,
    ) -> AcquireActionsToPropertyFormPropertiesResult:
        async_result = []
        with timeout(30):
            self._acquire_actions_to_property_form_properties(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_actions_to_property_form_properties_async(
        self,
        request: AcquireActionsToPropertyFormPropertiesRequest,
    ) -> AcquireActionsToPropertyFormPropertiesResult:
        async_result = []
        self._acquire_actions_to_property_form_properties(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_property_form(
        self,
        request: DeletePropertyFormRequest,
        callback: Callable[[AsyncResult[DeletePropertyFormResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='deletePropertyForm',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeletePropertyFormResult,
                callback=callback,
                body=body,
            )
        )

    def delete_property_form(
        self,
        request: DeletePropertyFormRequest,
    ) -> DeletePropertyFormResult:
        async_result = []
        with timeout(30):
            self._delete_property_form(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_property_form_async(
        self,
        request: DeletePropertyFormRequest,
    ) -> DeletePropertyFormResult:
        async_result = []
        self._delete_property_form(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_property_form_by_user_id(
        self,
        request: DeletePropertyFormByUserIdRequest,
        callback: Callable[[AsyncResult[DeletePropertyFormByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='deletePropertyFormByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.property_form_model_name is not None:
            body["propertyFormModelName"] = request.property_form_model_name
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
                result_type=DeletePropertyFormByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_property_form_by_user_id(
        self,
        request: DeletePropertyFormByUserIdRequest,
    ) -> DeletePropertyFormByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_property_form_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_property_form_by_user_id_async(
        self,
        request: DeletePropertyFormByUserIdRequest,
    ) -> DeletePropertyFormByUserIdResult:
        async_result = []
        self._delete_property_form_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _acquire_action_to_property_form_properties_by_stamp_sheet(
        self,
        request: AcquireActionToPropertyFormPropertiesByStampSheetRequest,
        callback: Callable[[AsyncResult[AcquireActionToPropertyFormPropertiesByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="formation",
            component='propertyForm',
            function='acquireActionToPropertyFormPropertiesByStampSheet',
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
                result_type=AcquireActionToPropertyFormPropertiesByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def acquire_action_to_property_form_properties_by_stamp_sheet(
        self,
        request: AcquireActionToPropertyFormPropertiesByStampSheetRequest,
    ) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        async_result = []
        with timeout(30):
            self._acquire_action_to_property_form_properties_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_action_to_property_form_properties_by_stamp_sheet_async(
        self,
        request: AcquireActionToPropertyFormPropertiesByStampSheetRequest,
    ) -> AcquireActionToPropertyFormPropertiesByStampSheetResult:
        async_result = []
        self._acquire_action_to_property_form_properties_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result