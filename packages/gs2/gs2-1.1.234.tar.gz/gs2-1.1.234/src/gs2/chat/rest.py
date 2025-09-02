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


class Gs2ChatRestClient(rest.AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeNamespacesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateNamespaceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/status".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetNamespaceStatusResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetNamespaceResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateNamespaceResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteNamespaceResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/system/version"

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetServiceVersionResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/system/dump/user/{userId}".format(
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=DumpUserDataByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/system/dump/user/{userId}".format(
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=CheckDumpUserDataByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/system/clean/user/{userId}".format(
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CleanUserDataByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/system/clean/user/{userId}".format(
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=CheckCleanUserDataByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/system/import/user/{userId}/prepare".format(
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=PrepareImportUserDataByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/system/import/user/{userId}".format(
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ImportUserDataByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/system/import/user/{userId}/{uploadToken}".format(
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            uploadToken=request.upload_token if request.upload_token is not None and request.upload_token != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=CheckImportUserDataByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeRoomsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/user".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateRoomResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateRoomFromBackendResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetRoomResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/user".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateRoomResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
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

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateRoomFromBackendResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/user".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteRoomResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            query_strings["userId"] = request.user_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteRoomFromBackendResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.password is not None:
            query_strings["password"] = request.password
        if request.category is not None:
            query_strings["category"] = request.category
        if request.start_at is not None:
            query_strings["startAt"] = request.start_at
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeMessagesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message/get".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.password is not None:
            query_strings["password"] = request.password
        if request.category is not None:
            query_strings["category"] = request.category
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.start_at is not None:
            query_strings["startAt"] = request.start_at
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeMessagesByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message/latest".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.password is not None:
            query_strings["password"] = request.password
        if request.category is not None:
            query_strings["category"] = request.category
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeLatestMessagesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message/latest/get".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.password is not None:
            query_strings["password"] = request.password
        if request.category is not None:
            query_strings["category"] = request.category
        if request.user_id is not None:
            query_strings["userId"] = request.user_id
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeLatestMessagesByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.category is not None:
            body["category"] = request.category
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=PostResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message/user/{userId}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.category is not None:
            body["category"] = request.category
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.password is not None:
            body["password"] = request.password

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=PostByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message/{messageName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
            messageName=request.message_name if request.message_name is not None and request.message_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.password is not None:
            query_strings["password"] = request.password

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetMessageResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message/{messageName}/get".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
            messageName=request.message_name if request.message_name is not None and request.message_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.password is not None:
            query_strings["password"] = request.password
        if request.user_id is not None:
            query_strings["userId"] = request.user_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetMessageByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/message/{messageName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
            messageName=request.message_name if request.message_name is not None and request.message_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.user_id is not None:
            query_strings["userId"] = request.user_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteMessageResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/room/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeSubscribesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/room/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeSubscribesByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/room/{roomName}/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeSubscribesByRoomNameResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/room/{roomName}/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SubscribeResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/room/{roomName}/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SubscribeByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/room/{roomName}/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSubscribeResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/room/{roomName}/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSubscribeByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/room/{roomName}/subscribe/notification".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=UpdateNotificationTypeResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/room/{roomName}/subscribe/notification".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.notification_types is not None:
            body["notificationTypes"] = [
                item.to_dict()
                for item in request.notification_types
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=UpdateNotificationTypeByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/room/{roomName}/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=UnsubscribeResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/room/{roomName}/subscribe".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            roomName=request.room_name if request.room_name is not None and request.room_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=UnsubscribeByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/model".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeCategoryModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/model/{category}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            category=request.category if request.category is not None and request.category != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetCategoryModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master/model".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.page_token is not None:
            query_strings["pageToken"] = request.page_token
        if request.limit is not None:
            query_strings["limit"] = request.limit

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=DescribeCategoryModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master/model".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.category is not None:
            body["category"] = request.category
        if request.description is not None:
            body["description"] = request.description
        if request.reject_access_token_post is not None:
            body["rejectAccessTokenPost"] = request.reject_access_token_post

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateCategoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{category}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            category=request.category if request.category is not None and request.category != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetCategoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{category}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            category=request.category if request.category is not None and request.category != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.reject_access_token_post is not None:
            body["rejectAccessTokenPost"] = request.reject_access_token_post

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateCategoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{category}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            category=request.category if request.category is not None and request.category != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteCategoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master/export".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=ExportMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetCurrentModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=PreUpdateCurrentModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):
        if request.settings is not None:
            res = self.pre_update_current_model_master(
                PreUpdateCurrentModelMasterRequest() \
                    .with_context_stack(request.context_stack) \
                    .with_namespace_name(request.namespace_name)
            )
            import requests
            requests.put(res.upload_url, data=request.settings, headers={
                'Content-Type': 'application/json',
            })
            request.mode = "preUpload"
            request.upload_token = res.upload_token
            request.settings = None

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.mode is not None:
            body["mode"] = request.mode
        if request.settings is not None:
            body["settings"] = request.settings
        if request.upload_token is not None:
            body["uploadToken"] = request.upload_token

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateCurrentModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='chat',
            region=self.session.region,
        ) + "/{namespaceName}/master/from_git_hub".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.checkout_setting is not None:
            body["checkoutSetting"] = request.checkout_setting.to_dict()

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateCurrentModelMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result