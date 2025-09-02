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


class Gs2StaminaRestClient(rest.AbstractGs2RestClient):

    def _describe_namespaces(
        self,
        request: DescribeNamespacesRequest,
        callback: Callable[[AsyncResult[DescribeNamespacesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
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
            service='stamina',
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
        if request.overflow_trigger_script is not None:
            body["overflowTriggerScript"] = request.overflow_trigger_script
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
            service='stamina',
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
            service='stamina',
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
            service='stamina',
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
        if request.overflow_trigger_script is not None:
            body["overflowTriggerScript"] = request.overflow_trigger_script
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
            service='stamina',
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
            service='stamina',
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
            service='stamina',
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
            service='stamina',
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
            service='stamina',
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
            service='stamina',
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
            service='stamina',
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
            service='stamina',
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
            service='stamina',
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

    def _describe_stamina_model_masters(
        self,
        request: DescribeStaminaModelMastersRequest,
        callback: Callable[[AsyncResult[DescribeStaminaModelMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
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
            result_type=DescribeStaminaModelMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_stamina_model_masters(
        self,
        request: DescribeStaminaModelMastersRequest,
    ) -> DescribeStaminaModelMastersResult:
        async_result = []
        with timeout(30):
            self._describe_stamina_model_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_stamina_model_masters_async(
        self,
        request: DescribeStaminaModelMastersRequest,
    ) -> DescribeStaminaModelMastersResult:
        async_result = []
        self._describe_stamina_model_masters(
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

    def _create_stamina_model_master(
        self,
        request: CreateStaminaModelMasterRequest,
        callback: Callable[[AsyncResult[CreateStaminaModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/model".format(
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
        if request.recover_interval_minutes is not None:
            body["recoverIntervalMinutes"] = request.recover_interval_minutes
        if request.recover_value is not None:
            body["recoverValue"] = request.recover_value
        if request.initial_capacity is not None:
            body["initialCapacity"] = request.initial_capacity
        if request.is_overflow is not None:
            body["isOverflow"] = request.is_overflow
        if request.max_capacity is not None:
            body["maxCapacity"] = request.max_capacity
        if request.max_stamina_table_name is not None:
            body["maxStaminaTableName"] = request.max_stamina_table_name
        if request.recover_interval_table_name is not None:
            body["recoverIntervalTableName"] = request.recover_interval_table_name
        if request.recover_value_table_name is not None:
            body["recoverValueTableName"] = request.recover_value_table_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateStaminaModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_stamina_model_master(
        self,
        request: CreateStaminaModelMasterRequest,
    ) -> CreateStaminaModelMasterResult:
        async_result = []
        with timeout(30):
            self._create_stamina_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_stamina_model_master_async(
        self,
        request: CreateStaminaModelMasterRequest,
    ) -> CreateStaminaModelMasterResult:
        async_result = []
        self._create_stamina_model_master(
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

    def _get_stamina_model_master(
        self,
        request: GetStaminaModelMasterRequest,
        callback: Callable[[AsyncResult[GetStaminaModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{staminaName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
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
            result_type=GetStaminaModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_stamina_model_master(
        self,
        request: GetStaminaModelMasterRequest,
    ) -> GetStaminaModelMasterResult:
        async_result = []
        with timeout(30):
            self._get_stamina_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stamina_model_master_async(
        self,
        request: GetStaminaModelMasterRequest,
    ) -> GetStaminaModelMasterResult:
        async_result = []
        self._get_stamina_model_master(
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

    def _update_stamina_model_master(
        self,
        request: UpdateStaminaModelMasterRequest,
        callback: Callable[[AsyncResult[UpdateStaminaModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{staminaName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.recover_interval_minutes is not None:
            body["recoverIntervalMinutes"] = request.recover_interval_minutes
        if request.recover_value is not None:
            body["recoverValue"] = request.recover_value
        if request.initial_capacity is not None:
            body["initialCapacity"] = request.initial_capacity
        if request.is_overflow is not None:
            body["isOverflow"] = request.is_overflow
        if request.max_capacity is not None:
            body["maxCapacity"] = request.max_capacity
        if request.max_stamina_table_name is not None:
            body["maxStaminaTableName"] = request.max_stamina_table_name
        if request.recover_interval_table_name is not None:
            body["recoverIntervalTableName"] = request.recover_interval_table_name
        if request.recover_value_table_name is not None:
            body["recoverValueTableName"] = request.recover_value_table_name

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateStaminaModelMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_stamina_model_master(
        self,
        request: UpdateStaminaModelMasterRequest,
    ) -> UpdateStaminaModelMasterResult:
        async_result = []
        with timeout(30):
            self._update_stamina_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_stamina_model_master_async(
        self,
        request: UpdateStaminaModelMasterRequest,
    ) -> UpdateStaminaModelMasterResult:
        async_result = []
        self._update_stamina_model_master(
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

    def _delete_stamina_model_master(
        self,
        request: DeleteStaminaModelMasterRequest,
        callback: Callable[[AsyncResult[DeleteStaminaModelMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/model/{staminaName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
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
            result_type=DeleteStaminaModelMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_stamina_model_master(
        self,
        request: DeleteStaminaModelMasterRequest,
    ) -> DeleteStaminaModelMasterResult:
        async_result = []
        with timeout(30):
            self._delete_stamina_model_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_stamina_model_master_async(
        self,
        request: DeleteStaminaModelMasterRequest,
    ) -> DeleteStaminaModelMasterResult:
        async_result = []
        self._delete_stamina_model_master(
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

    def _describe_max_stamina_table_masters(
        self,
        request: DescribeMaxStaminaTableMastersRequest,
        callback: Callable[[AsyncResult[DescribeMaxStaminaTableMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/maxStaminaTable".format(
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
            result_type=DescribeMaxStaminaTableMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_max_stamina_table_masters(
        self,
        request: DescribeMaxStaminaTableMastersRequest,
    ) -> DescribeMaxStaminaTableMastersResult:
        async_result = []
        with timeout(30):
            self._describe_max_stamina_table_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_max_stamina_table_masters_async(
        self,
        request: DescribeMaxStaminaTableMastersRequest,
    ) -> DescribeMaxStaminaTableMastersResult:
        async_result = []
        self._describe_max_stamina_table_masters(
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

    def _create_max_stamina_table_master(
        self,
        request: CreateMaxStaminaTableMasterRequest,
        callback: Callable[[AsyncResult[CreateMaxStaminaTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/maxStaminaTable".format(
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
        if request.experience_model_id is not None:
            body["experienceModelId"] = request.experience_model_id
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateMaxStaminaTableMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_max_stamina_table_master(
        self,
        request: CreateMaxStaminaTableMasterRequest,
    ) -> CreateMaxStaminaTableMasterResult:
        async_result = []
        with timeout(30):
            self._create_max_stamina_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_max_stamina_table_master_async(
        self,
        request: CreateMaxStaminaTableMasterRequest,
    ) -> CreateMaxStaminaTableMasterResult:
        async_result = []
        self._create_max_stamina_table_master(
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

    def _get_max_stamina_table_master(
        self,
        request: GetMaxStaminaTableMasterRequest,
        callback: Callable[[AsyncResult[GetMaxStaminaTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/maxStaminaTable/{maxStaminaTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            maxStaminaTableName=request.max_stamina_table_name if request.max_stamina_table_name is not None and request.max_stamina_table_name != '' else 'null',
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
            result_type=GetMaxStaminaTableMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_max_stamina_table_master(
        self,
        request: GetMaxStaminaTableMasterRequest,
    ) -> GetMaxStaminaTableMasterResult:
        async_result = []
        with timeout(30):
            self._get_max_stamina_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_max_stamina_table_master_async(
        self,
        request: GetMaxStaminaTableMasterRequest,
    ) -> GetMaxStaminaTableMasterResult:
        async_result = []
        self._get_max_stamina_table_master(
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

    def _update_max_stamina_table_master(
        self,
        request: UpdateMaxStaminaTableMasterRequest,
        callback: Callable[[AsyncResult[UpdateMaxStaminaTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/maxStaminaTable/{maxStaminaTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            maxStaminaTableName=request.max_stamina_table_name if request.max_stamina_table_name is not None and request.max_stamina_table_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.experience_model_id is not None:
            body["experienceModelId"] = request.experience_model_id
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateMaxStaminaTableMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_max_stamina_table_master(
        self,
        request: UpdateMaxStaminaTableMasterRequest,
    ) -> UpdateMaxStaminaTableMasterResult:
        async_result = []
        with timeout(30):
            self._update_max_stamina_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_max_stamina_table_master_async(
        self,
        request: UpdateMaxStaminaTableMasterRequest,
    ) -> UpdateMaxStaminaTableMasterResult:
        async_result = []
        self._update_max_stamina_table_master(
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

    def _delete_max_stamina_table_master(
        self,
        request: DeleteMaxStaminaTableMasterRequest,
        callback: Callable[[AsyncResult[DeleteMaxStaminaTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/maxStaminaTable/{maxStaminaTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            maxStaminaTableName=request.max_stamina_table_name if request.max_stamina_table_name is not None and request.max_stamina_table_name != '' else 'null',
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
            result_type=DeleteMaxStaminaTableMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_max_stamina_table_master(
        self,
        request: DeleteMaxStaminaTableMasterRequest,
    ) -> DeleteMaxStaminaTableMasterResult:
        async_result = []
        with timeout(30):
            self._delete_max_stamina_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_max_stamina_table_master_async(
        self,
        request: DeleteMaxStaminaTableMasterRequest,
    ) -> DeleteMaxStaminaTableMasterResult:
        async_result = []
        self._delete_max_stamina_table_master(
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

    def _describe_recover_interval_table_masters(
        self,
        request: DescribeRecoverIntervalTableMastersRequest,
        callback: Callable[[AsyncResult[DescribeRecoverIntervalTableMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverIntervalTable".format(
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
            result_type=DescribeRecoverIntervalTableMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_recover_interval_table_masters(
        self,
        request: DescribeRecoverIntervalTableMastersRequest,
    ) -> DescribeRecoverIntervalTableMastersResult:
        async_result = []
        with timeout(30):
            self._describe_recover_interval_table_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_recover_interval_table_masters_async(
        self,
        request: DescribeRecoverIntervalTableMastersRequest,
    ) -> DescribeRecoverIntervalTableMastersResult:
        async_result = []
        self._describe_recover_interval_table_masters(
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

    def _create_recover_interval_table_master(
        self,
        request: CreateRecoverIntervalTableMasterRequest,
        callback: Callable[[AsyncResult[CreateRecoverIntervalTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverIntervalTable".format(
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
        if request.experience_model_id is not None:
            body["experienceModelId"] = request.experience_model_id
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateRecoverIntervalTableMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_recover_interval_table_master(
        self,
        request: CreateRecoverIntervalTableMasterRequest,
    ) -> CreateRecoverIntervalTableMasterResult:
        async_result = []
        with timeout(30):
            self._create_recover_interval_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_recover_interval_table_master_async(
        self,
        request: CreateRecoverIntervalTableMasterRequest,
    ) -> CreateRecoverIntervalTableMasterResult:
        async_result = []
        self._create_recover_interval_table_master(
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

    def _get_recover_interval_table_master(
        self,
        request: GetRecoverIntervalTableMasterRequest,
        callback: Callable[[AsyncResult[GetRecoverIntervalTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverIntervalTable/{recoverIntervalTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            recoverIntervalTableName=request.recover_interval_table_name if request.recover_interval_table_name is not None and request.recover_interval_table_name != '' else 'null',
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
            result_type=GetRecoverIntervalTableMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_recover_interval_table_master(
        self,
        request: GetRecoverIntervalTableMasterRequest,
    ) -> GetRecoverIntervalTableMasterResult:
        async_result = []
        with timeout(30):
            self._get_recover_interval_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_recover_interval_table_master_async(
        self,
        request: GetRecoverIntervalTableMasterRequest,
    ) -> GetRecoverIntervalTableMasterResult:
        async_result = []
        self._get_recover_interval_table_master(
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

    def _update_recover_interval_table_master(
        self,
        request: UpdateRecoverIntervalTableMasterRequest,
        callback: Callable[[AsyncResult[UpdateRecoverIntervalTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverIntervalTable/{recoverIntervalTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            recoverIntervalTableName=request.recover_interval_table_name if request.recover_interval_table_name is not None and request.recover_interval_table_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.experience_model_id is not None:
            body["experienceModelId"] = request.experience_model_id
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateRecoverIntervalTableMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_recover_interval_table_master(
        self,
        request: UpdateRecoverIntervalTableMasterRequest,
    ) -> UpdateRecoverIntervalTableMasterResult:
        async_result = []
        with timeout(30):
            self._update_recover_interval_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_recover_interval_table_master_async(
        self,
        request: UpdateRecoverIntervalTableMasterRequest,
    ) -> UpdateRecoverIntervalTableMasterResult:
        async_result = []
        self._update_recover_interval_table_master(
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

    def _delete_recover_interval_table_master(
        self,
        request: DeleteRecoverIntervalTableMasterRequest,
        callback: Callable[[AsyncResult[DeleteRecoverIntervalTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverIntervalTable/{recoverIntervalTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            recoverIntervalTableName=request.recover_interval_table_name if request.recover_interval_table_name is not None and request.recover_interval_table_name != '' else 'null',
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
            result_type=DeleteRecoverIntervalTableMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_recover_interval_table_master(
        self,
        request: DeleteRecoverIntervalTableMasterRequest,
    ) -> DeleteRecoverIntervalTableMasterResult:
        async_result = []
        with timeout(30):
            self._delete_recover_interval_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_recover_interval_table_master_async(
        self,
        request: DeleteRecoverIntervalTableMasterRequest,
    ) -> DeleteRecoverIntervalTableMasterResult:
        async_result = []
        self._delete_recover_interval_table_master(
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

    def _describe_recover_value_table_masters(
        self,
        request: DescribeRecoverValueTableMastersRequest,
        callback: Callable[[AsyncResult[DescribeRecoverValueTableMastersResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverValueTable".format(
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
            result_type=DescribeRecoverValueTableMastersResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_recover_value_table_masters(
        self,
        request: DescribeRecoverValueTableMastersRequest,
    ) -> DescribeRecoverValueTableMastersResult:
        async_result = []
        with timeout(30):
            self._describe_recover_value_table_masters(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_recover_value_table_masters_async(
        self,
        request: DescribeRecoverValueTableMastersRequest,
    ) -> DescribeRecoverValueTableMastersResult:
        async_result = []
        self._describe_recover_value_table_masters(
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

    def _create_recover_value_table_master(
        self,
        request: CreateRecoverValueTableMasterRequest,
        callback: Callable[[AsyncResult[CreateRecoverValueTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverValueTable".format(
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
        if request.experience_model_id is not None:
            body["experienceModelId"] = request.experience_model_id
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=CreateRecoverValueTableMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def create_recover_value_table_master(
        self,
        request: CreateRecoverValueTableMasterRequest,
    ) -> CreateRecoverValueTableMasterResult:
        async_result = []
        with timeout(30):
            self._create_recover_value_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def create_recover_value_table_master_async(
        self,
        request: CreateRecoverValueTableMasterRequest,
    ) -> CreateRecoverValueTableMasterResult:
        async_result = []
        self._create_recover_value_table_master(
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

    def _get_recover_value_table_master(
        self,
        request: GetRecoverValueTableMasterRequest,
        callback: Callable[[AsyncResult[GetRecoverValueTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverValueTable/{recoverValueTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            recoverValueTableName=request.recover_value_table_name if request.recover_value_table_name is not None and request.recover_value_table_name != '' else 'null',
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
            result_type=GetRecoverValueTableMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_recover_value_table_master(
        self,
        request: GetRecoverValueTableMasterRequest,
    ) -> GetRecoverValueTableMasterResult:
        async_result = []
        with timeout(30):
            self._get_recover_value_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_recover_value_table_master_async(
        self,
        request: GetRecoverValueTableMasterRequest,
    ) -> GetRecoverValueTableMasterResult:
        async_result = []
        self._get_recover_value_table_master(
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

    def _update_recover_value_table_master(
        self,
        request: UpdateRecoverValueTableMasterRequest,
        callback: Callable[[AsyncResult[UpdateRecoverValueTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverValueTable/{recoverValueTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            recoverValueTableName=request.recover_value_table_name if request.recover_value_table_name is not None and request.recover_value_table_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.description is not None:
            body["description"] = request.description
        if request.metadata is not None:
            body["metadata"] = request.metadata
        if request.experience_model_id is not None:
            body["experienceModelId"] = request.experience_model_id
        if request.values is not None:
            body["values"] = [
                item
                for item in request.values
            ]

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        _job = rest.NetworkJob(
            url=url,
            method='PUT',
            result_type=UpdateRecoverValueTableMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_recover_value_table_master(
        self,
        request: UpdateRecoverValueTableMasterRequest,
    ) -> UpdateRecoverValueTableMasterResult:
        async_result = []
        with timeout(30):
            self._update_recover_value_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_recover_value_table_master_async(
        self,
        request: UpdateRecoverValueTableMasterRequest,
    ) -> UpdateRecoverValueTableMasterResult:
        async_result = []
        self._update_recover_value_table_master(
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

    def _delete_recover_value_table_master(
        self,
        request: DeleteRecoverValueTableMasterRequest,
        callback: Callable[[AsyncResult[DeleteRecoverValueTableMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/master/recoverValueTable/{recoverValueTableName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            recoverValueTableName=request.recover_value_table_name if request.recover_value_table_name is not None and request.recover_value_table_name != '' else 'null',
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
            result_type=DeleteRecoverValueTableMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_recover_value_table_master(
        self,
        request: DeleteRecoverValueTableMasterRequest,
    ) -> DeleteRecoverValueTableMasterResult:
        async_result = []
        with timeout(30):
            self._delete_recover_value_table_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_recover_value_table_master_async(
        self,
        request: DeleteRecoverValueTableMasterRequest,
    ) -> DeleteRecoverValueTableMasterResult:
        async_result = []
        self._delete_recover_value_table_master(
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
            service='stamina',
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

    def _get_current_stamina_master(
        self,
        request: GetCurrentStaminaMasterRequest,
        callback: Callable[[AsyncResult[GetCurrentStaminaMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
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
            result_type=GetCurrentStaminaMasterResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_current_stamina_master(
        self,
        request: GetCurrentStaminaMasterRequest,
    ) -> GetCurrentStaminaMasterResult:
        async_result = []
        with timeout(30):
            self._get_current_stamina_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_current_stamina_master_async(
        self,
        request: GetCurrentStaminaMasterRequest,
    ) -> GetCurrentStaminaMasterResult:
        async_result = []
        self._get_current_stamina_master(
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

    def _pre_update_current_stamina_master(
        self,
        request: PreUpdateCurrentStaminaMasterRequest,
        callback: Callable[[AsyncResult[PreUpdateCurrentStaminaMasterResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
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
            result_type=PreUpdateCurrentStaminaMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def pre_update_current_stamina_master(
        self,
        request: PreUpdateCurrentStaminaMasterRequest,
    ) -> PreUpdateCurrentStaminaMasterResult:
        async_result = []
        with timeout(30):
            self._pre_update_current_stamina_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def pre_update_current_stamina_master_async(
        self,
        request: PreUpdateCurrentStaminaMasterRequest,
    ) -> PreUpdateCurrentStaminaMasterResult:
        async_result = []
        self._pre_update_current_stamina_master(
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

    def _update_current_stamina_master(
        self,
        request: UpdateCurrentStaminaMasterRequest,
        callback: Callable[[AsyncResult[UpdateCurrentStaminaMasterResult]], None],
        is_blocking: bool,
    ):
        if request.settings is not None:
            res = self.pre_update_current_stamina_master(
                PreUpdateCurrentStaminaMasterRequest() \
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
            service='stamina',
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
            result_type=UpdateCurrentStaminaMasterResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_stamina_master(
        self,
        request: UpdateCurrentStaminaMasterRequest,
    ) -> UpdateCurrentStaminaMasterResult:
        async_result = []
        with timeout(30):
            self._update_current_stamina_master(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_stamina_master_async(
        self,
        request: UpdateCurrentStaminaMasterRequest,
    ) -> UpdateCurrentStaminaMasterResult:
        async_result = []
        self._update_current_stamina_master(
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

    def _update_current_stamina_master_from_git_hub(
        self,
        request: UpdateCurrentStaminaMasterFromGitHubRequest,
        callback: Callable[[AsyncResult[UpdateCurrentStaminaMasterFromGitHubResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
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
            result_type=UpdateCurrentStaminaMasterFromGitHubResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_current_stamina_master_from_git_hub(
        self,
        request: UpdateCurrentStaminaMasterFromGitHubRequest,
    ) -> UpdateCurrentStaminaMasterFromGitHubResult:
        async_result = []
        with timeout(30):
            self._update_current_stamina_master_from_git_hub(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_current_stamina_master_from_git_hub_async(
        self,
        request: UpdateCurrentStaminaMasterFromGitHubRequest,
    ) -> UpdateCurrentStaminaMasterFromGitHubResult:
        async_result = []
        self._update_current_stamina_master_from_git_hub(
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

    def _describe_stamina_models(
        self,
        request: DescribeStaminaModelsRequest,
        callback: Callable[[AsyncResult[DescribeStaminaModelsResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
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
            result_type=DescribeStaminaModelsResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_stamina_models(
        self,
        request: DescribeStaminaModelsRequest,
    ) -> DescribeStaminaModelsResult:
        async_result = []
        with timeout(30):
            self._describe_stamina_models(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_stamina_models_async(
        self,
        request: DescribeStaminaModelsRequest,
    ) -> DescribeStaminaModelsResult:
        async_result = []
        self._describe_stamina_models(
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

    def _get_stamina_model(
        self,
        request: GetStaminaModelRequest,
        callback: Callable[[AsyncResult[GetStaminaModelResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/model/{staminaName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
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
            result_type=GetStaminaModelResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_stamina_model(
        self,
        request: GetStaminaModelRequest,
    ) -> GetStaminaModelResult:
        async_result = []
        with timeout(30):
            self._get_stamina_model(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stamina_model_async(
        self,
        request: GetStaminaModelRequest,
    ) -> GetStaminaModelResult:
        async_result = []
        self._get_stamina_model(
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

    def _describe_staminas(
        self,
        request: DescribeStaminasRequest,
        callback: Callable[[AsyncResult[DescribeStaminasResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina".format(
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
            result_type=DescribeStaminasResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_staminas(
        self,
        request: DescribeStaminasRequest,
    ) -> DescribeStaminasResult:
        async_result = []
        with timeout(30):
            self._describe_staminas(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_staminas_async(
        self,
        request: DescribeStaminasRequest,
    ) -> DescribeStaminasResult:
        async_result = []
        self._describe_staminas(
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

    def _describe_staminas_by_user_id(
        self,
        request: DescribeStaminasByUserIdRequest,
        callback: Callable[[AsyncResult[DescribeStaminasByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina".format(
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
            result_type=DescribeStaminasByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def describe_staminas_by_user_id(
        self,
        request: DescribeStaminasByUserIdRequest,
    ) -> DescribeStaminasByUserIdResult:
        async_result = []
        with timeout(30):
            self._describe_staminas_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def describe_staminas_by_user_id_async(
        self,
        request: DescribeStaminasByUserIdRequest,
    ) -> DescribeStaminasByUserIdResult:
        async_result = []
        self._describe_staminas_by_user_id(
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

    def _get_stamina(
        self,
        request: GetStaminaRequest,
        callback: Callable[[AsyncResult[GetStaminaResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
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
            result_type=GetStaminaResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_stamina(
        self,
        request: GetStaminaRequest,
    ) -> GetStaminaResult:
        async_result = []
        with timeout(30):
            self._get_stamina(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stamina_async(
        self,
        request: GetStaminaRequest,
    ) -> GetStaminaResult:
        async_result = []
        self._get_stamina(
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

    def _get_stamina_by_user_id(
        self,
        request: GetStaminaByUserIdRequest,
        callback: Callable[[AsyncResult[GetStaminaByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
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
            result_type=GetStaminaByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def get_stamina_by_user_id(
        self,
        request: GetStaminaByUserIdRequest,
    ) -> GetStaminaByUserIdResult:
        async_result = []
        with timeout(30):
            self._get_stamina_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def get_stamina_by_user_id_async(
        self,
        request: GetStaminaByUserIdRequest,
    ) -> GetStaminaByUserIdResult:
        async_result = []
        self._get_stamina_by_user_id(
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

    def _update_stamina_by_user_id(
        self,
        request: UpdateStaminaByUserIdRequest,
        callback: Callable[[AsyncResult[UpdateStaminaByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
        if request.max_value is not None:
            body["maxValue"] = request.max_value
        if request.recover_interval_minutes is not None:
            body["recoverIntervalMinutes"] = request.recover_interval_minutes
        if request.recover_value is not None:
            body["recoverValue"] = request.recover_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=UpdateStaminaByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def update_stamina_by_user_id(
        self,
        request: UpdateStaminaByUserIdRequest,
    ) -> UpdateStaminaByUserIdResult:
        async_result = []
        with timeout(30):
            self._update_stamina_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def update_stamina_by_user_id_async(
        self,
        request: UpdateStaminaByUserIdRequest,
    ) -> UpdateStaminaByUserIdResult:
        async_result = []
        self._update_stamina_by_user_id(
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

    def _consume_stamina(
        self,
        request: ConsumeStaminaRequest,
        callback: Callable[[AsyncResult[ConsumeStaminaResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/consume".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.consume_value is not None:
            body["consumeValue"] = request.consume_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeStaminaResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_stamina(
        self,
        request: ConsumeStaminaRequest,
    ) -> ConsumeStaminaResult:
        async_result = []
        with timeout(30):
            self._consume_stamina(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_stamina_async(
        self,
        request: ConsumeStaminaRequest,
    ) -> ConsumeStaminaResult:
        async_result = []
        self._consume_stamina(
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

    def _consume_stamina_by_user_id(
        self,
        request: ConsumeStaminaByUserIdRequest,
        callback: Callable[[AsyncResult[ConsumeStaminaByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/consume".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.consume_value is not None:
            body["consumeValue"] = request.consume_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=ConsumeStaminaByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_stamina_by_user_id(
        self,
        request: ConsumeStaminaByUserIdRequest,
    ) -> ConsumeStaminaByUserIdResult:
        async_result = []
        with timeout(30):
            self._consume_stamina_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_stamina_by_user_id_async(
        self,
        request: ConsumeStaminaByUserIdRequest,
    ) -> ConsumeStaminaByUserIdResult:
        async_result = []
        self._consume_stamina_by_user_id(
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

    def _apply_stamina(
        self,
        request: ApplyStaminaRequest,
        callback: Callable[[AsyncResult[ApplyStaminaResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/apply".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
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
            result_type=ApplyStaminaResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def apply_stamina(
        self,
        request: ApplyStaminaRequest,
    ) -> ApplyStaminaResult:
        async_result = []
        with timeout(30):
            self._apply_stamina(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def apply_stamina_async(
        self,
        request: ApplyStaminaRequest,
    ) -> ApplyStaminaResult:
        async_result = []
        self._apply_stamina(
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

    def _apply_stamina_by_user_id(
        self,
        request: ApplyStaminaByUserIdRequest,
        callback: Callable[[AsyncResult[ApplyStaminaByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/apply".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
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
            result_type=ApplyStaminaByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def apply_stamina_by_user_id(
        self,
        request: ApplyStaminaByUserIdRequest,
    ) -> ApplyStaminaByUserIdResult:
        async_result = []
        with timeout(30):
            self._apply_stamina_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def apply_stamina_by_user_id_async(
        self,
        request: ApplyStaminaByUserIdRequest,
    ) -> ApplyStaminaByUserIdResult:
        async_result = []
        self._apply_stamina_by_user_id(
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

    def _recover_stamina_by_user_id(
        self,
        request: RecoverStaminaByUserIdRequest,
        callback: Callable[[AsyncResult[RecoverStaminaByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/recover".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.recover_value is not None:
            body["recoverValue"] = request.recover_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=RecoverStaminaByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def recover_stamina_by_user_id(
        self,
        request: RecoverStaminaByUserIdRequest,
    ) -> RecoverStaminaByUserIdResult:
        async_result = []
        with timeout(30):
            self._recover_stamina_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def recover_stamina_by_user_id_async(
        self,
        request: RecoverStaminaByUserIdRequest,
    ) -> RecoverStaminaByUserIdResult:
        async_result = []
        self._recover_stamina_by_user_id(
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

    def _raise_max_value_by_user_id(
        self,
        request: RaiseMaxValueByUserIdRequest,
        callback: Callable[[AsyncResult[RaiseMaxValueByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/raise".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.raise_value is not None:
            body["raiseValue"] = request.raise_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=RaiseMaxValueByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def raise_max_value_by_user_id(
        self,
        request: RaiseMaxValueByUserIdRequest,
    ) -> RaiseMaxValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._raise_max_value_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def raise_max_value_by_user_id_async(
        self,
        request: RaiseMaxValueByUserIdRequest,
    ) -> RaiseMaxValueByUserIdResult:
        async_result = []
        self._raise_max_value_by_user_id(
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

    def _decrease_max_value(
        self,
        request: DecreaseMaxValueRequest,
        callback: Callable[[AsyncResult[DecreaseMaxValueResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/decrease".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.decrease_value is not None:
            body["decreaseValue"] = request.decrease_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=DecreaseMaxValueResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def decrease_max_value(
        self,
        request: DecreaseMaxValueRequest,
    ) -> DecreaseMaxValueResult:
        async_result = []
        with timeout(30):
            self._decrease_max_value(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_max_value_async(
        self,
        request: DecreaseMaxValueRequest,
    ) -> DecreaseMaxValueResult:
        async_result = []
        self._decrease_max_value(
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

    def _decrease_max_value_by_user_id(
        self,
        request: DecreaseMaxValueByUserIdRequest,
        callback: Callable[[AsyncResult[DecreaseMaxValueByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/decrease".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.decrease_value is not None:
            body["decreaseValue"] = request.decrease_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=DecreaseMaxValueByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def decrease_max_value_by_user_id(
        self,
        request: DecreaseMaxValueByUserIdRequest,
    ) -> DecreaseMaxValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._decrease_max_value_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_max_value_by_user_id_async(
        self,
        request: DecreaseMaxValueByUserIdRequest,
    ) -> DecreaseMaxValueByUserIdResult:
        async_result = []
        self._decrease_max_value_by_user_id(
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

    def _set_max_value_by_user_id(
        self,
        request: SetMaxValueByUserIdRequest,
        callback: Callable[[AsyncResult[SetMaxValueByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/set".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.max_value is not None:
            body["maxValue"] = request.max_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetMaxValueByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_max_value_by_user_id(
        self,
        request: SetMaxValueByUserIdRequest,
    ) -> SetMaxValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_max_value_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_max_value_by_user_id_async(
        self,
        request: SetMaxValueByUserIdRequest,
    ) -> SetMaxValueByUserIdResult:
        async_result = []
        self._set_max_value_by_user_id(
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

    def _set_recover_interval_by_user_id(
        self,
        request: SetRecoverIntervalByUserIdRequest,
        callback: Callable[[AsyncResult[SetRecoverIntervalByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/recoverInterval/set".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.recover_interval_minutes is not None:
            body["recoverIntervalMinutes"] = request.recover_interval_minutes

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetRecoverIntervalByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_recover_interval_by_user_id(
        self,
        request: SetRecoverIntervalByUserIdRequest,
    ) -> SetRecoverIntervalByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_recover_interval_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_recover_interval_by_user_id_async(
        self,
        request: SetRecoverIntervalByUserIdRequest,
    ) -> SetRecoverIntervalByUserIdResult:
        async_result = []
        self._set_recover_interval_by_user_id(
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

    def _set_recover_value_by_user_id(
        self,
        request: SetRecoverValueByUserIdRequest,
        callback: Callable[[AsyncResult[SetRecoverValueByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/recoverValue/set".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.recover_value is not None:
            body["recoverValue"] = request.recover_value

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        if request.time_offset_token:
            headers["X-GS2-TIME-OFFSET-TOKEN"] = request.time_offset_token
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetRecoverValueByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_recover_value_by_user_id(
        self,
        request: SetRecoverValueByUserIdRequest,
    ) -> SetRecoverValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._set_recover_value_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_recover_value_by_user_id_async(
        self,
        request: SetRecoverValueByUserIdRequest,
    ) -> SetRecoverValueByUserIdResult:
        async_result = []
        self._set_recover_value_by_user_id(
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

    def _set_max_value_by_status(
        self,
        request: SetMaxValueByStatusRequest,
        callback: Callable[[AsyncResult[SetMaxValueByStatusResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/set".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.signed_status_body is not None:
            body["signedStatusBody"] = request.signed_status_body
        if request.signed_status_signature is not None:
            body["signedStatusSignature"] = request.signed_status_signature

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetMaxValueByStatusResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_max_value_by_status(
        self,
        request: SetMaxValueByStatusRequest,
    ) -> SetMaxValueByStatusResult:
        async_result = []
        with timeout(30):
            self._set_max_value_by_status(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_max_value_by_status_async(
        self,
        request: SetMaxValueByStatusRequest,
    ) -> SetMaxValueByStatusResult:
        async_result = []
        self._set_max_value_by_status(
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

    def _set_recover_interval_by_status(
        self,
        request: SetRecoverIntervalByStatusRequest,
        callback: Callable[[AsyncResult[SetRecoverIntervalByStatusResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/recoverInterval/set".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.signed_status_body is not None:
            body["signedStatusBody"] = request.signed_status_body
        if request.signed_status_signature is not None:
            body["signedStatusSignature"] = request.signed_status_signature

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetRecoverIntervalByStatusResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_recover_interval_by_status(
        self,
        request: SetRecoverIntervalByStatusRequest,
    ) -> SetRecoverIntervalByStatusResult:
        async_result = []
        with timeout(30):
            self._set_recover_interval_by_status(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_recover_interval_by_status_async(
        self,
        request: SetRecoverIntervalByStatusRequest,
    ) -> SetRecoverIntervalByStatusResult:
        async_result = []
        self._set_recover_interval_by_status(
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

    def _set_recover_value_by_status(
        self,
        request: SetRecoverValueByStatusRequest,
        callback: Callable[[AsyncResult[SetRecoverValueByStatusResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/recoverValue/set".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.key_id is not None:
            body["keyId"] = request.key_id
        if request.signed_status_body is not None:
            body["signedStatusBody"] = request.signed_status_body
        if request.signed_status_signature is not None:
            body["signedStatusSignature"] = request.signed_status_signature

        if request.request_id:
            headers["X-GS2-REQUEST-ID"] = request.request_id
        if request.access_token:
            headers["X-GS2-ACCESS-TOKEN"] = request.access_token
        if request.duplication_avoider:
            headers["X-GS2-DUPLICATION-AVOIDER"] = request.duplication_avoider
        _job = rest.NetworkJob(
            url=url,
            method='POST',
            result_type=SetRecoverValueByStatusResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_recover_value_by_status(
        self,
        request: SetRecoverValueByStatusRequest,
    ) -> SetRecoverValueByStatusResult:
        async_result = []
        with timeout(30):
            self._set_recover_value_by_status(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_recover_value_by_status_async(
        self,
        request: SetRecoverValueByStatusRequest,
    ) -> SetRecoverValueByStatusResult:
        async_result = []
        self._set_recover_value_by_status(
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

    def _delete_stamina_by_user_id(
        self,
        request: DeleteStaminaByUserIdRequest,
        callback: Callable[[AsyncResult[DeleteStaminaByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
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
            result_type=DeleteStaminaByUserIdResult,
            callback=callback,
            headers=headers,
            query_strings=query_strings,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def delete_stamina_by_user_id(
        self,
        request: DeleteStaminaByUserIdRequest,
    ) -> DeleteStaminaByUserIdResult:
        async_result = []
        with timeout(30):
            self._delete_stamina_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def delete_stamina_by_user_id_async(
        self,
        request: DeleteStaminaByUserIdRequest,
    ) -> DeleteStaminaByUserIdResult:
        async_result = []
        self._delete_stamina_by_user_id(
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

    def _verify_stamina_value(
        self,
        request: VerifyStaminaValueRequest,
        callback: Callable[[AsyncResult[VerifyStaminaValueResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/value/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaValueResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_value(
        self,
        request: VerifyStaminaValueRequest,
    ) -> VerifyStaminaValueResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_value(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_value_async(
        self,
        request: VerifyStaminaValueRequest,
    ) -> VerifyStaminaValueResult:
        async_result = []
        self._verify_stamina_value(
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

    def _verify_stamina_value_by_user_id(
        self,
        request: VerifyStaminaValueByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyStaminaValueByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/value/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaValueByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_value_by_user_id(
        self,
        request: VerifyStaminaValueByUserIdRequest,
    ) -> VerifyStaminaValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_value_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_value_by_user_id_async(
        self,
        request: VerifyStaminaValueByUserIdRequest,
    ) -> VerifyStaminaValueByUserIdResult:
        async_result = []
        self._verify_stamina_value_by_user_id(
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

    def _verify_stamina_max_value(
        self,
        request: VerifyStaminaMaxValueRequest,
        callback: Callable[[AsyncResult[VerifyStaminaMaxValueResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/max/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaMaxValueResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_max_value(
        self,
        request: VerifyStaminaMaxValueRequest,
    ) -> VerifyStaminaMaxValueResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_max_value(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_max_value_async(
        self,
        request: VerifyStaminaMaxValueRequest,
    ) -> VerifyStaminaMaxValueResult:
        async_result = []
        self._verify_stamina_max_value(
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

    def _verify_stamina_max_value_by_user_id(
        self,
        request: VerifyStaminaMaxValueByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyStaminaMaxValueByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/max/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaMaxValueByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_max_value_by_user_id(
        self,
        request: VerifyStaminaMaxValueByUserIdRequest,
    ) -> VerifyStaminaMaxValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_max_value_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_max_value_by_user_id_async(
        self,
        request: VerifyStaminaMaxValueByUserIdRequest,
    ) -> VerifyStaminaMaxValueByUserIdResult:
        async_result = []
        self._verify_stamina_max_value_by_user_id(
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

    def _verify_stamina_recover_interval_minutes(
        self,
        request: VerifyStaminaRecoverIntervalMinutesRequest,
        callback: Callable[[AsyncResult[VerifyStaminaRecoverIntervalMinutesResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/recover/interval/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaRecoverIntervalMinutesResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_recover_interval_minutes(
        self,
        request: VerifyStaminaRecoverIntervalMinutesRequest,
    ) -> VerifyStaminaRecoverIntervalMinutesResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_recover_interval_minutes(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_recover_interval_minutes_async(
        self,
        request: VerifyStaminaRecoverIntervalMinutesRequest,
    ) -> VerifyStaminaRecoverIntervalMinutesResult:
        async_result = []
        self._verify_stamina_recover_interval_minutes(
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

    def _verify_stamina_recover_interval_minutes_by_user_id(
        self,
        request: VerifyStaminaRecoverIntervalMinutesByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyStaminaRecoverIntervalMinutesByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/recover/interval/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaRecoverIntervalMinutesByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_recover_interval_minutes_by_user_id(
        self,
        request: VerifyStaminaRecoverIntervalMinutesByUserIdRequest,
    ) -> VerifyStaminaRecoverIntervalMinutesByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_recover_interval_minutes_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_recover_interval_minutes_by_user_id_async(
        self,
        request: VerifyStaminaRecoverIntervalMinutesByUserIdRequest,
    ) -> VerifyStaminaRecoverIntervalMinutesByUserIdResult:
        async_result = []
        self._verify_stamina_recover_interval_minutes_by_user_id(
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

    def _verify_stamina_recover_value(
        self,
        request: VerifyStaminaRecoverValueRequest,
        callback: Callable[[AsyncResult[VerifyStaminaRecoverValueResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/recover/value/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaRecoverValueResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_recover_value(
        self,
        request: VerifyStaminaRecoverValueRequest,
    ) -> VerifyStaminaRecoverValueResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_recover_value(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_recover_value_async(
        self,
        request: VerifyStaminaRecoverValueRequest,
    ) -> VerifyStaminaRecoverValueResult:
        async_result = []
        self._verify_stamina_recover_value(
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

    def _verify_stamina_recover_value_by_user_id(
        self,
        request: VerifyStaminaRecoverValueByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyStaminaRecoverValueByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/recover/value/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaRecoverValueByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_recover_value_by_user_id(
        self,
        request: VerifyStaminaRecoverValueByUserIdRequest,
    ) -> VerifyStaminaRecoverValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_recover_value_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_recover_value_by_user_id_async(
        self,
        request: VerifyStaminaRecoverValueByUserIdRequest,
    ) -> VerifyStaminaRecoverValueByUserIdResult:
        async_result = []
        self._verify_stamina_recover_value_by_user_id(
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

    def _verify_stamina_overflow_value(
        self,
        request: VerifyStaminaOverflowValueRequest,
        callback: Callable[[AsyncResult[VerifyStaminaOverflowValueResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/me/stamina/{staminaName}/overflow/value/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaOverflowValueResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_overflow_value(
        self,
        request: VerifyStaminaOverflowValueRequest,
    ) -> VerifyStaminaOverflowValueResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_overflow_value(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_overflow_value_async(
        self,
        request: VerifyStaminaOverflowValueRequest,
    ) -> VerifyStaminaOverflowValueResult:
        async_result = []
        self._verify_stamina_overflow_value(
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

    def _verify_stamina_overflow_value_by_user_id(
        self,
        request: VerifyStaminaOverflowValueByUserIdRequest,
        callback: Callable[[AsyncResult[VerifyStaminaOverflowValueByUserIdResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/{namespaceName}/user/{userId}/stamina/{staminaName}/overflow/value/verify/{verifyType}".format(
            namespaceName=request.namespace_name if request.namespace_name is not None and request.namespace_name != '' else 'null',
            userId=request.user_id if request.user_id is not None and request.user_id != '' else 'null',
            staminaName=request.stamina_name if request.stamina_name is not None and request.stamina_name != '' else 'null',
            verifyType=request.verify_type if request.verify_type is not None and request.verify_type != '' else 'null',
        )

        headers = self._create_authorized_headers()
        body = {
            'contextStack': request.context_stack,
        }
        if request.value is not None:
            body["value"] = request.value
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
            result_type=VerifyStaminaOverflowValueByUserIdResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_overflow_value_by_user_id(
        self,
        request: VerifyStaminaOverflowValueByUserIdRequest,
    ) -> VerifyStaminaOverflowValueByUserIdResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_overflow_value_by_user_id(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_overflow_value_by_user_id_async(
        self,
        request: VerifyStaminaOverflowValueByUserIdRequest,
    ) -> VerifyStaminaOverflowValueByUserIdResult:
        async_result = []
        self._verify_stamina_overflow_value_by_user_id(
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

    def _recover_stamina_by_stamp_sheet(
        self,
        request: RecoverStaminaByStampSheetRequest,
        callback: Callable[[AsyncResult[RecoverStaminaByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/recover"

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
            result_type=RecoverStaminaByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def recover_stamina_by_stamp_sheet(
        self,
        request: RecoverStaminaByStampSheetRequest,
    ) -> RecoverStaminaByStampSheetResult:
        async_result = []
        with timeout(30):
            self._recover_stamina_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def recover_stamina_by_stamp_sheet_async(
        self,
        request: RecoverStaminaByStampSheetRequest,
    ) -> RecoverStaminaByStampSheetResult:
        async_result = []
        self._recover_stamina_by_stamp_sheet(
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

    def _raise_max_value_by_stamp_sheet(
        self,
        request: RaiseMaxValueByStampSheetRequest,
        callback: Callable[[AsyncResult[RaiseMaxValueByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/raise"

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
            result_type=RaiseMaxValueByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def raise_max_value_by_stamp_sheet(
        self,
        request: RaiseMaxValueByStampSheetRequest,
    ) -> RaiseMaxValueByStampSheetResult:
        async_result = []
        with timeout(30):
            self._raise_max_value_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def raise_max_value_by_stamp_sheet_async(
        self,
        request: RaiseMaxValueByStampSheetRequest,
    ) -> RaiseMaxValueByStampSheetResult:
        async_result = []
        self._raise_max_value_by_stamp_sheet(
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

    def _decrease_max_value_by_stamp_task(
        self,
        request: DecreaseMaxValueByStampTaskRequest,
        callback: Callable[[AsyncResult[DecreaseMaxValueByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/decrease"

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
            result_type=DecreaseMaxValueByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def decrease_max_value_by_stamp_task(
        self,
        request: DecreaseMaxValueByStampTaskRequest,
    ) -> DecreaseMaxValueByStampTaskResult:
        async_result = []
        with timeout(30):
            self._decrease_max_value_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def decrease_max_value_by_stamp_task_async(
        self,
        request: DecreaseMaxValueByStampTaskRequest,
    ) -> DecreaseMaxValueByStampTaskResult:
        async_result = []
        self._decrease_max_value_by_stamp_task(
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

    def _set_max_value_by_stamp_sheet(
        self,
        request: SetMaxValueByStampSheetRequest,
        callback: Callable[[AsyncResult[SetMaxValueByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/max/set"

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
            result_type=SetMaxValueByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_max_value_by_stamp_sheet(
        self,
        request: SetMaxValueByStampSheetRequest,
    ) -> SetMaxValueByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_max_value_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_max_value_by_stamp_sheet_async(
        self,
        request: SetMaxValueByStampSheetRequest,
    ) -> SetMaxValueByStampSheetResult:
        async_result = []
        self._set_max_value_by_stamp_sheet(
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

    def _set_recover_interval_by_stamp_sheet(
        self,
        request: SetRecoverIntervalByStampSheetRequest,
        callback: Callable[[AsyncResult[SetRecoverIntervalByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/recoverInterval/set"

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
            result_type=SetRecoverIntervalByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_recover_interval_by_stamp_sheet(
        self,
        request: SetRecoverIntervalByStampSheetRequest,
    ) -> SetRecoverIntervalByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_recover_interval_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_recover_interval_by_stamp_sheet_async(
        self,
        request: SetRecoverIntervalByStampSheetRequest,
    ) -> SetRecoverIntervalByStampSheetResult:
        async_result = []
        self._set_recover_interval_by_stamp_sheet(
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

    def _set_recover_value_by_stamp_sheet(
        self,
        request: SetRecoverValueByStampSheetRequest,
        callback: Callable[[AsyncResult[SetRecoverValueByStampSheetResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/recoverValue/set"

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
            result_type=SetRecoverValueByStampSheetResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def set_recover_value_by_stamp_sheet(
        self,
        request: SetRecoverValueByStampSheetRequest,
    ) -> SetRecoverValueByStampSheetResult:
        async_result = []
        with timeout(30):
            self._set_recover_value_by_stamp_sheet(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def set_recover_value_by_stamp_sheet_async(
        self,
        request: SetRecoverValueByStampSheetRequest,
    ) -> SetRecoverValueByStampSheetResult:
        async_result = []
        self._set_recover_value_by_stamp_sheet(
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

    def _consume_stamina_by_stamp_task(
        self,
        request: ConsumeStaminaByStampTaskRequest,
        callback: Callable[[AsyncResult[ConsumeStaminaByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/consume"

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
            result_type=ConsumeStaminaByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def consume_stamina_by_stamp_task(
        self,
        request: ConsumeStaminaByStampTaskRequest,
    ) -> ConsumeStaminaByStampTaskResult:
        async_result = []
        with timeout(30):
            self._consume_stamina_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def consume_stamina_by_stamp_task_async(
        self,
        request: ConsumeStaminaByStampTaskRequest,
    ) -> ConsumeStaminaByStampTaskResult:
        async_result = []
        self._consume_stamina_by_stamp_task(
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

    def _verify_stamina_value_by_stamp_task(
        self,
        request: VerifyStaminaValueByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyStaminaValueByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/value/verify"

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
            result_type=VerifyStaminaValueByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_value_by_stamp_task(
        self,
        request: VerifyStaminaValueByStampTaskRequest,
    ) -> VerifyStaminaValueByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_value_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_value_by_stamp_task_async(
        self,
        request: VerifyStaminaValueByStampTaskRequest,
    ) -> VerifyStaminaValueByStampTaskResult:
        async_result = []
        self._verify_stamina_value_by_stamp_task(
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

    def _verify_stamina_max_value_by_stamp_task(
        self,
        request: VerifyStaminaMaxValueByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyStaminaMaxValueByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/max/verify"

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
            result_type=VerifyStaminaMaxValueByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_max_value_by_stamp_task(
        self,
        request: VerifyStaminaMaxValueByStampTaskRequest,
    ) -> VerifyStaminaMaxValueByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_max_value_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_max_value_by_stamp_task_async(
        self,
        request: VerifyStaminaMaxValueByStampTaskRequest,
    ) -> VerifyStaminaMaxValueByStampTaskResult:
        async_result = []
        self._verify_stamina_max_value_by_stamp_task(
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

    def _verify_stamina_recover_interval_minutes_by_stamp_task(
        self,
        request: VerifyStaminaRecoverIntervalMinutesByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyStaminaRecoverIntervalMinutesByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/recover/interval/verify"

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
            result_type=VerifyStaminaRecoverIntervalMinutesByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_recover_interval_minutes_by_stamp_task(
        self,
        request: VerifyStaminaRecoverIntervalMinutesByStampTaskRequest,
    ) -> VerifyStaminaRecoverIntervalMinutesByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_recover_interval_minutes_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_recover_interval_minutes_by_stamp_task_async(
        self,
        request: VerifyStaminaRecoverIntervalMinutesByStampTaskRequest,
    ) -> VerifyStaminaRecoverIntervalMinutesByStampTaskResult:
        async_result = []
        self._verify_stamina_recover_interval_minutes_by_stamp_task(
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

    def _verify_stamina_recover_value_by_stamp_task(
        self,
        request: VerifyStaminaRecoverValueByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyStaminaRecoverValueByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/recover/value/verify"

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
            result_type=VerifyStaminaRecoverValueByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_recover_value_by_stamp_task(
        self,
        request: VerifyStaminaRecoverValueByStampTaskRequest,
    ) -> VerifyStaminaRecoverValueByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_recover_value_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_recover_value_by_stamp_task_async(
        self,
        request: VerifyStaminaRecoverValueByStampTaskRequest,
    ) -> VerifyStaminaRecoverValueByStampTaskResult:
        async_result = []
        self._verify_stamina_recover_value_by_stamp_task(
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

    def _verify_stamina_overflow_value_by_stamp_task(
        self,
        request: VerifyStaminaOverflowValueByStampTaskRequest,
        callback: Callable[[AsyncResult[VerifyStaminaOverflowValueByStampTaskResult]], None],
        is_blocking: bool,
    ):

        url = Gs2Constant.ENDPOINT_HOST.format(
            service='stamina',
            region=self.session.region,
        ) + "/stamina/overflow/value/verify"

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
            result_type=VerifyStaminaOverflowValueByStampTaskResult,
            callback=callback,
            headers=headers,
            body=body,
        )

        self.session.send(
            job=_job,
            is_blocking=is_blocking,
        )

    def verify_stamina_overflow_value_by_stamp_task(
        self,
        request: VerifyStaminaOverflowValueByStampTaskRequest,
    ) -> VerifyStaminaOverflowValueByStampTaskResult:
        async_result = []
        with timeout(30):
            self._verify_stamina_overflow_value_by_stamp_task(
                request,
                lambda result: async_result.append(result),
                is_blocking=True,
            )

        if async_result[0].error:
            raise async_result[0].error
        return async_result[0].result


    async def verify_stamina_overflow_value_by_stamp_task_async(
        self,
        request: VerifyStaminaOverflowValueByStampTaskRequest,
    ) -> VerifyStaminaOverflowValueByStampTaskResult:
        async_result = []
        self._verify_stamina_overflow_value_by_stamp_task(
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