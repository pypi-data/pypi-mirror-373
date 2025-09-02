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


class Gs2ExperienceWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
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
            service="experience",
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
        if request.rank_cap_script_id is not None:
            body["rankCapScriptId"] = request.rank_cap_script_id
        if request.change_experience_script is not None:
            body["changeExperienceScript"] = request.change_experience_script.to_dict()
        if request.change_rank_script is not None:
            body["changeRankScript"] = request.change_rank_script.to_dict()
        if request.change_rank_cap_script is not None:
            body["changeRankCapScript"] = request.change_rank_cap_script.to_dict()
        if request.overflow_experience_script is not None:
            body["overflowExperienceScript"] = request.overflow_experience_script
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
            service="experience",
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
            service="experience",
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
            service="experience",
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
        if request.rank_cap_script_id is not None:
            body["rankCapScriptId"] = request.rank_cap_script_id
        if request.change_experience_script is not None:
            body["changeExperienceScript"] = request.change_experience_script.to_dict()
        if request.change_rank_script is not None:
            body["changeRankScript"] = request.change_rank_script.to_dict()
        if request.change_rank_cap_script is not None:
            body["changeRankCapScript"] = request.change_rank_cap_script.to_dict()
        if request.overflow_experience_script is not None:
            body["overflowExperienceScript"] = request.overflow_experience_script
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
            service="experience",
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
            service="experience",
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
            service="experience",
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
            service="experience",
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
            service="experience",
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
            service="experience",
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
            service="experience",
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
            service="experience",
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
            service="experience",
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

    def _describe_experience_model_masters(
        self,
        request: DescribeExperienceModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeExperienceModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='describeExperienceModelMasters',
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
                result_type=DescribeExperienceModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_experience_model_masters(
        self,
        request: DescribeExperienceModelMastersRequest,
    ) -> DescribeExperienceModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_experience_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_experience_model_masters_async(
        self,
        request: DescribeExperienceModelMastersRequest,
    ) -> DescribeExperienceModelMastersResult:
        async_result = []
        self._describe_experience_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_experience_model_master(
        self,
        request: CreateExperienceModelMasterRequest,
        callback: Callable[[AsyncResult[CreateExperienceModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='createExperienceModelMaster',
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
        if request.default_experience is not None:
            body["defaultExperience"] = request.default_experience
        if request.default_rank_cap is not None:
            body["defaultRankCap"] = request.default_rank_cap
        if request.max_rank_cap is not None:
            body["maxRankCap"] = request.max_rank_cap
        if request.rank_threshold_name is not None:
            body["rankThresholdName"] = request.rank_threshold_name
        if request.acquire_action_rates is not None:
            body["acquireActionRates"] = [
                item.to_dict()
                for item in request.acquire_action_rates
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateExperienceModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_experience_model_master(
        self,
        request: CreateExperienceModelMasterRequest,
    ) -> CreateExperienceModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_experience_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_experience_model_master_async(
        self,
        request: CreateExperienceModelMasterRequest,
    ) -> CreateExperienceModelMasterResult:
        async_result = []
        self._create_experience_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_experience_model_master(
        self,
        request: GetExperienceModelMasterRequest,
        callback: Callable[[AsyncResult[GetExperienceModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='getExperienceModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetExperienceModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_experience_model_master(
        self,
        request: GetExperienceModelMasterRequest,
    ) -> GetExperienceModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_experience_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_experience_model_master_async(
        self,
        request: GetExperienceModelMasterRequest,
    ) -> GetExperienceModelMasterResult:
        async_result = []
        self._get_experience_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_experience_model_master(
        self,
        request: UpdateExperienceModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateExperienceModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='updateExperienceModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.default_experience is not None:
            body["defaultExperience"] = request.default_experience
        if request.default_rank_cap is not None:
            body["defaultRankCap"] = request.default_rank_cap
        if request.max_rank_cap is not None:
            body["maxRankCap"] = request.max_rank_cap
        if request.rank_threshold_name is not None:
            body["rankThresholdName"] = request.rank_threshold_name
        if request.acquire_action_rates is not None:
            body["acquireActionRates"] = [
                item.to_dict()
                for item in request.acquire_action_rates
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateExperienceModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_experience_model_master(
        self,
        request: UpdateExperienceModelMasterRequest,
    ) -> UpdateExperienceModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_experience_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_experience_model_master_async(
        self,
        request: UpdateExperienceModelMasterRequest,
    ) -> UpdateExperienceModelMasterResult:
        async_result = []
        self._update_experience_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_experience_model_master(
        self,
        request: DeleteExperienceModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteExperienceModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModelMaster',
            function='deleteExperienceModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteExperienceModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_experience_model_master(
        self,
        request: DeleteExperienceModelMasterRequest,
    ) -> DeleteExperienceModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_experience_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_experience_model_master_async(
        self,
        request: DeleteExperienceModelMasterRequest,
    ) -> DeleteExperienceModelMasterResult:
        async_result = []
        self._delete_experience_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_experience_models(
        self,
        request: DescribeExperienceModelsRequest,
        callback: Callable[[AsyncResult[DescribeExperienceModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModel',
            function='describeExperienceModels',
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
                result_type=DescribeExperienceModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_experience_models(
        self,
        request: DescribeExperienceModelsRequest,
    ) -> DescribeExperienceModelsResult:
        async_result = []
        with timeout(30):
            self._describe_experience_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_experience_models_async(
        self,
        request: DescribeExperienceModelsRequest,
    ) -> DescribeExperienceModelsResult:
        async_result = []
        self._describe_experience_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_experience_model(
        self,
        request: GetExperienceModelRequest,
        callback: Callable[[AsyncResult[GetExperienceModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='experienceModel',
            function='getExperienceModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetExperienceModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_experience_model(
        self,
        request: GetExperienceModelRequest,
    ) -> GetExperienceModelResult:
        async_result = []
        with timeout(30):
            self._get_experience_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_experience_model_async(
        self,
        request: GetExperienceModelRequest,
    ) -> GetExperienceModelResult:
        async_result = []
        self._get_experience_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_threshold_masters(
        self,
        request: DescribeThresholdMastersRequest,
        callback: Callable[[AsyncResult[DescribeThresholdMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='describeThresholdMasters',
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
                result_type=DescribeThresholdMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_threshold_masters(
        self,
        request: DescribeThresholdMastersRequest,
    ) -> DescribeThresholdMastersResult:
        async_result = []
        with timeout(30):
            self._describe_threshold_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_threshold_masters_async(
        self,
        request: DescribeThresholdMastersRequest,
    ) -> DescribeThresholdMastersResult:
        async_result = []
        self._describe_threshold_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_threshold_master(
        self,
        request: CreateThresholdMasterRequest,
        callback: Callable[[AsyncResult[CreateThresholdMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='createThresholdMaster',
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
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateThresholdMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_threshold_master(
        self,
        request: CreateThresholdMasterRequest,
    ) -> CreateThresholdMasterResult:
        async_result = []
        with timeout(30):
            self._create_threshold_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_threshold_master_async(
        self,
        request: CreateThresholdMasterRequest,
    ) -> CreateThresholdMasterResult:
        async_result = []
        self._create_threshold_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_threshold_master(
        self,
        request: GetThresholdMasterRequest,
        callback: Callable[[AsyncResult[GetThresholdMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='getThresholdMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.threshold_name is not None:
            body["thresholdName"] = request.threshold_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetThresholdMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_threshold_master(
        self,
        request: GetThresholdMasterRequest,
    ) -> GetThresholdMasterResult:
        async_result = []
        with timeout(30):
            self._get_threshold_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_threshold_master_async(
        self,
        request: GetThresholdMasterRequest,
    ) -> GetThresholdMasterResult:
        async_result = []
        self._get_threshold_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_threshold_master(
        self,
        request: UpdateThresholdMasterRequest,
        callback: Callable[[AsyncResult[UpdateThresholdMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='updateThresholdMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.threshold_name is not None:
            body["thresholdName"] = request.threshold_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateThresholdMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_threshold_master(
        self,
        request: UpdateThresholdMasterRequest,
    ) -> UpdateThresholdMasterResult:
        async_result = []
        with timeout(30):
            self._update_threshold_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_threshold_master_async(
        self,
        request: UpdateThresholdMasterRequest,
    ) -> UpdateThresholdMasterResult:
        async_result = []
        self._update_threshold_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_threshold_master(
        self,
        request: DeleteThresholdMasterRequest,
        callback: Callable[[AsyncResult[DeleteThresholdMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='thresholdMaster',
            function='deleteThresholdMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.threshold_name is not None:
            body["thresholdName"] = request.threshold_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteThresholdMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_threshold_master(
        self,
        request: DeleteThresholdMasterRequest,
    ) -> DeleteThresholdMasterResult:
        async_result = []
        with timeout(30):
            self._delete_threshold_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_threshold_master_async(
        self,
        request: DeleteThresholdMasterRequest,
    ) -> DeleteThresholdMasterResult:
        async_result = []
        self._delete_threshold_master(
            request,
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
            service="experience",
            component='currentExperienceMaster',
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

    def _get_current_experience_master(
        self,
        request: GetCurrentExperienceMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentExperienceMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='currentExperienceMaster',
            function='getCurrentExperienceMaster',
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
                result_type=GetCurrentExperienceMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_experience_master(
        self,
        request: GetCurrentExperienceMasterRequest,
    ) -> GetCurrentExperienceMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_experience_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_experience_master_async(
        self,
        request: GetCurrentExperienceMasterRequest,
    ) -> GetCurrentExperienceMasterResult:
        async_result = []
        self._get_current_experience_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _pre_update_current_experience_master(
        self,
        request: PreUpdateCurrentExperienceMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentExperienceMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='currentExperienceMaster',
            function='preUpdateCurrentExperienceMaster',
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
                result_type=PreUpdateCurrentExperienceMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_experience_master(
        self,
        request: PreUpdateCurrentExperienceMasterRequest,
    ) -> PreUpdateCurrentExperienceMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_experience_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_experience_master_async(
        self,
        request: PreUpdateCurrentExperienceMasterRequest,
    ) -> PreUpdateCurrentExperienceMasterResult:
        async_result = []
        self._pre_update_current_experience_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_experience_master(
        self,
        request: UpdateCurrentExperienceMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentExperienceMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='currentExperienceMaster',
            function='updateCurrentExperienceMaster',
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
                result_type=UpdateCurrentExperienceMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_experience_master(
        self,
        request: UpdateCurrentExperienceMasterRequest,
    ) -> UpdateCurrentExperienceMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_experience_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_experience_master_async(
        self,
        request: UpdateCurrentExperienceMasterRequest,
    ) -> UpdateCurrentExperienceMasterResult:
        async_result = []
        self._update_current_experience_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_experience_master_from_git_hub(
        self,
        request: UpdateCurrentExperienceMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentExperienceMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='currentExperienceMaster',
            function='updateCurrentExperienceMasterFromGitHub',
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
                result_type=UpdateCurrentExperienceMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_experience_master_from_git_hub(
        self,
        request: UpdateCurrentExperienceMasterFromGitHubRequest,
    ) -> UpdateCurrentExperienceMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_experience_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_experience_master_from_git_hub_async(
        self,
        request: UpdateCurrentExperienceMasterFromGitHubRequest,
    ) -> UpdateCurrentExperienceMasterFromGitHubResult:
        async_result = []
        self._update_current_experience_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_statuses(
        self,
        request: DescribeStatusesRequest,
        callback: Callable[[AsyncResult[DescribeStatusesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='describeStatuses',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
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
                result_type=DescribeStatusesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_statuses(
        self,
        request: DescribeStatusesRequest,
    ) -> DescribeStatusesResult:
        async_result = []
        with timeout(30):
            self._describe_statuses(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_statuses_async(
        self,
        request: DescribeStatusesRequest,
    ) -> DescribeStatusesResult:
        async_result = []
        self._describe_statuses(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_statuses_by_user_id(
        self,
        request: DescribeStatusesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeStatusesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='describeStatusesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
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
                result_type=DescribeStatusesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_statuses_by_user_id(
        self,
        request: DescribeStatusesByUserIdRequest,
    ) -> DescribeStatusesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_statuses_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_statuses_by_user_id_async(
        self,
        request: DescribeStatusesByUserIdRequest,
    ) -> DescribeStatusesByUserIdResult:
        async_result = []
        self._describe_statuses_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_status(
        self,
        request: GetStatusRequest,
        callback: Callable[[AsyncResult[GetStatusResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='getStatus',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStatusResult,
                callback=callback,
                body=body,
            )
        )

    def get_status(
        self,
        request: GetStatusRequest,
    ) -> GetStatusResult:
        async_result = []
        with timeout(30):
            self._get_status(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_status_async(
        self,
        request: GetStatusRequest,
    ) -> GetStatusResult:
        async_result = []
        self._get_status(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_status_by_user_id(
        self,
        request: GetStatusByUserIdRequest,
        callback: Callable[[AsyncResult[GetStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='getStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_status_by_user_id(
        self,
        request: GetStatusByUserIdRequest,
    ) -> GetStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_status_by_user_id_async(
        self,
        request: GetStatusByUserIdRequest,
    ) -> GetStatusByUserIdResult:
        async_result = []
        self._get_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_status_with_signature(
        self,
        request: GetStatusWithSignatureRequest,
        callback: Callable[[AsyncResult[GetStatusWithSignatureResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='getStatusWithSignature',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
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
                result_type=GetStatusWithSignatureResult,
                callback=callback,
                body=body,
            )
        )

    def get_status_with_signature(
        self,
        request: GetStatusWithSignatureRequest,
    ) -> GetStatusWithSignatureResult:
        async_result = []
        with timeout(30):
            self._get_status_with_signature(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_status_with_signature_async(
        self,
        request: GetStatusWithSignatureRequest,
    ) -> GetStatusWithSignatureResult:
        async_result = []
        self._get_status_with_signature(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_status_with_signature_by_user_id(
        self,
        request: GetStatusWithSignatureByUserIdRequest,
        callback: Callable[[AsyncResult[GetStatusWithSignatureByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='getStatusWithSignatureByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
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
                result_type=GetStatusWithSignatureByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_status_with_signature_by_user_id(
        self,
        request: GetStatusWithSignatureByUserIdRequest,
    ) -> GetStatusWithSignatureByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_status_with_signature_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_status_with_signature_by_user_id_async(
        self,
        request: GetStatusWithSignatureByUserIdRequest,
    ) -> GetStatusWithSignatureByUserIdResult:
        async_result = []
        self._get_status_with_signature_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_experience_by_user_id(
        self,
        request: AddExperienceByUserIdRequest,
        callback: Callable[[AsyncResult[AddExperienceByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='addExperienceByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.experience_value is not None:
            body["experienceValue"] = request.experience_value
        if request.truncate_experience_when_rank_up is not None:
            body["truncateExperienceWhenRankUp"] = request.truncate_experience_when_rank_up
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AddExperienceByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_experience_by_user_id(
        self,
        request: AddExperienceByUserIdRequest,
    ) -> AddExperienceByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_experience_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_experience_by_user_id_async(
        self,
        request: AddExperienceByUserIdRequest,
    ) -> AddExperienceByUserIdResult:
        async_result = []
        self._add_experience_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_experience(
        self,
        request: SubExperienceRequest,
        callback: Callable[[AsyncResult[SubExperienceResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='subExperience',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.experience_value is not None:
            body["experienceValue"] = request.experience_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SubExperienceResult,
                callback=callback,
                body=body,
            )
        )

    def sub_experience(
        self,
        request: SubExperienceRequest,
    ) -> SubExperienceResult:
        async_result = []
        with timeout(30):
            self._sub_experience(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_experience_async(
        self,
        request: SubExperienceRequest,
    ) -> SubExperienceResult:
        async_result = []
        self._sub_experience(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_experience_by_user_id(
        self,
        request: SubExperienceByUserIdRequest,
        callback: Callable[[AsyncResult[SubExperienceByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='subExperienceByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.experience_value is not None:
            body["experienceValue"] = request.experience_value
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SubExperienceByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def sub_experience_by_user_id(
        self,
        request: SubExperienceByUserIdRequest,
    ) -> SubExperienceByUserIdResult:
        async_result = []
        with timeout(30):
            self._sub_experience_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_experience_by_user_id_async(
        self,
        request: SubExperienceByUserIdRequest,
    ) -> SubExperienceByUserIdResult:
        async_result = []
        self._sub_experience_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_experience_by_user_id(
        self,
        request: SetExperienceByUserIdRequest,
        callback: Callable[[AsyncResult[SetExperienceByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='setExperienceByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.experience_value is not None:
            body["experienceValue"] = request.experience_value
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SetExperienceByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_experience_by_user_id(
        self,
        request: SetExperienceByUserIdRequest,
    ) -> SetExperienceByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_experience_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_experience_by_user_id_async(
        self,
        request: SetExperienceByUserIdRequest,
    ) -> SetExperienceByUserIdResult:
        async_result = []
        self._set_experience_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_rank_cap_by_user_id(
        self,
        request: AddRankCapByUserIdRequest,
        callback: Callable[[AsyncResult[AddRankCapByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='addRankCapByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_cap_value is not None:
            body["rankCapValue"] = request.rank_cap_value
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AddRankCapByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def add_rank_cap_by_user_id(
        self,
        request: AddRankCapByUserIdRequest,
    ) -> AddRankCapByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_rank_cap_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_rank_cap_by_user_id_async(
        self,
        request: AddRankCapByUserIdRequest,
    ) -> AddRankCapByUserIdResult:
        async_result = []
        self._add_rank_cap_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_rank_cap(
        self,
        request: SubRankCapRequest,
        callback: Callable[[AsyncResult[SubRankCapResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='subRankCap',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_cap_value is not None:
            body["rankCapValue"] = request.rank_cap_value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SubRankCapResult,
                callback=callback,
                body=body,
            )
        )

    def sub_rank_cap(
        self,
        request: SubRankCapRequest,
    ) -> SubRankCapResult:
        async_result = []
        with timeout(30):
            self._sub_rank_cap(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_rank_cap_async(
        self,
        request: SubRankCapRequest,
    ) -> SubRankCapResult:
        async_result = []
        self._sub_rank_cap(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_rank_cap_by_user_id(
        self,
        request: SubRankCapByUserIdRequest,
        callback: Callable[[AsyncResult[SubRankCapByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='subRankCapByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_cap_value is not None:
            body["rankCapValue"] = request.rank_cap_value
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SubRankCapByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def sub_rank_cap_by_user_id(
        self,
        request: SubRankCapByUserIdRequest,
    ) -> SubRankCapByUserIdResult:
        async_result = []
        with timeout(30):
            self._sub_rank_cap_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_rank_cap_by_user_id_async(
        self,
        request: SubRankCapByUserIdRequest,
    ) -> SubRankCapByUserIdResult:
        async_result = []
        self._sub_rank_cap_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_rank_cap_by_user_id(
        self,
        request: SetRankCapByUserIdRequest,
        callback: Callable[[AsyncResult[SetRankCapByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='setRankCapByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_cap_value is not None:
            body["rankCapValue"] = request.rank_cap_value
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SetRankCapByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def set_rank_cap_by_user_id(
        self,
        request: SetRankCapByUserIdRequest,
    ) -> SetRankCapByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_rank_cap_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_rank_cap_by_user_id_async(
        self,
        request: SetRankCapByUserIdRequest,
    ) -> SetRankCapByUserIdResult:
        async_result = []
        self._set_rank_cap_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_status_by_user_id(
        self,
        request: DeleteStatusByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteStatusByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='deleteStatusByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
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
                result_type=DeleteStatusByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_status_by_user_id(
        self,
        request: DeleteStatusByUserIdRequest,
    ) -> DeleteStatusByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_status_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_status_by_user_id_async(
        self,
        request: DeleteStatusByUserIdRequest,
    ) -> DeleteStatusByUserIdResult:
        async_result = []
        self._delete_status_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rank(
        self,
        request: VerifyRankRequest,
        callback: Callable[[AsyncResult[VerifyRankResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='verifyRank',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_value is not None:
            body["rankValue"] = request.rank_value
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
                result_type=VerifyRankResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rank(
        self,
        request: VerifyRankRequest,
    ) -> VerifyRankResult:
        async_result = []
        with timeout(30):
            self._verify_rank(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rank_async(
        self,
        request: VerifyRankRequest,
    ) -> VerifyRankResult:
        async_result = []
        self._verify_rank(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rank_by_user_id(
        self,
        request: VerifyRankByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyRankByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='verifyRankByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_value is not None:
            body["rankValue"] = request.rank_value
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
                result_type=VerifyRankByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rank_by_user_id(
        self,
        request: VerifyRankByUserIdRequest,
    ) -> VerifyRankByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_rank_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rank_by_user_id_async(
        self,
        request: VerifyRankByUserIdRequest,
    ) -> VerifyRankByUserIdResult:
        async_result = []
        self._verify_rank_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rank_cap(
        self,
        request: VerifyRankCapRequest,
        callback: Callable[[AsyncResult[VerifyRankCapResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='verifyRankCap',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_cap_value is not None:
            body["rankCapValue"] = request.rank_cap_value
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
                result_type=VerifyRankCapResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rank_cap(
        self,
        request: VerifyRankCapRequest,
    ) -> VerifyRankCapResult:
        async_result = []
        with timeout(30):
            self._verify_rank_cap(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rank_cap_async(
        self,
        request: VerifyRankCapRequest,
    ) -> VerifyRankCapResult:
        async_result = []
        self._verify_rank_cap(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rank_cap_by_user_id(
        self,
        request: VerifyRankCapByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyRankCapByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='verifyRankCapByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rank_cap_value is not None:
            body["rankCapValue"] = request.rank_cap_value
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
                result_type=VerifyRankCapByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rank_cap_by_user_id(
        self,
        request: VerifyRankCapByUserIdRequest,
    ) -> VerifyRankCapByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_rank_cap_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rank_cap_by_user_id_async(
        self,
        request: VerifyRankCapByUserIdRequest,
    ) -> VerifyRankCapByUserIdResult:
        async_result = []
        self._verify_rank_cap_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_experience_by_stamp_sheet(
        self,
        request: AddExperienceByStampSheetRequest,
        callback: Callable[[AsyncResult[AddExperienceByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='addExperienceByStampSheet',
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
                result_type=AddExperienceByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def add_experience_by_stamp_sheet(
        self,
        request: AddExperienceByStampSheetRequest,
    ) -> AddExperienceByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_experience_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_experience_by_stamp_sheet_async(
        self,
        request: AddExperienceByStampSheetRequest,
    ) -> AddExperienceByStampSheetResult:
        async_result = []
        self._add_experience_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_experience_by_stamp_sheet(
        self,
        request: SetExperienceByStampSheetRequest,
        callback: Callable[[AsyncResult[SetExperienceByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='setExperienceByStampSheet',
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
                result_type=SetExperienceByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_experience_by_stamp_sheet(
        self,
        request: SetExperienceByStampSheetRequest,
    ) -> SetExperienceByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_experience_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_experience_by_stamp_sheet_async(
        self,
        request: SetExperienceByStampSheetRequest,
    ) -> SetExperienceByStampSheetResult:
        async_result = []
        self._set_experience_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_experience_by_stamp_task(
        self,
        request: SubExperienceByStampTaskRequest,
        callback: Callable[[AsyncResult[SubExperienceByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='subExperienceByStampTask',
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
                result_type=SubExperienceByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def sub_experience_by_stamp_task(
        self,
        request: SubExperienceByStampTaskRequest,
    ) -> SubExperienceByStampTaskResult:
        async_result = []
        with timeout(30):
            self._sub_experience_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_experience_by_stamp_task_async(
        self,
        request: SubExperienceByStampTaskRequest,
    ) -> SubExperienceByStampTaskResult:
        async_result = []
        self._sub_experience_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_rank_cap_by_stamp_sheet(
        self,
        request: AddRankCapByStampSheetRequest,
        callback: Callable[[AsyncResult[AddRankCapByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='addRankCapByStampSheet',
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
                result_type=AddRankCapByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def add_rank_cap_by_stamp_sheet(
        self,
        request: AddRankCapByStampSheetRequest,
    ) -> AddRankCapByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_rank_cap_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_rank_cap_by_stamp_sheet_async(
        self,
        request: AddRankCapByStampSheetRequest,
    ) -> AddRankCapByStampSheetResult:
        async_result = []
        self._add_rank_cap_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _sub_rank_cap_by_stamp_task(
        self,
        request: SubRankCapByStampTaskRequest,
        callback: Callable[[AsyncResult[SubRankCapByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='subRankCapByStampTask',
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
                result_type=SubRankCapByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def sub_rank_cap_by_stamp_task(
        self,
        request: SubRankCapByStampTaskRequest,
    ) -> SubRankCapByStampTaskResult:
        async_result = []
        with timeout(30):
            self._sub_rank_cap_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def sub_rank_cap_by_stamp_task_async(
        self,
        request: SubRankCapByStampTaskRequest,
    ) -> SubRankCapByStampTaskResult:
        async_result = []
        self._sub_rank_cap_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_rank_cap_by_stamp_sheet(
        self,
        request: SetRankCapByStampSheetRequest,
        callback: Callable[[AsyncResult[SetRankCapByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='setRankCapByStampSheet',
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
                result_type=SetRankCapByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_rank_cap_by_stamp_sheet(
        self,
        request: SetRankCapByStampSheetRequest,
    ) -> SetRankCapByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_rank_cap_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_rank_cap_by_stamp_sheet_async(
        self,
        request: SetRankCapByStampSheetRequest,
    ) -> SetRankCapByStampSheetResult:
        async_result = []
        self._set_rank_cap_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _multiply_acquire_actions_by_user_id(
        self,
        request: MultiplyAcquireActionsByUserIdRequest,
        callback: Callable[[AsyncResult[MultiplyAcquireActionsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='multiplyAcquireActionsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.experience_name is not None:
            body["experienceName"] = request.experience_name
        if request.property_id is not None:
            body["propertyId"] = request.property_id
        if request.rate_name is not None:
            body["rateName"] = request.rate_name
        if request.acquire_actions is not None:
            body["acquireActions"] = [
                item.to_dict()
                for item in request.acquire_actions
            ]
        if request.base_rate is not None:
            body["baseRate"] = request.base_rate
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=MultiplyAcquireActionsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def multiply_acquire_actions_by_user_id(
        self,
        request: MultiplyAcquireActionsByUserIdRequest,
    ) -> MultiplyAcquireActionsByUserIdResult:
        async_result = []
        with timeout(30):
            self._multiply_acquire_actions_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def multiply_acquire_actions_by_user_id_async(
        self,
        request: MultiplyAcquireActionsByUserIdRequest,
    ) -> MultiplyAcquireActionsByUserIdResult:
        async_result = []
        self._multiply_acquire_actions_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _multiply_acquire_actions_by_stamp_sheet(
        self,
        request: MultiplyAcquireActionsByStampSheetRequest,
        callback: Callable[[AsyncResult[MultiplyAcquireActionsByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='multiplyAcquireActionsByStampSheet',
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
                result_type=MultiplyAcquireActionsByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def multiply_acquire_actions_by_stamp_sheet(
        self,
        request: MultiplyAcquireActionsByStampSheetRequest,
    ) -> MultiplyAcquireActionsByStampSheetResult:
        async_result = []
        with timeout(30):
            self._multiply_acquire_actions_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def multiply_acquire_actions_by_stamp_sheet_async(
        self,
        request: MultiplyAcquireActionsByStampSheetRequest,
    ) -> MultiplyAcquireActionsByStampSheetResult:
        async_result = []
        self._multiply_acquire_actions_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rank_by_stamp_task(
        self,
        request: VerifyRankByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyRankByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='verifyRankByStampTask',
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
                result_type=VerifyRankByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rank_by_stamp_task(
        self,
        request: VerifyRankByStampTaskRequest,
    ) -> VerifyRankByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_rank_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rank_by_stamp_task_async(
        self,
        request: VerifyRankByStampTaskRequest,
    ) -> VerifyRankByStampTaskResult:
        async_result = []
        self._verify_rank_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_rank_cap_by_stamp_task(
        self,
        request: VerifyRankCapByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyRankCapByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="experience",
            component='status',
            function='verifyRankCapByStampTask',
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
                result_type=VerifyRankCapByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_rank_cap_by_stamp_task(
        self,
        request: VerifyRankCapByStampTaskRequest,
    ) -> VerifyRankCapByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_rank_cap_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_rank_cap_by_stamp_task_async(
        self,
        request: VerifyRankCapByStampTaskRequest,
    ) -> VerifyRankCapByStampTaskResult:
        async_result = []
        self._verify_rank_cap_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result