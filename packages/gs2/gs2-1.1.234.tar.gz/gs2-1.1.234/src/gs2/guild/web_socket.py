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


class Gs2GuildWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
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
            service="guild",
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
        if request.change_notification is not None:
            body["changeNotification"] = request.change_notification.to_dict()
        if request.join_notification is not None:
            body["joinNotification"] = request.join_notification.to_dict()
        if request.leave_notification is not None:
            body["leaveNotification"] = request.leave_notification.to_dict()
        if request.change_member_notification is not None:
            body["changeMemberNotification"] = request.change_member_notification.to_dict()
        if request.receive_request_notification is not None:
            body["receiveRequestNotification"] = request.receive_request_notification.to_dict()
        if request.remove_request_notification is not None:
            body["removeRequestNotification"] = request.remove_request_notification.to_dict()
        if request.create_guild_script is not None:
            body["createGuildScript"] = request.create_guild_script.to_dict()
        if request.update_guild_script is not None:
            body["updateGuildScript"] = request.update_guild_script.to_dict()
        if request.join_guild_script is not None:
            body["joinGuildScript"] = request.join_guild_script.to_dict()
        if request.receive_join_request_script is not None:
            body["receiveJoinRequestScript"] = request.receive_join_request_script.to_dict()
        if request.leave_guild_script is not None:
            body["leaveGuildScript"] = request.leave_guild_script.to_dict()
        if request.change_role_script is not None:
            body["changeRoleScript"] = request.change_role_script.to_dict()
        if request.delete_guild_script is not None:
            body["deleteGuildScript"] = request.delete_guild_script.to_dict()
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
            service="guild",
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
            service="guild",
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
            service="guild",
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
        if request.change_notification is not None:
            body["changeNotification"] = request.change_notification.to_dict()
        if request.join_notification is not None:
            body["joinNotification"] = request.join_notification.to_dict()
        if request.leave_notification is not None:
            body["leaveNotification"] = request.leave_notification.to_dict()
        if request.change_member_notification is not None:
            body["changeMemberNotification"] = request.change_member_notification.to_dict()
        if request.receive_request_notification is not None:
            body["receiveRequestNotification"] = request.receive_request_notification.to_dict()
        if request.remove_request_notification is not None:
            body["removeRequestNotification"] = request.remove_request_notification.to_dict()
        if request.create_guild_script is not None:
            body["createGuildScript"] = request.create_guild_script.to_dict()
        if request.update_guild_script is not None:
            body["updateGuildScript"] = request.update_guild_script.to_dict()
        if request.join_guild_script is not None:
            body["joinGuildScript"] = request.join_guild_script.to_dict()
        if request.receive_join_request_script is not None:
            body["receiveJoinRequestScript"] = request.receive_join_request_script.to_dict()
        if request.leave_guild_script is not None:
            body["leaveGuildScript"] = request.leave_guild_script.to_dict()
        if request.change_role_script is not None:
            body["changeRoleScript"] = request.change_role_script.to_dict()
        if request.delete_guild_script is not None:
            body["deleteGuildScript"] = request.delete_guild_script.to_dict()
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
            service="guild",
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
            service="guild",
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
            service="guild",
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
            service="guild",
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
            service="guild",
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
            service="guild",
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
            service="guild",
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
            service="guild",
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
            service="guild",
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

    def _describe_guild_model_masters(
        self,
        request: DescribeGuildModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeGuildModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guildModelMaster',
            function='describeGuildModelMasters',
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
                result_type=DescribeGuildModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_guild_model_masters(
        self,
        request: DescribeGuildModelMastersRequest,
    ) -> DescribeGuildModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_guild_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_guild_model_masters_async(
        self,
        request: DescribeGuildModelMastersRequest,
    ) -> DescribeGuildModelMastersResult:
        async_result = []
        self._describe_guild_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_guild_model_master(
        self,
        request: CreateGuildModelMasterRequest,
        callback: Callable[[AsyncResult[CreateGuildModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guildModelMaster',
            function='createGuildModelMaster',
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
        if request.default_maximum_member_count is not None:
            body["defaultMaximumMemberCount"] = request.default_maximum_member_count
        if request.maximum_member_count is not None:
            body["maximumMemberCount"] = request.maximum_member_count
        if request.inactivity_period_days is not None:
            body["inactivityPeriodDays"] = request.inactivity_period_days
        if request.roles is not None:
            body["roles"] = [
                item.to_dict()
                for item in request.roles
            ]
        if request.guild_master_role is not None:
            body["guildMasterRole"] = request.guild_master_role
        if request.guild_member_default_role is not None:
            body["guildMemberDefaultRole"] = request.guild_member_default_role
        if request.rejoin_cool_time_minutes is not None:
            body["rejoinCoolTimeMinutes"] = request.rejoin_cool_time_minutes
        if request.max_concurrent_join_guilds is not None:
            body["maxConcurrentJoinGuilds"] = request.max_concurrent_join_guilds
        if request.max_concurrent_guild_master_count is not None:
            body["maxConcurrentGuildMasterCount"] = request.max_concurrent_guild_master_count

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateGuildModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_guild_model_master(
        self,
        request: CreateGuildModelMasterRequest,
    ) -> CreateGuildModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_guild_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_guild_model_master_async(
        self,
        request: CreateGuildModelMasterRequest,
    ) -> CreateGuildModelMasterResult:
        async_result = []
        self._create_guild_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_guild_model_master(
        self,
        request: GetGuildModelMasterRequest,
        callback: Callable[[AsyncResult[GetGuildModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guildModelMaster',
            function='getGuildModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGuildModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_guild_model_master(
        self,
        request: GetGuildModelMasterRequest,
    ) -> GetGuildModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_guild_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_guild_model_master_async(
        self,
        request: GetGuildModelMasterRequest,
    ) -> GetGuildModelMasterResult:
        async_result = []
        self._get_guild_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_guild_model_master(
        self,
        request: UpdateGuildModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateGuildModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guildModelMaster',
            function='updateGuildModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.default_maximum_member_count is not None:
            body["defaultMaximumMemberCount"] = request.default_maximum_member_count
        if request.maximum_member_count is not None:
            body["maximumMemberCount"] = request.maximum_member_count
        if request.inactivity_period_days is not None:
            body["inactivityPeriodDays"] = request.inactivity_period_days
        if request.roles is not None:
            body["roles"] = [
                item.to_dict()
                for item in request.roles
            ]
        if request.guild_master_role is not None:
            body["guildMasterRole"] = request.guild_master_role
        if request.guild_member_default_role is not None:
            body["guildMemberDefaultRole"] = request.guild_member_default_role
        if request.rejoin_cool_time_minutes is not None:
            body["rejoinCoolTimeMinutes"] = request.rejoin_cool_time_minutes
        if request.max_concurrent_join_guilds is not None:
            body["maxConcurrentJoinGuilds"] = request.max_concurrent_join_guilds
        if request.max_concurrent_guild_master_count is not None:
            body["maxConcurrentGuildMasterCount"] = request.max_concurrent_guild_master_count

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateGuildModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_guild_model_master(
        self,
        request: UpdateGuildModelMasterRequest,
    ) -> UpdateGuildModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_guild_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_guild_model_master_async(
        self,
        request: UpdateGuildModelMasterRequest,
    ) -> UpdateGuildModelMasterResult:
        async_result = []
        self._update_guild_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_guild_model_master(
        self,
        request: DeleteGuildModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteGuildModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guildModelMaster',
            function='deleteGuildModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteGuildModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_guild_model_master(
        self,
        request: DeleteGuildModelMasterRequest,
    ) -> DeleteGuildModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_guild_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_guild_model_master_async(
        self,
        request: DeleteGuildModelMasterRequest,
    ) -> DeleteGuildModelMasterResult:
        async_result = []
        self._delete_guild_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_guild_models(
        self,
        request: DescribeGuildModelsRequest,
        callback: Callable[[AsyncResult[DescribeGuildModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guildModel',
            function='describeGuildModels',
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
                result_type=DescribeGuildModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_guild_models(
        self,
        request: DescribeGuildModelsRequest,
    ) -> DescribeGuildModelsResult:
        async_result = []
        with timeout(30):
            self._describe_guild_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_guild_models_async(
        self,
        request: DescribeGuildModelsRequest,
    ) -> DescribeGuildModelsResult:
        async_result = []
        self._describe_guild_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_guild_model(
        self,
        request: GetGuildModelRequest,
        callback: Callable[[AsyncResult[GetGuildModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guildModel',
            function='getGuildModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGuildModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_guild_model(
        self,
        request: GetGuildModelRequest,
    ) -> GetGuildModelResult:
        async_result = []
        with timeout(30):
            self._get_guild_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_guild_model_async(
        self,
        request: GetGuildModelRequest,
    ) -> GetGuildModelResult:
        async_result = []
        self._get_guild_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _search_guilds(
        self,
        request: SearchGuildsRequest,
        callback: Callable[[AsyncResult[SearchGuildsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='searchGuilds',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.display_name is not None:
            body["displayName"] = request.display_name
        if request.attributes1 is not None:
            body["attributes1"] = [
                item
                for item in request.attributes1
            ]
        if request.attributes2 is not None:
            body["attributes2"] = [
                item
                for item in request.attributes2
            ]
        if request.attributes3 is not None:
            body["attributes3"] = [
                item
                for item in request.attributes3
            ]
        if request.attributes4 is not None:
            body["attributes4"] = [
                item
                for item in request.attributes4
            ]
        if request.attributes5 is not None:
            body["attributes5"] = [
                item
                for item in request.attributes5
            ]
        if request.join_policies is not None:
            body["joinPolicies"] = [
                item
                for item in request.join_policies
            ]
        if request.include_full_members_guild is not None:
            body["includeFullMembersGuild"] = request.include_full_members_guild
        if request.order_by is not None:
            body["orderBy"] = request.order_by
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SearchGuildsResult,
                callback=callback,
                body=body,
            )
        )

    def search_guilds(
        self,
        request: SearchGuildsRequest,
    ) -> SearchGuildsResult:
        async_result = []
        with timeout(30):
            self._search_guilds(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def search_guilds_async(
        self,
        request: SearchGuildsRequest,
    ) -> SearchGuildsResult:
        async_result = []
        self._search_guilds(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _search_guilds_by_user_id(
        self,
        request: SearchGuildsByUserIdRequest,
        callback: Callable[[AsyncResult[SearchGuildsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='searchGuildsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.display_name is not None:
            body["displayName"] = request.display_name
        if request.attributes1 is not None:
            body["attributes1"] = [
                item
                for item in request.attributes1
            ]
        if request.attributes2 is not None:
            body["attributes2"] = [
                item
                for item in request.attributes2
            ]
        if request.attributes3 is not None:
            body["attributes3"] = [
                item
                for item in request.attributes3
            ]
        if request.attributes4 is not None:
            body["attributes4"] = [
                item
                for item in request.attributes4
            ]
        if request.attributes5 is not None:
            body["attributes5"] = [
                item
                for item in request.attributes5
            ]
        if request.join_policies is not None:
            body["joinPolicies"] = [
                item
                for item in request.join_policies
            ]
        if request.include_full_members_guild is not None:
            body["includeFullMembersGuild"] = request.include_full_members_guild
        if request.order_by is not None:
            body["orderBy"] = request.order_by
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SearchGuildsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def search_guilds_by_user_id(
        self,
        request: SearchGuildsByUserIdRequest,
    ) -> SearchGuildsByUserIdResult:
        async_result = []
        with timeout(30):
            self._search_guilds_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def search_guilds_by_user_id_async(
        self,
        request: SearchGuildsByUserIdRequest,
    ) -> SearchGuildsByUserIdResult:
        async_result = []
        self._search_guilds_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_guild(
        self,
        request: CreateGuildRequest,
        callback: Callable[[AsyncResult[CreateGuildResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='createGuild',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.display_name is not None:
            body["displayName"] = request.display_name
        if request.attribute1 is not None:
            body["attribute1"] = request.attribute1
        if request.attribute2 is not None:
            body["attribute2"] = request.attribute2
        if request.attribute3 is not None:
            body["attribute3"] = request.attribute3
        if request.attribute4 is not None:
            body["attribute4"] = request.attribute4
        if request.attribute5 is not None:
            body["attribute5"] = request.attribute5
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.member_metadata is not None:
            body["memberMetadata"] = request.member_metadata
        if request.join_policy is not None:
            body["joinPolicy"] = request.join_policy
        if request.custom_roles is not None:
            body["customRoles"] = [
                item.to_dict()
                for item in request.custom_roles
            ]
        if request.guild_member_default_role is not None:
            body["guildMemberDefaultRole"] = request.guild_member_default_role

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateGuildResult,
                callback=callback,
                body=body,
            )
        )

    def create_guild(
        self,
        request: CreateGuildRequest,
    ) -> CreateGuildResult:
        async_result = []
        with timeout(30):
            self._create_guild(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_guild_async(
        self,
        request: CreateGuildRequest,
    ) -> CreateGuildResult:
        async_result = []
        self._create_guild(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_guild_by_user_id(
        self,
        request: CreateGuildByUserIdRequest,
        callback: Callable[[AsyncResult[CreateGuildByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='createGuildByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.display_name is not None:
            body["displayName"] = request.display_name
        if request.attribute1 is not None:
            body["attribute1"] = request.attribute1
        if request.attribute2 is not None:
            body["attribute2"] = request.attribute2
        if request.attribute3 is not None:
            body["attribute3"] = request.attribute3
        if request.attribute4 is not None:
            body["attribute4"] = request.attribute4
        if request.attribute5 is not None:
            body["attribute5"] = request.attribute5
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.member_metadata is not None:
            body["memberMetadata"] = request.member_metadata
        if request.join_policy is not None:
            body["joinPolicy"] = request.join_policy
        if request.custom_roles is not None:
            body["customRoles"] = [
                item.to_dict()
                for item in request.custom_roles
            ]
        if request.guild_member_default_role is not None:
            body["guildMemberDefaultRole"] = request.guild_member_default_role
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateGuildByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def create_guild_by_user_id(
        self,
        request: CreateGuildByUserIdRequest,
    ) -> CreateGuildByUserIdResult:
        async_result = []
        with timeout(30):
            self._create_guild_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_guild_by_user_id_async(
        self,
        request: CreateGuildByUserIdRequest,
    ) -> CreateGuildByUserIdResult:
        async_result = []
        self._create_guild_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_guild(
        self,
        request: GetGuildRequest,
        callback: Callable[[AsyncResult[GetGuildResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='getGuild',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGuildResult,
                callback=callback,
                body=body,
            )
        )

    def get_guild(
        self,
        request: GetGuildRequest,
    ) -> GetGuildResult:
        async_result = []
        with timeout(30):
            self._get_guild(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_guild_async(
        self,
        request: GetGuildRequest,
    ) -> GetGuildResult:
        async_result = []
        self._get_guild(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_guild_by_user_id(
        self,
        request: GetGuildByUserIdRequest,
        callback: Callable[[AsyncResult[GetGuildByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='getGuildByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetGuildByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_guild_by_user_id(
        self,
        request: GetGuildByUserIdRequest,
    ) -> GetGuildByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_guild_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_guild_by_user_id_async(
        self,
        request: GetGuildByUserIdRequest,
    ) -> GetGuildByUserIdResult:
        async_result = []
        self._get_guild_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_guild(
        self,
        request: UpdateGuildRequest,
        callback: Callable[[AsyncResult[UpdateGuildResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='updateGuild',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.display_name is not None:
            body["displayName"] = request.display_name
        if request.attribute1 is not None:
            body["attribute1"] = request.attribute1
        if request.attribute2 is not None:
            body["attribute2"] = request.attribute2
        if request.attribute3 is not None:
            body["attribute3"] = request.attribute3
        if request.attribute4 is not None:
            body["attribute4"] = request.attribute4
        if request.attribute5 is not None:
            body["attribute5"] = request.attribute5
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.join_policy is not None:
            body["joinPolicy"] = request.join_policy
        if request.custom_roles is not None:
            body["customRoles"] = [
                item.to_dict()
                for item in request.custom_roles
            ]
        if request.guild_member_default_role is not None:
            body["guildMemberDefaultRole"] = request.guild_member_default_role

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateGuildResult,
                callback=callback,
                body=body,
            )
        )

    def update_guild(
        self,
        request: UpdateGuildRequest,
    ) -> UpdateGuildResult:
        async_result = []
        with timeout(30):
            self._update_guild(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_guild_async(
        self,
        request: UpdateGuildRequest,
    ) -> UpdateGuildResult:
        async_result = []
        self._update_guild(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_guild_by_guild_name(
        self,
        request: UpdateGuildByGuildNameRequest,
        callback: Callable[[AsyncResult[UpdateGuildByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='updateGuildByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.display_name is not None:
            body["displayName"] = request.display_name
        if request.attribute1 is not None:
            body["attribute1"] = request.attribute1
        if request.attribute2 is not None:
            body["attribute2"] = request.attribute2
        if request.attribute3 is not None:
            body["attribute3"] = request.attribute3
        if request.attribute4 is not None:
            body["attribute4"] = request.attribute4
        if request.attribute5 is not None:
            body["attribute5"] = request.attribute5
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.join_policy is not None:
            body["joinPolicy"] = request.join_policy
        if request.custom_roles is not None:
            body["customRoles"] = [
                item.to_dict()
                for item in request.custom_roles
            ]
        if request.guild_member_default_role is not None:
            body["guildMemberDefaultRole"] = request.guild_member_default_role

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateGuildByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def update_guild_by_guild_name(
        self,
        request: UpdateGuildByGuildNameRequest,
    ) -> UpdateGuildByGuildNameResult:
        async_result = []
        with timeout(30):
            self._update_guild_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_guild_by_guild_name_async(
        self,
        request: UpdateGuildByGuildNameRequest,
    ) -> UpdateGuildByGuildNameResult:
        async_result = []
        self._update_guild_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_member(
        self,
        request: DeleteMemberRequest,
        callback: Callable[[AsyncResult[DeleteMemberResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='deleteMember',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DeleteMemberResult,
                callback=callback,
                body=body,
            )
        )

    def delete_member(
        self,
        request: DeleteMemberRequest,
    ) -> DeleteMemberResult:
        async_result = []
        with timeout(30):
            self._delete_member(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_member_async(
        self,
        request: DeleteMemberRequest,
    ) -> DeleteMemberResult:
        async_result = []
        self._delete_member(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_member_by_guild_name(
        self,
        request: DeleteMemberByGuildNameRequest,
        callback: Callable[[AsyncResult[DeleteMemberByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='deleteMemberByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteMemberByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def delete_member_by_guild_name(
        self,
        request: DeleteMemberByGuildNameRequest,
    ) -> DeleteMemberByGuildNameResult:
        async_result = []
        with timeout(30):
            self._delete_member_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_member_by_guild_name_async(
        self,
        request: DeleteMemberByGuildNameRequest,
    ) -> DeleteMemberByGuildNameResult:
        async_result = []
        self._delete_member_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_member_role(
        self,
        request: UpdateMemberRoleRequest,
        callback: Callable[[AsyncResult[UpdateMemberRoleResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='updateMemberRole',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id
        if request.role_name is not None:
            body["roleName"] = request.role_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateMemberRoleResult,
                callback=callback,
                body=body,
            )
        )

    def update_member_role(
        self,
        request: UpdateMemberRoleRequest,
    ) -> UpdateMemberRoleResult:
        async_result = []
        with timeout(30):
            self._update_member_role(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_member_role_async(
        self,
        request: UpdateMemberRoleRequest,
    ) -> UpdateMemberRoleResult:
        async_result = []
        self._update_member_role(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_member_role_by_guild_name(
        self,
        request: UpdateMemberRoleByGuildNameRequest,
        callback: Callable[[AsyncResult[UpdateMemberRoleByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='updateMemberRoleByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.target_user_id is not None:
            body["targetUserId"] = request.target_user_id
        if request.role_name is not None:
            body["roleName"] = request.role_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateMemberRoleByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def update_member_role_by_guild_name(
        self,
        request: UpdateMemberRoleByGuildNameRequest,
    ) -> UpdateMemberRoleByGuildNameResult:
        async_result = []
        with timeout(30):
            self._update_member_role_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_member_role_by_guild_name_async(
        self,
        request: UpdateMemberRoleByGuildNameRequest,
    ) -> UpdateMemberRoleByGuildNameResult:
        async_result = []
        self._update_member_role_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _batch_update_member_role(
        self,
        request: BatchUpdateMemberRoleRequest,
        callback: Callable[[AsyncResult[BatchUpdateMemberRoleResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='batchUpdateMemberRole',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.members is not None:
            body["members"] = [
                item.to_dict()
                for item in request.members
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
                result_type=BatchUpdateMemberRoleResult,
                callback=callback,
                body=body,
            )
        )

    def batch_update_member_role(
        self,
        request: BatchUpdateMemberRoleRequest,
    ) -> BatchUpdateMemberRoleResult:
        async_result = []
        with timeout(30):
            self._batch_update_member_role(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def batch_update_member_role_async(
        self,
        request: BatchUpdateMemberRoleRequest,
    ) -> BatchUpdateMemberRoleResult:
        async_result = []
        self._batch_update_member_role(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _batch_update_member_role_by_guild_name(
        self,
        request: BatchUpdateMemberRoleByGuildNameRequest,
        callback: Callable[[AsyncResult[BatchUpdateMemberRoleByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='batchUpdateMemberRoleByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.members is not None:
            body["members"] = [
                item.to_dict()
                for item in request.members
            ]

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=BatchUpdateMemberRoleByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def batch_update_member_role_by_guild_name(
        self,
        request: BatchUpdateMemberRoleByGuildNameRequest,
    ) -> BatchUpdateMemberRoleByGuildNameResult:
        async_result = []
        with timeout(30):
            self._batch_update_member_role_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def batch_update_member_role_by_guild_name_async(
        self,
        request: BatchUpdateMemberRoleByGuildNameRequest,
    ) -> BatchUpdateMemberRoleByGuildNameResult:
        async_result = []
        self._batch_update_member_role_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_guild(
        self,
        request: DeleteGuildRequest,
        callback: Callable[[AsyncResult[DeleteGuildResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='deleteGuild',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DeleteGuildResult,
                callback=callback,
                body=body,
            )
        )

    def delete_guild(
        self,
        request: DeleteGuildRequest,
    ) -> DeleteGuildResult:
        async_result = []
        with timeout(30):
            self._delete_guild(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_guild_async(
        self,
        request: DeleteGuildRequest,
    ) -> DeleteGuildResult:
        async_result = []
        self._delete_guild(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_guild_by_guild_name(
        self,
        request: DeleteGuildByGuildNameRequest,
        callback: Callable[[AsyncResult[DeleteGuildByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='deleteGuildByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteGuildByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def delete_guild_by_guild_name(
        self,
        request: DeleteGuildByGuildNameRequest,
    ) -> DeleteGuildByGuildNameResult:
        async_result = []
        with timeout(30):
            self._delete_guild_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_guild_by_guild_name_async(
        self,
        request: DeleteGuildByGuildNameRequest,
    ) -> DeleteGuildByGuildNameResult:
        async_result = []
        self._delete_guild_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _increase_maximum_current_maximum_member_count_by_guild_name(
        self,
        request: IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest,
        callback: Callable[[AsyncResult[IncreaseMaximumCurrentMaximumMemberCountByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='increaseMaximumCurrentMaximumMemberCountByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.value is not None:
            body["value"] = request.value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=IncreaseMaximumCurrentMaximumMemberCountByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def increase_maximum_current_maximum_member_count_by_guild_name(
        self,
        request: IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest,
    ) -> IncreaseMaximumCurrentMaximumMemberCountByGuildNameResult:
        async_result = []
        with timeout(30):
            self._increase_maximum_current_maximum_member_count_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def increase_maximum_current_maximum_member_count_by_guild_name_async(
        self,
        request: IncreaseMaximumCurrentMaximumMemberCountByGuildNameRequest,
    ) -> IncreaseMaximumCurrentMaximumMemberCountByGuildNameResult:
        async_result = []
        self._increase_maximum_current_maximum_member_count_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _decrease_maximum_current_maximum_member_count(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountRequest,
        callback: Callable[[AsyncResult[DecreaseMaximumCurrentMaximumMemberCountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='decreaseMaximumCurrentMaximumMemberCount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DecreaseMaximumCurrentMaximumMemberCountResult,
                callback=callback,
                body=body,
            )
        )

    def decrease_maximum_current_maximum_member_count(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountRequest,
    ) -> DecreaseMaximumCurrentMaximumMemberCountResult:
        async_result = []
        with timeout(30):
            self._decrease_maximum_current_maximum_member_count(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_maximum_current_maximum_member_count_async(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountRequest,
    ) -> DecreaseMaximumCurrentMaximumMemberCountResult:
        async_result = []
        self._decrease_maximum_current_maximum_member_count(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _decrease_maximum_current_maximum_member_count_by_guild_name(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest,
        callback: Callable[[AsyncResult[DecreaseMaximumCurrentMaximumMemberCountByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='decreaseMaximumCurrentMaximumMemberCountByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.value is not None:
            body["value"] = request.value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DecreaseMaximumCurrentMaximumMemberCountByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def decrease_maximum_current_maximum_member_count_by_guild_name(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest,
    ) -> DecreaseMaximumCurrentMaximumMemberCountByGuildNameResult:
        async_result = []
        with timeout(30):
            self._decrease_maximum_current_maximum_member_count_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_maximum_current_maximum_member_count_by_guild_name_async(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountByGuildNameRequest,
    ) -> DecreaseMaximumCurrentMaximumMemberCountByGuildNameResult:
        async_result = []
        self._decrease_maximum_current_maximum_member_count_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_current_maximum_member_count(
        self,
        request: VerifyCurrentMaximumMemberCountRequest,
        callback: Callable[[AsyncResult[VerifyCurrentMaximumMemberCountResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='verifyCurrentMaximumMemberCount',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
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
                result_type=VerifyCurrentMaximumMemberCountResult,
                callback=callback,
                body=body,
            )
        )

    def verify_current_maximum_member_count(
        self,
        request: VerifyCurrentMaximumMemberCountRequest,
    ) -> VerifyCurrentMaximumMemberCountResult:
        async_result = []
        with timeout(30):
            self._verify_current_maximum_member_count(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_current_maximum_member_count_async(
        self,
        request: VerifyCurrentMaximumMemberCountRequest,
    ) -> VerifyCurrentMaximumMemberCountResult:
        async_result = []
        self._verify_current_maximum_member_count(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_current_maximum_member_count_by_guild_name(
        self,
        request: VerifyCurrentMaximumMemberCountByGuildNameRequest,
        callback: Callable[[AsyncResult[VerifyCurrentMaximumMemberCountByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='verifyCurrentMaximumMemberCountByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.value is not None:
            body["value"] = request.value
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyCurrentMaximumMemberCountByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def verify_current_maximum_member_count_by_guild_name(
        self,
        request: VerifyCurrentMaximumMemberCountByGuildNameRequest,
    ) -> VerifyCurrentMaximumMemberCountByGuildNameResult:
        async_result = []
        with timeout(30):
            self._verify_current_maximum_member_count_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_current_maximum_member_count_by_guild_name_async(
        self,
        request: VerifyCurrentMaximumMemberCountByGuildNameRequest,
    ) -> VerifyCurrentMaximumMemberCountByGuildNameResult:
        async_result = []
        self._verify_current_maximum_member_count_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_include_member(
        self,
        request: VerifyIncludeMemberRequest,
        callback: Callable[[AsyncResult[VerifyIncludeMemberResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='verifyIncludeMember',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyIncludeMemberResult,
                callback=callback,
                body=body,
            )
        )

    def verify_include_member(
        self,
        request: VerifyIncludeMemberRequest,
    ) -> VerifyIncludeMemberResult:
        async_result = []
        with timeout(30):
            self._verify_include_member(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_include_member_async(
        self,
        request: VerifyIncludeMemberRequest,
    ) -> VerifyIncludeMemberResult:
        async_result = []
        self._verify_include_member(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_include_member_by_user_id(
        self,
        request: VerifyIncludeMemberByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyIncludeMemberByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='verifyIncludeMemberByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.verify_type is not None:
            body["verifyType"] = request.verify_type
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=VerifyIncludeMemberByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def verify_include_member_by_user_id(
        self,
        request: VerifyIncludeMemberByUserIdRequest,
    ) -> VerifyIncludeMemberByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_include_member_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_include_member_by_user_id_async(
        self,
        request: VerifyIncludeMemberByUserIdRequest,
    ) -> VerifyIncludeMemberByUserIdResult:
        async_result = []
        self._verify_include_member_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_maximum_current_maximum_member_count_by_guild_name(
        self,
        request: SetMaximumCurrentMaximumMemberCountByGuildNameRequest,
        callback: Callable[[AsyncResult[SetMaximumCurrentMaximumMemberCountByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='setMaximumCurrentMaximumMemberCountByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.value is not None:
            body["value"] = request.value

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=SetMaximumCurrentMaximumMemberCountByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def set_maximum_current_maximum_member_count_by_guild_name(
        self,
        request: SetMaximumCurrentMaximumMemberCountByGuildNameRequest,
    ) -> SetMaximumCurrentMaximumMemberCountByGuildNameResult:
        async_result = []
        with timeout(30):
            self._set_maximum_current_maximum_member_count_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_maximum_current_maximum_member_count_by_guild_name_async(
        self,
        request: SetMaximumCurrentMaximumMemberCountByGuildNameRequest,
    ) -> SetMaximumCurrentMaximumMemberCountByGuildNameResult:
        async_result = []
        self._set_maximum_current_maximum_member_count_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _assume(
        self,
        request: AssumeRequest,
        callback: Callable[[AsyncResult[AssumeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='assume',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AssumeResult,
                callback=callback,
                body=body,
            )
        )

    def assume(
        self,
        request: AssumeRequest,
    ) -> AssumeResult:
        async_result = []
        with timeout(30):
            self._assume(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def assume_async(
        self,
        request: AssumeRequest,
    ) -> AssumeResult:
        async_result = []
        self._assume(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _assume_by_user_id(
        self,
        request: AssumeByUserIdRequest,
        callback: Callable[[AsyncResult[AssumeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='assumeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AssumeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def assume_by_user_id(
        self,
        request: AssumeByUserIdRequest,
    ) -> AssumeByUserIdResult:
        async_result = []
        with timeout(30):
            self._assume_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def assume_by_user_id_async(
        self,
        request: AssumeByUserIdRequest,
    ) -> AssumeByUserIdResult:
        async_result = []
        self._assume_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _increase_maximum_current_maximum_member_count_by_stamp_sheet(
        self,
        request: IncreaseMaximumCurrentMaximumMemberCountByStampSheetRequest,
        callback: Callable[[AsyncResult[IncreaseMaximumCurrentMaximumMemberCountByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='increaseMaximumCurrentMaximumMemberCountByStampSheet',
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
                result_type=IncreaseMaximumCurrentMaximumMemberCountByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def increase_maximum_current_maximum_member_count_by_stamp_sheet(
        self,
        request: IncreaseMaximumCurrentMaximumMemberCountByStampSheetRequest,
    ) -> IncreaseMaximumCurrentMaximumMemberCountByStampSheetResult:
        async_result = []
        with timeout(30):
            self._increase_maximum_current_maximum_member_count_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def increase_maximum_current_maximum_member_count_by_stamp_sheet_async(
        self,
        request: IncreaseMaximumCurrentMaximumMemberCountByStampSheetRequest,
    ) -> IncreaseMaximumCurrentMaximumMemberCountByStampSheetResult:
        async_result = []
        self._increase_maximum_current_maximum_member_count_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _decrease_maximum_current_maximum_member_count_by_stamp_task(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountByStampTaskRequest,
        callback: Callable[[AsyncResult[DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='decreaseMaximumCurrentMaximumMemberCountByStampTask',
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
                result_type=DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def decrease_maximum_current_maximum_member_count_by_stamp_task(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountByStampTaskRequest,
    ) -> DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult:
        async_result = []
        with timeout(30):
            self._decrease_maximum_current_maximum_member_count_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_maximum_current_maximum_member_count_by_stamp_task_async(
        self,
        request: DecreaseMaximumCurrentMaximumMemberCountByStampTaskRequest,
    ) -> DecreaseMaximumCurrentMaximumMemberCountByStampTaskResult:
        async_result = []
        self._decrease_maximum_current_maximum_member_count_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _set_maximum_current_maximum_member_count_by_stamp_sheet(
        self,
        request: SetMaximumCurrentMaximumMemberCountByStampSheetRequest,
        callback: Callable[[AsyncResult[SetMaximumCurrentMaximumMemberCountByStampSheetResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='setMaximumCurrentMaximumMemberCountByStampSheet',
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
                result_type=SetMaximumCurrentMaximumMemberCountByStampSheetResult,
                callback=callback,
                body=body,
            )
        )

    def set_maximum_current_maximum_member_count_by_stamp_sheet(
        self,
        request: SetMaximumCurrentMaximumMemberCountByStampSheetRequest,
    ) -> SetMaximumCurrentMaximumMemberCountByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_maximum_current_maximum_member_count_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_maximum_current_maximum_member_count_by_stamp_sheet_async(
        self,
        request: SetMaximumCurrentMaximumMemberCountByStampSheetRequest,
    ) -> SetMaximumCurrentMaximumMemberCountByStampSheetResult:
        async_result = []
        self._set_maximum_current_maximum_member_count_by_stamp_sheet(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_current_maximum_member_count_by_stamp_task(
        self,
        request: VerifyCurrentMaximumMemberCountByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyCurrentMaximumMemberCountByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='verifyCurrentMaximumMemberCountByStampTask',
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
                result_type=VerifyCurrentMaximumMemberCountByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_current_maximum_member_count_by_stamp_task(
        self,
        request: VerifyCurrentMaximumMemberCountByStampTaskRequest,
    ) -> VerifyCurrentMaximumMemberCountByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_current_maximum_member_count_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_current_maximum_member_count_by_stamp_task_async(
        self,
        request: VerifyCurrentMaximumMemberCountByStampTaskRequest,
    ) -> VerifyCurrentMaximumMemberCountByStampTaskResult:
        async_result = []
        self._verify_current_maximum_member_count_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _verify_include_member_by_stamp_task(
        self,
        request: VerifyIncludeMemberByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyIncludeMemberByStampTaskResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='guild',
            function='verifyIncludeMemberByStampTask',
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
                result_type=VerifyIncludeMemberByStampTaskResult,
                callback=callback,
                body=body,
            )
        )

    def verify_include_member_by_stamp_task(
        self,
        request: VerifyIncludeMemberByStampTaskRequest,
    ) -> VerifyIncludeMemberByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_include_member_by_stamp_task(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_include_member_by_stamp_task_async(
        self,
        request: VerifyIncludeMemberByStampTaskRequest,
    ) -> VerifyIncludeMemberByStampTaskResult:
        async_result = []
        self._verify_include_member_by_stamp_task(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_joined_guilds(
        self,
        request: DescribeJoinedGuildsRequest,
        callback: Callable[[AsyncResult[DescribeJoinedGuildsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='joinedGuild',
            function='describeJoinedGuilds',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DescribeJoinedGuildsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_joined_guilds(
        self,
        request: DescribeJoinedGuildsRequest,
    ) -> DescribeJoinedGuildsResult:
        async_result = []
        with timeout(30):
            self._describe_joined_guilds(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_joined_guilds_async(
        self,
        request: DescribeJoinedGuildsRequest,
    ) -> DescribeJoinedGuildsResult:
        async_result = []
        self._describe_joined_guilds(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_joined_guilds_by_user_id(
        self,
        request: DescribeJoinedGuildsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeJoinedGuildsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='joinedGuild',
            function='describeJoinedGuildsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DescribeJoinedGuildsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_joined_guilds_by_user_id(
        self,
        request: DescribeJoinedGuildsByUserIdRequest,
    ) -> DescribeJoinedGuildsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_joined_guilds_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_joined_guilds_by_user_id_async(
        self,
        request: DescribeJoinedGuildsByUserIdRequest,
    ) -> DescribeJoinedGuildsByUserIdResult:
        async_result = []
        self._describe_joined_guilds_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_joined_guild(
        self,
        request: GetJoinedGuildRequest,
        callback: Callable[[AsyncResult[GetJoinedGuildResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='joinedGuild',
            function='getJoinedGuild',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetJoinedGuildResult,
                callback=callback,
                body=body,
            )
        )

    def get_joined_guild(
        self,
        request: GetJoinedGuildRequest,
    ) -> GetJoinedGuildResult:
        async_result = []
        with timeout(30):
            self._get_joined_guild(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_joined_guild_async(
        self,
        request: GetJoinedGuildRequest,
    ) -> GetJoinedGuildResult:
        async_result = []
        self._get_joined_guild(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_joined_guild_by_user_id(
        self,
        request: GetJoinedGuildByUserIdRequest,
        callback: Callable[[AsyncResult[GetJoinedGuildByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='joinedGuild',
            function='getJoinedGuildByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetJoinedGuildByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_joined_guild_by_user_id(
        self,
        request: GetJoinedGuildByUserIdRequest,
    ) -> GetJoinedGuildByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_joined_guild_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_joined_guild_by_user_id_async(
        self,
        request: GetJoinedGuildByUserIdRequest,
    ) -> GetJoinedGuildByUserIdResult:
        async_result = []
        self._get_joined_guild_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_member_metadata(
        self,
        request: UpdateMemberMetadataRequest,
        callback: Callable[[AsyncResult[UpdateMemberMetadataResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='joinedGuild',
            function='updateMemberMetadata',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
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
                result_type=UpdateMemberMetadataResult,
                callback=callback,
                body=body,
            )
        )

    def update_member_metadata(
        self,
        request: UpdateMemberMetadataRequest,
    ) -> UpdateMemberMetadataResult:
        async_result = []
        with timeout(30):
            self._update_member_metadata(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_member_metadata_async(
        self,
        request: UpdateMemberMetadataRequest,
    ) -> UpdateMemberMetadataResult:
        async_result = []
        self._update_member_metadata(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_member_metadata_by_user_id(
        self,
        request: UpdateMemberMetadataByUserIdRequest,
        callback: Callable[[AsyncResult[UpdateMemberMetadataByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='joinedGuild',
            function='updateMemberMetadataByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.user_id is not None:
            body["userId"] = request.user_id
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
                result_type=UpdateMemberMetadataByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def update_member_metadata_by_user_id(
        self,
        request: UpdateMemberMetadataByUserIdRequest,
    ) -> UpdateMemberMetadataByUserIdResult:
        async_result = []
        with timeout(30):
            self._update_member_metadata_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_member_metadata_by_user_id_async(
        self,
        request: UpdateMemberMetadataByUserIdRequest,
    ) -> UpdateMemberMetadataByUserIdResult:
        async_result = []
        self._update_member_metadata_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _withdrawal(
        self,
        request: WithdrawalRequest,
        callback: Callable[[AsyncResult[WithdrawalResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='joinedGuild',
            function='withdrawal',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=WithdrawalResult,
                callback=callback,
                body=body,
            )
        )

    def withdrawal(
        self,
        request: WithdrawalRequest,
    ) -> WithdrawalResult:
        async_result = []
        with timeout(30):
            self._withdrawal(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def withdrawal_async(
        self,
        request: WithdrawalRequest,
    ) -> WithdrawalResult:
        async_result = []
        self._withdrawal(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _withdrawal_by_user_id(
        self,
        request: WithdrawalByUserIdRequest,
        callback: Callable[[AsyncResult[WithdrawalByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='joinedGuild',
            function='withdrawalByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=WithdrawalByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def withdrawal_by_user_id(
        self,
        request: WithdrawalByUserIdRequest,
    ) -> WithdrawalByUserIdResult:
        async_result = []
        with timeout(30):
            self._withdrawal_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def withdrawal_by_user_id_async(
        self,
        request: WithdrawalByUserIdRequest,
    ) -> WithdrawalByUserIdResult:
        async_result = []
        self._withdrawal_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_last_guild_master_activity(
        self,
        request: GetLastGuildMasterActivityRequest,
        callback: Callable[[AsyncResult[GetLastGuildMasterActivityResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='lastGuildMasterActivity',
            function='getLastGuildMasterActivity',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetLastGuildMasterActivityResult,
                callback=callback,
                body=body,
            )
        )

    def get_last_guild_master_activity(
        self,
        request: GetLastGuildMasterActivityRequest,
    ) -> GetLastGuildMasterActivityResult:
        async_result = []
        with timeout(30):
            self._get_last_guild_master_activity(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_last_guild_master_activity_async(
        self,
        request: GetLastGuildMasterActivityRequest,
    ) -> GetLastGuildMasterActivityResult:
        async_result = []
        self._get_last_guild_master_activity(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_last_guild_master_activity_by_guild_name(
        self,
        request: GetLastGuildMasterActivityByGuildNameRequest,
        callback: Callable[[AsyncResult[GetLastGuildMasterActivityByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='lastGuildMasterActivity',
            function='getLastGuildMasterActivityByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetLastGuildMasterActivityByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def get_last_guild_master_activity_by_guild_name(
        self,
        request: GetLastGuildMasterActivityByGuildNameRequest,
    ) -> GetLastGuildMasterActivityByGuildNameResult:
        async_result = []
        with timeout(30):
            self._get_last_guild_master_activity_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_last_guild_master_activity_by_guild_name_async(
        self,
        request: GetLastGuildMasterActivityByGuildNameRequest,
    ) -> GetLastGuildMasterActivityByGuildNameResult:
        async_result = []
        self._get_last_guild_master_activity_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _promote_senior_member(
        self,
        request: PromoteSeniorMemberRequest,
        callback: Callable[[AsyncResult[PromoteSeniorMemberResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='lastGuildMasterActivity',
            function='promoteSeniorMember',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=PromoteSeniorMemberResult,
                callback=callback,
                body=body,
            )
        )

    def promote_senior_member(
        self,
        request: PromoteSeniorMemberRequest,
    ) -> PromoteSeniorMemberResult:
        async_result = []
        with timeout(30):
            self._promote_senior_member(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def promote_senior_member_async(
        self,
        request: PromoteSeniorMemberRequest,
    ) -> PromoteSeniorMemberResult:
        async_result = []
        self._promote_senior_member(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _promote_senior_member_by_guild_name(
        self,
        request: PromoteSeniorMemberByGuildNameRequest,
        callback: Callable[[AsyncResult[PromoteSeniorMemberByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='lastGuildMasterActivity',
            function='promoteSeniorMemberByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=PromoteSeniorMemberByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def promote_senior_member_by_guild_name(
        self,
        request: PromoteSeniorMemberByGuildNameRequest,
    ) -> PromoteSeniorMemberByGuildNameResult:
        async_result = []
        with timeout(30):
            self._promote_senior_member_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def promote_senior_member_by_guild_name_async(
        self,
        request: PromoteSeniorMemberByGuildNameRequest,
    ) -> PromoteSeniorMemberByGuildNameResult:
        async_result = []
        self._promote_senior_member_by_guild_name(
            request,
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
            service="guild",
            component='currentGuildMaster',
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

    def _get_current_guild_master(
        self,
        request: GetCurrentGuildMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentGuildMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='currentGuildMaster',
            function='getCurrentGuildMaster',
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
                result_type=GetCurrentGuildMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_current_guild_master(
        self,
        request: GetCurrentGuildMasterRequest,
    ) -> GetCurrentGuildMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_guild_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_guild_master_async(
        self,
        request: GetCurrentGuildMasterRequest,
    ) -> GetCurrentGuildMasterResult:
        async_result = []
        self._get_current_guild_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _pre_update_current_guild_master(
        self,
        request: PreUpdateCurrentGuildMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentGuildMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='currentGuildMaster',
            function='preUpdateCurrentGuildMaster',
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
                result_type=PreUpdateCurrentGuildMasterResult,
                callback=callback,
                body=body,
            )
        )

    def pre_update_current_guild_master(
        self,
        request: PreUpdateCurrentGuildMasterRequest,
    ) -> PreUpdateCurrentGuildMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_guild_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_guild_master_async(
        self,
        request: PreUpdateCurrentGuildMasterRequest,
    ) -> PreUpdateCurrentGuildMasterResult:
        async_result = []
        self._pre_update_current_guild_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_guild_master(
        self,
        request: UpdateCurrentGuildMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentGuildMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='currentGuildMaster',
            function='updateCurrentGuildMaster',
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
                result_type=UpdateCurrentGuildMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_guild_master(
        self,
        request: UpdateCurrentGuildMasterRequest,
    ) -> UpdateCurrentGuildMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_guild_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_guild_master_async(
        self,
        request: UpdateCurrentGuildMasterRequest,
    ) -> UpdateCurrentGuildMasterResult:
        async_result = []
        self._update_current_guild_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_current_guild_master_from_git_hub(
        self,
        request: UpdateCurrentGuildMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentGuildMasterFromGitHubResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='currentGuildMaster',
            function='updateCurrentGuildMasterFromGitHub',
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
                result_type=UpdateCurrentGuildMasterFromGitHubResult,
                callback=callback,
                body=body,
            )
        )

    def update_current_guild_master_from_git_hub(
        self,
        request: UpdateCurrentGuildMasterFromGitHubRequest,
    ) -> UpdateCurrentGuildMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_guild_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_guild_master_from_git_hub_async(
        self,
        request: UpdateCurrentGuildMasterFromGitHubRequest,
    ) -> UpdateCurrentGuildMasterFromGitHubResult:
        async_result = []
        self._update_current_guild_master_from_git_hub(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_receive_requests(
        self,
        request: DescribeReceiveRequestsRequest,
        callback: Callable[[AsyncResult[DescribeReceiveRequestsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='receiveMemberRequest',
            function='describeReceiveRequests',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DescribeReceiveRequestsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_receive_requests(
        self,
        request: DescribeReceiveRequestsRequest,
    ) -> DescribeReceiveRequestsResult:
        async_result = []
        with timeout(30):
            self._describe_receive_requests(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_receive_requests_async(
        self,
        request: DescribeReceiveRequestsRequest,
    ) -> DescribeReceiveRequestsResult:
        async_result = []
        self._describe_receive_requests(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_receive_requests_by_guild_name(
        self,
        request: DescribeReceiveRequestsByGuildNameRequest,
        callback: Callable[[AsyncResult[DescribeReceiveRequestsByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='receiveMemberRequest',
            function='describeReceiveRequestsByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeReceiveRequestsByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def describe_receive_requests_by_guild_name(
        self,
        request: DescribeReceiveRequestsByGuildNameRequest,
    ) -> DescribeReceiveRequestsByGuildNameResult:
        async_result = []
        with timeout(30):
            self._describe_receive_requests_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_receive_requests_by_guild_name_async(
        self,
        request: DescribeReceiveRequestsByGuildNameRequest,
    ) -> DescribeReceiveRequestsByGuildNameResult:
        async_result = []
        self._describe_receive_requests_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_receive_request(
        self,
        request: GetReceiveRequestRequest,
        callback: Callable[[AsyncResult[GetReceiveRequestResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='receiveMemberRequest',
            function='getReceiveRequest',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.from_user_id is not None:
            body["fromUserId"] = request.from_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetReceiveRequestResult,
                callback=callback,
                body=body,
            )
        )

    def get_receive_request(
        self,
        request: GetReceiveRequestRequest,
    ) -> GetReceiveRequestResult:
        async_result = []
        with timeout(30):
            self._get_receive_request(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_receive_request_async(
        self,
        request: GetReceiveRequestRequest,
    ) -> GetReceiveRequestResult:
        async_result = []
        self._get_receive_request(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_receive_request_by_guild_name(
        self,
        request: GetReceiveRequestByGuildNameRequest,
        callback: Callable[[AsyncResult[GetReceiveRequestByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='receiveMemberRequest',
            function='getReceiveRequestByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.from_user_id is not None:
            body["fromUserId"] = request.from_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetReceiveRequestByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def get_receive_request_by_guild_name(
        self,
        request: GetReceiveRequestByGuildNameRequest,
    ) -> GetReceiveRequestByGuildNameResult:
        async_result = []
        with timeout(30):
            self._get_receive_request_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_receive_request_by_guild_name_async(
        self,
        request: GetReceiveRequestByGuildNameRequest,
    ) -> GetReceiveRequestByGuildNameResult:
        async_result = []
        self._get_receive_request_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _accept_request(
        self,
        request: AcceptRequestRequest,
        callback: Callable[[AsyncResult[AcceptRequestResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='receiveMemberRequest',
            function='acceptRequest',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.from_user_id is not None:
            body["fromUserId"] = request.from_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AcceptRequestResult,
                callback=callback,
                body=body,
            )
        )

    def accept_request(
        self,
        request: AcceptRequestRequest,
    ) -> AcceptRequestResult:
        async_result = []
        with timeout(30):
            self._accept_request(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def accept_request_async(
        self,
        request: AcceptRequestRequest,
    ) -> AcceptRequestResult:
        async_result = []
        self._accept_request(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _accept_request_by_guild_name(
        self,
        request: AcceptRequestByGuildNameRequest,
        callback: Callable[[AsyncResult[AcceptRequestByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='receiveMemberRequest',
            function='acceptRequestByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.from_user_id is not None:
            body["fromUserId"] = request.from_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AcceptRequestByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def accept_request_by_guild_name(
        self,
        request: AcceptRequestByGuildNameRequest,
    ) -> AcceptRequestByGuildNameResult:
        async_result = []
        with timeout(30):
            self._accept_request_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def accept_request_by_guild_name_async(
        self,
        request: AcceptRequestByGuildNameRequest,
    ) -> AcceptRequestByGuildNameResult:
        async_result = []
        self._accept_request_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _reject_request(
        self,
        request: RejectRequestRequest,
        callback: Callable[[AsyncResult[RejectRequestResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='receiveMemberRequest',
            function='rejectRequest',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.from_user_id is not None:
            body["fromUserId"] = request.from_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=RejectRequestResult,
                callback=callback,
                body=body,
            )
        )

    def reject_request(
        self,
        request: RejectRequestRequest,
    ) -> RejectRequestResult:
        async_result = []
        with timeout(30):
            self._reject_request(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reject_request_async(
        self,
        request: RejectRequestRequest,
    ) -> RejectRequestResult:
        async_result = []
        self._reject_request(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _reject_request_by_guild_name(
        self,
        request: RejectRequestByGuildNameRequest,
        callback: Callable[[AsyncResult[RejectRequestByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='receiveMemberRequest',
            function='rejectRequestByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.from_user_id is not None:
            body["fromUserId"] = request.from_user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=RejectRequestByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def reject_request_by_guild_name(
        self,
        request: RejectRequestByGuildNameRequest,
    ) -> RejectRequestByGuildNameResult:
        async_result = []
        with timeout(30):
            self._reject_request_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def reject_request_by_guild_name_async(
        self,
        request: RejectRequestByGuildNameRequest,
    ) -> RejectRequestByGuildNameResult:
        async_result = []
        self._reject_request_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_send_requests(
        self,
        request: DescribeSendRequestsRequest,
        callback: Callable[[AsyncResult[DescribeSendRequestsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='sendMemberRequest',
            function='describeSendRequests',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DescribeSendRequestsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_send_requests(
        self,
        request: DescribeSendRequestsRequest,
    ) -> DescribeSendRequestsResult:
        async_result = []
        with timeout(30):
            self._describe_send_requests(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_send_requests_async(
        self,
        request: DescribeSendRequestsRequest,
    ) -> DescribeSendRequestsResult:
        async_result = []
        self._describe_send_requests(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_send_requests_by_user_id(
        self,
        request: DescribeSendRequestsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeSendRequestsByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='sendMemberRequest',
            function='describeSendRequestsByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DescribeSendRequestsByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_send_requests_by_user_id(
        self,
        request: DescribeSendRequestsByUserIdRequest,
    ) -> DescribeSendRequestsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_send_requests_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_send_requests_by_user_id_async(
        self,
        request: DescribeSendRequestsByUserIdRequest,
    ) -> DescribeSendRequestsByUserIdResult:
        async_result = []
        self._describe_send_requests_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_send_request(
        self,
        request: GetSendRequestRequest,
        callback: Callable[[AsyncResult[GetSendRequestResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='sendMemberRequest',
            function='getSendRequest',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.target_guild_name is not None:
            body["targetGuildName"] = request.target_guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSendRequestResult,
                callback=callback,
                body=body,
            )
        )

    def get_send_request(
        self,
        request: GetSendRequestRequest,
    ) -> GetSendRequestResult:
        async_result = []
        with timeout(30):
            self._get_send_request(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_send_request_async(
        self,
        request: GetSendRequestRequest,
    ) -> GetSendRequestResult:
        async_result = []
        self._get_send_request(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_send_request_by_user_id(
        self,
        request: GetSendRequestByUserIdRequest,
        callback: Callable[[AsyncResult[GetSendRequestByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='sendMemberRequest',
            function='getSendRequestByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.target_guild_name is not None:
            body["targetGuildName"] = request.target_guild_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetSendRequestByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_send_request_by_user_id(
        self,
        request: GetSendRequestByUserIdRequest,
    ) -> GetSendRequestByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_send_request_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_send_request_by_user_id_async(
        self,
        request: GetSendRequestByUserIdRequest,
    ) -> GetSendRequestByUserIdResult:
        async_result = []
        self._get_send_request_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _send_request(
        self,
        request: SendRequestRequest,
        callback: Callable[[AsyncResult[SendRequestResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='sendMemberRequest',
            function='sendRequest',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.target_guild_name is not None:
            body["targetGuildName"] = request.target_guild_name
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
                result_type=SendRequestResult,
                callback=callback,
                body=body,
            )
        )

    def send_request(
        self,
        request: SendRequestRequest,
    ) -> SendRequestResult:
        async_result = []
        with timeout(30):
            self._send_request(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def send_request_async(
        self,
        request: SendRequestRequest,
    ) -> SendRequestResult:
        async_result = []
        self._send_request(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _send_request_by_user_id(
        self,
        request: SendRequestByUserIdRequest,
        callback: Callable[[AsyncResult[SendRequestByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='sendMemberRequest',
            function='sendRequestByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.target_guild_name is not None:
            body["targetGuildName"] = request.target_guild_name
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
                result_type=SendRequestByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def send_request_by_user_id(
        self,
        request: SendRequestByUserIdRequest,
    ) -> SendRequestByUserIdResult:
        async_result = []
        with timeout(30):
            self._send_request_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def send_request_by_user_id_async(
        self,
        request: SendRequestByUserIdRequest,
    ) -> SendRequestByUserIdResult:
        async_result = []
        self._send_request_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_request(
        self,
        request: DeleteRequestRequest,
        callback: Callable[[AsyncResult[DeleteRequestResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='sendMemberRequest',
            function='deleteRequest',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.target_guild_name is not None:
            body["targetGuildName"] = request.target_guild_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteRequestResult,
                callback=callback,
                body=body,
            )
        )

    def delete_request(
        self,
        request: DeleteRequestRequest,
    ) -> DeleteRequestResult:
        async_result = []
        with timeout(30):
            self._delete_request(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_request_async(
        self,
        request: DeleteRequestRequest,
    ) -> DeleteRequestResult:
        async_result = []
        self._delete_request(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_request_by_user_id(
        self,
        request: DeleteRequestByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteRequestByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='sendMemberRequest',
            function='deleteRequestByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.target_guild_name is not None:
            body["targetGuildName"] = request.target_guild_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteRequestByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def delete_request_by_user_id(
        self,
        request: DeleteRequestByUserIdRequest,
    ) -> DeleteRequestByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_request_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_request_by_user_id_async(
        self,
        request: DeleteRequestByUserIdRequest,
    ) -> DeleteRequestByUserIdResult:
        async_result = []
        self._delete_request_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_ignore_users(
        self,
        request: DescribeIgnoreUsersRequest,
        callback: Callable[[AsyncResult[DescribeIgnoreUsersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='ignoreUser',
            function='describeIgnoreUsers',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
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
                result_type=DescribeIgnoreUsersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_ignore_users(
        self,
        request: DescribeIgnoreUsersRequest,
    ) -> DescribeIgnoreUsersResult:
        async_result = []
        with timeout(30):
            self._describe_ignore_users(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_ignore_users_async(
        self,
        request: DescribeIgnoreUsersRequest,
    ) -> DescribeIgnoreUsersResult:
        async_result = []
        self._describe_ignore_users(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_ignore_users_by_guild_name(
        self,
        request: DescribeIgnoreUsersByGuildNameRequest,
        callback: Callable[[AsyncResult[DescribeIgnoreUsersByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='ignoreUser',
            function='describeIgnoreUsersByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeIgnoreUsersByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def describe_ignore_users_by_guild_name(
        self,
        request: DescribeIgnoreUsersByGuildNameRequest,
    ) -> DescribeIgnoreUsersByGuildNameResult:
        async_result = []
        with timeout(30):
            self._describe_ignore_users_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_ignore_users_by_guild_name_async(
        self,
        request: DescribeIgnoreUsersByGuildNameRequest,
    ) -> DescribeIgnoreUsersByGuildNameResult:
        async_result = []
        self._describe_ignore_users_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_ignore_user(
        self,
        request: GetIgnoreUserRequest,
        callback: Callable[[AsyncResult[GetIgnoreUserResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='ignoreUser',
            function='getIgnoreUser',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetIgnoreUserResult,
                callback=callback,
                body=body,
            )
        )

    def get_ignore_user(
        self,
        request: GetIgnoreUserRequest,
    ) -> GetIgnoreUserResult:
        async_result = []
        with timeout(30):
            self._get_ignore_user(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_ignore_user_async(
        self,
        request: GetIgnoreUserRequest,
    ) -> GetIgnoreUserResult:
        async_result = []
        self._get_ignore_user(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_ignore_user_by_guild_name(
        self,
        request: GetIgnoreUserByGuildNameRequest,
        callback: Callable[[AsyncResult[GetIgnoreUserByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='ignoreUser',
            function='getIgnoreUserByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetIgnoreUserByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def get_ignore_user_by_guild_name(
        self,
        request: GetIgnoreUserByGuildNameRequest,
    ) -> GetIgnoreUserByGuildNameResult:
        async_result = []
        with timeout(30):
            self._get_ignore_user_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_ignore_user_by_guild_name_async(
        self,
        request: GetIgnoreUserByGuildNameRequest,
    ) -> GetIgnoreUserByGuildNameResult:
        async_result = []
        self._get_ignore_user_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_ignore_user(
        self,
        request: AddIgnoreUserRequest,
        callback: Callable[[AsyncResult[AddIgnoreUserResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='ignoreUser',
            function='addIgnoreUser',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=AddIgnoreUserResult,
                callback=callback,
                body=body,
            )
        )

    def add_ignore_user(
        self,
        request: AddIgnoreUserRequest,
    ) -> AddIgnoreUserResult:
        async_result = []
        with timeout(30):
            self._add_ignore_user(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_ignore_user_async(
        self,
        request: AddIgnoreUserRequest,
    ) -> AddIgnoreUserResult:
        async_result = []
        self._add_ignore_user(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _add_ignore_user_by_guild_name(
        self,
        request: AddIgnoreUserByGuildNameRequest,
        callback: Callable[[AsyncResult[AddIgnoreUserByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='ignoreUser',
            function='addIgnoreUserByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
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
                result_type=AddIgnoreUserByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def add_ignore_user_by_guild_name(
        self,
        request: AddIgnoreUserByGuildNameRequest,
    ) -> AddIgnoreUserByGuildNameResult:
        async_result = []
        with timeout(30):
            self._add_ignore_user_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_ignore_user_by_guild_name_async(
        self,
        request: AddIgnoreUserByGuildNameRequest,
    ) -> AddIgnoreUserByGuildNameResult:
        async_result = []
        self._add_ignore_user_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_ignore_user(
        self,
        request: DeleteIgnoreUserRequest,
        callback: Callable[[AsyncResult[DeleteIgnoreUserResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='ignoreUser',
            function='deleteIgnoreUser',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.user_id is not None:
            body["userId"] = request.user_id

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteIgnoreUserResult,
                callback=callback,
                body=body,
            )
        )

    def delete_ignore_user(
        self,
        request: DeleteIgnoreUserRequest,
    ) -> DeleteIgnoreUserResult:
        async_result = []
        with timeout(30):
            self._delete_ignore_user(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_ignore_user_async(
        self,
        request: DeleteIgnoreUserRequest,
    ) -> DeleteIgnoreUserResult:
        async_result = []
        self._delete_ignore_user(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_ignore_user_by_guild_name(
        self,
        request: DeleteIgnoreUserByGuildNameRequest,
        callback: Callable[[AsyncResult[DeleteIgnoreUserByGuildNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="guild",
            component='ignoreUser',
            function='deleteIgnoreUserByGuildName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.guild_model_name is not None:
            body["guildModelName"] = request.guild_model_name
        if request.guild_name is not None:
            body["guildName"] = request.guild_name
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
                result_type=DeleteIgnoreUserByGuildNameResult,
                callback=callback,
                body=body,
            )
        )

    def delete_ignore_user_by_guild_name(
        self,
        request: DeleteIgnoreUserByGuildNameRequest,
    ) -> DeleteIgnoreUserByGuildNameResult:
        async_result = []
        with timeout(30):
            self._delete_ignore_user_by_guild_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_ignore_user_by_guild_name_async(
        self,
        request: DeleteIgnoreUserByGuildNameRequest,
    ) -> DeleteIgnoreUserByGuildNameResult:
        async_result = []
        self._delete_ignore_user_by_guild_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result