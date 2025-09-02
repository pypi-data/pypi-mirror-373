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


class Gs2AccountWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
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
            service="account",
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
        if request.change_password_if_take_over is not None:
            body["changePasswordIfTakeOver"] = request.change_password_if_take_over
        if request.different_user_id_for_login_and_data_retention is not None:
            body["differentUserIdForLoginAndDataRetention"] = request.different_user_id_for_login_and_data_retention
        if request.create_account_script is not None:
            body["createAccountScript"] = request.create_account_script.to_dict()
        if request.authentication_script is not None:
            body["authenticationScript"] = request.authentication_script.to_dict()
        if request.create_take_over_script is not None:
            body["createTakeOverScript"] = request.create_take_over_script.to_dict()
        if request.do_take_over_script is not None:
            body["doTakeOverScript"] = request.do_take_over_script.to_dict()
        if request.ban_script is not None:
            body["banScript"] = request.ban_script.to_dict()
        if request.un_ban_script is not None:
            body["unBanScript"] = request.un_ban_script.to_dict()
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
            service="account",
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
            service="account",
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
            service="account",
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
        if request.change_password_if_take_over is not None:
            body["changePasswordIfTakeOver"] = request.change_password_if_take_over
        if request.create_account_script is not None:
            body["createAccountScript"] = request.create_account_script.to_dict()
        if request.authentication_script is not None:
            body["authenticationScript"] = request.authentication_script.to_dict()
        if request.create_take_over_script is not None:
            body["createTakeOverScript"] = request.create_take_over_script.to_dict()
        if request.do_take_over_script is not None:
            body["doTakeOverScript"] = request.do_take_over_script.to_dict()
        if request.ban_script is not None:
            body["banScript"] = request.ban_script.to_dict()
        if request.un_ban_script is not None:
            body["unBanScript"] = request.un_ban_script.to_dict()
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
            service="account",
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
            service="account",
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
            service="account",
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
            service="account",
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
            service="account",
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
            service="account",
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
            service="account",
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
            service="account",
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
            service="account",
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

    def _describe_accounts(
        self,
        request: DescribeAccountsRequest,
        callback: Callable[[AsyncResult[DescribeAccountsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='describeAccounts',
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
                result_type=DescribeAccountsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_accounts(
        self,
        request: DescribeAccountsRequest,
    ) -> DescribeAccountsResult:
        async_result = []
        with timeout(30):
            self._describe_accounts(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_accounts_async(
        self,
        request: DescribeAccountsRequest,
    ) -> DescribeAccountsResult:
        async_result = []
        self._describe_accounts(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_account(
        self,
        request: CreateAccountRequest,
        callback: Callable[[AsyncResult[CreateAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='createAccount',
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
                result_type=CreateAccountResult,
                callback=callback,
                body=body,
            )
        )

    def create_account(
        self,
        request: CreateAccountRequest,
    ) -> CreateAccountResult:
        async_result = []
        with timeout(30):
            self._create_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_account_async(
        self,
        request: CreateAccountRequest,
    ) -> CreateAccountResult:
        async_result = []
        self._create_account(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_time_offset(
        self,
        request: UpdateTimeOffsetRequest,
        callback: Callable[[AsyncResult[UpdateTimeOffsetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='updateTimeOffset',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset is not None:
            body["timeOffset"] = request.time_offset
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateTimeOffsetResult,
                callback=callback,
                body=body,
            )
        )

    def update_time_offset(
        self,
        request: UpdateTimeOffsetRequest,
    ) -> UpdateTimeOffsetResult:
        async_result = []
        with timeout(30):
            self._update_time_offset(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_time_offset_async(
        self,
        request: UpdateTimeOffsetRequest,
    ) -> UpdateTimeOffsetResult:
        async_result = []
        self._update_time_offset(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_banned(
        self,
        request: UpdateBannedRequest,
        callback: Callable[[AsyncResult[UpdateBannedResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='updateBanned',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.banned is not None:
            body["banned"] = request.banned
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateBannedResult,
                callback=callback,
                body=body,
            )
        )

    def update_banned(
        self,
        request: UpdateBannedRequest,
    ) -> UpdateBannedResult:
        async_result = []
        with timeout(30):
            self._update_banned(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_banned_async(
        self,
        request: UpdateBannedRequest,
    ) -> UpdateBannedResult:
        async_result = []
        self._update_banned(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_ban(
        self,
        request: AddBanRequest,
        callback: Callable[[AsyncResult[AddBanResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='addBan',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ban_status is not None:
            body["banStatus"] = request.ban_status.to_dict()
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AddBanResult,
                callback=callback,
                body=body,
            )
        )

    def add_ban(
        self,
        request: AddBanRequest,
    ) -> AddBanResult:
        async_result = []
        with timeout(30):
            self._add_ban(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_ban_async(
        self,
        request: AddBanRequest,
    ) -> AddBanResult:
        async_result = []
        self._add_ban(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _remove_ban(
        self,
        request: RemoveBanRequest,
        callback: Callable[[AsyncResult[RemoveBanResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='removeBan',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.ban_status_name is not None:
            body["banStatusName"] = request.ban_status_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=RemoveBanResult,
                callback=callback,
                body=body,
            )
        )

    def remove_ban(
        self,
        request: RemoveBanRequest,
    ) -> RemoveBanResult:
        async_result = []
        with timeout(30):
            self._remove_ban(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def remove_ban_async(
        self,
        request: RemoveBanRequest,
    ) -> RemoveBanResult:
        async_result = []
        self._remove_ban(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_account(
        self,
        request: GetAccountRequest,
        callback: Callable[[AsyncResult[GetAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='getAccount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.include_last_authenticated_at is not None:
            body["includeLastAuthenticatedAt"] = request.include_last_authenticated_at
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetAccountResult,
                callback=callback,
                body=body,
            )
        )

    def get_account(
        self,
        request: GetAccountRequest,
    ) -> GetAccountResult:
        async_result = []
        with timeout(30):
            self._get_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_account_async(
        self,
        request: GetAccountRequest,
    ) -> GetAccountResult:
        async_result = []
        self._get_account(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_account(
        self,
        request: DeleteAccountRequest,
        callback: Callable[[AsyncResult[DeleteAccountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='deleteAccount',
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
                result_type=DeleteAccountResult,
                callback=callback,
                body=body,
            )
        )

    def delete_account(
        self,
        request: DeleteAccountRequest,
    ) -> DeleteAccountResult:
        async_result = []
        with timeout(30):
            self._delete_account(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_account_async(
        self,
        request: DeleteAccountRequest,
    ) -> DeleteAccountResult:
        async_result = []
        self._delete_account(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _authentication(
        self,
        request: AuthenticationRequest,
        callback: Callable[[AsyncResult[AuthenticationResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='account',
            function='authentication',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.password is not None:
            body["password"] = request.password
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AuthenticationResult,
                callback=callback,
                body=body,
            )
        )

    def authentication(
        self,
        request: AuthenticationRequest,
    ) -> AuthenticationResult:
        async_result = []
        with timeout(30):
            self._authentication(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def authentication_async(
        self,
        request: AuthenticationRequest,
    ) -> AuthenticationResult:
        async_result = []
        self._authentication(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_take_overs(
        self,
        request: DescribeTakeOversRequest,
        callback: Callable[[AsyncResult[DescribeTakeOversResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='describeTakeOvers',
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
                result_type=DescribeTakeOversResult,
                callback=callback,
                body=body,
            )
        )

    def describe_take_overs(
        self,
        request: DescribeTakeOversRequest,
    ) -> DescribeTakeOversResult:
        async_result = []
        with timeout(30):
            self._describe_take_overs(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_take_overs_async(
        self,
        request: DescribeTakeOversRequest,
    ) -> DescribeTakeOversResult:
        async_result = []
        self._describe_take_overs(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_take_overs_by_user_id(
        self,
        request: DescribeTakeOversByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeTakeOversByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='describeTakeOversByUserId',
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
                result_type=DescribeTakeOversByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_take_overs_by_user_id(
        self,
        request: DescribeTakeOversByUserIdRequest,
    ) -> DescribeTakeOversByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_take_overs_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_take_overs_by_user_id_async(
        self,
        request: DescribeTakeOversByUserIdRequest,
    ) -> DescribeTakeOversByUserIdResult:
        async_result = []
        self._describe_take_overs_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_take_over(
        self,
        request: CreateTakeOverRequest,
        callback: Callable[[AsyncResult[CreateTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='createTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def create_take_over(
        self,
        request: CreateTakeOverRequest,
    ) -> CreateTakeOverResult:
        async_result = []
        with timeout(30):
            self._create_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_take_over_async(
        self,
        request: CreateTakeOverRequest,
    ) -> CreateTakeOverResult:
        async_result = []
        self._create_take_over(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_take_over_by_user_id(
        self,
        request: CreateTakeOverByUserIdRequest,
        callback: Callable[[AsyncResult[CreateTakeOverByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='createTakeOverByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier
        if request.password is not None:
            body["password"] = request.password
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateTakeOverByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_take_over_by_user_id(
        self,
        request: CreateTakeOverByUserIdRequest,
    ) -> CreateTakeOverByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_take_over_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_take_over_by_user_id_async(
        self,
        request: CreateTakeOverByUserIdRequest,
    ) -> CreateTakeOverByUserIdResult:
        async_result = []
        self._create_take_over_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_take_over_open_id_connect(
        self,
        request: CreateTakeOverOpenIdConnectRequest,
        callback: Callable[[AsyncResult[CreateTakeOverOpenIdConnectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='createTakeOverOpenIdConnect',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.id_token is not None:
            body["idToken"] = request.id_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateTakeOverOpenIdConnectResult,
                callback=callback,
                body=body,
            )
        )

    def create_take_over_open_id_connect(
        self,
        request: CreateTakeOverOpenIdConnectRequest,
    ) -> CreateTakeOverOpenIdConnectResult:
        async_result = []
        with timeout(30):
            self._create_take_over_open_id_connect(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_take_over_open_id_connect_async(
        self,
        request: CreateTakeOverOpenIdConnectRequest,
    ) -> CreateTakeOverOpenIdConnectResult:
        async_result = []
        self._create_take_over_open_id_connect(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_take_over_open_id_connect_and_by_user_id(
        self,
        request: CreateTakeOverOpenIdConnectAndByUserIdRequest,
        callback: Callable[[AsyncResult[CreateTakeOverOpenIdConnectAndByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='createTakeOverOpenIdConnectAndByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.id_token is not None:
            body["idToken"] = request.id_token
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateTakeOverOpenIdConnectAndByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_take_over_open_id_connect_and_by_user_id(
        self,
        request: CreateTakeOverOpenIdConnectAndByUserIdRequest,
    ) -> CreateTakeOverOpenIdConnectAndByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_take_over_open_id_connect_and_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_take_over_open_id_connect_and_by_user_id_async(
        self,
        request: CreateTakeOverOpenIdConnectAndByUserIdRequest,
    ) -> CreateTakeOverOpenIdConnectAndByUserIdResult:
        async_result = []
        self._create_take_over_open_id_connect_and_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_take_over(
        self,
        request: GetTakeOverRequest,
        callback: Callable[[AsyncResult[GetTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='getTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def get_take_over(
        self,
        request: GetTakeOverRequest,
    ) -> GetTakeOverResult:
        async_result = []
        with timeout(30):
            self._get_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_take_over_async(
        self,
        request: GetTakeOverRequest,
    ) -> GetTakeOverResult:
        async_result = []
        self._get_take_over(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_take_over_by_user_id(
        self,
        request: GetTakeOverByUserIdRequest,
        callback: Callable[[AsyncResult[GetTakeOverByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='getTakeOverByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetTakeOverByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_take_over_by_user_id(
        self,
        request: GetTakeOverByUserIdRequest,
    ) -> GetTakeOverByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_take_over_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_take_over_by_user_id_async(
        self,
        request: GetTakeOverByUserIdRequest,
    ) -> GetTakeOverByUserIdResult:
        async_result = []
        self._get_take_over_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_take_over(
        self,
        request: UpdateTakeOverRequest,
        callback: Callable[[AsyncResult[UpdateTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='updateTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.old_password is not None:
            body["oldPassword"] = request.old_password
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def update_take_over(
        self,
        request: UpdateTakeOverRequest,
    ) -> UpdateTakeOverResult:
        async_result = []
        with timeout(30):
            self._update_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_take_over_async(
        self,
        request: UpdateTakeOverRequest,
    ) -> UpdateTakeOverResult:
        async_result = []
        self._update_take_over(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_take_over_by_user_id(
        self,
        request: UpdateTakeOverByUserIdRequest,
        callback: Callable[[AsyncResult[UpdateTakeOverByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='updateTakeOverByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.old_password is not None:
            body["oldPassword"] = request.old_password
        if request.password is not None:
            body["password"] = request.password
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateTakeOverByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def update_take_over_by_user_id(
        self,
        request: UpdateTakeOverByUserIdRequest,
    ) -> UpdateTakeOverByUserIdResult:
        async_result = []
        with timeout(30):
            self._update_take_over_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_take_over_by_user_id_async(
        self,
        request: UpdateTakeOverByUserIdRequest,
    ) -> UpdateTakeOverByUserIdResult:
        async_result = []
        self._update_take_over_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_take_over(
        self,
        request: DeleteTakeOverRequest,
        callback: Callable[[AsyncResult[DeleteTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='deleteTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def delete_take_over(
        self,
        request: DeleteTakeOverRequest,
    ) -> DeleteTakeOverResult:
        async_result = []
        with timeout(30):
            self._delete_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_take_over_async(
        self,
        request: DeleteTakeOverRequest,
    ) -> DeleteTakeOverResult:
        async_result = []
        self._delete_take_over(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_take_over_by_user_identifier(
        self,
        request: DeleteTakeOverByUserIdentifierRequest,
        callback: Callable[[AsyncResult[DeleteTakeOverByUserIdentifierResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='deleteTakeOverByUserIdentifier',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteTakeOverByUserIdentifierResult,
                callback=callback,
                body=body,
            )
        )

    def delete_take_over_by_user_identifier(
        self,
        request: DeleteTakeOverByUserIdentifierRequest,
    ) -> DeleteTakeOverByUserIdentifierResult:
        async_result = []
        with timeout(30):
            self._delete_take_over_by_user_identifier(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_take_over_by_user_identifier_async(
        self,
        request: DeleteTakeOverByUserIdentifierRequest,
    ) -> DeleteTakeOverByUserIdentifierResult:
        async_result = []
        self._delete_take_over_by_user_identifier(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_take_over_by_user_id(
        self,
        request: DeleteTakeOverByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteTakeOverByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='deleteTakeOverByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteTakeOverByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_take_over_by_user_id(
        self,
        request: DeleteTakeOverByUserIdRequest,
    ) -> DeleteTakeOverByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_take_over_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_take_over_by_user_id_async(
        self,
        request: DeleteTakeOverByUserIdRequest,
    ) -> DeleteTakeOverByUserIdResult:
        async_result = []
        self._delete_take_over_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _do_take_over(
        self,
        request: DoTakeOverRequest,
        callback: Callable[[AsyncResult[DoTakeOverResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='doTakeOver',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DoTakeOverResult,
                callback=callback,
                body=body,
            )
        )

    def do_take_over(
        self,
        request: DoTakeOverRequest,
    ) -> DoTakeOverResult:
        async_result = []
        with timeout(30):
            self._do_take_over(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def do_take_over_async(
        self,
        request: DoTakeOverRequest,
    ) -> DoTakeOverResult:
        async_result = []
        self._do_take_over(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _do_take_over_open_id_connect(
        self,
        request: DoTakeOverOpenIdConnectRequest,
        callback: Callable[[AsyncResult[DoTakeOverOpenIdConnectResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='doTakeOverOpenIdConnect',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type
        if request.id_token is not None:
            body["idToken"] = request.id_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DoTakeOverOpenIdConnectResult,
                callback=callback,
                body=body,
            )
        )

    def do_take_over_open_id_connect(
        self,
        request: DoTakeOverOpenIdConnectRequest,
    ) -> DoTakeOverOpenIdConnectResult:
        async_result = []
        with timeout(30):
            self._do_take_over_open_id_connect(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def do_take_over_open_id_connect_async(
        self,
        request: DoTakeOverOpenIdConnectRequest,
    ) -> DoTakeOverOpenIdConnectResult:
        async_result = []
        self._do_take_over_open_id_connect(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_authorization_url(
        self,
        request: GetAuthorizationUrlRequest,
        callback: Callable[[AsyncResult[GetAuthorizationUrlResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOver',
            function='getAuthorizationUrl',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetAuthorizationUrlResult,
                callback=callback,
                body=body,
            )
        )

    def get_authorization_url(
        self,
        request: GetAuthorizationUrlRequest,
    ) -> GetAuthorizationUrlResult:
        async_result = []
        with timeout(30):
            self._get_authorization_url(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_authorization_url_async(
        self,
        request: GetAuthorizationUrlRequest,
    ) -> GetAuthorizationUrlResult:
        async_result = []
        self._get_authorization_url(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_platform_ids(
        self,
        request: DescribePlatformIdsRequest,
        callback: Callable[[AsyncResult[DescribePlatformIdsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='describePlatformIds',
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
                result_type=DescribePlatformIdsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_platform_ids(
        self,
        request: DescribePlatformIdsRequest,
    ) -> DescribePlatformIdsResult:
        async_result = []
        with timeout(30):
            self._describe_platform_ids(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_platform_ids_async(
        self,
        request: DescribePlatformIdsRequest,
    ) -> DescribePlatformIdsResult:
        async_result = []
        self._describe_platform_ids(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_platform_ids_by_user_id(
        self,
        request: DescribePlatformIdsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribePlatformIdsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='describePlatformIdsByUserId',
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
                result_type=DescribePlatformIdsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_platform_ids_by_user_id(
        self,
        request: DescribePlatformIdsByUserIdRequest,
    ) -> DescribePlatformIdsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_platform_ids_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_platform_ids_by_user_id_async(
        self,
        request: DescribePlatformIdsByUserIdRequest,
    ) -> DescribePlatformIdsByUserIdResult:
        async_result = []
        self._describe_platform_ids_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_platform_id(
        self,
        request: CreatePlatformIdRequest,
        callback: Callable[[AsyncResult[CreatePlatformIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='createPlatformId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreatePlatformIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_platform_id(
        self,
        request: CreatePlatformIdRequest,
    ) -> CreatePlatformIdResult:
        async_result = []
        with timeout(30):
            self._create_platform_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_platform_id_async(
        self,
        request: CreatePlatformIdRequest,
    ) -> CreatePlatformIdResult:
        async_result = []
        self._create_platform_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_platform_id_by_user_id(
        self,
        request: CreatePlatformIdByUserIdRequest,
        callback: Callable[[AsyncResult[CreatePlatformIdByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='createPlatformIdByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreatePlatformIdByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_platform_id_by_user_id(
        self,
        request: CreatePlatformIdByUserIdRequest,
    ) -> CreatePlatformIdByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_platform_id_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_platform_id_by_user_id_async(
        self,
        request: CreatePlatformIdByUserIdRequest,
    ) -> CreatePlatformIdByUserIdResult:
        async_result = []
        self._create_platform_id_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_platform_id(
        self,
        request: GetPlatformIdRequest,
        callback: Callable[[AsyncResult[GetPlatformIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='getPlatformId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPlatformIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_platform_id(
        self,
        request: GetPlatformIdRequest,
    ) -> GetPlatformIdResult:
        async_result = []
        with timeout(30):
            self._get_platform_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_platform_id_async(
        self,
        request: GetPlatformIdRequest,
    ) -> GetPlatformIdResult:
        async_result = []
        self._get_platform_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_platform_id_by_user_id(
        self,
        request: GetPlatformIdByUserIdRequest,
        callback: Callable[[AsyncResult[GetPlatformIdByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='getPlatformIdByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetPlatformIdByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_platform_id_by_user_id(
        self,
        request: GetPlatformIdByUserIdRequest,
    ) -> GetPlatformIdByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_platform_id_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_platform_id_by_user_id_async(
        self,
        request: GetPlatformIdByUserIdRequest,
    ) -> GetPlatformIdByUserIdResult:
        async_result = []
        self._get_platform_id_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _find_platform_id(
        self,
        request: FindPlatformIdRequest,
        callback: Callable[[AsyncResult[FindPlatformIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='findPlatformId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=FindPlatformIdResult,
                callback=callback,
                body=body,
            )
        )

    def find_platform_id(
        self,
        request: FindPlatformIdRequest,
    ) -> FindPlatformIdResult:
        async_result = []
        with timeout(30):
            self._find_platform_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def find_platform_id_async(
        self,
        request: FindPlatformIdRequest,
    ) -> FindPlatformIdResult:
        async_result = []
        self._find_platform_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _find_platform_id_by_user_id(
        self,
        request: FindPlatformIdByUserIdRequest,
        callback: Callable[[AsyncResult[FindPlatformIdByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='findPlatformIdByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=FindPlatformIdByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def find_platform_id_by_user_id(
        self,
        request: FindPlatformIdByUserIdRequest,
    ) -> FindPlatformIdByUserIdResult:
        async_result = []
        with timeout(30):
            self._find_platform_id_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def find_platform_id_by_user_id_async(
        self,
        request: FindPlatformIdByUserIdRequest,
    ) -> FindPlatformIdByUserIdResult:
        async_result = []
        self._find_platform_id_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_platform_id(
        self,
        request: DeletePlatformIdRequest,
        callback: Callable[[AsyncResult[DeletePlatformIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='deletePlatformId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeletePlatformIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_platform_id(
        self,
        request: DeletePlatformIdRequest,
    ) -> DeletePlatformIdResult:
        async_result = []
        with timeout(30):
            self._delete_platform_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_platform_id_async(
        self,
        request: DeletePlatformIdRequest,
    ) -> DeletePlatformIdResult:
        async_result = []
        self._delete_platform_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_platform_id_by_user_identifier(
        self,
        request: DeletePlatformIdByUserIdentifierRequest,
        callback: Callable[[AsyncResult[DeletePlatformIdByUserIdentifierResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='deletePlatformIdByUserIdentifier',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type
        if request.user_identifier is not None:
            body["userIdentifier"] = request.user_identifier

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeletePlatformIdByUserIdentifierResult,
                callback=callback,
                body=body,
            )
        )

    def delete_platform_id_by_user_identifier(
        self,
        request: DeletePlatformIdByUserIdentifierRequest,
    ) -> DeletePlatformIdByUserIdentifierResult:
        async_result = []
        with timeout(30):
            self._delete_platform_id_by_user_identifier(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_platform_id_by_user_identifier_async(
        self,
        request: DeletePlatformIdByUserIdentifierRequest,
    ) -> DeletePlatformIdByUserIdentifierResult:
        async_result = []
        self._delete_platform_id_by_user_identifier(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_platform_id_by_user_id(
        self,
        request: DeletePlatformIdByUserIdRequest,
        callback: Callable[[AsyncResult[DeletePlatformIdByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='platformId',
            function='deletePlatformIdByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.type is not None:
            body["type"] = request.type
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeletePlatformIdByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_platform_id_by_user_id(
        self,
        request: DeletePlatformIdByUserIdRequest,
    ) -> DeletePlatformIdByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_platform_id_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_platform_id_by_user_id_async(
        self,
        request: DeletePlatformIdByUserIdRequest,
    ) -> DeletePlatformIdByUserIdResult:
        async_result = []
        self._delete_platform_id_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_data_owner_by_user_id(
        self,
        request: GetDataOwnerByUserIdRequest,
        callback: Callable[[AsyncResult[GetDataOwnerByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='dataOwner',
            function='getDataOwnerByUserId',
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
                result_type=GetDataOwnerByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_data_owner_by_user_id(
        self,
        request: GetDataOwnerByUserIdRequest,
    ) -> GetDataOwnerByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_data_owner_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_data_owner_by_user_id_async(
        self,
        request: GetDataOwnerByUserIdRequest,
    ) -> GetDataOwnerByUserIdResult:
        async_result = []
        self._get_data_owner_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_data_owner_by_user_id(
        self,
        request: UpdateDataOwnerByUserIdRequest,
        callback: Callable[[AsyncResult[UpdateDataOwnerByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='dataOwner',
            function='updateDataOwnerByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.data_owner_name is not None:
            body["dataOwnerName"] = request.data_owner_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateDataOwnerByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def update_data_owner_by_user_id(
        self,
        request: UpdateDataOwnerByUserIdRequest,
    ) -> UpdateDataOwnerByUserIdResult:
        async_result = []
        with timeout(30):
            self._update_data_owner_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_data_owner_by_user_id_async(
        self,
        request: UpdateDataOwnerByUserIdRequest,
    ) -> UpdateDataOwnerByUserIdResult:
        async_result = []
        self._update_data_owner_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_data_owner_by_user_id(
        self,
        request: DeleteDataOwnerByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteDataOwnerByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='dataOwner',
            function='deleteDataOwnerByUserId',
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
                result_type=DeleteDataOwnerByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_data_owner_by_user_id(
        self,
        request: DeleteDataOwnerByUserIdRequest,
    ) -> DeleteDataOwnerByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_data_owner_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_data_owner_by_user_id_async(
        self,
        request: DeleteDataOwnerByUserIdRequest,
    ) -> DeleteDataOwnerByUserIdResult:
        async_result = []
        self._delete_data_owner_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_take_over_type_models(
        self,
        request: DescribeTakeOverTypeModelsRequest,
        callback: Callable[[AsyncResult[DescribeTakeOverTypeModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOverTypeModel',
            function='describeTakeOverTypeModels',
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
                result_type=DescribeTakeOverTypeModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_take_over_type_models(
        self,
        request: DescribeTakeOverTypeModelsRequest,
    ) -> DescribeTakeOverTypeModelsResult:
        async_result = []
        with timeout(30):
            self._describe_take_over_type_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_take_over_type_models_async(
        self,
        request: DescribeTakeOverTypeModelsRequest,
    ) -> DescribeTakeOverTypeModelsResult:
        async_result = []
        self._describe_take_over_type_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_take_over_type_model(
        self,
        request: GetTakeOverTypeModelRequest,
        callback: Callable[[AsyncResult[GetTakeOverTypeModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOverTypeModel',
            function='getTakeOverTypeModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetTakeOverTypeModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_take_over_type_model(
        self,
        request: GetTakeOverTypeModelRequest,
    ) -> GetTakeOverTypeModelResult:
        async_result = []
        with timeout(30):
            self._get_take_over_type_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_take_over_type_model_async(
        self,
        request: GetTakeOverTypeModelRequest,
    ) -> GetTakeOverTypeModelResult:
        async_result = []
        self._get_take_over_type_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_take_over_type_model_masters(
        self,
        request: DescribeTakeOverTypeModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeTakeOverTypeModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOverTypeModelMaster',
            function='describeTakeOverTypeModelMasters',
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
                result_type=DescribeTakeOverTypeModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_take_over_type_model_masters(
        self,
        request: DescribeTakeOverTypeModelMastersRequest,
    ) -> DescribeTakeOverTypeModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_take_over_type_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_take_over_type_model_masters_async(
        self,
        request: DescribeTakeOverTypeModelMastersRequest,
    ) -> DescribeTakeOverTypeModelMastersResult:
        async_result = []
        self._describe_take_over_type_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_take_over_type_model_master(
        self,
        request: CreateTakeOverTypeModelMasterRequest,
        callback: Callable[[AsyncResult[CreateTakeOverTypeModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOverTypeModelMaster',
            function='createTakeOverTypeModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.open_id_connect_setting is not None:
            body["openIdConnectSetting"] = request.open_id_connect_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateTakeOverTypeModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_take_over_type_model_master(
        self,
        request: CreateTakeOverTypeModelMasterRequest,
    ) -> CreateTakeOverTypeModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_take_over_type_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_take_over_type_model_master_async(
        self,
        request: CreateTakeOverTypeModelMasterRequest,
    ) -> CreateTakeOverTypeModelMasterResult:
        async_result = []
        self._create_take_over_type_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_take_over_type_model_master(
        self,
        request: GetTakeOverTypeModelMasterRequest,
        callback: Callable[[AsyncResult[GetTakeOverTypeModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOverTypeModelMaster',
            function='getTakeOverTypeModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetTakeOverTypeModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_take_over_type_model_master(
        self,
        request: GetTakeOverTypeModelMasterRequest,
    ) -> GetTakeOverTypeModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_take_over_type_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_take_over_type_model_master_async(
        self,
        request: GetTakeOverTypeModelMasterRequest,
    ) -> GetTakeOverTypeModelMasterResult:
        async_result = []
        self._get_take_over_type_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_take_over_type_model_master(
        self,
        request: UpdateTakeOverTypeModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateTakeOverTypeModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOverTypeModelMaster',
            function='updateTakeOverTypeModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.open_id_connect_setting is not None:
            body["openIdConnectSetting"] = request.open_id_connect_setting.to_dict()

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateTakeOverTypeModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_take_over_type_model_master(
        self,
        request: UpdateTakeOverTypeModelMasterRequest,
    ) -> UpdateTakeOverTypeModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_take_over_type_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_take_over_type_model_master_async(
        self,
        request: UpdateTakeOverTypeModelMasterRequest,
    ) -> UpdateTakeOverTypeModelMasterResult:
        async_result = []
        self._update_take_over_type_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_take_over_type_model_master(
        self,
        request: DeleteTakeOverTypeModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteTakeOverTypeModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='takeOverTypeModelMaster',
            function='deleteTakeOverTypeModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.type is not None:
            body["type"] = request.type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteTakeOverTypeModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_take_over_type_model_master(
        self,
        request: DeleteTakeOverTypeModelMasterRequest,
    ) -> DeleteTakeOverTypeModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_take_over_type_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_take_over_type_model_master_async(
        self,
        request: DeleteTakeOverTypeModelMasterRequest,
    ) -> DeleteTakeOverTypeModelMasterResult:
        async_result = []
        self._delete_take_over_type_model_master(
            request,
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
            service="account",
            component='currentModelMaster',
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

    def _get_current_model_master(
        self,
        request: GetCurrentModelMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='currentModelMaster',
            function='getCurrentModelMaster',
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
                result_type=GetCurrentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_model_master(
        self,
        request: GetCurrentModelMasterRequest,
    ) -> GetCurrentModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_model_master_async(
        self,
        request: GetCurrentModelMasterRequest,
    ) -> GetCurrentModelMasterResult:
        async_result = []
        self._get_current_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _pre_update_current_model_master(
        self,
        request: PreUpdateCurrentModelMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='currentModelMaster',
            function='preUpdateCurrentModelMaster',
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
                result_type=PreUpdateCurrentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_model_master(
        self,
        request: PreUpdateCurrentModelMasterRequest,
    ) -> PreUpdateCurrentModelMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_model_master_async(
        self,
        request: PreUpdateCurrentModelMasterRequest,
    ) -> PreUpdateCurrentModelMasterResult:
        async_result = []
        self._pre_update_current_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_model_master(
        self,
        request: UpdateCurrentModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='currentModelMaster',
            function='updateCurrentModelMaster',
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
                result_type=UpdateCurrentModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_model_master(
        self,
        request: UpdateCurrentModelMasterRequest,
    ) -> UpdateCurrentModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_model_master_async(
        self,
        request: UpdateCurrentModelMasterRequest,
    ) -> UpdateCurrentModelMasterResult:
        async_result = []
        self._update_current_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_model_master_from_git_hub(
        self,
        request: UpdateCurrentModelMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentModelMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="account",
            component='currentModelMaster',
            function='updateCurrentModelMasterFromGitHub',
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
                result_type=UpdateCurrentModelMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_model_master_from_git_hub(
        self,
        request: UpdateCurrentModelMasterFromGitHubRequest,
    ) -> UpdateCurrentModelMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_model_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_model_master_from_git_hub_async(
        self,
        request: UpdateCurrentModelMasterFromGitHubRequest,
    ) -> UpdateCurrentModelMasterFromGitHubResult:
        async_result = []
        self._update_current_model_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result