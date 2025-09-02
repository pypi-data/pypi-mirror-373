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


class Gs2InventoryRestClient(rest.AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
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
            service='inventory',
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
        if request.acquire_script is not None:
            body["acquireScript"] = request.acquire_script.to_dict()
        if request.overflow_script is not None:
            body["overflowScript"] = request.overflow_script.to_dict()
        if request.consume_script is not None:
            body["consumeScript"] = request.consume_script.to_dict()
        if request.simple_item_acquire_script is not None:
            body["simpleItemAcquireScript"] = request.simple_item_acquire_script.to_dict()
        if request.simple_item_consume_script is not None:
            body["simpleItemConsumeScript"] = request.simple_item_consume_script.to_dict()
        if request.big_item_acquire_script is not None:
            body["bigItemAcquireScript"] = request.big_item_acquire_script.to_dict()
        if request.big_item_consume_script is not None:
            body["bigItemConsumeScript"] = request.big_item_consume_script.to_dict()
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
            service='inventory',
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
            service='inventory',
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
            service='inventory',
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
        if request.acquire_script is not None:
            body["acquireScript"] = request.acquire_script.to_dict()
        if request.overflow_script is not None:
            body["overflowScript"] = request.overflow_script.to_dict()
        if request.consume_script is not None:
            body["consumeScript"] = request.consume_script.to_dict()
        if request.simple_item_acquire_script is not None:
            body["simpleItemAcquireScript"] = request.simple_item_acquire_script.to_dict()
        if request.simple_item_consume_script is not None:
            body["simpleItemConsumeScript"] = request.simple_item_consume_script.to_dict()
        if request.big_item_acquire_script is not None:
            body["bigItemAcquireScript"] = request.big_item_acquire_script.to_dict()
        if request.big_item_consume_script is not None:
            body["bigItemConsumeScript"] = request.big_item_consume_script.to_dict()
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
            service='inventory',
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
            service='inventory',
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
            service='inventory',
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
            service='inventory',
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
            service='inventory',
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
            service='inventory',
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
            service='inventory',
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
            service='inventory',
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
            service='inventory',
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

    def _describe_inventory_model_masters(
        self,
        request: DescribeInventoryModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeInventoryModelMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory".format(
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
            result_type=DescribeInventoryModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_inventory_model_masters(
        self,
        request: DescribeInventoryModelMastersRequest,
    ) -> DescribeInventoryModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_inventory_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_inventory_model_masters_async(
        self,
        request: DescribeInventoryModelMastersRequest,
    ) -> DescribeInventoryModelMastersResult:
        async_result = []
        self._describe_inventory_model_masters(
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

    def _create_inventory_model_master(
        self,
        request: CreateInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[CreateInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.initial_capacity is not None:
            body["initialCapacity"] = request.initial_capacity
        if request.max_capacity is not None:
            body["maxCapacity"] = request.max_capacity
        if request.protect_referenced_item is not None:
            body["protectReferencedItem"] = request.protect_referenced_item

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_inventory_model_master(
        self,
        request: CreateInventoryModelMasterRequest,
    ) -> CreateInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_inventory_model_master_async(
        self,
        request: CreateInventoryModelMasterRequest,
    ) -> CreateInventoryModelMasterResult:
        async_result = []
        self._create_inventory_model_master(
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

    def _get_inventory_model_master(
        self,
        request: GetInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[GetInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=GetInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_inventory_model_master(
        self,
        request: GetInventoryModelMasterRequest,
    ) -> GetInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_inventory_model_master_async(
        self,
        request: GetInventoryModelMasterRequest,
    ) -> GetInventoryModelMasterResult:
        async_result = []
        self._get_inventory_model_master(
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

    def _update_inventory_model_master(
        self,
        request: UpdateInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.initial_capacity is not None:
            body["initialCapacity"] = request.initial_capacity
        if request.max_capacity is not None:
            body["maxCapacity"] = request.max_capacity
        if request.protect_referenced_item is not None:
            body["protectReferencedItem"] = request.protect_referenced_item

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_inventory_model_master(
        self,
        request: UpdateInventoryModelMasterRequest,
    ) -> UpdateInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_inventory_model_master_async(
        self,
        request: UpdateInventoryModelMasterRequest,
    ) -> UpdateInventoryModelMasterResult:
        async_result = []
        self._update_inventory_model_master(
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

    def _delete_inventory_model_master(
        self,
        request: DeleteInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DeleteInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_inventory_model_master(
        self,
        request: DeleteInventoryModelMasterRequest,
    ) -> DeleteInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_inventory_model_master_async(
        self,
        request: DeleteInventoryModelMasterRequest,
    ) -> DeleteInventoryModelMasterResult:
        async_result = []
        self._delete_inventory_model_master(
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

    def _describe_inventory_models(
        self,
        request: DescribeInventoryModelsRequest,
        callback: Callable[[AsyncResult[DescribeInventoryModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/inventory".format(
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
            result_type=DescribeInventoryModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_inventory_models(
        self,
        request: DescribeInventoryModelsRequest,
    ) -> DescribeInventoryModelsResult:
        async_result = []
        with timeout(30):
            self._describe_inventory_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_inventory_models_async(
        self,
        request: DescribeInventoryModelsRequest,
    ) -> DescribeInventoryModelsResult:
        async_result = []
        self._describe_inventory_models(
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

    def _get_inventory_model(
        self,
        request: GetInventoryModelRequest,
        callback: Callable[[AsyncResult[GetInventoryModelResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=GetInventoryModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_inventory_model(
        self,
        request: GetInventoryModelRequest,
    ) -> GetInventoryModelResult:
        async_result = []
        with timeout(30):
            self._get_inventory_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_inventory_model_async(
        self,
        request: GetInventoryModelRequest,
    ) -> GetInventoryModelResult:
        async_result = []
        self._get_inventory_model(
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

    def _describe_item_model_masters(
        self,
        request: DescribeItemModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeItemModelMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeItemModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_item_model_masters(
        self,
        request: DescribeItemModelMastersRequest,
    ) -> DescribeItemModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_item_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_item_model_masters_async(
        self,
        request: DescribeItemModelMastersRequest,
    ) -> DescribeItemModelMastersResult:
        async_result = []
        self._describe_item_model_masters(
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

    def _create_item_model_master(
        self,
        request: CreateItemModelMasterRequest,
        callback: Callable[[AsyncResult[CreateItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.stacking_limit is not None:
            body["stackingLimit"] = request.stacking_limit
        if request.allow_multiple_stacks is not None:
            body["allowMultipleStacks"] = request.allow_multiple_stacks
        if request.sort_value is not None:
            body["sortValue"] = request.sort_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateItemModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_item_model_master(
        self,
        request: CreateItemModelMasterRequest,
    ) -> CreateItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_item_model_master_async(
        self,
        request: CreateItemModelMasterRequest,
    ) -> CreateItemModelMasterResult:
        async_result = []
        self._create_item_model_master(
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

    def _get_item_model_master(
        self,
        request: GetItemModelMasterRequest,
        callback: Callable[[AsyncResult[GetItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetItemModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_item_model_master(
        self,
        request: GetItemModelMasterRequest,
    ) -> GetItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_model_master_async(
        self,
        request: GetItemModelMasterRequest,
    ) -> GetItemModelMasterResult:
        async_result = []
        self._get_item_model_master(
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

    def _update_item_model_master(
        self,
        request: UpdateItemModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.stacking_limit is not None:
            body["stackingLimit"] = request.stacking_limit
        if request.allow_multiple_stacks is not None:
            body["allowMultipleStacks"] = request.allow_multiple_stacks
        if request.sort_value is not None:
            body["sortValue"] = request.sort_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateItemModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_item_model_master(
        self,
        request: UpdateItemModelMasterRequest,
    ) -> UpdateItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_item_model_master_async(
        self,
        request: UpdateItemModelMasterRequest,
    ) -> UpdateItemModelMasterResult:
        async_result = []
        self._update_item_model_master(
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

    def _delete_item_model_master(
        self,
        request: DeleteItemModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=DeleteItemModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_item_model_master(
        self,
        request: DeleteItemModelMasterRequest,
    ) -> DeleteItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_item_model_master_async(
        self,
        request: DeleteItemModelMasterRequest,
    ) -> DeleteItemModelMasterResult:
        async_result = []
        self._delete_item_model_master(
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

    def _describe_item_models(
        self,
        request: DescribeItemModelsRequest,
        callback: Callable[[AsyncResult[DescribeItemModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeItemModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_item_models(
        self,
        request: DescribeItemModelsRequest,
    ) -> DescribeItemModelsResult:
        async_result = []
        with timeout(30):
            self._describe_item_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_item_models_async(
        self,
        request: DescribeItemModelsRequest,
    ) -> DescribeItemModelsResult:
        async_result = []
        self._describe_item_models(
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

    def _get_item_model(
        self,
        request: GetItemModelRequest,
        callback: Callable[[AsyncResult[GetItemModelResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetItemModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_item_model(
        self,
        request: GetItemModelRequest,
    ) -> GetItemModelResult:
        async_result = []
        with timeout(30):
            self._get_item_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_model_async(
        self,
        request: GetItemModelRequest,
    ) -> GetItemModelResult:
        async_result = []
        self._get_item_model(
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

    def _describe_simple_inventory_model_masters(
        self,
        request: DescribeSimpleInventoryModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeSimpleInventoryModelMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory".format(
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
            result_type=DescribeSimpleInventoryModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_simple_inventory_model_masters(
        self,
        request: DescribeSimpleInventoryModelMastersRequest,
    ) -> DescribeSimpleInventoryModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_simple_inventory_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_simple_inventory_model_masters_async(
        self,
        request: DescribeSimpleInventoryModelMastersRequest,
    ) -> DescribeSimpleInventoryModelMastersResult:
        async_result = []
        self._describe_simple_inventory_model_masters(
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

    def _create_simple_inventory_model_master(
        self,
        request: CreateSimpleInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[CreateSimpleInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateSimpleInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_simple_inventory_model_master(
        self,
        request: CreateSimpleInventoryModelMasterRequest,
    ) -> CreateSimpleInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_simple_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_simple_inventory_model_master_async(
        self,
        request: CreateSimpleInventoryModelMasterRequest,
    ) -> CreateSimpleInventoryModelMasterResult:
        async_result = []
        self._create_simple_inventory_model_master(
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

    def _get_simple_inventory_model_master(
        self,
        request: GetSimpleInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[GetSimpleInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=GetSimpleInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_simple_inventory_model_master(
        self,
        request: GetSimpleInventoryModelMasterRequest,
    ) -> GetSimpleInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_simple_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_simple_inventory_model_master_async(
        self,
        request: GetSimpleInventoryModelMasterRequest,
    ) -> GetSimpleInventoryModelMasterResult:
        async_result = []
        self._get_simple_inventory_model_master(
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

    def _update_simple_inventory_model_master(
        self,
        request: UpdateSimpleInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateSimpleInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateSimpleInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_simple_inventory_model_master(
        self,
        request: UpdateSimpleInventoryModelMasterRequest,
    ) -> UpdateSimpleInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_simple_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_simple_inventory_model_master_async(
        self,
        request: UpdateSimpleInventoryModelMasterRequest,
    ) -> UpdateSimpleInventoryModelMasterResult:
        async_result = []
        self._update_simple_inventory_model_master(
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

    def _delete_simple_inventory_model_master(
        self,
        request: DeleteSimpleInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteSimpleInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DeleteSimpleInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_simple_inventory_model_master(
        self,
        request: DeleteSimpleInventoryModelMasterRequest,
    ) -> DeleteSimpleInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_simple_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_simple_inventory_model_master_async(
        self,
        request: DeleteSimpleInventoryModelMasterRequest,
    ) -> DeleteSimpleInventoryModelMasterResult:
        async_result = []
        self._delete_simple_inventory_model_master(
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

    def _describe_simple_inventory_models(
        self,
        request: DescribeSimpleInventoryModelsRequest,
        callback: Callable[[AsyncResult[DescribeSimpleInventoryModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/simple/inventory".format(
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
            result_type=DescribeSimpleInventoryModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_simple_inventory_models(
        self,
        request: DescribeSimpleInventoryModelsRequest,
    ) -> DescribeSimpleInventoryModelsResult:
        async_result = []
        with timeout(30):
            self._describe_simple_inventory_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_simple_inventory_models_async(
        self,
        request: DescribeSimpleInventoryModelsRequest,
    ) -> DescribeSimpleInventoryModelsResult:
        async_result = []
        self._describe_simple_inventory_models(
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

    def _get_simple_inventory_model(
        self,
        request: GetSimpleInventoryModelRequest,
        callback: Callable[[AsyncResult[GetSimpleInventoryModelResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/simple/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=GetSimpleInventoryModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_simple_inventory_model(
        self,
        request: GetSimpleInventoryModelRequest,
    ) -> GetSimpleInventoryModelResult:
        async_result = []
        with timeout(30):
            self._get_simple_inventory_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_simple_inventory_model_async(
        self,
        request: GetSimpleInventoryModelRequest,
    ) -> GetSimpleInventoryModelResult:
        async_result = []
        self._get_simple_inventory_model(
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

    def _describe_simple_item_model_masters(
        self,
        request: DescribeSimpleItemModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeSimpleItemModelMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeSimpleItemModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_simple_item_model_masters(
        self,
        request: DescribeSimpleItemModelMastersRequest,
    ) -> DescribeSimpleItemModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_simple_item_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_simple_item_model_masters_async(
        self,
        request: DescribeSimpleItemModelMastersRequest,
    ) -> DescribeSimpleItemModelMastersResult:
        async_result = []
        self._describe_simple_item_model_masters(
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

    def _create_simple_item_model_master(
        self,
        request: CreateSimpleItemModelMasterRequest,
        callback: Callable[[AsyncResult[CreateSimpleItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateSimpleItemModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_simple_item_model_master(
        self,
        request: CreateSimpleItemModelMasterRequest,
    ) -> CreateSimpleItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_simple_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_simple_item_model_master_async(
        self,
        request: CreateSimpleItemModelMasterRequest,
    ) -> CreateSimpleItemModelMasterResult:
        async_result = []
        self._create_simple_item_model_master(
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

    def _get_simple_item_model_master(
        self,
        request: GetSimpleItemModelMasterRequest,
        callback: Callable[[AsyncResult[GetSimpleItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetSimpleItemModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_simple_item_model_master(
        self,
        request: GetSimpleItemModelMasterRequest,
    ) -> GetSimpleItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_simple_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_simple_item_model_master_async(
        self,
        request: GetSimpleItemModelMasterRequest,
    ) -> GetSimpleItemModelMasterResult:
        async_result = []
        self._get_simple_item_model_master(
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

    def _update_simple_item_model_master(
        self,
        request: UpdateSimpleItemModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateSimpleItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateSimpleItemModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_simple_item_model_master(
        self,
        request: UpdateSimpleItemModelMasterRequest,
    ) -> UpdateSimpleItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_simple_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_simple_item_model_master_async(
        self,
        request: UpdateSimpleItemModelMasterRequest,
    ) -> UpdateSimpleItemModelMasterResult:
        async_result = []
        self._update_simple_item_model_master(
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

    def _delete_simple_item_model_master(
        self,
        request: DeleteSimpleItemModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteSimpleItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/simple/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=DeleteSimpleItemModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_simple_item_model_master(
        self,
        request: DeleteSimpleItemModelMasterRequest,
    ) -> DeleteSimpleItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_simple_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_simple_item_model_master_async(
        self,
        request: DeleteSimpleItemModelMasterRequest,
    ) -> DeleteSimpleItemModelMasterResult:
        async_result = []
        self._delete_simple_item_model_master(
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

    def _describe_simple_item_models(
        self,
        request: DescribeSimpleItemModelsRequest,
        callback: Callable[[AsyncResult[DescribeSimpleItemModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/simple/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeSimpleItemModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_simple_item_models(
        self,
        request: DescribeSimpleItemModelsRequest,
    ) -> DescribeSimpleItemModelsResult:
        async_result = []
        with timeout(30):
            self._describe_simple_item_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_simple_item_models_async(
        self,
        request: DescribeSimpleItemModelsRequest,
    ) -> DescribeSimpleItemModelsResult:
        async_result = []
        self._describe_simple_item_models(
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

    def _get_simple_item_model(
        self,
        request: GetSimpleItemModelRequest,
        callback: Callable[[AsyncResult[GetSimpleItemModelResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/simple/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetSimpleItemModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_simple_item_model(
        self,
        request: GetSimpleItemModelRequest,
    ) -> GetSimpleItemModelResult:
        async_result = []
        with timeout(30):
            self._get_simple_item_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_simple_item_model_async(
        self,
        request: GetSimpleItemModelRequest,
    ) -> GetSimpleItemModelResult:
        async_result = []
        self._get_simple_item_model(
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

    def _describe_big_inventory_model_masters(
        self,
        request: DescribeBigInventoryModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeBigInventoryModelMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory".format(
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
            result_type=DescribeBigInventoryModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_big_inventory_model_masters(
        self,
        request: DescribeBigInventoryModelMastersRequest,
    ) -> DescribeBigInventoryModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_big_inventory_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_big_inventory_model_masters_async(
        self,
        request: DescribeBigInventoryModelMastersRequest,
    ) -> DescribeBigInventoryModelMastersResult:
        async_result = []
        self._describe_big_inventory_model_masters(
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

    def _create_big_inventory_model_master(
        self,
        request: CreateBigInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[CreateBigInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateBigInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_big_inventory_model_master(
        self,
        request: CreateBigInventoryModelMasterRequest,
    ) -> CreateBigInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_big_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_big_inventory_model_master_async(
        self,
        request: CreateBigInventoryModelMasterRequest,
    ) -> CreateBigInventoryModelMasterResult:
        async_result = []
        self._create_big_inventory_model_master(
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

    def _get_big_inventory_model_master(
        self,
        request: GetBigInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[GetBigInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=GetBigInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_big_inventory_model_master(
        self,
        request: GetBigInventoryModelMasterRequest,
    ) -> GetBigInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_big_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_big_inventory_model_master_async(
        self,
        request: GetBigInventoryModelMasterRequest,
    ) -> GetBigInventoryModelMasterResult:
        async_result = []
        self._get_big_inventory_model_master(
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

    def _update_big_inventory_model_master(
        self,
        request: UpdateBigInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateBigInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateBigInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_big_inventory_model_master(
        self,
        request: UpdateBigInventoryModelMasterRequest,
    ) -> UpdateBigInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_big_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_big_inventory_model_master_async(
        self,
        request: UpdateBigInventoryModelMasterRequest,
    ) -> UpdateBigInventoryModelMasterResult:
        async_result = []
        self._update_big_inventory_model_master(
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

    def _delete_big_inventory_model_master(
        self,
        request: DeleteBigInventoryModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteBigInventoryModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DeleteBigInventoryModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_big_inventory_model_master(
        self,
        request: DeleteBigInventoryModelMasterRequest,
    ) -> DeleteBigInventoryModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_big_inventory_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_big_inventory_model_master_async(
        self,
        request: DeleteBigInventoryModelMasterRequest,
    ) -> DeleteBigInventoryModelMasterResult:
        async_result = []
        self._delete_big_inventory_model_master(
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

    def _describe_big_inventory_models(
        self,
        request: DescribeBigInventoryModelsRequest,
        callback: Callable[[AsyncResult[DescribeBigInventoryModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/big/inventory".format(
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
            result_type=DescribeBigInventoryModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_big_inventory_models(
        self,
        request: DescribeBigInventoryModelsRequest,
    ) -> DescribeBigInventoryModelsResult:
        async_result = []
        with timeout(30):
            self._describe_big_inventory_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_big_inventory_models_async(
        self,
        request: DescribeBigInventoryModelsRequest,
    ) -> DescribeBigInventoryModelsResult:
        async_result = []
        self._describe_big_inventory_models(
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

    def _get_big_inventory_model(
        self,
        request: GetBigInventoryModelRequest,
        callback: Callable[[AsyncResult[GetBigInventoryModelResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/big/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=GetBigInventoryModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_big_inventory_model(
        self,
        request: GetBigInventoryModelRequest,
    ) -> GetBigInventoryModelResult:
        async_result = []
        with timeout(30):
            self._get_big_inventory_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_big_inventory_model_async(
        self,
        request: GetBigInventoryModelRequest,
    ) -> GetBigInventoryModelResult:
        async_result = []
        self._get_big_inventory_model(
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

    def _describe_big_item_model_masters(
        self,
        request: DescribeBigItemModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeBigItemModelMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeBigItemModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_big_item_model_masters(
        self,
        request: DescribeBigItemModelMastersRequest,
    ) -> DescribeBigItemModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_big_item_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_big_item_model_masters_async(
        self,
        request: DescribeBigItemModelMastersRequest,
    ) -> DescribeBigItemModelMastersResult:
        async_result = []
        self._describe_big_item_model_masters(
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

    def _create_big_item_model_master(
        self,
        request: CreateBigItemModelMasterRequest,
        callback: Callable[[AsyncResult[CreateBigItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.name is not None:
            body["name"] = request.name
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateBigItemModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_big_item_model_master(
        self,
        request: CreateBigItemModelMasterRequest,
    ) -> CreateBigItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_big_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_big_item_model_master_async(
        self,
        request: CreateBigItemModelMasterRequest,
    ) -> CreateBigItemModelMasterResult:
        async_result = []
        self._create_big_item_model_master(
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

    def _get_big_item_model_master(
        self,
        request: GetBigItemModelMasterRequest,
        callback: Callable[[AsyncResult[GetBigItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetBigItemModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_big_item_model_master(
        self,
        request: GetBigItemModelMasterRequest,
    ) -> GetBigItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_big_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_big_item_model_master_async(
        self,
        request: GetBigItemModelMasterRequest,
    ) -> GetBigItemModelMasterResult:
        async_result = []
        self._get_big_item_model_master(
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

    def _update_big_item_model_master(
        self,
        request: UpdateBigItemModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateBigItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateBigItemModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_big_item_model_master(
        self,
        request: UpdateBigItemModelMasterRequest,
    ) -> UpdateBigItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_big_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_big_item_model_master_async(
        self,
        request: UpdateBigItemModelMasterRequest,
    ) -> UpdateBigItemModelMasterResult:
        async_result = []
        self._update_big_item_model_master(
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

    def _delete_big_item_model_master(
        self,
        request: DeleteBigItemModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteBigItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/master/big/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=DeleteBigItemModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_big_item_model_master(
        self,
        request: DeleteBigItemModelMasterRequest,
    ) -> DeleteBigItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_big_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_big_item_model_master_async(
        self,
        request: DeleteBigItemModelMasterRequest,
    ) -> DeleteBigItemModelMasterResult:
        async_result = []
        self._delete_big_item_model_master(
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

    def _describe_big_item_models(
        self,
        request: DescribeBigItemModelsRequest,
        callback: Callable[[AsyncResult[DescribeBigItemModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/big/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeBigItemModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_big_item_models(
        self,
        request: DescribeBigItemModelsRequest,
    ) -> DescribeBigItemModelsResult:
        async_result = []
        with timeout(30):
            self._describe_big_item_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_big_item_models_async(
        self,
        request: DescribeBigItemModelsRequest,
    ) -> DescribeBigItemModelsResult:
        async_result = []
        self._describe_big_item_models(
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

    def _get_big_item_model(
        self,
        request: GetBigItemModelRequest,
        callback: Callable[[AsyncResult[GetBigItemModelResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/big/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetBigItemModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_big_item_model(
        self,
        request: GetBigItemModelRequest,
    ) -> GetBigItemModelResult:
        async_result = []
        with timeout(30):
            self._get_big_item_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_big_item_model_async(
        self,
        request: GetBigItemModelRequest,
    ) -> GetBigItemModelResult:
        async_result = []
        self._get_big_item_model(
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
            service='inventory',
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

    def _get_current_item_model_master(
        self,
        request: GetCurrentItemModelMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
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
            result_type=GetCurrentItemModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_current_item_model_master(
        self,
        request: GetCurrentItemModelMasterRequest,
    ) -> GetCurrentItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_item_model_master_async(
        self,
        request: GetCurrentItemModelMasterRequest,
    ) -> GetCurrentItemModelMasterResult:
        async_result = []
        self._get_current_item_model_master(
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

    def _pre_update_current_item_model_master(
        self,
        request: PreUpdateCurrentItemModelMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentItemModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
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
            result_type=PreUpdateCurrentItemModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def pre_update_current_item_model_master(
        self,
        request: PreUpdateCurrentItemModelMasterRequest,
    ) -> PreUpdateCurrentItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_item_model_master_async(
        self,
        request: PreUpdateCurrentItemModelMasterRequest,
    ) -> PreUpdateCurrentItemModelMasterResult:
        async_result = []
        self._pre_update_current_item_model_master(
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

    def _update_current_item_model_master(
        self,
        request: UpdateCurrentItemModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentItemModelMasterResult]], None],
        is_blocking: bool,
    ):
        if request.settings is not None:
            res = self.pre_update_current_item_model_master(
                PreUpdateCurrentItemModelMasterRequest() \
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
            service='inventory',
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
            result_type=UpdateCurrentItemModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_item_model_master(
        self,
        request: UpdateCurrentItemModelMasterRequest,
    ) -> UpdateCurrentItemModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_item_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_item_model_master_async(
        self,
        request: UpdateCurrentItemModelMasterRequest,
    ) -> UpdateCurrentItemModelMasterResult:
        async_result = []
        self._update_current_item_model_master(
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

    def _update_current_item_model_master_from_git_hub(
        self,
        request: UpdateCurrentItemModelMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentItemModelMasterFromGitHubResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
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
            result_type=UpdateCurrentItemModelMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_item_model_master_from_git_hub(
        self,
        request: UpdateCurrentItemModelMasterFromGitHubRequest,
    ) -> UpdateCurrentItemModelMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_item_model_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_item_model_master_from_git_hub_async(
        self,
        request: UpdateCurrentItemModelMasterFromGitHubRequest,
    ) -> UpdateCurrentItemModelMasterFromGitHubResult:
        async_result = []
        self._update_current_item_model_master_from_git_hub(
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

    def _describe_inventories(
        self,
        request: DescribeInventoriesRequest,
        callback: Callable[[AsyncResult[DescribeInventoriesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory".format(
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
            result_type=DescribeInventoriesResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_inventories(
        self,
        request: DescribeInventoriesRequest,
    ) -> DescribeInventoriesResult:
        async_result = []
        with timeout(30):
            self._describe_inventories(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_inventories_async(
        self,
        request: DescribeInventoriesRequest,
    ) -> DescribeInventoriesResult:
        async_result = []
        self._describe_inventories(
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

    def _describe_inventories_by_user_id(
        self,
        request: DescribeInventoriesByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeInventoriesByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory".format(
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
            result_type=DescribeInventoriesByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_inventories_by_user_id(
        self,
        request: DescribeInventoriesByUserIdRequest,
    ) -> DescribeInventoriesByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_inventories_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_inventories_by_user_id_async(
        self,
        request: DescribeInventoriesByUserIdRequest,
    ) -> DescribeInventoriesByUserIdResult:
        async_result = []
        self._describe_inventories_by_user_id(
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

    def _get_inventory(
        self,
        request: GetInventoryRequest,
        callback: Callable[[AsyncResult[GetInventoryResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=GetInventoryResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_inventory(
        self,
        request: GetInventoryRequest,
    ) -> GetInventoryResult:
        async_result = []
        with timeout(30):
            self._get_inventory(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_inventory_async(
        self,
        request: GetInventoryRequest,
    ) -> GetInventoryResult:
        async_result = []
        self._get_inventory(
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

    def _get_inventory_by_user_id(
        self,
        request: GetInventoryByUserIdRequest,
        callback: Callable[[AsyncResult[GetInventoryByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=GetInventoryByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_inventory_by_user_id(
        self,
        request: GetInventoryByUserIdRequest,
    ) -> GetInventoryByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_inventory_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_inventory_by_user_id_async(
        self,
        request: GetInventoryByUserIdRequest,
    ) -> GetInventoryByUserIdResult:
        async_result = []
        self._get_inventory_by_user_id(
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

    def _add_capacity_by_user_id(
        self,
        request: AddCapacityByUserIdRequest,
        callback: Callable[[AsyncResult[AddCapacityByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/capacity".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.add_capacity_value is not None:
            body["addCapacityValue"] = request.add_capacity_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AddCapacityByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def add_capacity_by_user_id(
        self,
        request: AddCapacityByUserIdRequest,
    ) -> AddCapacityByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_capacity_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_capacity_by_user_id_async(
        self,
        request: AddCapacityByUserIdRequest,
    ) -> AddCapacityByUserIdResult:
        async_result = []
        self._add_capacity_by_user_id(
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

    def _set_capacity_by_user_id(
        self,
        request: SetCapacityByUserIdRequest,
        callback: Callable[[AsyncResult[SetCapacityByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/capacity".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.new_capacity_value is not None:
            body["newCapacityValue"] = request.new_capacity_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=SetCapacityByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_capacity_by_user_id(
        self,
        request: SetCapacityByUserIdRequest,
    ) -> SetCapacityByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_capacity_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_capacity_by_user_id_async(
        self,
        request: SetCapacityByUserIdRequest,
    ) -> SetCapacityByUserIdResult:
        async_result = []
        self._set_capacity_by_user_id(
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

    def _delete_inventory_by_user_id(
        self,
        request: DeleteInventoryByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteInventoryByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DeleteInventoryByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_inventory_by_user_id(
        self,
        request: DeleteInventoryByUserIdRequest,
    ) -> DeleteInventoryByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_inventory_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_inventory_by_user_id_async(
        self,
        request: DeleteInventoryByUserIdRequest,
    ) -> DeleteInventoryByUserIdResult:
        async_result = []
        self._delete_inventory_by_user_id(
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

    def _verify_inventory_current_max_capacity(
        self,
        request: VerifyInventoryCurrentMaxCapacityRequest,
        callback: Callable[[AsyncResult[VerifyInventoryCurrentMaxCapacityResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.current_inventory_max_capacity is not None:
            body["currentInventoryMaxCapacity"] = request.current_inventory_max_capacity
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyInventoryCurrentMaxCapacityResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_inventory_current_max_capacity(
        self,
        request: VerifyInventoryCurrentMaxCapacityRequest,
    ) -> VerifyInventoryCurrentMaxCapacityResult:
        async_result = []
        with timeout(30):
            self._verify_inventory_current_max_capacity(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_inventory_current_max_capacity_async(
        self,
        request: VerifyInventoryCurrentMaxCapacityRequest,
    ) -> VerifyInventoryCurrentMaxCapacityResult:
        async_result = []
        self._verify_inventory_current_max_capacity(
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

    def _verify_inventory_current_max_capacity_by_user_id(
        self,
        request: VerifyInventoryCurrentMaxCapacityByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyInventoryCurrentMaxCapacityByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.current_inventory_max_capacity is not None:
            body["currentInventoryMaxCapacity"] = request.current_inventory_max_capacity
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyInventoryCurrentMaxCapacityByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_inventory_current_max_capacity_by_user_id(
        self,
        request: VerifyInventoryCurrentMaxCapacityByUserIdRequest,
    ) -> VerifyInventoryCurrentMaxCapacityByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_inventory_current_max_capacity_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_inventory_current_max_capacity_by_user_id_async(
        self,
        request: VerifyInventoryCurrentMaxCapacityByUserIdRequest,
    ) -> VerifyInventoryCurrentMaxCapacityByUserIdResult:
        async_result = []
        self._verify_inventory_current_max_capacity_by_user_id(
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

    def _verify_inventory_current_max_capacity_by_stamp_task(
        self,
        request: VerifyInventoryCurrentMaxCapacityByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyInventoryCurrentMaxCapacityByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/inventory/verify"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyInventoryCurrentMaxCapacityByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_inventory_current_max_capacity_by_stamp_task(
        self,
        request: VerifyInventoryCurrentMaxCapacityByStampTaskRequest,
    ) -> VerifyInventoryCurrentMaxCapacityByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_inventory_current_max_capacity_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_inventory_current_max_capacity_by_stamp_task_async(
        self,
        request: VerifyInventoryCurrentMaxCapacityByStampTaskRequest,
    ) -> VerifyInventoryCurrentMaxCapacityByStampTaskResult:
        async_result = []
        self._verify_inventory_current_max_capacity_by_stamp_task(
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

    def _add_capacity_by_stamp_sheet(
        self,
        request: AddCapacityByStampSheetRequest,
        callback: Callable[[AsyncResult[AddCapacityByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/inventory/capacity/add"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AddCapacityByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
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
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/inventory/capacity/set"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetCapacityByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
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
                is_blocking=True,
            )

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
            is_blocking=False,
        )

        import asyncio
        with timeout(30):
            while not async_result:
                await asyncio.sleep(0.01)

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result

    def _describe_item_sets(
        self,
        request: DescribeItemSetsRequest,
        callback: Callable[[AsyncResult[DescribeItemSetsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeItemSetsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_item_sets(
        self,
        request: DescribeItemSetsRequest,
    ) -> DescribeItemSetsResult:
        async_result = []
        with timeout(30):
            self._describe_item_sets(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_item_sets_async(
        self,
        request: DescribeItemSetsRequest,
    ) -> DescribeItemSetsResult:
        async_result = []
        self._describe_item_sets(
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

    def _describe_item_sets_by_user_id(
        self,
        request: DescribeItemSetsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeItemSetsByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeItemSetsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_item_sets_by_user_id(
        self,
        request: DescribeItemSetsByUserIdRequest,
    ) -> DescribeItemSetsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_item_sets_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_item_sets_by_user_id_async(
        self,
        request: DescribeItemSetsByUserIdRequest,
    ) -> DescribeItemSetsByUserIdResult:
        async_result = []
        self._describe_item_sets_by_user_id(
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

    def _get_item_set(
        self,
        request: GetItemSetRequest,
        callback: Callable[[AsyncResult[GetItemSetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.item_set_name is not None:
            query_strings["itemSetName"] = request.item_set_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetItemSetResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_item_set(
        self,
        request: GetItemSetRequest,
    ) -> GetItemSetResult:
        async_result = []
        with timeout(30):
            self._get_item_set(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_set_async(
        self,
        request: GetItemSetRequest,
    ) -> GetItemSetResult:
        async_result = []
        self._get_item_set(
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

    def _get_item_set_by_user_id(
        self,
        request: GetItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[GetItemSetByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.item_set_name is not None:
            query_strings["itemSetName"] = request.item_set_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetItemSetByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_item_set_by_user_id(
        self,
        request: GetItemSetByUserIdRequest,
    ) -> GetItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_set_by_user_id_async(
        self,
        request: GetItemSetByUserIdRequest,
    ) -> GetItemSetByUserIdResult:
        async_result = []
        self._get_item_set_by_user_id(
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

    def _get_item_with_signature(
        self,
        request: GetItemWithSignatureRequest,
        callback: Callable[[AsyncResult[GetItemWithSignatureResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}/signature".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.item_set_name is not None:
            query_strings["itemSetName"] = request.item_set_name
        if request.key_id is not None:
            query_strings["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetItemWithSignatureResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_item_with_signature(
        self,
        request: GetItemWithSignatureRequest,
    ) -> GetItemWithSignatureResult:
        async_result = []
        with timeout(30):
            self._get_item_with_signature(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_with_signature_async(
        self,
        request: GetItemWithSignatureRequest,
    ) -> GetItemWithSignatureResult:
        async_result = []
        self._get_item_with_signature(
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

    def _get_item_with_signature_by_user_id(
        self,
        request: GetItemWithSignatureByUserIdRequest,
        callback: Callable[[AsyncResult[GetItemWithSignatureByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/signature".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.item_set_name is not None:
            query_strings["itemSetName"] = request.item_set_name
        if request.key_id is not None:
            query_strings["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetItemWithSignatureByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_item_with_signature_by_user_id(
        self,
        request: GetItemWithSignatureByUserIdRequest,
    ) -> GetItemWithSignatureByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_item_with_signature_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_item_with_signature_by_user_id_async(
        self,
        request: GetItemWithSignatureByUserIdRequest,
    ) -> GetItemWithSignatureByUserIdResult:
        async_result = []
        self._get_item_with_signature_by_user_id(
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

    def _acquire_item_set_by_user_id(
        self,
        request: AcquireItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[AcquireItemSetByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/acquire".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.acquire_count is not None:
            body["acquireCount"] = request.acquire_count
        if request.expires_at is not None:
            body["expiresAt"] = request.expires_at
        if request.create_new_item_set is not None:
            body["createNewItemSet"] = request.create_new_item_set
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireItemSetByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_item_set_by_user_id(
        self,
        request: AcquireItemSetByUserIdRequest,
    ) -> AcquireItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._acquire_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_item_set_by_user_id_async(
        self,
        request: AcquireItemSetByUserIdRequest,
    ) -> AcquireItemSetByUserIdResult:
        async_result = []
        self._acquire_item_set_by_user_id(
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

    def _acquire_item_set_with_grade_by_user_id(
        self,
        request: AcquireItemSetWithGradeByUserIdRequest,
        callback: Callable[[AsyncResult[AcquireItemSetWithGradeByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/acquire/grade".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.grade_model_id is not None:
            body["gradeModelId"] = request.grade_model_id
        if request.grade_value is not None:
            body["gradeValue"] = request.grade_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireItemSetWithGradeByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_item_set_with_grade_by_user_id(
        self,
        request: AcquireItemSetWithGradeByUserIdRequest,
    ) -> AcquireItemSetWithGradeByUserIdResult:
        async_result = []
        with timeout(30):
            self._acquire_item_set_with_grade_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_item_set_with_grade_by_user_id_async(
        self,
        request: AcquireItemSetWithGradeByUserIdRequest,
    ) -> AcquireItemSetWithGradeByUserIdResult:
        async_result = []
        self._acquire_item_set_with_grade_by_user_id(
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

    def _consume_item_set(
        self,
        request: ConsumeItemSetRequest,
        callback: Callable[[AsyncResult[ConsumeItemSetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}/consume".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.consume_count is not None:
            body["consumeCount"] = request.consume_count
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeItemSetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_item_set(
        self,
        request: ConsumeItemSetRequest,
    ) -> ConsumeItemSetResult:
        async_result = []
        with timeout(30):
            self._consume_item_set(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_item_set_async(
        self,
        request: ConsumeItemSetRequest,
    ) -> ConsumeItemSetResult:
        async_result = []
        self._consume_item_set(
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

    def _consume_item_set_by_user_id(
        self,
        request: ConsumeItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[ConsumeItemSetByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/consume".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.consume_count is not None:
            body["consumeCount"] = request.consume_count
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeItemSetByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_item_set_by_user_id(
        self,
        request: ConsumeItemSetByUserIdRequest,
    ) -> ConsumeItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._consume_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_item_set_by_user_id_async(
        self,
        request: ConsumeItemSetByUserIdRequest,
    ) -> ConsumeItemSetByUserIdResult:
        async_result = []
        self._consume_item_set_by_user_id(
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

    def _delete_item_set_by_user_id(
        self,
        request: DeleteItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteItemSetByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.item_set_name is not None:
            query_strings["itemSetName"] = request.item_set_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='DELETE',
            result_type=DeleteItemSetByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_item_set_by_user_id(
        self,
        request: DeleteItemSetByUserIdRequest,
    ) -> DeleteItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_item_set_by_user_id_async(
        self,
        request: DeleteItemSetByUserIdRequest,
    ) -> DeleteItemSetByUserIdResult:
        async_result = []
        self._delete_item_set_by_user_id(
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

    def _verify_item_set(
        self,
        request: VerifyItemSetRequest,
        callback: Callable[[AsyncResult[VerifyItemSetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.count is not None:
            body["count"] = request.count
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyItemSetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_item_set(
        self,
        request: VerifyItemSetRequest,
    ) -> VerifyItemSetResult:
        async_result = []
        with timeout(30):
            self._verify_item_set(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_item_set_async(
        self,
        request: VerifyItemSetRequest,
    ) -> VerifyItemSetResult:
        async_result = []
        self._verify_item_set(
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

    def _verify_item_set_by_user_id(
        self,
        request: VerifyItemSetByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyItemSetByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.item_set_name is not None:
            body["itemSetName"] = request.item_set_name
        if request.count is not None:
            body["count"] = request.count
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyItemSetByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_item_set_by_user_id(
        self,
        request: VerifyItemSetByUserIdRequest,
    ) -> VerifyItemSetByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_item_set_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_item_set_by_user_id_async(
        self,
        request: VerifyItemSetByUserIdRequest,
    ) -> VerifyItemSetByUserIdResult:
        async_result = []
        self._verify_item_set_by_user_id(
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

    def _acquire_item_set_by_stamp_sheet(
        self,
        request: AcquireItemSetByStampSheetRequest,
        callback: Callable[[AsyncResult[AcquireItemSetByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/item/acquire"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireItemSetByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_item_set_by_stamp_sheet(
        self,
        request: AcquireItemSetByStampSheetRequest,
    ) -> AcquireItemSetByStampSheetResult:
        async_result = []
        with timeout(30):
            self._acquire_item_set_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_item_set_by_stamp_sheet_async(
        self,
        request: AcquireItemSetByStampSheetRequest,
    ) -> AcquireItemSetByStampSheetResult:
        async_result = []
        self._acquire_item_set_by_stamp_sheet(
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

    def _acquire_item_set_with_grade_by_stamp_sheet(
        self,
        request: AcquireItemSetWithGradeByStampSheetRequest,
        callback: Callable[[AsyncResult[AcquireItemSetWithGradeByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/item/acquire/grade"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireItemSetWithGradeByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_item_set_with_grade_by_stamp_sheet(
        self,
        request: AcquireItemSetWithGradeByStampSheetRequest,
    ) -> AcquireItemSetWithGradeByStampSheetResult:
        async_result = []
        with timeout(30):
            self._acquire_item_set_with_grade_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_item_set_with_grade_by_stamp_sheet_async(
        self,
        request: AcquireItemSetWithGradeByStampSheetRequest,
    ) -> AcquireItemSetWithGradeByStampSheetResult:
        async_result = []
        self._acquire_item_set_with_grade_by_stamp_sheet(
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

    def _consume_item_set_by_stamp_task(
        self,
        request: ConsumeItemSetByStampTaskRequest,
        callback: Callable[[AsyncResult[ConsumeItemSetByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/item/consume"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeItemSetByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_item_set_by_stamp_task(
        self,
        request: ConsumeItemSetByStampTaskRequest,
    ) -> ConsumeItemSetByStampTaskResult:
        async_result = []
        with timeout(30):
            self._consume_item_set_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_item_set_by_stamp_task_async(
        self,
        request: ConsumeItemSetByStampTaskRequest,
    ) -> ConsumeItemSetByStampTaskResult:
        async_result = []
        self._consume_item_set_by_stamp_task(
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

    def _verify_item_set_by_stamp_task(
        self,
        request: VerifyItemSetByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyItemSetByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/item/verify"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyItemSetByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_item_set_by_stamp_task(
        self,
        request: VerifyItemSetByStampTaskRequest,
    ) -> VerifyItemSetByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_item_set_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_item_set_by_stamp_task_async(
        self,
        request: VerifyItemSetByStampTaskRequest,
    ) -> VerifyItemSetByStampTaskResult:
        async_result = []
        self._verify_item_set_by_stamp_task(
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

    def _describe_reference_of(
        self,
        request: DescribeReferenceOfRequest,
        callback: Callable[[AsyncResult[DescribeReferenceOfResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
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
            result_type=DescribeReferenceOfResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_reference_of(
        self,
        request: DescribeReferenceOfRequest,
    ) -> DescribeReferenceOfResult:
        async_result = []
        with timeout(30):
            self._describe_reference_of(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_reference_of_async(
        self,
        request: DescribeReferenceOfRequest,
    ) -> DescribeReferenceOfResult:
        async_result = []
        self._describe_reference_of(
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

    def _describe_reference_of_by_user_id(
        self,
        request: DescribeReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeReferenceOfByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
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
            result_type=DescribeReferenceOfByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_reference_of_by_user_id(
        self,
        request: DescribeReferenceOfByUserIdRequest,
    ) -> DescribeReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_reference_of_by_user_id_async(
        self,
        request: DescribeReferenceOfByUserIdRequest,
    ) -> DescribeReferenceOfByUserIdResult:
        async_result = []
        self._describe_reference_of_by_user_id(
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

    def _get_reference_of(
        self,
        request: GetReferenceOfRequest,
        callback: Callable[[AsyncResult[GetReferenceOfResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference/{referenceOf}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
            referenceOf=request.reference_of if request.reference_of is not None and request.reference_of != '' else 'null',
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
            result_type=GetReferenceOfResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_reference_of(
        self,
        request: GetReferenceOfRequest,
    ) -> GetReferenceOfResult:
        async_result = []
        with timeout(30):
            self._get_reference_of(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_reference_of_async(
        self,
        request: GetReferenceOfRequest,
    ) -> GetReferenceOfResult:
        async_result = []
        self._get_reference_of(
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

    def _get_reference_of_by_user_id(
        self,
        request: GetReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[GetReferenceOfByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference/{referenceOf}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
            referenceOf=request.reference_of if request.reference_of is not None and request.reference_of != '' else 'null',
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
            result_type=GetReferenceOfByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_reference_of_by_user_id(
        self,
        request: GetReferenceOfByUserIdRequest,
    ) -> GetReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_reference_of_by_user_id_async(
        self,
        request: GetReferenceOfByUserIdRequest,
    ) -> GetReferenceOfByUserIdResult:
        async_result = []
        self._get_reference_of_by_user_id(
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

    def _verify_reference_of(
        self,
        request: VerifyReferenceOfRequest,
        callback: Callable[[AsyncResult[VerifyReferenceOfResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference/{referenceOf}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
            referenceOf=request.reference_of if request.reference_of is not None and request.reference_of != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
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
            method='POST',
            result_type=VerifyReferenceOfResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_reference_of(
        self,
        request: VerifyReferenceOfRequest,
    ) -> VerifyReferenceOfResult:
        async_result = []
        with timeout(30):
            self._verify_reference_of(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_reference_of_async(
        self,
        request: VerifyReferenceOfRequest,
    ) -> VerifyReferenceOfResult:
        async_result = []
        self._verify_reference_of(
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

    def _verify_reference_of_by_user_id(
        self,
        request: VerifyReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyReferenceOfByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference/{referenceOf}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
            referenceOf=request.reference_of if request.reference_of is not None and request.reference_of != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
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
            method='POST',
            result_type=VerifyReferenceOfByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_reference_of_by_user_id(
        self,
        request: VerifyReferenceOfByUserIdRequest,
    ) -> VerifyReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_reference_of_by_user_id_async(
        self,
        request: VerifyReferenceOfByUserIdRequest,
    ) -> VerifyReferenceOfByUserIdResult:
        async_result = []
        self._verify_reference_of_by_user_id(
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

    def _add_reference_of(
        self,
        request: AddReferenceOfRequest,
        callback: Callable[[AsyncResult[AddReferenceOfResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AddReferenceOfResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def add_reference_of(
        self,
        request: AddReferenceOfRequest,
    ) -> AddReferenceOfResult:
        async_result = []
        with timeout(30):
            self._add_reference_of(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_reference_of_async(
        self,
        request: AddReferenceOfRequest,
    ) -> AddReferenceOfResult:
        async_result = []
        self._add_reference_of(
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

    def _add_reference_of_by_user_id(
        self,
        request: AddReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[AddReferenceOfByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.reference_of is not None:
            body["referenceOf"] = request.reference_of

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AddReferenceOfByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def add_reference_of_by_user_id(
        self,
        request: AddReferenceOfByUserIdRequest,
    ) -> AddReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._add_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_reference_of_by_user_id_async(
        self,
        request: AddReferenceOfByUserIdRequest,
    ) -> AddReferenceOfByUserIdResult:
        async_result = []
        self._add_reference_of_by_user_id(
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

    def _delete_reference_of(
        self,
        request: DeleteReferenceOfRequest,
        callback: Callable[[AsyncResult[DeleteReferenceOfResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference/{referenceOf}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
            referenceOf=request.reference_of if request.reference_of is not None and request.reference_of != '' else 'null',
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
            result_type=DeleteReferenceOfResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_reference_of(
        self,
        request: DeleteReferenceOfRequest,
    ) -> DeleteReferenceOfResult:
        async_result = []
        with timeout(30):
            self._delete_reference_of(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_reference_of_async(
        self,
        request: DeleteReferenceOfRequest,
    ) -> DeleteReferenceOfResult:
        async_result = []
        self._delete_reference_of(
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

    def _delete_reference_of_by_user_id(
        self,
        request: DeleteReferenceOfByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteReferenceOfByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/inventory/{inventoryName}/item/{itemName}/{itemSetName}/reference/{referenceOf}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            itemSetName=request.item_set_name if request.item_set_name is not None and request.item_set_name != '' else 'null',
            referenceOf=request.reference_of if request.reference_of is not None and request.reference_of != '' else 'null',
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
            result_type=DeleteReferenceOfByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_reference_of_by_user_id(
        self,
        request: DeleteReferenceOfByUserIdRequest,
    ) -> DeleteReferenceOfByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_reference_of_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_reference_of_by_user_id_async(
        self,
        request: DeleteReferenceOfByUserIdRequest,
    ) -> DeleteReferenceOfByUserIdResult:
        async_result = []
        self._delete_reference_of_by_user_id(
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

    def _add_reference_of_item_set_by_stamp_sheet(
        self,
        request: AddReferenceOfItemSetByStampSheetRequest,
        callback: Callable[[AsyncResult[AddReferenceOfItemSetByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/item/reference/add"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AddReferenceOfItemSetByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def add_reference_of_item_set_by_stamp_sheet(
        self,
        request: AddReferenceOfItemSetByStampSheetRequest,
    ) -> AddReferenceOfItemSetByStampSheetResult:
        async_result = []
        with timeout(30):
            self._add_reference_of_item_set_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def add_reference_of_item_set_by_stamp_sheet_async(
        self,
        request: AddReferenceOfItemSetByStampSheetRequest,
    ) -> AddReferenceOfItemSetByStampSheetResult:
        async_result = []
        self._add_reference_of_item_set_by_stamp_sheet(
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

    def _delete_reference_of_item_set_by_stamp_sheet(
        self,
        request: DeleteReferenceOfItemSetByStampSheetRequest,
        callback: Callable[[AsyncResult[DeleteReferenceOfItemSetByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/item/reference/delete"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=DeleteReferenceOfItemSetByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_reference_of_item_set_by_stamp_sheet(
        self,
        request: DeleteReferenceOfItemSetByStampSheetRequest,
    ) -> DeleteReferenceOfItemSetByStampSheetResult:
        async_result = []
        with timeout(30):
            self._delete_reference_of_item_set_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_reference_of_item_set_by_stamp_sheet_async(
        self,
        request: DeleteReferenceOfItemSetByStampSheetRequest,
    ) -> DeleteReferenceOfItemSetByStampSheetResult:
        async_result = []
        self._delete_reference_of_item_set_by_stamp_sheet(
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

    def _verify_reference_of_by_stamp_task(
        self,
        request: VerifyReferenceOfByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyReferenceOfByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/item/reference/verify"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyReferenceOfByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_reference_of_by_stamp_task(
        self,
        request: VerifyReferenceOfByStampTaskRequest,
    ) -> VerifyReferenceOfByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_reference_of_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_reference_of_by_stamp_task_async(
        self,
        request: VerifyReferenceOfByStampTaskRequest,
    ) -> VerifyReferenceOfByStampTaskResult:
        async_result = []
        self._verify_reference_of_by_stamp_task(
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

    def _describe_simple_items(
        self,
        request: DescribeSimpleItemsRequest,
        callback: Callable[[AsyncResult[DescribeSimpleItemsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/simple/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeSimpleItemsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_simple_items(
        self,
        request: DescribeSimpleItemsRequest,
    ) -> DescribeSimpleItemsResult:
        async_result = []
        with timeout(30):
            self._describe_simple_items(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_simple_items_async(
        self,
        request: DescribeSimpleItemsRequest,
    ) -> DescribeSimpleItemsResult:
        async_result = []
        self._describe_simple_items(
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

    def _describe_simple_items_by_user_id(
        self,
        request: DescribeSimpleItemsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeSimpleItemsByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/simple/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeSimpleItemsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_simple_items_by_user_id(
        self,
        request: DescribeSimpleItemsByUserIdRequest,
    ) -> DescribeSimpleItemsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_simple_items_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_simple_items_by_user_id_async(
        self,
        request: DescribeSimpleItemsByUserIdRequest,
    ) -> DescribeSimpleItemsByUserIdResult:
        async_result = []
        self._describe_simple_items_by_user_id(
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

    def _get_simple_item(
        self,
        request: GetSimpleItemRequest,
        callback: Callable[[AsyncResult[GetSimpleItemResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/simple/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetSimpleItemResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_simple_item(
        self,
        request: GetSimpleItemRequest,
    ) -> GetSimpleItemResult:
        async_result = []
        with timeout(30):
            self._get_simple_item(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_simple_item_async(
        self,
        request: GetSimpleItemRequest,
    ) -> GetSimpleItemResult:
        async_result = []
        self._get_simple_item(
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

    def _get_simple_item_by_user_id(
        self,
        request: GetSimpleItemByUserIdRequest,
        callback: Callable[[AsyncResult[GetSimpleItemByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/simple/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetSimpleItemByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_simple_item_by_user_id(
        self,
        request: GetSimpleItemByUserIdRequest,
    ) -> GetSimpleItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_simple_item_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_simple_item_by_user_id_async(
        self,
        request: GetSimpleItemByUserIdRequest,
    ) -> GetSimpleItemByUserIdResult:
        async_result = []
        self._get_simple_item_by_user_id(
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

    def _get_simple_item_with_signature(
        self,
        request: GetSimpleItemWithSignatureRequest,
        callback: Callable[[AsyncResult[GetSimpleItemWithSignatureResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/simple/inventory/{inventoryName}/item/{itemName}/signature".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.key_id is not None:
            query_strings["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSimpleItemWithSignatureResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_simple_item_with_signature(
        self,
        request: GetSimpleItemWithSignatureRequest,
    ) -> GetSimpleItemWithSignatureResult:
        async_result = []
        with timeout(30):
            self._get_simple_item_with_signature(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_simple_item_with_signature_async(
        self,
        request: GetSimpleItemWithSignatureRequest,
    ) -> GetSimpleItemWithSignatureResult:
        async_result = []
        self._get_simple_item_with_signature(
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

    def _get_simple_item_with_signature_by_user_id(
        self,
        request: GetSimpleItemWithSignatureByUserIdRequest,
        callback: Callable[[AsyncResult[GetSimpleItemWithSignatureByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/simple/inventory/{inventoryName}/item/{itemName}/signature".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        query_strings = {
            'contextStack': request.context_stack,
        }
        if request.key_id is not None:
            query_strings["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='GET',
            result_type=GetSimpleItemWithSignatureByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_simple_item_with_signature_by_user_id(
        self,
        request: GetSimpleItemWithSignatureByUserIdRequest,
    ) -> GetSimpleItemWithSignatureByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_simple_item_with_signature_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_simple_item_with_signature_by_user_id_async(
        self,
        request: GetSimpleItemWithSignatureByUserIdRequest,
    ) -> GetSimpleItemWithSignatureByUserIdResult:
        async_result = []
        self._get_simple_item_with_signature_by_user_id(
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

    def _acquire_simple_items_by_user_id(
        self,
        request: AcquireSimpleItemsByUserIdRequest,
        callback: Callable[[AsyncResult[AcquireSimpleItemsByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/simple/inventory/{inventoryName}/acquire".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.acquire_counts is not None:
            body["acquireCounts"] = [
                item.to_dict()
                for item in request.acquire_counts
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
            result_type=AcquireSimpleItemsByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_simple_items_by_user_id(
        self,
        request: AcquireSimpleItemsByUserIdRequest,
    ) -> AcquireSimpleItemsByUserIdResult:
        async_result = []
        with timeout(30):
            self._acquire_simple_items_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_simple_items_by_user_id_async(
        self,
        request: AcquireSimpleItemsByUserIdRequest,
    ) -> AcquireSimpleItemsByUserIdResult:
        async_result = []
        self._acquire_simple_items_by_user_id(
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

    def _consume_simple_items(
        self,
        request: ConsumeSimpleItemsRequest,
        callback: Callable[[AsyncResult[ConsumeSimpleItemsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/simple/inventory/{inventoryName}/consume".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.consume_counts is not None:
            body["consumeCounts"] = [
                item.to_dict()
                for item in request.consume_counts
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
            result_type=ConsumeSimpleItemsResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_simple_items(
        self,
        request: ConsumeSimpleItemsRequest,
    ) -> ConsumeSimpleItemsResult:
        async_result = []
        with timeout(30):
            self._consume_simple_items(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_simple_items_async(
        self,
        request: ConsumeSimpleItemsRequest,
    ) -> ConsumeSimpleItemsResult:
        async_result = []
        self._consume_simple_items(
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

    def _consume_simple_items_by_user_id(
        self,
        request: ConsumeSimpleItemsByUserIdRequest,
        callback: Callable[[AsyncResult[ConsumeSimpleItemsByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/simple/inventory/{inventoryName}/consume".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.consume_counts is not None:
            body["consumeCounts"] = [
                item.to_dict()
                for item in request.consume_counts
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
            result_type=ConsumeSimpleItemsByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_simple_items_by_user_id(
        self,
        request: ConsumeSimpleItemsByUserIdRequest,
    ) -> ConsumeSimpleItemsByUserIdResult:
        async_result = []
        with timeout(30):
            self._consume_simple_items_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_simple_items_by_user_id_async(
        self,
        request: ConsumeSimpleItemsByUserIdRequest,
    ) -> ConsumeSimpleItemsByUserIdResult:
        async_result = []
        self._consume_simple_items_by_user_id(
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

    def _set_simple_items_by_user_id(
        self,
        request: SetSimpleItemsByUserIdRequest,
        callback: Callable[[AsyncResult[SetSimpleItemsByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/simple/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.counts is not None:
            body["counts"] = [
                item.to_dict()
                for item in request.counts
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=SetSimpleItemsByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_simple_items_by_user_id(
        self,
        request: SetSimpleItemsByUserIdRequest,
    ) -> SetSimpleItemsByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_simple_items_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_simple_items_by_user_id_async(
        self,
        request: SetSimpleItemsByUserIdRequest,
    ) -> SetSimpleItemsByUserIdResult:
        async_result = []
        self._set_simple_items_by_user_id(
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

    def _delete_simple_items_by_user_id(
        self,
        request: DeleteSimpleItemsByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteSimpleItemsByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/simple/inventory/{inventoryName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DeleteSimpleItemsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_simple_items_by_user_id(
        self,
        request: DeleteSimpleItemsByUserIdRequest,
    ) -> DeleteSimpleItemsByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_simple_items_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_simple_items_by_user_id_async(
        self,
        request: DeleteSimpleItemsByUserIdRequest,
    ) -> DeleteSimpleItemsByUserIdResult:
        async_result = []
        self._delete_simple_items_by_user_id(
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

    def _verify_simple_item(
        self,
        request: VerifySimpleItemRequest,
        callback: Callable[[AsyncResult[VerifySimpleItemResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/simple/inventory/{inventoryName}/item/{itemName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.count is not None:
            body["count"] = request.count
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifySimpleItemResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_simple_item(
        self,
        request: VerifySimpleItemRequest,
    ) -> VerifySimpleItemResult:
        async_result = []
        with timeout(30):
            self._verify_simple_item(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_simple_item_async(
        self,
        request: VerifySimpleItemRequest,
    ) -> VerifySimpleItemResult:
        async_result = []
        self._verify_simple_item(
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

    def _verify_simple_item_by_user_id(
        self,
        request: VerifySimpleItemByUserIdRequest,
        callback: Callable[[AsyncResult[VerifySimpleItemByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/simple/inventory/{inventoryName}/item/{itemName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.count is not None:
            body["count"] = request.count
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifySimpleItemByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_simple_item_by_user_id(
        self,
        request: VerifySimpleItemByUserIdRequest,
    ) -> VerifySimpleItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_simple_item_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_simple_item_by_user_id_async(
        self,
        request: VerifySimpleItemByUserIdRequest,
    ) -> VerifySimpleItemByUserIdResult:
        async_result = []
        self._verify_simple_item_by_user_id(
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

    def _acquire_simple_items_by_stamp_sheet(
        self,
        request: AcquireSimpleItemsByStampSheetRequest,
        callback: Callable[[AsyncResult[AcquireSimpleItemsByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/simple/item/acquire"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireSimpleItemsByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_simple_items_by_stamp_sheet(
        self,
        request: AcquireSimpleItemsByStampSheetRequest,
    ) -> AcquireSimpleItemsByStampSheetResult:
        async_result = []
        with timeout(30):
            self._acquire_simple_items_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_simple_items_by_stamp_sheet_async(
        self,
        request: AcquireSimpleItemsByStampSheetRequest,
    ) -> AcquireSimpleItemsByStampSheetResult:
        async_result = []
        self._acquire_simple_items_by_stamp_sheet(
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

    def _consume_simple_items_by_stamp_task(
        self,
        request: ConsumeSimpleItemsByStampTaskRequest,
        callback: Callable[[AsyncResult[ConsumeSimpleItemsByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/simple/item/consume"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeSimpleItemsByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_simple_items_by_stamp_task(
        self,
        request: ConsumeSimpleItemsByStampTaskRequest,
    ) -> ConsumeSimpleItemsByStampTaskResult:
        async_result = []
        with timeout(30):
            self._consume_simple_items_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_simple_items_by_stamp_task_async(
        self,
        request: ConsumeSimpleItemsByStampTaskRequest,
    ) -> ConsumeSimpleItemsByStampTaskResult:
        async_result = []
        self._consume_simple_items_by_stamp_task(
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

    def _set_simple_items_by_stamp_sheet(
        self,
        request: SetSimpleItemsByStampSheetRequest,
        callback: Callable[[AsyncResult[SetSimpleItemsByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/simple/item/set"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetSimpleItemsByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_simple_items_by_stamp_sheet(
        self,
        request: SetSimpleItemsByStampSheetRequest,
    ) -> SetSimpleItemsByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_simple_items_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_simple_items_by_stamp_sheet_async(
        self,
        request: SetSimpleItemsByStampSheetRequest,
    ) -> SetSimpleItemsByStampSheetResult:
        async_result = []
        self._set_simple_items_by_stamp_sheet(
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

    def _verify_simple_item_by_stamp_task(
        self,
        request: VerifySimpleItemByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifySimpleItemByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/simple/item/verify"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifySimpleItemByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_simple_item_by_stamp_task(
        self,
        request: VerifySimpleItemByStampTaskRequest,
    ) -> VerifySimpleItemByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_simple_item_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_simple_item_by_stamp_task_async(
        self,
        request: VerifySimpleItemByStampTaskRequest,
    ) -> VerifySimpleItemByStampTaskResult:
        async_result = []
        self._verify_simple_item_by_stamp_task(
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

    def _describe_big_items(
        self,
        request: DescribeBigItemsRequest,
        callback: Callable[[AsyncResult[DescribeBigItemsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/big/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeBigItemsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_big_items(
        self,
        request: DescribeBigItemsRequest,
    ) -> DescribeBigItemsResult:
        async_result = []
        with timeout(30):
            self._describe_big_items(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_big_items_async(
        self,
        request: DescribeBigItemsRequest,
    ) -> DescribeBigItemsResult:
        async_result = []
        self._describe_big_items(
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

    def _describe_big_items_by_user_id(
        self,
        request: DescribeBigItemsByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeBigItemsByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/big/inventory/{inventoryName}/item".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
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
            result_type=DescribeBigItemsByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_big_items_by_user_id(
        self,
        request: DescribeBigItemsByUserIdRequest,
    ) -> DescribeBigItemsByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_big_items_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_big_items_by_user_id_async(
        self,
        request: DescribeBigItemsByUserIdRequest,
    ) -> DescribeBigItemsByUserIdResult:
        async_result = []
        self._describe_big_items_by_user_id(
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

    def _get_big_item(
        self,
        request: GetBigItemRequest,
        callback: Callable[[AsyncResult[GetBigItemResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/big/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetBigItemResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_big_item(
        self,
        request: GetBigItemRequest,
    ) -> GetBigItemResult:
        async_result = []
        with timeout(30):
            self._get_big_item(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_big_item_async(
        self,
        request: GetBigItemRequest,
    ) -> GetBigItemResult:
        async_result = []
        self._get_big_item(
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

    def _get_big_item_by_user_id(
        self,
        request: GetBigItemByUserIdRequest,
        callback: Callable[[AsyncResult[GetBigItemByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/big/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=GetBigItemByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_big_item_by_user_id(
        self,
        request: GetBigItemByUserIdRequest,
    ) -> GetBigItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_big_item_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_big_item_by_user_id_async(
        self,
        request: GetBigItemByUserIdRequest,
    ) -> GetBigItemByUserIdResult:
        async_result = []
        self._get_big_item_by_user_id(
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

    def _acquire_big_item_by_user_id(
        self,
        request: AcquireBigItemByUserIdRequest,
        callback: Callable[[AsyncResult[AcquireBigItemByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/big/inventory/{inventoryName}/item/{itemName}/acquire".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.acquire_count is not None:
            body["acquireCount"] = request.acquire_count

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireBigItemByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_big_item_by_user_id(
        self,
        request: AcquireBigItemByUserIdRequest,
    ) -> AcquireBigItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._acquire_big_item_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_big_item_by_user_id_async(
        self,
        request: AcquireBigItemByUserIdRequest,
    ) -> AcquireBigItemByUserIdResult:
        async_result = []
        self._acquire_big_item_by_user_id(
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

    def _consume_big_item(
        self,
        request: ConsumeBigItemRequest,
        callback: Callable[[AsyncResult[ConsumeBigItemResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/big/inventory/{inventoryName}/item/{itemName}/consume".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.consume_count is not None:
            body["consumeCount"] = request.consume_count

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeBigItemResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_big_item(
        self,
        request: ConsumeBigItemRequest,
    ) -> ConsumeBigItemResult:
        async_result = []
        with timeout(30):
            self._consume_big_item(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_big_item_async(
        self,
        request: ConsumeBigItemRequest,
    ) -> ConsumeBigItemResult:
        async_result = []
        self._consume_big_item(
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

    def _consume_big_item_by_user_id(
        self,
        request: ConsumeBigItemByUserIdRequest,
        callback: Callable[[AsyncResult[ConsumeBigItemByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/big/inventory/{inventoryName}/item/{itemName}/consume".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.consume_count is not None:
            body["consumeCount"] = request.consume_count

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeBigItemByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_big_item_by_user_id(
        self,
        request: ConsumeBigItemByUserIdRequest,
    ) -> ConsumeBigItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._consume_big_item_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_big_item_by_user_id_async(
        self,
        request: ConsumeBigItemByUserIdRequest,
    ) -> ConsumeBigItemByUserIdResult:
        async_result = []
        self._consume_big_item_by_user_id(
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

    def _set_big_item_by_user_id(
        self,
        request: SetBigItemByUserIdRequest,
        callback: Callable[[AsyncResult[SetBigItemByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/big/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.count is not None:
            body["count"] = request.count

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=SetBigItemByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_big_item_by_user_id(
        self,
        request: SetBigItemByUserIdRequest,
    ) -> SetBigItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_big_item_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_big_item_by_user_id_async(
        self,
        request: SetBigItemByUserIdRequest,
    ) -> SetBigItemByUserIdResult:
        async_result = []
        self._set_big_item_by_user_id(
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

    def _delete_big_item_by_user_id(
        self,
        request: DeleteBigItemByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteBigItemByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/big/inventory/{inventoryName}/item/{itemName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
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
            result_type=DeleteBigItemByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_big_item_by_user_id(
        self,
        request: DeleteBigItemByUserIdRequest,
    ) -> DeleteBigItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_big_item_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_big_item_by_user_id_async(
        self,
        request: DeleteBigItemByUserIdRequest,
    ) -> DeleteBigItemByUserIdResult:
        async_result = []
        self._delete_big_item_by_user_id(
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

    def _verify_big_item(
        self,
        request: VerifyBigItemRequest,
        callback: Callable[[AsyncResult[VerifyBigItemResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/big/inventory/{inventoryName}/item/{itemName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.count is not None:
            body["count"] = request.count
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyBigItemResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_big_item(
        self,
        request: VerifyBigItemRequest,
    ) -> VerifyBigItemResult:
        async_result = []
        with timeout(30):
            self._verify_big_item(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_big_item_async(
        self,
        request: VerifyBigItemRequest,
    ) -> VerifyBigItemResult:
        async_result = []
        self._verify_big_item(
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

    def _verify_big_item_by_user_id(
        self,
        request: VerifyBigItemByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyBigItemByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/big/inventory/{inventoryName}/item/{itemName}/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            inventoryName=request.inventory_name if request.inventory_name is not None and request.inventory_name != '' else 'null',
            itemName=request.item_name if request.item_name is not None and request.item_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.count is not None:
            body["count"] = request.count
        if request.multiply_value_specifying_quantity is not None:
            body["multiplyValueSpecifyingQuantity"] = request.multiply_value_specifying_quantity

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyBigItemByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_big_item_by_user_id(
        self,
        request: VerifyBigItemByUserIdRequest,
    ) -> VerifyBigItemByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_big_item_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_big_item_by_user_id_async(
        self,
        request: VerifyBigItemByUserIdRequest,
    ) -> VerifyBigItemByUserIdResult:
        async_result = []
        self._verify_big_item_by_user_id(
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

    def _acquire_big_item_by_stamp_sheet(
        self,
        request: AcquireBigItemByStampSheetRequest,
        callback: Callable[[AsyncResult[AcquireBigItemByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/big/item/acquire"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=AcquireBigItemByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def acquire_big_item_by_stamp_sheet(
        self,
        request: AcquireBigItemByStampSheetRequest,
    ) -> AcquireBigItemByStampSheetResult:
        async_result = []
        with timeout(30):
            self._acquire_big_item_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def acquire_big_item_by_stamp_sheet_async(
        self,
        request: AcquireBigItemByStampSheetRequest,
    ) -> AcquireBigItemByStampSheetResult:
        async_result = []
        self._acquire_big_item_by_stamp_sheet(
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

    def _consume_big_item_by_stamp_task(
        self,
        request: ConsumeBigItemByStampTaskRequest,
        callback: Callable[[AsyncResult[ConsumeBigItemByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/big/item/consume"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeBigItemByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_big_item_by_stamp_task(
        self,
        request: ConsumeBigItemByStampTaskRequest,
    ) -> ConsumeBigItemByStampTaskResult:
        async_result = []
        with timeout(30):
            self._consume_big_item_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_big_item_by_stamp_task_async(
        self,
        request: ConsumeBigItemByStampTaskRequest,
    ) -> ConsumeBigItemByStampTaskResult:
        async_result = []
        self._consume_big_item_by_stamp_task(
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

    def _set_big_item_by_stamp_sheet(
        self,
        request: SetBigItemByStampSheetRequest,
        callback: Callable[[AsyncResult[SetBigItemByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/big/item/set"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_sheet is not None:
            body["stampSheet"] = request.stamp_sheet
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetBigItemByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_big_item_by_stamp_sheet(
        self,
        request: SetBigItemByStampSheetRequest,
    ) -> SetBigItemByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_big_item_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_big_item_by_stamp_sheet_async(
        self,
        request: SetBigItemByStampSheetRequest,
    ) -> SetBigItemByStampSheetResult:
        async_result = []
        self._set_big_item_by_stamp_sheet(
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

    def _verify_big_item_by_stamp_task(
        self,
        request: VerifyBigItemByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyBigItemByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='inventory',
            region=self.session.region,
        ) + "/stamp/big/item/verify"

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.stamp_task is not None:
            body["stampTask"] = request.stamp_task
        if request.key_id is not None:
            body["keyId"] = request.key_id

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=VerifyBigItemByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_big_item_by_stamp_task(
        self,
        request: VerifyBigItemByStampTaskRequest,
    ) -> VerifyBigItemByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_big_item_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_big_item_by_stamp_task_async(
        self,
        request: VerifyBigItemByStampTaskRequest,
    ) -> VerifyBigItemByStampTaskResult:
        async_result = []
        self._verify_big_item_by_stamp_task(
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