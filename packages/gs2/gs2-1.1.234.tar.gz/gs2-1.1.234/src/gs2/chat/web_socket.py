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


class Gs2ChatWebSocketClient(web_socket.AbstractGs2WebSocketClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
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
            service="chat",
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
        if request.allow_create_room is not None:
            body["allowCreateRoom"] = request.allow_create_room
        if request.message_life_time_days is not None:
            body["messageLifeTimeDays"] = request.message_life_time_days
        if request.post_message_script is not None:
            body["postMessageScript"] = request.post_message_script.to_dict()
        if request.create_room_script is not None:
            body["createRoomScript"] = request.create_room_script.to_dict()
        if request.delete_room_script is not None:
            body["deleteRoomScript"] = request.delete_room_script.to_dict()
        if request.subscribe_room_script is not None:
            body["subscribeRoomScript"] = request.subscribe_room_script.to_dict()
        if request.unsubscribe_room_script is not None:
            body["unsubscribeRoomScript"] = request.unsubscribe_room_script.to_dict()
        if request.post_notification is not None:
            body["postNotification"] = request.post_notification.to_dict()
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
        if request.allow_create_room is not None:
            body["allowCreateRoom"] = request.allow_create_room
        if request.message_life_time_days is not None:
            body["messageLifeTimeDays"] = request.message_life_time_days
        if request.post_message_script is not None:
            body["postMessageScript"] = request.post_message_script.to_dict()
        if request.create_room_script is not None:
            body["createRoomScript"] = request.create_room_script.to_dict()
        if request.delete_room_script is not None:
            body["deleteRoomScript"] = request.delete_room_script.to_dict()
        if request.subscribe_room_script is not None:
            body["subscribeRoomScript"] = request.subscribe_room_script.to_dict()
        if request.unsubscribe_room_script is not None:
            body["unsubscribeRoomScript"] = request.unsubscribe_room_script.to_dict()
        if request.post_notification is not None:
            body["postNotification"] = request.post_notification.to_dict()
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
            service="chat",
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

    def _describe_rooms(
        self,
        request: DescribeRoomsRequest,
        callback: Callable[[AsyncResult[DescribeRoomsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='describeRooms',
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
                result_type=DescribeRoomsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_rooms(
        self,
        request: DescribeRoomsRequest,
    ) -> DescribeRoomsResult:
        async_result = []
        with timeout(30):
            self._describe_rooms(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_rooms_async(
        self,
        request: DescribeRoomsRequest,
    ) -> DescribeRoomsResult:
        async_result = []
        self._describe_rooms(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_room(
        self,
        request: CreateRoomRequest,
        callback: Callable[[AsyncResult[CreateRoomResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='createRoom',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.name is not None:
            body["name"] = request.name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password
        if request.white_list_user_ids is not None:
            body["whiteListUserIds"] = [
                item
                for item in request.white_list_user_ids
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
                result_type=CreateRoomResult,
                callback=callback,
                body=body,
            )
        )

    def create_room(
        self,
        request: CreateRoomRequest,
    ) -> CreateRoomResult:
        async_result = []
        with timeout(30):
            self._create_room(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_room_async(
        self,
        request: CreateRoomRequest,
    ) -> CreateRoomResult:
        async_result = []
        self._create_room(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_room_from_backend(
        self,
        request: CreateRoomFromBackendRequest,
        callback: Callable[[AsyncResult[CreateRoomFromBackendResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='createRoomFromBackend',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.name is not None:
            body["name"] = request.name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password
        if request.white_list_user_ids is not None:
            body["whiteListUserIds"] = [
                item
                for item in request.white_list_user_ids
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
                result_type=CreateRoomFromBackendResult,
                callback=callback,
                body=body,
            )
        )

    def create_room_from_backend(
        self,
        request: CreateRoomFromBackendRequest,
    ) -> CreateRoomFromBackendResult:
        async_result = []
        with timeout(30):
            self._create_room_from_backend(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_room_from_backend_async(
        self,
        request: CreateRoomFromBackendRequest,
    ) -> CreateRoomFromBackendResult:
        async_result = []
        self._create_room_from_backend(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_room(
        self,
        request: GetRoomRequest,
        callback: Callable[[AsyncResult[GetRoomResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='getRoom',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetRoomResult,
                callback=callback,
                body=body,
            )
        )

    def get_room(
        self,
        request: GetRoomRequest,
    ) -> GetRoomResult:
        async_result = []
        with timeout(30):
            self._get_room(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_room_async(
        self,
        request: GetRoomRequest,
    ) -> GetRoomResult:
        async_result = []
        self._get_room(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_room(
        self,
        request: UpdateRoomRequest,
        callback: Callable[[AsyncResult[UpdateRoomResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='updateRoom',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password
        if request.white_list_user_ids is not None:
            body["whiteListUserIds"] = [
                item
                for item in request.white_list_user_ids
            ]
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
                result_type=UpdateRoomResult,
                callback=callback,
                body=body,
            )
        )

    def update_room(
        self,
        request: UpdateRoomRequest,
    ) -> UpdateRoomResult:
        async_result = []
        with timeout(30):
            self._update_room(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_room_async(
        self,
        request: UpdateRoomRequest,
    ) -> UpdateRoomResult:
        async_result = []
        self._update_room(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_room_from_backend(
        self,
        request: UpdateRoomFromBackendRequest,
        callback: Callable[[AsyncResult[UpdateRoomFromBackendResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='updateRoomFromBackend',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password
        if request.white_list_user_ids is not None:
            body["whiteListUserIds"] = [
                item
                for item in request.white_list_user_ids
            ]
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
                result_type=UpdateRoomFromBackendResult,
                callback=callback,
                body=body,
            )
        )

    def update_room_from_backend(
        self,
        request: UpdateRoomFromBackendRequest,
    ) -> UpdateRoomFromBackendResult:
        async_result = []
        with timeout(30):
            self._update_room_from_backend(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_room_from_backend_async(
        self,
        request: UpdateRoomFromBackendRequest,
    ) -> UpdateRoomFromBackendResult:
        async_result = []
        self._update_room_from_backend(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_room(
        self,
        request: DeleteRoomRequest,
        callback: Callable[[AsyncResult[DeleteRoomResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='deleteRoom',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
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
                result_type=DeleteRoomResult,
                callback=callback,
                body=body,
            )
        )

    def delete_room(
        self,
        request: DeleteRoomRequest,
    ) -> DeleteRoomResult:
        async_result = []
        with timeout(30):
            self._delete_room(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_room_async(
        self,
        request: DeleteRoomRequest,
    ) -> DeleteRoomResult:
        async_result = []
        self._delete_room(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_room_from_backend(
        self,
        request: DeleteRoomFromBackendRequest,
        callback: Callable[[AsyncResult[DeleteRoomFromBackendResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='room',
            function='deleteRoomFromBackend',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
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
                result_type=DeleteRoomFromBackendResult,
                callback=callback,
                body=body,
            )
        )

    def delete_room_from_backend(
        self,
        request: DeleteRoomFromBackendRequest,
    ) -> DeleteRoomFromBackendResult:
        async_result = []
        with timeout(30):
            self._delete_room_from_backend(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_room_from_backend_async(
        self,
        request: DeleteRoomFromBackendRequest,
    ) -> DeleteRoomFromBackendResult:
        async_result = []
        self._delete_room_from_backend(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_messages(
        self,
        request: DescribeMessagesRequest,
        callback: Callable[[AsyncResult[DescribeMessagesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='describeMessages',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.password is not None:
            body["password"] = request.password
        if request.category is not None:
            body["category"] = request.category
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.start_at is not None:
            body["startAt"] = request.start_at
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeMessagesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_messages(
        self,
        request: DescribeMessagesRequest,
    ) -> DescribeMessagesResult:
        async_result = []
        with timeout(30):
            self._describe_messages(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_messages_async(
        self,
        request: DescribeMessagesRequest,
    ) -> DescribeMessagesResult:
        async_result = []
        self._describe_messages(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_messages_by_user_id(
        self,
        request: DescribeMessagesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeMessagesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='describeMessagesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.password is not None:
            body["password"] = request.password
        if request.category is not None:
            body["category"] = request.category
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.start_at is not None:
            body["startAt"] = request.start_at
        if request.limit is not None:
            body["limit"] = request.limit
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeMessagesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_messages_by_user_id(
        self,
        request: DescribeMessagesByUserIdRequest,
    ) -> DescribeMessagesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_messages_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_messages_by_user_id_async(
        self,
        request: DescribeMessagesByUserIdRequest,
    ) -> DescribeMessagesByUserIdResult:
        async_result = []
        self._describe_messages_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_latest_messages(
        self,
        request: DescribeLatestMessagesRequest,
        callback: Callable[[AsyncResult[DescribeLatestMessagesResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='describeLatestMessages',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.password is not None:
            body["password"] = request.password
        if request.category is not None:
            body["category"] = request.category
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
                result_type=DescribeLatestMessagesResult,
                callback=callback,
                body=body,
            )
        )

    def describe_latest_messages(
        self,
        request: DescribeLatestMessagesRequest,
    ) -> DescribeLatestMessagesResult:
        async_result = []
        with timeout(30):
            self._describe_latest_messages(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_latest_messages_async(
        self,
        request: DescribeLatestMessagesRequest,
    ) -> DescribeLatestMessagesResult:
        async_result = []
        self._describe_latest_messages(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_latest_messages_by_user_id(
        self,
        request: DescribeLatestMessagesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeLatestMessagesByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='describeLatestMessagesByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.password is not None:
            body["password"] = request.password
        if request.category is not None:
            body["category"] = request.category
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
                result_type=DescribeLatestMessagesByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def describe_latest_messages_by_user_id(
        self,
        request: DescribeLatestMessagesByUserIdRequest,
    ) -> DescribeLatestMessagesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_latest_messages_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_latest_messages_by_user_id_async(
        self,
        request: DescribeLatestMessagesByUserIdRequest,
    ) -> DescribeLatestMessagesByUserIdResult:
        async_result = []
        self._describe_latest_messages_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _post(
        self,
        request: PostRequest,
        callback: Callable[[AsyncResult[PostResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='post',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.category is not None:
            body["category"] = request.category
        if request.metadata is not None:
            body["metadata"] = request.metadata
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
                result_type=PostResult,
                callback=callback,
                body=body,
            )
        )

    def post(
        self,
        request: PostRequest,
    ) -> PostResult:
        async_result = []
        with timeout(30):
            self._post(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def post_async(
        self,
        request: PostRequest,
    ) -> PostResult:
        async_result = []
        self._post(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _post_by_user_id(
        self,
        request: PostByUserIdRequest,
        callback: Callable[[AsyncResult[PostByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='postByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.category is not None:
            body["category"] = request.category
        if request.metadata is not None:
            body["metadata"] = request.metadata
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
                result_type=PostByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def post_by_user_id(
        self,
        request: PostByUserIdRequest,
    ) -> PostByUserIdResult:
        async_result = []
        with timeout(30):
            self._post_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def post_by_user_id_async(
        self,
        request: PostByUserIdRequest,
    ) -> PostByUserIdResult:
        async_result = []
        self._post_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_message(
        self,
        request: GetMessageRequest,
        callback: Callable[[AsyncResult[GetMessageResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='getMessage',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.message_name is not None:
            body["messageName"] = request.message_name
        if request.password is not None:
            body["password"] = request.password
        if request.access_token is not None:
            body["accessToken"] = request.access_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.access_token:
            body["xGs2AccessToken"] = request.access_token

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMessageResult,
                callback=callback,
                body=body,
            )
        )

    def get_message(
        self,
        request: GetMessageRequest,
    ) -> GetMessageResult:
        async_result = []
        with timeout(30):
            self._get_message(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_message_async(
        self,
        request: GetMessageRequest,
    ) -> GetMessageResult:
        async_result = []
        self._get_message(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_message_by_user_id(
        self,
        request: GetMessageByUserIdRequest,
        callback: Callable[[AsyncResult[GetMessageByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='getMessageByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.message_name is not None:
            body["messageName"] = request.message_name
        if request.password is not None:
            body["password"] = request.password
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetMessageByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def get_message_by_user_id(
        self,
        request: GetMessageByUserIdRequest,
    ) -> GetMessageByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_message_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_message_by_user_id_async(
        self,
        request: GetMessageByUserIdRequest,
    ) -> GetMessageByUserIdResult:
        async_result = []
        self._get_message_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_message(
        self,
        request: DeleteMessageRequest,
        callback: Callable[[AsyncResult[DeleteMessageResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='message',
            function='deleteMessage',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.message_name is not None:
            body["messageName"] = request.message_name
        if request.time_offset_token is not None:
            body["timeOffsetToken"] = request.time_offset_token

        if request.request_id:
            body["xGs2RequestId"] = request.request_id
        if request.duplication_avoider:
            body["xGs2DuplicationAvoider"] = request.duplication_avoider

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteMessageResult,
                callback=callback,
                body=body,
            )
        )

    def delete_message(
        self,
        request: DeleteMessageRequest,
    ) -> DeleteMessageResult:
        async_result = []
        with timeout(30):
            self._delete_message(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_message_async(
        self,
        request: DeleteMessageRequest,
    ) -> DeleteMessageResult:
        async_result = []
        self._delete_message(
            request,
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
            service="chat",
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
            service="chat",
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

    def _describe_subscribes_by_room_name(
        self,
        request: DescribeSubscribesByRoomNameRequest,
        callback: Callable[[AsyncResult[DescribeSubscribesByRoomNameResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='describeSubscribesByRoomName',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.page_token is not None:
            body["pageToken"] = request.page_token
        if request.limit is not None:
            body["limit"] = request.limit

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DescribeSubscribesByRoomNameResult,
                callback=callback,
                body=body,
            )
        )

    def describe_subscribes_by_room_name(
        self,
        request: DescribeSubscribesByRoomNameRequest,
    ) -> DescribeSubscribesByRoomNameResult:
        async_result = []
        with timeout(30):
            self._describe_subscribes_by_room_name(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_subscribes_by_room_name_async(
        self,
        request: DescribeSubscribesByRoomNameRequest,
    ) -> DescribeSubscribesByRoomNameResult:
        async_result = []
        self._describe_subscribes_by_room_name(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _subscribe(
        self,
        request: SubscribeRequest,
        callback: Callable[[AsyncResult[SubscribeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='subscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
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
                result_type=SubscribeResult,
                callback=callback,
                body=body,
            )
        )

    def subscribe(
        self,
        request: SubscribeRequest,
    ) -> SubscribeResult:
        async_result = []
        with timeout(30):
            self._subscribe(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def subscribe_async(
        self,
        request: SubscribeRequest,
    ) -> SubscribeResult:
        async_result = []
        self._subscribe(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _subscribe_by_user_id(
        self,
        request: SubscribeByUserIdRequest,
        callback: Callable[[AsyncResult[SubscribeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='subscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
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
                result_type=SubscribeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def subscribe_by_user_id(
        self,
        request: SubscribeByUserIdRequest,
    ) -> SubscribeByUserIdResult:
        async_result = []
        with timeout(30):
            self._subscribe_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def subscribe_by_user_id_async(
        self,
        request: SubscribeByUserIdRequest,
    ) -> SubscribeByUserIdResult:
        async_result = []
        self._subscribe_by_user_id(
            request,
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
            service="chat",
            component='subscribe',
            function='getSubscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token

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
            service="chat",
            component='subscribe',
            function='getSubscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
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

    def _update_notification_type(
        self,
        request: UpdateNotificationTypeRequest,
        callback: Callable[[AsyncResult[UpdateNotificationTypeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='updateNotificationType',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.access_token is not None:
            body["accessToken"] = request.access_token
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
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
                result_type=UpdateNotificationTypeResult,
                callback=callback,
                body=body,
            )
        )

    def update_notification_type(
        self,
        request: UpdateNotificationTypeRequest,
    ) -> UpdateNotificationTypeResult:
        async_result = []
        with timeout(30):
            self._update_notification_type(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_notification_type_async(
        self,
        request: UpdateNotificationTypeRequest,
    ) -> UpdateNotificationTypeResult:
        async_result = []
        self._update_notification_type(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_notification_type_by_user_id(
        self,
        request: UpdateNotificationTypeByUserIdRequest,
        callback: Callable[[AsyncResult[UpdateNotificationTypeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='updateNotificationTypeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
        if request.user_id is not None:
            body["userId"] = request.user_id
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
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
                result_type=UpdateNotificationTypeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def update_notification_type_by_user_id(
        self,
        request: UpdateNotificationTypeByUserIdRequest,
    ) -> UpdateNotificationTypeByUserIdResult:
        async_result = []
        with timeout(30):
            self._update_notification_type_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_notification_type_by_user_id_async(
        self,
        request: UpdateNotificationTypeByUserIdRequest,
    ) -> UpdateNotificationTypeByUserIdResult:
        async_result = []
        self._update_notification_type_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _unsubscribe(
        self,
        request: UnsubscribeRequest,
        callback: Callable[[AsyncResult[UnsubscribeResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='unsubscribe',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
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
                result_type=UnsubscribeResult,
                callback=callback,
                body=body,
            )
        )

    def unsubscribe(
        self,
        request: UnsubscribeRequest,
    ) -> UnsubscribeResult:
        async_result = []
        with timeout(30):
            self._unsubscribe(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def unsubscribe_async(
        self,
        request: UnsubscribeRequest,
    ) -> UnsubscribeResult:
        async_result = []
        self._unsubscribe(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _unsubscribe_by_user_id(
        self,
        request: UnsubscribeByUserIdRequest,
        callback: Callable[[AsyncResult[UnsubscribeByUserIdResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='subscribe',
            function='unsubscribeByUserId',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.room_name is not None:
            body["roomName"] = request.room_name
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
                result_type=UnsubscribeByUserIdResult,
                callback=callback,
                body=body,
            )
        )

    def unsubscribe_by_user_id(
        self,
        request: UnsubscribeByUserIdRequest,
    ) -> UnsubscribeByUserIdResult:
        async_result = []
        with timeout(30):
            self._unsubscribe_by_user_id(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def unsubscribe_by_user_id_async(
        self,
        request: UnsubscribeByUserIdRequest,
    ) -> UnsubscribeByUserIdResult:
        async_result = []
        self._unsubscribe_by_user_id(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_category_models(
        self,
        request: DescribeCategoryModelsRequest,
        callback: Callable[[AsyncResult[DescribeCategoryModelsResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='categoryModel',
            function='describeCategoryModels',
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
                result_type=DescribeCategoryModelsResult,
                callback=callback,
                body=body,
            )
        )

    def describe_category_models(
        self,
        request: DescribeCategoryModelsRequest,
    ) -> DescribeCategoryModelsResult:
        async_result = []
        with timeout(30):
            self._describe_category_models(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_category_models_async(
        self,
        request: DescribeCategoryModelsRequest,
    ) -> DescribeCategoryModelsResult:
        async_result = []
        self._describe_category_models(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_category_model(
        self,
        request: GetCategoryModelRequest,
        callback: Callable[[AsyncResult[GetCategoryModelResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='categoryModel',
            function='getCategoryModel',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.category is not None:
            body["category"] = request.category

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCategoryModelResult,
                callback=callback,
                body=body,
            )
        )

    def get_category_model(
        self,
        request: GetCategoryModelRequest,
    ) -> GetCategoryModelResult:
        async_result = []
        with timeout(30):
            self._get_category_model(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_category_model_async(
        self,
        request: GetCategoryModelRequest,
    ) -> GetCategoryModelResult:
        async_result = []
        self._get_category_model(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_category_model_masters(
        self,
        request: DescribeCategoryModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeCategoryModelMastersResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='categoryModelMaster',
            function='describeCategoryModelMasters',
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
                result_type=DescribeCategoryModelMastersResult,
                callback=callback,
                body=body,
            )
        )

    def describe_category_model_masters(
        self,
        request: DescribeCategoryModelMastersRequest,
    ) -> DescribeCategoryModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_category_model_masters(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_category_model_masters_async(
        self,
        request: DescribeCategoryModelMastersRequest,
    ) -> DescribeCategoryModelMastersResult:
        async_result = []
        self._describe_category_model_masters(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _create_category_model_master(
        self,
        request: CreateCategoryModelMasterRequest,
        callback: Callable[[AsyncResult[CreateCategoryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='categoryModelMaster',
            function='createCategoryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.category is not None:
            body["category"] = request.category
        if request.description is not None:
            body["description"] = request.description
        if request.reject_access_token_post is not None:
            body["rejectAccessTokenPost"] = request.reject_access_token_post

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=CreateCategoryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def create_category_model_master(
        self,
        request: CreateCategoryModelMasterRequest,
    ) -> CreateCategoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_category_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_category_model_master_async(
        self,
        request: CreateCategoryModelMasterRequest,
    ) -> CreateCategoryModelMasterResult:
        async_result = []
        self._create_category_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _get_category_model_master(
        self,
        request: GetCategoryModelMasterRequest,
        callback: Callable[[AsyncResult[GetCategoryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='categoryModelMaster',
            function='getCategoryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.category is not None:
            body["category"] = request.category

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=GetCategoryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def get_category_model_master(
        self,
        request: GetCategoryModelMasterRequest,
    ) -> GetCategoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_category_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_category_model_master_async(
        self,
        request: GetCategoryModelMasterRequest,
    ) -> GetCategoryModelMasterResult:
        async_result = []
        self._get_category_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _update_category_model_master(
        self,
        request: UpdateCategoryModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateCategoryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='categoryModelMaster',
            function='updateCategoryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.category is not None:
            body["category"] = request.category
        if request.description is not None:
            body["description"] = request.description
        if request.reject_access_token_post is not None:
            body["rejectAccessTokenPost"] = request.reject_access_token_post

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=UpdateCategoryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def update_category_model_master(
        self,
        request: UpdateCategoryModelMasterRequest,
    ) -> UpdateCategoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_category_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_category_model_master_async(
        self,
        request: UpdateCategoryModelMasterRequest,
    ) -> UpdateCategoryModelMasterResult:
        async_result = []
        self._update_category_model_master(
            request,
            lambda result: async_result.append(result),
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _delete_category_model_master(
        self,
        request: DeleteCategoryModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteCategoryModelMasterResult]], None],
    ):
        import uuid

        request_id = str(uuid.uuid4())
        body = self._create_metadata(
            service="chat",
            component='categoryModelMaster',
            function='deleteCategoryModelMaster',
            request_id=request_id,
        )

        if request.context_stack:
            body['contextStack'] = str(request.context_stack)
        if request.namespace_name is not None:
            body["namespaceName"] = request.namespace_name
        if request.category is not None:
            body["category"] = request.category

        if request.request_id:
            body["xGs2RequestId"] = request.request_id

        self.session.send(
            web_socket.NetworkJob(
                request_id=request_id,
                result_type=DeleteCategoryModelMasterResult,
                callback=callback,
                body=body,
            )
        )

    def delete_category_model_master(
        self,
        request: DeleteCategoryModelMasterRequest,
    ) -> DeleteCategoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_category_model_master(
                request,
                lambda result: async_result.append(result),
            )

        with timeout(30):
            while not async_result:
                time.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_category_model_master_async(
        self,
        request: DeleteCategoryModelMasterRequest,
    ) -> DeleteCategoryModelMasterResult:
        async_result = []
        self._delete_category_model_master(
            request,
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
            service="chat",
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
            service="chat",
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